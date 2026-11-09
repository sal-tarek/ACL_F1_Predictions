# Milestone 2: what the M1 EDA means for the knowledge graph

This file goes back over the M1 notebook's EDA (`acl_milestone1.ipynb`, sections 1–3) for
the 9 tables in the graph. For each finding it asks two questions:

1. Does it change how `Create_kg.py` builds the graph?
2. What must a Cypher query do so the finding doesn't give a wrong answer?

Every number below was re-checked on the loaded graph with Cypher (local Neo4j,
9 Nov 2026), not copied from M1. Where the graph gives a different number from M1, the
reason is stated.

**Short answer:**
- **`Create_kg.py` needs no change.** The graph keeps every source row, as the brief's
  counts require, so each M1 cleaning decision becomes a choice made in the query instead.
- **The queries need about 20 rules**, listed in section 4.

---

## 1. Why the graph and M1 handle the same data differently

M1 built a **modelling table**: one row per driver per race, cleaned for a podium model.
M2 builds a **knowledge graph** that has to represent the dataset, with exactly the
brief's counts (51,113 nodes, 163,510 relationships), and that the grader queries with
questions we haven't seen. So the M1 fixes that removed or changed rows aren't applied to
the graph. They become things a query has to handle.

| M1 decision (cleaned copy) | In the graph | Why |
|---|---|---|
| Removed 91 duplicate driver-race rows (kept the best `positionOrder`) | All 26,759 Results kept | The brief counts 26,759 Result nodes. Shared drives are real history. |
| Excluded the 11 Indianapolis 500 races from the model | Kept | They're in races.csv, and the brief counts them. |
| Flagged and dropped the 1,366 failed-to-qualify rows | Kept as ordinary Results | Same reason. |
| `United States` → `USA`, `Argentinian ` → `Argentine` | Only the trailing space is removed; spellings stay raw | The grader presumably queries the raw values. See DECISIONS.md §1. |
| Added numeric seconds columns (`q1_s`, `duration_s`, `fastestLapTime_s`) | Not added. Times stay strings, as the brief requires | The schema fixes the types. |
| Set the 16:42.640 Q1 outlier to missing in `q1_s` | Kept as the string `"16:42.640"` | The brief only allows omitting missing values. |
| Labelled 478 pit stops as red-flag pauses | Kept; nothing marks them | No such property exists in the schema. Queries filter by `milliseconds`. |

**Could we add extra properties** (e.g. `is_indy500`, a cleaned country)? The brief
forbids removing or renaming, not adding. But those properties would be our
interpretation, the grader's queries won't use them, and they would make the graph
differ from the schema the brief specifies. Decision: **no extra properties.**

---

## 2. Findings by table: M1 result, graph check, consequence

### Results (26,759 nodes)

| # | M1 finding | Checked on the graph | Consequence for queries |
|---|---|---|---|
| R1 | 85 driver-race pairs have 2–3 rows: shared drives (76 in 1950–57) plus 3 drivers entered in two cars | 85 pairs, up to 3 rows. 16 pairs have **two different constructors** | Per-driver-per-race counts ("starts", "races entered") must count **distinct races**, not Result nodes. A driver can be linked to two teams in one race. |
| R2 | Shared cars both credited with one place: 87 shared places in 45 races; 18 races have more than 3 podium rows (1950–60) | 18 races have more than 3 rows with `positionOrder <= 3`. **3 races have two `position = 1` rows**: 1951 French (Fagioli, Fangio), 1956 Argentine (Musso, Fangio), 1957 British (Brooks, Moss) | Win and podium counts credit both drivers of a shared car. That's correct, but "winners per race" can be 2. "Finished ahead" must use a strict `<`, so a tie counts for neither driver. |
| R3 | `position` missing for 10,953 rows. 2 classified rows (2005 Australian GP: Button 11th, Sato 14th) have no `position` | **26** rows have status `Finished` or `+N Laps` but no `position`: those 2, plus 24 coded `N` (not classified) or `R` | `position` doesn't measure classification. **Order by `positionOrder`**, which is never missing. A win is `position = 1`, as the brief defines it; every winner has `position`. |
| R4 | `grid = 0` in 1,638 rows. 72 are pit-lane starters who raced; the rest never started | 72 rows with laps > 0, best finish 5th | `grid = 0` is not a grid slot. Leave it out of grid averages and "positions gained", or treat it as a back-of-grid start. Pole = `grid = 1`. |
| R5 | "Did not start" isn't a single column. Non-starters use statuses like Injury, Engine or Brakes (code W), and Lammers 1981 is coded R | **58** Results with `grid = 0` and 0 laps still count as starts under the brief's rule (statuses: 107% Rule, Injury, Safety concerns, Underweight, Accident, Excluded, Engine …) | For the brief's Q4, apply the brief's status rule **literally**, as the grader expects. Mention the gap if asked. |
| R6 | 7 podium finishers have status Accident or Out of fuel (1966–99) | 7 | Status doesn't decide podium or classification. `positionOrder` does. Q2's "classified" is the brief's own status rule, so use it as written. |
| R7 | 12 rows score points from 12th or lower (1950s fastest-lap point) | 16 Results have points but no `position` | Points don't imply a classified finish. Sum points over **all** Results. |
| R8 | `time` mixes 6,552 gaps (`+5.478`) and 1,128 full race times in 21 formats | Same: 6,552 / 1,128 | Never sort or compare `Result.time`. Use `milliseconds`, which exists only for finishers on the lead lap. |
| R9 | Taylor, 1960 Dutch GP: 78 laps while the winner did 75 (likely a typo) | max 78, winner 75 | Kept. "Most laps" style queries could pick this row. |
| R10 | Points scales change across eras; 2021 Belgian GP gave half points | 2021 Belgian winner has 12.5 points | Season totals are fine; totals across eras aren't comparable. Q1 gives Verstappen **388.5**: Grand Prix points only, without the sprint points in his official 395.5. |

