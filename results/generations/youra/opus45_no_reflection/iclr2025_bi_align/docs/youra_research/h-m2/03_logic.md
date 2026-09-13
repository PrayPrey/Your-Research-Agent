# Logic: H-M2 (MECHANISM)

**Hypothesis:** BiDPO models generate responses with higher collaboration scores than DPO
**Type:** MECHANISM - inference-only comparison, no training, single run

Applied: No relevant KB pattern found (searched "DL API design patterns generation inference" — only unrelated diffusers/xDiT/LCM results); standard HF `generate()` + `scipy.stats.ttest_rel` paired-comparison pattern used (per architecture doc / experiment brief).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual code (Serena MCP had no active project registered; base code read directly via Read tool — same verification guarantee)
**Analyzed Path**: `docs/youra_research/h-m1/code/` (models.py, train.py, collab_score.py)
**Relevant Symbols**:
- `load_policy_model(model_name)` in `models.py` — loads bfloat16/device_map='auto' but is trainable (no `.eval()`). H-M2's `load_baseline_model`/`load_bidpo_model` must call `.eval()` explicitly for inference.
- `save_checkpoint(model, path)` in `train.py` — `torch.save(model.state_dict(), path)`, a **raw state_dict**, NOT `{"model_state_dict": ...}`. PRD FR-3 and 02c_experiment_brief.md code sample (`checkpoint["model_state_dict"]`) are **wrong** — confirmed by architecture doc's Codebase Analysis section too. H-M2 must load with `model.load_state_dict(torch.load(path, map_location="cpu"), strict=False)` directly.
- `compute_collab_score_v2(response)` in `collab_score.py` — identical across H-E1/H-M1, unbounded raw ratio, copy verbatim (no clipping needed here, unlike H-M1's training-time normalization).

---

## External Dependencies API

```python
# From: docs/youra_research/h-m1/code/collab_score.py (ACTUAL CODE, copy verbatim)
def compute_collab_score_v2(response: str) -> float:
    """Length-normalized collaboration score (unbounded, >= 0)."""
    ...

# From: docs/youra_research/h-m1/code/outputs/final.pt (ACTUAL CHECKPOINT FORMAT)
# Raw state_dict, saved via torch.save(model.state_dict(), path) in train.py.
# Load as:
bidpo_model.load_state_dict(torch.load("../h-m1/code/outputs/final.pt", map_location="cpu"), strict=False)
# NOT checkpoint["model_state_dict"] (PRD FR-3 is incorrect per verified train.py).
```

**Verified from**: `docs/youra_research/h-m1/code/{collab_score.py,train.py,models.py}` (read directly).

---

## M-1: Config + data + models [Complexity: 9, Budget: 2]

**Applied**: Standard `AutoModelForCausalLM.from_pretrained` + HF `datasets` load pattern (same as H-M1 models.py/data.py)

```python
# config.py
SEED: int = 42
BASELINE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_MODEL_BASE: str = "mistralai/Mistral-7B-Instruct-v0.2"
BIDPO_CHECKPOINT_PATH: str = "../h-m1/code/outputs/final.pt"
N_PROMPTS: int = 500
MAX_NEW_TOKENS: int = 256
TEMPERATURE: float = 0.7
TOP_P: float = 0.9
MAX_PROMPT_LENGTH: int = 768
OUTPUT_DIR: str = "outputs/"
FIGURES_DIR: str = "figures/"
RESULTS_PATH: str = "outputs/results.json"

# data.py
def load_hh_rlhf_prompts(n: int, seed: int) -> list[str]:
    """Load Anthropic/hh-rlhf test split, extract unique Human-turn prompts, sample n."""
    ...

def format_mistral_prompt(prompt: str) -> str:
    """Wrap as '[INST] {prompt} [/INST]'."""
    ...

# models.py
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
import torch

def load_tokenizer(model_name: str) -> PreTrainedTokenizer:
    """AutoTokenizer.from_pretrained; pad_token = eos_token if missing."""
    ...

def load_baseline_model(model_name: str) -> PreTrainedModel:
    """from_pretrained(model_name, torch_dtype=bfloat16, device_map='auto').eval()."""
    ...

def load_bidpo_model(base_model_name: str, checkpoint_path: str) -> PreTrainedModel:
    """Load base arch (bfloat16, device_map='auto'), then
    model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'), strict=False), .eval()."""
    ...
```

### Pseudo-code (load_hh_rlhf_prompts)

```
load_hh_rlhf_prompts(n, seed):
    ds = load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base")["test"]
    prompts = set()
    for ex in ds:
        parts = ex["chosen"].split("\n\nAssistant:")
        prompts.add(parts[0].strip())
    prompts = sorted(prompts)  # deterministic order before sampling
    random.Random(seed).shuffle(prompts)
    return prompts[:n]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | config.py + dirs | constants above, `os.makedirs` |
| L-1-2 | load_hh_rlhf_prompts + format_mistral_prompt | dataset extraction/sampling |
| L-1-3 | load_tokenizer + load_baseline_model | HF from_pretrained + eval() |
| L-1-4 | load_bidpo_model | base arch + state_dict load, strict=False, eval() |

---

## M-2: Generation [Complexity: 10, Budget: 1]

**Applied**: Standard HF `model.generate()` loop with seeded sampling (per experiment brief's Exa reference)

```python
# generate.py
from transformers import PreTrainedModel, PreTrainedTokenizer
from torch import Tensor
import torch

def generate_responses(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    prompts: list[str],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
) -> list[str]:
    """Seeded do_sample=True generation over prompts. Returns decoded response strings (prompt stripped)."""
    ...
```

### Pseudo-code

```
generate_responses(model, tokenizer, prompts, max_new_tokens, temperature, top_p, seed):
    torch.manual_seed(seed)
    responses = []
    for prompt in tqdm(prompts):
        formatted = format_mistral_prompt(prompt)
        inputs = tokenizer(formatted, return_tensors="pt", truncation=True,
                            max_length=cfg.MAX_PROMPT_LENGTH).to(model.device)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True,
                                  temperature=temperature, top_p=top_p,
                                  pad_token_id=tokenizer.pad_token_id)
        gen_ids = out[0][inputs["input_ids"].shape[1]:]  # [new_tokens]
        responses.append(tokenizer.decode(gen_ids, skip_special_tokens=True))
    return responses
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs.input_ids | [1, L] | single-prompt batch, L <= MAX_PROMPT_LENGTH |
| out | [1, L + new_tokens] | full generated sequence incl. prompt |
| gen_ids | [new_tokens] | response-only slice |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | generate_responses (both models, timed) | loop above, called twice by run_experiment with elapsed-time tracking wrapping each call |

