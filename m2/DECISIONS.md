# Milestone 2: decisions the brief doesn't cover

This file lists every choice made in `Create_kg.py` that the M2 brief does not spell out:
what we added, what we kept as-is on purpose, and what we found in the data while
checking it. The numbers come from a full scan of the 9 CSVs and from the loaded graph
(local Neo4j 2026.10.2, 9 Nov 2026).

**Result of the load:** 51,113 nodes and 163,510 relationships, matching the brief.
Every property has exactly one type, no value is `\N` or an empty string, and a second
run changes nothing.

---

## 1. Value cleaning: what we changed and what we kept

**Rule: we only remove spaces from the start and end of values. We never rewrite a
value.** The brief says nothing about cleaning, and the grader's private queries are
presumably written against the raw data. So spelling differences stay as they are, and
are listed here so nobody is surprised by them.

| # | Finding | Decision |
|---|---|---|
| A | **Trailing space in a nationality.** Franco Colapinto (driverId 861) is `"Argentinian "` in drivers.csv. | **Stripped.** Every string value is trimmed at load time, so he's stored as `"Argentinian"`. It was the only value in the 9 files with extra spaces; the graph now has none. |
| B | **Two spellings of one nationality.** Colapinto is `"Argentinian"`, while the 24 earlier Argentine drivers are `"Argentine"`. | Kept as in the CSV. A query for Argentine drivers needs `IN ['Argentine', 'Argentinian']`. It's the only such pair; East German and Rhodesian are real historical values. |
| C | **Two spellings of one country.** 11 US circuits have `circuit_country = "USA"`, and Las Vegas Strip (circuitId 80) has `"United States"`. | Kept as in the CSV. |
| D | **HTML entity in a name.** Constructor 201 is `"Lotus-Pratt &amp; Whitney"`. | Kept as in the CSV. |

---

## 2. Choices about missing values

- **Trimming.** Every value is trimmed before it's converted (see 1A).
- **What counts as missing.** The brief names the literal `\N` and the empty `q2`/`q3`
  cells. We treat **any** `\N`, empty or whitespace-only cell as missing. In practice only
  `q2` (22 cells) and `q3` (46 cells) are empty; every other gap is `\N`.
- **Missing means the property is absent**, never `null`, `""` or `"\N"`. In a query, an
  absent property reads as `null`, so `WHERE x IS NULL` works.
- **Zero is a value, not a gap.** These zeros are real entries in the CSV, so we keep them:

  | Value | Rows | Meaning |
  |---|---|---|
  | `grid = 0` | 1,638 | pit-lane start, or grid unknown (617 are before 1980) |
  | `laps = 0` | 2,532 | retired on lap 1, or did not start |
  | `rank = 0` | 258 | no fastest-lap rank recorded |
- **How often values are missing:**

  | Field | Present | Missing |
  |---|---|---|
  | `Driver.number` | 59 / 861 | numbers only exist from 2014 |
  | `Driver.code` | 104 / 861 | |
  | `Race.time` | 394 / 1,125 | missing before 2005 |
  | `Result.position` | 15,806 / 26,759 | DNFs and other non-finishers |
  | `Result.time`, `milliseconds` | 7,680 | only for drivers who finished |
  | `Result.fastestLap`, `fastestLapTime`, `fastestLapSpeed` | 8,252 | |
  | `Result.rank` | 8,510 | |
  | `Result.number` | 26,753 | |
  | `Qualifying.q1` | 10,338 / 10,494 | |
  | `Qualifying.q2` | 5,847 / 10,494 | |
  | `Qualifying.q3` | 3,629 / 10,494 | |

## 3. Choices about types

The brief fixes the types, and we follow it exactly. These are the details it leaves open:

- **Dates** become Neo4j `DATE` values. Python `date` objects are converted by the driver.
- **`eventId`** is built as `"raceId:driverId:stop"` from the integer values, e.g.
  `"1052:1:1"`.
- **Long pit stops keep their minutes.** `PitStop.duration` stays a string, as the brief
  says, so long stops look like `"51:09.017"`. Use `milliseconds` for any maths.
- **Race times stay as given.** `Race.time` is a string like `"15:00:00"`. We did not
  convert time zones.

## 4. What the graph leaves out on purpose

- **Columns not in the schema are not loaded:** `url` in every table, and the session
  columns in races (`fp1_date` to `sprint_time`).
- **Foreign keys are not stored as properties.** `Result` has no `raceId` or `driverId`
  property: the `FOR_RACE` and `BY_DRIVER` relationships replace them. To get a result's
  race, follow the relationship (`(res)-[:FOR_RACE]->(r)`).
- **Exception:** `Race.year` is both a property and the `IN_SEASON` link, because the
  schema lists `year` on Race.

## 5. Duplicates: what we checked

- **No duplicate keys** in any table. That covers driverId, constructorId, circuitId,
  year, statusId, raceId, resultId, qualifyId, and `(raceId, driverId, stop)` for pit
  stops. The `Ref` columns and race `(year, round)` are also unique.
