# Logic Design: H-C1
# Scale Attenuation of SFT Source Identity Effect

**Date:** 2026-08-02
**Phase:** 3 — Implementation Planning
**Hypothesis Type:** CONDITION / SHOULD_WORK

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new training experiment; no existing codebase to extend
**Analyzed Path**: N/A
**Relevant Symbols**: None — H-C1 is a training orchestration experiment, not a library extension

---

## Constants and Data Structures

```python
# Shared across all scripts
SOURCE_CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
SEEDS = [42, 123, 777]
MODEL_ID = "deepseek-ai/deepseek-coder-7b-base"
BENCHMARKS = ["humaneval", "mbpp"]

# results.json schema
ResultsDict = dict[
    str,  # condition: "humaneval_only" | "mbpp_only" | "leetcode_only" | "equal_mix"
    dict[
        str,  # benchmark: "humaneval" | "mbpp"
        list[float]  # pass@1 per seed, len=3; e.g. [0.326, 0.331, 0.319]
    ]
]
# Example:
# {
#   "humaneval_only": {"humaneval": [0.51, 0.53, 0.50], "mbpp": [0.38, 0.37, 0.39]},
#   ...
#   "eta_sq_7b": {"humaneval": 0.42, "mbpp": 0.38},
#   "eta_sq_1b": {"humaneval": 0.83, "mbpp": 0.79},
#   "gate_verdict": "PASS"
# }
```

---

## A-1: train.py [Complexity: 2, Budget: 3]

**Applied**: TRL SFTTrainer + HuggingFace datasets

### API Signatures

```python
def load_equalized_source_dataset(
    condition: str,                          # one of SOURCE_CONDITIONS
    data_dir: str = "data/h-c1/",
) -> Dataset:
    """Load post-dedup, token-equalized training JSONL for one source condition."""
    # Returns HuggingFace Dataset with columns: {"prompt": str, "completion": str}
    # Dataset size: 150–374 rows after dedup and oversampling to token budget

def build_sft_config(
    condition: str,
    seed: int,
    output_base: str = "outputs/h-c1/",
) -> SFTConfig:
    """Return SFTConfig for one condition/seed run."""
    # output_dir = f"{output_base}/{condition}_seed{seed}"

def train_one_run(
    condition: str,
    seed: int,
    output_base: str = "outputs/h-c1/",
    data_dir: str = "data/h-c1/",
    use_lora: bool = False,         # fallback if OOM; document if used
) -> str:
    """SFT one model. Returns checkpoint path."""

def run_all_training(
    output_base: str = "outputs/h-c1/",
    data_dir: str = "data/h-c1/",
    use_lora: bool = False,
    skip_existing: bool = True,     # resume: skip if checkpoint exists
) -> dict[str, str]:
    """Train all 12 runs. Returns {f'{condition}_seed{seed}': checkpoint_path}."""
```

### Pseudo-code: train_one_run

```
1. dataset = load_equalized_source_dataset(condition, data_dir)
2. set_seed(seed)
3. cfg = SFTConfig(
       output_dir=f"{output_base}/{condition}_seed{seed}",
       num_train_epochs=3,
       per_device_train_batch_size=4,
       gradient_accumulation_steps=8,   # effective batch = 32
       learning_rate=2e-5,
       lr_scheduler_type="cosine",
       warmup_ratio=0.03,
       bf16=True,
       seed=seed,
       max_seq_length=2048,
       dataset_text_field="text",       # formatted prompt+completion
       save_strategy="epoch",
       load_best_model_at_end=False,
   )
4. model = AutoModelForCausalLM.from_pretrained(
       MODEL_ID, torch_dtype=bfloat16, device_map="auto",
       attn_implementation="flash_attention_2"
   )
   if use_lora:
       model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, task_type="CAUSAL_LM"))
       # ponytail: LoRA changes fine-tuning regime vs H-E2; document in validation report if triggered
5. trainer = SFTTrainer(model=model, args=cfg, train_dataset=dataset)
6. trainer.train()
7. trainer.save_model(cfg.output_dir + "/final")
8. return cfg.output_dir + "/final"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | load_equalized_source_dataset | Load JSONL, apply prompt template, return HF Dataset |
| L-1-2 | train_one_run | SFTTrainer setup and training |
| L-1-3 | run_all_training | Loop 4 conditions × 3 seeds with skip-existing |

---

## A-2: evaluate.py [Complexity: 2, Budget: 3]

**Applied**: EvalPlus v0.3.1 subprocess interface

### API Signatures

```python
def evalplus_evaluate(
    model_path: str,                # path to saved HF checkpoint
    benchmark: str,                 # "humaneval" | "mbpp"
    backend: str = "hf",
    greedy: bool = True,
) -> float:
    """Run EvalPlus subprocess, parse pass@1. Returns float in [0, 1]."""
    # Subprocess: evalplus.evaluate --model {model_path} --dataset {benchmark}
    #             --backend {backend} [--greedy]
    # Parses stdout JSON: {"pass@1": float}

