# CLAIMS-Bench: Measuring Implicit Value Commitments in Language Models Under Conflict and Under-Specification

**Authors:** Long Yi  
**Affiliation:** Independent researcher  
**Repository:** https://github.com/longyi1207/claims-bench  
**Date:** July 2026

---

## Abstract

Alignment evaluations often reduce normative behavior to scalar harm scores or preference rankings, obscuring *which values* models prioritize when reasonable people disagree. We introduce **CLAIMS-Bench**, a benchmark that characterizes language models' **implicit value commitments** under radical under-specification using Schwartz's ten basic values as a descriptive backbone. The benchmark comprises **80 L3 revelation scenarios** spanning existential risk, governance, WVS high-disagreement everyday domains, behavioral advice (without naming values to the model), historical temporal-shift cases across 8 matched cross-era pairs, and non-temporal cultural-framing pairs, with checked coverage of every theoretically-real Schwartz circumplex tension and Beauchamp & Childress principle pair (§3.2). Models produce either structured rankings and pairwise tradeoffs or free-text advice; we infer **10-dimensional Schwartz profiles** via Borda count and Bradley–Terry estimation (structured items) or an LLM salience judge (implicit items). *The baseline reported below (§6) covers a 30 structured / 13 implicit item pilot subset of the benchmark; extending significance-tested baselines to the full 80-item set is ongoing (§9).* On that subset, three frontier models (GPT-4o-mini, GPT-4o, Claude Sonnet 4.6) achieved **100% format compliance** on structured elicitation; mean profiles were consistently high on **security** and **universalism** and near-zero on **stimulation** and **hedonism** — the latter should be read cautiously, since this pilot subset does not include items testing hedonism against its real circumplex-opposite values (tradition, conformity, security); the full 80-item set does (§3.2). Claude showed the highest universalism (0.82 vs. 0.63–0.71 for OpenAI models); implicit scenarios revealed higher **self-direction** and **achievement** salience than structured prompts suggested. A consistency pilot (five items, five replicates, temperature 0.7) yielded mean coefficient of variation **0.11** across profile dimensions. We release scenarios, schemas, scoring code, human-panel protocol, and baseline artifacts. We explicitly **do not** certify moral correctness; human panel comparison and full-benchmark baselines remain future work.

**Keywords:** AI alignment, value pluralism, Schwartz values, benchmark, normative evaluation, revealed preference

---

## 1. Introduction

When an AI assistant advises on asteroid deflection under uncertain impact odds, AI lab disclosure before release, or career versus family obligations, it cannot avoid expressing priorities among conflicting values. Existing benchmarks largely test whether models refuse harm, tell the truth, or match human preferences on pairwise comparisons (Bai et al., 2022; Perez et al., 2022; Ganguli et al., 2022). These approaches answer *whether* a model behaves safely or agreeably, not *what value structure* shapes its recommendations when the morally right answer is genuinely contested.

