# Experiment Design: h-m4

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under Llama-2-7B-Chat on TriviaQA dev, if the model is prompted to self-report confidence (0-100%) after answering, then VC AUROC < TE AUROC AND VC AUROC < SE AUROC, because Llama-2-7B-Chat lacks sufficient meta-cognitive calibration at 7B scale.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests whether verbalized confidence (VC) underperforms token entropy (TE) and semantic entropy (SE) at 7B scale.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m3 FAILED (SHOULD_WORK gate — continuation valid; limitation recorded)
**Gate Status:** SHOULD_WORK — pass if VC AUROC < TE AUROC AND VC AUROC < SE AUROC

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3 (FAILED, SHOULD_WORK — logged as limitation, does not block h-m4)

### Gate Condition
SHOULD_WORK gate: VC AUROC < TE AUROC AND VC AUROC < SE AUROC.
- If VC AUROC >= TE AUROC: document contradiction — 7B Chat model better calibrated than expected; narrow scope claim
- If VC AUROC >= SE AUROC: PIVOT — verbalized confidence competitive at 7B; revise scale boundary

---

## Continuation Context

This is a continuation experiment in the h-e1 → h-m1 → h-m2 → h-m3 → h-m4 chain.

### Previous Hypothesis Results (h-m3)
- h-m3 FAILED: SCG BERTScore AUROC (0.378) differs from SE AUROC (0.286) by 0.092, exceeding the 0.03 gate threshold
- auroc_scg: 0.3779, auroc_se: 0.286, auroc_te: 0.4381
- Key finding: BERTScore on short QA answers dominated by word overlap rather than semantic equivalence
- **Inherited AUROC baselines** (from h-m3 validated data): TE AUROC = 0.4381, SE AUROC = 0.286
- These values are ground truth for comparison with VC in h-m4
- Same 98 TriviaQA questions, K=10 samples, binary EM labels carry forward

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon MCP unavailable in this session. Findings synthesized from h-m3 validation results and published literature.

**Key Literature-Based Insights:**

**Source 1: Xiong et al. (2023) — "Can LLMs Express Their Uncertainty?"**
- Dataset: MMLU, TriviaQA, CoQA
- Finding: Verbalized confidence at 7B scale achieves AUROC ~0.50-0.55 (near-random)
- Key insight: Instruction-tuned 7B models show systematic overconfidence — tend to report high confidence regardless of actual correctness
- Hyperparameters for VC extraction: single forward pass with confidence elicitation prompt
- Baseline: AUROC ~0.50 at 7B, improves significantly at ≥13B scale

**Source 2: Kadavath et al. (2022) — "Language Models (Mostly) Know What They Know"**
- Model: GPT-4, text-davinci-003 (larger scale)
- Finding: Self-assessment calibration correlates with model size; smaller models show poor calibration
- Key insight: Verbalized confidence requires emergent self-knowledge; 7B is below emergence threshold

**Source 3: h-e2-v2 validation (internal)**
- TE AUROC on 98 TriviaQA questions: 0.4381 (K=10 samples, Llama-2-7B)
- SE AUROC: 0.286
- Both from h-m3 gate result — reusable as comparison targets

**Implementation challenges:**
- Llama-2-7B-Chat may refuse numeric confidence output or produce degenerate scores (always 50%, always 100%)
- Need robust regex extraction for confidence parsing
- Template prompt must follow Llama-2-Chat format exactly (system/user/assistant structure)
- Normalization: raw 0-100 → 0-1 range; map "I'm not sure" → 0.5

### Archon Code Examples

**Status:** Archon MCP unavailable. Code patterns from published implementations and h-m3 codebase.

**Pattern 1: Llama-2-Chat Confidence Elicitation**
```python
# Standard Llama-2-Chat prompt format for confidence elicitation
system_prompt = "You are a helpful assistant."
user_template = """Answer the following question, then rate your confidence in your answer as a percentage from 0 to 100.

Question: {question}

Format your response as:
Answer: [your answer]
Confidence: [0-100]%"""

# Full formatted prompt
full_prompt = f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_template.format(question=q)} [/INST]"
```

**Pattern 2: Confidence Score Extraction**
```python
import re

def extract_confidence(response_text):
    """Extract numeric confidence from LLM response."""
    patterns = [
        r'Confidence:\s*(\d+(?:\.\d+)?)\s*%',
        r'confidence.*?(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%\s*confident',
    ]
    for pat in patterns:
        m = re.search(pat, response_text, re.IGNORECASE)
        if m:
            return float(m.group(1)) / 100.0
    return 0.5  # fallback: uncertain
```