def evaluate_all_models(
    checkpoint_map: dict[str, str],  # {f'{condition}_seed{seed}': path}
    output_file: str = "outputs/h-c1/results_raw.json",
    skip_existing: bool = True,
) -> ResultsDict:
    """Evaluate all 12 checkpoints × 2 benchmarks = 24 evaluations.
    Returns nested dict {condition: {benchmark: [pass@1 x 3 seeds]}}."""

def parse_evalplus_output(stdout: str) -> float:
    """Extract pass@1 from evalplus stdout JSON. Returns float."""
    # Parses: {"pass@1": 0.512, ...} → 0.512
```

### Pseudo-code: evaluate_all_models

```
1. results = defaultdict(lambda: defaultdict(list))
2. for condition in SOURCE_CONDITIONS:
       for seed in SEEDS:
           key = f"{condition}_seed{seed}"
           path = checkpoint_map[key]
           for benchmark in BENCHMARKS:
               cache_key = f"{key}_{benchmark}"
               if skip_existing and cache_key in existing_results:
                   results[condition][benchmark].append(existing_results[cache_key])
                   continue
               pass1 = evalplus_evaluate(path, benchmark, greedy=True)
               results[condition][benchmark].append(pass1)
3. save_json(dict(results), output_file)
4. return results
```

### Data shapes

| Variable | Shape / Type | Note |
|----------|-------------|------|
| results[condition][benchmark] | list[float], len=3 | Pass@1 per seed |
| Total evaluations | 4 × 3 × 2 = 24 | float values in [0, 1] |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | evalplus_evaluate | Subprocess call + stdout parse |
| L-2-2 | parse_evalplus_output | JSON extraction from evalplus stdout |
| L-2-3 | evaluate_all_models | Loop + cache + save results_raw.json |

---

## A-3: analyze.py [Complexity: 3, Budget: 4]

**Applied**: scipy.stats.f_oneway for ANOVA; η² = SS_between / SS_total

### η² Formula

```
η² = SS_between / SS_total

where:
  SS_total   = sum((x_ij - grand_mean)²)  for all observations
  SS_between = sum(n_j * (mean_j - grand_mean)²)  for each condition j
  SS_within  = SS_total - SS_between

Equivalently from F-statistic (for reference calculation):
  η² ≈ (F * df_between) / (F * df_between + df_within)
  H-E2 reference: F=11.37, df_between=3, df_within=8
  → η²_1b ≈ (11.37 * 3) / (11.37 * 3 + 8) = 34.11 / 42.11 ≈ 0.810
  (Note: brief cites ~0.83; use direct SS calculation from H-E2 raw data if available)
```

### API Signatures

```python
def compute_eta_squared(
    values_by_condition: dict[str, list[float]],  # {condition: [pass@1 x 3]}
) -> float:
    """One-way ANOVA eta-squared. Returns η² in [0, 1]."""
    # Uses scipy.stats.f_oneway internally for F-stat; computes SS directly

def load_h_e2_results() -> dict[str, dict[str, list[float]]]:
    """Load H-E2 pass@1 results (1.3B) for eta-squared reference.
    Returns same ResultsDict schema as evaluate_all_models."""
    # Reads from docs/youra_research/h-e2/results.json or hardcoded H-E2 values:
    # humaneval: humaneval_only=[0.326,...], leetcode_only=[0.030,...],
    #            mbpp_only=[0.277,...], equal_mix=[0.098,...]
    # mbpp: values from H-E2 if available; else None (analysis skips that benchmark)

