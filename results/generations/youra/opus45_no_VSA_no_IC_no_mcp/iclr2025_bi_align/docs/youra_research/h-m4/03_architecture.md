# Architecture: H-M4 Differential Benchmark Profiles

**Hypothesis ID:** h-m4 | **Type:** MECHANISM | **Gate:** SHOULD_WORK

Applied: multi-model batch-evaluation pipeline pattern (load once, eval across benchmarks, aggregate + effect-size analysis)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-m3 code found and read directly (Read tool used in place of Serena — same filesystem, no MCP server available in this run; content verified against actual files, not specs)
**Analyzed Path**: `docs/youra_research/h-m3/code/`
**Findings**: `model.py` exposes `load_tokenizer(cfg)`, `load_trained_policy(cfg, checkpoint_path)` (LoRA merge-and-unload), `get_sequence_logprobs(model, input_ids, attention_mask)`. `config.py` defines `HM3Config` with `base_model`, `seeds`, `methods`, `output_root="./h-m3_models"`. No RLHF-specific loader exists in h-m3/code (only DPO trainer `dpo_train.py` present) — RLHF checkpoints must be verified at runtime; loader falls back gracefully if RLHF uses a different save format (full model vs adapter).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_tokenizer | `from h_m3.model import load_tokenizer` | `h-m3/code/model.py` |
| load_trained_policy | `from h_m3.model import load_trained_policy` | `h-m3/code/model.py` |
| get_sequence_logprobs | `from h_m3.model import get_sequence_logprobs` | `h-m3/code/model.py` |
| HM3Config | `from h_m3.config import HM3Config` | `h-m3/code/config.py` |

**Verified from**: `docs/youra_research/h-m3/code/` (actual implementation)

**Note**: `HM3Config.output_root = "./h-m3_models"` — h-m4 must confirm actual checkpoint directory naming (`dpo_seed_*`, `rlhf_seed_*` per PRD FR-1) at load time; add existence check with clear error if mismatched.

---

## Module Structure

### config.py (`h-m4/code/config.py`)

**Dependencies**: none

```python
@dataclass
class HM4Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    checkpoint_root: str = "../h-m3/code/checkpoints"
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])
    truthfulqa_path: str = "truthfulqa/truthful_qa"
    hh_rlhf_path: str = "Anthropic/hh-rlhf"
    max_length: int = 512
    batch_size: int = 8
    d_large_threshold: float = 0.3
    d_small_threshold: float = 0.15
    profile_corr_threshold: float = 0.8
    results_path: str = "./benchmark_results.json"
    analysis_path: str = "./differential_analysis.json"
    profile_plot_path: str = "./profile_comparison.png"
    seed: int = 42
```

### model_loader.py (`h-m4/code/model_loader.py`)

**Dependencies**: config, h-m3/model.py (load_trained_policy)

```python
def resolve_checkpoint_path(cfg: HM4Config, method: str, seed: int) -> str: ...
def load_all_models(cfg: HM4Config) -> dict[str, AutoModelForCausalLM]:
    """Returns {'dpo_seed42': model, ..., 'rlhf_seed1024': model}"""
def verify_model_integrity(model, expected_param_count: int | None = None) -> bool: ...
```

### benchmarks.py (`h-m4/code/benchmarks.py`)

**Dependencies**: config, datasets

```python
def load_truthfulqa(cfg: HM4Config) -> Dataset: ...
def load_hh_helpful(cfg: HM4Config) -> Dataset: ...
def load_hh_harmless(cfg: HM4Config) -> Dataset: ...
def get_benchmark(name: str, cfg: HM4Config) -> Dataset:
    """name in {'truthfulqa', 'hh_helpful', 'hh_harmless'}"""
```

### eval_mc1.py (`h-m4/code/eval_mc1.py`)

**Dependencies**: torch, h-m3/model.py (get_sequence_logprobs)

```python
def compute_sequence_logprob(logits, input_ids, target_ids) -> float: ...
def evaluate_mc1(model, tokenizer, sample: dict, device: str) -> int:
    """Returns 1 if predicted choice == correct_idx else 0"""
```

### eval_preference.py (`h-m4/code/eval_preference.py`)

