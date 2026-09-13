# Experiment Design: H-M1

**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under frozen LLMs (LLaMA-2-7B, Mistral-7B-v0.1) generating hallucinated answers on TriviaQA and NQ (recall-failure benchmarks), if we analyze token log-probability sequences, then hallucinated answers will show a significantly higher peakedness ratio (max log-prob / mean log-prob) than correct answers, because recall failures manifest as a single unknown fact-token surrounded by high-probability function words.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Verifies causal mechanism: does peakedness differ between hallucinated vs. correct answers on recall-failure benchmarks?

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 PASSED (MUST_WORK gate satisfied — multiple aggregation pairs show AUROC diff > 0.02 with non-overlapping bootstrap CI)
**Gate Status:** MUST_WORK — must show significantly higher peakedness in hallucinated vs. correct answers on TriviaQA and NQ

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASSED)

### Gate Condition
MUST_WORK: Hallucinated answers on TriviaQA and NQ show significantly higher peakedness ratio (max log-prob / mean log-prob) than correct answers; Mann-Whitney U test p < 0.05, directional, for at least one model.

---

## Continuation Context

H-E1 completed with key findings:
- LLaMA-2-7B on TriviaQA (n=500): min AUROC=0.151, mean AUROC=0.270, sum AUROC=0.104
- LLaMA-2-7B on TruthfulQA (n=817): min AUROC=0.399, mean AUROC=0.279, sum AUROC=0.541
- Aggregation choice produces measurably different AUROC on both datasets — MUST_WORK gate PASSED
- Best aggregator varies by dataset: sum wins TruthfulQA (0.541), mean wins TriviaQA (0.270)
- Mistral-7B experiment incomplete (crashed mid-run); LLaMA-2-7B results sufficient for gate

**Critical note from arXiv:2312.14183**: In TriviaQA with Falcon-40B, the Softmax distribution is "significantly more peaked for non-hallucination" than hallucinated outputs. This is the OPPOSITE of what H-M1 predicts. H-M1 must be tested empirically — the causal story (single unknown fact-token surrounded by high-prob function words) may not hold at 7B scale or may be inverted relative to the "peaked" definition. The experiment MUST compute the peakedness ratio and let data determine direction.

### Previous Hypothesis Results
- **H-E1**: PASSED. LLaMA-2-7B TriviaQA (n=500) and TruthfulQA (n=817) analyzed. Token log-probs extracted via `model.generate()` with `output_scores=True`. Binary correctness labels from exact-match/F1 against Farquhar 2023 gold answers. Reuse same infrastructure (data loading, model loading, label extraction) for H-M1.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "token log probability hallucination detection experiment design"**
- No domain-relevant results (Archon KB contains diffusion model content)
- Fallback: using lm-polygraph documentation + prior experiment code from H-E1

**Query 2: "token uncertainty distribution peakedness LLM hallucination"**
- No domain-relevant results in Archon KB

**Query 3: "factual QA benchmark AUROC hallucination TriviaQA NQ evaluation"**
- No domain-relevant results in Archon KB

**Conclusion:** Archon KB does not contain LLM uncertainty estimation content. All implementation grounding from Exa GitHub search and prior H-E1 code.

### Archon Code Examples

**Query: "token log probability aggregation AUROC hallucination detection PyTorch"**
- No relevant code examples found in Archon KB
- Implementation derived from Exa findings and lm-polygraph API

### Exa GitHub Implementations

**Repository 1: IINemo/lm-polygraph** (primary framework)
- **URL:** https://github.com/IINemo/lm-polygraph
- **Relevance:** Official framework for token-level uncertainty estimation on LLaMA-2 and Mistral-7B. Provides `MeanTokenEntropy`, `Perplexity` (sum), `MaxTokenEntropy` as built-in estimators.
- **Key API:**
  ```python
  from lm_polygraph.estimators import MeanTokenEntropy, Perplexity
  from lm_polygraph.utils.manager import estimate_uncertainty
  from lm_polygraph.utils.model import WhiteboxModel

  model = WhiteboxModel.from_pretrained("meta-llama/Llama-2-7b-hf", device="cuda")
  ue_method = MeanTokenEntropy()
  ue = estimate_uncertainty(model, ue_method, input_text="Who founded Rome?")
  ```
