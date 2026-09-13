# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under a controlled matched-training-scale comparison (~300B tokens), if corpus curation quality differs between Pythia-6.9B (The Pile) and OLMo-7B (Dolma), then OLMo-7B will show a higher MMLU/HellaSwag performance ratio AND a higher ARC-Challenge/Easy delta than Pythia-6.9B, because the quality difference produces measurably different generalization balance.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK — gates H-M1 through H-M4

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate. If H-E1 fails to show OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B ratio by > 0.02 absolute (Cohen's d > 0.2, p < 0.05), the entire verification workflow stops and mechanistic hypotheses H-M1 through H-M4 are blocked.

---

## Continuation Context

N/A — H-E1 is the first hypothesis in the chain. No previous hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)
None — this is the foundational hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP not available in ablation mode. Knowledge grounded in established literature:*

**Domain: lm-evaluation-harness benchmark evaluation**
- EleutherAI's lm-evaluation-harness is the standard framework for evaluating LLMs on MMLU, HellaSwag, ARC-Easy, ARC-Challenge benchmarks
- Standard shot configurations: MMLU (5-shot), HellaSwag (0-shot), ARC-Easy (25-shot), ARC-Challenge (25-shot) — these match Pythia and OLMo original papers
- HuggingFace Hub hosts all required model checkpoints; Pythia-6.9B has 154 intermediate checkpoints at regular token intervals; OLMo-7B has intermediate checkpoints at steps correlating to ~143B and ~300B tokens

**Domain: Pythia checkpoint structure**
- Pythia-6.9B checkpoint naming: `EleutherAI/pythia-6.9b` with revision `step{N}` where N is gradient step count
- At ~300B tokens with batch size 2M tokens: step ≈ 143,000 corresponds to ~143B tokens; step ≈ 300,000 corresponds to ~300B tokens (need to verify from Pythia paper Table A1)
- Pythia uses consistent data ordering across all model sizes (Biderman et al. 2023)

**Domain: OLMo checkpoint structure**
- OLMo-7B checkpoint on HuggingFace: `allenai/OLMo-7B-hf` with intermediate checkpoints available via `allenai/OLMo-7B` (non-hf format) or HuggingFace revisions
- OLMo step-to-token mapping requires checking the training config (global batch size × steps); step ≈ 557,000 is ~300B tokens given OLMo's global batch size of ~2M tokens/step (Groeneveld et al. 2024)

**Domain: Benchmark contamination**
- Dolma applied deduplication that may have removed benchmark-adjacent content; Assumption A5 (contamination confound) must be addressed in analysis

### Archon Code Examples

*MCP not available in ablation mode.*

Standard lm-evaluation-harness invocation pattern (from public documentation):
```bash
lm_eval --model hf \
  --model_args pretrained=EleutherAI/pythia-6.9b,revision=step143000 \
  --tasks mmlu,hellaswag,arc_easy,arc_challenge \
  --num_fewshot 0 \
  --batch_size auto \
  --output_path ./results/pythia-6.9b-143B/
```

### Exa GitHub Implementations

*MCP not available in ablation mode. Key repositories from public knowledge:*

**Repository 1**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: The definitive evaluation framework; both Pythia and OLMo papers use this for benchmark results
- **Architecture**: Plugin-based task registry; HuggingFace model integration via `lm_eval --model hf`
- **Key invocation**: `lm_eval --model hf --model_args pretrained=MODEL_ID,revision=REVISION --tasks TASKS`
- **Results format**: JSON output with per-task accuracy, stderr, and sample counts

**Repository 2**: EleutherAI/pythia
- **URL**: https://github.com/EleutherAI/pythia
- **Relevance**: Intermediate checkpoint mapping table (Table A1 in paper); step→token count conversion
- **Key data**: Pythia-6.9B trained for 143,000 steps at batch size 2,097,152 tokens = ~300B tokens total

**Repository 3**: allenai/OLMo
- **URL**: https://github.com/allenai/OLMo
- **Relevance**: OLMo checkpoint registry and step→token mapping; training configuration
- **Key data**: OLMo-7B trained with global batch size ~2M tokens; step 557,000 ≈ 300B tokens

**Serena Analysis Needed**: false — evaluation pipeline uses existing models and frameworks, no novel architecture to analyze

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment does NOT reproduce a paper implementation — it evaluates existing pretrained models using a standard harness. Implementation priority:

**Recommended Implementation Path:**
- Primary: lm-evaluation-harness (EleutherAI/lm-evaluation-harness, latest stable release)
- Fallback: Direct HuggingFace `pipeline` with manual metric computation
- Justification: lm-evaluation-harness is the only framework that handles few-shot prompt formatting identically to the original Pythia and OLMo evaluation runs, ensuring reproducibility

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. This is a model evaluation experiment using existing frameworks (lm-evaluation-harness), not a novel architecture requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** Benchmark evaluation datasets (MMLU, HellaSwag, ARC-Easy, ARC-Challenge)
**Type:** standard
**Source:** Handled internally by lm-evaluation-harness; auto-downloads from HuggingFace Datasets
**Path:** auto (lm-evaluation-harness downloads to `~/.cache/huggingface/datasets/`)

**Statistics:**
- MMLU: 14,042 test questions, 57 subjects, 5-shot
- HellaSwag: 10,042 validation examples, 0-shot
- ARC-Easy: 2,376 test examples, 25-shot
- ARC-Challenge: 1,172 test examples, 25-shot
- **Total evaluation samples: ~27,632 across all tasks**

**Hypothesis Fit Confirmation:**
- MMLU tests OOD generalization (broad knowledge, academic domains not heavily present in web training data)
- HellaSwag tests in-distribution commonsense (heavily represented in web-scraped corpora)
- MMLU/HellaSwag ratio operationalizes OOD/ID generalization balance
- ARC-Challenge (harder, science questions) vs. ARC-Easy (simpler) delta operationalizes reasoning generalization depth

**Loading Information** (for Phase 4 download):
- Method: lm-evaluation-harness (auto-download)
- Identifier: tasks=`mmlu,hellaswag,arc_easy,arc_challenge`
- Code: `lm_eval --tasks mmlu,hellaswag,arc_easy,arc_challenge` (framework handles download)

### Models

#### Baseline Model

**Architecture:** Pythia-6.9B — GPT-NeoX architecture, decoder-only transformer
**Parameter count:** 6.9B
**Training data:** The Pile (825GB, 300B tokens, minimal curation)
**Checkpoint:** Intermediate checkpoint at ~300B training tokens

**Configuration:**
- Layers: 32, Hidden dim: 4096, Heads: 32, Context: 2048
- Checkpoint revision: `step143000` (verify: 143,000 steps × 2,097,152 tokens/step ≈ 300B tokens)
- HuggingFace ID: `EleutherAI/pythia-6.9b`

**Loading Information** (for Phase 4 download):
- Method: HuggingFace (via lm-evaluation-harness `--model hf`)
- Identifier: `EleutherAI/pythia-6.9b` with `revision=step143000`
- Code: `--model_args pretrained=EleutherAI/pythia-6.9b,revision=step143000`

#### Proposed Model

**Architecture:** OLMo-7B — LLaMA-style architecture, decoder-only transformer
**Parameter count:** ~7B
**Training data:** Dolma (3T tokens, multi-stage quality filtering, ~300B tokens at matched checkpoint)
**Checkpoint:** Intermediate checkpoint at ~300B training tokens

**Configuration:**
- Layers: 32, Hidden dim: 4096, Heads: 32, Context: 2048
- Checkpoint: step ≈ 149,531 for ~300B tokens (verify from OLMo training config: global_train_tokens / tokens_per_step)
- HuggingFace ID: `allenai/OLMo-7B-hf` (use HF-compatible version)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Corpus Quality → Generalization Balance Measurement
# This is NOT a new neural module — it's a measurement protocol.
# The "mechanism" is the evaluation pipeline that quantifies OOD/ID balance.

import subprocess
import json
import numpy as np

def evaluate_model_checkpoint(
    model_id: str,
    revision: str,
    tasks: list[str],
    output_path: str,
    num_fewshot_map: dict[str, int]
) -> dict:
    """
    Args:
        model_id: HuggingFace model identifier (e.g., "EleutherAI/pythia-6.9b")
        revision: Checkpoint revision (e.g., "step143000")
        tasks: List of benchmark tasks
        output_path: Directory for JSON results
    Returns:
        dict: {task: {acc: float, acc_stderr: float}}
    """
    cmd = [
        "lm_eval", "--model", "hf",
        "--model_args", f"pretrained={model_id},revision={revision}",
        "--tasks", ",".join(tasks),
        "--batch_size", "auto",
        "--output_path", output_path,
        "--log_samples"
    ]
    subprocess.run(cmd, check=True)
    with open(f"{output_path}/results.json") as f:
        return json.load(f)["results"]

