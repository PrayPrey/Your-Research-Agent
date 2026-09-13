# Architecture: H-M2 — Min-k% Memorization Signal Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M2 (MECHANISM / SHOULD_WORK)
**Type:** MECHANISM — FULL tier (8 Epic tasks)

Applied: checkpoint-resume-pipeline pattern
Applied: model-load-cache pattern (HuggingFace revision-specific loading)
Applied: streaming-score-computation pattern (per-item forward pass with result accumulation)
Applied: paired-statistical-test-suite pattern
Applied: cross-hypothesis-reference pattern

---

## Codebase Analysis (Serena)

**Project Type:** incremental_hypothesis (base: h-m1)
**Status:** patterns derived from h-m1 code (Serena MCP unavailable — derived from h-m1/03_architecture.md and h-m1/03_logic.md)
**Analyzed Path:** `docs/youra_research/h-m1/code/` (via Read tool — actual structure)

**Findings from h-m1:**
- Flat code directory (no src/ nesting): `docs/youra_research/h-m1/code/*.py`
- Constants at module top in `config.py`; `ExperimentConfig` dataclass pattern
- JSON intermediate format for checkpoints between pipeline stages
- `sig_stars()` helper: `"***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"`
- `matplotlib.use("Agg")` before import pattern in visualizer.py
- `BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]` — reuse verbatim
- `CORRECTED_ALPHA = 0.0125` — reuse verbatim
- Checkpoint atomic write via `.tmp` + `os.replace()` pattern — reuse

**New in h-m2 (not in h-m1):**
- HuggingFace `revision=` parameter for checkpoint-specific loading
- Per-token log-probability extraction via shifted logit computation
- Paired t-test (vs Mann-Whitney U in h-m1)
- Cross-hypothesis score loading (reads h-m1 statistical_results.json)
- GPU memory management (fp16 model loading, device placement)

---

## File Organization

```
docs/youra_research/h-m2/code/
├── config.py
├── model_loader.py
├── benchmark_loader.py
├── mink_scorer.py
├── statistical_tester.py
├── ablation_runner.py
├── visualizer.py
├── pipeline.py
├── requirements.txt
└── run_experiment.sh

docs/youra_research/h-m2/
├── figures/
│   ├── fig_mink_comparison.png      (mandatory gate figure)
│   ├── fig_mink_heatmap.png
│   ├── fig_mink_violin.png
│   ├── fig_k_sensitivity.png
│   └── fig_cross_hypothesis.png     (bonus)
├── checkpoints/
│   ├── mink_scores_pile_1b.json
│   ├── mink_scores_deduped_1b.json
│   ├── mink_scores_pile_6.9b.json
│   └── mink_scores_deduped_6.9b.json
└── statistical_results_hm2.json
```

---

## Modules

### Config (`config.py`)

**Dependencies:** none

```python
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
CORRECTED_ALPHA = 0.0125   # Bonferroni 0.05/4 — same as h-m1
MODEL_CONFIGS = {
    "pile_1b":     ("EleutherAI/pythia-1b", "step98000"),
    "deduped_1b":  ("EleutherAI/pythia-1b-deduped", "step143000"),
    "pile_6.9b":   ("EleutherAI/pythia-6.9b", "step98000"),
    "deduped_6.9b":("EleutherAI/pythia-6.9b-deduped", "step143000"),
}
K_VALUES = [10, 20, 40]       # primary k=20
K_SENSITIVITY = [5, 10, 20, 40, 60]
MIN_SEQ_LEN = 32              # minimum tokens for scoring
MAX_SEQ_LEN = 512
RANDOM_SEED = 1
BASE_DIR = Path(__file__).parent.parent
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
FIGURES_DIR = BASE_DIR / "figures"
HM1_RESULTS_PATH = BASE_DIR.parent / "h-m1" / "statistical_results.json"
```

---

### ModelLoader (`model_loader.py`)

**Dependencies:** transformers, torch, config

Loads Pythia checkpoints with `revision=` parameter; handles fp16, device placement, step verification.

---

### BenchmarkLoader (`benchmark_loader.py`)

**Dependencies:** datasets, transformers (tokenizer), config

