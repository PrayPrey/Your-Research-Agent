# Phase 2B: Verification Plan
# H-EntropySWA-v1 — Entropy-Guided Zero-Shot Selective SWA Conversion in Llama-2-7B
# Generated: 2026-08-22 | Archon Project: 69f47604-8ee4-4c6e-9841-b41acba6a749

---

## Main Hypothesis

**ID:** H-EntropySWA-v1  
**Confidence:** 0.72  
**Statement:**  
Under the setting of Llama-2-7B (32 attention layers, no fine-tuning, standard WikiText-103 and GLUE SST-2 evaluation), if the k=4 layers with highest mean per-layer attention entropy (measured on a 100-sequence calibration set using `output_attentions=True`) are replaced with sliding window attention (window size w=512 tokens) zero-shot, then WikiText-103 perplexity will remain within 2 points and GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline, because high-entropy layers already contribute less unique global context than low-entropy layers, and the residual stream of the 28 remaining full-attention layers provides sufficient global context compensation for the converted layers.

**Alternative H0:**  
Entropy provides no predictive value for identifying SWA-safe layers (entropy-guided k=4 ≥ random-k=4 on perplexity), OR any selective SWA conversion (k≥1) causes >5pt perplexity degradation (zero-shot selective SWA is infeasible in Llama-2-7B).

---

## Causal Mechanism (Three-Step)

1. **Entropy Scoring** — Mean per-layer attention entropy on 100 calibration sequences identifies layers with diffuse, low-information-value global attention (supported by HIES [Choi et al., 2025], Michel et al. [2019]).
2. **SWA Replacement** — Replacing high-entropy layers with SWA(w=512) aligns mechanism with measured behavior; these layers were not exploiting sharp global attention (Raganato et al. [2020], Michel et al. [2019]).
3. **Residual Stream Compensation** — 28 retained full-attention layers propagate global context through the residual stream, compensating for SWA layers' reduced reach (Vaswani et al. [2017]; SWARR [Liu et al., 2026] confirms full-model SWA fails while partial retention mitigates collapse).

**Key tension:** Entropy identifies diffuse attention globally but does not distinguish local vs global diffuseness. Residual stream compensation is stronger for later-depth converted layers; depth position of entropy-selected layers is an explicit diagnostic output.

---

## Sub-Hypothesis Inventory

| ID   | Type      | Gate        | Status      | Prerequisites | Statement (short)                                              |
|------|-----------|-------------|-------------|---------------|----------------------------------------------------------------|
| h-e1 | EXISTENCE | MUST_WORK   | READY       | —             | Entropy criterion is stable (Spearman ρ ≥ 0.8 across 3 seeds) |
| h-e2 | EXISTENCE | MUST_WORK   | NOT_STARTED | h-e1          | k=4 entropy-guided SWA: WikiText-103 Δperplexity ≤ 2.0pt (P1) |
| h-m1 | MECHANISM | MUST_WORK   | NOT_STARTED | h-e2          | Entropy-k4 outperforms random-k4 and last-k4 on perplexity (P2) |
| h-m2 | MECHANISM | SHOULD_WORK | NOT_STARTED | h-e2          | k=8 boundary characterization + depth position analysis (P3)   |
| h-c1 | CONDITION | SHOULD_WORK | NOT_STARTED | h-e2          | k=4 SWA maintains GLUE SST-2 accuracy within 2pp of baseline   |

---

## Sub-Hypothesis Details

### h-e1 — Entropy Criterion Existence & Stability
**Gate:** MUST_WORK (failure invalidates entire hypothesis — no stable criterion, no valid experiment)  
**Assumptions tested:** A1 (entropy ranking stability)  
**Success criterion:** Spearman ρ ≥ 0.8 for top-8 layer rankings across 3 non-overlapping 100-sequence calibration subsets of WikiText-103 validation split  
**Falsification:** ρ < 0.7 → entropy ranking is noise; entropy criterion invalid  
**Mitigation if fails:** Increase calibration to 300 sequences; if still unstable, entropy criterion is infeasible for Llama-2-7B  
**Estimated runtime:** ~15 min on 1× H100 (entropy scoring only, CPU-feasible)

