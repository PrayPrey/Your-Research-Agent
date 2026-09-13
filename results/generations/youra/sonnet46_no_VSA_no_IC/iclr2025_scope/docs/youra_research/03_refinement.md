# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-22T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (independent-controller ablation)
- **Gap ID**: gap_1
- **Gap Title**: Zero-Shot SWA Layer Conversion Accuracy Bounds Without Fine-Tuning in Llama-2-7B
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All 6 convergence criteria met at Exchange 7 — SPECIFIC claim with quantified thresholds, MECHANISM via three-step entropy→SWA→residual stream compensation, PREDICTIONS P1-P3 with quantified success/falsification criteria, NOVELTY vs SWAA/SWARR/HIES, FEASIBILITY confirmed (<1 GPU-hour, existing code paths), OBJECTIONS addressed (calibration stability, depth position, benchmark divergence)

### Key Insights

1. **Selectivity is the key**: SWAA's catastrophic collapse is a full-model phenomenon. Selective conversion of k/32 << 1 layers may avoid it entirely via residual stream global context preservation from the 28 retained full-attention layers.

2. **Entropy as redundancy proxy, not locality proxy**: The entropy criterion's validity isn't about "high-entropy layers attend locally." It's about "high-entropy layers contribute less unique global context than the residual stream already provides." This framing addresses the diffuse-local vs diffuse-global confound.

3. **Residual stream global bus**: The three-step mechanism's key insight is that the residual stream of 28 full-attention layers provides a global context bus for the 4 SWA-converted layers — this is what SWARR inadvertently confirmed by showing that full-model SWA (0 full-attention layers retained) fails.

4. **All outcomes publishable**: Positive result (zero-shot efficiency method), partial result (k* boundary characterization), and negative result (refutation of entropy-local-sufficiency claim) are all publishable findings.

### Breakthrough Moments

- **Exchange 4 (Prof. Pax)**: Identified the residual stream as global context bus — the mechanistic key explaining why selective (not full-model) conversion should work.
- **Exchange 5 (Dr. Ally)**: Reformulated entropy criterion from "diffuse local" to "redundant with residual stream global context" — addressed Prof. Vera's local vs global confound.
- **Exchange 6 (Prof. Rex)**: Converted vague concerns about calibration and depth into concrete diagnostic experimental steps.

---

## Final Hypothesis

### Title
**Entropy-Guided Zero-Shot Selective Sliding Window Attention Conversion in Llama-2-7B**

**Hypothesis ID**: H-EntropySWA-v1

### Core Claim
Under the setting of Llama-2-7B (32 attention layers, no fine-tuning), if the k=4 layers with highest mean per-layer attention entropy (measured on a 100-sequence calibration set using `output_attentions=True`) are replaced with sliding window attention (window size w=512 tokens) zero-shot, then WikiText-103 perplexity will remain within 2 points and GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline, because high-entropy layers already contribute less unique global context than low-entropy layers, and the residual stream of the 28 remaining full-attention layers provides sufficient global context compensation for the converted layers.

### Mechanism

**Step 1 — Entropy Scoring:** Per-layer mean attention entropy (averaged across heads and positions) on 100 calibration sequences identifies layers with diffuse, low-information-value global attention. These are layers that don't exploit sharp global token retrieval — analogous to the prunable heads in Michel et al. [2019] and HIES [Choi et al., 2025].

**Step 2 — SWA Replacement:** Replacing entropy-selected layers with SWA(w=512) aligns the implemented attention mechanism with the measured behavior. Since these layers were already not exploiting sharp global attention, constraining them to a local window does not remove functionality they were actively using.

