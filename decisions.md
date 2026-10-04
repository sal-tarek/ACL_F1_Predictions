# Decisions log: pre-cleaning profile of our 11 tables (Sasa and Dany)

Source: `sasa-dany-ms1-pre-cleaning.ipynb`, steps P0 to D3. Every line names the step that proved it, so the evidence is one search away.
Our 11 tables: `seasons`, `circuits`, `drivers`, `constructors`, `status`, `sprint_results`, `driver_standings`, `lap_times`, `pit_stops`, `constructor_standings`, `constructor_results`.

How to read it:
- **Section 1** is what the data forces us to do (apply it in the cleaning task).
- **Section 2** is what the team still has to decide (with our proposal).
- **Section 3** lists the odd cases to **record in the data-quality log and not fix**.
- **Section 4** lists the facts that belong in the report's limitations and leakage sections.

The raw CSV files were never changed: D3 compares the fingerprint of every raw table with the one taken in P0 (13 tables, 0 changed). The cleaning task writes to a new (silver) layer and leaves the raw files alone.

---

## 1. Rules that follow from the data

### Keys and joins
- **Driver key = `driverId` only.** Never join on `code`, `number` or names (A5). **Circuit key = `circuitId` only**, never name or `location` (A2, A3). **Team key = `constructorId`**, but it is not one continuous team: some teams were renamed or split by engine, and some ids were reused across eras (A8).
- All 15 keys of our 11 tables are unique and all 20 links have 0 orphans; the notebook stops with an error if that ever changes (D1).
- **Join recipe:** build the driver-race table from `results` (one row per driver per race), then left-join the other tables on (`raceId`, `driverId`) or (`raceId`, `constructorId`). The extra rows in `driver_standings` (8,664), `constructor_standings` (892) and `constructor_results` (7) then drop out by themselves (D1, B3, B5, B6).
- **`raceId` is not in date order** (61 ids are earlier than the id before them). Order and lag by season + `round` (or the date), never by `raceId` (B4). Inside a season `round` is in date order (B4).

### Time and leakage (what may be used before the race)
- **Standings (drivers and teams): use only the row from the previous round of the same season.** The row under the same `raceId` already contains that race and that weekend's sprint points (B3, B4, B5). Evidence: with the same-race standings the rank correlation with the finishing order is 0.56 instead of 0.46, and the winner leads the table 48.4% of the time after the race against 32.8% before it (B4).
- **Round 1** of each season has no earlier standings (75 races, 6.5% of starts): use a documented start value plus a flag (B3, B4, B5).
- **No standings row yet = 0 points and 0 wins, but the position stays unknown, never 0** (B3, B4). For teams the same holds, except the Indianapolis 500 chassis of 1958 to 1960, which never get a row and stay out of team features (B5).
- **`statusId` is never a feature** (it is only known after the race); use it only for question 3 and for past-race DNF rates (A9).
- **`constructor_results`, `lap_times` and `pit_stops` of race R belong to race R:** they may only enter features for later races (B6, C1, C3).
- **Age at the race date is allowed** (known before the race) (A6). The sprint result is allowed in time, but see Section 2 (B2).

### Missing values and column handling
- Read `\N` as missing in an exploring copy and keep the raw text untouched (P0).
- **Do not fill** `drivers.number` and `drivers.code` (they are labels; their absence only means "the era before they existed") (A5). **Do not fill the empty sprint cells** (they mean "did not finish") (B1).
- **Drop** `url` columns (A1, A2), `constructor_results.status` after recording the McLaren 2007 fact (B6), and `pit_stops.time` (local clock time, cannot be combined with `races.time`) (C3).
- Use `milliseconds` (already numeric) for lap times, pit stops and the sprint time; if the text is ever parsed, the parser must handle hours (lap) and minutes (pit) (B2, C1, C3).
- Convert `dob` to a date in the silver table; every date of birth is valid (A6). `drivers.number` is only a decimal because of the missing values (A5).

### Scales that cannot be compared across seasons
- **Points** (drivers: 30 to 575 for a champion; teams: 16 to 107 handed out per race) change with the points system: use the gap to the leader, the share of the leader's points, or the rank (B3, B4, B5, B6).
- **Counts per season** (wins, podiums, points) become rates or shares, because seasons range from 7 to 24 races (A1).
- **Lap times** are used relative to the typical lap of their own race (C2). **Stop counts** are not comparable across seasons (1.42 to 2.68 per finisher); stop times are compared within a season (C3, C4).

