# Experiment Design: H-M1

**Date:** 2026-05-19
**Author:** Anonymous
**Hypothesis Statement:** Under controlled conditions, if execution reward directly signals functional incorrectness at program level, then the model reallocates probability mass toward control-flow and data-flow AST transformations (not surface edits), because program-level correctness objectives create gradient pressure specifically on execution-relevant code structures.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM Hypothesis** - Tests the causal link between execution reward and selective AST node reallocation.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 COMPLETED — PASS (Bootstrap 95% CI [4.6500, 8.7314] excludes zero; GRPO +250% structural efficiency over DPO)
**Gate Status:** MUST_WORK — blocking H-M2 if fails

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED — PASS)

### Gate Condition
MUST_WORK — If execution-RL does not show significantly higher proportion of control-flow/data-flow AST edits over DPO (p < 0.05), this blocks H-M2 and requires investigation of AST decomposition taxonomy.

---

## Continuation Context

This is a continuation experiment building on H-E1. H-E1 established that GRPO achieves 250% higher mean AST semantic edit distance per KL unit compared to DPO (27 KL-matched checkpoint pairs at tolerance=0.15). H-M1 now dissects the nature of those edits: are they concentrated in semantically relevant AST nodes (control-flow, data-flow) or in surface nodes?

### Previous Hypothesis Results (H-E1)
- **GRPO mean AST semantic edit distance**: 3.5 (DPO: 1.0)
- **Bootstrap 95% CI for GRPO−DPO differential**: [4.6500, 8.7314] — excludes zero
- **KL-matched pairs**: 27 checkpoint pairs at KL tolerance=0.15
- **Gate MUST_WORK**: PASS
- **Infrastructure proven**: TRL GRPOTrainer + DPOTrainer on DeepSeek-Coder-7B-instruct-v1.5; zss AST edit distance; evalplus evaluation harness

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GRPO execution reward AST edit distance experiment design**
- No domain-relevant results found. Archon KB contains primarily image generation / diffusion content, not code-generation RL.
- Returned results: OpenAI instruction following blog, LAION-5B, LoRA conceptual guide — all irrelevant to this domain.

**Query 2: DPO GRPO policy gradient code generation training**
- No domain-relevant results found. Returned HuggingFace diffusers training scripts — irrelevant.

**Conclusion**: Archon KB has no past cases for this specific domain. Experiment design grounded in Exa GitHub findings and domain knowledge from Phase 2B.

### Archon Code Examples

**Query: GRPO TRL GRPOTrainer reward function PyTorch**
- No domain-relevant code examples. Returned PyTorch distributed ops, scaled dot-product attention, Accelerate training boilerplate.
- **Insight extracted**: Accelerate + TRL integration pattern confirmed as standard approach.

### Exa GitHub Implementations

**Query 1: GRPO TRL GRPOTrainer execution reward code generation**

**Repository 1**: huggingface/trl (⭐ 18K+)
- **URL**: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Relevance**: Official TRL GRPOTrainer implementation — primary implementation path
- **Key API**:
  ```python
  from trl import GRPOTrainer, GRPOConfig
  trainer = GRPOTrainer(
      model="deepseek-ai/deepseek-coder-7b-instruct-v1.5",
      reward_funcs=[execution_reward_func, error_type_reward_func],
      args=training_args,
      train_dataset=dataset,
  )
  trainer.train()
  ```
- **Custom reward function signature**:
  ```python
  def execution_reward_func(prompts, completions, **kwargs) -> list[float]:
      # Returns 1.0 if code passes tests, 0.0 otherwise (binary)
      # Or error-type graduated: 1.0 pass, 0.5 runtime, 0.0 syntax
      rewards = []
      for completion in completions:
          reward = evaluate_code_execution(completion)
          rewards.append(reward)
      return rewards
  ```
- **Multi-task reward**: Supports list of reward functions (sum of rewards)
- **Used For**: Primary GRPOTrainer training loop for H-M1

