# Experiment Design: H-M4

**Date:** 2026-08-21
**Author:** Anonymous
**Hypothesis Statement:** Under short RLEF (50 GRPO steps), variance-50 achieves ≥2pp HumanEval+ pass@1 improvement over baseline AND ≥1pp improvement over random-50, as measured by EvalPlus correctness-based evaluation on HumanEval+ (164 problems, k=8 eval generations) at the step-50 checkpoint.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** — Tests capability transfer from gradient concentration to measurable pass@1 improvement.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M3 (FAILED / SHOULD_WORK — limitation recorded, execution continues)
**Gate Status:** SHOULD_WORK — failure narrows scope, does not block

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M4
- **Type:** MECHANISM
- **Prerequisites:** H-M3 (SHOULD_WORK, FAILED — limitation recorded)

### Gate Condition
**SHOULD_WORK (gate type):** Gradient concentration (H-M2 confirmed) must translate to HumanEval+ pass@1 improvement of ≥2pp over baseline AND ≥1pp over random-50 at step 50. Gate failure = partial result (P2 backup), not stop.

---

## Continuation Context

H-M4 is a **continuation experiment**. It reuses the GRPO training runs from H-M2 (variance-50 vs random-50 vs full-374, 50 steps). No new training is required if checkpoints were saved at steps 10, 20, and 50. H-M4 adds:
1. EvalPlus evaluation of all three conditions at step 0 (baseline)
2. EvalPlus evaluation at step 10, 20, and 50 checkpoints
3. Computation of pass@1 improvement = pass@1(step_N) - pass@1(step_0)

**Context from H-M2/H-M3:** Training infrastructure confirmed functional. frac_reward_zero_std logging operational. Checkpoint saving at steps 10/20/50 must be enabled in H-M2 training config for H-M4 to reuse them.

### Previous Hypothesis Results (H-M3)
H-M3 FAILED (SHOULD_WORK): The gradient concentration advantage of variance-50 was not sustained throughout all 50 GRPO steps. This is a LIMITATION, not a blocker. H-M4 proceeds with awareness that the frac_reward_zero_std gap may close mid-training, which increases risk that P1 fails. P2 (mechanistic evidence from H-M2) remains the primary evidence base.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Archon KB domain:** The Archon knowledge base is indexed primarily on computer vision/diffusion model literature and does not contain GRPO/RLEF/HumanEval-specific content. All 4 knowledge queries returned image-generation domain results (similarity < 0.47, diffusion/LoRA/DreamBooth content). No relevant findings for this hypothesis domain.

**Impact:** No Archon-sourced hyperparameters or experimental designs for GRPO code generation. All specifications derived from Exa GitHub searches and Phase 2B planning.

### Archon Code Examples

Same domain mismatch — all code examples were diffusion pipeline code. No applicable patterns.

### Exa GitHub Implementations

**Query 1: EvalPlus HumanEval+ evaluation with DeepSeek-Coder checkpoint**

**Repository 1: evalplus/evalplus** (⭐ 2K+)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official EvalPlus evaluation framework used for HumanEval+ and MBPP+ — the exact evaluation tool specified in H-M4 protocol
- **Key CLI usage:**
  ```bash
  pip install "evalplus[vllm]" --upgrade
  
  # Code generation from local checkpoint (hf backend):
  evalplus.codegen --model "/path/to/checkpoint-N" \
                   --greedy \
                   --root ./eval_results \
                   --dataset humaneval \
                   --backend hf
  
  # Evaluation of generated samples:
  evalplus.evaluate --model "/path/to/checkpoint-N" \
                    --dataset humaneval \
                    --backend hf \
                    --greedy
  ```
- **Key insight:** EvalPlus supports `--backend hf` for local HuggingFace checkpoints. DeepSeek-Coder series is confirmed in EvalPlus leaderboard (deepseek-coder-6.7b-instruct). For pass@k > 1, samples.jsonl must contain list of solutions per task_id.
- **Used for:** Evaluation protocol, CLI commands for checkpoint evaluation

**Repository 2: axolotl-ai-cloud/grpo_code** 
- **URL:** https://github.com/axolotl-ai-cloud/grpo_code/tree/main/eval_plus
- **Relevance:** Directly combines GRPO training with EvalPlus evaluation — the exact experimental pattern for H-M4
- **Key code:**
  ```bash
  # Evaluate GRPO-trained checkpoint on EvalPlus
  bash test.sh {path_to_local_model_checkpoint} {tensor_parallel_size} {output_dir}
  ```
