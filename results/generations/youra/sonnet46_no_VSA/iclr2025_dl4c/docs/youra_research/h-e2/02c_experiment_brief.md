# Experiment Design: H-E2

**Date:** 2026-08-02
**Author:** Anonymous
**Hypothesis Statement:** SFT training source identity (HumanEval-only vs MBPP-only vs LeetCode-only vs Equal-mix) produces a statistically significant main effect on pass@1 for at least one source-benchmark pair at 1.3B scale, with minimum effect size ≥2.0 absolute percentage points in a linear mixed-effects model (source_condition fixed effect p < 0.05, Holm-Bonferroni corrected), consistent in direction across ≥2/3 seeds.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** true (H-E2 has no prerequisites)
**Gate Status:** MUST_WORK (gate not yet satisfied)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E2
- **Type:** EXISTENCE
- **Prerequisites:** none

### Gate Condition
MUST_WORK gate. If all pairwise contrasts fall within ±1.5 pp on both benchmarks across all seeds → gate FAILS → H-M1, H-M2, H-C1 all blocked; pipeline routes to Phase 0.

---

## Continuation Context

No prior hypothesis in this verification chain. H-E2 is one of two parallel EXISTENCE hypotheses (H-E1 runs embedding analysis independently). This is the primary training experiment.

### Previous Hypothesis Results (if applicable)
None — first training hypothesis in the chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: SFT training source dataset experiment design**
- Archon KB does not contain prior YouRA cases directly matching code-SFT source ablation experiments.
- Closest hits: TRL SFTTrainer documentation (HuggingFace), LoRA/PEFT guides.
- Key insight: TRL SFTTrainer is the standard tool for SFT on HuggingFace models; `completion_only_loss=True` is the correct mode for prompt-completion pairs (mask prompt tokens, only loss on solution body).
- Key insight: DeepSeek-Coder models are on HuggingFace as `deepseek-ai/deepseek-coder-1.3b-base` and `deepseek-ai/deepseek-coder-7b-base`.

**Query 2: SFT fine-tuning benchmark specialization challenges**
- No direct Archon KB hits on SFT source ablation. General best practices: standardize prompt template before any training run to eliminate format confound; mask prompt tokens to avoid inflating loss on repeated preamble.
- LoRA guide (HuggingFace PEFT): LoRA on key/value projections is standard for 1.3B code models; r=8, lora_alpha=16 typical.

**Query 3: HumanEval MBPP pass@1 benchmark**
- EvalPlus NeurIPS 2023 paper: HumanEval+ = 164 tasks with 80× more tests; MBPP+ = 378 tasks (v0.2.0) with 35× more tests. Greedy decoding is the standard evaluation mode. `evalplus.evaluate --greedy` is the CLI command.
- DeepSeek-Coder-V2 paper: Pre-training ablation at 1B shows HumanEval ~30–37% and MBPP ~45–54% baseline range for 1B-scale models trained on 1T–2T tokens. This establishes expected pass@1 range for our 1.3B SFT experiments.

### Archon Code Examples

**TRL SFTTrainer — Key Configuration (from HuggingFace TRL docs):**
```python
from trl import SFTTrainer, SFTConfig

config = SFTConfig(
    max_length=1024,
    completion_only_loss=True,   # mask prompt, loss on solution only
    packing=False,               # disable for variable-length code problems
    dataset_text_field="text",
)
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    args=config,
)
trainer.train()
```
- **Pattern:** `completion_only_loss=True` ensures loss computed only on the canonical solution, not the function signature/docstring prompt.
- **Insight:** Preserving indentation in `canonical_solution` is critical (no `.lstrip()`).

### Exa GitHub Implementations

**Repository 1: ESONG1999/Code_Agent_RL_Github**
- **URL:** https://github.com/ESONG1999/Code_Agent_RL_Github
- **Relevance:** Full SFT pipeline on `deepseek-ai/deepseek-coder-1.3b-base` with HumanEval evaluation
- **Key findings:**
  - Backbone: `deepseek-ai/deepseek-coder-1.3b-base`
  - SFT hyperparameters: `r=8`, `lora_alpha=16`, `lora_dropout=0.05`, `lr=5e-5`, `epochs=1`, `per_device_batch_size=1`, `gradient_accumulation_steps=8`
  - Masking: loss only on canonical solution (prompt tokens masked)
  - SFT alone: base 15.2% → 36.4% pass@1 on HumanEval-style tasks (+21.2 pp)
  - Evaluation on 33 HumanEval-style tasks; greedy decoding