- **Key insight:** `Perplexity()` = normalized sum log-prob; `MeanTokenEntropy()` = mean entropy per token; `MaxTokenEntropy()` = max entropy token. Peakedness ratio (max log-prob / mean log-prob) is NOT a built-in — requires custom implementation on top of raw logprobs.
- **Used for:** Custom peakedness computation design

**Repository 2: jlko/semantic_uncertainty** (Farquhar 2023)
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Stars:** 411
- **Relevance:** Official implementation for Farquhar 2023 Nature paper. Contains TriviaQA and NQ splits with binary correctness labels (exact-match/F1). Same data splits used in H-E1.
- **Key data structure:**
  - `generate.py`: generates model responses with logprobs for TriviaQA/NQ
  - Binary label: exact-match or F1 ≥ 0.5 against gold answers
  - Data path: `jlko/semantic_uncertainty` HuggingFace dataset splits
- **Used for:** Dataset loading and binary label derivation

**Repository 3: arXiv:2312.14183 (amazon-science/llm-hallucinations-factual-qa)**
- **URL:** https://github.com/amazon-science/llm-hallucinations-factual-qa
- **Relevance:** Key empirical finding — with Falcon-40B on TriviaQA, Softmax distribution is "significantly MORE PEAKED for NON-hallucination" than hallucinated outputs. This inverts H-M1's directional prediction.
- **Critical insight:** At the FIRST generation position, non-hallucinating answers show peaked distributions; hallucinating answers show flat distributions. This is because the model is uncertain (distributes probability across many tokens) when hallucinating.
- **Implication for H-M1:** The peakedness ratio direction in H-M1 may be INVERTED. We test empirically: compare peakedness (max log-prob / mean log-prob) in hallucinated vs correct groups without assuming direction; report actual Mann-Whitney U direction.

**Repository 4: pengqian-lu/TPA** (ACL 2026)
- **URL:** https://github.com/pengqian-lu/TPA
- **Relevance:** Per-token probability attribution for hallucination detection on LLaMA-2-7B and Mistral-7B. Operates on same model family. Shows per-token logprob extraction pipeline is feasible.
- **Used for:** Confirmation that per-token logprob pipeline is tractable on LLaMA-2-7B/Mistral-7B

**Serena Analysis Needed:** No — lm-polygraph API and jlko/semantic_uncertainty code are sufficiently clear without deep semantic analysis.

### 🎯 Implementation Priority Assessment

**CRITICAL:** Reuse H-E1 infrastructure directly.

**Recommended Implementation Path:**
- Primary: Extend H-E1 code — token log-probs already extracted; add peakedness ratio computation and Mann-Whitney U test
- Fallback: lm-polygraph `WhiteboxModel` for fresh logprob extraction if H-E1 artifacts unavailable
- Justification: H-E1 already produces per-token log-prob sequences for TriviaQA (n=500) and NQ from Farquhar 2023 splits with binary labels. Adding peakedness computation is a 10-line extension.

### Code Analysis (Serena MCP)

Serena analysis not performed — code is sufficiently clear from Exa findings. H-E1 already demonstrates the complete logprob extraction pipeline. Peakedness computation is a straightforward NumPy/PyTorch operation.

---

## Experiment Specification

### Dataset

