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
