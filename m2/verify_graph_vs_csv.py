"""Private-style checks: does the graph give the same answers as the raw CSVs?

The grader runs unseen Cypher queries on our graph. They can only give the
expected answers if the graph faithfully represents the CSVs. This script asks
25 questions of the kind a grader might ask, covering every label, every
relationship type, and every property type (int, float, date, string, missing).
Each question is answered twice, with Cypher on the graph and with pandas on
the raw CSVs, and the two answers must match exactly (development tool, not a
deliverable).

Run:  python verify_graph_vs_csv.py
"""

import pandas as pd
from neo4j import GraphDatabase

from Create_kg import HERE, read_config

TOL = 1e-6


# ---------------------------------------------------------------- raw CSVs

def csv(name):
    df = pd.read_csv(HERE / f"{name}.csv", na_values=["\\N", ""], keep_default_na=False, encoding="utf-8-sig")
    for c in df.select_dtypes("object"):
        df[c] = df[c].str.strip()
    return df


d, c, ci, ra, res, q, p, st = (csv(n) for n in
                               ["drivers", "constructors", "circuits", "races", "results",
                                "qualifying", "pit_stops", "status"])
ra["date"] = pd.to_datetime(ra.date)
d["dob"] = pd.to_datetime(d.dob)
R = res.merge(ra[["raceId", "year", "round", "date", "circuitId"]], on="raceId").merge(st, on="statusId")
Q = q.merge(ra[["raceId", "year", "round"]], on="raceId")
P = p.merge(ra[["raceId", "year", "round"]], on="raceId")
CLASSIFIED = (R.status == "Finished") | R.status.str.startswith("+")


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def top(df, by, asc, n=None, cols=None):
    out = df.sort_values(by, ascending=asc)
    out = out.head(n) if n else out
    return out[cols] if cols else out


def counts(series, name_key, name_val="n"):
    g = series.value_counts().rename_axis(name_key).reset_index(name=name_val)
    return top(g, [name_val, name_key], [False, True])


# ---------------------------------------------------------------- the checks
# (question, cypher, pandas answer as a DataFrame with the same columns and order)