---

## M-3: Scoring + statistical analysis [Complexity: 8, Budget: 1]

**Applied**: `scipy.stats.ttest_rel` paired-comparison + Cohen's d pooled-std formula (per experiment brief's Exa reference)

```python
# analysis.py
from scipy import stats
import numpy as np
from collab_score import compute_collab_score_v2

def score_responses(responses: list[str]) -> list[float]:
    """Apply compute_collab_score_v2 to each response."""
    ...

def compare_collab_scores(bidpo_scores: list[float], dpo_scores: list[float]) -> dict:
    """Paired t-test (ttest_rel), one-sided p-value, Cohen's d, gate_passed bool."""
    ...

def score_components(response: str) -> dict:
    """Sub-counts: {reasoning, uncertainty, engagement, depth} raw regex-match counts (pre length-norm)."""
    ...
```

### Pseudo-code (compare_collab_scores)

```
compare_collab_scores(bidpo_scores, dpo_scores):
    t_stat, p_two = stats.ttest_rel(bidpo_scores, dpo_scores)
    p_one = p_two / 2 if t_stat > 0 else 1 - p_two / 2
    pooled_std = sqrt((std(bidpo)**2 + std(dpo)**2) / 2)
    cohens_d = (mean(bidpo) - mean(dpo)) / pooled_std
    return {
        bidpo_mean, bidpo_std, dpo_mean, dpo_std, mean_difference,
        t_statistic: t_stat, p_value: p_two, p_value_onesided: p_one,
        effect_size_cohens_d: cohens_d,
        gate_passed: mean(bidpo) > mean(dpo) and p_one < 0.05,
        n_samples: len(bidpo_scores),
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | score_responses | map compute_collab_score_v2 |
| L-3-2 | compare_collab_scores | t-test, p one-sided, Cohen's d, gate |
| L-3-3 | score_components | per-signal-category sub-counts for fig 4 |
| L-3-4 | wire into run_experiment | score both sets, call compare |

---

## M-4: Visualization + orchestration [Complexity: 9, Budget: 0]

**Applied**: Standard matplotlib bar/hist/scatter pattern (same as H-M1 visualize.py)

```python
# visualize.py
def plot_score_comparison_bar(stats: dict, out_path: str) -> None:
    """Bar chart, BiDPO vs DPO mean +/- std error bars. Required figure."""
    ...