- **Used for:** Confirms checkpoint-based EvalPlus evaluation pattern; same test.sh pattern applicable

**Query 2: TRL GRPOTrainer checkpoint save and binary execution reward**

**Repository 3: huggingface/trl** (official TRL)
- **URL:** https://github.com/huggingface/trl/blob/main/trl/scripts/grpo.py
- **Relevance:** Official TRL GRPOTrainer — used for all GRPO training in this experiment chain
- **Key checkpoint config:**
  ```python
  training_args = GRPOConfig(
      output_dir="./grpo_checkpoints",
      save_steps=10,          # Save every 10 steps → checkpoints at 10, 20, 30, 40, 50
      max_steps=50,
      per_device_train_batch_size=4,
      num_generations=4,      # G=4
      use_vllm=False,
      learning_rate=5e-7,
      logging_steps=1,
      report_to="none",
  )
  trainer = GRPOTrainer(
      model="deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      reward_funcs=binary_execution_reward,
      args=training_args,
      train_dataset=variance_50_dataset,
  )
  trainer.train()
  # Checkpoints saved as: ./grpo_checkpoints/checkpoint-10, checkpoint-20, checkpoint-50
  ```
- **Used for:** Checkpoint save configuration (save_steps=10), confirming checkpoint naming convention

**Repository 4: modal.com GRPO+TRL example**
- **URL:** https://modal.com/docs/examples/grpo_trl
- **Relevance:** End-to-end GRPO training + checkpoint loading pattern
- **Key insight:** `checkpoint-{N}` naming. For standard TRL, `checkpoint-N` format; for verl, `global_step_N/actor/huggingface`.
- **Used for:** Checkpoint path pattern confirmation

### 🎯 Implementation Priority Assessment

**CRITICAL: This is NOT a paper reproduction — it is an original experiment using the TRL framework.**

No author implementation to search for. The framework (TRL GRPOTrainer) is the authoritative reference.

**Recommended Implementation Path:**
- Primary: TRL GRPOTrainer (huggingface/trl) + EvalPlus CLI (evalplus/evalplus) — both official, actively maintained
- Fallback: Custom evaluation loop using evalplus Python API if CLI incompatible with checkpoint format
- Justification: These are the exact tools specified in Phase 2B and confirmed functional in H-E1

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. TRL GRPOTrainer and EvalPlus CLI APIs are well-documented and do not require semantic code analysis.

---

## Experiment Specification

### Dataset

**Training Dataset (for GRPO):**
- **Name:** MBPP (Mostly Basic Python Problems) — subset selection
- **Type:** standard (real, established benchmark)
- **Source:** google-research-datasets/mbpp (HuggingFace Datasets)
- **Training split:** 374 problems (HuggingFace `train` split)
- **Conditions:**
  - variance-50: Top-50 problems by p_i*(1-p_i) variance, selected in H-E1
  - random-50: 50 randomly sampled problems (fixed seed=42), selected in H-M2
  - full-374: All 374 training problems (upper bound reference)

**Evaluation Dataset (for pass@1 measurement):**
- **Name:** HumanEval+ (EvalPlus)
- **Type:** standard (real, established benchmark)
- **Source:** evalplus/humanevalplus (HuggingFace); 164 problems
- **Note:** HumanEval+ extends HumanEval with 80× more test cases for rigorous correctness evaluation

**Loading Information:**
- Method: HuggingFace Datasets (MBPP) + EvalPlus pip package (HumanEval+)
- Identifier (MBPP): `"google-research-datasets/mbpp"`, config `"full"`, split `"train"`
- Identifier (HumanEval+): installed via `pip install evalplus`, accessed via `evalplus.data.get_human_eval_plus()`
- Code:
  ```python
  # MBPP training data (subset selection inherited from H-E1/H-M2)
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", "full", split="train")
  # Apply variance-50 / random-50 filtering using problem_ids from H-E1
  
  # HumanEval+ evaluation (via EvalPlus CLI)
  # evalplus.evaluate handles dataset loading internally
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-Instruct (frozen, step 0 checkpoint)
- **Type:** Code LLM, instruction-tuned, 7B parameters, causal decoder
- **Source:** deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)
- **Role in experiment:** step-0 baseline; evaluate pass@1 before any GRPO training

**Loading Information:**
- Method: HuggingFace Transformers / EvalPlus `--backend hf`
- Identifier: `"deepseek-ai/deepseek-coder-7b-instruct-v1.5"`
- Code:
  ```python
  # Direct loading for evaluation
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  # OR via EvalPlus CLI:
  # evalplus.evaluate --model "deepseek-ai/deepseek-coder-7b-instruct-v1.5" \
  #                   --dataset humaneval --backend hf --greedy
  ```

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-Instruct + GRPO fine-tuning on variance-50 MBPP subset

**Core Mechanism Implementation (EvalPlus Checkpoint Evaluation Loop):**

```python
# Core Mechanism: EvalPlus evaluation at GRPO training checkpoints
# Based on: evalplus/evalplus CLI + TRL GRPOTrainer checkpoint structure
# H-M4 adds evaluation to H-M2 training runs