### Qualifying (10,494 nodes)

| # | M1 finding | Checked on the graph | Consequence for queries |
|---|---|---|---|
| Q1 | Data starts in 1994, but 1996–2002 covers only 6–59% of races | — | Qualifying answers before 2003 are incomplete. Say so. |
| Q2 | 156 entries have no time at all; the whole 1995 Australian GP field has positions but no times | — | `Qualifying.position` is always present; the times often aren't. Rank by `position`. |
| Q3 | One Q1 time is `16:42.640` (1995 Japanese GP) | It's the only Q1 time of 10 minutes or more. **As a string it sorts before `1:38.023`**, so a string `min()` names it the fastest lap of that race | **Never take `min`/`max` of `q1`/`q2`/`q3`/`fastestLapTime` as strings.** Convert first: `toInteger(split(t,':')[0])*60 + toFloat(split(t,':')[1])`. |
| Q4 | `q2`/`q3` are missing for drivers knocked out earlier (by design) | 5,847 / 3,629 present | A missing `q3` means "knocked out", not "unknown". Don't fill it. |
| Q5 | (not in M1) | **10 entries in 2015** have Qualifying linked to *Marussia* and the Result linked to *Manor Marussia* (Stevens, Merhi, Rossi) | The team can differ between a driver's Qualifying and Result in the same race. Use the Result's constructor for race questions and the Qualifying's for qualifying questions. |
| Q6 | One row per driver per race | No Qualifying row lacks a matching Result | Joining Qualifying to Result on race + driver is safe. |

### Races (1,125 nodes)

| # | M1 finding | Checked on the graph | Consequence for queries |
|---|---|---|---|
| RA1 | `raceId` is not chronological: the first rows are 2009 races | The lowest raceId is the 2009 Australian GP; the earliest date is the 1950 British GP | **Order races by `date`** (a real Neo4j DATE) or by `(year, round)`, never by `raceId`. |
| RA2 | A circuit can host two races in one season (2020, 2021) | 4 circuit-seasons | Circuit + year doesn't identify a race. Use the Race node. |
| RA3 | One circuit can have several Grand Prix names (Nürburgring has 4); the Indy circuit also hosted the US GP 2000–07 | **16 race names are used at more than one circuit** (Australian, Spanish, British, German, European …) | Filter by circuit with `circuitId`, not by race name, unless the question names the race. |
| RA4 | `time` is recorded only from 2005, in UTC | 394 present | Questions about race start time cover 2005 onwards only. |
| RA5 | 11 Indianapolis 500 races (1950–60): 95% of their drivers never raced elsewhere | 11 races, **405** Results (M1 had 381 after removing duplicates), **31** constructors that raced only there (M1: 30) | All-time counts (most entries, American drivers, constructors per nationality) include Indy. Leave it in unless a question excludes it. Identify it by race name (`'Indianapolis 500'`), not by circuit. |
| RA6 | Season length runs from 7 races (1950) to 24 (2024) | — | Compare seasons with rates, not totals. |