- **Training Config:**
  - Optimizer: AdamW (via QLoRA + LoRA adapters)
  - Learning rate: 5e-5
  - Batch size: 1 per device, gradient_accumulation=8 (effective BS=8)
  - Epochs: 1.0
- **Note:** Uses QLoRA (4-bit quantization) for single GPU. Our experiment uses full SFT (5× H100), so no quantization needed; same LoRA config otherwise viable as reference.

**Repository 2: deepseek-ai/DeepSeek-Coder (Official)**
- **URL:** https://github.com/deepseek-ai/DeepSeek-Coder
- **Relevance:** Official DeepSeek-Coder fine-tuning script and evaluation setup
- **Key findings:**
  - Official fine-tuning script: `finetune/finetune_deepseekcoder.py`
  - Recommended hyperparameters: bf16=True, DeepSpeed ZeRO-3 config for multi-GPU
  - Evaluation: HumanEval + MBPP via greedy pass@1
  - 1.3B base model: `deepseek-ai/deepseek-coder-1.3b-base`
  - Pre-training composition: 87% code, 13% natural language; 2T tokens total
  - The 1.3B model achieves competitive HumanEval and MBPP scores

**Repository 3: evalplus/evalplus (Official)**
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Standard evaluation framework for HumanEval+ and MBPP+
- **Key findings:**
  - HumanEval+: 164 tasks (same as base HumanEval but 80× more test cases)
  - MBPP+: 378 tasks (v0.2.0, after removing broken tasks)
  - CLI: `evalplus.evaluate --model <hf_id> --dataset [humaneval|mbpp] --backend [hf|vllm] --greedy`
  - Datasets on HuggingFace: `evalplus/humanevalplus`, `evalplus/mbppplus`
  - Standard greedy decoding (temperature=0) for pass@1

**Serena Analysis Needed:** false — code from search results is sufficiently clear for pseudo-code generation.

### 🎯 Implementation Priority Assessment

For this experiment, there is no single "paper author implementation" to reproduce — H-E2 is a novel ablation study. Priority hierarchy:

1. **Official DeepSeek-Coder fine-tuning script** (deepseek-ai/DeepSeek-Coder): ground truth for model loading and training setup
2. **TRL SFTTrainer** (HuggingFace TRL docs): standard SFT framework, well-tested
3. **ESONG1999/Code_Agent_RL_Github**: reference for DeepSeek-Coder-1.3b SFT hyperparameters

**Recommended Implementation Path:**
- Primary: TRL SFTTrainer + deepseek-ai official finetune script patterns
- Fallback: HuggingFace Transformers Trainer directly
- Justification: TRL SFTTrainer handles completion_only_loss correctly out of the box; the official DeepSeek-Coder script provides validated bf16 + DeepSpeed ZeRO-3 multi-GPU configuration.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. TRL SFTTrainer and DeepSeek-Coder fine-tuning patterns are well-documented and do not require semantic analysis.

---

## Experiment Specification

### Dataset

**Training Sources (4 conditions):**

| Condition | Source Dataset | HuggingFace ID | Notes |
|-----------|---------------|----------------|-------|
| HumanEval-only | HumanEval train split | `openai/openai_humaneval` (train problems) | 164 problems; repeat epochs for token budget match |
| MBPP-only | MBPP sanitized | `google-research-datasets/mbpp` (sanitized, train split) | ~374 train problems |
| LeetCode-only | LeetCodeDataset | `newfacade/LeetCodeDataset` (Python subset) | 2,869 Python problems; post-dedup required |
| Equal-mix | 1/4 of each source | Combined | Proportional mixing of all 3 above |

**Test Benchmarks (evaluation only — NOT used for training):**

| Benchmark | Source | Problems | HuggingFace ID |
|-----------|--------|----------|----------------|
| HumanEval+ | EvalPlus | 164 | `evalplus/humanevalplus` |
| MBPP+ | EvalPlus | 378 | `evalplus/mbppplus` |

