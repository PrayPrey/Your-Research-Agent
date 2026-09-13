# Architecture: H-M3 (Objective x Length F1 Retention, 2x3 Factorial)

**Hypothesis:** Token-level (CAB) achieves superior F1 retention at extrapolated lengths, interaction significant (MECHANISM)

Applied: linregress/ANOVA stats module pattern (scipy) — no direct KB match for MOHAWK/CAB distillation; reused H-M2 stats/config conventions instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2/code/ exists)
**Status**: Serena had no active project registered for this cwd; used direct file Read on actual h-m2/code/ files (config.py, data.py, model.py, analysis.py) to verify implementation, per fallback requirement to trust actual code over specs.
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2's actual code does NOT use real MOHAWK/CAB checkpoints — `model.py` loads `state-spaces/mamba-1.4b-hf` for BOTH "mohawk" and "cab" variants as a proxy, because goombalab/phi-mamba and wph6/CAB checkpoints require custom mamba-ssm CUDA builds unavailable in that environment. This means **no real distillation training code exists to reuse** — H-M3 must implement actual MOHAWK matrix-loss and CAB token-loss training from scratch. Reusable patterns: `AnalysisConfig` dataclass style, C4 streaming loader (`get_long_documents`/`build_batches`), `compute_slope` (scipy linregress), JSON result persistence, OOM-safe batch loop.

---

## File Organization

- `code/config.py` — fixed experiment config (dataclass, 6 conditions)
- `code/data_train.py` — C4 streaming loader for distillation training
- `code/data_eval.py` — LongBench QA loader + length-bucket truncation
- `code/model.py` — teacher (Phi-1.5) + student (Mamba) loaders, AttentionBridge module
- `code/losses.py` — MOHAWK matrix loss, CAB token loss
- `code/train.py` — distillation training loop (both objectives, 6 conditions)
- `code/generate.py` — QA response generation for eval
- `code/metrics.py` — qa_f1_score, F1 retention aggregation
- `code/stats.py` — 2x3 ANOVA, per-length t-tests, CIs
- `code/visualize.py` — required + optional figures
- `code/main.py` — orchestration entrypoint (train all 6 -> eval -> stats -> figures)
- `figures/`, `results/`, `checkpoints/` — outputs

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None

```python
@dataclass
class ExperimentConfig:
    teacher_name: str = "microsoft/phi-1_5"
    student_base_name: str = "state-spaces/mamba-1.4b-hf"  # proxy, per H-M2 finding
    train_dataset: str = "allenai/c4"
    train_dataset_config: str = "en"
    tokens_per_condition: int = 1_500_000_000  # scaled down via --smoke flag for PoC
    lengths: List[int] = field(default_factory=lambda: [4096, 16384, 32768])
    objectives: List[str] = field(default_factory=lambda: ["mohawk", "cab"])
    lr: float = 3e-4
    weight_decay: float = 0.1
    batch_size: int = 4
    grad_accum: int = 8
    seed: int = 42
    longbench_tasks: List[str] = field(default_factory=lambda: [
        "narrativeqa", "qasper", "multifieldqa_en", "hotpotqa",
        "2wikimqa", "musique", "triviaqa"])
    checkpoint_dir: str = "checkpoints"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### Model (`code/model.py`)

**Dependencies**: Config

```python
def load_teacher(config: ExperimentConfig) -> Tuple[nn.Module, "Tokenizer"]: ...
    # AutoModelForCausalLM(teacher_name, fp16/bf16, device_map="auto", output_hidden_states=True)

def load_student_base(config: ExperimentConfig) -> nn.Module: ...
    # MambaForCausalLM.from_pretrained(student_base_name) — fresh copy per condition

class AttentionBridge(nn.Module):
    def __init__(self, d_model: int, hidden_dim: int = None): ...
    def forward(self, q: Tensor, k: Tensor) -> Tuple[Tensor, Tensor]: ...  # (B_target, C_target)
```

### Losses (`code/losses.py`)

**Dependencies**: Model

```python
def mohawk_matrix_loss(teacher_attn: Tensor, student_mixer_matrix: Tensor) -> Tensor: ...
    # F.mse_loss(student_mixer_matrix, teacher_attn)

def cab_token_loss(teacher_layer, student_layer, bridge: AttentionBridge, hidden: Tensor) -> Tensor: ...
    # Q/K -> bridge -> B/C target; MSE vs student B/C projections
```

### Data - Training (`code/data_train.py`)

**Dependencies**: Config

```python
def get_c4_stream(config: ExperimentConfig, tokenizer, length: int): ...
    # streaming=True, tokenize/truncate to `length`, yields batches (reuses H-M2 build_batches pattern)
```

### Data - Eval (`code/data_eval.py`)

**Dependencies**: Config

```python
def load_longbench_tasks(config: ExperimentConfig) -> Dict[str, List[dict]]: ...
    # load_dataset("THUDM/LongBench", task, split="test") for each task

def bucket_by_length(samples: List[dict], tokenizer, target_lengths: List[int]) -> Dict[int, List[dict]]: ...
    # truncate from middle (preserve instruction+question), map to nearest bucket
```

### Train (`code/train.py`)

**Dependencies**: Config, Model, Losses, Data-Train

```python
def train_condition(config: ExperimentConfig, objective: str, length: int,
                     teacher, tokenizer) -> nn.Module: ...
    # fresh student + (bridge if cab); AdamW+cosine; loop tokens_per_condition
    # checkpoint every 500M tokens to checkpoint_dir/{objective}_{length}/

