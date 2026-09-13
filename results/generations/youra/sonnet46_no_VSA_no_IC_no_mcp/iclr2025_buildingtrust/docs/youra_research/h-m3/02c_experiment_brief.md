# Experiment Design: h-m3

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under the conditions confirmed in H-M1 and H-M2, if ΔECE = ECE(adversarial) − ECE(clean) is computed for all label-preserved (model, task) cells, then ΔECE > 0.05 for ≥60% of model × task combinations and mean ΔECE > 0 across all combinations.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Tests whether the confidence-accuracy gap confirmed in H-M2 manifests as measurable elevated ΔECE. This is the core empirical claim of H-DeltaECE-v1.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (VALIDATED, MUST_WORK ✅), h-m2 (COMPLETED, SHOULD_WORK EXPLORE ⚠️)
**Gate Status:** SHOULD_WORK — h-m2 soft fail (EXPLORE) recorded as limitation; proceeding per Phase 2B failure response policy

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m1, h-m2

### Gate Condition
SHOULD_WORK: ΔECE > 0.05 for ≥60% of model × task combinations AND mean ΔECE > 0 (one-sample t-test p < 0.05).
Failure response: EXPLORE — report as negative result; check calibration reliability diagrams; investigate whether models' uncertainty mechanism is adaptive.

---

## Continuation Context

**Continuation from h-m2 (EXPLORE — soft fail):**

| Finding | Value | Implication for h-m3 |
|---------|-------|----------------------|
| mean ΔAcc | −0.0105 | Accuracy drops exist; ECE will capture aggregate miscalibration even without large per-cell drops |
| mean conf_wrong_adv | 0.6162 | Confidence on wrong predictions below 0.70 gate — but still above 0.50 random baseline |
| Gate pass rate | 0/5 cells | Dual-gate too strict; ΔECE may still be positive even with moderate gap |
| ANLI difficulty gradient | R3 ≤ R1 | Confirmed — calibration expected to degrade more on harder rounds |
| Data scope | Llama-2-7b-hf only | Single-model scope from H-E1; h-m3 will use same scope |

**Key insight:** ECE = Σ_b |acc(b) − conf(b)| × |b|/n. Even small confidence-accuracy gaps, when systematic across bins, produce measurable ECE increases. H-M2 confirmed gaps exist (conf ~0.62, acc declining) — H-M3 tests whether these register as ΔECE > 0.05.

### Previous Hypothesis Results
- h-m1: ≥80% label preservation confirmed on AdvGLUE + ANLI ✅ (valid ΔECE signal foundation)
- h-m2: Soft fail EXPLORE — accuracy drops and confidence gaps present but below dual-gate thresholds

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon MCP unavailable in this session — WebSearch used as fallback per MCP Error Retry Protocol.

**Query 1: ECE computation for LLM adversarial benchmarks**
- Result: ECE (Guo et al. 2017) standard is 15-bin equal-width, weighted by bin size: ECE = Σ_b (|b|/n)|acc(b) − conf(b)|
- Clean-split ECE for open-weight LLMs: ~0.05–0.15 (Kadavath 2022 on TriviaQA/MMLU; Xiong 2023 on MMLU)
- Adversarial perturbation increases ECE: confirmed for image models (Guo 2017); for LLMs on adversarial NLP — unmeasured (PROVE_NEW claim)
- Key insight: ECE requires both confidence (max softmax over answer tokens) and correctness label per example

**Query 2: Implementation challenges for logit-based ECE on LLMs**
- lm-evaluation-harness (EleutherAI/lm-evaluation-harness) supports logit extraction for MC tasks via `loglikelihood` task type
- Continuation-sum method: sum log-probs over all tokens of each choice → softmax → confidence distribution
- Known pitfall: tokenization of multi-token answers (e.g., "entailment") may yield different token counts per model — must normalize per answer option
- ECE binning: 15 equal-width bins in [0, 1] is standard; adaptive binning (equal-mass) reduces variance but changes comparability

**Query 3: Calibration reliability diagrams for LLMs**
- NetCal Python library (`netcal` package): `netcal.metrics.ECE`, `netcal.presentation.ReliabilityDiagram`
- Alternative: manual implementation with numpy — standard and well-understood
- CCPS (2025, arXiv 2505.21772): reduces ECE ~55% via perturbation probing — confirms ECE is valid signal for LLMs

### Archon Code Examples

**Status:** Archon MCP unavailable — pattern from published implementations used.

