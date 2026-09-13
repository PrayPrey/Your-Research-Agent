# H-M3 Architecture: Background Linear Decodability (Formal Test)

Applied: flat-two-file pattern (config + run_experiment) from H-M2

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-m2/code/)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: Two-file structure — `config.py` (constants only) + `run_experiment.py` (all logic). H-M3 is strictly simpler: drop weight-diff and gradient-norm analysis (FR-1, FR-2), keep only probe + stats + viz + report.

---

## File Organization

- `h-m3/code/config.py` — constants
- `h-m3/code/run_experiment.py` — all experiment logic + orchestration
- `h-m3/figures/` — output figures (auto-created at runtime)
- `h-m3/results.json` — output results
- `h-m3/04_validation.md` — output report

---

## External Dependencies (Base Hypothesis)

| Module/Pattern | Import Path | File Location |
|---|---|---|
| `load_resnet50` | copy/adapt inline | `h-m2/code/run_experiment.py:L26-40` |
| `extract_layer4_features` | copy/adapt inline | `h-m2/code/run_experiment.py:L168-188` |
| `linear_probe` | copy/adapt inline | `h-m2/code/run_experiment.py:L191-199` |
| `paired_ttest` / `gate_verdict` | copy/adapt inline | `h-m2/code/run_experiment.py:L223-240` |
| Config constants | adapt from | `h-m2/code/config.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

---

## Module Definitions

### Config (`h-m3/code/config.py`)

**Dependencies**: none

```python
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = (
    "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research"
    "/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
)
BASE_DIR: str  # dirname(dirname(__file__))
FIGURES_DIR: str  # BASE_DIR/figures
RESULTS_JSON: str  # BASE_DIR/results.json
VALIDATION_REPORT: str  # BASE_DIR/04_validation.md

METHODS: list = ["erm", "groupdro", "sam"]  # no dfr — H-M3 scope
SEEDS: list = [1, 2, 3]
PRIMARY_METHODS: list = ["erm", "groupdro"]  # paired t-test gate

PROBE_C: float = 1e9
PROBE_SOLVER: str = "lbfgs"
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
PROBE_N_TEST_SAMPLES: int = 5794
BATCH_SIZE: int = 100

IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
```

---

### RunExperiment (`h-m3/code/run_experiment.py`)

**Dependencies**: config, torch, torchvision, sklearn, scipy, wilds, matplotlib, numpy

```python
def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module: ...
    # resnet50(weights=None), fc=Linear(2048,2), load_state_dict, eval(), to(device)

def get_transform() -> T.Compose: ...
    # Resize(256) + CenterCrop(224) + ToTensor + Normalize(IMAGENET_MEAN, IMAGENET_STD)

def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader: ...
    # wilds.get_dataset(waterbirds, root_dir=WILDS_CACHE).get_subset(split, transform)

def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str,
) -> tuple[np.ndarray, np.ndarray]: ...
    # model.eval() + torch.no_grad()
    # forward: conv1→bn1→relu→maxpool→layer1→layer2→layer3→layer4→adaptive_avg_pool2d→flatten
    # bg_label = metadata[:, 0].numpy() % 2
    # returns (features [N, 2048], bg_labels [N])

def run_probe(features: np.ndarray, labels: np.ndarray) -> float: ...
    # LogisticRegression(solver=PROBE_SOLVER, C=PROBE_C, max_iter=PROBE_MAX_ITER,
    #                    random_state=PROBE_RANDOM_STATE).fit(features, labels).score(...)
    # convergence guard: retry with max_iter=5000 on ConvergenceWarning

def run_all_probes(test_loader: DataLoader, device: str) -> dict[str, float]: ...
    # loops METHODS x SEEDS: load_resnet50 → extract_layer4_features → run_probe
    # returns {"erm_seed1": acc, "groupdro_seed1": acc, ..., "sam_seed3": acc}
    # prints [H-M3] log lines per experiment brief

