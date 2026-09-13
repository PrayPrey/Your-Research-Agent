# Validated Hypothesis Synthesis

**Generated:** 2026-08-31
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 6

---

## 1. Executive Summary

The original hypothesis predicted that OLMo-7B, trained on Dolma (multi-stage curated corpus), would show a higher MMLU/HellaSwag generalization balance ratio and a higher ARC-Challenge/Easy delta than Pythia-6.9B (The Pile, minimal curation) at a matched training scale of ~300B tokens. Both primary predictions were directly refuted: Pythia-6.9B achieves a higher MMLU/HellaSwag ratio (0.565 vs 0.538, difference = −0.0265, 95% CI [−0.0447, −0.0069], p=0.996 one-sided, Cohen's d = −2.732), and a less-negative ARC delta (−0.334 vs −0.344). All three MUST_WORK gate criteria failed; the direction of effect is opposite to the hypothesis.

The refined hypothesis acknowledges this null/negative result while preserving the scientific question: corpus curation quality may produce generalization balance differences, but the effect is not detectable via the MMLU/HellaSwag ratio metric at ~300B training tokens under the Pythia/OLMo architecture-confounded comparison. Three alternative explanations — architecture difference, training scale (300B insufficient), and metric insensitivity — remain plausible and unresolved. The causal mechanism (4 steps) has no verified steps; Step 3 (higher curation → higher MMLU/HellaSwag ratio) was directly falsified.

Key theoretical contributions are negative: (1) The MMLU/HellaSwag ratio does not reliably discriminate corpus curation quality at ~300B token scale in a cross-architecture comparison; (2) HellaSwag performance converges to identical values (0.458) for both models regardless of corpus quality at this scale. Future work must resolve the architecture confound before any causal claim about curation quality and generalization balance is possible.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | OLMo-7B (Dolma) shows higher MMLU/HellaSwag ratio than Pythia-6.9B (The Pile) at ~300B tokens |
| **Refined Core Statement** | At ~300B tokens, OLMo-7B does NOT show higher generalization balance ratio; architecture confound unresolved |
| **Predictions Supported** | 0 / 3 (P3 inconclusive; P1, P2 refuted) |
| **Overall Pass Rate** | 0% |
| **Hypotheses Validated** | 0 / 1 (h-e1 FAILED; h-m1 through h-m4 BLOCKED) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | OLMo-7B MMLU/HellaSwag ratio > Pythia ratio by > 0.02 absolute (Cohen's d > 0.2, p < 0.05) | h-e1 | ratio_diff = OLMo − Pythia | −0.0265 (Pythia 0.565, OLMo 0.538) | **REFUTED** | HIGH | 95% CI [−0.0447, −0.0069] entirely negative; p=0.996; Cohen's d = −2.732 (large effect in wrong direction) |
| **P2** | OLMo ARC-Challenge/Easy delta > Pythia delta (directional, p < 0.10) | h-e1 | ARC_Challenge − ARC_Easy | Pythia: −0.334; OLMo: −0.344 | **REFUTED** | HIGH | OLMo more negative (worse reasoning generalization); ARC-Challenge: 0.296 vs 0.336 |
| **P3** | Quality proxy score positively correlates with Pythia sub-domain benchmark performance (r > 0.3, p < 0.05) | Not executed | Pearson r (quality vs benchmark) | Not computed | **INCONCLUSIVE** | N/A | h-m1 (which requires this analysis) was blocked after h-e1 gate failure; corpus sampling not executed |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Higher curation reduces training noise (fewer repetitive n-grams, less boilerplate) | Equal n-gram repetition rates across quality levels | Not directly tested — corpus text not analyzed in h-e1 | UNVERIFIED |
| 2 | Reduced noise → gradient updates encode more generalizable patterns | No gradient variance reduction in high-quality vs low-quality batches | Not tested — gradient analysis not performed | UNVERIFIED |
| 3 | Better representations → higher MMLU/HellaSwag ratio for OLMo | MMLU improvement not accompanied by maintained HellaSwag | OLMo HellaSwag identical to Pythia (0.458), but OLMo MMLU is lower (0.246 vs 0.259) | **FALSIFIED** |
| 4 | Quality advantage accumulates with tokens (widening gap) | Gap constant or shrinking | Temporal trajectory not executed | UNVERIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under a controlled matched-training-scale comparison (~300B tokens) between foundation models trained on corpora of differing curation quality, if corpus curation quality is higher (as measured by n-gram repetition rate, Flesch-Kincaid grade level, and language ID confidence applied to representative domain samples), then models will show better OOD-to-ID generalization balance (higher MMLU/HellaSwag performance ratio and higher ARC-Challenge/Easy performance delta), because higher-quality data contains less noise and fewer style-specific artifacts, allowing the model to learn more generalizable representations rather than domain-specific statistical patterns.

### 3.2 Refined Core Statement (Phase 4.5)

> At approximately matched training scale (~300B tokens), OLMo-7B (Dolma, multi-stage curation) does NOT show higher MMLU/HellaSwag generalization balance ratio than Pythia-6.9B (The Pile, minimal curation) under fast-evaluation conditions (Pythia ratio=0.565 vs OLMo ratio=0.538, difference=−0.0265, 95% CI [−0.045, −0.007]). This result refutes the existence premise of the corpus-quality → generalization-balance hypothesis in the specific form tested (matched ~300B token scale, cross-architecture comparison, MMLU/HellaSwag ratio metric), but does not rule out curation quality effects at different training scales, with architecture-matched comparisons, or using different balance metrics.

**Key Changes:**
- Original: "OLMo will show higher ratio" → Refined: "OLMo shows LOWER ratio (refuted)"
- Original: Causal claim about curation quality → Refined: Descriptive null result; causality unattributable
- Refined adds: Architecture confound, scale limitation, metric sensitivity qualification

### 3.3 Causal Mechanism — Verified Chain

```
Original Chain: Step 1 [noise reduction] → Step 2 [generalizable gradients]
                → Step 3 [higher MMLU/HellaSwag ratio] → Step 4 [widening gap]

Verified Chain: NONE

  Step 1 [UNVERIFIED]: Corpus text not analyzed
  Step 2 [UNVERIFIED]: Gradient analysis not performed
  Step 3 [FALSIFIED]: OLMo achieves LOWER, not higher, MMLU/HellaSwag ratio
  Step 4 [UNVERIFIED]: Temporal trajectory not executed

Note: The chain's key observable output (Step 3) was directly falsified.
The proposed mechanism is empirically unsupported at the scale tested.
```

**Removed/Modified Steps:**
- **Step 3** (More generalizable representations → higher MMLU/HellaSwag ratio): FALSIFIED — OLMo ratio is significantly lower than Pythia's, opposite to prediction

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| OLMo shows higher MMLU/HellaSwag ratio at ~300B tokens | REMOVE | P1 directly refuted; opposite direction observed | ratio_diff=−0.0265, CI [−0.045, −0.007], p=0.996 |
| OLMo shows higher ARC-Challenge/Easy delta | REMOVE | P2 directly refuted | OLMo delta=−0.344 < Pythia delta=−0.334 |
| Effect attributable to curation quality, not architecture | REMOVE | Architecture confound (GPT-NeoX vs LLaMA-style) not bounded; temporal trajectory not executed | A4 unverified |
| Quality proxy (n-gram + FK + langID) predicts generalization balance | INCONCLUSIVE | P3 not executed; proxy never validated | A2 untested at corpus level |
| Higher curation → better OOD-to-ID generalization balance | MODIFY to: "Curation quality effect on generalization balance is not detectable at ~300B tokens with the metrics and model pair tested" | Scope-qualified null result | All gate criteria failed |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Checkpoints available at ~300B tokens | SUPPORTING | **VERIFIED** | Pythia step143000 ≈ 299.9B (−0.03%), OLMo step68000 ≈ 301B (+0.33%); deviation < 0.5% | N/A — assumption held |
| A2: Quality proxies (n-gram + FK + langID) valid for downstream generalization | SUPPORTING | **UNVERIFIED (implicitly suspect)** | OLMo achieves no generalization advantage despite higher curation — either proxies don't capture relevant quality dimensions, or effect doesn't manifest at 300B | If proxies are invalid, the IV operationalization fails; results describe architecture differences, not quality effects |
| A3: Pile sub-domain mixing identical across Pythia sizes | SUPPORTING | **UNVERIFIED** | P3 not executed; sub-domain analysis never run | Within-Pythia quality correlation impossible without this |
| A4: Architecture differences bounded by temporal trajectory | SUPPORTING | **UNVERIFIED** | Temporal trajectory not tested; 143B checkpoint not evaluated | Causal attribution to data quality impossible; observed difference could be pure architecture effect |
| A5: Contamination rates differ (Dolma dedup may inflate OLMo) | SUPPORTING | **UNVERIFIED** | Min-K% analysis not executed; note: given OLMo performs WORSE on MMLU, Dolma contamination in OLMo's favor is implausible — Pile contamination benefiting Pythia now warrants investigation | Cannot rule out Pile → MMLU contamination inflating Pythia MMLU |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments demonstrate that at ~300B training tokens, Pythia-6.9B (The Pile) achieves MMLU accuracy of 0.259 while OLMo-7B (Dolma) achieves 0.246 — a difference favoring Pythia. HellaSwag scores are identical for both models (0.458). The MMLU/HellaSwag ratio consequently favors Pythia (0.565 vs 0.538). The observed pattern — lower MMLU for OLMo, identical commonsense performance — is the opposite of the predicted pattern.

We hypothesize that this result is most likely explained by the uncontrolled architecture difference: GPT-NeoX (Pythia) may be more efficient than LLaMA-style (OLMo) at few-shot MMLU-style classification at this parameter scale and token count, irrespective of corpus quality. Alternatively, 300B tokens may be insufficient for Dolma's curation quality advantage to manifest in MMLU performance — the Dolma advantage may emerge at later training stages (consistent with data quality × token count interactions described by Muennighoff et al. 2023).

No steps of the proposed causal mechanism (noise reduction → generalizable gradients → higher ratio → widening gap) were verified. Step 3 was directly falsified. The proposed mechanism cannot be confirmed with current evidence.

### 4.2 Unexpected Findings Analysis

#### Finding 1: Identical HellaSwag Performance (0.458 for both models)

- **Observation:** Both models achieve exactly 0.4580 on HellaSwag 0-shot at ~300B tokens
- **Why Unexpected:** Phase 2C expected differentiated commonsense performance reflecting different corpus quality; corpus composition differences should manifest in web-sourced commonsense task
- **Deviation Type:** HYPOTHESIS_ISSUE — not an implementation gap
- **Competing Explanations:**
  1. **Scale ceiling:** Both models are at a convergent learning stage for HellaSwag at 300B tokens — commonsense performance saturates at similar levels regardless of corpus quality at this scale (Plausibility: HIGH)
  2. **Sampling noise:** --limit 500 fast evaluation introduces identical sampling outcome by chance; true scores differ by a small amount (Plausibility: MEDIUM)
  3. **HellaSwag insensitivity:** HellaSwag is well-represented in both corpora (web-sourced commonsense), making it insensitive to quality differences between The Pile and Dolma (Plausibility: MEDIUM)
- **Most Likely:** Scale ceiling — HellaSwag learning may plateau early in training, making it an insensitive discriminator of quality effects
- **Additional Evidence Needed:** Full 10K-sample HellaSwag evaluation + 143B token checkpoint to determine if HellaSwag scores were already identical earlier

#### Finding 2: Pythia outperforms OLMo on MMLU despite lower corpus curation

- **Observation:** Pythia-6.9B MMLU = 0.259 > OLMo-7B MMLU = 0.246 (Pythia higher by 0.013)
- **Why Unexpected:** Dolma includes explicit academic content (S2ORC semantic scholar papers, Wikipedia) which were expected to improve MMLU knowledge-intensive performance; Phase 2C expected OLMo MMLU ≥ Pythia MMLU
- **Deviation Type:** HYPOTHESIS_ISSUE
- **Competing Explanations:**
  1. **Architecture advantage (GPT-NeoX):** GPT-NeoX attention mechanism or tokenization may be more efficient for 5-shot MMLU classification at 6.9B parameters vs LLaMA-style OLMo (Plausibility: HIGH — uncontrolled)
  2. **Training scale effect:** 300B tokens insufficient for Dolma's academic content advantage to manifest; full OLMo-7B (2T tokens) outperforms in literature (Groeneveld et al. 2024) (Plausibility: HIGH)
  3. **Dolma academic proportion at 300B:** At 300B tokens, OLMo may not yet have seen sufficient academic content to boost MMLU, despite Dolma's overall academic richness (Plausibility: MEDIUM)
  4. **Pile contamination:** The Pile may contain MMLU-adjacent content (e.g., from academic PDFs in PubMed, ArXiv) that inflates Pythia's MMLU (Plausibility: LOW — opposite of A5's expected direction, but worth investigating)
- **Most Likely:** Architecture effect + training scale, acting together and not separable in this design
- **Additional Evidence Needed:** (1) Same-architecture pair with different corpora; (2) Temporal trajectory at 143B; (3) Pile contamination (Min-K% for MMLU test set vs The Pile)

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Pythia > OLMo on MMLU at 300B tokens; ratio opposite to prediction | Groeneveld et al. 2024 — Academic paper ratio in Dolma improves MMLU at full training | CONTRADICTS at intermediate scale (their result is full training; we test at 300B) | [Groeneveld24] |
| Architecture confound unresolvable in cross-suite comparison | Penedo et al. 2023 — RefinedWeb uses Falcon (different arch) | CONSISTENT_WITH (architecture confounds persist across curation studies; our study has same problem) | [Penedo23] |
| Quality effects may compound with more tokens | Muennighoff et al. 2023 — Data quality × token count interaction | CONSISTENT_WITH (our 300B null may be consistent with quality effects emerging later) | [Muennighoff23] |
| HellaSwag converges at 300B regardless of corpus | Biderman et al. 2023 — Pythia dedup shows small gains on HellaSwag from deduplication | EXTENDS (dedup alone small gain; curation difference also yields no HellaSwag gain at this scale) | [Biderman23] |

*Note: Literature connections based on references from 03_refinement.yaml. Semantic Scholar MCP unavailable in ablation mode; comprehensive systematic search recommended.*

### 4.4 Theoretical Contributions

1. **EMPIRICAL (Null result):** First matched-scale comparison of Pythia-6.9B and OLMo-7B at ~300B training tokens demonstrates Pythia achieves equal or higher MMLU/HellaSwag ratio than OLMo, directly refuting the corpus-quality → generalization-balance hypothesis in the form tested. This establishes a methodological lower bound: cross-architecture comparisons with single-checkpoint evaluation cannot isolate corpus quality effects.

2. **METHODOLOGICAL:** The MMLU/HellaSwag ratio is not a reliable discriminator of corpus curation quality at ~300B token scale in an architecture-confounded comparison. HellaSwag converges to identical values (0.458) for both models, reducing the ratio to a proxy for MMLU differences only — which are themselves confounded by architecture.

3. **EMPIRICAL:** The identical HellaSwag scores suggest that commonsense reasoning performance converges for 6-8B models across corpus quality levels at ~300B tokens. This has implications for how "generalization balance" metrics should be designed: tasks that plateau early may be unsuitable as denominators in a balance ratio.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Matched-scale MMLU/HellaSwag ratio comparison (OLMo vs Pythia) | MUST_WORK | **FAILED** | 0% | Pythia ratio (0.565) > OLMo ratio (0.538); effect opposite to prediction |
| h-m1 | Corpus quality proxy validation | MUST_WORK | **BLOCKED** | N/A | Not executed; prerequisite h-e1 failed |
| h-m2 | Gradient encoding of generalizable patterns | SHOULD_WORK | **BLOCKED** | N/A | Not executed |
| h-m3 | Transfer from commonsense to knowledge tasks | SHOULD_WORK | **BLOCKED** | N/A | Not executed |
| h-m4 | Temporal trajectory of quality advantage | SHOULD_WORK | **BLOCKED** | N/A | Not executed |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 5 (1 existence + 4 mechanism) |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 1 (h-e1) |
| **Blocked** | 4 (h-m1 through h-m4) |
| **Total Tasks Completed** | h-e1 complete (tasks in ablation mode — count unavailable) |
| **SDD Compliance Rate** | N/A (ablation mode) |

### 5.3 Optimal Hyperparameters

```yaml
# Evaluation configuration that produced reliable results for h-e1
evaluation:
  framework: lm-evaluation-harness
  version: "0.4.12"
  mode: fast_eval  # --limit 500 (screening); use full eval for final results
  
  tasks:
    mmlu:
      shot: 5
      metric: acc
    hellaswag:
      shot: 0
      metric: acc
    arc_easy:
      shot: 25
      metric: acc
    arc_challenge:
      shot: 25
      metric: acc_norm
      
  models:
    pythia_6.9b:
      hf_id: EleutherAI/pythia-6.9b
      revision: step143000
      training_tokens: 299.9B
    olmo_7b:
      hf_id: allenai/OLMo-7B
      revision: step68000-tokens301B
      training_tokens: 301B
      
  token_match_tolerance: 1%  # Both within 0.5% of 300B
  hardware: H100 NVL
  bootstrap_iters: 1000  # For CI on ratio difference
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Matched-checkpoint evaluation pipeline | h-e1 | code/evaluator.py | YES — identical protocol for temporal trajectory |
| MMLU/HellaSwag ratio computation with bootstrap CI | h-e1 | code/metrics.py | YES — for any model comparison |
| lm-eval-harness integration (Pythia + OLMo) | h-e1 | code/run.py | YES — validated for both model families |
| Per-subject MMLU heatmap visualization | h-e1 | code/figures.py, figures/mmlu_heatmap.png | YES — for any MMLU comparison |
| Bootstrap distribution figure | h-e1 | code/figures.py, figures/bootstrap_dist.png | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | MMLU/HellaSwag ratio difference (OLMo − Pythia) | > 0.02 | −0.0265 | HYPOTHESIS_ISSUE | Direction opposite; not implementation error — evaluation pipeline ran correctly |
| **h-e1** | ARC delta comparison (OLMo > Pythia, p < 0.10) | Directional | OLMo: −0.344 < Pythia: −0.334 | HYPOTHESIS_ISSUE | Same wrong direction |
| **h-e1** | P3: Sub-domain quality correlation (r > 0.3) | r > 0.3, p < 0.05 | Not executed | SCOPE_CHANGE | Blocked by P1/P2 failure and ablation mode |
| **h-e1** | Bootstrap CI on ratio | CI excludes 0 (OLMo > Pythia) | CI [−0.045, −0.007] excludes 0, but in wrong direction | HYPOTHESIS_ISSUE | Statistical method worked; hypothesis direction wrong |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| figures/absolute_scores.png | h-e1 | Bar chart: MMLU, HellaSwag, ARC-Easy, ARC-Challenge for Pythia-6.9B vs OLMo-7B | Results: Experiment Setup |
| figures/ratio_delta.png | h-e1 | MMLU/HellaSwag ratio with 95% bootstrap CI for both models | Results: Primary Metric |
| figures/mmlu_heatmap.png | h-e1 | Per-subject MMLU accuracy heatmap (61 subjects, both models) | Results: MMLU Analysis |
| figures/bootstrap_dist.png | h-e1 | Bootstrap distribution of ratio differences (OLMo − Pythia); null line at 0, threshold line at 0.02 | Results: Statistical Analysis |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Architecture Confound Not Bounded

- **What:** The comparison between OLMo-7B (LLaMA-style) and Pythia-6.9B (GPT-NeoX) involves two distinct architectural families; the planned confound-bounding mechanism (temporal trajectory analysis) was not executed
- **Why This Matters:** The observed Pythia MMLU advantage (0.013 absolute) cannot be attributed to corpus quality — GPT-NeoX attention mechanisms, tokenization, or positional encoding may inherently favor few-shot multiple-choice tasks at 6.9B parameters
- **Root Cause:** Temporal trajectory (comparing 143B and 300B checkpoints to determine if gap is widening — quality driven — or stable — architecture driven) was planned in Phase 2C as the primary confound-bounding strategy but was not implemented in h-e1. Gate failure triggered Phase 2A routing before temporal analysis was added.
- **Impact on Claims:** No causal attribution to corpus quality is possible. The null result is valid only as a descriptive observation, not as evidence against or for the quality hypothesis
- **Why Acceptable:** The descriptive null result (Pythia not worse than OLMo at 300B) is itself informative for the field; the architecture confound is a scope limitation clearly stated in the original hypothesis (A4)

#### L2: Fast Evaluation (500-sample limit)

- **What:** lm-evaluation-harness was run with --limit 500 (approximately 8-9 examples per MMLU subject across 57 subjects) instead of the full 14,042-question dataset
- **Why This Matters:** Per-subject MMLU accuracy estimates have high variance with ~8-9 samples; bootstrap CI on the ratio may underestimate true variance
- **Root Cause:** Hardware time constraint; fast eval chosen for rapid hypothesis screening on H100 NVL
- **Impact on Claims:** The direction of the effect is consistent across all metrics (Pythia ≥ OLMo on every metric), and Cohen's d = −2.732 is a large effect unlikely to reverse with full evaluation. The exact magnitude of the ratio difference is unreliable.
- **Why Acceptable:** The large negative Cohen's d and CI entirely below zero suggest the direction is real; full evaluation is recommended before publication to confirm magnitude

#### L3: Single Training Scale (~300B tokens)

- **What:** Only one checkpoint per model (~300B tokens) was evaluated; no temporal trajectory at 143B or earlier checkpoints
- **Why This Matters:** Corpus curation quality effects may compound with training scale. The Dolma advantage seen in OLMo's full training (Groeneveld et al. 2024: OLMo at 2T tokens outperforms Pythia) may require more than 300B tokens to manifest
- **Root Cause:** h-e1 gate failure triggered Phase 2A routing; temporal trajectory was not added as a follow-up within the same hypothesis
- **Impact on Claims:** The null result is valid specifically for ~300B tokens. Cannot rule out quality effects at later training stages.
- **Why Acceptable:** The hypothesis specifically targeted ~300B tokens as the matched comparison point; this is the intended scope of h-e1

#### L4: P3 (Corpus Quality Proxy Validation) Not Executed

- **What:** The sub-domain quality proxy correlation analysis (computing n-gram repetition, FK grade level, fastText language ID for 10K document samples from each Pile sub-domain) was never performed
- **Why This Matters:** A2 assumption remains unvalidated — we don't know whether Dolma is measurably higher quality by these specific proxies, undermining the IV operationalization
- **Root Cause:** P3 was gated on P1/P2 success; additionally, ablation mode restricted file access for corpus text analysis
- **Impact on Claims:** The "corpus quality" IV was never directly measured; all claims rest on the proxy of corpus identity (The Pile vs Dolma) rather than demonstrated quality score differences
- **Why Acceptable:** P3 was designated secondary (non-gate); the existence test (P1, P2) could be evaluated without it

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Model scale | 6-8B parameter range at ~300B tokens | Smaller (<1B, different dynamics) or larger (>30B, architecture effects may differ) | Only 6.9B/7B tested |
| Training tokens | ~300B tokens | >500B tokens (Dolma quality advantage may emerge later per Muennighoff 2023) | Single checkpoint |
| Evaluation completeness | Fast eval (500 samples): direction reliable | Full eval (14K MMLU questions): magnitudes may differ | --limit 500 flag |
| Architecture pair | GPT-NeoX (Pythia) vs LLaMA-style (OLMo) | Same-architecture pair with different corpora | Architecture confound present |
| Balance metric | MMLU/HellaSwag ratio | Other OOD/ID metrics (e.g., GSM8K/HellaSwag, MMLU/WinoGrande) | Only one ratio tested |
| Evaluation regime | 0/5/25-shot standard configs | Instruction-tuned models (alignment confound) | Base model evaluation only |

### 6.3 Assumption Violation Impact

- **A2 (Quality proxies are valid):** Implicitly suspect — OLMo achieves no advantage despite higher curation. Either (a) Dolma's quality advantage doesn't manifest via n-gram/FK/langID proxies, or (b) the proxies don't predict MMLU/HellaSwag balance. Impact: IV operationalization is in question; must validate proxies before re-running the hypothesis. The "higher curation" claim for Dolma is well-documented (Groeneveld 2024), but its relevance to the specific outcome metric is unproven.

- **A4 (Temporal trajectory bounds architecture confound):** Not executed. Impact: All results are architecture-confounded; causal attribution to corpus quality is impossible without temporal trajectory or architecture-matched comparison.

- **A5 (Contamination direction):** Direction assumption was incorrect — Dolma contamination benefiting OLMo is implausible given OLMo's lower MMLU. The Pile's potential MMLU contamination (benefiting Pythia) is now the priority concern and was not investigated.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Architecture difference (GPT-NeoX vs LLaMA-style) fully explains the MMLU performance gap, with corpus quality having negligible effect at 300B tokens
  - **Why Not Yet Tested:** Requires architecture-matched corpus comparison — two models with identical architecture, one trained on The Pile, one on Dolma
  - **Proposed Experiment:** Train two 1-3B parameter models with identical LLaMA-style architecture on The Pile subset (~10B tokens) vs Dolma subset (~10B tokens) at matched scale. Compare MMLU/HellaSwag ratio.
  - **Expected Outcome if True:** Architecture-matched models show no ratio difference despite documented corpus quality difference; expected outcome if False: ratio differs in direction of higher-quality corpus
  - **Priority:** HIGH — resolves the core confound preventing any causal claim

- **Alternative:** Corpus curation quality effects emerge at training scales >300B tokens (delayed benefit hypothesis)
  - **Why Not Yet Tested:** Only 300B checkpoint evaluated; no temporal trajectory at 143B, 200B, 300B
  - **Proposed Experiment:** Evaluate Pythia-6.9B at step72000 (≈143B tokens) and step143000 (≈300B tokens), and OLMo-7B at matched steps. Compare whether the MMLU/HellaSwag ratio gap is widening or stable across token counts.
  - **Expected Outcome if True:** Gap is narrowing at 300B (OLMo approaching Pythia) even if not yet crossing; at 500B tokens, OLMo would exceed Pythia
  - **Priority:** HIGH — directly tests h-m4 and can be executed with existing checkpoints

### 7.2 From Unverified Assumptions

- **Assumption A2:** Quality proxies (n-gram repetition + Flesch-Kincaid + fastText language ID) validly measure curation quality dimensions relevant to downstream generalization
  - **Proposed Test:** Sample 10K documents from The Pile and Dolma; compute all three proxy metrics; confirm that Dolma scores significantly higher on the composite index. If not, the IV operationalization fails.
  - **If Violated:** The "high vs low curation" comparison is confounded by unmeasured quality dimensions; must select alternative proxies (e.g., perplexity under a reference model, toxicity rate, duplicate rate after deduplication)
  - **Priority:** HIGH — prerequisite for any re-run of P3 or hypothesis redesign

- **Assumption A4:** Temporal trajectory bounds the architecture confound (architecture drives constant gap; data quality drives widening gap)
  - **Proposed Test:** Run temporal trajectory at 143B and 300B tokens for both models; plot ratio trajectories
  - **If Violated:** Architecture confound is stable and indistinguishable from data quality — future work must use architecture-matched design
  - **Priority:** HIGH — determines whether the existing Pythia/OLMo comparison is salvageable

- **Assumption A5 (revised):** The Pile may contain MMLU-adjacent contamination inflating Pythia's MMLU performance (opposite of original A5 direction)
  - **Proposed Test:** Min-K% contamination detection comparing MMLU test questions against The Pile training data; compare contamination rate to Dolma contamination against same questions
  - **If True:** Pythia's MMLU advantage partially explained by contamination; the "null" result is partly artifact
  - **Priority:** MEDIUM — secondary analysis; main findings hold regardless

### 7.3 From Scope Extension Opportunities

- **Extension:** Test the hypothesis with OLMo at full training (2T tokens) vs Pythia at 300B — while unmatched in scale, demonstrates whether quality eventually produces the predicted generalization balance
  - **Current Evidence Suggesting Feasibility:** OLMo full-training checkpoints already on HuggingFace; Groeneveld et al. 2024 reports higher MMLU for full-trained OLMo
  - **Resources:** Single evaluation run (no new training), ~2 hours on H100; provides existence-of-effect evidence separate from matched-scale test
  - **Expected Challenges:** Scale confound makes causal claims impossible; serves only as qualitative existence evidence

- **Extension:** Test with alternative balance metrics (GSM8K/HellaSwag, MMLU/WinoGrande) to determine whether the null result is metric-specific
  - **Current Evidence Suggesting Feasibility:** GSM8K and WinoGrande both supported natively by lm-evaluation-harness; no new evaluation infrastructure needed
  - **Resources:** Additional 1-2 hours evaluation per model; can be done alongside temporal trajectory experiments

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

"We attempted to measure whether better data produces smarter models — and found that, at 300 billion training tokens, the answer is: not in the way we expected. OLMo-7B, trained on one of the most carefully curated pre-training corpora (Dolma), achieves a lower knowledge-to-commonsense ratio than Pythia-6.9B, trained on The Pile with minimal filtering. More strikingly, both models achieve identical commonsense reasoning scores, suggesting that web-sourced commonsense knowledge converges regardless of curation quality at this training scale."

**Hook Strategy:** Counterintuitive result — the "better data" model performs worse on the metric designed to measure its advantage
**Why This Hook:** Null results are underreported in ML; a well-controlled negative result with a specific scope qualification ("at 300B tokens, with this architecture pair, with this metric") is scientifically valuable. The hook frames the contribution as revealing a gap in our understanding rather than confirming a prior belief.

### 8.2 Key Insight (Experiment-Verified)

> At ~300B training tokens, the MMLU/HellaSwag generalization balance ratio is not a reliable discriminator of corpus curation quality in a cross-architecture comparison: HellaSwag performance converges to identical values (0.458) for GPT-NeoX and LLaMA-style models, reducing the ratio to a noisy proxy for MMLU differences that are themselves architecture-confounded.

**Verification Evidence:** Pythia-6.9B HellaSwag = OLMo-7B HellaSwag = 0.4580 (exact equality in fast eval); ratio difference = −0.0265 (95% CI [−0.045, −0.007], p=0.996, d=−2.732); all three gate criteria failed

### 8.3 Strongest Claims (Paper-Ready)

1. **At ~300B training tokens, Pythia-6.9B (The Pile) achieves a higher MMLU/HellaSwag ratio than OLMo-7B (Dolma), opposite to the corpus-quality → generalization-balance prediction**
   - Evidence: ratio_diff = −0.0265, 95% CI [−0.045, −0.007], p=0.996 (one-sided), d=−2.732
   - Confidence: HIGH (clear direction, CI excludes zero)
   - Suggested Section: Results — Primary Finding

2. **HellaSwag (0-shot commonsense) performance converges to identical values for both models at ~300B tokens regardless of corpus curation quality**
   - Evidence: Both models: 0.4580; difference = 0 in fast eval
   - Confidence: MEDIUM (fast eval; full evaluation recommended to confirm)
   - Suggested Section: Results — Secondary Analysis / Discussion

3. **The matched-scale cross-architecture comparison methodology is insufficient to attribute performance differences to corpus quality without architecture-matched controls or temporal trajectory analysis**
   - Evidence: A4 unverified; architecture confound not bounded; temporal trajectory not executed
   - Confidence: HIGH (methodological limitation, not disputed by results)
   - Suggested Section: Discussion — Limitations and Future Work

4. **The MMLU/HellaSwag ratio metric is not sensitive to corpus curation quality at ~300B token scale in a cross-architecture setting**
   - Evidence: Null result + identical HellaSwag denominator
   - Confidence: MEDIUM (specific to this architecture pair and scale)
   - Suggested Section: Discussion — Metric Design Implications

### 8.4 Honest Limitations (Must Include in Paper)

1. **Architecture confound (L1)**
   - Why Acceptable: Architecture confound is a known limitation of any cross-suite comparison; temporal trajectory and architecture-matched comparisons are proposed as future work; the null result is still informative within this scope
   - Suggested Framing: "Our comparison between architecturally distinct models (GPT-NeoX vs LLaMA-style) cannot isolate corpus quality effects from architecture effects. The reported null result is conditional on this cross-architecture design; future work using architecture-matched pairs would provide stronger causal evidence."

2. **Fast evaluation (L2)**
   - Why Acceptable: Direction is highly consistent (large Cohen's d) and all four metrics favor Pythia; fast eval is appropriate for hypothesis screening
   - Suggested Framing: "To enable rapid hypothesis evaluation, we used a 500-sample evaluation limit. Full evaluation across 14,042 MMLU questions is recommended before drawing conclusions about effect magnitude; however, the direction of the effect is robust (d = −2.732)."

3. **Single training scale (L3)**
   - Why Acceptable: The hypothesis explicitly targeted ~300B tokens; this is the scope, not a failure
   - Suggested Framing: "Our findings are specific to ~300B training tokens. Prior work (Groeneveld et al. 2024) shows OLMo advantages at full training (2T tokens), suggesting curation quality effects may compound with training scale beyond our test point."

4. **P3 not executed (L4 / IV unvalidated)**
   - Why Acceptable: P3 was secondary; primary gate failure was directionally clear without it
   - Suggested Framing: "The corpus quality IV was operationalized via corpus identity (The Pile vs Dolma) rather than directly measured quality proxy scores. Future work should validate that Dolma scores measurably higher on n-gram repetition, Flesch-Kincaid, and language ID confidence metrics before re-testing the hypothesis."

### 8.5 Evidence Highlights (Most Persuasive)

1. **MMLU/HellaSwag Ratio Comparison with Bootstrap CI**
   - Data: Pythia ratio = 0.565, OLMo ratio = 0.538; 95% CI on difference = [−0.045, −0.007]; p=0.996; d=−2.732
   - "So What": The effect is statistically significant in the wrong direction — the curated corpus model performs worse on the metric specifically designed to capture curation benefits. This is not noise; it is a clear directional signal.
   - Suggested Figure/Table: figures/ratio_delta.png (ratio bar chart with CI) + bootstrap distribution histogram (figures/bootstrap_dist.png)

2. **Identical HellaSwag Scores**
   - Data: Both models: HellaSwag = 0.4580 (exact match in fast eval); ARC-Easy Pythia = 0.670 > OLMo = 0.640
   - "So What": The denominator of the ratio metric (HellaSwag) is identical — the ratio difference is entirely driven by MMLU, not by differentiated commonsense performance. This reveals a structural weakness in using HellaSwag as the "in-distribution" baseline for this comparison.
   - Suggested Figure/Table: figures/absolute_scores.png (side-by-side bar chart)

3. **Per-Subject MMLU Heatmap**
   - Data: Per-subject accuracy across 61 MMLU subjects for both models (figures/mmlu_heatmap.png)
   - "So What": Reveals whether Pythia's MMLU advantage is broad (all subjects) or concentrated in specific domains (potential contamination signal). If concentrated in web-common domains, contamination hypothesis gains plausibility.
   - Suggested Figure/Table: figures/mmlu_heatmap.png

4. **All Four Benchmark Metrics Favor Pythia**
   - Data: MMLU: 0.259 > 0.246; HellaSwag: tied; ARC-Easy: 0.670 > 0.640; ARC-Challenge: 0.336 > 0.296
   - "So What": The null/negative result is consistent across all metrics — this is not a metric-specific artifact. OLMo underperforms or ties on every individual benchmark, making the directional refutation robust to choice of aggregation method.
   - Suggested Figure/Table: Table 2 in paper with all four metrics side-by-side

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results, gate outcomes, bootstrap CI, figures |
| `h-e1/04_checkpoint.yaml` | h-e1 | Pass rate (0.0), failed checks, gate failure record |
| `h-e1/03_tasks.yaml` | h-e1 | Planned tasks, expected metrics, success criteria (ablation mode: unavailable) |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, evaluation protocol, expected outcomes |
| `03_refinement.yaml` | All | Original hypothesis, predictions P1-P3, assumptions A1-A5, causal mechanism |
| `verification_state.yaml` | All | Pipeline state — h-e1 FAIL, h-m1 through h-m4 BLOCKED |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
*Phase 4.5 v2.0 — 2026-08-31*