**Step 3 — Residual Stream Compensation:** The 28 retained full-attention layers propagate global context through the residual stream, compensating for the SWA layers' reduced reach. The SWARR [2026] finding that full-model SWA fails even with SFT confirms that global context loss (0 full-attention layers) is the failure mode; selective conversion (28/32 full-attention layers retained) avoids this.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** *(primary)* | k=4 entropy-guided SWA maintains WikiText-103 perplexity within 2pt of baseline | Δperplexity ≤ 2.0 points | Δperplexity > 2.0 points |
| **P2** | Entropy-guided k=4 outperforms random-k=4 and last-k=4 on perplexity preservation | Δperplexity(entropy) < Δperplexity(random) AND < Δperplexity(last-k) | Entropy ≥ random selection |
| **P3** | k=8 entropy-guided SWA characterizes conversion capacity boundary | Δperplexity(k8) > Δperplexity(k4), characterizing k* | Non-monotone degradation would be anomalous |

---

## Novelty

**Key Innovation:** First empirical characterization of zero-shot accuracy bounds for selective FA→SWA layer conversion, using per-layer attention entropy as a layer-level convertibility signal in a pre-trained causal decoder LLM. SWAA requires fine-tuning for recovery; this work defines the zero-shot frontier.

**Differentiation from Prior Work:**
- vs **SWAA [2025]**: SWAA converts ALL layers + fine-tuning required. H-EntropySWA-v1 converts k/32 << 1 layers + zero-shot. Complementary contributions.
- vs **SWARR [2026]**: Full-model conversion + RL recovery. Not applicable to zero-shot selective setting.
- vs **HIES [2025]**: Head-level entropy for pruning in encoders. This work: layer-level entropy for SWA conversion in causal decoders.
- vs **Michel et al. [2019]**: Head removal (harder constraint). SWA conversion is weaker (maintains head capacity with local window).

---

## Experimental Design

**Model:** Llama-2-7B (`meta-llama/Llama-2-7b-hf`)

**Datasets:** WikiText-103 (`wikitext-103-raw-v1`), GLUE SST-2 (`glue/sst2`) — all via HuggingFace datasets

**Baselines:**
1. Full-attention k=0 (unmodified Llama-2-7B)
2. Random-k=4 SWA (mean of 3 random seeds)
3. Last-k=4 SWA (deepest 4 layers by depth index)
4. Entropy-guided k=8 SWA (boundary characterization)

**Implementation:** `AttentionMaskConverter(is_causal=True, sliding_window=512)` from HuggingFace; or direct `attn_mask` modification per selected layer in `modeling_llama.py`

**Entropy Scoring:**
```python
# For each layer l in Llama-2-7B:
outputs = model(**inputs, output_attentions=True)
attn_weights = outputs.attentions[l]  # (batch, heads, seq, seq)
entropy_l = -(attn_weights * torch.log(attn_weights + 1e-9)).sum(-1).mean()
```

**Calibration Stability Check:** Run on 3 non-overlapping 100-sequence subsets; compute Spearman ρ for top-8 layer rankings; require ρ ≥ 0.8.

---

## Limitations

- Validated only on Llama-2-7B (32 layers, RoPE); generalization to other causal decoders is future work
- Fixed window size w=512; sensitivity to w=256 or w=1024 unexplored (secondary ablation)
- Calibration on WikiText-103 sequences; SST-2 domain calibration may produce different layer rankings (ablation)
- Entropy criterion measures behavior on calibration sequences ≤ ~512 tokens; behavior on longer sequences not characterized
- k* boundary (maximum safe conversion count) may be Llama-2-7B-specific

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-EntropySWA-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 7/7 |
| **Clarity Verified** | Yes |
| **Feasibility Constraint** | PASS — existing datasets, model, benchmarks; no new annotations; <1 GPU-hour |
| **Remaining Objections** | Scoped as limitations/ablations, not experiment blockers |

---

*Phase 2A complete — ready for Phase 2B hypothesis verification planning.*
*Architecture: Self-Contained Tikitaka Loop (independent-controller ablation, Claude plays all personas)*
*Generated: 2026-08-22 | Workflow: phase2a-dialogue*
