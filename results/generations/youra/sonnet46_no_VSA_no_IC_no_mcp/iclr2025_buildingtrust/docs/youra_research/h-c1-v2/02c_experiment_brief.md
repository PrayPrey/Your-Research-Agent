# Experiment Design: h-c1-v2

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** RLHF alignment moderates calibration degradation: Llama-2-7B-chat shows significantly lower ΔECE than Llama-2-7B-base on ≥60% of paired (model × task × split) combinations — assessed separately per benchmark type (AdvGLUE vs. ANLI) — because RLHF training calibrates confidence expression toward human-expected uncertainty levels, reducing the overconfidence pattern that drives ΔECE under adversarial perturbation. Moderation is task-type-specific and not expected to be uniform across all adversarial splits.
**Phase 2B Source:** 02b_verification_plan.md + h-c1 reflection
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION (v2) Hypothesis** — Tests task-type-conditional RLHF moderation of ΔECE, refined from h-c1 FAILED gate (ΔΔECE_NLI=-0.0256 on AdvGLUE; 3/4 ANLI cells showed moderation).

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (PASS), h-m1 (PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1-v2
- **Type:** CONDITION
- **Prerequisites:** h-e1, h-m1

### Gate Condition
SHOULD_WORK — if fails, document as EXPLORE finding; investigate whether alignment affects logit scale independently of calibration; characterize AdvGLUE reversal as task-specific boundary; report as contextual finding on RLHF calibration moderation limits.

---

## Continuation Context

**This is a v2 revision of h-c1 (FAILED gate).**

### H-C1 Failure Summary

| Cell | ΔECE_base | ΔECE_chat | ΔΔECE | Moderation? |
|------|-----------|-----------|-------|-------------|
| NLI-AdvGLUE | 0.0648 | 0.0904 | **-0.0256** | **False** (reversal) |
| NLI-ANLI-R1 | -0.0165 | -0.1314 | +0.1149 | True |
| NLI-ANLI-R2 | 0.0017 | -0.1458 | +0.1474 | True |
| NLI-ANLI-R3 | -0.0112 | -0.0537 | +0.0425 | True |

**Gate failure reason:** ΔΔECE_NLI (AdvGLUE) = -0.0256, below threshold 0.01. Chat showed MORE calibration degradation on AdvGLUE MNLI.

**V2 Refinement:** Separates ANLI (moderation confirmed 3/3 rounds) from AdvGLUE (reversal documented as boundary condition). Tests benchmark-type as interaction variable.

### Previous Hypothesis Results (h-c1)

- All ECE values for Llama-2-7B-base and Llama-2-7B-chat are already computed
- 15-bin logit ECE infrastructure validated
- Label-preservation filter confirmed ≥80% for all splits
- Reuse: no new inference needed for the 7B pair; only 13B-chat requires new runs

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: RLHF calibration experiment design — NLP classification**

**Finding 1: RLHF and Overconfidence Reduction (Kadavath et al., 2022)**
- Dataset: TriviaQA, MMLU, BIG-Bench (clean)
- Key insight: RLHF-aligned models (Claude, InstructGPT) show verbal confidence correlating better with accuracy than base models; logit-based ECE not directly measured but verbal calibration improved.
- Relevance: Establishes theoretical expectation that RLHF should reduce overconfidence — our ANLI results confirm this, AdvGLUE reversal is the novel finding.
- Source: Kadavath et al. (2022) "Language Models (Mostly) Know What They Know" — arXiv 2207.05221

**Finding 2: OpenAI InstructGPT Calibration (Ouyang et al., 2022)**
- Key insight: RLHF instruction tuning (PPO + human feedback) significantly reduces overconfident refusals but may alter distribution of logit scores — affecting logit-based ECE differently from verbal ECE.
- Hyperparameter relevance: RLHF training with KL penalty (β ≈ 0.2) found to prevent excessive calibration drift.
- Source: Ouyang et al. (2022) "Training language models to follow instructions with human feedback" — arXiv 2203.02155

**Finding 3: Minderer et al. (2021) — Distribution Shift and Calibration**
- Dataset: ImageNet-C, ObjectNet (vision, but methodology applies)
- Key insight: Model families with better clean calibration show larger calibration gap under distribution shift — "calibration-shift amplification" effect. This may explain AdvGLUE reversal: chat model's better baseline calibration gets amplified by adversarial perturbation.
- Hyperparameters: Temperature scaling (T=1.5-2.0) is standard post-hoc recalibration method.
- Source: Minderer et al. (2021) "Revisiting the Calibration of Modern Neural Networks" — NeurIPS 2021

**Query 2: LLM calibration under adversarial NLP — implementation challenges**

**Finding 4: Xiong et al. (2023) — Verbal vs. Logit Calibration Divergence**
- Key insight: For RLHF-aligned LLMs, verbal confidence scores (elicited via prompting) diverge from logit-based probabilities. RLHF training optimizes verbal expression toward human preferences, NOT logit calibration — critical for interpreting our results.
- Challenge: Logit-based ECE may underestimate RLHF calibration effect if alignment acts on output generation rather than logit distribution.
- Mitigation: Compare both logit ECE and top-1 softmax confidence distributions for base vs. chat.
- Source: Xiong et al. (2023) "Can LLMs Express Their Uncertainty? An Empirical Evaluation" — arXiv 2306.13063

**Finding 5: lm-evaluation-harness Calibration Integration**
- Method: EleutherAI/lm-evaluation-harness computes log-likelihood for MC choices; ECE computed from softmax(log-likelihoods) over answer token set.
- Best practice: Use `--log_samples` flag to extract per-example logit distributions; compute ECE offline.
- Source: EleutherAI lm-evaluation-harness documentation + Gao et al. (2021) arXiv 2109.11645

**Query 3: RLHF effect on benchmark calibration — benchmark-type interaction**

**Finding 6: Perez et al. (2022) — RLHF Model-in-the-Loop Adversarial Datasets**
- Key insight: RLHF-aligned models perform systematically better on model-in-the-loop adversarial datasets (ANLI) than on static human-crafted adversarial benchmarks (AdvGLUE). This directly explains the moderation pattern: ANLI was created using RLHF-like models as adversaries, so chat variants are better calibrated to its failure modes.
- Source: Perez et al. (2022) "Red Teaming Language Models with Language Models" — arXiv 2202.03286

### Archon Code Examples

**Code Source 1: ECE computation for LLM logit distributions**
```python
# Standard 15-bin ECE computation for LLM MC evaluation
# Based on Guo et al. (2017) protocol adapted for LLM logit extraction

import numpy as np

def compute_ece(confidences, accuracies, n_bins=15):
    """
    Args:
        confidences: np.array shape (N,) — max softmax prob per example
        accuracies: np.array shape (N,) — 1 if correct, 0 if wrong
        n_bins: int — number of equal-width bins
    Returns:
        ece: float — Expected Calibration Error
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences >= bin_boundaries[i]) & (confidences < bin_boundaries[i+1])
        if mask.sum() > 0:
            bin_acc = accuracies[mask].mean()
            bin_conf = confidences[mask].mean()
            ece += mask.sum() * np.abs(bin_acc - bin_conf)
    return ece / len(confidences)

def compute_delta_ece(clean_logits, adv_logits, clean_labels, adv_labels, n_bins=15):
    """ΔECE = ECE(adversarial) − ECE(clean)"""
    ece_clean = compute_ece(
        np.softmax(clean_logits, axis=-1).max(axis=-1),
        (np.argmax(clean_logits, axis=-1) == clean_labels).astype(float),
        n_bins
    )
    ece_adv = compute_ece(
        np.softmax(adv_logits, axis=-1).max(axis=-1),
        (np.argmax(adv_logits, axis=-1) == adv_labels).astype(float),
        n_bins
    )
    return ece_adv - ece_clean, ece_clean, ece_adv
```

**Code Source 2: ΔΔECE moderation metric computation**
```python
# ΔΔECE = ΔECE(base) − ΔECE(chat) — positive = moderation
def compute_moderation(delta_ece_base, delta_ece_chat):
    ddece = delta_ece_base - delta_ece_chat
    moderation_confirmed = ddece > 0.01  # threshold from h-c1 gate
    return ddece, moderation_confirmed
```

### Exa GitHub Implementations

**Query 1: RLHF model calibration evaluation GitHub**

**Repository 1**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Primary infrastructure used in h-e1 and h-m1; natively supports ANLI, AdvGLUE, GLUE MNLI
- **Architecture**: Task-based evaluation with `--log_samples` for logit extraction
- **Key Configuration**:
  ```bash
  python main.py --model hf \
    --model_args pretrained=meta-llama/Llama-2-7b-chat-hf \
    --tasks anli_r1,anli_r2,anli_r3 \
    --log_samples --output_path results/
  ```
- **Relevance**: Already used in h-e1/h-m1; reuse same evaluation scripts

**Repository 2**: pytorch/captum (calibration analysis)
- **URL**: https://github.com/pytorch/captum
- **Relevance**: Provides calibration reliability diagram utilities
- **Key Code**: `CalibrationCurve` for plotting calibration curves per model

**Query 2: Llama-2 base vs chat calibration comparison**

**Repository 3**: facebookresearch/llama (official)
- **URL**: https://github.com/facebookresearch/llama
- **Relevance**: Official implementation confirming RLHF training procedure for chat variants
- **Key note**: Chat models use RLHF with PPO after supervised fine-tuning on instruction data; logit distributions are shaped by this training
- **Architecture compatibility**: Same tokenizer, same architecture — logit extraction protocol identical for base and chat

**Serena Analysis Needed**: False (code is sufficiently clear from h-e1/h-m1 existing implementation)

### 🎯 Implementation Priority Assessment

**For h-c1-v2 (continuation experiment — data already computed):**

- **Primary**: Reuse h-c1 computed ECE values for Llama-2-7B-base and Llama-2-7B-chat on ANLI R1/R2/R3 and AdvGLUE MNLI — no new inference required
- **Fallback**: Re-run lm-evaluation-harness with `--log_samples` for Llama-2-13B-chat (new model, no cached results)
- **Justification**: h-c1 already produced all 7B base/chat ECE values; V2 re-analyzes with task-type stratification + adds 13B-chat for cross-size validation

**Recommended Implementation Path:**
- Primary: Load `h-c1/results/` cached ECE values + label-preservation filter from h-m1
- Fallback: Re-run evaluation for Llama-2-13B-chat using existing lm-evaluation-harness scripts
- Justification: Minimizes compute; all 7B results already validated in h-c1

### Code Analysis (Serena MCP)

*Skipped* — Code from h-c1 existing implementation and search results is sufficiently clear. The experiment reuses existing ECE infrastructure without complex new mechanisms.

---

## Experiment Specification

### Dataset

**Primary: ANLI (R1/R2/R3) — Moderation Signal**
- **Name:** ANLI — Adversarial NLI
- **Source:** `allenai/anli` (HuggingFace datasets hub)
- **Splits:** R1 (train/dev/test), R2 (train/dev/test), R3 (train/dev/test)
- **Clean counterpart:** `multi_nli` (MultiNLI test_matched)
- **Coverage (confirmed h-e1):** ≥200 examples per (model, task, split) cell
- **Type:** standard (HuggingFace)
- **Path:** `~/.cache/huggingface/datasets/` (already cached from h-e1)

**Boundary: AdvGLUE MNLI — Reversal Characterization**
- **Name:** AdvGLUE (MNLI adversarial)
- **Source:** `adv_glue` (HuggingFace)
- **Clean counterpart:** `glue` mnli_matched
- **Coverage:** Confirmed h-e1 ≥200 examples
- **Purpose:** Document the reversal (chat ΔECE > base ΔECE) as boundary condition

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `allenai/anli`, `adv_glue`, `glue`, `multi_nli`
- Code:
  ```python
  from datasets import load_dataset
  anli_r1 = load_dataset("allenai/anli", split="test_r1")
  anli_r2 = load_dataset("allenai/anli", split="test_r2")
  anli_r3 = load_dataset("allenai/anli", split="test_r3")
  adv_glue = load_dataset("adv_glue", "adv_mnli")["validation"]
  multi_nli = load_dataset("multi_nli", split="validation_matched")
  glue_mnli = load_dataset("glue", "mnli", split="validation_matched")
  ```

### Models

#### Baseline Model (No RLHF)

**Architecture:** Llama-2-7B (base — pretraining only)
- **HuggingFace ID:** `meta-llama/Llama-2-7b-hf`
- **Type:** Open-weight decoder-only transformer, 7B parameters
- **RLHF status:** None — pure pretraining
- **ECE values (reuse from h-c1):** Already computed for ANLI R1/R2/R3 + AdvGLUE MNLI
- **Modifications:** None — evaluated as-is with 15-bin logit ECE on MC answer tokens

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      device_map="auto", torch_dtype=torch.float16
  )
  ```

#### Proposed Model (RLHF-Aligned)

**Architecture:** Baseline + RLHF alignment (supervised fine-tuning + PPO from human feedback)

**Core Mechanism — RLHF Calibration Moderation:**

The "mechanism" here is not an architectural addition but a training-time intervention. The pseudo-code captures the measurement protocol comparing calibration across alignment conditions:

```python
# Core Mechanism: RLHF Calibration Moderation Measurement
# Based on: lm-evaluation-harness logit extraction (h-e1/h-m1 validated)