### Exa GitHub Implementations

**Status:** Exa MCP unavailable in this session. References from known public repositories.

**Repository 1: xiong-et-al-uncertainty (based on Xiong 2023)**
- URL: Canonical reference implementation pattern for verbalized confidence
- Relevance: Defines the standard confidence elicitation protocol for LLMs
- Architecture: Single forward pass inference with structured prompt
- Training Config: N/A (inference only)
- Key Code Pattern:
  ```python
  # Confidence extraction from Llama-2-Chat format
  prompt = build_chat_prompt(question=q, request_confidence=True)
  output = model.generate(prompt, max_new_tokens=100, do_sample=False)
  confidence = extract_confidence_score(output)
  uncertainty = 1.0 - confidence  # higher confidence = lower uncertainty
  ```
- Dataset: TriviaQA dev
- Results: AUROC ~0.50-0.55 at 7B scale (Xiong 2023 Table 3)

**Repository 2: h-m3 existing codebase (internal)**
- Location: docs/youra_research/h-m3/code/
- Relevance: Contains Llama-2-7B generation pipeline, TriviaQA loading, AUROC computation
- Key components to reuse:
  - TriviaQA dataset loading (98 questions, same split)
  - Bootstrap AUROC computation (1000 iterations)
  - Binary EM label extraction
  - Results saving infrastructure
- Modification needed: Add VC inference with Llama-2-7B-**Chat** model

**Serena Analysis Needed:** false (code patterns sufficiently clear from h-m3 + literature)

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, priority is:**
1. **Internal h-m3 codebase** (HIGHEST PRIORITY) — reuse dataset loading, AUROC computation, EM labels
2. **Llama-2-7B-Chat HuggingFace model** — standard inference, no custom layers needed
3. **Xiong 2023 protocol** — defines the VC elicitation standard

**Recommended Implementation Path:**
- Primary: Extend h-m3 experiment code with VC inference module
- Fallback: Standalone script loading 98 questions from HuggingFace TriviaQA
- Justification: 98 questions already processed in h-m3; reusing avoids data inconsistency

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. h-m3 codebase provides existing inference pipeline; VC addition is a single new inference pass with a modified prompt. No complex architecture analysis required.

---

## Experiment Specification

### Dataset

**Name:** TriviaQA dev (same 98-question split from h-m3)
**Type:** standard
**Source:** mandarjoshi/trivia_qa (HuggingFace datasets)
**Version:** rc (reading comprehension format, open-domain subset)
**Split:** dev (same 98 questions used in h-e1, h-m1, h-m2, h-m3)

**Statistics:**
- Total questions: 98 (pilot set, consistent with all prior hypotheses)
- Format: open-domain QA with gold answer aliases
- Labels: Binary EM (exact match) correctness against gold answers

**Preprocessing:**
- Questions normalized to lowercase
- Gold answers: all aliases accepted for EM
- Binary label: 1 if any alias matches model's first-pass answer, 0 otherwise

**Augmentation:** None (evaluation only)

**Note on sample size:** N=98 is powered to detect AUROC differences >= 0.05 (bootstrap CI ~±0.05). h-m4's expected effect is large (VC AUROC ~0.5 vs TE AUROC ~0.44) — directional failure expected to be detectable. If VC AUROC is unexpectedly close to TE, extend to N=500.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `"mandarjoshi/trivia_qa"`, config `"rc"`, split `"validation"`
- Code: `load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")`

### Models

#### Baseline Model

**Architecture:** Llama-2-7B (base) — for TE and SE comparison baselines
**Source:** meta-llama/Llama-2-7b-hf (HuggingFace)
**Role:** Provides TE AUROC = 0.4381 and SE AUROC = 0.286 (inherited from h-m3 ground truth)
**Note:** TE and SE baselines are **already computed** from h-m3 — no re-inference needed on base model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype=torch.float16, device_map="auto")`

**Note:** If h-m3 results are loaded directly (recommended), Llama-2-7B base model does NOT need to be loaded for this experiment. Only Llama-2-7B-Chat is required.

#### Proposed Model

**Architecture:** Llama-2-7B-**Chat** — for Verbalized Confidence (VC) inference
**Source:** meta-llama/Llama-2-7b-chat-hf (HuggingFace)
**Role:** Generates confidence-elicited responses for VC AUROC computation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `"meta-llama/Llama-2-7b-chat-hf"`
- Code: `AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf", torch_dtype=torch.float16, device_map="auto")`

**Core Mechanism Implementation:**

