# Changes to the notebook

Every change we make to `acl_milestone1.ipynb`, section by section: **where**, **what** and **why**. New sections are added at the bottom.

---

## Section 1: Initial EDA (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | New headings **1.1**, **1.2**, **1.3**; the summary is now **1.4** | Each check got a short heading and a "why" line. | Four code cells sat in a row with no explanation. The brief asks for the reason behind each EDA choice, and headings make the notebook easier to navigate. |
| 2 | **1.4**, *Hidden missing values* | Now says 8 of the 9 text columns in `results` (11 of 14 in `races`) are text because of `\N`. The rest are text anyway (names, dates, `positionText`). | The old sentence said all of them were text because of `\N`. |
| 3 | **1.1** code + **1.4** text | Prints where qualifying's 68 missing cells are (`q2`, `q3`, in 2023 and 2024), plus one sentence explaining them. | The overview table showed these 68 cells, but nothing explained them. |
| 4 | **1.2** code + **1.4**, *Coverage over time* | Prints the share of races with qualifying data for 1994–2003. The text now says 94% in 1994 (not "complete"), then 6–59% until 2002. | 1994 was not complete: one race (Monaco) has no qualifying rows. |
| 5 | **1.3** code + **1.4**, *The target* | Prints the repeated pairs (85), the rows in them (176) and the extra rows (91). | Section 1 said 176, while sections 3 and 4 say 91. Both are right, and now both are shown. |
| 6 | **1.3** code + **1.4**, *The target* | New check: podium rows per race. 18 races (1950–1960) have more than 3. | Every race should have exactly 3 podium rows. This problem was only shown later, in section 2. |

**Not changed:** the four existing checks, the three charts and every number from before. Only the three edited code cells were re-run; all other outputs in the notebook are untouched. The full notebook was then run top to bottom with no errors.

---

## Section 2: Audit and cleaning (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | New cell at the end of section 2: **Key checks for all 14 tables** | One table that checks every table's key (unique, never empty) and every foreign key (no orphans). All 14 pass. | The brief asks to check keys for all tables. `lap_times` and `pit_stops` had no foreign-key check before. |
| 2 | `qualifying`, the "share missing per year" cell + the qualifying summary | Added a heatmap of missing Q1/Q2/Q3 times per season, plus one sentence. | The 31-row table was hard to read. This pattern is the reason training starts in 2003, so it needs a picture. |
| 3 | `pit_stops`, the long-stops cell + the pit_stops summary | Added a histogram of stop lengths with lines at 60 s and 5 minutes. | It shows the empty gap that makes the 5-minute cutoff safe. A threshold decision should come with a picture. |
| 4 | `results`, *Keep rule for duplicated pairs* | One new reason: all 85 pairs are from 1950–1978, so the rule cannot change the model, Q1 or Q3. | This is the strongest argument for the rule, and it was missing. |
| 5 | `pit_stops`, the two conversion cells | Deleted the first one. The second does the same conversion and now also shows the example rows. | The same code ran twice. |
| 6 | `driver_standings`, the "standing minus scored" cell | Removed a stray space at the start of the cell. | It is invalid Python outside Jupyter, and the editor showed it as an error. |
| 7 | `results` (2 cells) and `lap_times` (1 cell) | Removed the printed "(expected 1563)", "# expect 72" and "(expect 19)". The lap_times cell now checks its number with an `assert`. | A printed expected number looks as if the answer was known in advance. |
| 8 | `results`, the `QYEAR = 2003` line | The comment now gives the reason ("first year with complete qualifying coverage") instead of "change after reading the table". | The old comment sounded like a manual edit, which the brief does not allow. |
| 9 | `circuits`, `status`, `lap_times` (3 cells) | `pd.set_option(...)` became `with pd.option_context(...)`. | The old line changed the display setting for the whole notebook. Now it only affects its own table. |
| 10 | `lap_times`: extreme-laps cell + its text | Prints the slowest race (2021 Belgian GP, 1 lap) and the text now explains it. | The text said "we have not yet checked which race this is". |
| 11 | `results`, *What a duplicated pair looks like* | "We have not checked the others" now says that the next cell checks all 85 pairs. | The old sentence was out of date. |
| 12 | `pit_stops` conversion cell + text, and section 3's type table | The pit stop clock time stays as text, like the race start times in `races`. The `time_of_day` column was removed. | The two tables treated the same kind of column in two different ways. |

**Not changed:** every check, decision and number from before. Only the 12 edited code cells were re-run (sections 0–2 run again in a scratch copy); all other outputs in the notebook are untouched.

---