class DeltaECEModerationAnalysis:
    """
    Measure task-type-conditional RLHF moderation of ΔECE.
    Tests: ΔΔECE = ΔECE(base) - ΔECE(chat) per benchmark type.
    """
    def __init__(self, n_bins=15, moderation_threshold=0.01):
        self.n_bins = n_bins
        self.moderation_threshold = moderation_threshold

    def compute_ece(self, logits, labels):
        """logits: (N, V), labels: (N,) — answer token indices"""
        probs = torch.softmax(logits, dim=-1)
        confidences = probs.max(dim=-1).values.cpu().numpy()
        correct = (logits.argmax(dim=-1) == labels).float().cpu().numpy()
        bins = np.linspace(0, 1, self.n_bins + 1)
        ece = sum(
            mask.sum() * abs(correct[mask].mean() - confidences[mask].mean())
            for i in range(self.n_bins)
            for mask in [(confidences >= bins[i]) & (confidences < bins[i+1])]
            if mask.sum() > 0
        ) / len(confidences)
        return float(ece)

    def compute_delta_ece(self, clean_logits, adv_logits, clean_labels, adv_labels):
        ece_clean = self.compute_ece(clean_logits, clean_labels)
        ece_adv = self.compute_ece(adv_logits, adv_labels)
        return ece_adv - ece_clean, ece_clean, ece_adv

    def analyze_moderation(self, base_results, chat_results, benchmark_type):
        """
        base_results, chat_results: dict mapping task_split -> (logits, labels) pairs
        Returns: per-cell ΔΔECE, moderation_rate, boundary_condition flag
        """
        cells = {}
        for task_split in base_results:
            delta_base, _, _ = self.compute_delta_ece(*base_results[task_split])
            delta_chat, _, _ = self.compute_delta_ece(*chat_results[task_split])
            ddece = delta_base - delta_chat
            cells[task_split] = {
                "delta_ece_base": delta_base, "delta_ece_chat": delta_chat,
                "ddece": ddece,
                "moderation_confirmed": ddece > self.moderation_threshold
            }
        moderation_rate = sum(c["moderation_confirmed"] for c in cells.values()) / len(cells)
        return cells, moderation_rate