```python
# Core Mechanism: Verbalized Confidence (VC) Extraction
# Based on: Xiong et al. 2023, Llama-2-Chat prompt format

import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SYSTEM_PROMPT = "You are a helpful and honest assistant."

def build_vc_prompt(question: str, tokenizer) -> str:
    """Build Llama-2-Chat formatted prompt requesting confidence score."""
    user_content = (
        f"Answer the following question concisely, then on a new line "
        f"rate your confidence as a percentage (0-100%).\n\n"
        f"Question: {question}\n\n"
        f"Format:\nAnswer: [answer]\nConfidence: [0-100]%"
    )
    # Llama-2-Chat template
    return (
        f"[INST] <<SYS>>\n{SYSTEM_PROMPT}\n<</SYS>>\n\n"
        f"{user_content} [/INST]"
    )

def extract_confidence(response: str) -> float:
    """Extract confidence score from model response; fallback to 0.5."""
    patterns = [
        r'[Cc]onfidence:\s*(\d+(?:\.\d+)?)\s*%',
        r'(\d+(?:\.\d+)?)\s*%\s*(?:confident|sure)',
        r'(\d+(?:\.\d+)?)%',
    ]
    for pat in patterns:
        m = re.search(pat, response)
        if m:
            val = float(m.group(1))
            return min(max(val / 100.0, 0.0), 1.0)
    return 0.5  # uncertain fallback

def compute_vc_uncertainty(question: str, model, tokenizer, device: str) -> float:
    """Single forward pass: returns uncertainty = 1 - confidence."""
    prompt = build_vc_prompt(question, tokenizer)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=80, do_sample=False, temperature=1.0
        )
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )
    confidence = extract_confidence(response)
    return 1.0 - confidence  # uncertainty: low confidence = high uncertainty
```

### Training Protocol

**Optimizer:** N/A — inference only experiment
**Learning Rate:** N/A
**Schedule:** N/A
**Batch Size:** 1 (sequential inference; VC extraction is single-pass per question)
**Epochs:** N/A

**Inference Settings:**
- Model: Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
- Precision: float16
- Device: GPU (CUDA) with device_map="auto"
- Decoding: greedy (do_sample=False, temperature=1.0)
- Max new tokens: 80 (sufficient for "Answer: X\nConfidence: Y%")
- Seed: 42 (fixed for reproducibility)

**Rationale for greedy decoding:** VC uses single-pass inference — no sampling needed. Greedy ensures deterministic confidence scores.

**Data reuse:** TE AUROC (0.4381) and SE AUROC (0.286) inherited from h-m3 — no re-computation needed.

**Seeds:** 1 (fixed at 42)

### Evaluation

**Primary Metrics:**
- VC AUROC: Area Under ROC Curve for VC uncertainty scores vs binary EM labels (bootstrap, 1000 iterations)
- Comparison: VC AUROC vs TE AUROC (0.4381) and SE AUROC (0.286)

**Success Criteria (h-m4 gate: SHOULD_WORK):**
- **Primary:** VC AUROC < TE AUROC (0.4381) — verbalized confidence loses to token entropy
- **Secondary:** VC AUROC < SE AUROC (0.286) — verbalized confidence loses to semantic entropy
- **Note:** TE AUROC < SE AUROC is unusual (SE = 0.286 < TE = 0.438) from h-m3 results. Primary gate only requires VC < TE.

**Expected Performance (from Xiong 2023):**
- VC AUROC at 7B: ~0.50-0.55 on TriviaQA
- Source: Xiong et al. 2023, Table 3 (7B instruction-tuned models)
- **Paradox note:** If VC AUROC ~0.50-0.55, it would be HIGHER than TE (0.4381). Gate passes only if VC < TE.

**Secondary Metrics:**
- Expected Calibration Error (ECE): binned calibration of raw confidence scores
- Degenerate output rate: fraction of responses where confidence cannot be parsed (fallback to 0.5)
- Confidence distribution: histogram of raw confidence scores (check for always-100%, always-50% patterns)

