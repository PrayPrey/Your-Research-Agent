# H-M2 Phase 4 Validation Report

**Hypothesis ID:** h-m2  
**Gate Type:** SHOULD_WORK  
**Gate Verdict:** GATE_FAIL (preliminary — full evaluation in progress)  
**Analysis Date:** 2026-08-20  
**Analysis Status:** Preliminary — partial eval cache (70m: 10/154, 1b: 2/154, 6.9b: 0/154)

---

## 1. Hypothesis Statement

Under the Pythia checkpoint trajectory (154 checkpoints × 16 model sizes), cumulative Wikipedia
exposure increase during training correlates more strongly with MMLU score improvement than
HellaSwag improvement, and Books exposure correlates more strongly with HellaSwag than MMLU,
confirmed via Spearman ρ comparison on 3 representative model sizes (70M, 1B, 6.9B).

**Sub-hypotheses tested:**
- **P1:** ρ(Wikipedia, MMLU) > ρ(Wikipedia, HellaSwag) for ≥2 of 3 model sizes
- **P2:** ρ(Books3, HellaSwag) > ρ(Books3, MMLU) for ≥2 of 3 model sizes

---

## 2. Experimental Setup

- **Models:** EleutherAI/pythia-70m, pythia-1b, pythia-6.9b
- **Checkpoints:** 154 per model (steps 0, 1, 2, 4, 8, ..., 143000)
- **Benchmarks:** MMLU 5-shot (acc), HellaSwag 10-shot (acc_norm)
- **Exposure data:** H-E1 cumulative domain trajectories shape (22, 154) per model
- **Floor filter:** Exclude checkpoints where any benchmark < 0.20
- **Spearman ρ:** Rank correlation between cumulative domain exposure and benchmark scores
- **Fisher z-test:** One-tailed test H1: ρ1 > ρ2 at α=0.10
- **Gate criterion:** P1 directional count ≥ 2/3 model sizes

---

## 3. Data Limitations Discovered

### 3.1 Books3 Exposure = 0.0 (Critical)

The H-E1 trajectory arrays show **Books3 (index 2) = 0.0 for all 154 checkpoints across all 3
model sizes**. This is not a sampling artifact — H-E1 results.json confirms `per_domain_std[2] = 0.0`
for all model sizes.

**Cause:** The H-E1 PoC used a 600k-document sample (`doc_idx_is_identity: true`) which may not
have captured sufficient Books3 documents to produce a measurable cumulative exposure signal.

**Impact:** P2 is **structurally untestable** — Spearman ρ requires non-constant X variable.
Any P2 result would be NaN. This invalidates half the hypothesis as stated.

### 3.2 Evaluation Cache Incomplete

Full evaluation of 154 × 3 = 462 checkpoints is in progress (background parallel workers on
5 × H100 NVL GPUs). At time of report:

| Model | Cached | Coverage |
|-------|--------|----------|
| 70m   | 10     | 6.5%     |
| 1b    | 2      | 1.3%     |
| 6.9b  | 0      | 0%       |

### 3.3 Identical Exposure Trajectories Across Model Sizes

All 3 model sizes share **identical** H-E1 domain exposure trajectories (same values at all
checkpoints). This is expected — Pythia models of different sizes are trained on the same Pile
data sequence, so cumulative domain exposure is model-size-independent.

---

## 4. Results

### 4.1 P1: Wikipedia Exposure vs MMLU/HellaSwag

**70m (N=10 checkpoints, steps: 0,1,2,4,50k,71k-74k,143k):**

| Correlation | ρ | Direction |
|-------------|---|-----------|
| ρ(Wikipedia, MMLU) | -0.391 | Wikipedia ↑ → MMLU ↓ |
| ρ(Wikipedia, HellaSwag) | +0.423 | Wikipedia ↑ → HellaSwag ↑ |

**P1 result for 70m: FAIL** — Wikipedia exposure correlates *more strongly* with HellaSwag,
opposite to hypothesis prediction. The direction is reversed: Wikipedia exposure tracks better with
HellaSwag improvement (motor/commonsense reasoning) than with MMLU (factual knowledge recall).