### Circuits (77 nodes)

| # | Finding | Consequence for queries |
|---|---|---|
| C1 | The US is spelled `USA` at 11 circuits and `United States` at Las Vegas Strip (M1 merged them on its cleaned copy) | Use `IN ['USA','United States']`. |
| C2 | Countries are nouns (`UK`, `Germany`) while nationalities are adjectives (`British`, `German`), so none match exactly | A "home race" query needs an explicit country-to-nationality map. |
| C3 | Altitude runs from −7 m (Baku) to 2,227 m; Yeongam and Miami are at 0 m | Real values. A 0 here is a value, not a missing one. |

### Drivers (861 nodes)

| # | Finding | Consequence for queries |
|---|---|---|
| D1 | `number` and `code` aren't identifiers: 11 numbers and 7 codes are reused (Michael and Mick Schumacher are both `MSC`) | Match drivers by `driverId`. Never join on code or number. |
| D2 | Full names are unique (forename + surname, checked) | The brief's `Driver` column (full name) is safe to output. Still group by the node or ID. |
| D3 | `Argentine` (24) and `Argentinian` (1, Colapinto). Dual nationality `American-Italian` and `Argentine-Italian`; historical `East German` and `Rhodesian` | Nationality filters need both spellings. Dual nationalities don't match a plain `'Italian'` filter. |
| D4 | `number` exists only for drivers active from 2014; `code` mostly from the 2000s | A missing property means "didn't exist in that era". |

### Constructors (212 nodes)

| # | Finding | Consequence for queries |
|---|---|---|
| K1 | One team can have several IDs: 50 constructors share a Wikipedia page in 13 groups (Cooper 11, Team Lotus 7, Brabham 6). Renames get a new ID (Marussia → Manor Marussia, Renault → Alpine) | A team's history by name finds only one ID. Q5 tells us to compare by ID, so a rename counts as a change. |
| K2 | One ID can cover separate eras: Mercedes 1954–55 and 2010–24 (checked) | All-time totals per constructor mix eras. |
| K3 | Eagle (88) has no Results | Queries that start from Results never see it. To list it with 0 entries, start from Constructor and use `OPTIONAL MATCH`. |
| K4 | Names are unique | Outputting `constructor_name` is safe. |

### Status (139 nodes)

| # | Finding | Consequence for queries |
|---|---|---|
| S1 | One column mixes finishes, `+N Laps`, failures, crashes, non-starts and rulings | Use the brief's definitions exactly: classified = `'Finished'` or starts with `'+'`; non-start = `'Did not qualify'`, `'Did not prequalify'`, `'Withdrew'`. |
| S2 | Unclear labels: `Not classified` (172 rows), `Retired`, `Mechanical`, `Technical` | `Not classified` is **not** classified for Q2. |
| S3 | `+49 Laps` and `+38 Laps` are never used | Unlinked nodes, harmless. |

### PitStop (11,371 nodes)

| # | M1 finding | Checked on the graph | Consequence for queries |
|---|---|---|---|
| P1 | Covers 2011–2024; the 2021 Belgian GP has none (abandoned) | 0 pit stops, 20 Results | Pit-stop answers start in 2011, and a missing stop isn't a "0-stop strategy". |
| P2 | 478 stops over 5 minutes are red-flag pauses; 39 are slow stops of 1–5 minutes | 478 / 39 | For stop counts or average durations, exclude `milliseconds > 300000`. Use medians if possible. |
| P3 | `duration` has two formats (`23.4` and `1:29.401`) | As strings, `'1:29.401' < '23.426'` is **true** | Sort and compare by `milliseconds`, never by `duration`. |
| P4 | `stop` is wrong in 8 driver-races: 2024 Monaco stops are numbered 15–70, and two drivers start at stop 2 | 8 driver-races where `max(stop)` ≠ the number of stops | Count stops with `count(p)`, not `max(p.stop)`. `eventId` is still unique. |
| P5 | `PitStop.time` is local clock time, 1–9 h off from `Race.time` (UTC) | — | Don't combine the two. |
| P6 | 3 classified finishers have no stop (at most 2 rows missing) | — | Negligible. |

---

## 3. Effect on `Create_kg.py`