### Coverage and flags
- Coverage steps up in **1958** (team tables), **1996** (lap times), **2011** (pit stops) and **2021** (sprint) (D2). Use flags `has_team_standing`, `has_lap_data`, `has_pit_data` and `has_sprint`; **never fill the earlier seasons with an average** (D2, B5, C1, C3).
- Keep a **core feature set** that exists in every season (results, grid, standings from the previous round) and an **extended set** (laps, pit stops); report the score per era (D2).
- **Build team form from `results`** (the drivers' points or positions in earlier races), not from `constructor_results`: its meaning changes (best car only until 1978, sprint points from 2021) (B7). Official team points: `constructor_standings` from 1958 with the one-round shift (B5, B7).

### Table-specific cleaning
- **Circuits (A3):** group by `circuitId`; set a minimum number of races before a circuit is ranked (5 per era keeps 16 circuits); never assume one race per circuit per season; flag `alt = 0` as possibly unknown.
- **Countries and nationalities (A4, A7):** merge `United States` into `USA`; join on `country` only; trim spaces and merge `Argentinian` into `Argentine`; keep the written nationality-to-country map as a table in the notebook.
- **Constructors (A8):** compute team form from a recent window only (for example the previous 1 or 2 seasons) so a gap resets it; add a "prior entries" count; set a minimum number of starts; keep Eagle (harmless).
- **Status (A9):** keep the draft grouping of the 139 statuses as a table; the Q3 task finalises it.
- **Lap times (C2):** keep only clean racing laps: drop lap 1, the pit-stop lap and the lap after a stop (2011 on) and laps above the cutoff (Section 2); red-flag laps (above 3 times the typical lap) are always out.
- **Pit stops (C4):** a real stop is up to 60 s; 60 s to 5 minutes is a very slow stop (counts as a stop, out of duration averages); over 5 minutes is a red-flag pause (out of durations and counts). Recount the stops of each driver in each race by sorting on `lap`; do not trust the `stop` number.
- **Standings (B3):** keep `position` numeric and ignore `positionText` (only the 1997 `D` row differs). Points are decimals (276 rows), not integers.
- **Sprint (B1, B2):** use `milliseconds`, not `time`; any sprint feature needs `has_sprint`.

---

## 2. Decisions the team still has to make

| # | Decision | Our proposal | Step |
|---|---|---|---|
| 1 | Use the sprint result in the main model? | No: 1.6% of races, repeats the Sunday grid in 2021 to 2022, adds no podium signal. At most an optional experiment with `has_sprint`. | B2 |
| 2 | Cutoff for a "clean" lap | Start at 1.2 times the race's typical lap (removes 6.6% of laps) and test 1.5 times (1.99%). | C2 |
| 3 | Start value for round 1 standings features | A documented start value (0 points, position unknown) plus a flag; the alternative is last season's final standing. | B3, B4, B5 |
| 4 | Team form before 1958 and in round 1 | Flag it, start the team-feature window in 1958, or derive team form from `results` for every season. | B5, B7 |
| 5 | Q3: grouping of the grey statuses | Finalise the draft grouping, argue each grey status against the brief, report the rates with and without the grey zone and say which is the headline. | A9 |
| 6 | Q2: nationality-to-country map | Finish the map and decide the four mixed or historical nationalities; exclude the Indianapolis 500 from Q2 (or report with and without it). | A4, A7 |
| 7 | Q1: minimum races per circuit | At least 5 races in each era (16 circuits). | A3 |
| 8 | Q3: minimum starts per constructor | Set it, and mention the renames. Exclude the Indianapolis 500 (its constructors are chassis builders). | A8 |
| 9 | Source of a driver's best lap | One source only: `lap_times` (from 1996) or `results.fastestLapTime` (from 2004); they agree for 97.5%. | C2 |
| 10 | Which seasons a model trains on | The brief's windows (2014 to 2021, 2022 to 2024) have full lap and pit coverage; for all seasons use the core set against the extended set. | D2 |
| 11 | The podium label before 1960 | `positionOrder <= 3` gives more than 3 rows in 18 races (shared drives); tell the teammates who profile `results`. | B4 |

---

## 3. Data-quality log: record, do not fix

**Drivers and standings**
- 1997 European GP: Michael Schumacher's row has `positionText` `D`, 78 points and position 26 (last), because he was disqualified from that championship (B3).
- 50 driver-seasons (1950 to 1967, 1979 to 1990) end with fewer standing points than the driver scored (the old "best N results count" rules); Prost 1988 scored 105 and has 87 (B4).
- 3 races (1951 French, 1956 Argentine, 1957 British GP) have two drivers on `positionOrder` 1 (shared car); 18 races between 1950 and 1960 give more than 3 rows for `positionOrder <= 3` (B4).
- 469 race starts have no driver-standings row, 447 of them in the 1990s and 2000s; every start that scored has a row (B3).
- Reused or duplicate labels: 7 shared `code` values, 11 reused `number` values, 45 shared surnames; `driverId` skips 809; three `driverRef` values start with a capital letter (A5).

**Teams**
- McLaren 2007: `E` in `constructor_standings` and `D` in `constructor_results` (17 rows); the points stay, the position is last (B5, B6).
- Team points go down twice: Force India 2018 round 13 (59 to 18) and Racing Point 2020 round 5 (42 to 41) (B5).
- Indianapolis 500 chassis (Epperly, Kurtis Kraft, Watson and others, 1958 to 1960) scored points but have no standings row; the 1958 Indianapolis 500 has no `constructor_results` rows (B5, B6).
- `constructor_results`: 7 rows without a team start (BMW Sauber 2002, Brabham 1979 twice, Marussia 2015 four times); 410 team starts without a row (400 before 1958 and 10 later) (B6).
- 1958 to 1978: `constructor_results` counts only the best car (302 team-races); BRM at the 1959 British GP is a one-off (B7).
- 3 reference rows are never used: constructor Eagle and the statuses +49 Laps and +38 Laps (D1).

**Laps and pit stops**
- 43 lap rows are written with hours (2011 Canadian GP lap 25, 2014 British GP laps 1 and 2): red-flag stoppages (C1).
- 90 driver-races have a different number of laps in `lap_times` and `results` (35 races): the 2014 Chinese GP is +2 for all 20 classified cars; several pairs look swapped (2001 Hungarian, 2001 Japanese, 2009 Italian GP); one disqualified driver at the 2024 São Paulo GP (C2).
- The best lap differs between `lap_times` and `results` in 210 of 8,249 driver-races (C2). The 2005 US GP has lap rows for only 6 cars; the 2021 Belgian GP has a single lap (C1).
- 478 pit-stop rows are red-flag pauses (26 races); 39 are very slow stops; 8 driver-races have odd stop numbers (6 at the 2024 Monaco GP, where the number 70 is a label error; the 2014 British GP and 2019 Singapore GP start at stop 2); 3 stops after the "last lap" belong to the disqualified 2024 São Paulo driver (C3, C4).

**Sprint**
- `grid = 0` in 11 sprint rows is a pit-lane start, not an error (B2). The `time` text matches `milliseconds` in all 340 rows that have one (B2).

---

## 4. Facts for the report (limitations and leakage)

- **Coverage drift (D2 chart):** driver standings cover all 1,125 races, team tables 94%, lap times 48% (from 1996), pit stops 25% (from 2011), sprint 1.6% (from 2021). The brief's two periods are fully covered except the sprint (and the one-lap 2021 Belgian GP for pit stops).
- **Era sensitivity:** points systems (8 or 9 to 25 for a win, 26 with the fastest-lap point in 2019 to 2024, 50 once in 2014), the age of the grid (median 39 in 1950 to 27.9 in 2024), and the mechanical-retirement rate (9.2% to 5.6%) all change with the era (A6, A9, B4).
- **Leakage evidence:** the same-race standings look better (0.56 against 0.46 rank correlation), which is why only the previous round is used (B4). Sprint, qualifying and grid are known before the race; status, results, laps, pit stops and the standings of the same race are not.
- **Immutability:** the raw tables were loaded as text, only exploring copies were changed, and the D3 fingerprint check passes (13 tables, 0 changed).