### h-e2 — Zero-Shot SWA Conversion Feasibility (Prediction P1)
**Gate:** MUST_WORK (failure → route to Phase 0; zero-shot selective SWA fundamentally infeasible)  
**Assumptions tested:** A2 (high-entropy layers approximable by SWA), A3 (residual stream compensation), A5 (mask implementation correctness)  
**Success criterion:** Δperplexity(entropy-k4 vs baseline) ≤ 2.0 on WikiText-103 test set  
**Falsification:** Δperplexity > 2.0 → entropy criterion selected layers that WERE using global attention meaningfully; OR Δperplexity > 5.0 for any k≥1 → zero-shot SWA infeasible  
**Implementation:** HF AttentionMaskConverter(sliding_window=512) or direct attn_mask injection in modeling_llama.py; validate mask correctness (positions within [i-512, i])  
**Estimated runtime:** ~30 min on 1× H100

### h-m1 — Entropy Criterion Superiority over Baselines (Prediction P2)
**Gate:** MUST_WORK (failure → entropy provides no selection advantage; mechanism claim invalid)  
**Comparison baselines:** random-k=4 (mean of 3 seeds), last-k=4 (deepest 4 layers, indices 28-31)  
**Success criterion:** Δperplexity(entropy-k4) < Δperplexity(random-k4) AND Δperplexity(entropy-k4) < Δperplexity(last-k4)  
**Falsification:** Δperplexity(entropy-k4) ≥ Δperplexity(random-k4) → entropy provides no selection advantage; hypothesis novelty claim invalidated  
**Estimated runtime:** ~45 min on 1× H100 (3 random seeds + last-k eval)

### h-m2 — Conversion Capacity Boundary & Depth Position Diagnosis (Prediction P3)
**Gate:** SHOULD_WORK (failure does not block Phase 5; informative negative result)  
**Success criterion:** Δperplexity(entropy-k8) > Δperplexity(entropy-k4), characterizing degradation curve; depth positions of entropy-selected layers cluster in later layers (supporting residual stream mechanism)  
**Falsification:** Non-monotone degradation (k8 ≤ k4 perplexity) is anomalous; or selected layers cluster in early positions (challenges residual stream compensation)  
**Estimated runtime:** ~20 min on 1× H100

### h-c1 — GLUE SST-2 Accuracy Preservation
**Gate:** SHOULD_WORK (failure does not block Phase 5; treated as independent benchmark)  
**Assumptions tested:** A4 (WikiText-103 + SST-2 jointly characterize accuracy preservation)  
**Success criterion:** ΔSST-2 accuracy (entropy-k4 vs baseline) ≤ 2 percentage points on GLUE SST-2 validation set  
**Falsification:** ΔSST-2 > 5pp → generalization to discriminative tasks fails  
**Note:** SST-2 test labels unavailable; use validation set. Domain sensitivity ablation: compare entropy ranking from WikiText vs SST-2 calibration sequences  
**Estimated runtime:** ~15 min on 1× H100

---

## Dependency Graph (DAG)

```
h-e1 (MUST_WORK, READY)
  └─► h-e2 (MUST_WORK)
         ├─► h-m1 (MUST_WORK)
         ├─► h-m2 (SHOULD_WORK)
         └─► h-c1 (SHOULD_WORK)
```

h-e1 is the critical path entry. h-e2 gates all downstream work. h-m1 is the second MUST_WORK gate. h-m2 and h-c1 run in parallel after h-e2 passes; their results enrich but do not gate Phase 5.

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| h-e1 FAIL: entropy ranking unstable | Low | Critical — blocks all | Increase calibration to 300 seq; if fails, abandon entropy criterion |
| h-e2 FAIL: k=4 conversion exceeds 2pt threshold | Medium | Critical — Phase 0 route | Both-positive and negative results publishable; characterizes zero-shot SWA boundary |
| h-m1 FAIL: entropy ≤ random-k performance | Medium | High — invalidates novelty claim | Publication as negative result (characterizes limits of entropy-based selection) |
| h-m2: non-monotone degradation | Low | Low — SHOULD_WORK, informative | Analyze depth positions for mechanistic explanation |
| h-c1: SST-2 diverges from WikiText | Medium | Low — independent benchmark | Treated separately; partial result acceptable |
| Implementation bug in SWA mask | Low | Medium — confounds all results | Explicit mask validation (check attended positions ∈ [i-512, i]) before evaluation |