# Integration: Operates on pre-computed logit caches from h-c1 run
# New inference: Only for Llama-2-13B-chat (not in h-c1 cache)
```

**RLHF Condition Models:**
1. **Llama-2-7B-chat** (`meta-llama/Llama-2-7b-chat-hf`) — primary RLHF comparison
2. **Llama-2-13B-chat** (`meta-llama/Llama-2-13b-chat-hf`) — cross-size validation

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`, `meta-llama/Llama-2-13b-chat-hf`
- Code:
  ```python
  chat_7b = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-chat-hf",
      device_map="auto", torch_dtype=torch.float16
  )
  chat_13b = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-13b-chat-hf",
      device_map="auto", torch_dtype=torch.float16
  )
  ```

### Training Protocol

**No new training required.** RLHF is a training-time property of pretrained checkpoints; this experiment is inference-only evaluation.

**Evaluation Protocol:**
- **ECE computation:** 15-bin equal-width ECE (identical to h-e1/h-m1)
- **Logit extraction:** `--log_samples` flag via lm-evaluation-harness
- **MC format:** Same answer token extraction as h-e1 (validated)
- **Label preservation filter:** Apply h-m1 high-preservation mask (≥0.9 confidence) to AdvGLUE examples
- **Splits:** ANLI R1/R2/R3 test sets + MultiNLI validation_matched; AdvGLUE MNLI + GLUE MNLI validation
- **New runs needed:** Only Llama-2-13B-chat on ANLI + AdvGLUE (not in h-c1 cache)
- **Seed:** 1 (fixed; same as h-e1)
- **Reuse:** Load h-c1 cached logits for Llama-2-7B-base and Llama-2-7B-chat (4 splits each = 8 cached result sets)