def plot_score_distributions(bidpo_scores: list[float], dpo_scores: list[float], out_path: str) -> None:
    """Overlapping histograms."""
    ...

def plot_per_prompt_scatter(dpo_scores: list[float], bidpo_scores: list[float], out_path: str) -> None:
    """X=DPO, Y=BiDPO, diagonal reference line."""
    ...

def plot_score_component_breakdown(bidpo_responses: list[str], dpo_responses: list[str], out_path: str) -> None:
    """Stacked bar: mean reasoning/uncertainty/engagement/depth counts, BiDPO vs DPO."""
    ...

def plot_length_vs_score(responses: list[str], scores: list[float], out_path: str) -> None:
    """Scatter: word_count vs score, verbosity confound check."""
    ...

# run_experiment.py
def main() -> None:
    """Verify checkpoint exists -> load prompts -> load+generate baseline (free GPU) ->
    load+generate bidpo -> score both -> compare -> plot 5 figures -> save results.json."""
    ...
```

### Pseudo-code (main)

```
main():
    assert os.path.exists(cfg.BIDPO_CHECKPOINT_PATH), "H-M1 checkpoint missing"
    prompts = load_hh_rlhf_prompts(cfg.N_PROMPTS, cfg.SEED)
    tokenizer = load_tokenizer(cfg.BASELINE_MODEL)

    baseline = load_baseline_model(cfg.BASELINE_MODEL)
    dpo_responses = generate_responses(baseline, tokenizer, prompts, cfg.MAX_NEW_TOKENS,
                                        cfg.TEMPERATURE, cfg.TOP_P, cfg.SEED)
    del baseline; torch.cuda.empty_cache()

    bidpo = load_bidpo_model(cfg.BIDPO_MODEL_BASE, cfg.BIDPO_CHECKPOINT_PATH)
    bidpo_responses = generate_responses(bidpo, tokenizer, prompts, cfg.MAX_NEW_TOKENS,
                                          cfg.TEMPERATURE, cfg.TOP_P, cfg.SEED)
    del bidpo; torch.cuda.empty_cache()

    dpo_scores = score_responses(dpo_responses)
    bidpo_scores = score_responses(bidpo_responses)
    stats_dict = compare_collab_scores(bidpo_scores, dpo_scores)

    plot_score_comparison_bar(stats_dict, f"{cfg.FIGURES_DIR}/score_comparison_bar.png")
    plot_score_distributions(bidpo_scores, dpo_scores, f"{cfg.FIGURES_DIR}/score_distributions.png")
    plot_per_prompt_scatter(dpo_scores, bidpo_scores, f"{cfg.FIGURES_DIR}/per_prompt_scatter.png")
    plot_score_component_breakdown(bidpo_responses, dpo_responses, f"{cfg.FIGURES_DIR}/component_breakdown.png")
    plot_length_vs_score(bidpo_responses + dpo_responses, bidpo_scores + dpo_scores,
                          f"{cfg.FIGURES_DIR}/length_vs_score.png")

    json.dump(stats_dict, open(cfg.RESULTS_PATH, "w"), indent=2)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | plot_score_comparison_bar | required figure |
| L-4-2 | plot_score_distributions + plot_per_prompt_scatter | 2 figures |
| L-4-3 | plot_score_component_breakdown + plot_length_vs_score | 2 figures |
| L-4-4 | main() orchestration + checkpoint verify + results.json | wiring above |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in table for non-obvious cases
- [x] Subtask count within budget (4 tasks, total 13 subtasks, task-level budgets per allocation)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included (base_hypothesis scenario, read directly)
- [x] External Dependencies API section included with H-M1 verified signatures + checkpoint format correction