**Pre-experiment Data Preparation Steps:**
1. **Deduplication:** Remove any training problems with cosine similarity > 0.95 (all-MiniLM-L6-v2) against HumanEval+ and MBPP+ test sets
2. **Problem-count matching:** Downsample to equal number of problems across all 4 conditions (limited by HumanEval-only at ~164 post-dedup)
3. **Token-budget equalization:** Repeat smaller sets to equalize total training tokens across conditions (≥3 epochs for HumanEval-only)
4. **Format normalization:** Apply uniform prompt template: `"# Complete the following Python function:\n{docstring}\n{function_signature}"` across all sources

**Dataset Type:** standard (all real, established datasets)
**Dataset Path:** `auto` (HuggingFace download) + `./data/sft_sources/` after preprocessing

**Loading Information:**
- Method: HuggingFace `datasets`
- HumanEval-only: `load_dataset("openai/openai_humaneval")` then filter train problems
- MBPP-only: `load_dataset("google-research-datasets/mbpp", "sanitized")` then filter train split
- LeetCode-only: `load_dataset("newfacade/LeetCodeDataset")` Python subset
- HumanEval+: `from evalplus.data import get_human_eval_plus`
- MBPP+: `from evalplus.data import get_mbpp_plus`

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-1.3B-Base
**Type:** Decoder-only transformer (code-specialized)

**Loading Information:**
- Method: HuggingFace `transformers.AutoModelForCausalLM`
- Identifier: `deepseek-ai/deepseek-coder-1.3b-base`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-1.3b-base",
      trust_remote_code=True,
      torch_dtype=torch.bfloat16,
  )
  tokenizer = AutoTokenizer.from_pretrained(
      "deepseek-ai/deepseek-coder-1.3b-base",
      trust_remote_code=True,
  )
  ```

**Configuration:**
- Parameters: ~1.3B
- Architecture: Grouped-Query Attention, 16K window size
- Pretrained on 2T tokens (87% code, 13% natural language)
- Context length: 16K (we use max_length=2048 for SFT)

**Modifications for H-E2:** No architectural modifications — this is a pure SFT source ablation. The same base model is fine-tuned under 4 different data conditions.

#### Proposed Model

**Architecture:** Same as Baseline (no architectural change)
**Experiment Logic:** 4 independent SFT runs of the same 1.3B model on different source conditions × 3 seeds = 12 checkpoints total

**Core Mechanism Implementation:**

```python
# SFT Source Ablation: Training Data Construction
# Condition: one of {humaneval_only, mbpp_only, leetcode_only, equal_mix}
# Based on: TRL SFTTrainer (HuggingFace) + deepseek-ai/DeepSeek-Coder finetune script

def build_sft_dataset(condition: str, target_problems: int, target_tokens: int):
    """
    Args:
        condition: one of 4 source conditions
        target_problems: number of problems after dedup (≤164 for HumanEval-only)
        target_tokens: total token budget (equalized across conditions)
    Returns:
        HuggingFace Dataset with 'text' field = prompt + solution
    """
    # Step 1: Load raw source
    raw = load_source(condition)               # HumanEval / MBPP / LeetCode / mix

    # Step 2: Dedup against eval benchmarks
    deduped = dedup_against_eval(raw,
        benchmarks=["humaneval_plus", "mbpp_plus"],
        encoder="all-MiniLM-L6-v2",
        threshold=0.95)

    # Step 3: Subsample to target_problems
    sampled = deduped.shuffle(seed=42).select(range(target_problems))

    # Step 4: Apply uniform prompt template
    def format_example(ex):
        prompt = UNIFORM_TEMPLATE.format(
            docstring=ex["docstring"],
            signature=ex["function_signature"]
        )
        return {"text": prompt + ex["canonical_solution"]}

    # Step 5: Repeat to reach token budget
    formatted = sampled.map(format_example)
    return repeat_to_token_budget(formatted, target_tokens)


