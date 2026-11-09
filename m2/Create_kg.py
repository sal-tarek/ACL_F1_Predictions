"""Build the Formula 1 Knowledge Graph in Neo4j (Milestone 2).

Reads the nine CSV files and config.txt from the folder this script is in.
Safe to re-run: every node and relationship is created with MERGE on a
unique key, so a second run creates no duplicates.
"""

import csv
from datetime import date
from pathlib import Path

from neo4j import GraphDatabase

HERE = Path(__file__).resolve().parent
BATCH = 2000


# ---------------------------------------------------------------- config

def read_config(path):
    """Read KEY=VALUE lines by key (the grading config also has DATABASE)."""
    cfg = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            cfg[key.strip().upper()] = value.strip()
    return cfg


# ---------------------------------------------------------------- type helpers
# A missing value (\N or an empty cell) becomes None, and None properties
# are dropped before they reach Neo4j, so the property is simply omitted.
# Values are stripped of leading/trailing spaces (one nationality in
# drivers.csv is "Argentinian " with a trailing space).

def _missing(v):
    return v is None or v.strip() in ("", "\\N")


def as_int(v):
    return None if _missing(v) else int(v.strip())


def as_float(v):
    return None if _missing(v) else float(v.strip())


def as_str(v):
    return None if _missing(v) else v.strip()


def as_date(v):
    return None if _missing(v) else date.fromisoformat(v.strip())


