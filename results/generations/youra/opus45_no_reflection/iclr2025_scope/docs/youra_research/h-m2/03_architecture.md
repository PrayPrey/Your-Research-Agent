# Architecture: H-M2 (Token-Level vs Matrix-Level Distillation Drift)

**Hypothesis:** Token-level representations remain stable across lengths while matrix-level degrades (MECHANISM)

Applied: EmbedDistillLoss pattern (l2/cosine distance metric, projection for dim mismatch) — from HF hidden-state distillation KB results.

## Codebase Analysis (Serena)

**Project Type**: green-field (no `h-m1/code/` folder found; H-M1 has no code artifacts to reuse)
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: H-M1 is a prerequisite result (context/gate), not a code dependency. Reused H-M1's `03_architecture.md` structural pattern (config dataclass, streaming data loader, separate metrics/analysis/visualize modules) conceptually since no actual code exists to verify against.

---

## File Organization

- `code/config.py` — fixed analysis config (dataclass)
- `code/data.py` — C4 streaming loader with length-based sampling (512/1024/1536/2048)
- `code/models.py` — teacher (Phi-1.5) + student (MOHAWK, CAB) loaders with fallback
- `code/extraction.py` — hidden state extraction + dimension projection
- `code/drift.py` — L2/cosine drift computation, per-layer breakdown
- `code/stats.py` — slope regression, CI, variance validation
- `code/visualize.py` — required + optional figures
- `code/main.py` — orchestration entrypoint
- `figures/` — output plots
- `results/` — aggregated JSON/CSV stats

---

## Modules

### Config (`code/config.py`)

**Dependencies**: None

```python
@dataclass
class AnalysisConfig:
    teacher_name: str = "microsoft/phi-1_5"
    mohawk_name: str = "goombalab/phi-mamba"
    cab_name: str = "wph6/CAB"
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    target_lengths: List[int] = field(default_factory=lambda: [512, 1024, 1536, 2048])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])
    num_samples: int = 500
    min_doc_chars: int = 8192
    batch_size: int = 8
    teacher_dim: int = 2048
    seed: int = 42
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### Data (`code/data.py`)

**Dependencies**: Config

```python
def get_long_documents(config: AnalysisConfig, tokenizer) -> List[str]: ...
    # streams C4 validation, filters len(text) >= min_doc_chars, takes num_samples, seeded

def build_batches(docs: List[str], tokenizer, length: int, batch_size: int) -> List[dict]: ...
    # tokenize + truncate/pad to `length`, yields {input_ids, attention_mask} batches
```

### Models (`code/models.py`)

**Dependencies**: Config

```python
def load_teacher(config: AnalysisConfig) -> Tuple[nn.Module, "Tokenizer"]: ...
    # AutoModelForCausalLM.from_pretrained(teacher_name, torch_dtype=fp16,
    #   device_map="auto", output_hidden_states=True)

def load_student(config: AnalysisConfig, variant: str) -> nn.Module: ...
    # variant in {"mohawk", "cab"}; loads phi-mamba checkpoint via mamba-ssm/transformers
    # on failure for "cab": raises CABUnavailableError (caught by caller for fallback note)

def get_student_dim(model: nn.Module) -> int: ...
    # returns hidden dim of student model config
```

### Extraction (`code/extraction.py`)

**Dependencies**: Models

```python
def extract_hidden_states(model: nn.Module, input_ids: Tensor, layers: List[int]) -> Dict[int, Tensor]: ...
    # forward(output_hidden_states=True), returns {layer_idx: (batch, seq, dim)}

def get_projection(student_dim: int, teacher_dim: int, device) -> Optional[nn.Linear]: ...
    # returns nn.Linear(student_dim, teacher_dim) if dims differ, else None

def project_if_needed(hidden: Tensor, projection: Optional[nn.Linear]) -> Tensor: ...
```

### Drift (`code/drift.py`)

**Dependencies**: None

```python
def l2_drift(h_teacher: Tensor, h_student: Tensor) -> float: ...
    # torch.norm(h_t - h_s, p=2, dim=-1).mean().item()

def cosine_sim(h_teacher: Tensor, h_student: Tensor) -> float: ...
    # F.cosine_similarity(h_t, h_s, dim=-1).mean().item()