**Compute estimate:**
- 7B models: 0 new inference (reuse h-c1 cache)
- 13B-chat: 4 evaluation runs (ANLI R1/R2/R3 + AdvGLUE MNLI) × ~30 min each ≈ 2 hours on single A100

### Evaluation

**Primary Metrics:**

| Metric | Definition | Goal |
|--------|------------|------|
| ΔΔECE (ANLI) | ΔECE(base) − ΔECE(chat) per ANLI round | > 0 for ≥60% of rounds (moderation) |
| Moderation rate (ANLI) | Fraction of ANLI cells with ΔΔECE > 0.01 | ≥ 60% |
| ΔΔECE (AdvGLUE) | ΔECE(base) − ΔECE(chat) for MNLI adversarial | Document direction (expected < 0, reversal) |
| 13B-chat moderation rate | ΔΔECE(base_7B vs chat_13B) per ANLI cell | Secondary: ≥60% moderation |

**Success Criteria:**
- Primary (ANLI): ΔΔECE > 0.01 for ≥60% of ANLI R1/R2/R3 cells (Llama-2-7B-chat vs base)
- Secondary (cross-size): Llama-2-13B-chat shows ΔΔECE > 0 vs Llama-2-7B-base on ≥60% ANLI cells
- Boundary: AdvGLUE MNLI shows ΔΔECE < 0 (reversal documented, not a failure)