**Repository 2**: modal-labs/modal-examples grpo_trl.py
- **URL**: https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/reinforcement-learning/grpo_trl.py
- **Relevance**: Production-ready execution reward for code generation (sandbox execution)
- **Key Code**:
  ```python
  def compute_reward(completion: str, testcase: Sequence[str]) -> int:
      sb = modal.Sandbox.create(app=app)
      code_to_execute = get_generated_code_and_test_cases(completion, testcase)
      p = sb.exec("python", "-c", code_to_execute, timeout=30)
      p.wait()
      return 1 if p.returncode == 0 else 0
  ```
- **Dataset used**: OpenCoder-LLM/opc-sft-stage2 (educational_instruct)
- **Used For**: Execution reward implementation pattern

**Repository 3**: policy-gradient/GRPO-Zero
- **URL**: https://github.com/policy-gradient/GRPO-Zero
- **Relevance**: Minimal GRPO from scratch — clarifies advantage computation
- **GRPO Algorithm**:
  ```
  For each question q_i, sample M answers
  A[t] = (r_ij - mean_i) / std_i   # per-token advantage
  Loss = ∇_θ log π_θ(a[t]) · A[t]  # policy gradient
  ```
- **Used For**: Understanding KL dynamics and advantage normalization

**Query 2: AST edit distance control-flow data-flow probability mass GRPO DPO**

**Source 1**: arxiv 2404.08817 — "Revisiting Code Similarity Evaluation with AST Edit Distance"
- **URL**: https://arxiv.org/abs/2404.08817
- **Relevance**: Validates AST edit distance (TSED/zss) for measuring code structural change
- **Key insight**: AST edit distance correlates highly with established metrics; effective for capturing control-flow/data-flow structural differences
- **Used For**: Validates zss AST edit distance as structural reallocation metric

**Source 2**: arxiv 2002.08653 — "Detecting Code Clones with FA-AST"
- **Relevance**: Control-flow + data-flow edge taxonomy for AST node classification
- **Node types used**: If, For, While (control-flow); Assign, Call, Return (data-flow); surface = strings, comments, variable names
- **Used For**: AST node decomposition taxonomy for H-M1

**Serena Analysis Needed**: false — code from search results is sufficiently clear for this experiment. The TRL GRPOTrainer API is well-documented; AST node classification uses Python's built-in `ast` module.

### 🎯 Implementation Priority Assessment

For this experiment, no single paper defines the method — we are COMPARING two established training paradigms (GRPO vs DPO). Therefore:

**Recommended Implementation Path:**
- Primary: TRL official GRPOTrainer (huggingface/trl) + TRL DPOTrainer — both from same library for fair comparison
- Fallback: Custom implementation using policy-gradient/GRPO-Zero patterns
- Justification: H-E1 already validated TRL-based implementation. H-M1 reuses same checkpoints and adds AST decomposition analysis layer.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. TRL GRPOTrainer is well-documented; AST decomposition uses Python `ast` module with standard node type inspection.

---

## Experiment Specification

### Dataset

**Name**: HumanEval+ / MBPP+ (EvalPlus benchmark suite)
**Type**: standard
**Source**: evalplus/evalplus (official EvalPlus organization)
**Version**: Latest stable (EvalPlus v0.2.0+)
**Splits**:
- HumanEval+: 164 problems (full set)
- MBPP+: 378 problems (full sanitized set)
- **Total**: 542 evaluation problems — statistically meaningful for AST edit proportion analysis

**Hypothesis Fit**: Canonical function-level Python benchmarks. AST parsing of model outputs is straightforward (Python `ast` module). Sufficient number of problems for Mann-Whitney U test with adequate power. Already proven valid in H-E1 with 27 KL-matched checkpoint pairs.

**Preprocessing**:
- Use evalplus harness for prompt formatting
- Parse model outputs to extract Python code blocks
- Filter syntactically invalid outputs (log rate)
- Normalize AST: strip docstrings and comments before edit distance computation

**Augmentation**: None (evaluation benchmark — no training augmentation)

**Synthetic Data Policy**: COMPLIANT — HumanEval+ and MBPP+ are real, established standard benchmarks (type: standard). Not synthetic.

