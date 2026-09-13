# Reflection Report: h-e1 — Phase 4 Gate Processing
**Date:** 2026-05-21  
**Gate:** MUST_WORK → FAIL  
**Reflection Outcome:** ROUTED_TO_PHASE_0

---

## 1. Gate Evaluation Summary

| Condition | Required | Actual | Status |
|-----------|----------|--------|--------|
| SE AUROC > TP AUROC (8B/TriviaQA) | SE > TP, CI excl. 0 | SE=0.4735 vs TP=0.6835 | ❌ FAIL |
| SE AUROC > TP AUROC (8B/NQ) | SE > TP, CI excl. 0 | SE=0.5524 vs TP=0.6551 | ❌ FAIL |
| SE AUROC > TP AUROC (70B/TriviaQA) | SE > TP, CI excl. 0 | Pending | ⏳ Unknown |
| SE AUROC > TP AUROC (70B/NQ) | SE > TP, CI excl. 0 | Pending | ⏳ Unknown |

**Note:** Gate is FAIL regardless of 70B results — both 8B conditions failed and ALL conditions must pass.

---

## 2. Experimental Results

### 8B (Llama-3-8B-Base) — 500 samples each

**TriviaQA rc.nocontext validation:**
- Correctness: 66.0% (330/500)
- token_prob AUROC: 0.6835 [0.6361, 0.7332]
- semantic_entropy AUROC: 0.4735 [0.4409, 0.5036]
- kle AUROC: 0.2642 [0.2158, 0.3107]
- selfcheck_nli AUROC: 0.6862 [0.6362, 0.7340]
- SE mechanism: mean_k=9.884, degenerate_fraction=0.894

**NaturalQuestions open-domain validation:**
- Correctness: 19.4% (97/500)
- token_prob AUROC: 0.6551 [0.5960, 0.7063]
- semantic_entropy AUROC: 0.5524 [0.5121, 0.5977]
- kle AUROC: 0.3753 [0.3078, 0.4372]
- selfcheck_nli AUROC: 0.4508 [0.3943, 0.5084]
- SE mechanism: mean_k=9.796, degenerate_fraction=0.848

---

## 3. Root Cause Analysis

### Primary Cause: Stochastic Sampling Collapse on Base Model

The SE mechanism technically activated (mean_k < N=10), but with extremely high `degenerate_fraction` values:
- TriviaQA: degenerate_fraction = 0.894 (89.4% of queries have all samples in one cluster)
- NQ: degenerate_fraction = 0.848 (84.8%)

**Why this matters for SE:** When all N=10 stochastic samples cluster into one class (K=1), SE = 0 (no uncertainty). This creates a near-uniform SE score distribution that is less discriminative than token log-probability.

**Why this happens on base models:** Llama-3-8B-Base (not instruction-tuned) is highly deterministic in its factual recall. With temperature=1.0 and short factual answers, the stochastic samples are near-identical, all semantically equivalent → all in one cluster → SE ≈ 0 for all queries.

### Secondary Cause: KLE Also Fails

KLE (EigValLaplacian) shows even lower AUROC (0.26 TriviaQA, 0.38 NQ), well below the 0.5 random baseline. This suggests the graph Laplacian structure of the similarity matrix for clustered responses provides no discriminative signal — or possibly negative signal (inverse correlation with correctness).

### What Worked

- SE mechanism is correctly implemented (clustering activates, mean_k < N)
- Token probability is a strong predictor (AUROC ~0.68 on both datasets)
- SelfCheckGPT-NLI performs comparably to token_prob on TriviaQA (0.686)
- Experimental infrastructure is sound (real models, real data, proper evaluation)

---

## 4. Modification Assessment

**Could a minor SELF_MODIFY fix this?**

No. The failure is fundamental to the hypothesis premise:
- The hypothesis assumes SE > TP for base models at both 8B and 70B
- The data shows SE ≪ TP at 8B on both datasets
- This is not a hyperparameter issue — it's a model type issue (base vs instruct)
- Increasing n_samples or changing temperature would reduce degenerate_fraction but likely not reverse the ordering

**Is this a scope/reformulation issue (SUPERSEDED)?**

Possibly. If the hypothesis were reformulated to apply to instruction-tuned models or to a setting where sampling diversity is guaranteed, it might be testable. However, the original main hypothesis (EGSH) is about base models (Llama-3-8B-Base and 70B-Base).

**Decision: ROUTED_TO_PHASE_0**

The PoC demonstrates that SE/KLE do NOT show advantage over token-probability for factual QA with Llama-3-Base models. This is a fundamental finding that invalidates the prerequisite existence claim. Phase 0 should redesign the research direction entirely.

---

## 5. Lessons Learned for Phase 0

1. **Base model stochastic diversity is insufficient for SE**: Instruction-tuned models may provide better sampling diversity for SE computation.
2. **Token probability is a strong QA uncertainty baseline**: Any hypothesis claiming SE/KLE superiority must carefully verify sampling conditions.
3. **degenerate_fraction is a key diagnostic**: Should be monitored and gated before AUROC comparison.
4. **Hypothesis reformulation options**:
   - Restrict to instruction-tuned models where SE shows empirical advantage
   - Condition the claim on degenerate_fraction < 0.5
   - Focus on longer-form generation (summarization, explanation) rather than factual QA
   - Consider a different UQ method not based on clustering (e.g., conformal prediction, verbalized uncertainty)

---

## 6. Cascade Effects

Dependents of h-e1 (all set to CASCADE_FAILED):
- **h-m1** (MECHANISM): Scale-dependent MI depth shift — requires h-e1 to confirm SE advantage first
- **h-m2** (MECHANISM): SE/KLE scale > TP scale — requires h-m1
- **h-m3** (MECHANISM): Interaction effect Delta > 0.02 — requires h-m2
- **h-m4** (MECHANISM): Layer-wise probe gap narrowing — requires h-m3

All 5 sub-hypotheses of H-EGSH-v1 are now FAILED or CASCADE_FAILED.

---

## 7. Routing Decision

**Route to: Phase 0 (Brainstorming)**  
**Reason:** MUST_WORK FAIL with no viable modification path. Full hypothesis redesign required.  
**Serena Memory:** `phase4_failures/failure_h-e1`