def compare_scales(
    eta_sq_7b: dict[str, float],    # {"humaneval": float, "mbpp": float}
    eta_sq_1b: dict[str, float],    # {"humaneval": float, "mbpp": float}
) -> dict:
    """Evaluate gate condition. Returns gate dict."""
    # Returns:
    # {
    #   "humaneval_attenuated": bool,   # eta_sq_7b["humaneval"] < eta_sq_1b["humaneval"]
    #   "mbpp_attenuated": bool,
    #   "gate_verdict": "PASS" | "NULL",  # PASS if any benchmark attenuated
    #   "eta_sq_7b": eta_sq_7b,
    #   "eta_sq_1b": eta_sq_1b,
    #   "cohens_f_7b": dict[str, float],  # sqrt(η² / (1 - η²)) per benchmark
    # }

def run_full_analysis(
    results_7b: ResultsDict,
    h_e2_results_path: str = "docs/youra_research/h-e2/results.json",
    output_file: str = "outputs/h-c1/results.json",
) -> dict:
    """Full analysis pipeline. Returns and saves final results.json."""

def verify_h_c1_mechanism(
    results_7b: ResultsDict,
    results_1b: ResultsDict,
) -> tuple[bool, dict]:
    """Verify scale attenuation is measurable. Returns (all_complete, indicators)."""
    # Exact implementation as specified in experiment brief (see below)
```

### verify_h_c1_mechanism (verbatim from experiment brief)

```python
def verify_h_c1_mechanism(results_7b, results_1b):
    """Verify scale attenuation is measurable."""
    indicators = {}
    for benchmark in ["humaneval", "mbpp"]:
        all_complete = all(
            len(results_7b[cond][benchmark]) == 3
            for cond in ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
        )
        indicators[f"{benchmark}_complete"] = all_complete

        condition_means_7b = [np.mean(results_7b[cond][benchmark]) for cond in results_7b]
        var_7b = np.var(condition_means_7b)
        condition_means_1b = [np.mean(results_1b[cond][benchmark]) for cond in results_1b]
        var_1b = np.var(condition_means_1b)

        indicators[f"{benchmark}_attenuation"] = var_7b < var_1b
        indicators[f"{benchmark}_var_7b"] = var_7b
        indicators[f"{benchmark}_var_1b"] = var_1b

    return all(indicators[k] for k in indicators if "_complete" in k), indicators
```

### Pseudo-code: compute_eta_squared

```
1. groups = list(values_by_condition.values())   # list of lists, each len=3
   # groups shape: 4 conditions × 3 seeds
2. all_vals = flatten(groups)                    # len=12
3. grand_mean = mean(all_vals)
4. ss_between = sum(len(g) * (mean(g) - grand_mean)**2 for g in groups)
5. ss_total = sum((x - grand_mean)**2 for x in all_vals)
6. eta_sq = ss_between / ss_total
7. # Sanity check via scipy: f_stat, p_val = f_oneway(*groups)
8. return eta_sq
```

### Pseudo-code: run_full_analysis

```
1. results_1b = load_h_e2_results(h_e2_results_path)
2. for benchmark in BENCHMARKS:
       vals_7b = {c: results_7b[c][benchmark] for c in SOURCE_CONDITIONS}
       vals_1b = {c: results_1b[c][benchmark] for c in SOURCE_CONDITIONS
                  if results_1b[c].get(benchmark)}  # H-E2 may have partial data
       eta_7b[benchmark] = compute_eta_squared(vals_7b)
       eta_1b[benchmark] = compute_eta_squared(vals_1b) if len(vals_1b)==4 else H_E2_REF[benchmark]
3. gate = compare_scales(eta_7b, eta_1b)
4. complete_ok, indicators = verify_h_c1_mechanism(results_7b, results_1b)
5. final = {**results_7b, "eta_sq_7b": eta_7b, "eta_sq_1b": eta_1b,
            "gate": gate, "mechanism_indicators": indicators}