def train_all_conditions(config: ExperimentConfig) -> Dict[str, nn.Module]: ...
    # loop 2 objectives x 3 lengths -> train_condition -> {"mohawk_4096": model, ...}
```

### Generate (`code/generate.py`)

**Dependencies**: Model

```python
def generate_response(model: nn.Module, tokenizer, prompt: str, max_new_tokens: int = 128) -> str: ...
```

### Metrics (`code/metrics.py`)

**Dependencies**: None

```python
def qa_f1_score(prediction: str, ground_truth: str) -> float: ...
    # token overlap F1, from LongBench eval.py

def evaluate_condition(model, tokenizer, samples_by_length: Dict[int, List[dict]],
                        length: int) -> Dict[str, List[float]]: ...
    # returns {task_name: [f1, ...]} for this condition@length

def f1_retention(student_f1: float, teacher_f1: float) -> float: ...
    # (student_f1 / teacher_f1) * 100
```

### Stats (`code/stats.py`)

**Dependencies**: None

```python
def run_two_way_anova(f1_scores: Dict[str, List[float]]) -> dict: ...
    # statsmodels ols("f1 ~ C(objective)*C(length)") -> anova_lm(typ=2)
    # returns {"objective_p", "length_p", "interaction_p", "f_stats"}

def per_length_ttest(cab_scores: List[float], mohawk_scores: List[float]) -> dict: ...
    # scipy.stats.ttest_ind -> {"diff", "p_value", "ci95"}

def evaluate_gate(anova_result: dict, ttests: Dict[int, dict]) -> dict: ...
    # pass = interaction_p<0.05 and ttests[16384]["diff"]>=3 and ttests[32768]["diff"]>=5
```

### Visualization (`code/visualize.py`)

**Dependencies**: Stats/Metrics results dict

```python
def plot_f1_retention_bars(results: dict, out_dir: str) -> None: ...
    # required: X=length, bars=MOHAWK/CAB, error bars=95% CI

def plot_interaction(results: dict, out_dir: str) -> None: ...
    # required: line plot MOHAWK vs CAB across lengths, crossover annotation

def plot_per_task_breakdown(results: dict, out_dir: str) -> None: ...  # optional
def plot_effect_size_heatmap(results: dict, out_dir: str) -> None: ...  # optional
```

### Main (`code/main.py`)

**Dependencies**: All modules

```python
def main() -> None: ...
    # config -> train_all_conditions -> load_longbench_tasks -> bucket_by_length
    # for each of 6 models x 3 eval lengths: evaluate_condition -> f1_retention
    # run_two_way_anova, per_length_ttest x3, evaluate_gate
    # save JSON, generate all figures, print PASS/FAIL
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location | Reuse Note |
|--------|-------------|----------------|------------|
| AnalysisConfig pattern | N/A (pattern only) | `h-m2/code/config.py` | Dataclass style reused, not imported directly |
| C4 streaming loader | N/A (pattern only) | `h-m2/code/data.py` (`get_long_documents`, `build_batches`) | Adapted into `data_train.py` |
| compute_slope | N/A (pattern only) | `h-m2/code/analysis.py` | scipy stats convention reused in `stats.py` |
| CABUnavailableError handling | N/A (pattern only) | `h-m2/code/model.py` | H-M2 found real CAB/MOHAWK checkpoints unusable; H-M3 must implement training from scratch, cannot import H-M2 student loaders |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation, via Read tool — Serena had no active project for this path)

**No direct code import reuse possible**: H-M2 did not implement real MOHAWK/CAB distillation (used identical Mamba proxy for both arms), so H-M3 has no distillation training code to import. Only structural/stylistic patterns (config, data streaming, stats) carry over.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Config + teacher/student loaders | ExperimentConfig, load_teacher, load_student_base, AttentionBridge module | 8 | 2+2+2+2 |
| C-2 | MOHAWK + CAB loss implementation | matrix MSE loss, token-level bridge loss with Q/K->B/C alignment | 10 | 2+2+4+2 |
| C-3 | C4 training data pipeline | streaming loader per length bucket (4K/16K/32K) | 6 | 2+1+1+2 |
| C-4 | Distillation training loop (6 conditions) | AdamW+cosine, checkpointing every 500M tokens, OOM handling, smoke-mode for PoC scale | 15 | 3+3+4+5 |
| C-5 | LongBench data loading + length bucketing | 7 QA tasks x ~200 samples, middle-truncation strategy | 7 | 2+2+2+1 |
| C-6 | Generation + F1 evaluation | generate_response, qa_f1_score, per-task/per-length aggregation | 9 | 2+2+2+3 |
| C-7 | F1 retention computation | student/teacher ratio per condition x length | 4 | 1+1+1+1 |
| C-8 | 2x3 ANOVA + t-test statistical analysis | statsmodels ANOVA with interaction, per-length t-tests, CIs, gate evaluation | 11 | 2+2+4+3 |
| C-9 | Visualization suite | required bar chart + interaction plot, 2 optional figures | 8 | 3+2+2+1 |
| C-10 | Main orchestration + PASS/FAIL summary | wire train->eval->stats->figures, JSON persistence, gate report | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [C-4], Medium(9-13): [C-2, C-6, C-8, C-9], Low(4-8): [C-1, C-3, C-5, C-7, C-10]