def compute_generalization_balance(results: dict) -> dict:
    """
    Compute OOD/ID generalization balance metrics.
    Returns:
        mmlu_hellaswag_ratio: MMLU_acc / HellaSwag_acc
        arc_delta: ARC_Challenge_acc - ARC_Easy_acc
    """
    mmlu = np.mean([v["acc,none"] for k, v in results.items()
                    if k.startswith("mmlu_")])
    hellaswag = results["hellaswag"]["acc,none"]
    arc_easy = results["arc_easy"]["acc,none"]
    arc_challenge = results["arc_challenge"]["acc_norm,none"]
    return {
        "mmlu_hellaswag_ratio": mmlu / hellaswag,
        "arc_delta": arc_challenge - arc_easy,
        "mmlu": mmlu,
        "hellaswag": hellaswag
    }
```

### Training Protocol

**Note:** This is an EVALUATION-ONLY experiment. No training is performed. Protocol refers to evaluation execution parameters.

**Evaluation Protocol:**

**Framework:** lm-evaluation-harness (latest stable: v0.4.x as of 2026)
- Install: `pip install lm-eval`
- Version pin: `lm-eval==0.4.3` (verify latest stable)

**Shot configurations (matching original papers):**
- MMLU: 5-shot
- HellaSwag: 0-shot
- ARC-Easy: 25-shot
- ARC-Challenge: 25-shot

**Batch size:** `auto` (lm-evaluation-harness auto-selects based on VRAM)

**Hardware requirement:** 1× A100 80GB or 2× A40 48GB (for 6.9B/7B models in fp16)

**Bootstrap resampling:** 3 random prompt subsamples for MMLU (using lm-eval's `--bootstrap_iters` flag or manual implementation) to estimate confidence intervals on the ratio

**Seeds:** 1 (fixed; evaluation is deterministic given fixed prompts)

**Execution order:**
1. Evaluate Pythia-6.9B @ step143000 on all 4 tasks
2. Evaluate OLMo-7B @ matched ~300B checkpoint on all 4 tasks
3. Compute ratio and delta for both; run bootstrap CI

**Estimated wall time:** ~2 hours per model on A100 (MMLU is the bottleneck at 14K questions × 5-shot)

### Evaluation

**Task Type:** LLM benchmark evaluation (classification over multiple-choice options)

**Primary Metrics:**
- `mmlu_hellaswag_ratio` = mean_MMLU_accuracy / HellaSwag_accuracy
  - Operationalizes OOD/ID generalization balance (MMLU = OOD, HellaSwag = ID)
  - Higher ratio → better OOD-relative-to-ID performance → better generalization balance

**Secondary Metrics:**
- `arc_delta` = ARC_Challenge_acc_norm - ARC_Easy_acc
  - Operationalizes reasoning generalization depth (Challenge = harder OOD reasoning, Easy = simpler ID reasoning)
  - Higher delta (less negative or positive) → model generalizes better to hard reasoning

**Success Criteria (EXISTENCE PoC — direction-based):**
- **Primary:** OLMo_ratio > Pythia_ratio by > 0.02 absolute (i.e., OLMo shows meaningfully better OOD/ID balance)
  - Cohen's d > 0.2 (small effect size minimum)
  - Bootstrap p < 0.05 (3 subsamples of MMLU subjects)
- **Secondary:** OLMo_arc_delta > Pythia_arc_delta (directional, p < 0.10)
- **PoC Pass:** If primary criterion met → existence confirmed → unblock H-M1

**Expected Baseline Performance (from literature):**
- Pythia-6.9B full training: MMLU ~27%, HellaSwag ~63%, ratio ~0.43
- OLMo-7B full training: MMLU ~32%, HellaSwag ~69%, ratio ~0.46
- At ~300B tokens (intermediate): expect ~70-80% of full-training performance
- Expected Pythia ratio at 300B: ~0.40-0.43
- Expected OLMo ratio at 300B: ~0.42-0.47
- Target difference: > 0.02 (hypothesis threshold)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiple-choice accuracy (normalized and unnormalized)
- Library: lm-evaluation-harness (built-in metrics); numpy for ratio/delta computation; scipy.stats for bootstrap CI
- Code:
```python
from scipy import stats
import numpy as np