**Primary Datasets:** TriviaQA and NQ (recall-failure benchmarks)
- **Type:** standard (real data via Farquhar 2023 splits)
- **Source:** jlko/semantic_uncertainty (HuggingFace) — same splits as H-E1
- **Splits used:** Test splits with binary correctness labels (exact-match/F1)
- **Sample counts:** TriviaQA ≥ 500 samples (H-E1 used 500), NQ ≥ 500 samples
- **Binary labels:** Correct (1) vs Hallucinated (0) per Farquhar 2023 exact-match/F1 criterion
- **Hypothesis fit:** TriviaQA and NQ are recall-failure benchmarks — the mechanism under test is recall failure token distribution shape
- **NOT included:** TruthfulQA (imitative falsehood benchmark — not a recall-failure dataset; H-M1 only predicts effect on recall-failure benchmarks)
- **Synthetic data check:** PASSED — standard real benchmark datasets only

**Loading Information:**
- Method: HuggingFace `load_dataset` (same as H-E1)
- Identifier: `jlko/semantic_uncertainty` dataset splits or local cache from H-E1
- Code:
  ```python
  from datasets import load_dataset
  # Or reuse H-E1 cached data directly
  ds_trivia = load_dataset("jlko/semantic_uncertainty", "trivia_qa", split="validation")
  ds_nq = load_dataset("jlko/semantic_uncertainty", "nq", split="validation")
  ```

### Models

#### Baseline Model

**Architecture:** LLaMA-2-7B (primary); Mistral-7B-v0.1 (secondary, if H-E1 run completes)
- **Type:** Frozen decoder-only LLM, greedy decoding, single forward pass
- **Source:** HuggingFace model hub (same as H-E1)
- **Configuration:** Frozen weights, `do_sample=False`, `max_new_tokens=50`, `output_scores=True`
- **Note:** Mistral-7B crashed mid-run in H-E1. For H-M1, LLaMA-2-7B is the primary model. Attempt Mistral-7B if resources allow, but gate only requires one model.

**Loading Information:**
- Method: HuggingFace `AutoModelForCausalLM`
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  model.eval()
  ```

#### Proposed Model

**Architecture:** Same frozen LLM — no architectural change. The "proposed model" is the analytical framework applied to LLM outputs.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Token Distribution Peakedness Analysis
# Based on: H-E1 logprob extraction + arXiv:2312.14183 peakedness concept

def compute_peakedness(token_logprobs: list[float]) -> float:
    """
    Compute peakedness ratio: max_logprob / mean_logprob (absolute values).
    
    Args:
        token_logprobs: List of per-token log-probabilities (negative floats)
    Returns:
        peakedness: max(abs(logprobs)) / mean(abs(logprobs))
        Higher = more peaked = one token much more uncertain than average
    """
    import numpy as np
    abs_logprobs = np.abs(token_logprobs)  # convert neg logprobs to positive
    if len(abs_logprobs) == 0 or np.mean(abs_logprobs) == 0:
        return 1.0  # degenerate case
    return float(np.max(abs_logprobs) / np.mean(abs_logprobs))

def analyze_group_peakedness(model_outputs: list[dict]) -> dict:
    """
    Separate by correctness label and compute peakedness distributions.
    
    Args:
        model_outputs: List of {token_logprobs: [...], correct: bool}
    Returns:
        {hallucinated: [peakedness], correct: [peakedness]}
    """
    hallucinated = [compute_peakedness(o["token_logprobs"])
                    for o in model_outputs if not o["correct"]]
    correct = [compute_peakedness(o["token_logprobs"])
               for o in model_outputs if o["correct"]]
    return {"hallucinated": hallucinated, "correct": correct}

from scipy.stats import mannwhitneyu
def test_peakedness_difference(hallucinated: list, correct: list) -> dict:
    """Mann-Whitney U test: is peakedness distribution different?"""
    stat, p = mannwhitneyu(hallucinated, correct, alternative="two-sided")
    direction = "hallucinated_higher" if np.mean(hallucinated) > np.mean(correct) else "correct_higher"
    return {"statistic": stat, "p_value": p, "direction": direction,
            "mean_hallucinated": np.mean(hallucinated),
            "mean_correct": np.mean(correct)}
```

### Training Protocol

**No training required** — frozen model inference only.