6. save_json(final, output_file)
7. return final
```

### H-E2 η² Reference Calculation

```python
# From H-E2 ANOVA: F=11.37, df_between=3, df_within=8
# η² ≈ (F × df_between) / (F × df_between + df_within)
H_E2_REF_ETA_SQ = {
    "humaneval": (11.37 * 3) / (11.37 * 3 + 8),  # ≈ 0.810
    # H-E2 brief cites ~0.83; use direct SS calc from raw data if available
}
# ponytail: if H-E2 raw per-seed pass@1 is available, compute SS directly for accuracy
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_eta_squared | SS-based ANOVA η² from condition groups |
| L-3-2 | load_h_e2_results | Load H-E2 JSON or fall back to hardcoded reference values |
| L-3-3 | compare_scales | Gate verdict + Cohen's f computation |
| L-3-4 | run_full_analysis | Orchestrate analysis, save results.json |

---

## A-4: figures.py [Complexity: 2, Budget: 3]

**Applied**: matplotlib / seaborn standard plotting

### API Signatures

```python
def plot_eta_sq_comparison(
    eta_sq_7b: dict[str, float],    # {"humaneval": float, "mbpp": float}
    eta_sq_1b: dict[str, float],
    out_path: str = "docs/youra_research/h-c1/figures/eta_sq_comparison.png",
) -> None:
    """Grouped bar chart: η² at 1.3B vs 7B per benchmark. MANDATORY figure."""

def plot_pass1_by_condition_scale(
    results_7b: ResultsDict,
    results_1b: ResultsDict,
    out_path: str = "docs/youra_research/h-c1/figures/pass1_by_condition_scale.png",
) -> None:
    """Grouped bar chart: mean pass@1 per condition × scale × benchmark.
    x-axis: SOURCE_CONDITIONS; bars: 1.3B vs 7B; facets: humaneval / mbpp."""

def plot_seed_variance_7b(
    results_7b: ResultsDict,
    out_path: str = "docs/youra_research/h-c1/figures/seed_variance_7b.png",
) -> None:
    """Box plots of pass@1 across 3 seeds per condition at 7B.
    x-axis: SOURCE_CONDITIONS; two panels: humaneval / mbpp."""

def plot_scale_attenuation_scatter(
    eta_sq_7b: dict[str, float],
    eta_sq_1b: dict[str, float],
    out_path: str = "docs/youra_research/h-c1/figures/scale_attenuation_scatter.png",
) -> None:
    """Scatter: x=η²_1.3B, y=η²_7B; one point per benchmark.
    Diagonal y=x line = no attenuation reference."""

def generate_all_figures(
    results_7b: ResultsDict,
    results_1b: ResultsDict,
    eta_sq_7b: dict[str, float],
    eta_sq_1b: dict[str, float],
    figures_dir: str = "docs/youra_research/h-c1/figures/",
) -> None:
    """Generate and save all 4 required figures."""
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | plot_eta_sq_comparison | Mandatory bar chart η² at 2 scales |
| L-4-2 | plot_pass1_by_condition_scale + plot_seed_variance_7b | Pass@1 grouped bars + seed box plots |
| L-4-3 | plot_scale_attenuation_scatter + generate_all_figures | Scatter + orchestration |

---

## A-5: main.py [Complexity: 1, Budget: 2]

```python
def main(
    stage: str = "all",    # "train" | "evaluate" | "analyze" | "figures" | "all"
    output_base: str = "outputs/h-c1/",
    data_dir: str = "data/h-c1/",
    h_e2_results: str = "docs/youra_research/h-e2/results.json",
    use_lora: bool = False,
    skip_existing: bool = True,
) -> None:
    """Orchestrate full H-C1 pipeline."""
    # 1. train:    run_all_training()        → checkpoint_map
    # 2. evaluate: evaluate_all_models()     → results_7b (ResultsDict)
    # 3. analyze:  run_full_analysis()       → final results.json
    # 4. figures:  generate_all_figures()    → 4 PNGs in figures/
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | main | CLI arg parsing + stage dispatch |
| L-5-2 | checkpoint verification | Verify all 12 checkpoints exist before evaluate stage |

---

## Total Subtask Count

| Script | Subtasks Used | Budget |
|--------|--------------|--------|
| train.py | 3 | 3 |
| evaluate.py | 3 | 3 |
| analyze.py | 4 | 4 |
| figures.py | 3 | 3 |
| main.py | 2 | 2 |
| **Total** | **15** | **15** |