**Loading Information** (for Phase 4 download):
- Method: evalplus CLI / pip package
- Identifier: `evalplus/humanevalplus`, `evalplus/mbppplus`
- Code:
  ```python
  # Option 1: evalplus CLI (recommended)
  pip install evalplus
  from evalplus.data import get_human_eval_plus, get_mbpp_plus
  humaneval_data = get_human_eval_plus()   # dict of 164 problems
  mbpp_data = get_mbpp_plus()              # dict of 378 problems

  # Option 2: HuggingFace datasets
  from datasets import load_dataset
  humaneval = load_dataset("evalplus/humanevalplus")
  mbpp = load_dataset("evalplus/mbppplus")
  ```

### Models

#### Baseline Model

**Architecture**: DeepSeek-Coder-7B-instruct-v1.5 + SFT-only (no RL fine-tuning)
**Configuration**:
- 7B parameter decoder-only transformer
- Code-specialized pretraining
- Instruction-tuned (instruct variant)
- Used as: (1) reference policy for KL computation, (2) SFT-only baseline condition

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `deepseek-ai/deepseek-coder-7b-instruct-v1.5`
- Code:
  ```python
  from transformers import AutoTokenizer, AutoModelForCausalLM
  import torch

  model_id = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
  tokenizer = AutoTokenizer.from_pretrained(model_id)
  model = AutoModelForCausalLM.from_pretrained(
      model_id,
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  ```

**Modifications for H-M1**: None for baseline. For comparison conditions, model fine-tuned via GRPO (binary reward, error-type reward) and DPO using TRL.

#### Proposed Model

**Architecture**: DeepSeek-Coder-7B-instruct-v1.5 — same base, fine-tuned with GRPO (binary + error-type execution rewards). This is the **treatment condition**, not an architectural change.

**Core Mechanism Implementation:**

```python
# Core Mechanism: AST Node Decomposition for Structural Reallocation Analysis
# Based on: Python ast module + zss library (from H-E1)
# Purpose: Decompose AST edits into semantic vs surface categories

import ast
from zss import simple_distance, Node

# AST node type taxonomy (from FA-AST literature: arxiv 2002.08653)
CONTROL_FLOW_NODES = {ast.If, ast.For, ast.While, ast.Try, ast.With,
                       ast.ExceptHandler, ast.Break, ast.Continue}
DATA_FLOW_NODES    = {ast.Assign, ast.AugAssign, ast.AnnAssign,
                      ast.Call, ast.Return, ast.Yield, ast.Import,
                      ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef}
SURFACE_NODES      = {ast.Constant, ast.Name, ast.Expr, ast.Pass, ast.Global}

def classify_ast_edit(node_type: str) -> str:
    """Classify AST node into control_flow | data_flow | surface."""
    node_cls = getattr(ast, node_type, None)
    if node_cls in CONTROL_FLOW_NODES: return "control_flow"
    if node_cls in DATA_FLOW_NODES:    return "data_flow"
    return "surface"

def compute_edit_distribution(code_base: str, code_new: str) -> dict:
    """
    Returns proportion of edits by category.
    Output: {"control_flow": float, "data_flow": float, "surface": float,
             "semantic": float, "total_edits": int}
    """
    tree_base = ast_to_zss(ast.parse(code_base))
    tree_new  = ast_to_zss(ast.parse(code_new))
    edit_ops  = zss_edit_operations(tree_base, tree_new)  # list of (op, node_type)
    counts = {"control_flow": 0, "data_flow": 0, "surface": 0}
    for op, node_type in edit_ops:
        counts[classify_ast_edit(node_type)] += 1
    total = max(sum(counts.values()), 1)
    proportions = {k: v / total for k, v in counts.items()}
    proportions["semantic"] = proportions["control_flow"] + proportions["data_flow"]
    proportions["total_edits"] = total
    return proportions
```

### Training Protocol

**From H-E1 (Reusing proven configuration for controlled comparison — only analysis layer changes):**