import subprocess
from pathlib import Path

def evaluate_checkpoint_pass_at_1(
    checkpoint_dir: str,
    dataset: str = "humaneval",
    n_samples: int = 8,  # k=8 for pass@1 estimation
    output_root: str = "./eval_results"
) -> float:
    """
    Run EvalPlus evaluation on a GRPO checkpoint.
    Returns pass@1 on HumanEval+.
    """
    # Step 1: Generate k=8 samples per problem
    gen_cmd = [
        "python", "-m", "evalplus.codegen",
        "--model", checkpoint_dir,
        "--dataset", dataset,
        "--backend", "hf",
        "--n_samples", str(n_samples),
        "--temperature", "0.8",   # non-zero temp for k>1 sampling
        "--root", output_root,
    ]
    subprocess.run(gen_cmd, check=True)
    
    # Step 2: Evaluate generated samples
    eval_cmd = [
        "python", "-m", "evalplus.evaluate",
        "--dataset", dataset,
        "--samples", f"{output_root}/samples.jsonl",
    ]
    result = subprocess.run(eval_cmd, capture_output=True, text=True)
    
    # Step 3: Parse pass@1 from output
    pass_at_1 = parse_pass_at_1(result.stdout)
    return pass_at_1

# Evaluation schedule for H-M4:
CHECKPOINTS = {
    "step_0":  "deepseek-ai/deepseek-coder-7b-instruct-v1.5",  # frozen baseline
    "step_10": "./grpo_checkpoints/variance50/checkpoint-10",
    "step_20": "./grpo_checkpoints/variance50/checkpoint-20",
    "step_50": "./grpo_checkpoints/variance50/checkpoint-50",
}
CONDITIONS = ["baseline_frozen", "variance50", "random50", "full374"]
```

### Training Protocol

**NOTE:** H-M4 does NOT run new GRPO training. It evaluates checkpoints from H-M2 training.

**Inherited from H-M2 (continuation experiment):**

| Parameter | Value | Source |
|-----------|-------|--------|
| Model | DeepSeek-Coder-7B-Instruct-v1.5 | H-E1 confirmed functional |
| Optimizer | AdamW (TRL default) | TRL GRPOTrainer default |
| Learning rate | 5e-7 | Phase 2B specification |
| GRPO group size G | 4 | Phase 2B specification |
| use_vllm | False | H-E1 environment constraint |
| generation_batch_size | 4 | Phase 2B specification |
| max_steps | 50 | Phase 2B specification |
| save_steps | 10 | Required for H-M4 evaluation |
| Reward function | binary_execution_reward | Phase 2B specification |
| Seeds | 1 (fixed seed=42) | Phase 2B specification |

**H-M4-specific additions:**
- Checkpoint save at steps 0 (frozen baseline), 10, 20, 50
- EvalPlus evaluation at each checkpoint for all 3 conditions
- k=8 sampling per HumanEval+ problem for pass@1 estimation

**IMPORTANT for Phase 4 implementation:** If H-M2 checkpoints already exist from prior training, H-M4 skips training and runs evaluation only. If not, H-M4 must re-run H-M2 training with `save_steps=10` enabled.

### Evaluation

**Primary Evaluation: HumanEval+ pass@1**

| Metric | Definition | Threshold |
|--------|-----------|-----------|
| pass@1 (HumanEval+) | Fraction of 164 HumanEval+ problems solved correctly in 1 attempt (estimated from k=8 samples) | Primary gate |
| improvement_variance50 | pass@1(step_50, variance50) - pass@1(step_0, frozen) | ≥ 2pp (P1) |
| gap_vs_random50 | improvement_variance50 - improvement_random50 | ≥ 1pp (P1) |
| efficiency_ratio | improvement_variance50 / improvement_full374 | ≥ 0.80 (P3, conditional) |

**Success Criteria (PoC):**
- **P1 (primary):** improvement_variance50 ≥ 2pp AND gap_vs_random50 ≥ 1pp at step 50
- **P3 (secondary, conditional):** efficiency_ratio ≥ 0.80 if both variance50 and full374 achieve ≥ 2pp improvement
- **PoC pass condition:** P1 satisfied at step 50

**Expected Baseline Performance (from research):**
- DeepSeek-Coder-7B-Instruct HumanEval+ pass@1 (frozen): ~72-75% (from EvalPlus leaderboard, deepseek-coder-6.7b-instruct)
- Improvement range at 50 GRPO steps on 374 problems: up to 13pp in prior work (Skopin & Kotelnikov); directional improvement expected even for 50-problem subsets
- Risk R4: 50-step budget on 50 problems may yield < 2pp for all conditions — if full-374 also < 2pp, P1 is declared "untestable" not "failed"

**Metrics Loading Information:**
- Task Type: code_generation → correctness evaluation
- Library: `evalplus` (pip package)
- Code:
  ```python
  # Via CLI (recommended):
  evalplus.evaluate --model {checkpoint_path} --dataset humaneval --backend hf --greedy
  
  # Via Python API:
  from evalplus.data import get_human_eval_plus, write_jsonl
  from evalplus.evaluate import evaluate_functional_correctness
  problems = get_human_eval_plus()  # 164 problems with augmented tests
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Pass@1 Improvement Bar Chart**: Target (2pp, 1pp gap) vs actual metrics for all 3 conditions at step 50