## Section 3: Cleaning summary (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **3.1** *What the modelling table is* | Now says only `lap_times` is summarised (for the pace feature, 7.8), and `pit_stops` is cleaned but not used as a feature. Also mentions joins on `constructorId`. | It said both tables are summarised and joined, but `pit_stops` is never used. |
| 2 | **3.3** *Features that must look backwards only* | Round 1 now uses the previous season's final position (as decided in 7.4), instead of "0 and a flag". | The old rule was changed in section 7, so the summary contradicted it. |
| 3 | **3.3**, same sentence | Gives both match rates: 99.8% (drivers) and 99.3% (constructors). | 99.8% was only true for the driver standings. |
| 4 | **3.6** *Missing values* | Removed "a flag marks the filled values"; now points to the fill rules (9.2) and the order experiments (9.6). | No flags are added in section 9. |
| 5 | **3.2** *Rows we remove or mark* | "91 duplicate driver-races" → "91 extra rows in 85 duplicate driver-races". The pit-lane row now says `grid_clean` (and `grid` is unchanged). | Same wording as sections 1 and 2, and more exact. |
| 6 | **3.4** *Numbers that are not comparable* | The old "best car only" and "best results only" rules are now marked as F1 history. | The tables show the gaps, not the rules. Section 2 already says so. |
| 7 | New **3.8** *Keys, joins and two more fixes* | Four short points: all keys pass, join only on ids, the impossible 1,002.6 s qualifying time, team history restarting after a 5-season break. | These section 2 decisions were missing from the summary. |
| 8 | Section 2, `results` anomaly-check cell | One new print: "shared finishing places: 87, rows in them: 184, seasons 1950 to 1961". | Section 3 quotes these numbers, so the code must print them. |

**Not changed:** the 7 existing subsections and their structure. Only one code cell (the anomaly check) was re-run (sections 0–2 in a scratch copy); all other outputs are untouched.

---

## Section 4: EDA after cleaning (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **4.3** column types cell | Re-ran it. The pit_stops "added" list is now `duration_s, kind`. | Its saved output still showed `time_of_day`, which was removed in section 2. |
| 2 | **4.4** target and grid cell | One new print: podiums among the never_ran rows (0) and the Indy 500 rows (36). | The summary quoted these numbers, but no cell printed them. |
| 3 | **4.5** summary | "91 shared-drive rows removed" → "91 duplicate rows removed". | 3 of the 91 are drivers entered in two cars who started in neither, not shared drives. |
| 4 | **4.2** missing values cell + the summary | A small table of missing values for all 14 tables (before and after cleaning), plus one sentence. `post_clean` moved up one cell so this table can use it. | Section 1 checks all 14 tables, so the "after" check should too. |
| 5 | New headings **4.1**–**4.4**; the summary is now **4.5** | Each check got a short heading and one sentence saying why. | Section 4 mirrors section 1, which already has headings 1.1–1.4. |

**Not changed:** the four checks, the charts and every number from before. Only the three edited code cells were re-run (sections 0–4 in a scratch copy); all other outputs are untouched.

---

## Section 5: Modelling table, phase 1 (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | Section 5 code cell | The combined table is now called `base` (it was `m`) and gets the target column `podium`. The joins and the three checks are the same. | Nothing used `m`: the name `m` is reused in section 6, so the table was lost. The intro also says this table has the target. |
| 2 | Section 7, first code cell | `fe` now takes its columns from `base` instead of joining `results_unique` and `races` again. | The same table was built twice. A check confirmed that `fe` is exactly the same as before. |
| 3 | Section 5 intro | Each next step now has its section number (7, 9.1 and 9.7, 8, 9), plus one sentence: section 7 uses this table. | The plan is now also a map of the notebook. |
| 4 | Section 5 intro | "scale and encode" → "scale". "keep the training seasons" → "keep the seasons 2003–2024". | Nothing is encoded (all features are numbers), and the kept seasons include validation and test. |

