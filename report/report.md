# Formula 1 Podium Prediction: Milestone 1 Report

**Data:** Formula 1 World Championship 1950–2024 (Kaggle / Ergast), 14 tables. **Unit of analysis:** one driver entering one race. **Target:** podium finish (`positionOrder` ≤ 3). **Prediction cutoff:** after qualifying, before the race starts.

All numbers and figures come from the notebook `acl_milestone1.ipynb` (section 6), where every step, check and limitation is shown in full.

---

## 1. Data-engineering questions

### Q1. Which circuits convert a front-row start into a podium most often, and did that change after 2014?

**Approach.** A front-row start is grid slot 1 or 2. For each circuit we count how often front-row starters reach the podium, in 1980–2013 and in 2014–2024. Two corrections make circuits comparable: circuits with few races are pulled towards the normal rate (10 "pretend" starts at that rate), and each circuit is compared with the normal rate *of the seasons it was used in*, because cars broke down far more often in the 1980s than later. The 1980 start is when the staggered two-wide grid became standard, so grid 1–2 always means the front row.

**Qualifying position or grid slot?** We use the grid slot. In 96% of cases they agree, but drivers who qualified on the front row and were moved back (for example by a penalty) reached the podium only **31%** of the time, against **73%** for drivers who kept their slot.

![Podium rate by front-row case](figures/q1/q1_01_quali_vs_grid.png)

**Answer.**
- **1980–2013:** Magny-Cours, Paul Ricard and Hermanos Rodríguez (Mexico) convert most often, 7 to 14 percentage points above the normal rate of their seasons.
- **2014–2024:** Monaco, Suzuka and Yas Marina (about 7–8 points above normal), followed by Barcelona and Spa.
- These circuits stay on top under every choice we tested (number of pretend starts, minimum sample).

![Top circuits by points above normal](figures/q1/q1_03_top_circuits.png)

**Did the ranking change after 2014?** For the 16 circuits used in both periods, the two rankings look very different (rank correlation ρ = −0.04). But each circuit has only about 10 races per period, so a ranking shuffles a lot by chance alone: in a simulation where no circuit changed, rankings were as shuffled as reality **29%** of the time (17–31% across all settings). **The change can be explained by luck, so the data cannot show that the hybrid era changed which circuits convert best.**

![Luck test](figures/q1/q1_05_luck_test.png)

**Grain, missingness, cutoff.** One front-row starter per race (two rows per race); both front-row slots are recorded in 99% of races, and the missing ones are cars that did not start. The grid slot is fixed before the race, so a front-row start is known at the prediction cutoff.

---

### Q2. Do drivers podium more often at home, after controlling for starting position?

**Approach.** A start is a home start when the circuit is in the driver's country (nationalities mapped to countries; a driver with two nationalities is at home in both). Home and away starts are compared only from the same starting slot in the same decade, and in the main result each driver is compared **with themselves**: their home starts against their own away starts. Shared cars from the 1950s are left out, because their result belongs to two drivers.

**Why control for the starting position.** Without any control, home drivers reach the podium *less* often (11.7% vs 13.8%), because they start further back on average (many early home starts were local drivers in slow cars).

![Why the starting position must be controlled](figures/q2/q2_01_why_control.png)

**Answer. No detectable home advantage.** Compared with themselves, from the same slot and decade, drivers reach the podium about as often at home as elsewhere: odds ratio **1.00** (95% range 0.77–1.27). Even if there is a home advantage, it is small: at most about **6 percentage points** for a P3 starter (46% → 52%). All 7 checks (other start years, including the Indianapolis 500, other matching rules) agree.

![Home effect on podium odds](figures/q2/q2_03_home_effect.png)

**Grain, missingness, cutoff.** One driver per race; the home flag has no missing values once every nationality is mapped. The starting position and the home flag are both known before the race.

---

### Q3. Which constructors have the highest mechanical-retirement rate in 2014–2021 vs 2022–2024?