# Training loop (per condition, per seed)
trainer = SFTTrainer(
    model=model,
    args=SFTConfig(
        num_train_epochs=num_epochs,    # ≥3 for HumanEval-only
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,  # effective BS=16
        learning_rate=2e-5,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        bf16=True,
        completion_only_loss=True,      # mask prompt tokens
        max_length=2048,
        seed=seed,                      # iterate over [42, 123, 777]
    ),
    train_dataset=sft_dataset,
)
trainer.train()
```

### Training Protocol

**Optimizer:** AdamW
- Parameters: weight_decay=0.01, beta1=0.9, beta2=0.95
- Source: DeepSeek-Coder official fine-tuning script (bf16 + DeepSpeed ZeRO-3)

**Learning Rate:** 2e-5
- Schedule: Cosine decay with 5% warmup
- Source: Standard code SFT LR from TRL docs + DeepSeek-Coder finetune script range (1e-5 to 5e-5 typical)

**Batch Size:** 4 per device × 4 gradient accumulation = effective BS 16 (across 5× H100)
- Actual global effective BS: 16 × 5 GPUs = 80 sequences per step
- Source: Adapted from ESONG1999 reference (scaled up for multi-GPU)

**Epochs:** Variable per condition to equalize token budget
- HumanEval-only: ~5–8 epochs (repeat to match MBPP token budget)
- MBPP-only: ~3 epochs
- LeetCode-only: ~1 epoch (2,869 problems)
- Equal-mix: ~2–3 epochs
- Source: Token-budget equalization protocol from Phase 2B spec

**Loss Function:** Cross-entropy (completion_only_loss=True — solution tokens only)

**Max Sequence Length:** 2048 tokens

**Seeds:** 3 runs per condition — seeds: [42, 123, 777]

**Total Runs:** 4 conditions × 3 seeds = **12 SFT runs**

**Compute Estimate:** ~24 compute-hours on 5× H100 (per Phase 2B estimate)

**Infrastructure:**
- Framework: TRL SFTTrainer + Accelerate + DeepSpeed ZeRO-3
- Precision: bfloat16
- Model loading: `trust_remote_code=True`

### Evaluation

**Primary Metrics:**
- `pass@1` (greedy decoding, temperature=0) on HumanEval+ (164 tasks) and MBPP+ (378 tasks)
- Evaluated via EvalPlus: `evalplus.evaluate --dataset [humaneval|mbpp] --backend hf --greedy`

**Statistical Analysis:**
```
Model: pass@1 ~ source_condition + solution_length + (1|problem_id)
Fit via: statsmodels MixedLM (Python) or lme4 (R)
Fixed effects: source_condition (4-level factor), solution_length (covariate)
Random effects: (1|problem_id) — random intercept per problem
Pairwise contrasts: Holm-Bonferroni correction across C(4,2)=6 pairs
```

**Success Criteria (MUST_WORK gate):**
- Fixed effect of `source_condition`: p < 0.05 (Holm-Bonferroni corrected) for ≥1 benchmark
- Minimum pairwise contrast: ≥2.0 pp for ≥1 source-benchmark pair
- Direction consistent across ≥2/3 seeds (≥2 out of 3 seeds agree on sign of contrast)

**Falsification Criterion:**
- All pairwise contrasts within ±1.5 pp on both benchmarks across all seeds → H-E2 FAILS

**Expected Baseline Performance (from research):**
- DeepSeek-Coder-1.3B base pretrained: HumanEval ~15–30%, MBPP ~45% (from EvalPlus leaderboard and DeepSeek-Coder-V2 paper ablations at 1B scale)
- After SFT on ~164–2869 problems: expected +5–25 pp improvement (ESONG1999 shows +21 pp on HumanEval-style from SFT alone)

**Metrics Loading Information:**
- Task Type: code generation (pass@1)
- Library: EvalPlus (standard) + statsmodels for mixed-effects model
- EvalPlus code:
  ```bash
  evalplus.evaluate \
    --model ./checkpoints/condition_{cond}_seed_{seed} \
    --dataset humaneval \
    --backend hf \
    --greedy
  ```
- MixedLM code:
  ```python
  import statsmodels.formula.api as smf
  # results_df: columns [pass1, source_condition, solution_length, problem_id]
  md = smf.mixedlm(
      "pass1 ~ C(source_condition) + solution_length",
      results_df,
      groups=results_df["problem_id"]
  )
  mdf = md.fit()
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of pass@1 per source condition on HumanEval+ and MBPP+ (with error bars across 3 seeds)

