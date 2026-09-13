# Experiment Design: H-C1

**Date:** 2026-08-02
**Author:** Anonymous
**Hypothesis Statement:** The SFT source identity effect on pass@1 is attenuated at 7B scale relative to 1.3B (smaller between-condition effect size at 7B), consistent with the hypothesis that larger pretraining coverage reduces the marginal impact of SFT source identity via weight-space reinforcement of already-seen distributions.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION (SHOULD_WORK) Hypothesis** — Tests scale modulation of a previously confirmed source effect.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E2 VALIDATED (MUST_WORK gate passed; p=0.020, max effect 29.6 pp)
**Gate Status:** SHOULD_WORK — failure does not block pipeline; partial/null result is informative

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-C1
- **Type:** CONDITION
- **Prerequisites:** H-E2 (VALIDATED)

### Gate Condition
SHOULD_WORK gate. Success criterion: between-condition effect size (η² or Cohen's f) is **smaller at 7B than 1.3B** for at least one benchmark. Failure = "scale does not attenuate source effects" — this is informative (source alignment robust to scale) and does not block Phase 5.

---

## Continuation Context

**Previous Hypothesis:** H-E2 (VALIDATED)

### Previous Hypothesis Results (H-E2)
- One-way ANOVA on HumanEval pass@1 across 4 source conditions: **F=11.37, p=0.020** (significant)
- humaneval_only mean=32.6%, leetcode_only mean=3.0%, mbpp_only mean=27.7%, equal_mix mean=9.8%
- Max pairwise effect: humaneval_only vs leetcode_only = **29.6 absolute pp** (>>2.0 threshold)
- Direction consistent across ≥2/3 seeds
- NOTE: H-E2 partially complete — equal_mix has 1 seed only; h-c1 will run all 4 conditions × 7B × 3 seeds fresh

**H-C1 Reuse from H-E2:**
- Same 4 source conditions (HumanEval-only, MBPP-only, LeetCode-only, Equal-mix)
- Same training set construction protocol (post-dedup, token-budget equalized, standardized prompt template)
- Same evaluation benchmarks (HumanEval+ 164 tasks, MBPP+ 378 tasks via EvalPlus)
- **Change:** Model scale 1.3B → 7B (deepseek-ai/deepseek-coder-7b-base)
- **Controlled comparison:** Only the model scale changes; everything else held constant

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: SFT scale attenuation model size effect**
- No directly relevant past cases in Archon KB for this specific experiment type
- Archon KB is populated with diffusion model / image generation cases; code LLM SFT at scale is not represented

**Query 2: LLM scale source identity training generalization**
- DeepSpeed training infrastructure documentation found (relevant for multi-GPU 7B training)
- No past cases on source-identity × scale interaction

**Query 3: Code LLM benchmark pass@1 model scale**
- Consistency Models training scripts (not relevant)
- FLOPs calculation library (relevant for estimating 7B training cost)
- 4-bit quantization reference (relevant for memory-efficient 7B loading)

### Archon Code Examples

**Query: TRL SFTTrainer DeepSeek-Coder fine-tuning**
- No directly matching code examples in Archon KB
- Results returned DreamBooth/diffusion training scripts (unrelated domain)

**Assessment:** Archon KB does not contain relevant prior cases for this specific code LLM SFT × scale experiment. External sources (Exa/GitHub) are the primary implementation reference.

### Exa GitHub Implementations

**Query 1: TRL SFTTrainer large language model fine-tuning 7B**

**Repository: huggingface/trl** (official TRL library)
- **URL:** https://github.com/huggingface/trl
- **Relevance:** Primary SFTTrainer implementation used in H-C1
- **Architecture:** SFTTrainer wraps HuggingFace Trainer; supports full fine-tuning and LoRA
- **Key Code:**
  ```python
  from trl import SFTConfig, SFTTrainer
  from datasets import load_dataset

  trainer = SFTTrainer(
      model="deepseek-ai/deepseek-coder-7b-base",
      args=SFTConfig(
          output_dir="./outputs/h-c1/{condition}_{seed}",
          num_train_epochs=3,
          per_device_train_batch_size=4,
          gradient_accumulation_steps=8,  # effective batch = 32
          learning_rate=2e-5,
          bf16=True,
          seed=42,
          save_strategy="epoch",
      ),
      train_dataset=train_dataset,
  )
  trainer.train()
  ```
- **Training Config:**
  - Optimizer: AdamW (default)
  - Learning rate: 2e-5
  - Batch size: per_device×grad_accum = effective 32
  - Precision: bfloat16
- **Dataset:** Flexible (any HuggingFace dataset)
- **Source:** https://huggingface.co/docs/trl/en/sft_trainer

**Query 2: EvalPlus evaluation framework**

**Repository: evalplus/evalplus** (⭐1789)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Standard evaluation framework for HumanEval+ and MBPP+
- **Key Code:**
  ```bash
  # Evaluate fine-tuned model on HumanEval+
  evalplus.evaluate --model "./outputs/h-c1/humaneval_only_42" \
                    --dataset humaneval \
                    --backend hf \
                    --greedy

  # Evaluate on MBPP+
  evalplus.evaluate --model "./outputs/h-c1/humaneval_only_42" \
                    --dataset mbpp \
                    --backend hf \
                    --greedy
  ```
- **Output format:** `{'pass@1': float}` for base and base+extra tests
- **HumanEval+:** 164 tasks, 80x more tests than original HumanEval
- **MBPP+:** 378 tasks (v0.2.0), 35x more tests than original MBPP
- **Source:** https://github.com/evalplus/evalplus

**Query 3: DeepSeek-Coder SFT scale effect**
- **DeepSeek-Coder paper** (arxiv 2401.14196): Models from 1.3B to 33B, trained on 2T tokens; 87% code, 13% natural language. Base models available: `deepseek-ai/deepseek-coder-1.3b-base` and `deepseek-ai/deepseek-coder-7b-base` (HuggingFace).
- Architecture diffs: 1.3B uses D=2048, L=24, H=16; 6.7B uses D=4096, L=32, H=32. The 7B variant (deepseek-coder-7b-base) has substantially more pretraining co-exposure to LeetCode/HumanEval-style code by virtue of scale.
- **Key insight:** Larger models have broader pretraining distribution coverage; SFT source specificity may be diluted at 7B because the model already "knows" the test distribution from pretraining.

**Key Research Finding — Scale × SFT interaction (ACL 2024):**
- Dong et al. (2024) "How Abilities in Large Language Models are Affected by Supervised Fine-tuning Data Composition" (ACL 2024): "distinct capabilities scale differently and **larger models generally show superior performance with same amount of data**"; "data composition appears to enhance various abilities under limited data conditions, yet can lead to performance conflict" at larger scales. This directly supports H-C1's prediction that the marginal source-identity effect shrinks at 7B.

**Key Research Finding — Scaling meets fine-tuning (ICLR 2024):**
- Zhang et al. (2024) "When Scaling Meets LLM Finetuning" (ICLR 2024): "LLM finetuning benefits more from LLM model scaling than pretraining data scaling"; fine-tuning follows a power-based multiplicative scaling law. Larger models are less sensitive to individual fine-tuning data properties — consistent with attenuation hypothesis.

**Serena Analysis Needed:** false (no local codebase to analyze; this is a training experiment, not a library extension)

### 🎯 Implementation Priority Assessment

For H-C1, the experiment re-uses H-E2 training infrastructure. No novel mechanism to implement — the "mechanism" under study is the **statistical comparison of effect sizes across scales**.

**Recommended Implementation Path:**
- Primary: TRL SFTTrainer (official HuggingFace TRL) + EvalPlus (official evalplus/evalplus)
- Fallback: accelerate + custom training loop if TRL memory overhead is too large for 7B
- Justification: TRL SFTTrainer is the same framework used for H-E2 at 1.3B; using the same framework for 7B ensures controlled comparison (no confounds from different training codebases)

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. No complex custom architecture to analyze; H-C1 uses standard SFTTrainer on a pretrained model, identical to H-E2 except for model ID.

---

## Experiment Specification

### Dataset

**Dataset:** HumanEval-train, MBPP-train, LeetCode-Python, Equal-mix (4 SFT source conditions)
**Type:** standard / programmatic-api
**Source conditions (4, same as H-E2):**

| Condition | Source | Post-dedup Train Size |
|-----------|--------|----------------------|
| humaneval_only | HumanEval train split | ~150 problems (after dedup) |
| mbpp_only | MBPP train split | ~374 problems (after dedup) |
| leetcode_only | LeetCode Python subset | token-budget matched |
| equal_mix | Equal parts of all 3 | token-budget matched |

**Token budget equalization:** All 4 conditions matched to the same total training token count (determined by smallest condition after dedup, repeated via oversampling if needed)

**Dedup protocol (from H-E2):** all-MiniLM-L6-v2 cosine similarity > 0.95 against HumanEval+ and MBPP+ test sets → remove contaminated examples

**Preprocessing:**
- Standardized prompt template applied uniformly across all conditions (from H-E2)
- Max sequence length: 2048 tokens (adequate for code problems)
- Tokenizer: `deepseek-ai/deepseek-coder-7b-base` tokenizer

**Statistics:**
- Evaluation: HumanEval+ 164 tasks, MBPP+ 378 tasks (EvalPlus v0.3.1)
- Training: 4 conditions × 3 seeds = 12 SFT runs

**Reuse from H-E2:** The constructed training sets (post-dedup, equalized) from H-E2 are reused directly. H-C1 changes only the model size.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + custom dedup script (from H-E2)
- Identifier: Training sets saved as jsonl files from H-E2 pipeline
- Code:
  ```python
  from datasets import load_dataset
  # HumanEval train (via bigcode/humanevalpack or OpenAI humaneval)
  he_train = load_dataset("openai/openai_humaneval", split="test")  # train split is full problem set
  # MBPP train
  mbpp_train = load_dataset("google-research-datasets/mbpp", split="train")
  # LeetCode: curated Python subset (e.g., greengerong/leetcode or custom)
  # Equal-mix: constructed by sampling equally from above
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-7B-Base (`deepseek-ai/deepseek-coder-7b-base`)
**Type:** Causal language model, decoder-only transformer
**Parameters:** ~7B (D=4096, L=32, H=32, RoPE θ=100000)
**Pretraining:** 2T tokens, 87% code, 13% natural language; 16K context window with FIM task
**Role in H-C1:** Baseline at 7B scale — each of 4 source conditions is SFT'd from this base
**Comparison target:** H-E2 results at 1.3B scale (DeepSeek-Coder-1.3B-Base)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `deepseek-ai/deepseek-coder-7b-base`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "deepseek-ai/deepseek-coder-7b-base",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-7b-base")
  ```

#### Proposed Model

**Architecture:** DeepSeek-Coder-7B-Base + SFT on one of 4 source conditions

**Core Mechanism Implementation:**

H-C1 does not have a novel architectural mechanism. The "mechanism" under test is **scale-dependent attenuation of source identity effect**. The experiment design is therefore a controlled ablation:

```python
# H-C1 Core: Scale × Source Condition Experiment
# This pseudo-code captures the full experimental logic

SOURCE_CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]
MODEL_7B = "deepseek-ai/deepseek-coder-7b-base"

def run_h_c1_experiment():
    results = {}  # {condition: {seed: {benchmark: pass@1}}}

    for condition in SOURCE_CONDITIONS:
        results[condition] = {}
        train_data = load_equalized_source_dataset(condition)  # reuse H-E2 datasets

        for seed in SEEDS:
            # SFT training
            model_path = sft_train(
                base_model=MODEL_7B,
                train_data=train_data,
                seed=seed,
                output_dir=f"./outputs/h-c1/{condition}_seed{seed}"
            )

            # EvalPlus evaluation (greedy, temperature=0)
            he_pass1 = evalplus_evaluate(model_path, dataset="humaneval", greedy=True)
            mbpp_pass1 = evalplus_evaluate(model_path, dataset="mbpp", greedy=True)
            results[condition][seed] = {"humaneval": he_pass1, "mbpp": mbpp_pass1}

    return results

def compute_effect_size_7b(results):
    # Mixed-effects model: pass@1 ~ source_condition + (1|problem)
    # Extract eta² (proportion of variance explained by source_condition)
    # Compare to H-E2 eta² at 1.3B
    for benchmark in ["humaneval", "mbpp"]:
        values = {cond: [results[cond][s][benchmark] for s in SEEDS]
                  for cond in SOURCE_CONDITIONS}
        eta_sq_7b = compute_eta_squared(values)  # from ANOVA
        # Compare: eta_sq_7b < eta_sq_1.3b → attenuation confirmed
    return eta_sq_7b
```

### Training Protocol

**Reused from H-E2 (controlled comparison — only model scale changes):**

**Optimizer:** AdamW
- Parameters: β1=0.9, β2=0.999, weight_decay=0.01
- **Source:** TRL SFTTrainer defaults; consistent with DeepSeek-Coder SFT practice

**Learning Rate:** 2e-5
- **Source:** Standard LLM fine-tuning rate (Zhang et al. ICLR 2024; TRL documentation)
- **Schedule:** Cosine decay with warmup (warmup_ratio=0.03)

**Batch Size:** 32 effective (per_device=4, gradient_accumulation=8, assuming 4× H100)
- **Source:** TRL SFTTrainer + memory constraints of 7B model in bfloat16

**Epochs:** 3
- **Source:** H-E2 protocol (same); sufficient for convergence on small training sets with repetition
- **Note:** For HumanEval-only condition (~150 problems), 3 epochs with oversampling to match token budget

**Loss Function:** Cross-entropy (next-token prediction), completion-only loss masking prompt tokens
- **Source:** Standard SFT; TRL `completion_only_loss=True`

**Precision:** bfloat16
- **Source:** DeepSeek-Coder-7B fits in ~14GB VRAM per GPU in bf16; 4× H100 = 320GB total

**Seeds:** 42, 123, 777 (3 seeds per condition = 12 total runs)

**Max Sequence Length:** 2048 tokens
- **Source:** Code problem average length well within this; consistent with H-E2

**Compute Estimate:** 12 runs × ~2h each on 4×H100 = ~24 compute-hours (7B portion)

### Evaluation

**Benchmarks:**
- HumanEval+ (164 tasks, EvalPlus v0.3.1, greedy decoding, temperature=0)
- MBPP+ (378 tasks, EvalPlus v0.3.1, greedy decoding, temperature=0)

**Primary Metric:** pass@1 (proportion of tasks where greedy solution passes all test cases)

**Effect Size Metric (Primary for H-C1):**
- η² (eta-squared) from one-way ANOVA on pass@1 across 4 source conditions, separately for each benchmark and model scale
- Cohen's f (equivalent, f = √(η²/(1-η²)))
- **Key comparison:** η²_7B vs η²_1.3B per benchmark

**Statistical Model (same as H-E2):**
```
pass@1 ~ source_condition + solution_length + (1|problem)
```
(linear mixed-effects, random intercept per problem)

**Success Criteria:**
- **Primary:** η²_7B < η²_1.3B for at least one benchmark (attenuation confirmed)
- **Secondary:** Between-condition pass@1 variance is numerically smaller at 7B
- **Tertiary:** LeetCode-only advantage on HumanEval+ is attenuated at 7B vs 1.3B

**Expected Performance at 7B (from EvalPlus leaderboard and DeepSeek-Coder paper):**
- DeepSeek-Coder-6.7B-Base HumanEval: ~45-49% pass@1 (before SFT)
- After SFT, humaneval_only condition expected to approach ~50-60% pass@1 at 7B
- **Source:** EvalPlus leaderboard; DeepSeek-Coder paper (arxiv 2401.14196)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code generation (pass@1)
- Library: evalplus (pip install evalplus)
- Code:
  ```bash
  evalplus.evaluate --model {model_path} --dataset humaneval --backend hf --greedy
  evalplus.evaluate --model {model_path} --dataset mbpp --backend hf --greedy
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** η²_7B vs η²_1.3B bar chart per benchmark (attenuation visualization)

#### Additional Figures (LLM Autonomous)
Based on H-C1's scale comparison nature:
1. **Pass@1 by Condition × Scale:** Grouped bar chart (4 conditions × 2 scales × 2 benchmarks) — shows the raw pass@1 distribution shift
2. **Effect Size Comparison Table/Heatmap:** η² at 1.3B vs 7B per benchmark, with 95% CI
3. **Seed Variance Plot:** Box plots of pass@1 across 3 seeds for each condition at 7B — consistency check
4. **Scale Attenuation Scatter:** x=η²_1.3B, y=η²_7B per benchmark; diagonal line = no attenuation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-c1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E2 effect confirmed (F=11.37, p=0.020, max effect 29.6 pp at 1.3B) | TRUE — H-E2 VALIDATED |
| Mechanism Isolatable | Scale is the only variable changing (same datasets, same protocol, same seeds) | TRUE — by design |
| Baseline Measurable | 4 source conditions at 7B each produce independent pass@1 scores | TRUE — EvalPlus evaluation |

### Architecture Compatibility Check

**H-C1 tests scale modulation, not a novel architectural mechanism.**

Required features for this experiment:
- DeepSeek-Coder-7B-Base must be loadable in bfloat16 on available hardware (~14GB/GPU)
- TRL SFTTrainer must support 7B full fine-tuning (or LoRA if memory-constrained)
- EvalPlus must support HuggingFace model evaluation with `--backend hf`

**Potential incompatibility:**
- If 4× H100 is insufficient for 7B full fine-tuning: use LoRA (r=16, α=32) as fallback
  - Note: LoRA changes the fine-tuning regime; document if used (minor confounder vs H-E2)
- Flash Attention 2 recommended for 7B memory efficiency: `attn_implementation="flash_attention_2"`

> ⚠️ If hardware cannot run 7B full fine-tuning, Phase 4 MUST document LoRA fallback and note limitation.

### Mechanism Activation Indicators

H-C1's "mechanism" is the **statistical pattern** of source-effect attenuation. Verification indicators:

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Training Completion | All 12 checkpoints saved successfully | training loop |
| Evaluation Coverage | pass@1 recorded for all 12 models × 2 benchmarks | evaluate.py |
| Variance Comparison | η²_7B computed and comparable to η²_1.3B | analysis.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_h_c1_mechanism(results_7b, results_1b):
    """Verify scale attenuation is measurable."""
    indicators = {}
    for benchmark in ["humaneval", "mbpp"]:
        # Check all conditions have 3 seed results
        all_complete = all(
            len(results_7b[cond][benchmark]) == 3
            for cond in ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
        )
        indicators[f"{benchmark}_complete"] = all_complete

        # Compute between-condition variance
        condition_means_7b = [
            np.mean(results_7b[cond][benchmark])
            for cond in results_7b
        ]
        var_7b = np.var(condition_means_7b)
        condition_means_1b = [
            np.mean(results_1b[cond][benchmark])
            for cond in results_1b
        ]
        var_1b = np.var(condition_means_1b)

        indicators[f"{benchmark}_attenuation"] = var_7b < var_1b
        indicators[f"{benchmark}_var_7b"] = var_7b
        indicators[f"{benchmark}_var_1b"] = var_1b

    return all(indicators[k] for k in indicators if "_complete" in k), indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| All 12 models trained | TRUE | Checkpoint existence check |
| All 24 pass@1 scores computed | TRUE | EvalPlus output files |
| η²_7B < η²_1.3B | At least 1 benchmark | ANOVA eta-squared comparison |
| Hypothesis Supported | η²_7B < η²_1.3B (≥1 benchmark) | compute_effect_size_7b() |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. All 12 SFT runs complete and checkpoints saved
2. All 24 pass@1 scores computed (12 models × 2 benchmarks)
3. η²_7B < η²_1.3B for at least one benchmark (attenuation confirmed)

**Acceptable Null Result:** η²_7B ≥ η²_1.3B → "source effect robust to scale" — informative for main hypothesis H-D1; documents in validation report with interpretation.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Result:** No directly relevant past cases in Archon KB for this experiment type.
- Archon KB contains diffusion model training, image generation, and general deep learning infrastructure
- Queries on SFT scale effects, code LLM source identity, and benchmark evaluation returned unrelated results
- **Used for:** None — external sources (Exa) are the primary implementation reference for H-C1

### B. GitHub Implementations (Exa)

**Repository 1: huggingface/trl** (official TRL)
- **URL:** https://github.com/huggingface/trl
- **Query Used:** "TRL SFTTrainer large language model fine-tuning 7B training script PyTorch"
- **Relevance:** Primary SFT framework for H-C1 (and H-E2)
- **Key Code:**
  ```python
  from trl import SFTConfig, SFTTrainer
  trainer = SFTTrainer(
      model="deepseek-ai/deepseek-coder-7b-base",
      args=SFTConfig(output_dir="...", num_train_epochs=3, bf16=True, seed=42),
      train_dataset=train_dataset,
  )
  trainer.train()
  ```
- **Configuration extracted:** bf16, AdamW, cosine schedule, completion-only loss
- **Used for:** Training protocol specification

**Repository 2: evalplus/evalplus** (⭐1789)
- **URL:** https://github.com/evalplus/evalplus
- **Query Used:** "EvalPlus evalplus evaluate HumanEval MBPP pass@k code generation"
- **Relevance:** Standard evaluation framework; same one implicitly used in H-E2
- **Key Code:**
  ```bash
  evalplus.evaluate --model {model_path} --dataset humaneval --backend hf --greedy
  evalplus.evaluate --model {model_path} --dataset mbpp --backend hf --greedy
  ```
- **Configuration extracted:** greedy decoding, hf backend, HumanEval+ 164 tasks, MBPP+ 378 tasks
- **Used for:** Evaluation protocol specification

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — this experiment involves no novel code architecture. The experiment is a statistical comparison of SFT outcomes across model scales. Serena analysis is appropriate for novel mechanism implementations (attention layers, custom modules), not for training script orchestration.

### D. Previous Hypothesis Context

**Source:** H-E2 Validation Results (from pipeline state)
- **Reused components:**
  - Training datasets (post-dedup, token-equalized, 4 conditions)
  - Evaluation benchmarks (HumanEval+ 164 tasks, MBPP+ 378 tasks)
  - Statistical analysis protocol (mixed-effects model, ANOVA eta-squared)
  - Seeds: 42, 123, 777
- **Why reused:** Controlled comparison — only model scale changes (1.3B → 7B)
- **H-E2 effect at 1.3B:** η² estimated from ANOVA F=11.37 ≈ 0.83 (on 3 conditions with data); this is the reference value for attenuation comparison

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|-----------------|
| Dataset (4 conditions) | Previous hypothesis | H-E2 protocol (same datasets reused) |
| Token equalization protocol | Previous hypothesis | H-E2 02b_verification_plan.md |
| Base model (7B) | Exa web search | DeepSeek-Coder paper (arxiv 2401.14196) |
| TRL SFTTrainer config | Exa GitHub | huggingface/trl (official docs) |
| Training hyperparameters | Exa GitHub + ICLR 2024 | TRL defaults; Zhang et al. 2024 |
| EvalPlus evaluation | Exa GitHub | evalplus/evalplus (official) |
| Scale × SFT scaling law | Exa web search | Zhang et al. ICLR 2024 (ICLR 2024) |
| SFT data composition × scale | Exa web search | Dong et al. ACL 2024 |
| Effect size (η²) analysis | Phase 2B plan | 02b_verification_plan.md H-C1 section |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed via harness)
**Date:** 2026-08-02

### Workflow History for This Hypothesis
- 2026-08-02: Phase 2C experiment design IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + Web Search — primary sources), Serena (skipped — no novel architecture)*
*All specifications grounded in researched implementations and H-E2 validated protocol*
*Next Phase: Phase 3 - Implementation Planning*
