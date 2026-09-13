# Architecture: H-M2 (MECHANISM)

**Hypothesis:** BiDPO models generate responses with higher collaboration scores than DPO
**Type:** MECHANISM - inference-only comparison, no training, single run

Applied: No directly relevant KB pattern found (searched "DL experiment architecture generation comparison" — only unrelated diffusers/community-pipeline results); standard HF `generate()` + `scipy.stats.ttest_rel` paired-comparison pattern used instead (per experiment brief's Exa research).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: patterns found from base code (read directly; Serena MCP had no active project registered for this workspace, so files were read via Read tool instead — same verification guarantee: actual code inspected, not specs)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- `collab_score.py` — `compute_collab_score_v2(response: str) -> float`, identical to H-E1 version, raw unbounded ratio (not normalized).
- `models.py` — `load_tokenizer(model_name)` sets `pad_token = eos_token`; `load_policy_model(model_name)` loads with `torch_dtype=bfloat16, device_map="auto", attn_implementation="flash_attention_2"`, **and calls `.train()`** — H-M2 must call `.eval()` after loading for inference.
- `train.py` — `save_checkpoint(model, path)` saves **raw `model.state_dict()`** via `torch.save(model.state_dict(), path)`. **PRD's assumption of `checkpoint["model_state_dict"]` is WRONG** — the actual checkpoint at `outputs/final.pt` is a bare state_dict, load directly with `model.load_state_dict(torch.load(path), strict=False)`.
- `outputs/results.json` — H-M1 gate actually recorded `"gate_passed": false` (loss did not decrease per warmup-adjusted check: initial=0.8915, final=0.8915, flat). PRD/brief describe H-M1 as PASSED with "0.929→0.918"; actual logged history shows `total_loss` steps 100→200 as 0.8832→0.8915 (increased). Noting this discrepancy — architecture proceeds per Phase 4 instructions but checkpoint quality is uncertain; H-M2 code should treat `final.pt` as-is (not `best.pt`) per PRD path spec.
- `config.py` — model name `mistralai/Mistral-7B-Instruct-v0.2`, matches H-M2 spec.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| collab_score_v2 | copy into `h-m2/code/collab_score.py` | `docs/youra_research/h-m1/code/collab_score.py` (identical to h-e1 version) |
| final.pt checkpoint | `torch.load("../h-m1/code/outputs/final.pt")` → raw `state_dict` | `docs/youra_research/h-m1/code/outputs/final.pt` |

**Verified from**: `docs/youra_research/h-m1/code/{collab_score.py,train.py,models.py,outputs/results.json}` (actual implementation, read directly)

**Note**: Checkpoint loading code MUST be `bidpo_model.load_state_dict(torch.load(ckpt_path, map_location="cpu"), strict=False)` — NOT `checkpoint["model_state_dict"]` as stated in PRD FR-3. Phase 4 Coder: use the actual format above.

---

## File Structure

- `config.py` - fixed hyperparameters (model names, checkpoint path, generation params, seed)
- `collab_score.py` - copied from H-M1/H-E1 (compute_collab_score_v2)
- `data.py` - HH-RLHF prompt extraction (500 unique prompts)
- `models.py` - load baseline + BiDPO models/tokenizer for inference
- `generate.py` - response generation for both models
- `analysis.py` - scoring, paired t-test, Cohen's d, gate evaluation
- `visualize.py` - bar chart, histograms, scatter, component breakdown, length-vs-score
- `run_experiment.py` - orchestration entrypoint

---

## Module Interfaces

### config.py

```python
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
```

### collab_score.py

**Dependencies**: None (re, numpy) — copied verbatim from H-M1

```python
def compute_collab_score_v2(response: str) -> float: ...
```

### data.py

**Dependencies**: config

```python
def load_hh_rlhf_prompts(n: int, seed: int) -> list[str]:
    """Load Anthropic/hh-rlhf test split, extract unique Human-turn prompts, sample n."""
    ...
def format_mistral_prompt(prompt: str) -> str:
    """Wrap as '[INST] {prompt} [/INST]'."""
    ...
```

### models.py

**Dependencies**: config

```python
def load_tokenizer(model_name: str) -> PreTrainedTokenizer:
    """pad_token = eos_token (matches H-M1 pattern)."""
    ...
def load_baseline_model(model_name: str) -> PreTrainedModel:
    """bfloat16, device_map='auto', .eval() for inference."""
    ...
def load_bidpo_model(base_model_name: str, checkpoint_path: str) -> PreTrainedModel:
    """Load base arch, then model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'), strict=False), .eval()."""
    ...
```

### generate.py

**Dependencies**: config, models

```python
def generate_responses(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer,
    prompts: list[str], max_new_tokens: int, temperature: float, top_p: float, seed: int,
) -> list[str]:
    """Deterministic seeded generation (do_sample=True), returns decoded response strings, tracks elapsed time."""
    ...
```

### analysis.py

**Dependencies**: collab_score, scipy.stats, numpy

```python
def score_responses(responses: list[str]) -> list[float]:
    """Apply compute_collab_score_v2 to each response."""
    ...
def compare_collab_scores(bidpo_scores: list[float], dpo_scores: list[float]) -> dict:
    """Paired t-test (ttest_rel), one-sided p-value, Cohen's d, gate_passed bool. Returns full stats dict."""
    ...
def score_components(response: str) -> dict:
    """Breaks raw_score into reasoning/uncertainty/engagement/depth sub-counts for figure 3."""
    ...
```

### visualize.py

**Dependencies**: analysis (scores, stats dict)

```python
def plot_score_comparison_bar(stats: dict, out_path: str) -> None:
    """Required: bar chart, BiDPO vs DPO mean +/- std error bars."""
    ...
def plot_score_distributions(bidpo_scores: list[float], dpo_scores: list[float], out_path: str) -> None: ...
def plot_per_prompt_scatter(dpo_scores: list[float], bidpo_scores: list[float], out_path: str) -> None:
    """X=DPO, Y=BiDPO, diagonal reference line."""
    ...
def plot_score_component_breakdown(bidpo_responses: list[str], dpo_responses: list[str], out_path: str) -> None: ...
def plot_length_vs_score(responses: list[str], scores: list[float], out_path: str) -> None: ...
```

### run_experiment.py

**Dependencies**: config, data, models, generate, analysis, visualize

```python
def main() -> None:
    """Verify checkpoint exists -> load prompts -> load both models sequentially (free GPU between) ->
    generate both response sets -> score -> compare -> plot 5 figures -> save results.json -> gate check."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup config + copy collab_score | config.py, copy collab_score.py from H-M1 | 4 | 1+1+1+1 |
| E-2 | Prompt extraction | Load HH-RLHF test split, extract 500 unique prompts, Mistral format | 7 | 2+2+2+1 |
| E-3 | Checkpoint verification + model loading | Load baseline + BiDPO (raw state_dict, strict=False), sequential GPU memory management | 9 | 3+2+2+2 |
| E-4 | Response generation (both models) | Seeded generate() loop, 500 prompts x 2 models, timing tracking | 10 | 3+2+2+3 |
| E-5 | Collaboration scoring | Apply compute_collab_score_v2 to 1000 responses | 4 | 1+1+1+1 |
| E-6 | Statistical comparison | Paired t-test, one-sided p, Cohen's d, gate evaluation | 8 | 2+2+3+1 |
| E-7 | Visualization suite | 5 figures: bar, histograms, scatter, component breakdown, length-vs-score | 9 | 3+1+2+3 |
| E-8 | End-to-end orchestration + gate check | run_experiment.py, results.json, 04_validation.md inputs | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-3, E-4, E-6, E-7], Low(4-8): [E-1, E-2, E-5, E-8]

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Module sections = interface code only
- [x] 8 Epic tasks with complexity (within 6-12 range)
- [x] Total length < 500 lines
- [x] Codebase Analysis (Serena) section included (base_hypothesis scenario; actual files read directly since Serena had no active project registered)
- [x] External Dependencies section included with verified file location and corrected checkpoint format