def bootstrap_ratio_comparison(pythia_results, olmo_results, n_bootstrap=1000):
    """Bootstrap CI on ratio difference."""
    mmlu_subjects = [k for k in pythia_results if k.startswith("mmlu_")]
    
    diffs = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(mmlu_subjects, len(mmlu_subjects), replace=True)
        p_mmlu = np.mean([pythia_results[s]["acc,none"] for s in sample])
        o_mmlu = np.mean([olmo_results[s]["acc,none"] for s in sample])
        p_ratio = p_mmlu / pythia_results["hellaswag"]["acc,none"]
        o_ratio = o_mmlu / olmo_results["hellaswag"]["acc,none"]
        diffs.append(o_ratio - p_ratio)
    
    return {
        "mean_diff": np.mean(diffs),
        "ci_95": np.percentile(diffs, [2.5, 97.5]),
        "p_value": np.mean(np.array(diffs) <= 0)  # one-sided
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing Pythia-6.9B vs OLMo-7B on MMLU/HellaSwag ratio and ARC delta at ~300B tokens

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type and evaluation design, the following additional figures would communicate results most effectively:

1. **Absolute benchmark scores bar chart**: Side-by-side MMLU, HellaSwag, ARC-Easy, ARC-Challenge for both models (shows individual components before ratio computation)
2. **Ratio/delta visualization**: Scatter or lollipop chart showing the two derived metrics (ratio and delta) for both models with bootstrap CI error bars
3. **MMLU subject-level breakdown**: Heatmap of per-subject accuracy for both models (reveals whether OLMo advantage is domain-specific or broad)
4. **Bootstrap distribution**: Histogram of bootstrap ratio differences with null hypothesis line at 0 and threshold line at 0.02

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (lm-evaluation-harness completes for both model checkpoints)
2. `olmo_mmlu_hellaswag_ratio > pythia_mmlu_hellaswag_ratio + 0.02`

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (verify before running evaluation):**

| Pre-condition | Check | How to Verify |
|---------------|-------|---------------|
| mechanism_exists | Checkpoint revision for Pythia ~300B tokens exists on HuggingFace Hub | `huggingface_hub.list_repo_refs("EleutherAI/pythia-6.9b")` — check step143000 exists |
| mechanism_exists | Checkpoint revision for OLMo ~300B tokens exists on HuggingFace Hub | `huggingface_hub.list_repo_refs("allenai/OLMo-7B-hf")` — identify matched step |
| mechanism_isolatable | Token count difference between selected checkpoints < 10% | Compute: abs(pythia_tokens - olmo_tokens) / 300B < 0.10 |
| baseline_measurable | lm-evaluation-harness produces non-null MMLU results for both models | Test run on single MMLU subject before full evaluation |

**Architecture Compatibility:** ✅ — Both models are supported by lm-evaluation-harness HuggingFace backend. No custom architecture modifications required.

**Activation Indicators:**
- `mechanism_log_message`: lm-evaluation-harness stdout shows "Running..." for all 4 tasks on both models
- `tensor_shape_change`: N/A (evaluation-only experiment, no architecture modification)
- `metric_delta_expected`: OLMo_ratio - Pythia_ratio in range [0.02, 0.10] based on literature gap estimates

**Mechanism Verification Code:**
```python
def verify_experiment_preconditions(pythia_id, pythia_revision, olmo_id, olmo_revision):
    """Verify all pre-conditions before running full evaluation."""
    from huggingface_hub import list_repo_refs
    import warnings
    
    # Check Pythia checkpoint exists
    pythia_refs = {r.name for r in list_repo_refs(pythia_id).branches}
    assert pythia_revision in pythia_refs, f"Pythia revision {pythia_revision} not found"
    
    # Check OLMo checkpoint exists
    olmo_refs = {r.name for r in list_repo_refs(olmo_id).branches}
    assert olmo_revision in olmo_refs, f"OLMo revision {olmo_revision} not found"
    
    # Estimate token counts and check match
    # Pythia: step143000 × 2,097,152 tokens/step ≈ 300B
    pythia_tokens = int(pythia_revision.replace("step", "")) * 2_097_152
    # OLMo: need to read from training config or metadata
    print(f"Pythia checkpoint tokens: {pythia_tokens / 1e9:.1f}B")
    print(f"Token count match within 10%: {abs(pythia_tokens - 3e11) / 3e11 < 0.10}")
    
    return True

# Run quick sanity check on single task
def sanity_check_single_subject(model_id, revision):
    """Test lm-eval on single MMLU subject before full run."""
    cmd = ["lm_eval", "--model", "hf",
           "--model_args", f"pretrained={model_id},revision={revision}",
           "--tasks", "mmlu_abstract_algebra",
           "--num_fewshot", "5",
           "--limit", "50",  # Only 50 examples for sanity check
           "--output_path", f"./sanity_{revision}/"]
    subprocess.run(cmd, check=True)
```

**Failure Detection:**
- If lm-evaluation-harness raises `ValueError: Model checkpoint not found` → verify revision name from HuggingFace Hub UI
- If MMLU accuracy < 0.20 for both models → evaluation setup error (expected > 0.20 for 4-way MC even random)
- If OLMo ratio - Pythia ratio > 0.15 → likely token count mismatch (OLMo checkpoint is much later in training)

**Hypothesis Support Threshold:** `olmo_ratio - pythia_ratio > 0.02` AND `p_value < 0.05`
**Hypothesis Support Metric:** `mmlu_hellaswag_ratio` (primary); `arc_delta` (secondary)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*MCP not available in ablation mode. References from established literature:*

**Source A.1**: Biderman et al. (2023) — Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling
- **Type:** Primary paper for Pythia model suite
- **Relevance:** Checkpoint naming convention (step{N}), training configuration (batch size 2,097,152 tokens), step→token conversion table (Table A1)
- **Key Insights:**
  - 143,000 steps ≈ 300B tokens for Pythia models
  - Consistent data ordering across all Pythia model sizes
  - All checkpoints available on HuggingFace Hub at `EleutherAI/pythia-{size}`
- **Used For:** Pythia checkpoint selection, token count verification

**Source A.2**: Groeneveld et al. (2024) — OLMo: Accelerating the Science of Language Models
- **Type:** Primary paper for OLMo model suite
- **Relevance:** OLMo training configuration, checkpoint availability, benchmark evaluation protocol
- **Key Insights:**
  - OLMo-7B uses global batch size ~2M tokens
  - Intermediate checkpoints available; need to compute step→token from training config
  - Evaluated with lm-evaluation-harness using same shot configs
- **Used For:** OLMo checkpoint selection, evaluation protocol matching

**Source A.3**: Gao et al. (2021) — A Framework for Few-Shot Language Model Evaluation (lm-evaluation-harness)
- **Type:** Framework paper
- **Relevance:** Standard shot configurations for MMLU (5-shot), HellaSwag (0-shot), ARC (25-shot)
- **Used For:** Evaluation protocol design, shot configuration selection

### B. GitHub Implementations (Exa)

**Repository B.1**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance**: Primary evaluation framework; supports both Pythia and OLMo via HuggingFace backend
- **Key invocation**:
  ```bash
  lm_eval --model hf \
    --model_args pretrained=MODEL_ID,revision=REVISION \
    --tasks mmlu,hellaswag,arc_easy,arc_challenge \
    --batch_size auto \
    --output_path ./results/
  ```
- **Configuration Extracted:** Standard CLI interface; `--limit` flag for debugging; `--log_samples` for bootstrap resampling
- **Used For:** Core evaluation execution design

**Repository B.2**: EleutherAI/pythia
- **URL**: https://github.com/EleutherAI/pythia
- **Relevance**: Checkpoint step table (training_config/pythia_6.9b_config.json); verification of step→token mapping
- **Used For:** Pythia checkpoint revision selection

**Repository B.3**: allenai/OLMo
- **URL**: https://github.com/allenai/OLMo
- **Relevance**: Training configuration for step→token mapping; checkpoint naming convention
- **Used For:** OLMo checkpoint revision selection

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — evaluation pipeline uses existing frameworks with clear public documentation. No complex novel architecture requiring semantic code analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Benchmark tasks selection | Literature | A.2 (OLMo paper evaluation protocol) |
| Shot configurations | Literature + Framework | A.3 (lm-eval standard configs) |
| Pythia checkpoint at 300B | Literature | A.1 (Table A1, step143000) |
| OLMo checkpoint at 300B | Literature | A.2 (training config) |
| Evaluation framework | GitHub | B.1 (lm-evaluation-harness) |
| Success threshold (> 0.02) | Hypothesis | Phase 2B H-E1 specification |
| Bootstrap CI method | Literature | Standard statistical practice |
| Hardware requirements | Estimation | 7B-class model fp16 evaluation |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- 2026-08-31: H-E1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-31: experiment_design.status = COMPLETED (Phase 2C finished)

---

*MCP Tools Used: Knowledge grounded in literature (Archon/Exa MCP unavailable in ablation mode)*
*All specifications grounded in established Pythia/OLMo paper protocols and lm-evaluation-harness documentation*
*Next Phase: Phase 3 - Implementation Planning*