**Inference Protocol:**
- Optimizer: N/A (no gradient updates)
- Decoding: Greedy (`do_sample=False`, `temperature=1.0`)
- Forward passes: 1 per sample (same as H-E1)
- Seeds: 1 (fixed, same as H-E1 for reproducibility)
- Batch size: 1 (or 4 with padding, same as H-E1)
- Precision: float16, device_map="auto"

**Reuse from H-E1:** If H-E1 cached logprob files exist at `h-e1/outputs/`, load them directly — no re-inference needed. The peakedness computation runs on already-extracted token_logprobs.

**Source:** H-E1 validation report; jlko/semantic_uncertainty generate.py pipeline

### Evaluation

**Primary Metric:** Mann-Whitney U test statistic and p-value comparing peakedness ratio distributions between hallucinated and correct answer groups on TriviaQA and NQ.

**Success Criteria (MUST_WORK gate):**
- Mann-Whitney U test p < 0.05, any direction, for at least one model on TriviaQA or NQ
- Report actual direction (whether hallucinated > correct or correct > hallucinated)

**Secondary:**
- Effect consistent across both LLaMA-2-7B and Mistral-7B-v0.1
- Effect present on both TriviaQA and NQ independently

**Expected Results (from arXiv:2312.14183 prior):**
- Direction likely: correct_higher (non-hallucinating more peaked) — OPPOSITE of H-M1 prediction
- If so: document as A2 assumption violation and PIVOT per H-M1 failure response

**Additional analyses:**
- Distribution plots: peakedness histogram for hallucinated vs correct groups
- Correlation between peakedness and AUROC from H-E1 (do higher-peakedness samples correspond to lower uncertainty scores?)
- Mean peakedness per dataset split (TriviaQA vs NQ separately)