**Dependencies**: torch, h-m3/model.py (get_sequence_logprobs)

```python
def parse_hh_conversation(conversation: str) -> tuple[str, str]: ...
def compute_response_logprob(model, tokenizer, conversation: str, device: str) -> float: ...
def evaluate_preference(model, tokenizer, sample: dict, device: str) -> int:
    """Returns 1 if chosen_logprob > rejected_logprob else 0"""
```

### evaluate.py (`h-m4/code/evaluate.py`)

**Dependencies**: benchmarks, eval_mc1, eval_preference, model_loader, config

```python
def evaluate_model_on_benchmark(model, tokenizer, benchmark_name: str, dataset, device) -> dict:
    """Returns {'scores': list[int], 'accuracy': float, 'stderr': float}"""
def run_all_evaluations(cfg: HM4Config) -> dict:
    """Returns {model_id: {benchmark_name: {scores, accuracy, stderr}}}"""
    # saves to cfg.results_path
```

### analysis.py (`h-m4/code/analysis.py`)

**Dependencies**: config, numpy, scipy.stats

```python
def analyze_differential_profiles(dpo_results: list[dict], rlhf_results: list[dict]) -> dict:
    """Cohen's d + t-test per benchmark; differential_profile bool"""
def analyze_profile_shape(dpo_results: list[dict], rlhf_results: list[dict]) -> dict:
    """z-normalized profile vectors + correlation"""
def analyze_cross_benchmark_correlations(dpo_results: list[dict], rlhf_results: list[dict]) -> dict:
    """pairwise correlation diffs across methods"""
def run_full_analysis(cfg: HM4Config, benchmark_results: dict) -> dict:
    """Orchestrates all 3 analyses, writes cfg.analysis_path"""
```

### visualize.py (`h-m4/code/visualize.py`)

**Dependencies**: config, matplotlib, analysis output

```python
def plot_profile_comparison(dpo_profile: list[float], rlhf_profile: list[float],
                             benchmarks: list[str], out_path: str) -> None: ...
```

### run_experiment.py (`h-m4/code/run_experiment.py`)

**Dependencies**: config, model_loader, evaluate, analysis, visualize

```python
def main() -> int:
    """Loads models -> runs evaluations -> analysis -> plot -> returns 0/1 exit code"""
```

---

## Codebase Analysis Note (Serena Requirement)

No `mcp__serena__*` tools were available in this execution environment; direct `Read` on `h-m3/code/*.py` substitutes for symbol lookup per the "trust actual code over specs" rule. Confirmed: h-m3 code is DPO-centric (`dpo_train.py` only); no RLHF trainer file exists in `h-m3/code/`. **Risk**: RLHF checkpoints referenced in h-m4 PRD FR-1 may not exist under `h-m3/checkpoints/rlhf_seed_*` — Task A-1 must include a hard existence check before evaluation proceeds.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + checkpoint verification | HM4Config, resolve/verify all 10 checkpoint paths exist | 6 | 2+2+1+1 |
| A-2 | Model loader | Load 10 models via h-m3 load_trained_policy, integrity check | 8 | 3+3+1+1 |
| A-3 | Benchmark loaders | TruthfulQA + HH-helpful + HH-harmless dataset loading/formatting | 7 | 2+2+2+1 |
| A-4 | MC1 evaluation | evaluate_mc1 + sequence logprob scoring for TruthfulQA | 8 | 2+2+3+1 |
| A-5 | Preference evaluation | evaluate_preference + conversation parsing for HH benchmarks | 8 | 2+2+3+1 |
| A-6 | Batch evaluation orchestration | run_all_evaluations across 10 models x 3 benchmarks, save results | 10 | 3+3+2+2 |
| A-7 | Differential profile analysis | Cohen's d, t-tests, differential criterion check | 7 | 2+1+3+1 |
| A-8 | Profile shape + correlation analysis | z-norm profiles, correlation, cross-benchmark correlation diffs | 6 | 2+1+2+1 |
| A-9 | Visualization | Radar chart profile_comparison.png | 4 | 1+1+1+1 |
| A-10 | Experiment runner + validation report | run_experiment.py orchestration, 04_validation.md generation | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-6], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-7, A-8, A-9, A-10]