**Condition A — GRPO Binary Reward:**
- **Trainer**: TRL GRPOTrainer
- **Reward**: Binary execution (1.0 pass, 0.0 fail)
- **Optimizer**: AdamW, lr=1e-5, warmup_ratio=0.1
- **Schedule**: Cosine decay
- **Batch Size**: 8 prompts × 4 generations = 32 rollouts
- **KL coefficient**: 0.1 (adaptive)
- **Max epochs**: 3
- **Checkpoint saving**: Every 50 steps (dense, for KL matching)

**Condition B — GRPO Error-Type Reward:**
- Same as A but reward = {1.0: pass, 0.5: runtime_error, 0.0: syntax_error}

**Condition C — DPO Baseline:**
- **Trainer**: TRL DPOTrainer
- **Preference pairs**: Generated via execution oracle (deterministic preference labels)
- **β**: 0.1
- **Optimizer**: AdamW, lr=5e-6
- **Batch Size**: 16
- **Max epochs**: 3
- **Checkpoint saving**: Every 50 steps

**Note on H-M1 reuse**: H-E1 already produced trained GRPO and DPO checkpoints. H-M1 re-analyzes those same checkpoints with the AST decomposition layer — no re-training required if checkpoints are available. If checkpoints not preserved, re-train with same config.

**Seeds**: 1 (fixed, same as H-E1)
**Training prompts**: CodeAlpaca/OSS-Instruct prompt set (same as H-E1)

### Evaluation

**Primary Metrics**:

1. **Semantic Edit Proportion (SEP)**: Proportion of AST edits in control-flow + data-flow nodes
   - Computed per problem per checkpoint pair
   - Aggregated: mean SEP across all 542 problems × 27 KL-matched checkpoint pairs

2. **Mann-Whitney U test**: Compare SEP distributions (GRPO vs DPO)
   - H0: SEP_GRPO = SEP_DPO
   - H1: SEP_GRPO > SEP_DPO (one-sided)
   - Significance level: p < 0.05

3. **Reward-Correctness Spearman ρ**: Correlation between reward signal and pass@1 at each training checkpoint
   - Computed separately for GRPO-binary and GRPO-error-type conditions

**Success Criteria**:
- Primary: SEP_GRPO significantly higher than SEP_DPO (Mann-Whitney U p < 0.05, one-sided)
- Secondary: Reward-correctness Spearman ρ > 0.5 for at least one GRPO condition

**PoC Pass Condition**:
1. Code runs without error
2. SEP_GRPO > SEP_DPO (effect direction confirmed)