def paired_ttest(erm_accs: list, gdro_accs: list) -> tuple[float, float]: ...
    # scipy.stats.ttest_rel(erm_accs, gdro_accs, alternative='greater')
    # cohens_d = mean(diff) / std(diff, ddof=1)
    # returns (p_value, cohens_d)

def gate_verdict(p_value: float, cohens_d: float) -> str: ...
    # 'CONFIRMED' if p<0.05 and d>0
    # 'SUGGESTIVE' if p<0.10 and d>0.5
    # else 'REJECTED'

def save_figures(probe_results: dict, stat_results: dict) -> None: ...
    # Fig1 (gate_metrics.png): grouped bar ERM vs GroupDRO x3 seeds + p-value annotation
    # Fig2 (all_probes.png): all 9 checkpoints bar chart grouped by method
    # Fig3 (paired_diff.png): scatter (ERM_i - GroupDRO_i) i=1,2,3 + mean±std bar
    # Fig4 (probe_vs_wga.png): probe_acc vs WGA scatter for all 9 checkpoints + Pearson r
    # saves to FIGURES_DIR

def save_results(results: dict) -> None: ...
    # json.dump(results, RESULTS_JSON, indent=2)

def generate_validation_report(results: dict) -> None: ...
    # writes 04_validation.md: gate verdict, probe acc table, stat test, sanity check status

def main() -> None: ...
    # 1. test_loader = get_loader('test', BATCH_SIZE)
    # 2. probe_results = run_all_probes(test_loader, device)
    # 3. sanity: assert ERM_mean > 0.6; assert all accs in [0.5, 1.0]
    # 4. erm_accs, gdro_accs = extract from probe_results
    # 5. p_value, cohens_d = paired_ttest(erm_accs, gdro_accs)
    # 6. verdict = gate_verdict(p_value, cohens_d)
    # 7. save_figures, save_results, generate_validation_report
    # 8. print [H-M3] summary lines
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config | Write `config.py` with all H-M3 constants | 5 | 1+1+1+2 |
| A-2 | Data loading | `get_transform` (256+CenterCrop), `get_loader` via WILDS API | 6 | 1+2+1+2 |
| A-3 | Feature extraction | `load_resnet50`, `extract_layer4_features` — bg_label=metadata[:,0]%2 | 7 | 2+2+1+2 |
| A-4 | Linear probe loop | `run_probe`, `run_all_probes` for 9 checkpoints + convergence guard | 7 | 2+2+2+1 |
| A-5 | Statistical analysis | `paired_ttest`, `gate_verdict`, sanity checks, [H-M3] log messages | 8 | 2+2+2+2 |
| A-6 | Visualization | 4 figures: gate bar, all-9 bar, paired diff scatter, probe-vs-WGA scatter | 10 | 3+2+3+2 |
| A-7 | Report + results | `save_results` (JSON), `generate_validation_report` (markdown) | 7 | 2+2+1+2 |
| A-8 | Orchestration | `main()` wiring, assertion guards, end-to-end smoke test | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-6, A-8], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-7]

---

## Implementation Notes for Phase 4

1. **H-M3 drops FR-1 and FR-2 from H-M2** — no weight diff, no gradient norm. `run_experiment.py` is shorter.
2. **Transform**: H-M2 used `Resize((224,224))`; use `Resize(256)+CenterCrop(224)` per experiment brief.
3. **Probe trains and scores on same test set features** (N=5794) — measuring raw decodability, not generalization.
4. **SAM is exploratory** (H-P1b, no gate threshold): include in probe loop and figures; exclude from `paired_ttest` gate.
5. **WGA values for Fig4**: hardcode from H-M1 validated results (ERM≈0.72, GroupDRO≈0.88, SAM per H-M1 report).
6. **Convergence guard**: catch `ConvergenceWarning`, retry `LogisticRegression(max_iter=5000)`.