#### Additional Figures (LLM Autonomous)
- **2×4 Transfer Matrix Heatmap:** Rows = 4 training sources, Columns = 2 test benchmarks, Cell = mean pass@1. This is the primary visualization showing the alignment pattern.
- **Seed Consistency Plot:** Strip plots showing per-seed pass@1 per condition per benchmark (demonstrates ≥2/3 seed consistency)
- **Mixed-Effects Model Coefficient Plot:** Forest plot of pairwise contrasts with 95% CI, Holm-Bonferroni corrected p-values
- **Token Budget Verification:** Bar chart confirming equalized training tokens across 4 conditions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all 12 SFT runs + all 24 evaluations complete)
2. At least one pairwise source-condition contrast ≥2.0 pp on ≥1 benchmark, direction consistent ≥2/3 seeds, mixed-effects p < 0.05 (Holm-Bonferroni)

---

## 🔬 Mechanism Verification Protocol

**Pre-conditions (verify before running all 12 seeds):**
- `mechanism_exists`: true — SFT source identity is a well-defined discrete manipulation
- `mechanism_isolatable`: true — token-budget equalization and format normalization remove confounds; only source identity varies
- `baseline_measurable`: true — DeepSeek-Coder-1.3B-base pretrained pass@1 on HumanEval+ and MBPP+ is measurable as zero-shot baseline

**Architecture Compatibility:**
- `architecture_compatibility`: CONFIRMED — DeepSeek-Coder-1.3B-Base is a standard causal LM; TRL SFTTrainer fully supports it with `trust_remote_code=True`. No custom layers required.

**Activation Indicators:**
- `mechanism_log_message`: "Training loss decreasing per condition; eval pass@1 at checkpoint > base model pass@1"
- `tensor_shape_change`: N/A — no architectural modification; mechanism is in training data, not model
- `metric_delta_expected`: ≥5 pp improvement over base model on the same-source benchmark (e.g., HumanEval-only trained model should show ≥5 pp over base on HumanEval+)

**Mechanism Verification Code:**
```python
# After each SFT run, verify mechanism activated (training improved over base)
BASE_HUMANEVAL = 0.15   # approximate DeepSeek-Coder-1.3B base pass@1
BASE_MBPP = 0.45

def verify_sft_activation(pass1_humaneval, pass1_mbpp, condition):
    he_improved = pass1_humaneval > BASE_HUMANEVAL + 0.03  # at least +3 pp over base
    mbpp_improved = pass1_mbpp > BASE_MBPP + 0.01
    print(f"[{condition}] HumanEval+ {pass1_humaneval:.3f} (base {BASE_HUMANEVAL}): {'✅' if he_improved else '⚠️'}")
    print(f"[{condition}] MBPP+ {pass1_mbpp:.3f} (base {BASE_MBPP}): {'✅' if mbpp_improved else '⚠️'}")
    return he_improved or mbpp_improved
```

**Failure Detection:**
- If all 4 conditions produce pass@1 within ±1.5 pp of each other → source effect absent → gate FAIL
- If SFT pass@1 < base model pass@1 → training diverged → abort and debug (LR too high, dedup removed all data)
- If any seed crashes OOM → reduce batch size or enable gradient checkpointing

**Success Criteria:**
- `hypothesis_support_threshold`: p < 0.05 (Holm-Bonferroni), min contrast ≥2.0 pp
- `hypothesis_support_metric`: source_condition fixed effect in MixedLM + pairwise contrasts

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1: TRL SFTTrainer Documentation (HuggingFace)**
- Type: Official documentation
- Query: "SFT fine-tuning benchmark specialization implementation challenges"
- Key insights: `completion_only_loss=True` for masking prompt tokens; `SFTConfig.packing=False` for code tasks
- Used for: Training protocol design, loss configuration

**Source A.2: HuggingFace PEFT/LoRA Guide**
- Type: Documentation
- Query: "SFT fine-tuning benchmark specialization implementation challenges"
- Key insights: LoRA r=8, lora_alpha=16, lora_dropout=0.05 typical for 1.3B code models
- Used for: Reference hyperparameter baseline (not used in main experiment — full SFT preferred for clean ablation)