CHECKS = [
 ("Most career wins (top 10)",
  "MATCH (d:Driver)<-[:BY_DRIVER]-(r:Result {position: 1}) RETURN d.driverId AS id, count(r) AS wins ORDER BY wins DESC, id LIMIT 10",
  lambda: top(R[R.position == 1].groupby("driverId").size().rename("wins").rename_axis("id").reset_index(),
              ["wins", "id"], [False, True], 10)),

 ("Constructor points 2023",
  "MATCH (c:Constructor)<-[:FOR_CONSTRUCTOR]-(x:Result)-[:FOR_RACE]->(:Race {year: 2023}) RETURN c.constructorId AS id, sum(x.points) AS pts ORDER BY pts DESC, id",
  lambda: top(R[R.year == 2023].groupby("constructorId").points.sum().rename("pts").rename_axis("id").reset_index(),
              ["pts", "id"], [False, True])),

 ("Races per season (via IN_SEASON)",
  "MATCH (s:Season)<-[:IN_SEASON]-(r:Race) RETURN s.year AS year, count(r) AS n ORDER BY year",
  lambda: ra.groupby("year").size().rename("n").reset_index()),

 ("Circuits per country",
  "MATCH (c:Circuit) RETURN c.circuit_country AS country, count(*) AS n ORDER BY n DESC, country",
  lambda: counts(ci.country, "country")),

 ("Drivers per nationality",
  "MATCH (d:Driver) RETURN d.nationality AS nat, count(*) AS n ORDER BY n DESC, nat",
  lambda: counts(d.nationality, "nat")),

 ("Constructors per nationality",
  "MATCH (c:Constructor) RETURN c.constructor_nationality AS nat, count(*) AS n ORDER BY n DESC, nat",
  lambda: counts(c.nationality, "nat")),

 ("Drivers born on or after 2000-01-01 (date property)",
  "MATCH (d:Driver) WHERE d.dob >= date('2000-01-01') RETURN d.driverId AS id ORDER BY id",
  lambda: d[d.dob >= "2000-01-01"][["driverId"]].rename(columns={"driverId": "id"}).sort_values("id")),

 ("Drivers with no number (missing property)",
  "MATCH (d:Driver) WHERE d.number IS NULL RETURN count(d) AS n",
  lambda: pd.DataFrame([{"n": int(d.number.isna().sum())}])),

 ("Codes shared by more than one driver",
  "MATCH (d:Driver) WHERE d.code IS NOT NULL WITH d.code AS code, count(*) AS n WHERE n > 1 RETURN count(*) AS shared",
  lambda: pd.DataFrame([{"shared": int((d.code.dropna().value_counts() > 1).sum())}])),

 ("Pole positions (top 10)",
  "MATCH (d:Driver)<-[:BY_DRIVER]-(q:Qualifying {position: 1}) RETURN d.driverId AS id, count(q) AS poles ORDER BY poles DESC, id LIMIT 10",
  lambda: top(Q[Q.position == 1].groupby("driverId").size().rename("poles").rename_axis("id").reset_index(),
              ["poles", "id"], [False, True], 10)),

 ("Fastest Q3 per 2023 race (time string to seconds)",
  "MATCH (q:Qualifying)-[:FOR_RACE]->(r:Race {year: 2023}) WHERE q.q3 IS NOT NULL "
  "WITH r, min(toInteger(split(q.q3, ':')[0]) * 60 + toFloat(split(q.q3, ':')[1])) AS best RETURN r.round AS round, best ORDER BY round",
  lambda: Q[(Q.year == 2023) & Q.q3.notna()].assign(best=lambda x: x.q3.map(secs))
          .groupby("round").best.min().reset_index()),

 ("Qualifying entries with no Q1 time",
  "MATCH (q:Qualifying) WHERE q.q1 IS NULL RETURN count(q) AS n",
  lambda: pd.DataFrame([{"n": int(q.q1.isna().sum())}])),

 ("Real pit stops per 2023 race and their mean (excl. red flags)",
  "MATCH (p:PitStop)-[:FOR_RACE]->(r:Race {year: 2023}) WHERE p.milliseconds <= 300000 "
  "RETURN r.round AS round, count(p) AS stops, toFloat(sum(p.milliseconds)) / count(p) AS avg_ms ORDER BY round",
  lambda: P[(P.year == 2023) & (P.milliseconds <= 300000)].groupby("round")
          .agg(stops=("milliseconds", "size"), avg_ms=("milliseconds", "mean")).reset_index()),

 ("Most stops by one driver in one race",
  "MATCH (p:PitStop)-[:BY_DRIVER]->(d:Driver), (p)-[:FOR_RACE]->(r:Race) WITH r, d, count(p) AS n RETURN max(n) AS max_stops, count(*) AS driver_races",
  lambda: pd.DataFrame([{"max_stops": int(p.groupby(["raceId", "driverId"]).size().max()),
                         "driver_races": int(p.groupby(["raceId", "driverId"]).ngroups)}])),

 ("2024 calendar in date order with circuits (date sort + AT_CIRCUIT)",
  "MATCH (r:Race {year: 2024})-[:AT_CIRCUIT]->(c:Circuit) RETURN toString(r.date) AS date, c.circuitRef AS circuit ORDER BY r.date",
  lambda: ra[ra.year == 2024].merge(ci[["circuitId", "circuitRef"]], on="circuitId").sort_values("date")
          .assign(date=lambda x: x.date.dt.strftime("%Y-%m-%d"))[["date", "circuitRef"]]
          .rename(columns={"circuitRef": "circuit"})),

 ("Races with no start time",
  "MATCH (r:Race) WHERE r.time IS NULL RETURN count(r) AS n",
  lambda: pd.DataFrame([{"n": int(ra.time.isna().sum())}])),

 ("Most common statuses (top 10)",
  "MATCH (x:Result)-[:HAS_STATUS]->(s:Status) RETURN s.status AS status, count(x) AS n ORDER BY n DESC, status LIMIT 10",
  lambda: counts(R.status, "status").head(10)),

 ("Non-classified entries per constructor 2022",
  "MATCH (c:Constructor)<-[:FOR_CONSTRUCTOR]-(x:Result)-[:FOR_RACE]->(:Race {year: 2022}), (x)-[:HAS_STATUS]->(s:Status) "
  "WHERE NOT (s.status = 'Finished' OR s.status STARTS WITH '+') RETURN c.constructor_name AS team, count(x) AS dnfs ORDER BY dnfs DESC, team",
  lambda: top(R[(R.year == 2022) & ~CLASSIFIED].merge(c[["constructorId", "name"]], on="constructorId")
              .groupby("name").size().rename("dnfs").rename_axis("team").reset_index(), ["dnfs", "team"], [False, True])),

 ("Highest fastest-lap speed per circuit (float, top 5)",
  "MATCH (x:Result)-[:FOR_RACE]->(:Race)-[:AT_CIRCUIT]->(c:Circuit) WHERE x.fastestLapSpeed IS NOT NULL "
  "RETURN c.circuitId AS id, max(x.fastestLapSpeed) AS top ORDER BY top DESC, id LIMIT 5",
  lambda: top(R.dropna(subset=["fastestLapSpeed"]).groupby("circuitId").fastestLapSpeed.max().rename("top")
              .rename_axis("id").reset_index(), ["top", "id"], [False, True], 5)),

 ("Youngest race winners in days (date arithmetic)",
  "MATCH (d:Driver)<-[:BY_DRIVER]-(x:Result {position: 1})-[:FOR_RACE]->(r:Race) "
  "RETURN d.driverId AS id, r.raceId AS race, duration.inDays(d.dob, r.date).days AS age_days ORDER BY age_days, race LIMIT 5",
  lambda: top(R[R.position == 1].merge(d[["driverId", "dob"]], on="driverId")
              .assign(age_days=lambda x: (x.date - x.dob).dt.days)
              .rename(columns={"driverId": "id", "raceId": "race"}), ["age_days", "race"], [True, True], 5,
              ["id", "race", "age_days"])),

 ("2023 entries starting behind their qualifying position (Qualifying + Result)",
  "MATCH (q:Qualifying)-[:FOR_RACE]->(r:Race {year: 2023}), (q)-[:BY_DRIVER]->(d:Driver), "
  "(x:Result)-[:FOR_RACE]->(r), (x)-[:BY_DRIVER]->(d) WHERE x.grid > q.position RETURN count(*) AS n",
  lambda: pd.DataFrame([{"n": int((lambda m: (m.grid > m.position_q).sum())(
      R[R.year == 2023].merge(q, on=["raceId", "driverId"], suffixes=("", "_q"))))}])),

 ("Laps completed per driver 2021",
  "MATCH (d:Driver)<-[:BY_DRIVER]-(x:Result)-[:FOR_RACE]->(:Race {year: 2021}) RETURN d.driverId AS id, sum(x.laps) AS laps ORDER BY laps DESC, id",
  lambda: top(R[R.year == 2021].groupby("driverId").laps.sum().rename("laps").rename_axis("id").reset_index(),
              ["laps", "id"], [False, True])),

 ("Highest circuits (int alt, float lat)",
  "MATCH (c:Circuit) RETURN c.circuitRef AS ref, c.alt AS alt, c.lat AS lat ORDER BY alt DESC, ref LIMIT 3",
  lambda: top(ci.rename(columns={"circuitRef": "ref"}), ["alt", "ref"], [False, True], 3, ["ref", "alt", "lat"])),

 ("Fastest winning race times (milliseconds)",
  "MATCH (x:Result {positionOrder: 1}) WHERE x.milliseconds IS NOT NULL RETURN x.resultId AS id, x.milliseconds AS ms ORDER BY ms, id LIMIT 3",
  lambda: top(res[(res.positionOrder == 1) & res.milliseconds.notna()]
              .rename(columns={"resultId": "id", "milliseconds": "ms"}), ["ms", "id"], [True, True], 3, ["id", "ms"])),

 ("Most Monaco wins (circuit by ref, top 5)",
  "MATCH (:Circuit {circuitRef: 'monaco'})<-[:AT_CIRCUIT]-(:Race)<-[:FOR_RACE]-(x:Result {position: 1})-[:BY_DRIVER]->(d:Driver) "
  "RETURN d.driverId AS id, count(*) AS wins ORDER BY wins DESC, id LIMIT 5",
  lambda: top(R[(R.circuitId == 6) & (R.position == 1)].groupby("driverId").size().rename("wins")
              .rename_axis("id").reset_index(), ["wins", "id"], [False, True], 5)),
]