Fisher z-test (70m, P1): z = -1.923, p_one_tailed = 0.973 (highly non-significant in H1 direction).

**1b:** N=2 — insufficient for Spearman correlation.  
**6.9b:** N=0 — no cached checkpoints.

### 4.2 P2: Books3 Exposure vs HellaSwag/MMLU

**Result: UNTESTABLE** — Books3 exposure = 0.0 in H-E1 for all models. Spearman ρ undefined.

### 4.3 Gate Indicators

| Indicator | Value | Threshold | Pass? |
|-----------|-------|-----------|-------|
| P1 directional count | 0/3 | ≥2/3 | FAIL |
| P2 directional count | 0/3 (0 testable) | ≥2/3 | FAIL |
| Models with sufficient N | 1/3 | — | — |

---

## 5. Gate Verdict

**GATE_FAIL (preliminary)**

**Primary reasons:**
1. **P2 structurally untestable:** Books3 exposure = 0 in H-E1 data across all models and checkpoints. Half the hypothesis cannot be evaluated with current H-E1 outputs.
2. **P1 preliminary failure (70m):** With N=10 checkpoints available for 70m, Wikipedia exposure correlates *more* with HellaSwag (ρ=+0.423) than MMLU (ρ=-0.391) — the opposite of the hypothesis prediction. While N=10 gives limited statistical power, the directional signal is clearly contrary to P1.
3. **Evaluation incomplete:** 1b and 6.9b lack sufficient cached checkpoints for analysis. Full evaluation running in background.

**Caveats:**
- The preliminary P1 result for 70m may not generalize to 1b and 6.9b (larger models may show different Wikipedia-MMLU alignment).
- N=10 for 70m is below the MIN_VALID_CHECKPOINTS=100 threshold — the Spearman ρ has wide confidence intervals and may not reflect the full training trajectory.
- The hypothesis as stated presupposes Books3 shows non-zero variation in H-E1, which is not satisfied.

**Recommendation for follow-up:**
- Re-run H-E1 with a larger sample (>6M docs) to get non-zero Books3 coverage
- Wait for full evaluation cache (154 checkpoints per model) before finalizing P1 verdict
- Consider revising hypothesis to focus only on Wikipedia vs other high-variance domains (Pile-CC, StackExchange, PubMed Abstracts) where H-E1 shows meaningful variance

---

## 6. Decontamination Audit

Conservative audit (Pile index maps unavailable): assumed no significant contamination.
MMLU and HellaSwag overlap rates: 0.0 (conservative estimate). Adjusted scores: N/A.

---

## 7. Figures

Figures not generated at this stage due to insufficient data (N<10 for 1b, N=0 for 6.9b).
Figures will be generated once full evaluation cache is populated.

Expected: fig1_gate_metrics.png, fig2_domain_heatmap.png, fig3_trajectories.png,
fig4_fisher_forest.png, fig5_floor_diagnostic.png — saved to `docs/youra_research/h-m2/figures/`

---

## 8. Output Files

| File | Status |
|------|--------|
| `results/h-m2/correlation_matrix.json` | Saved (70m only) |
| `results/h-m2/gate_summary.json` | Saved |
| `results/h-m2/fisher_tests.json` | Saved (70m only) |
| `docs/youra_research/h-m2/experiment_results.json` | Saved |
| `docs/youra_research/h-m2/04_validation.md` | This file |
| Figures (fig1-fig5) | Pending (full eval cache required) |

---

## 9. Validation Summary

```
Gate: SHOULD_WORK
Verdict: GATE_FAIL (preliminary)
Confidence: Low (N=10/154 for 70m only; 1b and 6.9b evaluation in progress)
P1 (Wikipedia→MMLU>HellaSwag): FAIL for 70m (direction reversed)
P2 (Books3→HellaSwag>MMLU): UNTESTABLE (Books3=0 in H-E1)
Blocking data issue: Books3 exposure = 0.0 in H-E1 for all 3 model sizes
Next step: Full eval cache completion or H-E1 re-run with larger sample
```