**Source A.3: EvalPlus Paper (NeurIPS 2023) via Archon KB**
- Type: Paper abstract
- Query: "HumanEval MBPP pass@1 evaluation benchmark LLM code"
- Key insights: HumanEval+ = 164 tasks / 80× tests; MBPP+ = 378 tasks / 35× tests; greedy decoding standard
- Used for: Evaluation protocol, dataset size confirmation

### B. GitHub Implementations (Exa)

**Repository B.1: ESONG1999/Code_Agent_RL_Github**
- URL: https://github.com/ESONG1999/Code_Agent_RL_Github
- Query: "TRL SFTTrainer DeepSeek-Coder SFT training HumanEval MBPP code generation"
- Relevance: Exact same backbone (deepseek-coder-1.3b-base), SFT on HumanEval-style tasks, greedy pass@1 evaluation
- Key code basis for pseudo-code:
  ```python
  # From ESONG1999 reference
  # r=8, lora_alpha=16, lora_dropout=0.05
  # learning_rate=5e-5, num_train_epochs=1.0
  # per_device_train_batch_size=1, gradient_accumulation_steps=8
  # Objective: causal LM loss on prompt + canonical_solution, mask prompt tokens
  ```
- Configuration extracted: lr=5e-5 (our experiment scales to 2e-5 for full fine-tune without QLoRA)
- Their results: 15.2% → 36.4% SFT pass@1 (+21.2 pp) on HumanEval subset
- Used for: Training hyperparameter calibration, expected SFT improvement range

**Repository B.2: deepseek-ai/DeepSeek-Coder (Official)**
- URL: https://github.com/deepseek-ai/DeepSeek-Coder
- Query: "TRL SFTTrainer DeepSeek-Coder SFT training HumanEval MBPP code generation"
- Relevance: Official fine-tuning script; multi-GPU bf16 + DeepSpeed ZeRO-3 setup
- Configuration extracted: bf16=True, DeepSpeed ZeRO-3, `trust_remote_code=True`
- Used for: Model loading, multi-GPU training configuration

**Repository B.3: evalplus/evalplus (Official)**
- URL: https://github.com/evalplus/evalplus
- Query: "EvalPlus evalplus HumanEval+ MBPP+ evaluation pass@1 greedy decoding"
- Relevance: Standard evaluation framework; 164 HumanEval+ tasks, 378 MBPP+ tasks
- Key commands:
  ```bash
  evalplus.evaluate --model <checkpoint> --dataset humaneval --backend hf --greedy
  evalplus.evaluate --model <checkpoint> --dataset mbpp --backend hf --greedy
  ```
- Used for: Evaluation protocol

**Repository B.4: newfacade/LeetCodeDataset**
- URL: https://huggingface.co/datasets/newfacade/LeetCodeDataset
- Query: "LeetCode Python problems dataset HuggingFace SFT code training dataset"
- Relevance: Python LeetCode problems (2,869 total) for LeetCode-only training condition
- Loading: `load_dataset("newfacade/LeetCodeDataset")`
- Used for: LeetCode-only training condition data source

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. TRL SFTTrainer, DeepSeek-Coder fine-tuning, and EvalPlus are well-documented with explicit parameter specifications.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E2 is the first training hypothesis in the verification chain (no prior validated checkpoints to reuse).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Training source datasets | HuggingFace Datasets | B.4 (LeetCode), standard (HumanEval/MBPP) |
| Evaluation benchmarks | EvalPlus | B.3 |
| Model: DeepSeek-Coder-1.3B | Official | B.2 |
| SFT framework: TRL SFTTrainer | Archon KB | A.1 |
| Training hyperparameters | GitHub + Archon | B.1, A.1 |
| completion_only_loss | TRL docs | A.1 |
| Mixed-effects model | statsmodels docs | Exa web search |
| Expected performance range | Paper + GitHub | B.1, A.3 |
| Dedup protocol | Phase 2B spec | 02b_verification_plan.md |
| Token budget equalization | Phase 2B spec | 02b_verification_plan.md |
| Evaluation CLI commands | EvalPlus | B.3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — not written to file)
**Date:** 2026-08-02

### Workflow History for This Hypothesis
- H-E2 set to IN_PROGRESS: 2026-08-02T13:36:33+00:00
- Phase 2C experiment design: IN_PROGRESS → COMPLETED: 2026-08-02

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search), Serena (skipped — not needed)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 — Implementation Planning*