def props(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


def read_csv(name):
    # utf-8-sig also reads files saved with a byte-order mark (e.g. by Excel).
    with open(HERE / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- row builders

def driver_rows():
    for r in read_csv("drivers.csv"):
        yield {"id": as_int(r["driverId"]), "props": props(
            driverId=as_int(r["driverId"]),
            driverRef=as_str(r["driverRef"]),
            number=as_int(r["number"]),
            code=as_str(r["code"]),
            forename=as_str(r["forename"]),
            surname=as_str(r["surname"]),
            dob=as_date(r["dob"]),
            nationality=as_str(r["nationality"]),
        )}


def constructor_rows():
    for r in read_csv("constructors.csv"):
        yield {"id": as_int(r["constructorId"]), "props": props(
            constructorId=as_int(r["constructorId"]),
            constructorRef=as_str(r["constructorRef"]),
            constructor_name=as_str(r["name"]),
            constructor_nationality=as_str(r["nationality"]),
        )}


def circuit_rows():
    for r in read_csv("circuits.csv"):
        yield {"id": as_int(r["circuitId"]), "props": props(
            circuitId=as_int(r["circuitId"]),
            circuitRef=as_str(r["circuitRef"]),
            circuit_name=as_str(r["name"]),
            circuit_loc=as_str(r["location"]),
            circuit_country=as_str(r["country"]),
            lat=as_float(r["lat"]),
            lng=as_float(r["lng"]),
            alt=as_int(r["alt"]),
        )}


def season_rows():
    for r in read_csv("seasons.csv"):
        yield {"id": as_int(r["year"]), "props": props(year=as_int(r["year"]))}


def status_rows():
    for r in read_csv("status.csv"):
        yield {"id": as_int(r["statusId"]), "props": props(
            statusId=as_int(r["statusId"]),
            status=as_str(r["status"]),
        )}


def race_rows():
    for r in read_csv("races.csv"):
        yield {
            "id": as_int(r["raceId"]),
            "circuitId": as_int(r["circuitId"]),
            "year": as_int(r["year"]),
            "props": props(
                raceId=as_int(r["raceId"]),
                year=as_int(r["year"]),
                round=as_int(r["round"]),
                name=as_str(r["name"]),
                date=as_date(r["date"]),
                time=as_str(r["time"]),
            ),
        }


def result_rows():
    for r in read_csv("results.csv"):
        yield {
            "id": as_int(r["resultId"]),
            "raceId": as_int(r["raceId"]),
            "driverId": as_int(r["driverId"]),
            "constructorId": as_int(r["constructorId"]),
            "statusId": as_int(r["statusId"]),
            "props": props(
                resultId=as_int(r["resultId"]),
                number=as_int(r["number"]),
                grid=as_int(r["grid"]),
                position=as_int(r["position"]),
                positionText=as_str(r["positionText"]),
                positionOrder=as_int(r["positionOrder"]),
                points=as_float(r["points"]),
                laps=as_int(r["laps"]),
                time=as_str(r["time"]),
                milliseconds=as_int(r["milliseconds"]),
                fastestLap=as_int(r["fastestLap"]),
                rank=as_int(r["rank"]),
                fastestLapTime=as_str(r["fastestLapTime"]),
                fastestLapSpeed=as_float(r["fastestLapSpeed"]),
            ),
        }


def qualifying_rows():
    for r in read_csv("qualifying.csv"):
        yield {
            "id": as_int(r["qualifyId"]),
            "raceId": as_int(r["raceId"]),
            "driverId": as_int(r["driverId"]),
            "constructorId": as_int(r["constructorId"]),
            "props": props(
                qualifyId=as_int(r["qualifyId"]),
                number=as_int(r["number"]),
                position=as_int(r["position"]),
                q1=as_str(r["q1"]),
                q2=as_str(r["q2"]),
                q3=as_str(r["q3"]),
            ),
        }


def pitstop_rows():
    for r in read_csv("pit_stops.csv"):
        event_id = f'{as_int(r["raceId"])}:{as_int(r["driverId"])}:{as_int(r["stop"])}'
        yield {
            "id": event_id,
            "raceId": as_int(r["raceId"]),
            "driverId": as_int(r["driverId"]),
            "props": props(
                eventId=event_id,
                stop=as_int(r["stop"]),
                lap=as_int(r["lap"]),
                time=as_str(r["time"]),
                duration=as_str(r["duration"]),
                milliseconds=as_int(r["milliseconds"]),
            ),
        }


# ---------------------------------------------------------------- graph writes

CONSTRAINTS = [
    ("Driver", "driverId"),
    ("Constructor", "constructorId"),
    ("Circuit", "circuitId"),
    ("Season", "year"),
    ("Status", "statusId"),
    ("Race", "raceId"),
    ("Result", "resultId"),
    ("Qualifying", "qualifyId"),
    ("PitStop", "eventId"),
]


def node_query(label, key):
    return (
        f"UNWIND $rows AS row "
        f"MERGE (n:{label} {{{key}: row.id}}) "
        f"SET n += row.props"
    )


def rel_query(src_label, src_key, rel, dst_label, dst_key, row_field):
    # Rows whose parent id is missing are skipped (no dangling relationship).
    # Returns how many rows found both ends, so skipped links can be reported.
    return (
        f"UNWIND $rows AS row "
        f"WITH row WHERE row.{row_field} IS NOT NULL "
        f"MATCH (a:{src_label} {{{src_key}: row.id}}) "
        f"MATCH (b:{dst_label} {{{dst_key}: row.{row_field}}}) "
        f"MERGE (a)-[:{rel}]->(b) "
        f"RETURN count(*) AS linked"
    )


# session.run() is used instead of driver.execute_query() because it works in
# every neo4j driver version (4.x to 6.x); execute_query needs driver 5.5+.

def run(session, query, **params):
    return list(session.run(query, **params))


def run_batched(session, query, rows):
    rows = list(rows)
    for i in range(0, len(rows), BATCH):
        run(session, query, rows=rows[i:i + BATCH])
    return rows


def link(session, label, key, rel, dst_label, dst_key, field, rows):
    query = rel_query(label, key, rel, dst_label, dst_key, field)
    linked = 0
    for i in range(0, len(rows), BATCH):
        linked += run(session, query, rows=rows[i:i + BATCH])[0]["linked"]
    expected = sum(1 for r in rows if r[field] is not None)
    if linked < expected:
        print(f"  WARNING: {expected - linked} {label}-[:{rel}]->{dst_label} "
              f"links skipped (parent {dst_label} not found)")


def main():
    cfg = read_config(HERE / "config.txt")
    database = cfg.get("DATABASE") or None  # None = the server's default database

    with GraphDatabase.driver(cfg["URI"], auth=(cfg["USERNAME"], cfg["PASSWORD"])) as driver, \
            driver.session(database=database) as session:
        driver.verify_connectivity()

        for label, key in CONSTRAINTS:
            run(session,
                f"CREATE CONSTRAINT {label.lower()}_{key}_unique IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.{key} IS UNIQUE")

        # 1. Entity (parent) nodes first.
        entities = [
            ("Driver", "driverId", driver_rows),
            ("Constructor", "constructorId", constructor_rows),
            ("Circuit", "circuitId", circuit_rows),
            ("Season", "year", season_rows),
            ("Status", "statusId", status_rows),
        ]
        for label, key, rows in entities:
            n = len(run_batched(session, node_query(label, key), rows()))
            print(f"{label:12s} {n:6d} nodes")

        races = run_batched(session, node_query("Race", "raceId"), race_rows())
        print(f"{'Race':12s} {len(races):6d} nodes")
        link(session, "Race", "raceId", "AT_CIRCUIT", "Circuit", "circuitId", "circuitId", races)
        link(session, "Race", "raceId", "IN_SEASON", "Season", "year", "year", races)

        # 2. Fact nodes, then their links to the parents.
        facts = [
            ("Result", "resultId", result_rows, [
                ("FOR_RACE", "Race", "raceId", "raceId"),
                ("BY_DRIVER", "Driver", "driverId", "driverId"),
                ("FOR_CONSTRUCTOR", "Constructor", "constructorId", "constructorId"),
                ("HAS_STATUS", "Status", "statusId", "statusId"),
            ]),
            ("Qualifying", "qualifyId", qualifying_rows, [
                ("FOR_RACE", "Race", "raceId", "raceId"),
                ("BY_DRIVER", "Driver", "driverId", "driverId"),
                ("FOR_CONSTRUCTOR", "Constructor", "constructorId", "constructorId"),
            ]),
            ("PitStop", "eventId", pitstop_rows, [
                ("FOR_RACE", "Race", "raceId", "raceId"),
                ("BY_DRIVER", "Driver", "driverId", "driverId"),
            ]),
        ]
        for label, key, rows, rels in facts:
            data = run_batched(session, node_query(label, key), rows())
            print(f"{label:12s} {len(data):6d} nodes")
            for rel, dst_label, dst_key, field in rels:
                link(session, label, key, rel, dst_label, dst_key, field, data)

        nodes = run(session, "MATCH (n) RETURN count(n) AS c")[0]["c"]
        rels = run(session, "MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
        print(f"\nTotal: {nodes} nodes, {rels} relationships (expected 51113 / 163510)")


if __name__ == "__main__":
    main()
