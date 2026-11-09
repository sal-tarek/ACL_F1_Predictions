"""Check queries.txt two ways (development tool, not a deliverable).

1. Splits queries.txt on the "//N. Query N" headers, the way the autograder
   is described as extracting them, and runs each query on the graph.
2. Computes the same answer independently with pandas from the raw CSVs.
3. Compares the two (columns, row order, values) and prints PASS/FAIL.

Run from anywhere:  python verify_queries.py
"""

import re
from pathlib import Path

import pandas as pd
from neo4j import GraphDatabase

from Create_kg import HERE, read_config

TOL = 1e-6
CLASSIFIED = lambda s: (s == "Finished") | s.str.startswith("+")
NON_START = ["Did not qualify", "Did not prequalify", "Withdrew"]


# ---------------------------------------------------------------- queries.txt

def load_queries(path):
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^//(\d+)\.\s*Query\s*\d+\s*$", text, flags=re.M)
    queries = {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}
    for n, q in queries.items():
        assert q.startswith("MATCH"), f"query {n} does not start with MATCH"
        assert "RETURN" in q, f"query {n} has no RETURN"
    return queries


# ---------------------------------------------------------------- pandas side

def csv(name):
    return pd.read_csv(HERE / f"{name}.csv", na_values=["\\N"], keep_default_na=False,
                       encoding="utf-8-sig", skipinitialspace=True)


def frames():
    d = csv("drivers")
    d["Driver"] = d.forename.str.strip() + " " + d.surname.str.strip()
    res = csv("results").merge(csv("races")[["raceId", "year", "date", "circuitId"]], on="raceId")
    res = res.merge(csv("status"), on="statusId").merge(d[["driverId", "Driver"]], on="driverId")
    res = res.merge(csv("constructors")[["constructorId", "name"]].rename(columns={"name": "Constructor"}),
                    on="constructorId")
    return res


def p1(res):
    x = res[res.year == 2021]
    g = x.groupby(["driverId", "Driver"]).agg(Points=("points", "sum"),
                                              Wins=("position", lambda s: int((s == 1).sum()))).reset_index()
    return g.sort_values(["Points", "Wins", "Driver"], ascending=[False, False, True])[["Driver", "Points", "Wins"]]


def p2(res):
    x = res[res.year.between(2014, 2021)].copy()
    x["cls"] = CLASSIFIED(x.status)
    g = x.groupby(["constructorId", "Constructor"]).agg(Entries=("resultId", "count"),
                                                        Classified=("cls", "sum")).reset_index()
    g = g[g.Entries >= 100].copy()
    g["Reliability"] = g.Classified / g.Entries
    return g.sort_values(["Reliability", "Constructor"], ascending=[False, True])[
        ["Constructor", "Entries", "Classified", "Reliability"]]


def p3(res):
    h = res[res.driverId == 1][["raceId", "constructorId", "Constructor", "positionOrder"]]
    b = res[res.driverId == 822][["raceId", "constructorId", "positionOrder"]]
    m = h.merge(b, on=["raceId", "constructorId"], suffixes=("_h", "_b"))
    g = m.groupby("Constructor").agg(Shared_Races=("raceId", "nunique"),
                                     Hamilton_Ahead=("positionOrder_h", lambda s: 0),
                                     ).reset_index()
    g["Hamilton_Ahead"] = g.Constructor.map(m.assign(a=m.positionOrder_h < m.positionOrder_b).groupby("Constructor").a.sum())
    g["Bottas_Ahead"] = g.Constructor.map(m.assign(a=m.positionOrder_b < m.positionOrder_h).groupby("Constructor").a.sum())
    return g.sort_values(["Shared_Races", "Constructor"], ascending=[False, True])


def p4(res):
    x = res[(res.circuitId == 6) & (pd.to_datetime(res.date) < "2020-01-01") & ~res.status.isin(NON_START)]
    g = x.groupby(["driverId", "Driver"]).agg(Starts=("raceId", "nunique"), Avg_Finish=("positionOrder", "mean"),
                                              Wins=("position", lambda s: int((s == 1).sum()))).reset_index()
    g = g[g.Starts >= 5]
    return g.sort_values(["Avg_Finish", "Wins", "Driver"], ascending=[True, False, True])[
        ["Driver", "Starts", "Avg_Finish", "Wins"]]


def p5(res):
    x = res[res.year.isin([2020, 2021])]
    e = x.groupby(["driverId", "year", "constructorId"]).size().rename("n").reset_index()
    e = e.sort_values(["driverId", "year", "n", "constructorId"], ascending=[True, True, False, True])
    prim = e.groupby(["driverId", "year"]).constructorId.first().unstack().dropna()
    changed = prim[prim[2020] != prim[2021]].index
    d = csv("drivers").set_index("driverId").loc[changed]
    d = d.assign(s=d.surname.str.strip(), f=d.forename.str.strip()).sort_values(["s", "f"])
    names = (d.f + " " + d.s).tolist()
    return pd.DataFrame([{"Drivers_Changed": len(names), "Drivers": names}])


# ---------------------------------------------------------------- compare

def same(a, b):
    if isinstance(a, list) or isinstance(b, list):
        return list(a) == list(b)
    if isinstance(a, float) or isinstance(b, float):
        return abs(float(a) - float(b)) <= TOL
    return a == b


def compare(n, graph_rows, expected):
    exp = expected.to_dict("records")
    cols = list(expected.columns)
    problems = []
    if graph_rows and list(graph_rows[0].keys()) != cols:
        problems.append(f"columns {list(graph_rows[0].keys())} != {cols}")
    if len(graph_rows) != len(exp):
        problems.append(f"{len(graph_rows)} rows vs {len(exp)} expected")
    for i, (g, e) in enumerate(zip(graph_rows, exp)):
        bad = [c for c in cols if not same(g.get(c), e[c])]
        if bad:
            problems.append(f"row {i}: " + ", ".join(f"{c}: graph={g.get(c)!r} csv={e[c]!r}" for c in bad))
            if len(problems) > 5:
                break
    print(f"Query {n}: {'PASS' if not problems else 'FAIL'}  ({len(graph_rows)} rows)")
    for p in problems:
        print("   ", p)
    return not problems


def main():
    queries = load_queries(HERE / "queries.txt")
    res = frames()
    expected = {1: p1(res), 2: p2(res), 3: p3(res), 4: p4(res), 5: p5(res)}
    cfg = read_config(HERE / "config.txt")
    ok = True
    with GraphDatabase.driver(cfg["URI"], auth=(cfg["USERNAME"], cfg["PASSWORD"])) as drv, \
            drv.session(database=cfg.get("DATABASE") or None) as s:
        for n in sorted(queries):
            rows = [r.data() for r in s.run(queries[n])]
            ok &= compare(n, rows, expected[n])
            for r in rows[:5]:
                print("     ", r)
            if len(rows) > 5:
                print(f"      ... {len(rows) - 5} more")
    print("\nALL PASS" if ok else "\nSOME FAILED")


if __name__ == "__main__":
    main()
