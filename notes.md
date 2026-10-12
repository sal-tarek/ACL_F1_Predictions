# Things to understand before evaluation

A checklist for going through sections 7–9 of `acl_milestone1.ipynb`. Tick a box when you can explain it in your own words.

---

## 1. The measuring tools (used everywhere in section 7)

- [ ] **AUC (ROC-AUC).** Pick one random podium row and one random non-podium row. AUC = how often the feature gives the podium row the "better" value. 0.5 = useless (coin flip), 1.0 = perfect. Example: `grid_clean` has 0.885, so in 88.5% of such pairs the podium driver started further up.
  - Why a **minus sign** sometimes: for grid, position, gap and pace, *smaller is better*, so the value is flipped before computing the AUC.
  - How it's computed: the `auc()` helper at the start of section 7 (Mann–Whitney test, which counts exactly those pairs).
- [ ] **PR-AUC.** Like AUC, but it focuses on how well the podium rows are found. It matters because only ~15% of rows are podiums (the classes are imbalanced).
- [ ] **Spearman correlation ("overlap").** How much two features rank drivers the same way. 1 or −1 = they say the same thing, 0 = unrelated. Above ~0.9 means one of them is redundant (`quali_pos` vs grid was 0.96, so it was dropped).
- [ ] **"Same X, different Y" tables.** Compare drivers who are equal on one feature (e.g. the same grid area) but differ on another. If the podium rate still differs, the second feature adds something new.

## 2. Leakage (the most important idea)

- [ ] A feature may only use information known **before the race starts** (after qualifying).
- [ ] `shift(1)` = "leave out the current race" when averaging over previous races.
- [ ] Why `race_pace`, `mech`, `crash` and `statusId` are never features: they're only known after the race.

## 3. The 9 features (section 7, table in 7.10)

For each one, know: how it's calculated, why it's valid before the race, when it's missing. The explanation is under the table in 7.10.

- [ ] `grid_clean`: grid slot; pit-lane starters at the back
- [ ] `grid_minus_quali`: grid − qualifying position (penalties)
- [ ] `quali_gap_pct`: % slower than the fastest Q1 lap
- [ ] `form_podium_rate`: podiums in the driver's last 10 starts
- [ ] `career_starts`: experience
- [ ] `champ_pos`: championship position before this race
- [ ] `team_form`: the team's podiums per car start, last 10 races
- [ ] `team_mech_rel`: the team's breakdown rate minus the field's, last 20 races
- [ ] `pace_form`: the driver's typical lap ÷ the race's typical lap, last 10 starts (only races with 10+ laps; see the worked example in the chat)

Tested and **not** used: circuit history (7.7), sprints (7.9), constructor standings, average finish, wins, points share.

## 4. Seasons and split (section 8)

- [ ] Why 2003: qualifying data is mostly missing in 1996–2002.
- [ ] Split: train 2003–2018, validation 2019–2021, test 2022–2024.
- [ ] Why split by season, not randomly: matches real use, keeps a race's drivers together, and keeps history features honest.
- [ ] Why 2019 stays in validation: a bigger validation set means less noisy scores (±0.016 vs ±0.019).
- [ ] The final model is retrained on 2003–2021 before the test.

## 5. Preprocessing (section 9)

- [ ] **Filling (9.2):** why fill instead of drop (we'd lose every rookie). Know the rule for each feature:
  - `grid_minus_quali` → 0
  - `quali_gap_pct` → the driver's recent median
  - `form_podium_rate` → 0
  - `pace_form`, `team_form`, `team_mech_rel` → the training median
  - `champ_pos` → worst in the race + 1
- [ ] **"Training median":** computed on 2003–2018 only, then used for every part.
- [ ] **Capping (9.3):**
  - `quali_gap_pct` at 7%, from the 107% rule;
  - `team_mech_rel` and `pace_form` at the 1st/99th percentiles of training.
  - Why: a few extreme values come from bad laps or from averages over very few races.
- [ ] **Effect (9.4):** filling barely changes the distributions; capping shortens 3 ranges; the AUC doesn't change.
- [ ] **Scaling (9.5):** (value − training mean) ÷ training std. Needed for logistic regression and the neural network, not for trees. Validation/test means aren't exactly 0, and that's expected.
- [ ] **Order experiments (9.6):**
  1. Learning the values from all seasons leaks the future. The score barely changes here, but it's still wrong.
  2. Scaling before filling changes what the fill values mean (a rookie gets 14% form instead of 0).

## 6. Decisions to be able to defend

- [ ] Renamed teams are not linked to their old name (Brawn 2009 vs Honda 2008).
- [ ] `never_ran` was rechecked for 2003+ (Räikkönen 2017, US GP 2005).
- [ ] Why `pace_form` needs 10+ laps (Stroll, Bahrain 2020: pace 7.8).
- [ ] `pace_form` is still a candidate: the ablation decides.

## 7. Models (section 10.1–10.5)

- [ ] **Why accuracy isn't used:** always saying "no podium" is already 84.9% accurate. Our models get about 91.5%.
- [ ] **ROC-AUC vs PR-AUC vs F1 vs top-3 per race** (10.1), and why the F1 threshold is chosen on validation.
- [ ] **Tuning (Step 1):** try several settings, keep the best one on validation.
- [ ] **How logistic regression works:** a weighted sum turned into a probability. Know how to read the weights chart.
- [ ] **How gradient boosting works:** many small trees, each fixing the last ones' mistakes. Why deep trees memorise.
- [ ] **How the neural network works:** hidden layers, epochs, loss, early stopping. Read the printed progress in 10.4 Step 2.
- [ ] **Why the validation scores are higher than training** (2019–2021 were easier seasons).
- [ ] **The main limitation:** each row is scored on its own, so the models don't know each race has exactly 3 podiums. The grid's top 3 is still as good at picking 3 per race.
- [ ] Still to do: **10.6 ablation** (decides `pace_form`) and **10.7 test** on 2022–2024.

---

## Quick model check (2026-10-12, validation 2019–2021, not in the notebook)

| Model | ROC-AUC | PR-AUC | F1 | Top-3 picks on the podium |
|---|---|---|---|---|
| Grid only (top 3 on the grid) | 0.917 | 0.683 | 0.719 | 72.2% |
| Logistic regression | 0.932 | 0.717 | 0.699 | 67.8% |
| Gradient boosting | 0.938 | 0.745 | 0.729 | 70.6% |

To look into in section 10: the models beat the grid on ROC-AUC and PR-AUC, but not yet on picking the top 3 within each race.