Loads all 4 benchmark test sets; formats items as question+answer text; tokenizes and filters short items.

---

### MinKScorer (`mink_scorer.py`)

**Dependencies:** torch, numpy, model_loader, benchmark_loader, config

Core min-k% computation: forward pass, per-token log-prob extraction, min-k% aggregation. Checkpoint/resume per model-benchmark.

---

### StatisticalTester (`statistical_tester.py`)

**Dependencies:** scipy.stats, numpy, config

Paired t-test (one-tailed), Wilcoxon signed-rank, Cohen's d, Spearman cross-hypothesis correlation. Reuses `BENCHMARKS` and `CORRECTED_ALPHA` from config.

---

### AblationRunner (`ablation_runner.py`)

**Dependencies:** mink_scorer, statistical_tester, config

k-sensitivity analysis across k ∈ {5,10,20,40,60} for MMLU.

---

### Visualizer (`visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy, config

Reuses `sig_stars()` from h-m1 convention. Produces all 4-5 required figures.

---

### Pipeline (`pipeline.py`)

**Dependencies:** all modules, config

End-to-end orchestrator with checkpoint/resume per stage. Stages: `load_benchmarks → score_models → run_stats → run_ablations → generate_figures`.

---

## Epic Tasks

| ID | Task | Description | Module_Size | Dependencies | Algorithm | Integration | Total |
|----|------|-------------|-------------|--------------|-----------|-------------|-------|
| A-1 | Config & scaffold | config.py, requirements.txt, run_experiment.sh, dirs | 2 | 0 | 0 | 0 | 2 |
| A-2 | Model loader | HuggingFace revision= loading; fp16; step verification; 4 checkpoints | 4 | 2 | 2 | 2 | 10 |
| A-3 | Benchmark loader | Load 4 benchmarks; format question+answer; tokenize; filter <32 tokens | 3 | 1 | 1 | 2 | 7 |
| A-4 | Min-k% scorer | Per-token log-prob via shifted logits; min-k% aggregation; batch scoring; checkpoint/resume per model-benchmark | 5 | 4 | 4 | 3 | 16 |
| A-5 | Statistical tester | Paired t-test; Wilcoxon; Cohen's d; Spearman cross-hypothesis; Bonferroni | 3 | 1 | 4 | 2 | 10 |
| A-6 | Ablation runner | k-sensitivity for MMLU at k∈{5,10,20,40,60}; compile results | 2 | 3 | 2 | 2 | 9 |
| A-7 | Visualizer | Bar chart (mandatory); heatmap; violin; k-sensitivity; cross-hypothesis scatter | 4 | 3 | 2 | 3 | 12 |
| A-8 | Pipeline orchestrator | Checkpoint/resume over all 5 stages; mechanism activation check; CLI args | 2 | 5 | 1 | 4 | 12 |

**Distribution**: VeryHigh(16+): [A-4], High(12-15): [A-7, A-8], Medium(9-11): [A-2, A-5, A-6], Low(7-8): [A-3], VeryLow(1-3): [A-1]

**Total Epics: 8** (within MECHANISM range 6-12 ✓)

---

## External Dependencies (Base Hypothesis H-M1)

| Module | Reuse | Source Location |
|--------|-------|-----------------|
| BENCHMARKS constant | Copy | `h-m1/code/config.py` (verified from 03_architecture.md) |
| CORRECTED_ALPHA = 0.0125 | Copy | `h-m1/code/config.py` (verified from 03_config.md) |
| sig_stars() | Copy | `h-m1/code/visualizer.py` (verified from 03_logic.md line 23) |
| matplotlib Agg backend | Copy | `h-m1/code/visualizer.py` (verified from 03_architecture.md Serena findings) |
| JSON checkpoint + atomic write pattern | Follow | `h-m1/code/` all modules |
| Flat code directory structure | Follow | `h-m1/code/` (no src/ nesting) |
| H-M1 statistical results | Load (read-only) | `h-m1/statistical_results.json` — cross-hypothesis Spearman |

**Verified from:** `docs/youra_research/h-m1/03_architecture.md`, `03_logic.md`, `03_config.md` (actual implementation specs, not just specs — h-m1 Phase 4 code runs from these)