# ---------------------------------------------------------------- compare

def norm(v):
    if hasattr(v, "item"):
        v = v.item()
    return v


def same(a, b):
    a, b = norm(a), norm(b)
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and abs(float(a) - float(b)) <= TOL
    return a == b


def main():
    cfg = read_config(HERE / "config.txt")
    passed = 0
    with GraphDatabase.driver(cfg["URI"], auth=(cfg["USERNAME"], cfg["PASSWORD"])) as drv, \
            drv.session(database=cfg.get("DATABASE") or None) as s:
        for i, (question, cypher, expected_fn) in enumerate(CHECKS, 1):
            graph = [r.data() for r in s.run(cypher)]
            exp = expected_fn().to_dict("records")
            cols = list(exp[0].keys()) if exp else []
            ok = len(graph) == len(exp) and all(
                list(g.keys()) == cols and all(same(g[k], e[k]) for k in cols) for g, e in zip(graph, exp))
            passed += ok
            print(f"{i:2d}. {'PASS' if ok else 'FAIL'}  {question}  ({len(graph)} rows)")
            if not ok:
                print("     graph:", graph[:3])
                print("     csv:  ", exp[:3])
    print(f"\n{passed}/{len(CHECKS)} checks match the CSVs")


if __name__ == "__main__":
    main()