**ECE Computation Pattern (from Guo 2017 / netcal):**
```python
# Standard 15-bin ECE computation
def compute_ece(confidences, accuracies, n_bins=15):
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences >= bin_boundaries[i]) & (confidences < bin_boundaries[i+1])
        if mask.sum() > 0:
            bin_acc = accuracies[mask].mean()
            bin_conf = confidences[mask].mean()
            ece += (mask.sum() / len(confidences)) * abs(bin_acc - bin_conf)
    return ece
```

### Exa GitHub Implementations

**Status:** Exa MCP unavailable — WebSearch used as fallback.

**Repository 1: EleutherAI/lm-evaluation-harness** (⭐ ~7000+)
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Relevance: Standard framework for LLM evaluation with logit extraction support
- Key capability: `loglikelihood` task type returns log-probabilities per answer option; can be extended to compute ECE
- AdvGLUE/ANLI tasks: available as standard tasks in harness
- Architecture: Task configs in YAML; model evaluation via `lm_eval.api`
- Serena needed: No — existing H-E1 codebase already uses this infrastructure

**Repository 2: LLM-Calibration-Mechanism (Exploration-Lab)**
- URL: https://github.com/Exploration-Lab/LLM-Calibration-Mechanism
- Relevance: Computes ECE and MCE from saved logits/activations; validates calibration metrics for open-weight LLMs
- Key insight: ECE computation from saved logits is separable from evaluation — load results, compute ECE offline

**Repository 3: EFS-OpenSource/calibration-framework (NetCal)**
- URL: https://github.com/EFS-OpenSource/calibration-framework
- Relevance: Production ECE library with `ReliabilityDiagram` class
- Install: `pip install netcal`
- Code: `from netcal.metrics import ECE; ece = ECE(15).measure(confidences, labels)`

**Serena Analysis Needed:** No — mechanism is measurement-based (ECE formula application), not a complex neural architecture.

### 🎯 Implementation Priority Assessment

**This is a measurement experiment, not a paper reproduction.** No single "official author implementation" — standard ECE formula from Guo (2017) is the ground truth.

**Recommended Implementation Path:**
- Primary: Custom implementation using existing H-E1 logit extraction pipeline + numpy ECE computation
- Fallback: NetCal library (`pip install netcal`) for ECE + reliability diagrams
- Justification: H-E1 already extracts logits per (model, task, split) cell; h-m3 adds ECE computation layer on top of existing results. Reusing H-E1 infrastructure enables controlled comparison.

### Code Analysis (Serena MCP)

**Serena Analysis:** Not performed — experiment is a measurement layer on top of existing lm-evaluation-harness outputs. No complex novel architecture to analyze. H-E1 codebase already analyzed in prior phases.

---

## Experiment Specification

### Dataset

**Dataset 1 (Primary Adversarial): AdvGLUE**
- Source: HuggingFace — `AI-Secure/adv_glue`
- Tasks: SST-2 (sentiment), QQP (duplicate detection), MNLI/RTE/QNLI (NLI)
- Split used: Test split (human-verified adversarial examples)
- Label preservation: ≥80% confirmed (H-M1)
- Size: ~13,167 examples across 5 tasks; test split varies by task (~500–3,000 per task)
- Type: standard (real adversarial benchmark)

**Dataset 2 (Primary Adversarial): ANLI**
- Source: HuggingFace — `facebook/anli`
- Rounds: R1 (1,000 test), R2 (1,000 test), R3 (1,200 test)
- Tasks: NLI (entailment/neutral/contradiction, 3-way)
- Label preservation: Confirmed in H-M1 (model-in-the-loop human-validated)
- Total: 3,200 test examples across R1/R2/R3
- Type: standard (real adversarial benchmark)

**Clean Counterpart Datasets:**
- GLUE (for AdvGLUE ΔECE baseline): `nyu-mll/glue` — same tasks as AdvGLUE
- MultiNLI (for ANLI ΔECE baseline): `nyu-mll/multi_nli` — same NLI task format as ANLI

**Scope note (continuation from H-E1/H-M1/H-M2):** Single model (Llama-2-7b-hf) due to H-E1 data scope. Full 4-model grid (Llama-2-7b-hf, Llama-2-7b-chat-hf, Llama-2-13b-chat-hf, Mistral-7B-Instruct-v0.1) is the ideal from PRD but constrained by available H-E1 outputs.