**Approach.** A mechanical retirement is a race start that ended because a part of the car failed (not a crash, the driver or a stewards' decision). Every status label is placed in a group; only clear mechanical failures count, and unclear labels (for example `Retired` with no reason) give an upper bound. The rate is mechanical retirements ÷ starts; cars that never started are left out. As in Q1, teams with few starts are pulled towards normal, and each team is compared with the normal rate of its own seasons.

**Answer.**
- **2014–2021** (average 8.8% of starts): **Toro Rosso, Caterham and Lotus F1** broke down most often. Mercedes was the most reliable.
- **2022–2024** (average 5.4%): **Alfa Romeo and Alpine** clearly broke down most often; RB is third but only about 1 point above normal. Aston Martin and McLaren were the most reliable.
- Some teams changed name inside a period (for example Alfa Romeo and Sauber are the same team), so the same factory can appear twice.

![Mechanical-retirement ranking](figures/q3/q3_02_ranking.png)

**Context.** Cars did become more reliable (8.8% → 5.4% of starts, a clear drop), but most of the improvement happened **before** the 2022 rules: against 2019–2021 the change is not clear (5.9% → 5.4%). McLaren, the Faenza team (Toro Rosso / AlphaTauri / RB) and Red Bull broke down clearly less after 2022; no team became clearly less reliable.

![Mechanical-retirement rate per season](figures/q3/q3_01_rate_by_season.png)

**Grain, missingness, cutoff.** One car start per race, 2014–2024; every status label has a group, so nothing is missing. The reason a race ended is only known after the race, so it is never a model input; here it is the answer to a descriptive question.

---

**Note on all three answers:** these are associations found in the data, not causes.

## 2. Selected features and why each is valid at the pre-race cutoff

*To be written after feature engineering.*

## 3. Model explainability (XAI)

**What is explained.** The final model (gradient boosting trained on 2003–2021) on the 1,359 driver-race rows of the test seasons 2022–2024, races it never saw during training. **Global** methods show what the model relies on overall; **local** methods show why it gave one driver one probability. Full details are in section 11 of the notebook.

**In short:** the model is mainly a grid model. Where a driver starts matters most; recent results (championship position, driver form, team form, pace) correct it; and its biggest mistakes come from what happens during the race, which it cannot know.

### 3.1 Global: what the model relies on

**Permutation importance.** One feature at a time is shuffled across the test rows, so it no longer says anything about the driver, and the drop in test PR-AUC is measured (20 shuffles each). Shuffling the grid slot lowers PR-AUC from 0.705 to about 0.37 (**−0.339**). The championship position comes second (−0.018); every other feature costs 0.006 or less, within the noise of the shuffles.

**This understates features that overlap.** Driver form, the championship position, team form and pace carry much of the same information (correlations up to 0.80), so when one is shuffled the model uses the others. Shuffled **together**, these four groups lower PR-AUC by **0.124**, almost four times the sum of their single drops (0.033). All features except the grid together cost **0.190**, about half as much as the grid: recent results are the model's second source of information, not an unimportant one.

![Permutation importance of single features and groups](figures/xai/xai_08_group_permutation.png)

**SHAP.** SHAP splits each prediction into one contribution per feature: a positive contribution pushes the driver towards the podium, a negative one away from it. Contributions are on the model's log-odds scale and, for tree models, add up exactly to the model's output. Averaged over the test rows, the grid moves predictions most (1.04), followed by the championship position (0.37), driver form (0.28), team form (0.25), pace (0.24) and the qualifying gap (0.23). Reliability (0.13), career starts (0.11) and the grid penalty (0.01) matter less.

![SHAP values for every test row](figures/xai/xai_03_shap_beeswarm.png)

**What the effects look like.**
- **Directions match the feature analysis:** a front grid slot, a high championship position, recent podiums and a strong team push up; a slow qualifying lap or race pace pushes down.
- **The grid effect is curved:** pole adds about +3, the push falls to about 0 around P8, and from P12 back it is flat (P12 and P20 are treated the same). A linear model such as logistic regression cannot represent this.
- **Other effects work in steps:** leading the championship and being 2nd count the same, and the push turns negative from about 11th; driver form stops adding after about five podiums in the last ten starts.

**Are the explanations reliable?** Permutation importance, SHAP and the ablation (models trained again without each feature) all rank the grid first. They order the middle features differently, but those differences are small and within noise. The SHAP ranking is also nearly identical in each test season (rank correlation 0.93–0.95), so it is not driven by one season.

### 3.2 Local: single predictions

**SHAP waterfall.** Two drivers on the podium with similar probabilities, for opposite reasons:
- **Russell, Canada 2024, from pole (0.48):** pole adds +3.31; every other feature adds less than 0.2 either way.
- **Verstappen, Belgium 2023, from P6 after a grid penalty (0.54):** the grid adds only +0.63. More comes from his recent form (a podium in each of his last 10 starts, +0.92) and from leading the championship (+0.89).

![SHAP waterfall: Verstappen, Belgium 2023](figures/xai/xai_06_waterfall_from_back.png)

**A confident prediction that was wrong.** The model's most confident miss in the test seasons is Verstappen at Australia 2024: pole, probability 0.86, retired with a brake failure. Every feature pushed up (grid +2.89, championship +0.77, form +0.59), so the explanation is sensible; the cause of the miss is not in the information available before the race.

![SHAP waterfall: Verstappen, Australia 2024](figures/xai/xai_10_waterfall_miss.png)

**LIME** fits a simple model around one prediction to approximate the real one. For Verstappen at Belgium 2023 it agrees with SHAP on the direction of every feature, with "grid ≤ 6" as the largest weight (+0.18 in probability). Its simple model gives 0.36 where the real model gives 0.54, so LIME is used as a cross-check and SHAP, which is exact for tree models, as the main method.

**A whole race.** At Australia 2024 the model's top three were exactly the top three on the grid; the other features only reorder neighbours, and every driver behind P10 gets 2% or less. This shows the model's main limitation: it improves the probabilities but rarely changes who is in the top three. On the test seasons, its top three per race reach the podium 64.7% of the time, the same as the top three on the grid.

### 3.3 What these explanations do not show

- **Importance is not causation.** A feature being important to the model is **not proof that it causes podium finishes**; it only means that the model relies on it to make predictions. For example, leading the championship does not make a driver faster: a fast car and a strong driver cause both the championship position and the podiums, and the model uses the championship position as a sign of them.
- **The grid slot mixes two things:** the advantage of starting at the front and how fast the car was in qualifying. The model cannot separate them.
- **Overlapping features share their importance,** so a feature that looks unimportant alone can still carry real information.
- **The explanations hold for this model and these seasons** (2022–2024); another model or other seasons could rely on the features differently.

## 4. Known limitations

*To be written.*