**Not changed:** the joins, the checks, and every number after section 5. Only the two edited code cells were re-run (in a scratch copy up to section 7's first cell); `fe` was checked to be identical to the old one.

---

## Section 6: Data-engineering questions (13 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | Q1, Q2 and Q3 intros | Each now has a **Missingness:** sentence, next to Grain and the pre-race cutoff. | The brief asks each answer to justify its grain, missingness and cutoff. Only Q1 said anything about missing values. |
| 2 | Q2, *1.1* check table | One new row: missing values in season, circuit country and nationality (0). | This check was a silent `assert`, so nothing was shown. |
| 3 | Q3, *1. The data* | One line under the table: missing values in season, status, status group and constructor (0). | Same reason as #2. |
| 4 | Q3, Part B answer + the answers table | "should not be credited to the 2022 rules" → "the data does not show that the 2022 rules caused it". "Was it the 2022 rules? mostly not" → "Did the drop come with the 2022 rules? mostly before 2022". | The limitations say Q3 is descriptive only and does not show *why* reliability changed. The answer now says when the drop happened, not what caused it. |

**Not changed:** the methods, the charts and every number. The two `assert` checks stay. Only the four edited code cells were re-run (sections 0–6 in a scratch copy); all other outputs are untouched.

---

## Section 10: Models, finished (14 Oct 2026)

New subsections at the end of section 10, plus small edits to keep the older text correct.

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | New **10.6** *The final model* | Gradient boosting is chosen as the final model. A new check redraws the 60 validation races 1,000 times: gradient boosting is clearly better than the baseline (+0.035 PR-AUC, range +0.002 to +0.068), and not clearly different from the network. | The ablation, the test and the explanations need one final model, chosen before the test. |
| 2 | New **10.7** *Feature-group ablation* | Four experiments on the 7 feature groups: one group removed (gradient boosting and logistic regression, with ranges), each group alone, every pair removed (heatmap), and all 127 combinations. Decision: all 7 groups (9 features) are kept; `pace_form` is no longer a candidate. | The brief asks for a feature-group ablation. Removing one group at a time can mislead when groups overlap, so the other three experiments show what the groups know alone and together. |
| 3 | New **10.8** *The final test* | The three models are trained again on 2003–2021 (preprocessing learned again on 2003–2021, the network for a fixed number of epochs) and scored once on 2022–2024, with the thresholds chosen on validation. Test table, every model on every part, ranges, ROC and PR curves, confusion matrices, and the most confident mistakes. | The brief asks for every model's score on the unseen test set. Section 8.2 planned the retraining on 2003–2021. |
| 4 | New **10.9** *Primary and secondary metric* | PR-AUC is the primary metric and F1 the secondary, with a table and prints as evidence (ROC-AUC is high even for the grid; answering "no podium" for everyone gives 84.9% accuracy). | The brief asks for a justified primary/secondary metric choice. |
| 5 | Section 10 intro, **10.1**, **10.2** | The intro now says the test part is used once (10.8). 10.1 names F1 as the second score. The ablation reference in 10.2 is now 10.7. | The old text said the test was never used and pointed to 10.6 for the ablation. |
| 6 | Notebook settings (`kernelspec`) | The kernel name `.venv (3.9.21)` became `.venv`. | Antigravity renames it when it opens the notebook. With the old name, the notebook was marked as changed on opening, so the IDE did not reload it when the file changed on disk and kept showing an old copy. |
| 7 | **10.4** and **10.5** readings, **10.6** | Network numbers updated to this run: best epoch 133 → 105, PR-AUC over 5 seeds 0.735 → 0.736, range of the six networks 0.730–0.748 → 0.731–0.748. 10.5 and 10.6 no longer say gradient boosting has the best top-3 per race (the network has 71.7% against 71.1%). | The network gives slightly different numbers on different computers (the old outputs came from a Mac). The whole notebook was run again, so the text must match the new outputs. |

| 8 | New **Experiment 5** in 10.7 (*one feature removed*), the 10.7 intro and the decision | Each of the 9 features is removed on its own (gradient boosting with ranges, and logistic regression). No feature makes the model clearly better when removed, so all 9 stay; `grid_minus_quali` changes the score by only −0.001. The intro table lists the fifth experiment, and the decision is now *the final features*. | Experiment 1 removes whole groups. Two groups hold two features, so one of them could be useless while the other is needed. |
| 9 | **10.9** evidence print and reading | The final model's accuracy is printed next to the accuracy of answering "no podium" for everyone (validation 91.5% against 84.9%, test 89.5% against 84.9%). | It shows with a number why accuracy is not used as a metric. |

**Not changed:** sections 0–9 and the logistic regression and gradient boosting results. The whole notebook was run top to bottom (609 cells, no errors, no warnings). In sections 0–9 only the order of tied rows in a few tables and line breaks in some printed text differ from before; no number changed.

---

## Section 11: Explainability, new (14 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | New **11.1** *Permutation importance* | Each feature is shuffled 20 times on the test part and the drop in PR-AUC of the final model is measured (table and chart). | The brief asks for permutation importance as a global explanation. |
| 2 | New **11.2** *SHAP* | SHAP contributions for every test row, with a check that they add up to the model's score; a bar chart, a beeswarm chart and a chart of the grid slot's contribution. | The brief asks for SHAP as a global explanation. The grid chart shows the curved effect that logistic regression cannot learn. |
| 3 | New **11.3** *Do the explanations agree?* | One table that puts permutation importance, SHAP and the ablation (10.7, experiment 5) side by side, with ranks. | The three measures answer different questions, so where they agree the conclusion is stronger. |
| 4 | New **11.4** *One prediction explained with SHAP* | Two test rows chosen by a rule (the least certain pole-sitter, the most certain driver from P5 or further back), each with a waterfall chart. | The brief asks for at least one local explanation. Two drivers with the same probability for opposite reasons show what the model relies on. |
| 5 | New **11.5** *LIME* | A LIME explanation of the same Verstappen prediction, compared with SHAP. | The brief's checklist names LIME for the local explanation. Comparing it with SHAP shows that both agree, and that LIME is only approximate. |
| 6 | New **11.6** *What the explanations show, and what they do not* | The statement that importance is not proof of cause, with two examples. | The brief asks to state this explicitly. |
| 7 | `report/figures/xai/` | The 7 charts of section 11 are saved for the report. | The XAI charts must also be in the report. |

**Not changed:** sections 0–10. The whole notebook was run top to bottom (645 cells, no errors, no warnings).

---

## Section 10: network numbers that hold on any computer (15 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **10.4** intro | One note: the network's exact numbers depend on the computer, so the text gives rounded values and the outputs give this run's numbers. Logistic regression and gradient boosting gave the same numbers everywhere. | The notebook was run on two computers (Daniel's and a Mac). The network's best epoch was 105 on one and 133 on the other, and a few of its scores moved in the third decimal. |
| 2 | **10.4** reading | "range 0.731–0.748, best epoch 105" → "about 0.73–0.75", and the best epoch is read from Step 2 (about 100–140). "0.736 ± 0.010" → "about 0.735 ± 0.010". | Same reason. |
| 3 | **10.5** reading | The network's top-3 per race "slightly higher: 71.7%" → "about the same: 70–72% depending on the run". | On the Mac run it was 70.6%, lower than gradient boosting's 71.1%, so the old sentence was only true on one computer. |
| 4 | **10.6** reading | The range of gradient boosting minus the network → "about −0.013 to +0.02". | The upper end was +0.021 on one run and +0.022 on the other. |
| 5 | **10.8** reading | "F1 is 0.674–0.679" → "0.67–0.68"; the network "150 with 89 false alarms" → "about 150 with about 90". | The network's test F1 was 0.677 on one run and 0.673 on the other. |

**Not changed:** every code cell and every output. Only these five text cells were edited. The whole notebook was also run top to bottom on the Mac (645 cells, no errors): apart from the network, every number is the same as in the saved outputs, and only the order of tied rows in a few section 2 tables differs.

---

## Section 2: out-of-date sentences (18 Oct 2026)

Seven sentences in section 2 described plans that later sections changed. They now say what the notebook actually does.

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **2. Audit and cleaning**, intro | The flagged rows are "removed in section 5" → "removed in 9.1, when the modelling table is built after the history features". | Section 5 only builds the base table. The rows are removed in 9.1. |
| 2 | `results`, *Summary of anomaly checks* | "if an all-years training window is chosen, shared-drive cars would need to be collapsed" → the all-seasons version in 10.8 keeps them as recorded, because every model scores each row on its own (as section 3 says). | 10.8 trained on 1950–2018 without collapsing them, so the old sentence contradicted it. |
| 3 | `qualifying`, *summary of checks* | "**Plan for features** … we may build" → "**Features built from it** … section 7.2 builds"; "we will test it in the ablation yet to come" → the features are `quali_gap_pct` and `grid_minus_quali`, and the ablation (10.7) tests them. | The plan was carried out in 7.2 and 10.7. |
| 4 | `races`, *missing values*, "One caveat" | "This only matters if the training window reaches 2021" → the model's seasons include 2021 (validation, final training) and 2022 (test), so on these 6 sprint weekends `grid_minus_quali` partly reflects the sprint; 6 of 428 races, so the effect is small. | The training window does reach 2021. |
| 5 | *circuits and drivers: countries and nationalities* | Removed "the `is_home` feature must use the same map"; now says the model has no home-race feature because Q2 found no home advantage. "excluded from both" → "excluded from Q2". | No `is_home` feature exists in the notebook. |
| 6 | `driver_standings`, *structure, keys and what a row means* | Round 1 "start at 0 and are marked with a flag" → the driver's final position of the previous season is used (7.4). | 7.4 changed the round-1 rule; section 3 was already fixed on 13 Oct, but section 2 still had the old rule. |
| 7 | `driver_standings`, *is a row written before or after its race* | Round 1 starts "get 0 points with a flag" → the previous season's final position is used (7.4). | Same as #6. |

**Not changed:** every code cell, every output and every number. Only these 7 markdown cells were edited (one line each), so nothing needed to run again.

---

## Section 4: out-of-date sentence (18 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **4.5** *What the cleaning changed*, "Rows" | The flagged groups are "removed in section 5, after the history features" → "removed in 9.1, when the modelling table is built after the history features". | Section 5 only builds the base table; the rows are removed in 9.1. Same fix as in the section 2 intro. |

**Not changed:** every code cell, every output and every number. Only this one markdown cell was edited, so nothing needed to run again.

---

## Section 7: readings match the outputs again (18 Oct 2026)

The written readings in 7.1–7.9 still quoted the run before the 17 Oct changes (the F-only removal rule moved the model rows from 24,577 to 24,921). 41 numbers now match the outputs printed above them, and 4 sentences were updated. The meaning of every reading is unchanged.

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **7.1** reading | Slots 4–10: 17% → 16%; AUC 0.885 → 0.887. | Match the printed output. |
| 2 | **7.2** reading and decision | Coverage 99.8% / 98.4% → 99.7% / 98.3%; 72.5% / 6.3% → 72.6% / 6.4%; gap AUC 0.826 → 0.827. | Same. |
| 3 | **7.3** reading and decision | N = 20: 0.843 → 0.844; N = 50: 0.830 → 0.831; "within 0.005" → "within 0.006"; experience AUC 0.659 → 0.661; short vs full window 44.1% / 55.8% → 46.3% / 55.7%. "missing for the 683 debuts" → "missing at every debut". | Same; no cell printed 683. |
| 4 | **7.4** reading and decision | Coverage 96.5% (88.2% + 8.2%) → 96.3% (88.0% + 8.4%); points share 0.836 → 0.837; win rate 0.724 → 0.725; AUC 0.840 → 0.841; round 1: 0.803 / 0.790 → 0.805 / 0.789; "3.5% with no value" → 3.7%. | Match the printed output. |
| 5 | **7.5** reading | Coverage 98.8% → 98.7%; restarts 22 → 23; points share 0.842 → 0.841. | Same. |
| 6 | **7.6** reading | Coverage 98.8% → 98.7%; 0.653 / 0.610 → 0.651 / 0.611; 20 races 0.669 → 0.668; driver rate 0.616 → 0.612; Spearman 0.76 → 0.75; crash rate 0.569 → 0.568; AUC 0.669 → 0.668. | Same. |
| 7 | **7.7** step 3 and reading | "Only real starts count, as for driver form" → every entry counts except failed qualifications and the Indianapolis 500; 41.4% → 41.1%. | The old wording contradicted 7.3; the number matches the output. |
| 8 | **7.8** reading and decision | Coverage 46% → 45%; same-row AUCs 0.872 / 0.881 → 0.871 / 0.880; 62.0% / 43.2% → 61.8% / 43.5%; 6.7% → 6.5%. The decision now adds: training starts in 2003 (8.1) and the ablation keeps pace (10.7). | Match the output; the "candidate" was decided later. |
| 9 | **7.9** reading | "only 236 starts" → 240. | Match the printed output. |
| 10 | **7.10** *How each feature is calculated* | "count real starts only" → count every entry except failed qualifications and the Indianapolis 500. | Same wording fix as #7. |

**Not changed:** every code cell and every output. Only these 11 markdown cells were edited, so nothing needed to run again. Numbers read off charts were spot-checked and already matched.

---

## Section 8: one number pair (19 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **8.3** *Reading*, first bullet | "Training is slightly lower (14.1% against 15.1%)" → "(14.0% against 15.0%)". | Match the table printed above it (same cause as the section 7 refresh). |

**Not changed:** every code cell and every output. Only this one markdown cell was edited.

---

## Section 9: readings match the outputs again (19 Oct 2026)

Same cause as section 7: the readings quoted the run before the 17 Oct row rule. 21 numbers now match the outputs, and 2 phrases were updated.

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **9** intro, step table | "9.1 Rows: keeps the drivers who started" → keeps every driver except those who failed to qualify. | The 17 Oct rule. |
| 2 | **9.2** reading | "150 of 8,909 rows" → 8,966; `grid_minus_quali` 21 → 24; "141 of the 144 gaps" → 145 of 148. | Match the printed tables. |
| 3 | **9.3** intro, *What a percentile is* | Limits −0.164 / +0.319 → −0.165 / +0.356; Caterham's 0.92 "becomes 0.319" → 0.356. | Match the printed limits. |
| 4 | **9.3** reading | 106 → 107 rows above 7%; "7 of 106 (6.6%)" → 7 of 107 (6.5%); limits as in #3; 127 → 126 training rows; pace limit 1.053 → 1.054; 128 → 130 training rows. | Match the printed tables. |
| 5 | **9.4** reading | "change by at most a few thousandths" → adds "except for `champ_pos` (next point)"; `team_mech_rel` −0.26…0.92 → −0.23…0.92, capped −0.16…0.32 → −0.17…0.36; `pace_form` 1.053 → 1.054. | The champ_pos mean moves by 0.22, as the next point says; the rest match the table. |
| 6 | **9.5** intro | `team_mech_rel` "about −0.16 to +0.32" → −0.17 to +0.36. | Match the capped range. |

**Not changed:** every code cell and every output. Only these 6 markdown cells were edited.

---

## Section 10: readings match the outputs again (19 Oct 2026)

Same cause as sections 7 and 9: the readings quoted the run before the 17 Oct row rule. In that run gradient boosting was clearly better than the baseline and the championship position was clearly needed. In the saved outputs neither is true, so 13 statements were rewritten and about 37 numbers updated. Each reading keeps its style and its limitations.

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **10.2** reading | Validation PR-AUC for `C` ≥ 0.1: 0.715–0.717 → 0.713–0.717; training 0.677 → 0.675; podium share 15.1% / 14.1% → 15.0% / 14.0%; grid 0.683 / 0.620 → 0.676 / 0.617. | Match the printed tables. |
| 2 | **10.3** reading | "The best settings are depth 2" → depth 2 and 3 are tied (0.744–0.746) and depth 3 is fixed in the code; depth 5: 0.980 / 0.700 → 0.985 / 0.684; "loss still falling, lowest at 285 trees" → lowest after 193 trees (0.2083), then almost flat (0.2090); "beats the baseline on every score" → on the ranking scores (PR-AUC 0.744, ROC-AUC 0.940, top-3 70.6%), F1 the same (0.729 vs 0.730); max career starts 321 → 324. | Match the tuning table, the loss print and the scores table. The code comment already says depth 3 is fixed. |
| 3 | **10.4** reading | Chosen network "two hidden layers (32, 16), small weight decay, best epoch 100–140" → one hidden layer of 32, no weight decay, best epoch 215; ±0.010 → ±0.008; chosen run 0.748 → 0.746; gradient boosting 0.752 → 0.744. | Match the tuning table, the training print and the seed print. |
| 4 | **10.5** reading | Ranges 0.932–0.941 / 0.717–0.752 / grid 0.683 → 0.932–0.940 / 0.717–0.746 / 0.676; "gradient boosting is the best model" → it and the network are practically tied (best ROC-AUC vs best PR-AUC); extra complexity 0.035 / 3 points → about 0.03 / 2–3 points; F1 0.732–0.738 → 0.729–0.735, podiums found and false alarms → 142/67, 132/50, 143/66; "training at most 0.002 above validation" → at most 0.009 (gradient boosting); grid top-3 130 (72.2%) / 128 (71.1%) → 129 (71.7%) / 127 (70.6%). | Match the comparison table, the gap table and the confusion matrices. |
| 5 | **10.6** reading | "Clearly better than the baseline (+0.035, range +0.002 to +0.068)" → not clearly better (+0.027, range −0.005 to +0.055); network +0.004 → −0.002 (range −0.027 to +0.024); "best validation PR-AUC (0.752)" → best ROC-AUC (0.940), PR-AUC tied with the network; ±0.010 → ±0.008. | The printed table says "no" for both comparisons. Gradient boosting is still chosen: the same model every run, tied on PR-AUC, simpler, exact SHAP. |
| 6 | **10.7** intro | Network spread ±0.010 → ±0.008. | Match 10.4. |
| 7 | **Experiment 1** reading | 0.752 → 0.665 (−0.082) → 0.744 → 0.665 (−0.080); "championship position also clearly needed (−0.012)" → only the grid is clear, the other five losses are −0.003 to −0.007 and not clear; qualifying +0.003 → +0.007; logistic regression "agrees on two groups" → agrees on the grid, others within ±0.007. | The printed table says "yes" only for the grid. |
| 8 | **Experiment 2** reading | Alone: 0.683 / 0.629 / 0.596 / 0.587 / 0.582 / 0.496 / 0.231 → grid 0.677, standings 0.630, pace 0.596, team form 0.590, driver form 0.575, qualifying 0.493, reliability 0.245; guessing 0.151 → 0.150; driver form "costs nothing (+0.002)" → costs only 0.003. | Match the table (pace now comes before team form). |
| 9 | **Experiment 3** reading | Overlap examples rewritten from the heatmap: standings + reliability −0.017, reliability + pace −0.017, pace + standings −0.013, team form + reliability or pace −0.011; grid pairs −0.065…−0.099 → −0.070…−0.103; driver form (and qualifying) pairs −0.010 to +0.013. | The old pairs (−0.024, −0.021, −0.020, −0.019) are not in the chart. |
| 10 | **Experiment 4** reading | "Grid + standings reach 0.743" → grid + pace reach 0.746 (all 9: 0.744); best of 3–6 groups 0.755–0.763 → 0.751–0.761; 30 → 36 of 127 within 0.01; best set "grid, standings, team form, reliability, pace 0.763, +0.010 (−0.010 to +0.028)" → grid, standings, pace 0.761, +0.017 (−0.005 to +0.038). | Match the table and the two prints. |
| 11 | **Experiment 5** reading | "Same two clearly needed" → only `grid_clean` (−0.080); `grid_minus_quali` range → −0.006 to +0.004; `quali_gap_pct` +0.000 → +0.008; 72.5% → 72.6%; qualifying + pace −0.019 → −0.004; `form_podium_rate` / `career_starts` +0.002 each → +0.000 / −0.007; logistic regression ±0.008 → ±0.007. | Match the table and the heatmap. |
| 12 | **Decision: the final features** | "Two groups are clearly needed" → only the grid; pace 0.582 / 0.012 / about 0.020 → 0.596 / 0.004 / 0.011–0.017; reliability 0.231 / −0.006 / −0.009…−0.018 → 0.245 / −0.007 / −0.011…−0.017; driver form and qualifying "lose nothing" → lose little or nothing. | Follows from experiments 1–5. The decision itself (keep all 9 features) does not change. |
| 13 | **10.8** reading | Gradient boosting 0.727 / 0.748 → 0.719 / 0.744; range −0.042 → −0.049 to +0.005. | Match the A-vs-B table. |
| 14 | **10.9** version B reading | Gradient boosting 0.717 / 0.702 → 0.716 / 0.705; "F1 lower for logistic regression and the network" → lower for all three. | Match the test A-vs-B table. |
| 15 | **10.9** reading | Final model 0.707 / 0.939 / 0.674 / 66.7% → 0.705 / 0.938 / 0.645 / 64.7%; grid gap 0.055–0.070 over 0.647 → 0.059–0.072 over 0.645; model order and best F1 / top-3 (now the network: 0.682, 66.7%); gradient boosting − logistic regression −0.010 (… +0.018) → −0.012 (… +0.015); misses "about 0.85" → 0.82–0.86; 25 most confident 20 → 22; validation → test 0.752 → 0.707, F1 0.738 → 0.674, grid 0.683 → 0.647 → 0.744 → 0.705, 0.729 → 0.645, 0.676 → 0.645; podiums found / false alarms 147/85, 146/80, ~150/~90 → 129/67, 144/80, 147/80. New bullet: gradient boosting's threshold (0.421) finds fewer podiums on test (recall 0.733 → 0.632), so its test F1 (0.645) is just below the grid's (0.647); it is not retuned. | Match the test tables and the confusion matrices. The new bullet says openly what the table shows. |
| 16 | **10.10** reading | Models' ROC-AUC 0.932–0.941 → 0.932–0.940; PR-AUC gap +0.069 / +0.070 → +0.070 / +0.072; "63% right, 72% found" → 66% right, 63% found; F1 over the grid +0.030 → +0.035 on test for the best model, and the final model's test F1 (0.645) is just below the grid's (0.647); accuracy 84.9% / 91.5% / 89.5% → 85.0% / 91.8% / 89.6%. | Match the metrics table and the prints. |

**Not changed:** every code cell and every output. Only these 16 markdown cells were edited. Every decision stays the same: gradient boosting is the final model and all 9 features are kept; only the reasons quoted for them now match the outputs.

---

## Section 12 and report section 7: two phrases that overclaimed (19 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **12** intro, step 1; **12.2** reading, last bullet; **report** section 7 | "Any of them can be missing" / "Every feature has a fill rule" → any feature can be missing except `grid_clean` and `career_starts`, which are always known at the cutoff (the grid is set, career starts are a count); the 7 others each have a fill rule. | 9.2 has no fill rule for these two, because they are never missing at the cutoff. The old wording promised more than the function does. |
| 2 | **12.2** reading; **report** section 7 | Zhou's filled `champ_pos` of 20 "behind every other driver" → behind every driver who has a standing; Albon, Magnussen and Hülkenberg (back after a season out) had none either and are also filled with 20. | Checked in the raw 2021 final standings: these three have no 2021 standing, so they get the same fill. |

**Not changed:** every code cell and every output. Only markdown cells 682 and 689 were edited. The report PDF was exported again from report.md (still 28 pages).

---

## Sections 11 and 12 after the rework, Kaggle numbers, and the report (19 Oct 2026)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **11** (all code cells) | XAI now explains **both models carried forward**, `opt_gb['A']` and `opt_gb['C']`, as scored in 10.9, with each option's own test inputs (`opt_X[o]['test']`) and units (`opt_capped[o]`). Every method (permutation, group permutation, SHAP global and per season, waterfalls, LIME, whole race) runs for both, side by side. C's figures are saved with `_C`. A check confirms both models give exactly the probabilities of 10.9. | 11 used `gb_final`, which is now the retrained A-GB that 10.9 does not report, so its numbers mixed two models (handoff, item 2). Both models are carried forward (10.6), and comparing their explanations shows how A and C differ. |
| 2 | **11.3** | The agreement table is now per **group**: group permutation, group SHAP (contributions added up per row) and the change in experiment 1 of 10.7 (`leave_one`), with ranks and Spearman per option. | `leave_one_feature` (experiment 5) no longer exists (handoff, item 1); the ablation now works on groups. |
| 3 | **11.5** | LIME is built per option on that option's training rows (2003–2018 for A, 1950–2018 for C); the two extra features of C are treated as categories. | It was built on 2003–2021 (`X_final`), which is not the training part of the reported model. |
| 4 | **11** setup cell | Installs `shap` and `lime` with pip if missing. | They are not always installed on Kaggle. |
| 5 | **12** | `predict_podium(record, option='A' or 'C', race_worst_champ_pos=None)` uses the option's model, fill values, caps, scaler and threshold (`opt_gb`, `opt_learned`, `opt_caps`, `opt_scaler`, `opt_gb_threshold`). It refuses a record without `grid_clean`, `career_starts` or, in C, the two extra features. 12.1 and 12.2 show both models and check both against 10.9. | It used the retrained model and the 2003–2021 preprocessing. A missing grid slot used to pass silently to the model. |
| 6 | **11–12** readings | All rewritten from the Kaggle run. New findings: C-GB uses only 4 of its 11 features (grid, team form, driver form, standings), with the reasons from 9.2, 9.4 and 10.3; its probabilities are less extreme; A spreads the correction over all 9 features. | The old text described one model and quoted old numbers (handoff, item 4). |
| 7 | **10.4**, **10.5**, **10.6** readings | Network numbers matched to the Kaggle run: 0.730 → 0.731 (B), 0.740 → 0.741 (C), ±0.019 → ±0.020 and 0.701–0.752 → 0.699–0.753 (C seeds), 0.723 → 0.724 (B mean), +0.007 → +0.006 (C network in 10.6). | The network moves slightly between computers (as 10.4 says). Every other output of sections 0–10 is identical on Kaggle and in Salma's run. |
| 8 | Notebook outputs | The notebook now holds the outputs of the Kaggle run (Python 3.13). | These are the numbers the evaluator sees. |
| 9 | **report** sections 4–8 | Rewritten for the options design: the three training-season options, the split and option D, per-option preprocessing and its effect, both order experiments, the three models per option with settings and limitations, validation and test tables with every metric for every model, the carried-forward models, the ablation for A and C, the random split, the final test, XAI for both models, the new inference function and updated limitations. §3: the teammate grid-gap trial (no longer in the notebook) removed from "tested and not used". | The report still described one retrained final model and the old numbers. |
| 10 | **report** figures | Every figure re-exported from the Kaggle outputs; `mod_08_random_split` and the five `xai_*_C` figures added; `mod_08_ablation_pairs`, `mod_09_ablation_combinations`, `mod_10_ablation_feature_removed` and `prep_01_fill_cap_effect` removed (their experiments or chart no longer exist). PDF exported again from report.md. | The figures were from the old notebook. |

**Not changed:** the code and outputs of sections 0–10, and every decision in them. The pace group is still labelled "pace (candidate)" in the code (handoff, item 5); the report calls it "pace". On a local computer with scikit-learn 1.9.1, option C's tuning chose depth 3 instead of depth 2; the Kaggle run matches Salma's run.

---

## XAI additions after the review (19 Oct 2026, second Kaggle run)

| # | Where | What we changed | Why |
|---|---|---|---|
| 1 | **10.3** reading | "Trees can use the two flags…" → a tree *could* use them, but 11.2 shows option C's model never splits on them; its gain comes from the features with real values in every season. | The old sentence contradicted the XAI results. |
| 2 | **11.2**, new chart 5 | The grid's SHAP contribution coloured by team form, and a table by grid slot and team form, for A and C (`xai_13_grid_team_interaction`). | Gradient boosting was chosen partly for interactions; nothing showed one. Result: a small interaction (the grid adds up to 0.5 less for a strong team at the same slot); both models are close to additive. |
| 3 | **11.3**, new *The baseline* | Logistic regression's contributions (weight × scaled value, log-odds) next to the SHAP sizes, with rank agreement. | It ties gradient boosting on the test part and was not explained. Result: same top features (rank agreement 0.70 in A, 0.59 in C), different amounts. |
| 4 | **11.3**, new *Can the probabilities be read as chances?* | Calibration table and chart on the test part, expected vs real podiums, Brier score, sum of probabilities per race (`xai_14_calibration`). | The readings called probabilities "chances" and C "less extreme" without a check. Result: A is well calibrated; C is under-confident above about 0.4. |
| 5 | **11.4** miss reading, **11.2** reading, 11 overview table | "If well calibrated, one in six at 0.84 and more than one in three at 0.63" → the calibration results (82% of A's predictions above 0.8 reached the podium; 78% of C's predictions in 0.6–0.7). | The calibration check showed the C half of the claim was wrong. |
| 6 | **10.9** code comment | "keeps the names used in section 11" → kept for reference only. | Sections 11 and 12 no longer use `gb_final`. |
| 7 | **report** §6.2, §6.3, §6.4, §8 | The interaction, the baseline comparison and calibration added with their figures; the "one in six" claim corrected; a limitation on C's cautious probabilities. XAI figures and the PDF exported again from the second Kaggle run. | Keep the report in line with the notebook. |

**Not changed:** every other output. The second Kaggle run gave the same outputs as the first in every cell that existed before.