**Expected Performance** (from H-E1 + literature):
- H-E1 showed GRPO total edit distance 3.5× higher than DPO — if concentrated in semantic nodes, SEP_GRPO should be substantially higher
- Based on FA-AST literature: execution-relevant edits (control-flow + data-flow) expected to dominate in execution-RL trained models
- Source: arxiv 2002.08653 (FA-AST node taxonomy), arxiv 2404.08817 (AST edit distance validation)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation + AST analysis
- Library: `ast` (stdlib), `zss` (pip install zss), `scipy.stats` (Mann-Whitney U), `numpy`
- Code:
  ```python
  from scipy.stats import mannwhitneyu
  import numpy as np

  stat, p_value = mannwhitneyu(sep_grpo, sep_dpo, alternative='greater')
  effect_size = np.median(sep_grpo) - np.median(sep_dpo)
  spearman_rho, _ = spearmanr(reward_signals, pass_at_1_per_checkpoint)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing mean SEP (semantic edit proportion) for GRPO-binary, GRPO-error-type, and DPO conditions with error bars (95% CI)

#### Additional Figures (LLM Autonomous)
1. **AST Edit Distribution Stacked Bar**: For each condition, stacked bar showing proportion of control-flow / data-flow / surface edits across all checkpoint pairs
2. **Reward-Correctness Scatter**: Spearman ρ scatter plot (reward signal vs pass@1 per checkpoint) for GRPO conditions
3. **SEP vs KL Trajectory**: Line plot showing semantic edit proportion vs KL divergence trajectory over training steps for GRPO vs DPO
4. **Edit Node Heatmap**: Heatmap of specific AST node type frequencies (If, For, While, Assign, Call, Return) for GRPO vs DPO

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `SEP_GRPO > SEP_DPO` (semantic edit proportion direction confirmed)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | AST decomposition into control-flow/data-flow/surface nodes is implementable for Python code | TRUE — Python `ast` module provides full node type access |
| Mechanism Isolatable | SEP can be computed independently for GRPO and DPO checkpoints | TRUE — analysis layer is decoupled from training |
| Baseline Measurable | DPO checkpoint SEP can be computed using same pipeline | TRUE — same AST decomposition applied to DPO outputs |

### Architecture Compatibility Check

**Model**: DeepSeek-Coder-7B-instruct-v1.5 generates Python code — fully parseable by Python `ast` module.

**Required Features**:
- Python code output parseable by `ast.parse()`
- Checkpoints saved at sufficient density for KL matching (every 50 steps)
- TRL GRPOTrainer and DPOTrainer compatible with DeepSeek-Coder-7B architecture (confirmed in H-E1)

**Incompatible Architectures**: None — this is an output analysis mechanism, not an architectural modification. Any model generating syntactically valid Python code is compatible.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | `"AST decomposition: control_flow=X, data_flow=Y, surface=Z"` | ast_analysis.py:compute_edit_distribution() |
| Tensor Shape | N/A — this is a post-hoc analysis, no tensor shape change | N/A |
| Metric Delta | SEP_GRPO > SEP_DPO (positive delta in semantic proportion) | evaluate_sep.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(sep_grpo: list, sep_dpo: list, results: dict) -> tuple:
    """Verify that AST decomposition mechanism is working correctly."""
    from scipy.stats import mannwhitneyu
    stat, p_value = mannwhitneyu(sep_grpo, sep_dpo, alternative='greater')
    indicators = {
        "decomposition_working": results.get("total_edits_analyzed", 0) > 0,
        "semantic_proportion_computed": all(0 <= s <= 1 for s in sep_grpo + sep_dpo),
        "grpo_higher": float(sum(g > d for g, d in zip(sep_grpo, sep_dpo))) / len(sep_grpo) > 0.5,
        "statistically_significant": p_value < 0.05,
    }
    return all(indicators.values()), indicators, p_value
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE — AST decomposition runs on all outputs | Log: total_edits_analyzed > 0 |
| Effect Measurable | SEP_GRPO > SEP_DPO (any positive delta) | Before/after comparison per checkpoint pair |
| Hypothesis Supported | Mann-Whitney U p < 0.05, one-sided | Scipy mannwhitneyu(sep_grpo, sep_dpo, alternative='greater') |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB**: No domain-relevant results found for GRPO/DPO code generation or AST edit distance. Archon KB contains primarily image generation / diffusion model content. Zero queries returned relevant results.

**Used For**: Confirmed absence of prior cases — design is based on Exa findings and Phase 2B domain knowledge.

### B. GitHub Implementations (Exa)

**Repository 1**: huggingface/trl — GRPOTrainer
- **URL**: https://github.com/huggingface/trl/blob/main/trl/trainer/grpo_trainer.py
- **Query Used**: "GRPO TRL GRPOTrainer execution reward code generation DeepSeek implementation GitHub"
- **Relevance**: Official TRL implementation — primary training framework
- **Key API**: `GRPOTrainer(model, reward_funcs, args, train_dataset)` with custom execution reward functions
- **Configuration Extracted**: reward_funcs list interface, multi-task reward support, vLLM integration option
- **Used For**: Training protocol (Condition A and B — GRPO binary and error-type)

**Repository 2**: huggingface/trl — grpo.py script
- **URL**: https://github.com/huggingface/trl/blob/main/trl/scripts/grpo.py
- **Relevance**: Production GRPO training script with CLI
- **Key patterns**: `accuracy_reward`, `reasoning_accuracy_reward` reward function registry; `get_dataset()` for dataset loading
- **Used For**: Training script structure reference

**Repository 3**: modal-labs/modal-examples — grpo_trl.py
- **URL**: https://github.com/modal-labs/modal-examples/blob/main/06_gpu_and_ml/reinforcement-learning/grpo_trl.py
- **Relevance**: Execution reward for coding with sandbox isolation
- **Key Code**:
  ```python
  def compute_reward(completion: str, testcase: Sequence[str]) -> int:
      # Sandboxed execution; return 1 if returncode == 0, else 0
  ```
- **Dataset**: OpenCoder-LLM/opc-sft-stage2 educational_instruct
- **Used For**: Execution reward pattern (binary pass/fail)

**Repository 4**: policy-gradient/GRPO-Zero
- **URL**: https://github.com/policy-gradient/GRPO-Zero
- **Relevance**: Minimal GRPO from scratch — confirms advantage computation formula
- **Key insight**: `A[t] = (r - mean) / std` per group; token-level policy gradient
- **Used For**: Confirming GRPO advantage normalization for KL budget understanding

**Source 5**: arxiv 2404.08817 — AST Edit Distance paper
- **URL**: https://arxiv.org/abs/2404.08817
- **Relevance**: Validates zss/TSED AST edit distance as effective structural metric for code
- **Used For**: Validating AST edit distance metric for H-M1 structural reallocation measurement

**Source 6**: arxiv 2002.08653 — FA-AST (Flow-Augmented AST)
- **URL**: https://arxiv.org/pdf/2002.08653
- **Relevance**: Control-flow and data-flow edge taxonomy for AST node classification
- **Node taxonomy extracted**:
  - Control-flow: If, For, While, Try, With, ExceptHandler
  - Data-flow: Assign, AugAssign, AnnAssign, Call, Return, Yield, FunctionDef
  - Surface: Constant, Name, Expr, Pass, comments
- **Used For**: AST node decomposition taxonomy (core to H-M1 mechanism)

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. TRL GRPOTrainer API is well-documented; AST decomposition uses Python stdlib `ast` module with straightforward node type inspection.

### D. Previous Hypothesis Context

**Source**: H-E1 validation results (verification_state.yaml)
- **Reused Components**:
  - Dataset: HumanEval+ / MBPP+ — proven stable, 542 problems
  - Training infrastructure: TRL GRPOTrainer + DPOTrainer on DeepSeek-Coder-7B-instruct-v1.5
  - AST edit distance: zss library implementation validated
  - KL matching: 27 checkpoint pairs at tolerance=0.15 confirmed feasible
- **Why Reused**: Enables controlled comparison — only analysis layer (AST decomposition) changes; training conditions identical to H-E1

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HumanEval+/MBPP+) | Phase 2B + H-E1 continuation | 02b_verification_plan.md §1.3; H-E1 validated |
| Dataset loading (evalplus) | Exa web search | evalplus/evalplus GitHub + HuggingFace |
| Model (DeepSeek-Coder-7B-instruct-v1.5) | Phase 2B + H-E1 continuation | 02b_verification_plan.md §1.3; H-E1 proven |
| Model loading code | Exa web search | huggingface.co/deepseek-ai/deepseek-coder-7b-instruct-v1.5 |
| GRPO training (TRL) | Exa GitHub | huggingface/trl GRPOTrainer |
| DPO training (TRL) | Exa GitHub | huggingface/trl DPOTrainer |
| Execution reward pattern | Exa GitHub | modal-labs/modal-examples grpo_trl.py |
| AST node decomposition taxonomy | Exa arXiv | arxiv 2002.08653 (FA-AST) |
| AST edit distance validation | Exa arXiv | arxiv 2404.08817 |
| Mann-Whitney U test | Domain knowledge | scipy.stats.mannwhitneyu |
| Spearman ρ | Domain knowledge | scipy.stats.spearmanr |
| GRPO advantage formula | Exa GitHub | policy-gradient/GRPO-Zero |
| Training hyperparameters | H-E1 continuation | H-E1 validation report (verification_state.yaml) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-19T09:09:09Z

### Workflow History for This Hypothesis
- 2026-05-19T09:09:09Z: H-M1 set to IN_PROGRESS (hypothesis loop starting Phase 2C → 3 → 4)
- 2026-05-19 (Phase 2C): Experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain match), Exa (GitHub + arXiv — primary source), Serena (skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