#### Additional Figures (LLM Autonomous)
- **Learning curve:** pass@1 improvement trajectory across steps 10, 20, 50 for all 3 conditions (shows if variance-50 advantage accumulates over training)
- **Condition comparison heatmap:** pass@1 at each (condition × step) checkpoint, 3×4 grid
- **Scatter:** frac_reward_zero_std (from H-M2 logs) vs pass@1 improvement per condition — tests mechanistic-capability correlation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m4/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. EvalPlus evaluation runs without error for all 3 conditions × 4 checkpoints
2. `improvement_variance50 ≥ 2pp` AND `gap_vs_random50 ≥ 1pp` at step 50

**Failure interpretation:**
- If P1 fails but P3 metric (mechanistic) passes: PARTIAL — mechanism confirmed (H-M2), capability transfer needs longer training
- If both P1 and frac_reward_zero_std evidence (H-M2 P2) fail: ABANDON — H0 supported
- If no condition achieves 2pp improvement: R4 realized — declare "P1 untestable" with P2 as primary evidence

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB:** No relevant sources found. All 5 knowledge queries (GRPO, RLEF, EvalPlus, variance selection, DeepSeek MBPP) returned computer vision / diffusion model domain content (similarity < 0.47). This confirms the Archon KB is indexed on vision/generative-image literature, not code-LLM/RLEF research.

**Impact on specification:** All hyperparameters and protocols derived from Phase 2B planning (built on cited papers: Gradient Starvation arXiv:2605.07689, VIGOR arXiv:2607.22002, Gehring et al. arXiv:2410.02089, Sun et al. arXiv:2506.05316) and Exa GitHub search.

### B. GitHub Implementations (Exa)

**Repository 1: evalplus/evalplus**
- **URL:** https://github.com/evalplus/evalplus
- **Query:** "EvalPlus HumanEval+ evaluation DeepSeek-Coder GRPO RLEF checkpoint pass@1"
- **Relevance:** Official EvalPlus framework — the canonical tool for HumanEval+ evaluation
- **Key finding:** `--backend hf` supports local HuggingFace checkpoints; DeepSeek-Coder-6.7B confirmed in leaderboard; k>1 sampling uses `--n_samples` flag
- **Used for:** Evaluation CLI commands, pass@1 measurement methodology