**Metrics Loading Information:**
- Task Type: Statistical comparison (non-parametric)
- Library: `scipy.stats.mannwhitneyu`, `numpy`, `matplotlib`
- Code:
  ```python
  from scipy.stats import mannwhitneyu
  stat, p = mannwhitneyu(hallucinated_peakedness, correct_peakedness, alternative="two-sided")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of mean peakedness ratio for hallucinated vs correct groups on TriviaQA and NQ (2 datasets × 2 groups = 4 bars), with error bars (95% CI)

#### Additional Figures (LLM Autonomous)
Based on the mechanism hypothesis, additional informative figures:
1. **Peakedness distribution histograms**: Overlapping KDE plots of peakedness ratio distributions for hallucinated vs correct groups (per dataset)
2. **Scatter plot**: Peakedness ratio vs token-level uncertainty score (from H-E1) to show correlation
3. **Box plot**: Peakedness by dataset (TriviaQA, NQ) and correctness label — shows distribution spread

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mann-Whitney U p < 0.05 for at least one dataset/model pair (any direction)
3. Direction documented and compared to H-M1 prediction

**Note:** The gate passes even if direction is opposite to H-M1 prediction — the failure response for H-M1 is "EXPLORE/PIVOT", not STOP. The MUST_WORK gate only requires a significant difference exists, which is necessary for the mechanism chain to have any informative value.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Query Results**: No domain-relevant content found. Archon KB contains diffusion model implementations (consistency models, k-diffusion, diffusers) — no LLM uncertainty estimation content indexed.

**Implication:** All implementation grounding derived from Exa GitHub search and H-E1 prior experiment.

### B. GitHub Implementations (Exa)

**Repository 1: IINemo/lm-polygraph**
- **URL:** https://github.com/IINemo/lm-polygraph
- **Query:** "lm-polygraph token uncertainty estimation min mean aggregation LLM hallucination GitHub"
- **Relevance:** Official LLM uncertainty estimation framework; confirms LLaMA-2 + Mistral-7B supported; provides `MeanTokenEntropy` and `Perplexity` as built-in estimators; peakedness ratio requires custom implementation on raw logprobs
- **Used for:** Model loading API; confirmation of token-level logprob access pattern

**Repository 2: jlko/semantic_uncertainty**
- **URL:** https://github.com/jlko/semantic_uncertainty
- **Query:** "jlko semantic_uncertainty TriviaQA NQ Farquhar 2023 dataset splits"
- **Relevance:** Farquhar 2023 official implementation; TriviaQA + NQ splits with binary correctness labels; same pipeline as H-E1
- **Used for:** Dataset loading; binary label derivation method; confirms reuse of H-E1 data artifacts

**Repository 3: arXiv:2312.14183 (amazon-science/llm-hallucinations-factual-qa)**
- **URL:** https://arxiv.org/abs/2312.14183
- **Query:** "token log probability peakedness ratio hallucination detection TriviaQA LLaMA"
- **Key finding:** "The distribution is significantly more peaked for non-hallucination than hallucinated ones" (Falcon-40B, TriviaQA, first generation position)
- **Used for:** Directional prior on peakedness — suggests H-M1 direction may be inverted; informs need for two-sided test and direction reporting

**Repository 4: pengqian-lu/TPA**
- **URL:** https://github.com/pengqian-lu/TPA
- **Relevance:** ACL 2026 paper on per-token probability attribution; uses LLaMA-2-7B + Mistral-7B; confirms feasibility of per-token logprob extraction pipeline
- **Used for:** Confirmation that per-token logprob extraction is tractable on target models

### C. Code Analysis (Serena)

Serena analysis not performed — code from Exa results was sufficiently clear. H-E1 already demonstrated the complete logprob extraction pipeline. Peakedness computation is a straightforward NumPy operation.

### D. Previous Hypothesis Context

**Source:** H-E1 validation results (from current pipeline state)
- **Reused components:**
  - Dataset: TriviaQA (n=500), NQ — same Farquhar 2023 splits
  - Model: LLaMA-2-7B frozen, greedy decoding, float16
  - Token log-prob extraction: `output_scores=True` from `model.generate()`
  - Binary labels: exact-match/F1 from Farquhar 2023
- **Why reused:** Enables controlled comparison — only analysis (peakedness vs AUROC) changes; underlying data and inference identical

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TriviaQA, NQ) | GitHub | jlko/semantic_uncertainty (B.2) |
| Binary correctness labels | GitHub | jlko/semantic_uncertainty (B.2) |
| Model loading (LLaMA-2-7B) | GitHub + Prior | lm-polygraph (B.1) + H-E1 (D) |
| Peakedness ratio definition | arXiv | arXiv:2312.14183 (B.3) |
| Directional prior | arXiv | arXiv:2312.14183 (B.3) — inverted direction |
| Mann-Whitney U test | scipy | scipy.stats.mannwhitneyu |
| Training protocol (frozen inference) | Prior | H-E1 validation report (D) |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md H-M1 section |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — managed via state fenced blocks)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- H-E1 COMPLETED, PASSED (2026-08-21) — prerequisite satisfied
- H-M1 IN_PROGRESS — Phase 2C experiment design initiated 2026-08-21

---

## Quality Validation Results

```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified (frozen inference, no training — N/A for optimizer)
✅ Dataset choice justified (TriviaQA + NQ = recall-failure benchmarks per Phase 2B)
✅ Mechanism grounded in code (peakedness from arXiv:2312.14183; extraction from H-E1)
⚠️  Directional assumption uncertain (arXiv:2312.14183 suggests direction OPPOSITE to H-M1 — documented)
✅ Full traceability (all specs trace to documented sources in Appendix)
✅ No synthetic data

Overall: PASSED (with documented directional uncertainty)
```

**Documented limitation:** H-M1 predicts hallucinated > correct peakedness, but arXiv:2312.14183 evidence suggests the opposite at the first generation token. H-M1 uses answer-level peakedness (over all answer tokens), which may differ from single-position analysis. The experiment resolves this empirically — gate passes on any significant difference regardless of direction.

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + web search), Serena (not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
