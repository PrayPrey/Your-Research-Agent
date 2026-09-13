# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under factual QA with black-box Llama-3-8B-Instruct at temperature=0.7, if we compute SMC-NLI (fraction of entailment/neutral pairs among N=10 sample pairs) for 1000 HaluEval questions, then the SMC-NLI score distribution will show meaningful variation across questions (not uniformly high or low), enabling AUROC > 0.60 on HaluEval binary hallucination labels, because correct answers concentrate samples while hallucinated answers spread them.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK (gate not yet evaluated — awaiting Phase 4 results)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition

MUST_WORK gate: SMC-NLI AUROC > 0.60 on HaluEval binary hallucination labels (1000 questions). Failure blocks the entire verification chain (H-M1, H-M2, H-M3 all depend on this).

---

## Continuation Context

No prior hypothesis — this is the first hypothesis in the verification chain.

### Previous Hypothesis Results (if applicable)

None — H-E1 is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

> **Note:** Archon MCP was unavailable in this session. Research performed via WebSearch. All findings documented with web sources.

**Query 1: SMC-NLI / SelfCheckGPT experiment design**

- **SelfCheckGPT (Manakul et al. 2023, EMNLP)**
  - Dataset used: WikiBio (open-ended biographical generation) — primary evaluation
  - NLI model: DeBERTa-v3-large fine-tuned on Multi-NLI
  - Method: Prob(contradiction) as inconsistency score per sentence vs. sampled passages
  - Key insight: NLI variant uses sentence-level scoring (premise = sentence, hypothesis = sampled passage)
  - Reported AUROC: ~0.58 on a HaluEval-based external evaluation
  - Source: [github.com/potsawee/selfcheckgpt](https://github.com/potsawee/selfcheckgpt)

- **SINdex / SAC3 (2023-2024)**
  - SAC3 uses cross-consistency (question perturbation + answer perturbation) across samples
  - NLI DeBERTa-v3-large used for semantic equivalence clustering
  - Benchmarks: HaluEval-QA, TruthfulQA, FinanceBench
  - Key insight: bidirectional NLI (entailment in both directions) is more robust than unidirectional

**Query 2: Implementation challenges and best practices**

- Pairwise NLI on N=10 samples yields C(10,2)=45 pairs — computationally feasible in batch mode
- DeBERTa-v3-large has 434M parameters; batched inference with batch_size=8-16 on GPU is standard
- Short factual answers (1-3 tokens) can cause NLI OOD issue: NLI models trained on sentence-length text may collapse
  - Mitigation: prepend the question to each answer before NLI scoring (e.g., "Q: [question] A: [answer]")
  - Alternative: use SMC-Embed (cosine similarity with all-mpnet-base-v2) as parallel robustness check
- HaluEval QA has balanced 50/50 labels — ideal for AUROC evaluation without class imbalance correction

**Query 3: Benchmark expected performance**

- SelfCheckGPT-NLI on external HaluEval evaluation: ~0.58 AUROC (reported in benchmark comparisons)
- Semantic Entropy / Semantic Uncertainty: ~0.75-0.80 AUROC on TriviaQA/NQ (but requires logits — white-box)
- Verbalized confidence baseline: ~0.55-0.65 AUROC (known to be poorly calibrated)
- SMC-NLI target for H-E1: > 0.60 (conservative PoC threshold, achievable given SelfCheckGPT baseline)

### Archon Code Examples

> Archon MCP unavailable. Code examples sourced from SelfCheckGPT official GitHub (WebSearch).

**SelfCheckGPT-NLI official implementation pattern (potsawee/selfcheckgpt):**

```python
# Official SelfCheckGPT NLI implementation pattern
from selfcheckgpt.modeling_selfcheck import SelfCheckNLI
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
selfcheck_nli = SelfCheckNLI(device=device)
# sentences: list of sentences from primary response
# sampled_passages: list of N stochastic sample texts
sent_scores_nli = selfcheck_nli.predict(
    sentences=sentences,
    sampled_passages=[sample1, sample2, sample3],
)
# Output: Prob(contradiction) per sentence — lower = more consistent
```

Note: H-E1 uses pairwise NLI (all 45 pairs among 10 samples), not sentence-vs-passage scoring. The DeBERTa model is shared; the scoring logic differs.

### Exa GitHub Implementations

> **Note:** Exa MCP unavailable. GitHub findings via WebSearch.

**Repository 1**: potsawee/selfcheckgpt
- **URL**: https://github.com/potsawee/selfcheckgpt
- **Relevance**: Official SelfCheckGPT implementation — closest reference for NLI-based consistency scoring
- **Architecture**: NLI scoring via `cross-encoder/nli-deberta-v3-large` (HuggingFace cross-encoder)
- **Key Code Pattern**:
  ```python
  # NLI pairwise scoring core
  from transformers import AutoTokenizer, AutoModelForSequenceClassification
  model_name = "cross-encoder/nli-deberta-v3-large"
  tokenizer = AutoTokenizer.from_pretrained(model_name)
  model = AutoModelForSequenceClassification.from_pretrained(model_name)
  # Labels: contradiction=0, entailment=1, neutral=2
  ```
- **Training Config**: N/A (inference-only; no training needed for SMC scoring)
- **Dataset**: WikiBio (original), adaptable to HaluEval QA
- **Results**: ~0.65-0.75 AUROC on WikiBio biography generation

**Repository 2**: RUCAIBox/HaluEval
- **URL**: https://github.com/RUCAIBox/HaluEval
- **Relevance**: Official HaluEval dataset with qa_data.json containing binary hallucination labels
- **Key Files**: `data/qa_data.json` — 10,000 QA pairs with hallucinated/correct labels (50/50 balance)

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is NOT a paper-reproduction experiment — it tests a new SMC-NLI framing (pairwise consistency ratio, not sentence-level contradiction). The SelfCheckGPT repo is a reference for the NLI scorer component, not the full algorithm.

**Recommended Implementation Path:**
- Primary: Custom SMC-NLI scorer (pairwise, not sentence-level) using `cross-encoder/nli-deberta-v3-large`
- Fallback: Adapt SelfCheckGPT-NLI scoring, but aggregate at question level
- Justification: H-E1 hypothesis tests pairwise fraction of (entailment+neutral)/45 pairs, which differs from SelfCheckGPT's sentence-vs-passage design. Custom implementation required, but DeBERTa NLI model is shared.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. SelfCheckGPT NLI implementation is straightforward: load DeBERTa cross-encoder, batch-score (premise, hypothesis) pairs, take label logits.

---

## Experiment Specification

### Dataset

**Name:** HaluEval QA (primary) + SMC-Embed robustness check on same subset

**Type:** standard (real, publicly available)

**Source:** HuggingFace / GitHub RUCAIBox/HaluEval

**Statistics:**
- Total QA pairs: 10,000 (balanced: 5,000 hallucinated, 5,000 correct)
- Subset used for H-E1: 1,000 questions (random sample, stratified 50/50)
- Format: question + hallucinated_answer + right_answer + binary label

**Hypothesis Fit:** HaluEval has balanced binary hallucination labels (50/50), making AUROC evaluation directly meaningful without class imbalance. Labels are gold-standard (ChatGPT-generated hallucinations reviewed by humans). Primary benchmark as specified in Phase 2B Section 2.2.

**Preprocessing:**
- Load `qa_data.json` from RUCAIBox/HaluEval GitHub (or HuggingFace mirror)
- Extract fields: `question`, `right_answer`, `hallucinated_answer`, binary label
- Note: we do NOT use the provided answers — we generate our own from Llama-3-8B-Instruct
- Labels (binary): `right_answer` → 0 (non-hallucinated), `hallucinated_answer` → 1 (hallucinated)
- Stratified sample 500 non-hallucinated + 500 hallucinated question instances

**Augmentation:** None (inference-only experiment)

**Loading Information** (for Phase 4 download):
- Method: GitHub JSON download + optional HuggingFace mirror
- Identifier: `RUCAIBox/HaluEval` (GitHub) or `pminervini/HaluEval` (HuggingFace)
- Code:
  ```python
  # Option 1: Direct JSON
  import json, requests
  url = "https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/qa_data.json"
  data = json.loads(requests.get(url).text)
  
  # Option 2: HuggingFace
  from datasets import load_dataset
  dataset = load_dataset("pminervini/HaluEval", "qa")
  ```

### Models

#### Baseline Model

**Architecture:** Llama-3-8B-Instruct (black-box inference — no logit access used)

**Type:** Decoder-only autoregressive LLM (instruction-tuned)

**Source:** HuggingFace: `meta-llama/Meta-Llama-3-8B-Instruct`

**Configuration:**
- Parameters: 8B
- Input format: instruction-following chat template
- Sampling: temperature=0.7, top_p=0.9, max_new_tokens=50
- N samples per question: 10
- Total inference calls: 1,000 questions × 10 samples = 10,000 forward passes

**Hypothesis Fit:** Achieves ~60-70% factual accuracy on TriviaQA (both hallucination and correct regimes populated), fully local (no API cost), supports sampling with temperature control.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
  ```python
  from transformers import AutoTokenizer, AutoModelForCausalLM
  import torch
  model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  model = AutoModelForCausalLM.from_pretrained(
      model_id, torch_dtype=torch.float16, device_map="auto"
  )
  ```

**Additional Component: NLI Scorer**
- Model: `cross-encoder/nli-deberta-v3-large`
- Purpose: Pairwise NLI scoring to compute SMC-NLI
- Loading:
  ```python
  from transformers import AutoTokenizer, AutoModelForSequenceClassification
  nli_model_id = "cross-encoder/nli-deberta-v3-large"
  nli_tokenizer = AutoTokenizer.from_pretrained(nli_model_id)
  nli_model = AutoModelForSequenceClassification.from_pretrained(nli_model_id)
  # Label mapping: {contradiction: 0, entailment: 1, neutral: 2}
  ```

**Additional Component: Embedding Model (SMC-Embed, robustness check)**
- Model: `sentence-transformers/all-mpnet-base-v2`
- Loading:
  ```python
  from sentence_transformers import SentenceTransformer
  embed_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
  ```

#### Proposed Model

**Architecture:** Baseline (Llama-3-8B-Instruct) + SMC-NLI scoring head (post-hoc, no training)

**Core Mechanism Implementation:**

```python
# SMC-NLI: Semantic Mode Consistency via NLI
# Based on: SelfCheckGPT NLI design (Manakul et al. 2023)
# H-E1 adaptation: pairwise scoring, question-level AUROC

import torch
import itertools
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class SMC_NLI:
    """
    Pairwise NLI-based consistency scorer.
    SMC-NLI = fraction of (entailment + neutral) pairs among N*(N-1)/2 pairs.
    High score = consistent (likely factual). Low score = inconsistent (likely hallucinated).
    """
    def __init__(self, model_id="cross-encoder/nli-deberta-v3-large", device="cuda"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id).to(device)
        self.device = device
        # Label order for cross-encoder/nli-deberta-v3-large: contradiction=0, entailment=1, neutral=2

    def score(self, question: str, samples: list[str], batch_size: int = 16) -> float:
        """
        Args:
            question: the factual QA question (prepended to ground answers)
            samples: list of N=10 generated answers
            batch_size: NLI inference batch size
        Returns:
            smc_nli: float in [0,1], higher = more consistent
        """
        # Prepend question for short-answer NLI robustness (OOD mitigation)
        prefixed = [f"Q: {question} A: {s}" for s in samples]
        pairs = list(itertools.combinations(range(len(prefixed)), 2))
        premises = [prefixed[i] for i, j in pairs]
        hypotheses = [prefixed[j] for i, j in pairs]

        scores = []
        for k in range(0, len(pairs), batch_size):
            enc = self.tokenizer(
                premises[k:k+batch_size], hypotheses[k:k+batch_size],
                return_tensors="pt", truncation=True, max_length=512, padding=True
            ).to(self.device)
            with torch.no_grad():
                logits = self.model(**enc).logits
            probs = torch.softmax(logits, dim=-1)  # [B, 3]
            # entailment=1, neutral=2; contradiction=0
            ent_neut = (probs[:, 1] + probs[:, 2]).cpu().numpy()
            scores.extend(ent_neut.tolist())

        return float(np.mean(scores))  # SMC-NLI score for this question
```

### Training Protocol

> **EXISTENCE (PoC):** No model training. This is an inference-only experiment. "Training protocol" here means inference hyperparameters.

**Inference Configuration:**
- **LLM sampling:** temperature=0.7, top_p=0.9, do_sample=True, max_new_tokens=50
  - Source: Phase 2B Section 1.5 (A4); SelfCheckGPT paper used temperature ~0.7
- **NLI batch size:** 16 (pairs per batch); fits within 16GB VRAM with DeBERTa-large
  - Source: SelfCheckGPT official implementation defaults
- **N samples per question:** 10 (45 pairwise combinations)
  - Source: Phase 2B Section 2.2 (H-E1 specification)
- **Questions evaluated:** 1,000 (stratified 500 correct + 500 hallucinated)
  - Source: Phase 2B Section 1.5 (A3)
- **Seed:** 42 (fixed for reproducibility of random sample selection from HaluEval)
- **Hardware assumption:** single GPU, ≥16GB VRAM (A100/V100/RTX 3090)

**Estimated compute:**
- Llama-3-8B inference: 10,000 calls × ~0.5s = ~1.4 hours (GPU)
- NLI scoring: 1,000 questions × 45 pairs = 45,000 NLI forward passes × ~8ms = ~6 min (batched)
- Total: ~1.5-2 hours on single A100

### Evaluation

**Task Type:** Binary classification (hallucinated vs. correct)

**Primary Metrics:**
- **AUROC (Area Under ROC Curve):** main metric. Threshold-free, appropriate for 50/50 balanced labels.
  - Computed: `sklearn.metrics.roc_auc_score(labels, -smc_nli_scores)` (note: lower SMC-NLI = more hallucinated, so negate)
- **SMC-NLI distribution std:** secondary existence check. std > 0.05 confirms non-degenerate distribution.

**Parallel robustness check (SMC-Embed):**
- Compute mean pairwise cosine similarity using all-mpnet-base-v2
- AUROC computed identically
- If SMC-NLI AUROC < 0.60 but SMC-Embed AUROC > 0.60: NLI OOD confirmed, switch primary metric

**Success Criteria (PoC — EXISTENCE):**
- `proposed_metric > baseline_metric` where:
  - Proposed: SMC-NLI AUROC > 0.60
  - Baseline: random classifier AUROC = 0.50
- Secondary: SMC-NLI std > 0.05

**Expected Baseline Performance (from research):**
- SelfCheckGPT-NLI on HaluEval-adjacent tasks: ~0.58 AUROC (benchmarks found in WebSearch)
- Verbalized confidence baseline: ~0.55-0.65 AUROC
- Random baseline: 0.50 AUROC
- SMC-NLI target: > 0.60 (conservative — within reach given pairwise scoring improvement)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification
- Library: sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  import numpy as np
  auroc = roc_auc_score(labels, -np.array(smc_nli_scores))
  std_check = np.std(smc_nli_scores) > 0.05
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — SMC-NLI AUROC vs. random baseline (0.50) vs. SMC-Embed AUROC

#### Additional Figures (LLM Autonomous)
Phase 4 Coder should generate figures that best communicate H-E1 results. Suggested (LLM decides final set):
1. **SMC-NLI score distribution** — histogram split by label (correct vs. hallucinated), to visually confirm separation
2. **ROC curve** — SMC-NLI and SMC-Embed on same plot
3. **SMC-NLI vs SMC-Embed scatter** — per-question correlation to assess when they disagree

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `smc_nli_auroc > 0.60` (proposed > baseline 0.50)

**Failure Routing (from Phase 2B):**
- IF SMC-NLI AUROC < 0.60 but SMC-Embed AUROC > 0.60: NLI is OOD → switch to SMC-Embed as primary; continue to H-M1 with SMC-Embed
- IF both < 0.60: PIVOT — stop main experiment, reassess

---

## 🔬 Mechanism Verification Protocol

**Purpose:** Verify the SMC-NLI mechanism actually functions — not just that code runs.

**Pre-conditions (check before running):**
- `mechanism_exists`: DeBERTa-v3-large NLI model loads and produces 3-class logits for (premise, hypothesis) pairs ✓
- `mechanism_isolatable`: SMC-NLI score is computed independently per question — no cross-question dependencies ✓
- `baseline_measurable`: AUROC against binary HaluEval labels is well-defined (sklearn.metrics.roc_auc_score) ✓
- `architecture_compatibility`: Llama-3-8B-Instruct supports temperature sampling; DeBERTa cross-encoder accepts any text pair ✓

**Activation Indicators (log during execution):**
- `mechanism_log_message`: "SMC-NLI score for question {i}: {score:.4f} | Label: {label}" — logged per question
- `tensor_shape_change`: NLI logits shape = [batch_size, 3]; softmax output = [batch_size, 3] (entailment/contradiction/neutral)
- `metric_delta_expected`: Mean SMC-NLI(correct) should be > mean SMC-NLI(hallucinated) by at least 0.05

**Mechanism Verification Code:**
```python
# Sanity check — run on 5 questions before full experiment
def verify_mechanism(model, tokenizer, nli_model, nli_tokenizer, sample_questions, device):
    """Run on 5 questions; assert NLI produces valid 3-class probs and scores vary."""
    scores = []
    for q_data in sample_questions[:5]:
        samples = generate_samples(model, tokenizer, q_data["question"], N=10, temp=0.7)
        smc = score_smc_nli(nli_model, nli_tokenizer, q_data["question"], samples, device)
        scores.append(smc)
        print(f"Q: {q_data['question'][:50]} | SMC-NLI: {smc:.4f} | Label: {q_data['label']}")
    assert max(scores) - min(scores) > 0.01, "FAIL: SMC-NLI scores degenerate (no variation)"
    assert 0.0 <= min(scores) <= max(scores) <= 1.0, "FAIL: SMC-NLI scores out of [0,1]"
    print("✅ Mechanism verification PASSED")
```

**Failure Detection:**
- IF all SMC-NLI scores cluster near 1.0 → NLI always predicts entailment/neutral (OOD); switch to SMC-Embed
- IF all SMC-NLI scores cluster near 0.0 → NLI always predicts contradiction (inverted OOD); switch to SMC-Embed
- IF std(scores) < 0.01 → degenerate; STOP and investigate NLI model or question format

**Success Criteria (mechanism level):**
- `hypothesis_support_threshold`: SMC-NLI AUROC > 0.60
- `hypothesis_support_metric`: `sklearn.metrics.roc_auc_score(labels, -np.array(smc_nli_scores))`

---

## Appendix: Reference Implementations

### A. Web Search Sources (Archon MCP unavailable)

**Source A.1**: SelfCheckGPT (Manakul et al., EMNLP 2023)
- **URL**: https://github.com/potsawee/selfcheckgpt
- **Query Used**: "SelfCheckGPT NLI pairwise sampling AUROC HaluEval"
- **Relevance**: Official NLI-based consistency scorer; DeBERTa-v3-large model and inference pattern
- **Key Insights**:
  - NLI model: `cross-encoder/nli-deberta-v3-large`
  - Sentence-level scoring (our H-E1 uses question-level pairwise, which is a design variation)
  - Prob(contradiction) used as inconsistency signal (we use 1 - Prob(contradiction) = SMC-NLI)
- **Used For**: NLI model selection, code pattern for DeBERTa inference

**Source A.2**: HaluEval (Li et al., 2023)
- **URL**: https://github.com/RUCAIBox/HaluEval
- **Query Used**: "HaluEval dataset HuggingFace load_dataset binary hallucination labels"
- **Relevance**: Official dataset with 10,000 QA pairs, balanced 50/50 hallucination labels
- **Key Insights**:
  - `data/qa_data.json` contains question, right_answer, hallucinated_answer
  - HuggingFace mirror: `pminervini/HaluEval`
- **Used For**: Dataset selection, loading code, label format

**Source A.3**: SAC3 / SINdex (2023-2024)
- **URL**: https://arxiv.org/pdf/2311.01740
- **Query Used**: "semantic mode consistency sampling NLI DeBERTa hallucination prediction"
- **Relevance**: Bidirectional NLI for semantic equivalence clustering — confirms DeBERTa-v3-large as standard NLI scorer
- **Key Insights**:
  - Bidirectional NLI (entailment in both directions) improves robustness
  - Question prepending to short answers helps OOD issue
- **Used For**: OOD mitigation strategy (question prepending), NLI label interpretation

### B. GitHub Implementations

**Repository B.1**: potsawee/selfcheckgpt
- **URL**: https://github.com/potsawee/selfcheckgpt
- **Query Used**: "potsawee selfcheckgpt GitHub implementation NLI pairwise sampling code example"
- **Relevance**: Direct reference implementation for NLI consistency detection
- **Key Code** (annotated):
  ```python
  # SelfCheckGPT NLI — sentence vs. passages scoring
  selfcheck_nli = SelfCheckNLI(device=device)  # loads cross-encoder/nli-deberta-v3-large
  sent_scores_nli = selfcheck_nli.predict(
      sentences=sentences,       # list of sentences from primary response
      sampled_passages=[s1, s2, s3],  # list of N stochastic samples
  )
  # H-E1 modification: replace sentence-vs-passage with pairwise answer scoring
  ```
- **Configuration Extracted**: batch_size=16, truncation=True, max_length=512
- **Used For**: NLI model loading, batch inference pattern, SMC-NLI pseudo-code

**Repository B.2**: RUCAIBox/HaluEval
- **URL**: https://github.com/RUCAIBox/HaluEval
- **Configuration Extracted**: `data/qa_data.json` structure — `{question, right_answer, hallucinated_answer}`
- **Used For**: Dataset loading, label extraction code

### C. Code Analysis (Serena)

Serena analysis not performed — code from SelfCheckGPT is sufficiently clear for H-E1 implementation. NLI scorer is a standard HuggingFace cross-encoder; no complex architecture to analyze.

### D. Previous Hypothesis Context

None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: HaluEval QA | Web search | Source A.2 (RUCAIBox/HaluEval) |
| Dataset loading code | Web search | Source A.2 (HuggingFace mirror) |
| NLI model: DeBERTa-v3-large | Web search | Source A.1, A.3 |
| NLI scoring pattern | GitHub | Repo B.1 (SelfCheckGPT) |
| Pairwise SMC-NLI formula | Phase 2B | 02b_verification_plan.md Section 2.2 |
| N=10 samples, temperature=0.7 | Phase 2B | 02b_verification_plan.md Section 1.5 (A4) |
| 1000 questions subset | Phase 2B | 02b_verification_plan.md Section 1.5 (A3) |
| AUROC success threshold > 0.60 | Phase 2B | 02b_verification_plan.md Section 2.2 |
| Question prepending (OOD fix) | Web search | Source A.3 (SAC3) |
| SMC-Embed robustness check | Phase 2B | 02b_verification_plan.md Section 2.2 |
| LLM: Llama-3-8B-Instruct | Phase 2B | 02b_verification_plan.md Section 1.3 |
| Inference hyperparameters | Phase 2B + A.1 | SelfCheckGPT defaults |
| Evaluation metric: sklearn AUROC | Phase 2B | Standard for binary classification |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in pipeline block)
**Date:** 2026-08-31

### Workflow History for This Hypothesis

- Phase 2C experiment design: COMPLETED (2026-08-31)

---

*Research Tools Used: WebSearch (Archon MCP and Exa MCP unavailable in this session)*
*All specifications grounded in real implementations and real datasets*
*Next Phase: Phase 3 - Implementation Planning*