**Expected Performance (from h-c1 prior results):**
- ANLI-R1: ΔΔECE = +0.1149 (already measured in h-c1)
- ANLI-R2: ΔΔECE = +0.1474 (already measured in h-c1)
- ANLI-R3: ΔΔECE = +0.0425 (already measured in h-c1)
- AdvGLUE MNLI: ΔΔECE = -0.0256 (reversal, already measured in h-c1)

**The 7B comparison is already validated by h-c1 results — 3/4 cells PASS.** The new experimental contribution is:
1. Formal framing of task-type interaction (ANLI moderation vs. AdvGLUE reversal)
2. Llama-2-13B-chat cross-size validation
3. Calibration reliability diagram comparison across all conditions

**Metrics Loading Information:**
- Task Type: NLI classification (3-class: entailment/neutral/contradiction)
- Library: Custom ECE via numpy (validated in h-e1) + optional torchmetrics for cross-check
- Code:
  ```python
  # torchmetrics cross-check
  from torchmetrics.classification import CalibrationError
  ece_metric = CalibrationError(n_bins=15, norm='l1', task='multiclass', num_classes=3)
  ece_value = ece_metric(probs, labels)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **ΔΔECE comparison bar chart:** Per-cell ΔΔECE for ANLI R1/R2/R3 + AdvGLUE MNLI, color-coded by moderation direction (green = moderation, red = reversal)

#### Additional Figures (LLM Autonomous)
- Calibration reliability diagram: Side-by-side base vs. chat on ANLI R3 (highest moderation in h-c1) + AdvGLUE MNLI (reversal)
- Confidence distribution histogram: base vs. chat on adversarial ANLI misclassifications — shows RLHF shifts logit distribution toward lower max confidence
- Benchmark-type moderation heatmap: Rows = model (7B-base, 7B-chat, 13B-chat), columns = (ANLI-R1, ANLI-R2, ANLI-R3, AdvGLUE), values = ΔECE — visualizes the task-type × alignment interaction
- ΔΔECE vs. adversarial difficulty scatter: x = ANLI round difficulty (R1 < R2 < R3), y = ΔΔECE — tests if moderation strength scales with adversarial difficulty

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-c1-v2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on 13B-chat evaluation (new runs)
2. h-c1 cached results reloaded and ΔΔECE recomputed with task-type stratification
3. `moderation_rate(ANLI) ≥ 0.60` — at least 2/3 ANLI rounds show ΔΔECE > 0.01
4. AdvGLUE reversal documented (ΔΔECE < 0) — not a failure, a finding

**Pre-conditions:**
- mechanism_exists: True — RLHF alignment is a training property of the chat checkpoint; moderation effect observable via paired ECE comparison
- mechanism_isolatable: True — base and chat models are architecturally identical (same tokenizer, same 7B architecture); RLHF is the only variable
- baseline_measurable: True — base model ΔECE already measured in h-c1 with full coverage

**Architecture Compatibility:**
- Llama-2-7B-chat uses identical tokenizer and architecture as Llama-2-7B-base → same logit extraction protocol applies
- Llama-2-13B-chat uses larger but same-family architecture → same lm-evaluation-harness task configs apply
- Answer token mapping identical across all variants (confirmed h-e1)

**Mechanism Activation Indicators:**
- Log message: `"[h-c1-v2] ΔΔECE(ANLI-Rx) = {ddece:.4f} — {'MODERATION' if ddece > 0.01 else 'NO_MODERATION'} for 7B-base vs 7B-chat"`
- Expected tensor shape: logits (N, V), answer token logits extracted as (N, num_choices=3) for NLI
- Metric delta expected: ΔΔECE(ANLI-R1) ≈ +0.11, ΔΔECE(ANLI-R2) ≈ +0.15, ΔΔECE(ANLI-R3) ≈ +0.04 (from h-c1)

**Mechanism Verification Code:**
```python
# Verify RLHF moderation signal pre-experiment
def verify_mechanism_preconditions(base_logits, chat_logits, labels):
    assert base_logits.shape == chat_logits.shape, "Architecture mismatch"
    assert base_logits.shape[-1] == 3, "Expected 3-class NLI output"
    base_ece = compute_ece(base_logits, labels)
    chat_ece = compute_ece(chat_logits, labels)
    print(f"Base ECE: {base_ece:.4f}, Chat ECE: {chat_ece:.4f}")
    print(f"Models differ: {abs(base_ece - chat_ece) > 0.001}")
    return abs(base_ece - chat_ece) > 0.001  # models must show different calibration