**Synthetic data check:** PASSED — all datasets are real, established NLP benchmarks.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `AI-Secure/adv_glue`, `facebook/anli`, `nyu-mll/glue`, `nyu-mll/multi_nli`
- Code:
```python
from datasets import load_dataset
adv_glue = load_dataset("AI-Secure/adv_glue", "adv_sst2")  # repeat per task
anli = load_dataset("facebook/anli")  # R1/R2/R3 included
glue_clean = load_dataset("nyu-mll/glue", "sst2")  # clean counterpart
mnli_clean = load_dataset("nyu-mll/multi_nli")  # clean NLI counterpart
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7b-hf (decoder-only transformer, 7B parameters)
- Source: `meta-llama/Llama-2-7b-hf` (HuggingFace)
- Type: open-weight decoder-only LLM
- Continuation from H-E1/H-M1/H-M2: Same model, same evaluation infrastructure
- Role: "Baseline" = model evaluated on clean splits; "Proposed" = same model on adversarial splits
- Note: No architecture modification — this experiment measures ECE on clean vs. adversarial inputs using the same model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", torch_dtype=torch.float16, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Same model — ΔECE experiment contrasts INPUTS (clean vs. adversarial), not architectures.

**Core Mechanism Implementation:**

```python
# Core Mechanism: ΔECE Computation (Confidence-Accuracy Gap → ECE)
# Based on: Guo et al. 2017 (arXiv 1706.04599); lm-evaluation-harness logit extraction
# H-E1 infrastructure: logits already extracted per (model, task, split) cell

def compute_ece_from_logits(logits_per_example, labels, n_bins=15):
    """
    Args:
        logits_per_example: List[np.array] — shape (n_choices,) per example
        labels: np.array shape (N,) — ground truth indices
        n_bins: int — number of equal-width bins (Guo 2017: 15)
    Returns:
        ece: float, confidences: np.array, accuracies: np.array
    """
    # Step 1: Softmax over answer-token logits to get confidence
    confidences = np.array([softmax(lgt)[np.argmax(softmax(lgt))] for lgt in logits_per_example])
    predictions = np.array([np.argmax(softmax(lgt)) for lgt in logits_per_example])
    correct = (predictions == labels).astype(float)

    # Step 2: 15-bin ECE (Guo 2017 standard)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (confidences >= bin_boundaries[i]) & (confidences < bin_boundaries[i+1])
        if mask.sum() > 0:
            bin_acc = correct[mask].mean()
            bin_conf = confidences[mask].mean()
            ece += (mask.sum() / len(confidences)) * abs(bin_acc - bin_conf)

    return ece, confidences, correct

def compute_delta_ece(cell_results):
    """
    cell_results: dict with keys 'clean' and 'adversarial',
                  each containing logits_per_example + labels
    Returns ΔECE = ECE(adversarial) - ECE(clean)
    """
    ece_clean, _, _ = compute_ece_from_logits(**cell_results['clean'])
    ece_adv, _, _ = compute_ece_from_logits(**cell_results['adversarial'])
    return ece_adv - ece_clean, ece_clean, ece_adv