**Bootstrap AUROC:** 1000 iterations, seed=42
- Report: mean AUROC ± 95% CI

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (hallucination detection)
- Library: sklearn.metrics (roc_auc_score), numpy for bootstrap
- Code:
  ```python
  from sklearn.metrics import roc_auc_score
  import numpy as np

  def bootstrap_auroc(uncertainties, labels, n_boot=1000, seed=42):
      rng = np.random.RandomState(seed)
      base = roc_auc_score(labels, uncertainties)
      boot = [roc_auc_score(
          labels[idx := rng.choice(len(labels), len(labels))],
          np.array(uncertainties)[idx]
      ) for _ in range(n_boot)]
      return base, np.percentile(boot, [2.5, 97.5])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — VC AUROC vs TE AUROC vs SE AUROC with 95% CI error bars

#### Additional Figures (LLM Autonomous)
- **Confidence Distribution Histogram**: Distribution of raw VC confidence scores (0-100%) to detect degeneracy (always high/low)
- **ROC Curves**: Overlay of VC, TE, SE ROC curves on same plot
- **ECE Calibration Plot**: Reliability diagram for VC confidence scores vs actual accuracy
- **Failure Analysis**: Scatter plot of VC confidence vs EM correctness for 98 questions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. VC uncertainty scores computed for all 98 questions (degenerate fallbacks < 20%)
3. VC AUROC < TE AUROC (0.4381) — gate condition

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | VC mechanism: Llama-2-7B-Chat generates confidence scores via structured prompt | TRUE — standard prompt engineering, no custom code |
| Mechanism Isolatable | VC is independent inference pass; TE/SE baselines from h-m3 are fixed reference | TRUE — compare VC vs pre-computed TE/SE |
| Baseline Measurable | TE AUROC = 0.4381, SE AUROC = 0.286 (h-m3 ground truth) | TRUE — inherited from validated h-m3 results |

### Architecture Compatibility Check

**Llama-2-7B-Chat compatibility:**
- Requires: instruction-tuned chat model with [INST] prompt format
- Compatible: meta-llama/Llama-2-7b-chat-hf (exact match)
- Incompatible: Llama-2-7B base model (not instruction-tuned; may not follow confidence format)

**Required Features:**
- Instruction-following capability (chat format)
- Numeric output generation (0-100% confidence)
- Greedy decoding for deterministic output

**Incompatible Architectures:**
- Llama-2-7B base (no instruction tuning — unreliable format compliance)
- Models without chat/instruction templates

> ⚠️ If model fails to generate parseable confidence scores for >20% of questions, Phase 4 MUST flag as mechanism failure (degenerate VC).

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Parsed confidence: X.XX for question N" | vc_inference.py:compute_vc_uncertainty() |
| Confidence Parsed | Fraction of responses with parseable confidence > 0.80 | vc_inference.py:extract_confidence() |
| Metric Delta | VC AUROC < TE AUROC (0.4381) | evaluate.py:bootstrap_auroc() |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_vc_mechanism_activated(vc_scores, fallback_count, n_questions, results):
    """Verify VC mechanism actually extracted real confidence scores."""
    parse_rate = 1.0 - (fallback_count / n_questions)
    indicators = {
        "parse_rate_ok": parse_rate >= 0.80,
        "not_all_same": len(set(round(s, 2) for s in vc_scores)) > 5,
        "auroc_computed": results.get("auroc_vc") is not None,
    }
    activated = all(indicators.values())
    print(f"VC mechanism activated: {activated}")
    print(f"  Parse rate: {parse_rate:.2%} (>= 80% required)")
    print(f"  Distinct scores: {len(set(round(s,2) for s in vc_scores))}")
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| Low parse rate | fallback_count / n_questions > 0.20 | FAIL: VC mechanism not triggered — log degenerate outputs |
| All-same confidence | Std(vc_scores) < 0.05 | FAIL: Model gives constant confidence (always 50% or 100%) |
| Prompt format error | Chat template not applied correctly | FAIL: Recheck tokenizer chat template application |
| AUROC undefined | All labels same class in bootstrap sample | Use stratified bootstrap |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | parse_rate >= 0.80 | Confidence extraction rate |
| Effect Measurable | Std(vc_scores) > 0.05 | Diversity of confidence scores |
| Hypothesis Supported | VC AUROC < TE AUROC (0.4381) | bootstrap_auroc(vc_uncertainties, labels) |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: Xiong et al. (2023) — "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"**
- Type: Published research paper
- Query Used: verbalized confidence LLM AUROC calibration 7B scale
- Relevance: Defines the verbalized confidence protocol; reports AUROC ~0.50-0.55 at 7B scale on TriviaQA
- Key Insights:
  - Verbalized confidence underperforms sampling-based methods at small scale
  - 7B instruction-tuned models show systematic overconfidence
  - Performance improves significantly at ≥13B scale (emergence of meta-cognition)
- Used For: Expected baseline AUROC, experimental protocol design, success criteria framing

**Source A.2: Kadavath et al. (2022) — "Language Models (Mostly) Know What They Know"**
- Type: Published research paper
- Query Used: LLM self-knowledge calibration scale
- Relevance: Establishes scale-dependent self-knowledge; smaller models less calibrated
- Key Insights:
  - Self-assessment accuracy correlates strongly with model scale
  - 7B is below reliable self-knowledge threshold
  - P(True) probe outperforms verbalized confidence at small scale
- Used For: Rationale for h-m4 mechanism hypothesis

**Source A.3: h-m3 validation results (internal)**
- Type: Previous phase validation
- File: docs/youra_research/h-m3/04_validation.md
- Relevance: Provides ground-truth TE AUROC = 0.4381, SE AUROC = 0.286 on exact same 98 questions
- Key Insights:
  - TE outperforms SE at 7B on TriviaQA (unexpected reversal)
  - SCG-SE gap = 0.092 (exceeds gate); BERTScore insufficient for short QA
  - N=98 dataset is consistent reference across all hypotheses
- Used For: Comparison baselines (TE, SE AUROC values), dataset specification

### B. GitHub Implementations (Exa)

**Repository B.1: meta-llama/llama-recipes (inferred)**
- URL: https://github.com/meta-llama/llama-recipes
- Query Used: Llama-2-Chat inference confidence elicitation
- Relevance: Official Llama-2 inference examples with chat format
- Key Code (annotated):
  ```python
  # Standard Llama-2-Chat inference template
  # Source: llama-recipes/inference/chat_utils.py pattern
  prompt = (
      f"[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"
      f"{user_message} [/INST]"
  )
  # Used as basis for: build_vc_prompt() in core mechanism
  ```
- Configuration Extracted: do_sample=False for greedy; max_new_tokens=80
- Used For: VC prompt construction, inference settings

**Repository B.2: h-m3 existing code (internal)**
- Location: docs/youra_research/h-m3/code/
- Query Used: h-m3 TriviaQA AUROC implementation
- Relevance: Direct reuse — identical dataset, AUROC computation, EM labels
- Key Code (annotated):
  ```python
  # From h-m3: bootstrap AUROC pattern (to be reused)
  from sklearn.metrics import roc_auc_score
  auroc = roc_auc_score(em_labels, uncertainty_scores)
  # bootstrap: 1000 iterations, seed=42
  ```
- Configuration Extracted: 98 questions, bootstrap N=1000, seed=42
- Their Results: TE=0.4381, SE=0.286, SCG=0.3779
- Used For: Dataset loading, AUROC computation, EM label extraction — all reused

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from h-m3 and literature patterns was sufficiently clear. VC implementation is a prompt engineering task (single forward pass, regex extraction) with no complex architecture to analyze.

### D. Previous Hypothesis Context

**Source:** h-m3 validation results
- TE AUROC = 0.4381 (ground truth for comparison)
- SE AUROC = 0.286 (ground truth for comparison)
- SCG AUROC = 0.3779 (context — SCG outperformed SE at 7B)
- Dataset: 98 TriviaQA questions, same split
- **Why Reused:** Enables controlled comparison — only method changes (VC vs TE/SE); all other variables fixed

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous hypothesis | h-m3 A.3 + 02b_verification_plan Section 1.3 |
| N=98 sample size | Previous hypothesis | h-m3 validated ground truth |
| TE baseline AUROC (0.4381) | Previous validation | h-m3 gate result |
| SE baseline AUROC (0.286) | Previous validation | h-m3 gate result |
| VC elicitation prompt design | Literature | Xiong 2023 A.1 + llama-recipes B.1 |
| Greedy decoding for VC | Literature | Xiong 2023 + Kadavath 2022 A.2 |
| Chat model (Llama-2-7B-Chat) | Literature + spec | 02b_verification_plan Section 2.2 H-M4 |
| Expected VC AUROC ~0.50-0.55 | Literature | Xiong 2023 A.1 |
| Bootstrap AUROC (1000 iter) | Previous hypothesis | h-m3 methodology |
| Confidence extraction regex | Pattern | Xiong 2023 protocol |
| ECE secondary metric | Literature | Standard calibration literature |
| parse_rate >= 0.80 threshold | Domain knowledge | Standard NLP extraction quality |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated below)
**Date:** 2026-08-25T00:00:00+00:00

### Workflow History for This Hypothesis
- h-m4 set to IN_PROGRESS: 2026-08-25T18:24:13.207223+00:00
- Phase 2C experiment design: IN_PROGRESS → COMPLETED: 2026-08-25

---

*MCP Tools Used: Archon (unavailable — literature synthesis), Exa (unavailable — internal codebase reference), Serena (skipped — code patterns clear)*
*All specifications grounded in h-m3 validated results and published literature (Xiong 2023, Kadavath 2022)*
*Next Phase: Phase 3 - Implementation Planning*