| Finding | Could the script change? | Decision |
|---|---|---|
| Shared drives (R1, R2) | Remove duplicates as M1 did | **No.** The brief requires 26,759 Results, and they're real. |
| Indy 500 (RA5) | Leave out or flag | **No.** Same reason. |
| Spelling variants (C1, D3) | Normalise | **No.** Raw values stay; only spaces are trimmed (DECISIONS.md §1). |
| Q1 outlier (Q3) | Omit it as M1 did | **No.** It isn't a missing value, so the brief's omit rule doesn't apply. |
| Red-flag pit stops (P2) | Flag | **No.** No property for it in the schema. Filter in queries. |
| Wrong `stop` numbers (P4) | Recount | **No.** `stop` is the source value and part of `eventId`, which the brief defines. |
| Time strings (Q3, P3, R8) | Store numbers | **No.** The brief requires strings. Convert in queries. |
| Missing values, types, keys | — | Already handled (DECISIONS.md §2–5). |

**Conclusion:** the script is correct as it stands. Every finding is handled either by
keeping the source data faithfully or by a rule in the queries.

---

## 4. Rules for writing queries

1. **Identify things by node or ID**, never by name, code, number, race name, or circuit + year.
2. **Order races by `r.date`** (or `r.year, r.round`), never by `raceId`. Compare dates with `date('2020-01-01')`.
3. **Finishing order = `positionOrder`.** Wins = `position = 1`. `position` is missing for 10,953 rows, including 26 with a classified status.
4. **Count distinct races** when the question is per driver per race (starts, entries per driver). Result nodes ≠ races in 85 cases.
5. **Average and sum over all Result nodes** unless the question says otherwise (Q4 says to use all remaining Results).
6. **Use the brief's status definitions exactly**: classified = `Finished` or `+…`; non-start = DNQ, DNPQ, Withdrew. `Not classified` is neither.
7. **Never compare time strings** (`q1`–`q3`, `fastestLapTime`, `Result.time`, `duration`). Use `milliseconds`, or convert `m:ss.sss` to seconds in Cypher.
8. **`grid = 0` is not a slot.** Leave it out of grid-based averages.
9. **A missing property reads as `null`.** `count(x)` counts nodes, `count(x.prop)` counts present values, and `avg`/`sum` skip nulls.
10. **Pit stops:** use `count(p)`, not `max(p.stop)`, and exclude `milliseconds > 300000` for real stop durations.
11. **Coverage limits:** qualifying from 1994 (complete from 2003), pit stops from 2011, race start times from 2005.
12. **Spellings:** `Argentine`/`Argentinian`, `USA`/`United States`, adjectives vs country names.
13. **Indy 500 is in the graph.** Exclude it by race name only when a question asks for that.
14. **A team can differ between Qualifying and Result** (Marussia 2015). Take the constructor from the fact the question is about.
15. **Strict `<` for "ahead of"**, so shared places count for nobody.
16. **Sort by an exact average.** Neo4j's `avg()` can be off in the last digit
    (`4.000000000000001`), which flips the order of two drivers whose averages are really
    equal (Vettel and Stewart at Monaco are both 6.25). Use
    `toFloat(sum(x)) / count(x)` when a tie-break depends on it.
17. **Every returned column needs `AS` with the brief's exact name.** Round decimals to no fewer than 2 places.

## 5. What this means for the brief's 5 queries

| Query | Findings that apply | What to do |
|---|---|---|
| **Q1** 2021 points and wins | R10 (half points at Spa), R2 (no shared cars in 2021) | `sum(points)`, wins = `position = 1`, group by driver node. Expect Verstappen 388.5. |
| **Q2** Reliability 2014–21 | S1, S2, K1 (renamed teams are separate IDs) | Entries = Result nodes per constructor ID; classified uses the brief's rule; `HAVING` ≥ 100 per ID; reliability as a 0–1 float. |
| **Q3** Hamilton vs Bottas | R1, R2, rule 15 | Pair Results in the same race with the **same constructor node**; compare `positionOrder` with strict `<`. |
| **Q4** Monaco before 2020 | R1 (7 shared-drive pairs at Monaco), R5, rule 2 | Circuit by `circuitId: 6`; `r.date < date('2020-01-01')`; drop the 3 non-start statuses; Starts = `count(DISTINCT race)`; average finish and wins over all remaining Results; ≥ 5 starts. |
| **Q5** Primary constructor 2020 vs 2021 | R1, K1 (Renault 4 → Alpine 214) | Entries per (driver, season, constructor ID) = Result nodes; tie → lower `constructorId`; compare IDs; only drivers with entries in both seasons; one row. |