def compute_drift_per_layer(teacher_hidden: Dict[int, Tensor], student_hidden: Dict[int, Tensor],
                             projection: Optional[nn.Linear]) -> Dict[int, dict]: ...
    # per layer: {"l2": float, "cosine": float}
```

### Stats (`code/stats.py`)

**Dependencies**: None

```python
def compute_slope(lengths: List[int], drifts: List[float]) -> dict: ...
    # scipy.stats.linregress -> {"slope", "intercept", "r_value", "ci95_lo", "ci95_hi"}

def variance_check(drifts: List[float]) -> bool: ...
    # std(drifts) < mean(drifts)

def evaluate_gate(mohawk_slope: float, cab_slope: float, cab_drifts_by_length: Dict[int, float]) -> dict: ...
    # {"pass": cab_slope < mohawk_slope and max(cab)/min(cab) < 2.0, "cab_slope", "mohawk_slope", "ratio"}
```

### Analysis Pipeline (`code/main.py` orchestration helper: `code/analysis.py`)

**Dependencies**: Config, Data, Models, Extraction, Drift, Stats

```python
def run_variant(config: AnalysisConfig, teacher, tokenizer, student, variant: str,
                 docs: List[str]) -> Dict[int, dict]: ...
    # for length in target_lengths: build_batches -> extract both -> compute_drift_per_layer
    # aggregate mean L2/cosine per length across batches; returns {length: {"l2": float, "cosine": float, "per_layer": {...}}}

def run_full_analysis(config: AnalysisConfig) -> dict: ...
    # loads teacher + both students, docs once, runs run_variant for mohawk & cab
    # computes compute_slope for each, evaluate_gate, variance_check per condition
    # returns {"mohawk": {...}, "cab": {...}, "gate": {...}}

def save_results(results: dict, config: AnalysisConfig) -> None: ...
    # writes JSON to output_dir
```

### Visualization (`code/visualize.py`)

**Dependencies**: Analysis results dict

```python
def plot_drift_vs_length(results: dict, out_dir: str) -> None: ...
    # required: line plot, MOHAWK orange / CAB blue, slope annotations

def plot_per_layer_heatmap(results: dict, out_dir: str) -> None: ...
    # layers x lengths x {mohawk,cab} heatmap (optional)

def plot_cosine_bars(results: dict, out_dir: str) -> None: ...
    # bar chart per length (optional)

def plot_drift_distributions(results: dict, out_dir: str) -> None: ...
    # violin plots per condition (optional)
```

### Main (`code/main.py`)

**Dependencies**: All modules

```python
def main() -> None: ...
    # load config -> run_full_analysis -> save_results -> generate all figures
    # print PASS/FAIL summary based on results["gate"]["pass"]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Config + C4 streaming data pipeline | AnalysisConfig, filter >=8192 char docs, seeded 500 sample, multi-length batching | 8 | 2+2+2+2 |
| B-2 | Teacher model loading | Load Phi-1.5 fp16 with output_hidden_states | 4 | 1+1+1+1 |
| B-3 | Student model loading (MOHAWK + CAB) with fallback | Load phi-mamba/CAB checkpoints, handle unavailable CAB gracefully | 10 | 2+3+2+3 |
| B-4 | Hidden state extraction + projection | Extract layers 8/12/16 for teacher/student, dimension projection layer | 8 | 2+2+2+2 |
| B-5 | Drift computation (L2 + cosine, per-layer) | l2_drift, cosine_sim, per-layer aggregation | 6 | 1+1+2+2 |
| B-6 | Statistical analysis (slope, CI, variance) | scipy linregress slope, 95% CI, std<mean validation | 8 | 2+2+3+1 |
| B-7 | Analysis pipeline orchestration | Loop 4 lengths x 500 docs x 2 variants x 3 layers, aggregate | 13 | 3+3+3+4 |
| B-8 | Gate evaluation + results persistence | cab_slope < mohawk_slope check, bounded-drift check, save JSON | 6 | 1+2+1+2 |
| B-9 | Visualization suite | Required drift-vs-length plot + 3 optional figures | 9 | 3+2+2+2 |
| B-10 | Main orchestration + PASS/FAIL summary | Wire all modules, print/report gate result | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-6, B-7, B-9], Low(4-8): [B-1, B-2, B-4, B-5, B-8, B-10]