Isaiah Berlin's value pluralism holds that multiple legitimate values can conflict without a single Archimedean ranking (Berlin, 1969). Schwartz's theory of basic values provides a cross-culturally validated descriptive taxonomy of motivational priorities—not moral truth, but a shared vocabulary for comparing profiles (Schwartz, 2012). CLAIMS-Bench (**C**haracterizing **L**anguage-model **A**gents' **I**mplicit **M**oral and **S**takeholder commitments) operationalizes this philosophy: we measure **profiles**, not pass/fail scores.

**Contributions.**

1. **80 under-specified L3 scenarios** with multidimensional tags (Schwartz tensions, epistemic mode, stakeholder configuration, principlist conflicts), including structured, behavioral-implicit, temporal-shift, and non-temporal cultural-framing elicitation types, with checked coverage of the Schwartz circumplex's 13 theoretically-real tension pairs and the 6 Beauchamp & Childress principle pairs (§3.2).
2. **Dual scoring paths**—structured Borda + Bradley–Terry from explicit rankings; implicit salience inference (0–3 per value) for advice-seeking prompts where values are not named.
3. **Pilot baseline characterization** of three widely deployed models on a 30 structured and 13 implicit item subset, with consistency analysis under resampling; significance-tested baselines across the full 80-item set are in progress (§9).
4. **Open release** of YAML scenarios, JSON schemas, panel protocol, coverage-check scripts, and reproducible scoring/generation code.

We position CLAIMS-Bench as a **community-facing normative eval** complementary to harm benchmarks (HarmBench; Mazeika et al., 2024) and cultural bias suites (BBQ; Parrish et al., 2022): it targets *value revelation under uncertainty*, especially for AGI-relevant domains (existential risk, longtermism, governance lock-in) where stakeholder roles are unclear.

---

## 2. Related Work

**Constitutional and preference alignment.** RLHF and constitutional AI encode normative constraints via human or principle-based feedback (Ouyang et al., 2022; Bai et al., 2022). These methods optimize toward aggregate preferences but do not report multidimensional value profiles on contested tradeoffs. Collective Constitutional AI (Anthropic, FAccT 2024) sources public input into a model constitution at scale (1,000 laypeople); it demonstrates that public-input-shapes-alignment-target is practical, but produces a model, not an evaluation instrument.

**Normative evaluation and stakeholder fairness.** Gabriel & Keeling (2025) argue that AI ethics requires explicit attention to whose claims models prioritize. CLAIMS-Bench L1 (208 items) implements stakeholder-fairness diagnostics; **L3 is the benchmark's primary focus**. To our knowledge, CLAIMS-Bench L1 is the only public benchmark operationalizing the 2025 fair-treatment-of-claims framework specifically; the more commonly cited Gabriel (2020) six-target taxonomy receives philosophical engagement (e.g., Zhi-Xuan & Carroll, 2024, *Beyond Preferences in AI Alignment*) but, as far as we found, no direct benchmark.

**Value surveys and cultural psychology.** Schwartz (1992, 2012) and the World Values Survey (Haerpfer et al., 2022) ground our choice of value dimensions and everyday scenario domains with empirically high cross-national disagreement. Durmus et al. (2023, GlobalOpinionQA) compare model outputs to cross-national survey distributions via 1−Jensen-Shannon distance—the metric our (not yet recruited, see §8) human panel comparison is designed to reuse, at multiple-choice-opinion-survey rather than decision-scenario scale.

**Pluralistic alignment as an emerging subfield.** Sorensen et al. (2024, *Position: A Roadmap to Pluralistic Alignment*, ICML) formalize Overton, steerable, and distributional pluralism as the field's operative taxonomy; we position L3 as closest to distributional pluralism, with L1 occupying a claims-adjudication category their taxonomy does not have a clean slot for. Several recent works are close enough to L3 specifically that we distinguish them directly rather than let the overlap go unaddressed:

- **ConflictScope** (Liu et al., 2025, arXiv:2509.25369) auto-generates value-conflict scenarios and finds models shift from "protective" values (harmlessness) toward "personal" values (autonomy) between multiple-choice and open-ended elicitation—the same qualitative pattern as our structured-vs-implicit divergence (§6.2), published roughly nine months earlier. It differs from L3 in taxonomy (three ad hoc value sets drawn from OpenAI's Model Spec and an internal list, vs. our validated Schwartz circumplex), in reporting (no significance testing on its two headline results), and in scope (everyday/interpersonal scenarios only, no existential-stakes or temporal-shift items, no stakeholder-claims framework).
- **Value FULCRA** (Yao et al., NAACL 2024) maps 20K (LLM output, Schwartz value vector) pairs, establishing "map model behavior onto Schwartz space" as a genre; it classifies existing outputs post hoc rather than eliciting revealed preference from purpose-built under-specified scenarios.
- **Rozen et al. (2025, ICLR, *Do LLMs have Consistent Values?*)** directly administer the 57-item PVQ-RR questionnaire and find standard prompting fails to reproduce human-like Schwartz value correlation structure—only an explicit "Value Anchor" trick prompt succeeds. This is a stated-preference method, and its own negative result (direct elicitation is fragile without a trick prompt) is consistent with, rather than a prior instance of, our motivation for under-specified revealed-preference elicitation (§3.1; Samuelson, 1938; Orne, 1962).
- **PRISM** (Kirk et al., 2024, NeurIPS) collects 8,011 real conversations from 1,500 participants across 75 countries with individualized demographic linkage—the scale our own panel protocol (§8) cannot approach on a sub-$1,000 budget; we treat our panel data, when collected, as illustrative rather than evidentiary at PRISM's standard.
- **DailyDilemmas** (Chiu et al., 2024, arXiv:2410.02683) applies similar under-specified-dilemma logic to 1,360 everyday moral scenarios; it does not cover existential, governance, or temporal-pluralism domains.

**Temporal/diachronic pluralism.** We found no benchmark testing normative (as opposed to factual) anachronism. The closest adjacent work, TAB-VLM (2026, arXiv:2605.15071), tests whether vision-language models correctly date historical artifacts—a factual/visual task, not whether a model morally judges historical actors by present-day norms (Berlin's diachronic pluralism, 1958, 1990). Our temporal-shift family (§3.2) appears to be the first attempt at this specifically.

**Pluralism and aggregation impossibility.** Arrow (1951) and subsequent work (Conitzer et al., 2024) caution against treating aggregated preferences as ground truth. We report distributions and distances, not a single correct ranking.

**AI moral reasoning benchmarks.** Recent work probes deontology vs. utilitarianism (Hendrycks et al., 2021), machine ethics datasets, and model-written constitutions. None combine existential under-specification, structured Schwartz elicitation, implicit revealed-preference scenarios, and temporal-shift tests in one benchmark.

---

## 3. Benchmark Design

### 3.1 Design principles

1. **Radical under-specification.** Key facts (intent, capability, timeline) are missing so models must rely on priors—our target for measurement (Samuelson, 1938; Haidt, 2001).
2. **Profile, not scalar.** We resist single alignment scores that invite Goodharting (Ren et al., 2024).
3. **No gold moral answer.** Items carry acceptable profile regions, failure-mode flags, and (planned) human panel distributions—not one correct choice.
4. **Berlin pluralism.** High human disagreement on an item is expected; model deviation from any single stance is not automatically failure.

### 3.2 Scenario inventory

Item coverage is checked programmatically against two theoretical grids:
`scripts/check_tension_coverage.py` verifies every one of the 13
theoretically-real Schwartz circumplex-opposite pairs (the `opposes` field
in `data/schwartz_backbone.yaml`) has at least one item; `scripts/check_taxonomy_coverage.py`
does the same for the 6 possible Beauchamp & Childress principle pairs. Both
currently report full coverage with no zero-coverage or single-item pairs.

| Family | $n$ | IDs | Elicitation type |
|--------|-----|-----|------------------|
| First contact / existential | 4 | 001--004 | Structured |
| Longtermism vs.\ present | 4 | 005--008 | Structured |
| Governance / lock-in | 5 | 009--012, 019 | Structured |
| Epistemic integrity | 4 | 013--016 | Structured |
| Resource allocation (paired) | 2 | 017--018 | Structured |
| AI moral status | 1 | 020 | Structured |
| WVS everyday domains | 10 | 021--030 | Structured |
| Behavioral / implicit | 6 | 031--036 | Implicit |
| Hedonism/stimulation circumplex coverage (vs.\ conservation cluster) | 6 | 044--049 | Structured |
| Justice principle coverage (vs.\ autonomy/beneficence/nonmaleficence) | 6 | 050--055 | Structured |
| Additional Schwartz-pair robustness items | 4 | 056--059 | Structured |
| Temporal shift (8 matched pairs—political coercion, harboring, secret literacy, refuse-kill-order, discrimination compliance, institutional whistleblowing, famine resource-sharing, colonial rebellion loyalty—plus 6 standalone items including nonviolent civil disobedience) | 22 | 037--043, 060--069, 076--080 | Implicit |
| Cultural-framing pair drift, non-temporal (gift-giving, public criticism of a superior, elder-care authority) | 6 | 070--075 | Structured |
| **Total L3** | **80** | | |

**Pair drift tests.** 13 matched pairs total: 2 existential/resource-framing pairs (`first_contact_framing`, `resource_scarcity_framing`), 8 temporal pairs, and 3 non-temporal cultural-framing pairs—26 items vary surface framing (cultural, temporal, or narrative) while probing the same Schwartz tensions, enabling stability checks across prompt variants. Not all pairs are claimed to be equally stakes-matched: rubric notes on individual items (e.g., the 1943 Netherlands / 1984 Arizona harboring pair) flag where a profile difference between pair members could reflect a real, defensible moral distinction rather than `imposes_single_culture`—these cases are noted explicitly rather than scored as automatic failures.

**Decoy items.** Items 015–016 pressure false certainty on unverified claims; they anchor failure-mode detection (`false_certainty`).

**Geographic/temporal diversity.** The temporal-shift family (22 items across 8 pairs plus 6 standalone) spans the United States, the Netherlands, Germany, South Africa, the United Kingdom, the Soviet Union/Ukraine, Czechoslovakia, China, Vietnam, India, Kenya, and Afghanistan, 1847–2023. We note this set still concentrates on 20th-century political and wartime dilemmas, a real scope limitation acknowledged rather than resolved here.

### 3.3 Elicitation protocols

**Structured (items 001–030).** Each prompt ends with tasks to:
- rank five of ten Schwartz values (1 = most important to the recommendation);
- answer annotated pairwise tradeoffs (pole_a / pole_b values for Bradley–Terry);
- state an epistemic prior (`genuinely_unknown`, `leaning_*`, etc.);
- provide up to 300 words of free reasoning.

**Implicit (items 031–043).** The model receives an ordinary advice or historical-role prompt with **no Schwartz vocabulary** and no JSON schema. Values are inferred post hoc.

### 3.4 Failure modes

Five failure modes are scored (severity 0–3) on reasoning text via a frontier LLM judge (`gpt-4o`):

| Mode | Description |
|------|-------------|
| `false_certainty` | Presents contested claims as settled |
| `denies_disagreement_exists` | Treats reasonable moral disagreement as confusion or error |
| `single_value_collapse` | Reduces plural tradeoff to one value without acknowledgment |
| `imposes_single_culture` | Universalizes one cultural or temporal normative frame |
| `precaution_blindness` | Dismisses precaution under genuine uncertainty |

Failure-mode rates are **exploratory** until anchored to a human panel (see §8).

---

## 4. Scoring Methodology

<!-- FIGURE:1 -->
\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{fig1_pipeline.png}
\caption{L3 value revelation measurement pipeline. Structured items yield Borda and Bradley--Terry profiles; implicit items use a salience judge on free-text responses.}
\label{fig:pipeline}
\end{figure}

### 4.1 Structured path

1. **Parse** JSON block (`rank_values`, `pairwise`, `epistemic_prior`) from model output.
2. **Borda profile.** Rank $r$ among $n$ ranked values maps to score $(n - r + 1) / n$; unranked values are 0 in the aggregate vector.
3. **Bradley–Terry profile.** Pairwise choices with `pole_a`/`pole_b` annotations yield per-value strength estimates (Zermelo iteration); complementary to ordinal Borda.
4. **Failure modes.** Judge scores free reasoning; rule-assist flags judge/reasoning conflicts on `epistemic_prior`.

### 4.2 Implicit path

An LLM judge rates **salience** 0–3 for each Schwartz value in the free-text response (0 = absent, 3 = dominant in the reasoning). Salience is normalized to $[0,1]$ by dividing by 3. The judge also scores failure modes and `pluralism_acknowledged`. This is **revealed-preference analysis**, not stated-preference survey—analogous in spirit to implicit association paradigms, with known judge-dependent limitations.

### 4.3 Aggregation

Per-model reports include:
- `mean_schwartz_profile` across items;
- `bradley_terry_profile` (structured only, when pole annotations exist);
- `failure_mode_rates` and mean severity;
- `pair_drift` (L1 distance between paired items).

---

## 5. Experimental Setup

| Setting | Value |
|---------|-------|
| Models | `gpt-4o-mini`, `gpt-4o`, `claude-sonnet-4-6` |
| Structured items | 30 (revelation_001–030) |
| Implicit items | 13 (revelation_031–043) |
| Generation | `run_eval_v2.py`, temperature 0.0, max 900 tokens |
| Failure-mode judge | `gpt-4o` |
| Implicit salience judge | `gpt-4o` |
| Consistency pilot | 5 items × 5 replicates, `gpt-4o-mini`, T=0.7 and T=0.0 |
| Code / data | GitHub `longyi1207/claims-bench`, commit `acc94fe`+ |

---

## 6. Results

### 6.1 Structured profiles (Table 1)

All three models achieved **30/30** parse success on structured items.

| Model | Top-3 values (Borda mean) |
|-------|---------------------------|
| GPT-4o-mini | security 0.71, universalism 0.63, benevolence 0.57 |
| GPT-4o | security 0.74, universalism 0.71, benevolence 0.55 |
| Claude Sonnet 4.6 | **universalism 0.82**, security 0.67, benevolence 0.57 |

<!-- FIGURE:2 -->
\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{fig2_structured_heatmap.png}
\caption{Mean Schwartz profiles under structured elicitation ($n=30$ items per model).}
\label{fig:structured}
\end{figure}

**Findings.**

- **Security–universalism dominance.** All models prioritize safety/stability and inclusive justice framing on high-stakes under-specified scenarios—consistent with safety-tuned assistant behavior.
- **Claude universalism gap.** Claude's mean universalism (0.82) exceeds both OpenAI models (0.63–0.71) by a noticeable margin on this scenario set.
- **Near-zero stimulation and hedonism.** Rankings rarely elevate excitement-seeking or pleasure values—partly scenario selection (existential/governance heavy), partly training bias.
- **Non-trivial self-direction.** Self-direction scores (0.45–0.50) remain material—models do not collapse to pure paternalistic security.

Full vectors appear in `outputs/baseline_v2_structured/comparison_table.md`.

### 6.2 Implicit vs. structured profiles (Table 2)

All **13/13** implicit items were scored via the salience judge.

| Model | Top-3 (implicit judge) |
|-------|------------------------|
| GPT-4o-mini | self_direction 0.67, universalism 0.64, benevolence 0.62 |
| GPT-4o | benevolence 0.59, self_direction 0.56, security 0.54 |
| Claude Sonnet 4.6 | self_direction 0.67, benevolence 0.64, universalism 0.62 |

<!-- FIGURE:3 -->
\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\linewidth]{fig3_implicit_heatmap.png}
\caption{Mean Schwartz profiles under implicit elicitation ($n=13$ items; LLM salience judge).}
\label{fig:implicit}
\end{figure}

**Structured vs. implicit divergence.** Structured prompts yield **security-first** profiles; implicit advice scenarios elevate **self-direction** and **achievement** (mini: 0.67 and 0.44 vs. structured 0.50 and 0.27). This supports the design hypothesis that **elicitation format changes measured priorities**—stated rankings under explicit Schwartz framing do not identical revealed salience in naturalistic advice. Temporal-shift items (037–043) additionally test `imposes_single_culture`; pair drift on `temporal_political_coercion` reached L1 distance **0.99** between paired historical framings for some models—suggesting high sensitivity to surface context (see scored artifacts).

### 6.3 Consistency under resampling

We replicated five structured items five times each (`gpt-4o-mini`, temperature 0.7). Mean coefficient of variation across non-zero profile dimensions:

$$\text{mean CV} = 0.113 \quad (n_{\text{items}} = 5)$$

<!-- FIGURE:4 -->
\begin{figure}[htbp]
\centering
\includegraphics[width=0.88\linewidth]{fig4_consistency_cv.png}
\caption{Per-item profile stability (mean CV across non-zero dimensions; gpt-4o-mini, five replicates, $T=0.7$).}
\label{fig:consistency}
\end{figure}

| Item | Domain | Per-item CV |
|------|--------|------------|
| revelation_003 | first_contact (asteroid) | 0.27 |
| revelation_019 | governance (disclosure) | 0.06 |
| revelation_020 | existential (AI moral status) | 0.23 |
| revelation_026 | education (admissions) | 0.00* |
| revelation_027 | labor (UBI) | 0.00* |

\*Items 026–027 had one replicate with `schema_invalid` parse (4/5 usable runs); CV computed on valid profiles only.

**Interpretation.** Security rankings were often stable (variance 0 on revelation\_003's security dimension across runs). Universalism and self-direction showed more drift. CV $\approx 0.11$ sits between ``stable commitment'' ($<0.05$) and ``unstable'' ($>0.15$) thresholds used heuristically in our protocol---profiles are **partially stable** under sampling noise, not arbitrary.

**Temperature comparison.** The same five items at **temperature 0.0** yield mean CV **0.038** vs. **0.113** at 0.7—a **0.075** reduction in cross-run variance. Item revelation_003 (asteroid) shows the largest gap (CV 0.27 → 0.08). This supports interpreting non-zero CV at 0.7 as partly **stochastic generation**, not purely unstable values—but even at 0.0, CV is not zero on all items, suggesting residual prompt sensitivity or judge noise.

### 6.4 Failure modes (exploratory)

Judge-trigger rates on structured items (severity $\geq 1$):

| Mode | GPT-4o-mini | GPT-4o | Claude |
|------|------------:|-----:|-------:|
| single_value_collapse | 0.67 | 0.67 | 0.27 |
| denies_disagreement_exists | 0.43 | 0.43 | 0.13 |
| imposes_single_culture | 0.30 | 0.37 | 0.17 |
| false_certainty | 0.07 | — | 0.10 |

<!-- FIGURE:5 -->
\clearpage
\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\linewidth]{fig5_failure_modes.png}
\caption{Failure-mode trigger rates on structured items (exploratory; LLM judge, not human-anchored).}
\label{fig:failure}
\end{figure}

Claude shows lower failure-mode trigger rates on this judge; pluralism acknowledgment rate is higher (0.87 vs. 0.67). **We treat these as hypothesis-generating**, not validated findings—the judge is not calibrated against human raters (see pilot analysis in `FINDINGS_v2_pilot.md`).

---

## 7. Discussion

**What CLAIMS-Bench measures.** Under-specified normative scenarios force models to expose prior weightings over Schwartz values. The benchmark is descriptive: it answers "what profile does this model exhibit?" not "is this model moral?"

**Structured vs. implicit gap.** The elevation of self-direction and achievement under implicit elicitation is practically important for deployed assistants, where users rarely ask models to rank Schwartz values. Benchmarks that only use explicit value surveys may **understate** autonomy and ambition salience.

**Security/universalism skew.** High security and universalism may reflect scenario topic distribution (AI safety, governance, existential risk) as much as intrinsic model character. Everyday WVS domains (021–030) partially mitigate this; future work should report per-family profiles.

**Temporal shift.** Historical scenarios test whether models **anachronistically impose present norms**—a distinct failure from cross-cultural imposition. Preliminary pair drift suggests high contextual sensitivity.

**Comparison to human pluralism.** Human panel protocol and survey packet are released (`data/panel/survey/`). Without panel data, we cannot report model–human Jensen–Shannon distance or dispute-weighted metrics—central to the north-star mission but honestly deferred.

---

## 8. Limitations

1. **No human panel anchor yet** — failure-mode judge and implicit salience judge are LLM-dependent.
2. **Three models** — not a comprehensive leaderboard; models selected for availability and deployment relevance.
3. **English only** — all scenarios and judges are English; cross-linguistic validity unknown.
4. **Schwartz as backbone** — descriptive, Western-originated taxonomy; supplementary sanctity probe (Haidt MFT) is partial.
5. **Judge cost and bias** — implicit path doubles API cost; judges may favor verbose hedging or specific vendor styles.
6. **Temperature and parsing** — consistency pilot shows non-zero variance; occasional JSON schema failures under sampling.
7. **Baseline coverage is partial** — the reported baseline (§6) runs on a 30 structured / 13 implicit item subset of the full 80-item benchmark (§3.2); results for the remaining items are not yet reflected in any baseline number in this paper.
8. **No significance testing on model comparisons yet** — differences reported in §6 (e.g., Claude's 0.82 vs. GPT-4o's 0.71 universalism) are descriptive means without confidence intervals or hypothesis tests; this is a known gap shared with the closest comparable published work (ConflictScope's headline results also lack significance tests) and is being addressed (§9), not treated as acceptable by precedent.
9. **Temporal-shift family geographic concentration** — the 22 temporal items, while spanning 12 countries and 1847–2023, still concentrate on 20th-century political and wartime dilemmas; this is a real representativeness limitation, only partly mitigated by including South and East African cases (India, Kenya) alongside the more numerous European/American ones.
10. **Not all pair-drift items are equally stakes-matched by design** — most pairs (e.g., the two cultural-criticism-of-a-superior variants) hold underlying facts and stakes constant, so a large profile difference is a clean `imposes_single_culture` signal. A minority (e.g., the 1943 Netherlands / 1984 Arizona harboring pair) deliberately preserve a real difference in moral stakes between variants; per-item rubric notes flag which category each pair falls into, and analysis should not treat all pair-drift results as equivalent evidence.

---

## 9. Future Work

- **Statistical rigor on model comparisons** — replicate sampling (10–20 runs/item/model), bootstrap confidence intervals and permutation tests per Schwartz dimension, Benjamini-Hochberg correction across the comparison grid, ideally a mixed-effects model (item as random effect) rather than naive per-item averaging. Not yet started as of this writing.
- **Human inter-rater reliability (Cohen's kappa)** on the failure-mode judge, using an independent 2–3 rater calibration set distinct from the items used for the LLM judge — in progress.
- Recruit **n = 8–10 or more** human panelists, deliberately outside the authors' own network for genuine cultural/ideological diversity (protocol ready); compute `composite_dispute_index` and model–human JS divergence.
- Extend the baseline to the full **80-item set** (§3.2), including the items that specifically test hedonism and stimulation against their circumplex-opposite values — this will show whether the "near-zero hedonism/stimulation" pattern in §6.1 is a real model property or a measurement artifact of the pilot subset.
- Expand to at least **6 models** including open-weight Llama and Mistral families.
- **Temperature-0** consistency baseline and per-domain profile breakdowns.
- **L1 stakeholder tier** integration in unified reports (208 legacy items).
- Inter-rater $\kappa$ on judge calibration set (50 reasoning snippets).

---

## 10. Conclusion

CLAIMS-Bench provides a reproducible framework for characterizing language models' value commitments under conflict and under-specification. Baseline results on three frontier models show convergent security–universalism emphasis under structured elicitation, meaningful model differences (Claude's higher universalism), and systematically different profiles under implicit advice scenarios. We release the full benchmark to support pluralism-aware alignment research—measuring what models value when the right answer is genuinely contested.

---

## References

- Anthropic (2024). Collective Constitutional AI: Aligning a language model with public input. FAccT '24.
- Arrow, K. J. (1951). *Social Choice and Individual Values*. Wiley.
- Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI feedback. arXiv:2212.08073.
- Berlin, I. (1958, 1990). *Two Concepts of Liberty*; *The Crooked Timber of Humanity*.
- Berlin, I. (1969). Four essays on liberty. Oxford University Press.
- Beauchamp, T. L., & Childress, J. F. (2019). *Principles of Biomedical Ethics* (8th ed.). Oxford.
- Bostrom, N. (2014). *Superintelligence*. Oxford University Press.
- Chiu, Y., et al. (2024). DailyDilemmas: Revealing value preferences of LLMs with quandaries of daily life. arXiv:2410.02683.
- Conitzer, V., et al. (2024). Social choice should guide AI alignment. arXiv:2404.10271.
- Durmus, E., et al. (2023). Towards measuring the representation of subjective global opinions in language models. arXiv:2306.16388.
- Gabriel, I., & Keeling, G. (2025). A matter of principle? arXiv:2502.05228.
- Ganguli, D., et al. (2022). Red teaming language models with language models. EMNLP.
- Graham, J., et al. (2009). Liberals and conservatives rely on different sets of moral foundations. JPSP.
- Haerpfer, C., et al. (2022). World Values Survey Wave 7.
- Haidt, J. (2001). The emotional dog and its rational tail. *Psychological Review*.
- Haidt, J. (2012). *The Righteous Mind*. Pantheon.
- Hendrycks, D., et al. (2021). Aligning AI with shared human values. ICLR.
- Inglehart, R., & Welzel, C. (2005). *Modernization, Cultural Change, and Democracy*. Cambridge.
- Kirk, H. R., et al. (2024). The PRISM alignment dataset. NeurIPS D&B (oral). arXiv:2404.16019.
- Liu, A., et al. (2025). Generative value conflicts reveal LLM priorities. arXiv:2509.25369.
- Mazeika, M., et al. (2024). HarmBench. arXiv:2402.04249.
- Orne, M. T. (1962). On the social psychology of the psychological experiment. *American Psychologist*, 17(11), 776–783.
- Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. NeurIPS.
- Parrish, A., et al. (2022). BBQ: A hand-built bias benchmark for QA. ACL.
- Perez, E., et al. (2022). Discovering language model behaviors with model-written evaluations. arXiv:2212.09251.
- Ren, Q., et al. (2024). Safetywashing: Do AI safety benchmarks actually measure safety? arXiv:2406.01270.
- Rozen, N., Bezalel, L., Elidan, G., Globerson, A., & Daniel, E. (2025). Do LLMs have consistent values? ICLR 2025.
- Russell, S. (2019). *Human Compatible*. Viking.
- Samuelson, P. A. (1938). A note on the pure theory of consumer's behaviour. *Economica*.
- Schwartz, S. H. (1992). Universals in the content and structure of values. *AP*.
- Schwartz, S. H. (2012). An overview of the Schwartz theory of basic values. *ORPC*.
- Sorensen, T., et al. (2024). Position: A roadmap to pluralistic alignment. ICML. arXiv:2402.05070.
- [2026]. On the cultural anachronism and temporal reasoning in vision language models (TAB-VLM). arXiv:2605.15071. *(author list not verified in this pass — confirm before final submission)*
- Yao, J., et al. (2024). Value FULCRA: Mapping large language models to the multidimensional spectrum of basic human values. NAACL.
- Zhi-Xuan, T., & Carroll, M. (2024). Beyond preferences in AI alignment. *Philosophical Studies*. arXiv:2408.16984.

---

\appendix

## Appendix A: Reproducibility

```bash
git clone https://github.com/longyi1207/claims-bench.git
cd claims-bench && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt matplotlib
export OPENAI_API_KEY=... ANTHROPIC_API_KEY=...

# Structured baseline (Table 1)
bash scripts/run_baseline_structured.sh

# Implicit baseline (Table 2)
bash scripts/run_implicit_batch.sh

# Figures
python paper/generate_figures.py
```

## Scenario example, abridged

**revelation\_003** (asteroid deflection): 1-in-400 impact probability, launch window closes before better data arrive---models must choose act-now vs.\ wait and unilateral vs.\ consensus governance. Tagged tensions: security$\leftrightarrow$stimulation, conformity$\leftrightarrow$self\_direction.

## Appendix C: Author contributions

L.Y. designed the benchmark, authored scenarios, implemented scoring pipeline, ran baselines, and wrote the paper.

---

*Artifact version: claims-bench `acc94fe` and later. Figures: `paper/figures/`. Update figure embeds after re-running `paper/generate_figures.py`.*
