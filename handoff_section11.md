# Handoff for section 11 (XAI) and section 12 (inference)

Sections 7.10 to 10.11 were reworked on 2026-10-19. This note explains what changed and what section 11 and 12 need to adapt to. Everything up to the end of 10.11 has been run and the readings match the outputs.

**Before you start.**
1. Run the notebook from the top to the end of section 10 first (Restart and run). Sections 0–10 were edited in pieces and have not been run top to bottom since, and section 11 needs their variables anyway. It takes a while, and the network tuning in 10.4 is the slowest part.
2. If any cell before section 11 gives an error, send it back to us instead of fixing it, because those sections are ours.

## The big change: several versions of the data instead of one model

We no longer have one "final model". The TAs reward experiments more than a single choice, so we tested several versions and report all of them.

| Version | Training seasons | Split | Features |
|---|---|---|---|
| A | 2003–2018 | by time (validation 2019–2021) | the 9 features |
| B | 1950–2018 | by time | 6 features (no qualifying, no pace) |
| C | 1950–2018 | by time | the 9 features + `has_quali_data` + `has_pace_data` (11) |
| D-A | 2003–2021 | random whole races (60 validation races) | as A |
| D-C | 1950–2021 | random whole races | as C |

The test part is 2022–2024 for every version.

- Every option has its own preprocessing (fill, cap, scale learned from its own training part) and chooses its own settings on its own validation part.
- **Two models are carried forward (10.6): gradient boosting in option A and gradient boosting in option C.** They are tied on validation (0.747 against 0.744, not clear). B is dropped. The network is not carried forward because its score moves with the random seed.
- The ablation (10.7) now has only two experiments (one group removed, one group alone), for A-GB and C-GB. Experiments 3, 4 and 5 were removed.
- 10.8 is now the random split (option D). The old "training on all seasons / version B" section is gone.
- 10.9 scores every model on the test, compares validation and test, does the split experiment, and tests retraining on 2019–2021.
- Metrics (10.10): primary PR-AUC, secondary F1.
- 10.11 is a summary table of every version (PR-AUC and F1, validation and test). No model is chosen there.

## Main results you may want to refer to

- Test PR-AUC: A-GB 0.717, C-GB 0.704, grid 0.645. Both clearly beat the grid. A against C is not clear.
- On the test, logistic regression is as good as gradient boosting (A-LR 0.716). The validation advantage of GB and the network did not carry over.
- Retraining A-GB on 2003–2021 made it slightly worse on the test (0.717 to 0.704, clear). So **the reported models are the ones trained without the validation seasons** (`opt_gb['A']`, `opt_gb['C']`), not the retrained ones.
- The random split picked a bad model for C (depth 5, test 0.652). With C's settings on the same random training races it reaches 0.702.
- A-GB settings are now **depth 2**, rate 0.03, 300 trees (it used to be depth 3). C-GB is depth 2, rate 0.03, 100 trees.

## Names you can use in section 11

| Name | What it is |
|---|---|
| `OPTIONS` | `{option: (first season, feature list)}` for A, B, C |
| `F`, `FLAGS` | the 9 features, and the 2 extra features of C |
| `opt_X[o][part]` | `(X, y)` scaled, for part in train / validation / test |
| `opt_scaled[o]`, `opt_capped[o]` | the full table of option o, scaled or in original units (after filling and capping) |
| `opt_gb[o]`, `opt_gb_params[o]` | the gradient boosting model of option o as reported, and its settings |
| `opt_gb_threshold[o]` | its F1 threshold (chosen on validation) |
| `test_rows`, `y_test_final` | the test rows (same for every option) |
| `test_prob[(version, model)]` | test probabilities, for example `test_prob[('C', 'gradient boosting')]` |
| `OPT_GROUPS[o]`, `GROUPS` | the feature groups (in C, each flag sits in its group) |
| `features_of(*groups, option=o)`, `features_without(*groups, option=o)` | feature lists per group; the default option is A |
| `race_redraws`, `change_range`, `val_redraws`, `test_redraws` | the race redraws for 95% ranges |

Option A also keeps the old names (`gb`, `GB_PARAMS`, `p_gb`, `gb_threshold`, `X_train`, `X_val`, `X_test`, `p_test`, `test_results`), so most old code still runs.

## Things in section 11 and 12 that will break or are now wrong

1. **11.3 uses `leave_one_feature`** (the old ablation experiment 5). It no longer exists. Either drop that comparison or compare with `leave_one` (experiment 1, groups, columns `option`, `group removed`, `change`).
2. **`gb_final` is now the retrained A-GB** (trained on 2003–2021), together with `final_fill`, `final_caps`, `final_scaler`, `X_final` and `X_test_final`. Section 11 and the inference function (12) use these. But the reported model is `opt_gb['A']` (not retrained), and `p_test[gb_name]` comes from `opt_gb['A']`. If a cell mixes `gb_final` with `p_test`, the numbers will not match. We suggest explaining `opt_gb['A']` (and maybe `opt_gb['C']`) with `opt_X[o]['test'][0]` as the test inputs.
3. **Which model(s) to explain is not decided.** A-GB only, or A-GB and C-GB. C has 11 features, so its SHAP plots would include the two flags.
4. **The text in section 11 still says "the final model" and quotes old numbers** (for example depth 3, test PR-AUC 0.705, the old SHAP probabilities). Every number needs rereading after the rerun.
5. **The pace group is still labelled "pace (candidate)"** in `FEATURES` (7.10). It shows up in group tables. Renaming it to "pace" means rerunning from 7.10.

## Still open for the whole notebook

- The preprocessing-order experiments are in 9.6 (default models, all options) and again at the end of 10.6 with the carried-forward models (A-GB and C-GB).
- A full rerun from top to bottom before submitting, then a check that every reading matches the new outputs (the network numbers can shift slightly between computers).
- `changes.md` has no entry for today yet.
- The report, the Kaggle run (check that `lime` and `shap` are installed there), commit and merge into `sasa-dany`.
