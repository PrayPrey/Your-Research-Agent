# H-E1 Context (JIT Generated from Phase 2B)

**Source:** 02b_verification_plan.md
**Generated:** 2026-05-11 (Phase 2C Step 1)
**Hypothesis:** h-e1

---

## Hypothesis Information

**ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None (foundation hypothesis)

**Statement:**
Under fixed-budget inference conditions, if token-level entropy, semantic entropy, and SelfCheckGPT-BERTScore (N=5) are applied to LLaMA-2-7B-chat on the 2,000-example stratified HaluEval-QA sample, then semantic entropy will achieve statistically significantly higher AUROC (≥ 0.05 difference, non-overlapping 95% bootstrap CIs) than at least one baseline UQ method, because a discrimination gap between UQ methods must exist for the comparative hypothesis to be meaningful.

**Rationale:**
This existence hypothesis establishes that differential UQ performance is detectable on HaluEval-QA — a prerequisite for all mechanism hypotheses. Without this gap, the remaining causal chain cannot be validated.

---

## Experimental Setup

### Dataset

- **Name:** HaluEval-QA (QA subset)
- **Type:** standard
- **Source:** Li et al. (2023) arXiv:2305.11747
- **HuggingFace Path:** pminervini/HaluEval or RUCAIBox/HaluEval (QA subset)
- **Sample:** 2,000 stratified examples (balanced hallucination/factual labels by question type)
- **Hypothesis Fit:** Binary hallucination labels enable AUROC computation; QA subset has highest label reliability; 2,000 examples provide stable AUROC estimates (SE < 0.02)

### Models

- **Primary:** LLaMA-2-7B-chat
  - HuggingFace ID: meta-llama/Llama-2-7b-chat-hf
  - Type: Decoder-only causal LM
  - **Hypothesis Fit:** Accessible logits via HuggingFace generate(output_scores=True); known to hallucinate on factual QA; 7B scale feasible on single A100

- **NLI Model:** microsoft/deberta-large-mnli (for semantic entropy clustering)

### UQ Signals (Independent Variables)

1. **token_entropy_mean** — Mean token-level entropy from greedy pass logits
2. **semantic_entropy** — Kuhn et al. 2023 (lorenzkuhn/semantic_uncertainty) with deberta-large-mnli clustering
3. **selfcheckgpt_bertscore_n5** — Manakul et al. 2023 (potsawee/selfcheckgpt), N=5 stochastic samples

### Controlled Variables

- Inference: temp=0 greedy + temp=1.0 stochastic
- Dataset: Fixed 2,000 stratified examples
- NLI model: deberta-large-mnli
- N=5 SelfCheckGPT samples
- Bootstrap resamples: 1,000

---

## Verification Protocol

1. Load HaluEval-QA QA subset; stratified sample 2,000 examples (balanced hallucination/factual labels by question type).
2. Generate LLaMA-2-7B-chat responses: 1 greedy pass (temp=0) for token entropy + 5 stochastic samples (temp=1.0) for SelfCheckGPT; save all logits and samples.
3. Compute token_entropy_mean, semantic_entropy (lorenzkuhn/semantic_uncertainty + deberta-large-mnli), and selfcheckgpt_bertscore_n5 (potsawee/selfcheckgpt).
4. Compute AUROC per method vs. HaluEval binary labels; bootstrap 1,000 resamples for 95% CI; apply Bonferroni correction for 3 pairwise comparisons.
5. Report all AUROC values with CIs; confirm gap ≥ 0.05 with non-overlapping CIs for at least the top vs. bottom ranked methods.

---

## Success Criteria

- **Primary:** At least one pairwise AUROC difference ≥ 0.05 with non-overlapping 95% bootstrap CIs (p < 0.05 after Bonferroni correction)
- **Secondary:** Semantic entropy AUROC > token_entropy_mean AUROC (directional confirmation)

---

## Gate Condition

**Type:** MUST_WORK
**Description:** At least one pairwise AUROC difference ≥ 0.05 with non-overlapping 95% bootstrap CIs. If this fails, H-M1, H-M2, H-M3 are blocked.

**Failure Response:** EXPLORE — investigate whether HaluEval label quality (A1) or model uncertainty collapse (A4) explain null result.

---

## Baseline & Comparison Targets

| Method | Known Performance | Dataset | Notes |
|--------|-------------------|---------|-------|
| Semantic Entropy (Kuhn 2023) | AUROC ~0.78 | TriviaQA | Primary reference point |
| SelfCheckGPT-BERTScore (Manakul 2023) | AUC-PR ~0.85 | WikiBio | Different task |
| Token Entropy (Kadavath 2022) | ECE ~0.05 | Various | Calibration metric, not AUROC |

---

## Dependencies

- **Upstream:** None (first hypothesis)
- **Downstream:** H-M1 depends on H-E1 (MUST_WORK gate)