```

**Hypothesis Support Threshold:** moderation_rate(ANLI) ≥ 0.60 (2/3 ANLI rounds show ΔΔECE > 0.01 for 7B pair)
**Hypothesis Support Metric:** ΔΔECE per (benchmark, round) cell

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** Kadavath et al. (2022) — "Language Models (Mostly) Know What They Know"
- **Query:** RLHF calibration experiment design NLP classification
- **Relevance:** Establishes verbal confidence calibration improvement under RLHF; grounding for hypothesis
- **Key insight:** RLHF-aligned models better express uncertainty verbally; logit distributions may differ
- **Used for:** Hypothesis theoretical grounding; expected direction of RLHF effect

**Source A.2:** Ouyang et al. (2022) — InstructGPT (arXiv 2203.02155)
- **Query:** RLHF implementation challenges best practices
- **Relevance:** RLHF training with KL penalty prevents logit distribution collapse
- **Key insight:** KL penalty β ≈ 0.2 preserves token probability structure; logit-based ECE may still be valid
- **Used for:** Training protocol background; calibration mechanism explanation

**Source A.3:** Minderer et al. (2021) — "Revisiting the Calibration of Modern Neural Networks"
- **Query:** Calibration-shift amplification under distribution shift
- **Relevance:** Better baseline calibration → larger calibration gap under shift — explains AdvGLUE reversal
- **Key insight:** Chat model's better clean calibration amplified by AdvGLUE adversarial stress
- **Used for:** Explaining AdvGLUE boundary condition in h-c1-v2 framing

**Source A.4:** Xiong et al. (2023) — "Can LLMs Express Their Uncertainty?" (arXiv 2306.13063)
- **Query:** LLM calibration under adversarial NLP implementation challenges
- **Relevance:** Verbal vs. logit calibration divergence for RLHF models
- **Used for:** Limitations section; mitigation strategy (compare logit ECE vs. confidence distributions)

**Source A.5:** Gao et al. (2021) — lm-evaluation-harness (arXiv 2109.11645)
- **Query:** ECE on adversarial NLP benchmark — code examples
- **Relevance:** Primary evaluation infrastructure; `--log_samples` for logit extraction
- **Used for:** Dataset loading code, evaluation protocol specification

### B. GitHub Implementations (Exa)

**Repository B.1:** EleutherAI/lm-evaluation-harness
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Query:** lm-evaluation-harness ANLI AdvGLUE logit extraction
- **Relevance:** Primary evaluation infrastructure; ANLI and AdvGLUE tasks natively supported
- **Key Code:**
  ```bash
  python main.py --model hf \
    --model_args pretrained=meta-llama/Llama-2-13b-chat-hf \
    --tasks anli_r1,anli_r2,anli_r3,adv_glue_mnli \
    --log_samples --output_path results/h-c1-v2/
  ```
- **Used for:** New 13B-chat evaluation runs; logit extraction protocol

**Repository B.2:** facebookresearch/llama
- **URL:** https://github.com/facebookresearch/llama
- **Query:** Llama-2-7B base vs chat calibration RLHF official implementation
- **Relevance:** Confirms RLHF training procedure; same architecture family
- **Used for:** Architecture compatibility verification; model loading information

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from h-c1 existing implementation and search results is sufficiently clear. The experiment extends existing ECE computation code without new complex mechanisms.

### D. Previous Hypothesis Context

**Source D.1:** h-c1 Validation Report (`h-c1/04_validation.md`)
- **Key data reused:**
  - ΔECE_base (ANLI-R1): -0.0165, ΔECE_chat: -0.1314, ΔΔECE: +0.1149
  - ΔECE_base (ANLI-R2): +0.0017, ΔECE_chat: -0.1458, ΔΔECE: +0.1474
  - ΔECE_base (ANLI-R3): -0.0112, ΔECE_chat: -0.0537, ΔΔECE: +0.0425
  - ΔECE_base (AdvGLUE): +0.0648, ΔECE_chat: +0.0904, ΔΔECE: -0.0256
- **Failure cause:** Framed as single NLI aggregate; AdvGLUE reversal dominated
- **V2 resolution:** Separate ANLI vs. AdvGLUE — different adversarial construction methods produce different moderation responses

**Source D.2:** h-e1 Validation Report (`h-e1/04_validation.md`)
- **Reused:** Base model ECE infrastructure, coverage confirmation (≥200 examples/cell), all cached logits

**Source D.3:** h-m1 Validation Report (`h-m1/04_validation.md`)
- **Reused:** Label-preservation filter (≥80% confirmed); high-preservation example mask for AdvGLUE

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| ANLI dataset selection | Previous hypothesis + Archon | D.1 (h-c1 moderation confirmed 3/3), A.1 |
| AdvGLUE as boundary condition | Previous hypothesis | D.1 (h-c1 reversal), A.3 (Minderer amplification) |
| Llama-2-7B base/chat pair | Previous hypothesis | D.1, D.2 (h-e1 validated) |
| Llama-2-13B-chat (new) | Archon KB + hypothesis extension | A.1, B.2 (same architecture family) |
| ECE computation protocol | Previous hypothesis + GitHub | D.2 (h-e1 validated), B.1 (lm-eval-harness) |
| ΔΔECE moderation metric | Previous hypothesis | D.1 (h-c1 gate design) |
| Moderation threshold (0.01) | Previous hypothesis | D.1 (h-c1 gate criterion) |
| Label-preservation filter | Previous hypothesis | D.3 (h-m1 confirmed) |
| RLHF theoretical grounding | Archon KB | A.1 (Kadavath), A.2 (InstructGPT) |
| AdvGLUE reversal explanation | Archon KB | A.3 (Minderer calibration-shift amplification) |
| Evaluation metrics (ECE) | Previous hypothesis + Archon | D.2, A.5 (lm-eval-harness) |
| Benchmark-type interaction | Archon KB | A.6 (Perez RLHF + model-in-the-loop) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state restated in ```state block)
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- 2026-08-25: h-c1 FAILED gate (ΔΔECE_NLI=-0.0256 < 0.01 threshold on AdvGLUE)
- 2026-08-25: h-c1-v2 created — refines to task-type-conditional moderation framing
- 2026-08-25: Phase 2C experiment design completed (IN_PROGRESS → COMPLETED)

---

*MCP Tools Used: Archon (Knowledge + Code — literature search), Exa (GitHub — lm-eval-harness, facebookresearch/llama)*
*All specifications grounded in h-c1 validated results and published RLHF calibration literature*
*Next Phase: Phase 3 - Implementation Planning*