```

### Training Protocol

**Note:** This is a measurement experiment — no model training occurs. The protocol governs evaluation, ECE computation, and statistical testing.

**Evaluation Protocol (inheriting H-E1 infrastructure):**
- Framework: lm-evaluation-harness (EleutherAI, pinned to H-E1 version)
- Task type: `loglikelihood` — extracts log-probabilities per answer token sequence
- Prompt template: Same as H-E1/H-M1/H-M2 (fixed for controlled comparison)
- Batch size: 8 (GPU memory constrained; same as H-E1)
- Precision: float16 (same as H-E1)
- Device: CUDA (single GPU)
- Seed: 42 (fixed for reproducibility)

**ECE Computation:**
- Bins: 15 (equal-width, [0, 1]) — Guo 2017 standard
- Confidence: max softmax probability over answer-option logits per example
- Label: ground-truth answer index (label-preserved subset per H-M1 filter)

**Statistical Test:**
- One-sample t-test on ΔECE values across (model, task) cells
- H0: mean ΔECE ≤ 0
- Significance threshold: p < 0.05
- Note: With single-model scope (h-m2 limitation), "cells" = (model=Llama-2-7b-hf) × (tasks=AdvGLUE-tasks + ANLI-R1/R2/R3) = ~8 cells minimum

**Seeds:** 1 (fixed — evaluation is deterministic given fixed model weights and prompt)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Gate Threshold |
|--------|-----------|---------------|
| ΔECE per cell | ECE(adversarial) − ECE(clean) for each (model, task) pair | > 0.05 |
| Proportion cells with ΔECE > 0.05 | Count(ΔECE > 0.05) / total cells | ≥ 60% |
| Mean ΔECE | Average ΔECE across all cells | > 0 (p < 0.05) |
| ECE(clean) | Baseline calibration per cell | Expected: 0.05–0.15 (Kadavath 2022 sanity check) |
| ECE(adversarial) | Adversarial calibration per cell | Expected: > ECE(clean) if H-M3 holds |

**Secondary Metrics:**
- Calibration reliability diagrams: clean vs. adversarial overlay per representative (model, task) pair
- ΔECE sorted by task difficulty: expect ANLI-R3 > ANLI-R2 > ANLI-R1 (consistent with H-M2 difficulty gradient)
- Per-bin calibration gap: which confidence bins show largest miscalibration increase

**Success Criteria:**
- Primary: ≥60% of (model, task) cells show ΔECE > 0.05 AND mean ΔECE > 0 (p < 0.05, one-sample t-test)
- Secondary: Calibration reliability diagrams show visible miscalibration shift on adversarial splits
- Expected baseline ECE(clean): 0.05–0.15 (sanity check against Kadavath 2022)

**Failure response (gate not met):** EXPLORE — document as negative result; investigate whether ECE reduction mechanisms are adaptive; report calibration reliability diagrams regardless.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-class calibration measurement
- Library: `numpy` (custom ECE) or `netcal` (`pip install netcal`)
- Code:
```python
# Option A: custom (preferred — no dependency)
ece = compute_ece_from_logits(logits, labels, n_bins=15)
# Option B: netcal
from netcal.metrics import ECE
ece = ECE(15).measure(confidences, labels)
# Reliability diagram
from netcal.presentation import ReliabilityDiagram
ReliabilityDiagram(15).plot(confidences, labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **ΔECE Bar Chart**: ΔECE per (model, task) cell, horizontal line at 0.05 gate threshold, color-coded by pass/fail

#### Additional Figures (LLM Autonomous)
- Calibration reliability diagrams: clean vs. adversarial overlay for 2–3 representative (model, task) pairs
- ΔECE heatmap: rows = models, columns = tasks (for multi-model extension)
- Bin-level calibration gap: stacked bar showing per-bin |acc(b) − conf(b)| for clean and adversarial
- ECE(clean) vs ECE(adversarial) scatter plot: diagonal = no change line; points above = miscalibration increase

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Logit-based ECE computation infrastructure exists in H-E1 codebase | TRUE — H-E1 validated logit extraction for all cells |
| Mechanism Isolatable | ECE(clean) and ECE(adversarial) computed independently per cell | TRUE — clean and adversarial splits are separate dataset objects |
| Baseline Measurable | ECE(clean) can be computed without adversarial data | TRUE — GLUE/MultiNLI clean splits are independent |

### Architecture Compatibility Check

**Required:** Model with extractable logit distributions over discrete answer options (MC format).
- Llama-2-7b-hf: ✅ Compatible — decoder-only LM, lm-evaluation-harness extracts per-token log-probabilities for each answer choice
- This is purely a measurement protocol: no architectural change required

**Incompatible patterns:**
- Models without logit access (closed-source API-only)
- Tasks where answer space is open-ended (generation tasks — no fixed answer tokens)

> ⚠️ If logit extraction fails for any cell, that cell is EXCLUDED (not failed) — document coverage in results.

---

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"ECE computed: clean={ece_clean:.4f}, adv={ece_adv:.4f}, ΔECE={delta:.4f} for (model, task)"` | `evaluate.py:compute_delta_ece()` |
| Value Range | `0.0 ≤ ECE(clean) ≤ 0.5`; `ECE(adversarial) ≥ ECE(clean)` if H-M3 holds | `results/h-m3_ece_table.csv` |
| Metric Delta | ΔECE > 0 for majority of cells (even if below 0.05 gate) | `results/h-m3_delta_ece.json` |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results_dict):
    """Verify ECE computation completed and ΔECE signal is present."""
    indicators = {
        "ece_computed": all(
            r['ece_clean'] is not None and r['ece_adv'] is not None
            for r in results_dict.values()
        ),
        "baseline_in_range": all(
            0.0 <= r['ece_clean'] <= 0.5 for r in results_dict.values()
        ),
        "delta_positive_majority": (
            sum(1 for r in results_dict.values() if r['delta_ece'] > 0)
            >= len(results_dict) / 2
        )
    }
    activated = all(indicators.values())
    return activated, indicators
```

---

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| ECE not computed | `ece_clean is None` for any cell | FAIL: logit extraction issue — check H-E1 pipeline |
| ECE out of range | `ECE < 0` or `ECE > 1` | FAIL: implementation error — check softmax normalization |
| ΔECE uniformly ≤ 0 | All cells show ΔECE ≤ 0 | EXPLORE: adversarial perturbation does not increase miscalibration — report as antithesis supported |
| Clean ECE outside Kadavath range | Clean ECE > 0.25 for all cells | FLAG: possible logit extraction artifact — cross-check with verbal elicitation |

---

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| ECE Computed | All cells have valid ECE values | `verify_mechanism_activated()` returns True |
| Effect Direction | mean ΔECE > 0 | One-sample t-test H0: mean ≤ 0 |
| Hypothesis Supported | ≥60% cells ΔECE > 0.05 AND p < 0.05 | Gate pass: SHOULD_WORK satisfied |

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources (WebSearch fallback — Archon MCP unavailable)

**Source A.1: Guo et al. 2017 — "On Calibration of Modern Neural Networks"**
- arXiv: 1706.04599
- Key insight: 15-bin ECE is the standard; temperature scaling is the primary calibration fix
- Used for: ECE formula, bin count (15), success criterion derivation

**Source A.2: Kadavath et al. 2022 — "Language Models (Mostly) Know What They Know"**
- Context: LLM calibration on clean benchmarks (TriviaQA, MMLU, BIG-Bench)
- Key insight: Clean-split ECE for LLMs typically 0.05–0.15; verbal elicitation well-calibrated for Claude/GPT-3
- Used for: Expected ECE(clean) baseline range (sanity check)

**Source A.3: Wang et al. 2021 — "Adversarial GLUE: A Multi-Task Benchmark"**
- arXiv: 2111.02840; HuggingFace: AI-Secure/adv_glue
- Key insight: AdvGLUE covers 5 NLU tasks; human-verified label preservation; 15-30% accuracy drops for BERT-family models
- Used for: Dataset selection, label preservation rationale, task coverage

**Source A.4: Nie et al. 2020 — "Adversarial NLI: A New Benchmark for Natural Language Understanding"**
- HuggingFace: facebook/anli; GitHub: facebookresearch/anli
- Key insight: 3 rounds R1/R2/R3 with increasing difficulty; NLI 3-way; model-in-the-loop collection
- Used for: Dataset selection, difficulty gradient (R1 < R2 < R3) hypothesis

**Source A.5: Calibrating LLM Confidence by Probing Perturbed Representation Stability (CCPS, 2025)**
- arXiv: 2505.21772 (EMNLP 2025)
- Key insight: ECE reduction of ~55% via perturbation probing — confirms ECE is a valid, improvable signal for LLMs
- Used for: Confirming logit-based ECE is valid for LLMs (assumption A1 support)

**Source A.6: On the Robustness of Verbal Confidence of LLMs in Adversarial Attacks (2025)**
- arXiv: 2507.06489
- Key insight: Adversarial attacks increase ECE; high-performance models (GPT-4, Llama-3-70B) susceptible to miscalibration
- Used for: Confirming adversarial-calibration connection; related work positioning

### B. GitHub Implementations (WebSearch fallback — Exa MCP unavailable)

**Repository B.1: EleutherAI/lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Query used: "lm-evaluation-harness logit ECE calibration LLM"
- Architecture: YAML task configs; `loglikelihood` task type for MC evaluation
- Key capability: Returns log-probs per answer option — directly usable for ECE
- Used for: Evaluation infrastructure (inherited from H-E1); AdvGLUE/ANLI task support

**Repository B.2: Exploration-Lab/LLM-Calibration-Mechanism**
- URL: https://github.com/Exploration-Lab/LLM-Calibration-Mechanism
- Relevance: ECE/MCE from saved LLM activations; validates calibration for open-weight models on MMLU
- Key insight: ECE computation is separable from evaluation — compute offline from saved logits
- Used for: Validating offline ECE computation pattern; calibration direction analysis

**Repository B.3: EFS-OpenSource/calibration-framework (NetCal)**
- URL: https://github.com/EFS-OpenSource/calibration-framework
- Relevance: Production ECE library with `ReliabilityDiagram` class; supports 15-bin ECE
- Install: `pip install netcal`
- Used for: Optional fallback for ECE computation and reliability diagram generation

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — mechanism is standard ECE formula application (no complex novel architecture). H-E1 codebase uses lm-evaluation-harness; existing infrastructure is sufficient.

### D. Previous Hypothesis Context

**Source D.1: h-m2 (EXPLORE — COMPLETED)**
- Key results: mean ΔAcc = −0.0105; mean conf_wrong_adv = 0.6162; 0/5 cells pass dual gate
- Reused: Same model (Llama-2-7b-hf), same task set, same evaluation pipeline, same label-preserved subset
- Rationale: Controlled experiment — only the measurement (ECE vs. accuracy+confidence dual-gate) changes

**Source D.2: h-m1 (VALIDATED)**
- Key results: ≥80% label preservation confirmed; label-preserved subset identified
- Reused: Label-preserved subset filter (applied before ECE computation)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| AdvGLUE dataset selection | Phase 2A/2B + arXiv | A.3 (Wang 2021) |
| ANLI dataset selection | Phase 2A/2B + arXiv | A.4 (Nie 2020) |
| ECE formula (15-bin) | Research paper | A.1 (Guo 2017) |
| Clean ECE baseline range | Research paper | A.2 (Kadavath 2022) |
| Label-preserved subset | Previous hypothesis | D.2 (h-m1) |
| Model selection (Llama-2-7b-hf) | Previous hypothesis | D.1 (h-m2) |
| ECE computation infrastructure | GitHub | B.1 (lm-evaluation-harness) |
| Offline ECE from logits pattern | GitHub | B.2 (LLM-Calibration-Mechanism) |
| Reliability diagram | GitHub | B.3 (NetCal) |
| ΔECE validity for LLMs | Research paper | A.5 (CCPS 2025) |
| Adversarial-calibration connection | Research paper | A.6 (2507.06489) |
| Evaluation protocol | Previous hypothesis | D.1 (h-m2) |
| Statistical test design | Phase 2B spec | 02b_verification_plan.md H-M3 |

---

## Quality Validation

**Check 1: All hyperparameters justified?** ✅ — ECE bins (15) from Guo 2017; batch size/precision inherited from H-E1
**Check 2: Dataset choice justified?** ✅ — AdvGLUE + ANLI selected in Phase 2A, confirmed in h-m1/h-m2, same scope
**Check 3: Mechanism grounded in code?** ✅ — ECE formula from Guo 2017; pseudo-code matches standard implementation pattern from B.1/B.2
**Check 4: No unsupported assumptions?** ✅ — All claims cite prior hypotheses or published sources; h-m2 soft-fail limitation documented
**Check 5: Full traceability?** ✅ — Traceability matrix covers all specifications

**Overall: PASSED** (with noted limitation: single-model scope from H-E1; multi-model grid is ideal but constrained)

---

## State Information

**State File:** ABLATION MODE — state restated below
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- h-m3 set IN_PROGRESS: 2026-08-25T19:07:29
- Phase 2C experiment design: COMPLETED 2026-08-25

---

*MCP Tools Used: WebSearch (Archon/Exa unavailable — fallback per MCP Error Retry Protocol)*
*All specifications grounded in published research and prior hypothesis results (h-m1, h-m2)*
*Next Phase: Phase 3 - Implementation Planning*

---

## Sources (WebSearch)

- [On the Robustness of Verbal Confidence of LLMs in Adversarial Attacks](https://arxiv.org/pdf/2507.06489)
- [Calibrating LLM Confidence by Probing Perturbed Representation Stability](https://arxiv.org/abs/2505.21772)
- [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [Exploration-Lab/LLM-Calibration-Mechanism](https://github.com/Exploration-Lab/LLM-Calibration-Mechanism)
- [EFS-OpenSource/calibration-framework (NetCal)](https://github.com/EFS-OpenSource/calibration-framework)
- [AI-Secure/adv_glue · Hugging Face](https://huggingface.co/datasets/AI-Secure/adv_glue)
- [facebook/anli · Hugging Face](https://huggingface.co/datasets/facebook/anli)
- [Adversarial GLUE Benchmark](https://adversarialglue.github.io/)
- [Does Alignment Tuning Really Break LLMs' Internal Confidence?](https://arxiv.org/pdf/2409.00352)
- [Extreme Miscalibration and the Illusion of Adversarial Robustness](https://arxiv.org/pdf/2402.17509)