**Repository 2: axolotl-ai-cloud/grpo_code**
- **URL:** https://github.com/axolotl-ai-cloud/grpo_code/tree/main/eval_plus
- **Query:** "EvalPlus HumanEval+ evaluation DeepSeek-Coder GRPO RLEF checkpoint pass@1"
- **Relevance:** Directly combines GRPO training with EvalPlus evaluation — exact experimental pattern
- **Used for:** Confirms GRPO + EvalPlus integration pattern; `test.sh {checkpoint_path}` evaluation pattern

**Repository 3: huggingface/trl (grpo.py)**
- **URL:** https://github.com/huggingface/trl/blob/main/trl/scripts/grpo.py
- **Query:** "TRL GRPOTrainer MBPP binary execution reward code generation training loop checkpoint save"
- **Key code extracted:**
  ```python
  trainer = GRPOTrainer(
      model=model_args.model_name_or_path,
      reward_funcs=reward_funcs,
      args=training_args,    # GRPOConfig with save_steps=10
      train_dataset=dataset[split],
  )
  trainer.train()
  trainer.save_model(training_args.output_dir)
  ```
- **Used for:** Checkpoint save configuration, GRPOConfig parameter reference

**Repository 4: TRL GRPOConfig documentation**
- **URL:** https://huggingface.co/docs/trl/en/grpo_trainer
- **Key finding:** `save_steps` parameter controls checkpoint save frequency; `use_adaptive_entropy` saves entropy_coef with checkpoint for resumability
- **Used for:** Checkpoint save parameter specification (save_steps=10)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa search results was sufficiently clear. TRL GRPOTrainer and EvalPlus CLI are well-documented APIs; no complex custom layers or unfamiliar architectures requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** H-M2 and H-M3 training runs
- **Reused components:**
  - Training infrastructure: TRL GRPOTrainer, binary_execution_reward, use_vllm=False
  - Checkpoint paths: ./grpo_checkpoints/{condition}/checkpoint-{step}
  - MBPP subset IDs: variance-50 and random-50 problem IDs from H-E1/H-M2
  - Hyperparameters: lr=5e-7, G=4, batch=4, max_steps=50 (all inherited)
- **Why reused:** H-M4 is evaluation-only on H-M2 checkpoints; enables controlled comparison (only evaluation added, no training change)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training dataset (MBPP) | Phase 2B + H-E1 validated | 02b_verification_plan.md §1.3 |
| Evaluation dataset (HumanEval+) | EvalPlus (Exa B.1) | evalplus/evalplus |
| Variance-50 problem IDs | H-E1 output | docs/youra_research/h-e1/04_validation.md |
| Random-50 problem IDs | H-M2 training run | docs/youra_research/h-m2/04_validation.md |
| lr=5e-7, G=4, batch=4 | Phase 2B §2.3 | 02b_verification_plan.md |
| Checkpoint save_steps=10 | TRL docs (Exa B.3, B.4) | huggingface/trl GRPOConfig |
| EvalPlus CLI --backend hf | EvalPlus docs (Exa B.1) | evalplus/evalplus README |
| pass@1 ≥ 2pp threshold | Phase 2B §H-M4 success | 02b_verification_plan.md §2.2 |
| gap ≥ 1pp threshold | Phase 2B §H-M4 success | 02b_verification_plan.md §2.2 |
| k=8 eval generations | Phase 2B §H-M4 protocol | 02b_verification_plan.md §2.2 |
| Baseline pass@1 ~72-75% | EvalPlus leaderboard | evalplus.github.io/leaderboard.html |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — restated in state block)
**Date:** 2026-08-21

### Workflow History for This Hypothesis
- H-M4 set IN_PROGRESS: 2026-08-21T17:13:13Z
- Phase 2C experiment design: IN_PROGRESS → COMPLETED: 2026-08-21

---

## Quality Validation Results

```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified (inherited from H-M2 or Phase 2B)
✅ Dataset choice justified (MBPP training, HumanEval+ eval — from Phase 2A)
✅ Mechanism grounded in code (EvalPlus CLI + TRL checkpoint pattern from Exa)
✅ No unsupported assumptions (all thresholds from Phase 2B; baseline ~72% from EvalPlus leaderboard)
✅ Full traceability (all specs in Traceability Matrix §E)

Note: Archon KB returned no relevant results (diffusion domain mismatch).
All specifications backed by Phase 2B planning + Exa GitHub evidence.

Overall: PASSED
```

---

*MCP Tools Used: Archon (Knowledge + Code, 4 queries — no relevant results), Exa (GitHub, 2 queries — 4 relevant repositories)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