---

## Timeline / Effort Estimate

| Step | Sub-hypothesis | Est. GPU time | Parallelizable? |
|------|----------------|---------------|-----------------|
| 1 | h-e1 (entropy scoring + stability) | 15 min | No — must run first |
| 2 | h-e2 (baseline + entropy-k4 eval) | 30 min | No — prereq: h-e1 |
| 3 | h-m1 (random-k4 ×3 + last-k4 eval) | 45 min | Partial (seeds parallel) |
| 4a | h-m2 (entropy-k8 eval + depth analysis) | 20 min | Yes — parallel with h-c1 |
| 4b | h-c1 (SST-2 eval) | 15 min | Yes — parallel with h-m2 |
| **Total** | | **~2.1 GPU-hours** | |

Within 1 GPU-hour pilot constraint for h-e1+h-e2 (primary feasibility check). Full suite ≤2.5 hours on 1× H100.

---

## Dialectical Analysis (Thesis–Antithesis–Synthesis)

**Thesis:** High-entropy layers in Llama-2-7B have diffuse attention patterns equivalent to or approximable by local-window attention; replacing them with SWA(w=512) zero-shot preserves model quality because these layers were not exploiting global attention meaningfully.

**Antithesis:** Attention entropy measures flatness of the distribution but does not distinguish between "diffuse local" and "diffuse global" attention. A layer with high entropy could be attending broadly to all positions in a globally meaningful way — constraining it to a local window would then eliminate globally-useful patterns that entropy alone cannot detect. Furthermore, early-depth converted layers cannot receive residual stream global context compensation (the residual stream has not accumulated sufficient global information at those positions).

**Synthesis:** The entropy criterion is not a direct proxy for "local vs global" behavior but rather for "redundancy with the residual stream global context bus." High-entropy layers contribute less unique information precisely because the residual stream from preceding full-attention layers already carries the global context they would have provided. This synthesis is validated operationally by: (1) the Spearman ρ stability test (h-e1), (2) the perplexity preservation test (h-e2), and (3) the depth position diagnostic in h-m2 — if entropy-selected layers cluster in later positions where the residual stream is richest, the synthesis mechanism is confirmed. This reframing (from "diffuse = local" to "diffuse = redundant with residual stream") is the key conceptual contribution of Phase 2A Exchange 5.

---

## Controlled Variables Summary

| Variable | Value | Rationale |
|----------|-------|-----------|
| Model | Llama-2-7B (meta-llama/Llama-2-7b-hf) | 32-layer causal decoder; SWAA [2025] uses same model class |
| Fine-tuning | None (zero-shot) | Core experimental constraint |
| SWA window | w=512 fixed | Ablation on w=256/1024 is secondary if compute budget allows |
| Calibration set | 100 sequences from WikiText-103 validation split | Standard for quantization (GPTQ/AWQ); balances compute and stability |
| Evaluation: LM | WikiText-103 test set (full) | Standard perplexity benchmark for efficiency papers |
| Evaluation: CLS | GLUE SST-2 validation set | Test labels unavailable; validation set is standard practice |
| Random seeds | 3 seeds for random-k baseline | Reduces seed-specific variance in comparison |

---

## Archon Project / Task IDs

| Entity | Archon ID |
|--------|-----------|
| Pipeline Project | 69f47604-8ee4-4c6e-9841-b41acba6a749 |
| Main hypothesis task | abc6c77a-1450-49da-813c-c13e12eaef57 |
| h-e1 task | bcc9ea4e-c975-4627-8a4e-0ce03e3a5c85 |
| h-e2 task | fbc24a54-3ebe-4814-aa71-b0725f202a62 |
| h-m1 task | ae20747c-c7bb-4fca-afdc-540d8bf9ee75 |
| h-m2 task | 2c9ce5b5-fe18-4082-b5f0-9a0238b980dd |
| h-c1 task | 96216ce2-5e07-44fd-9956-03d9c2d55295 |

---

## Next Action

Begin **Phase 2C** with **h-e1** (first READY sub-hypothesis): design experiment for entropy criterion stability verification.