- **No two drivers share a full name**, and no two constructors share a name. A
  `forename + ' ' + surname` column therefore identifies one driver, but queries should
  still group by ID.
- **Shared drives are kept as separate Results.** 85 `(race, driver)` pairs have two
  Result rows, because in the 1950s two drivers could share one car (79 of the pairs are
  from that decade, 7 are at Monaco). Each row is its own Result node. This is what the
  brief's Q4 warning is about: count starts as distinct races.
- **Some race positions are shared too.** 123 `(race, positionOrder)` repeats and 82
  `(race, position)` repeats come from the same shared drives.
- **Driver numbers and codes repeat across eras.** 22 drivers share a race number with
  someone else (e.g. 44, 10, 99), and 7 codes repeat. These are **not** unique keys, so
  they have no constraint.
- **Same name, different team.** Renault (id 4) and Alpine (id 214) are different
  constructor nodes, as are Lotus-Climax, Lotus-Ford, Team Lotus and the other Lotus
  variants. We never merge teams by name. Q5 relies on this.

## 6. Odd values we kept

| Finding | Rows | Decision |
|---|---|---|
| Pit stops longer than 10 minutes, up to 51:09 (2022 British GP, raceId 1083). Red-flag stoppages: Australia 2023 alone has 46. | 460 (517 over 60 s) | Kept. They're real records. Filter them in a query if needed. |
| Fractional points (1.33, 3.14, 4.14 …), from shared drives and split fastest-lap points in the 1950s | dozens | Kept as floats. |
| Points earned without a classified position (1950s fastest-lap point while retired) | 16 | Kept. |
| `positionText` is a number but `position` is missing (raceId 71, resultIds 1149 and 1152) | 2 | Kept as in the CSV. We don't fill `position` from `positionText`. |
| Circuit altitude below sea level (Baku, −7 m) | 1 | Kept. It's real. |
| Dual nationality written as one value: Alfonso Thiele `"American-Italian"`, Alessandro de Tomaso `"Argentine-Italian"` | 2 | Kept as one string. The schema has a single `nationality` property, so it isn't split. |
| Status `"Not classified"` (statusId 62) | — | Kept. It is **not** a classified finish for Q2: the brief counts only `"Finished"` and statuses starting with `"+"`. |

## 7. Nodes with no links

The brief's 51,113 counts every CSV row, so these are loaded even though nothing links
to them:

- **Constructor 88, Eagle:** has no Results or Qualifying rows.
- **Statuses 133 (`"+49 Laps"`) and 134 (`"+38 Laps"`):** never used by any Result.

Everything else is linked. Every race has results; the data covers 1950 to 2024 (75
seasons, 24 races in 2024). Qualifying data starts in 1994 and pit-stop data in 2011,
so questions about qualifying or pit stops before then return nothing.

## 8. Engineering choices in the script

| Choice | Why |
|---|---|
| File named `Create_kg.py`, capital C | The brief's exact deliverable name. A Linux autograder treats `create_kg.py` as a different file. |
| CSVs and `config.txt` read from the script's own folder | The brief says "same directory". The script works no matter which folder it's launched from. |
| Config parsed by key: case-insensitive, split on the first `=`, spaces stripped, blank lines and `#` lines skipped | The brief requires reading by key. Splitting on the first `=` keeps a password that contains `=`. |
| `DATABASE=` used if present, otherwise the server default | The brief forbids hardcoding a name. The grading config has the line; ours doesn't. |
| Files read as `utf-8-sig` | Handles files re-saved with a byte-order mark (e.g. by Excel). Accented names like Pérez and Räikkönen load correctly. |
| A uniqueness constraint on each node key | Not required by the brief. It blocks duplicates at the database level, and its index makes `MERGE` fast. |
| `MERGE` on the key only, then `SET n += props` | Re-runs update the node instead of duplicating it. |
| Relationships `MERGE`d, each type in its own pass | A broken foreign key would drop only that one link, not the node. Re-runs don't add second arrows. |
| Loaded in `UNWIND` batches of 2,000 rows | One round trip per 2,000 rows. A full load takes about 30 s. |
| Prints a warning if a link can't find its parent | No link is ever skipped silently. Today it never fires: all foreign keys resolve. |
| Uses `session.run()`, not `driver.execute_query()` | Works with any neo4j driver version from 4.x to 6.x. Tested with 5.0.1 and 6.4.1. |
| CSV copies, `config.txt` and Neo4j credential downloads are gitignored | The data stays in `data/`, and passwords stay off GitHub. |

## 9. Notes for the queries (`queries.txt`)

- **Points are Grand Prix points only.** Sprint results aren't in the graph, as the brief
  says.
- **Q2:** a classified finish is `status = "Finished"` or a status starting with `"+"`.
  `"Not classified"` doesn't count.
- **Q4:** shared drives exist at Monaco (7 pairs), so count starts as distinct races.
- **Q5:** compare constructors by ID, since Renault (4) and Alpine (214) have different
  IDs.
- **Group by ID, display by name.** Names happen to be unique today, but grouping by ID
  doesn't depend on that.
