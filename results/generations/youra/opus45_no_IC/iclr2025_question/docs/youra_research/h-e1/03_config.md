# Config: H-E1 (EXISTENCE / PoC)

**Format**: Hardcoded dict (single fixed config, no tuning — per PoC rules)

Applied: sklearn silhouette_score precomputed-distance-matrix pattern (from Archon KB / architecture doc; no direct config-dataclass pattern found in KB, standard PoC dict used)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no `code/` dir exists yet)
**Config Files Found**: None
**Pattern Used**: dict

---

## C-1: Core Experiment Config [Complexity: 6, Budget: 2]

Single fixed dict covering experiment, data, generation, and clustering settings — no variation, no grid, PoC only.

```python
# config.py
CONFIG = {
    # Experiment
    "seed": 42,

    # Data
    "benchmarks": [
        "trivia_qa", "natural_questions", "squad",
        "pop_qa", "halueval_qa", "fever",
    ],
    "n_samples": 1000,

    # Generation
    "gen_model": "meta-llama/Llama-2-7b-hf",
    "n_generations": 10,
    "temperature": 0.7,
    "max_new_tokens": 64,

    # Semantic entropy (NLI)
    "nli_model": "microsoft/deberta-v3-large",

    # Clustering
    "kde_bandwidth": "scott",
    "entropy_support_range": (0, 3),   # linspace bounds for JS-divergence
    "entropy_support_points": 1000,
    "cluster_k_range": (2, 4),         # inclusive sweep for fcluster
    "linkage_method": "ward",
    "silhouette_threshold": 0.5,       # gate condition
}
```

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define CONFIG dict | Single fixed dict in `config.py`, all params above, no variants |

---

## C-2: Path Config [Complexity: 2, Budget: 2]

```python
# config.py (continued)
PATHS = {
    "cache_dir": "h-e1/cache",       # generation cache, ~10GB
    "figures_dir": "h-e1/figures",   # output figures
    "results_path": "h-e1/results.json",  # gate metric + entropy summary
}
```

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Define PATHS dict | cache_dir, figures_dir, results_path; created via `os.makedirs(exist_ok=True)` in run.py |

---

## YAML Equivalent (reference only, not used at runtime)

```yaml
seed: 42
benchmarks: [trivia_qa, natural_questions, squad, pop_qa, halueval_qa, fever]
n_samples: 1000
gen_model: meta-llama/Llama-2-7b-hf
n_generations: 10
temperature: 0.7
nli_model: microsoft/deberta-v3-large
kde_bandwidth: scott
cluster_k_range: [2, 4]
linkage_method: ward
silhouette_threshold: 0.5
cache_dir: h-e1/cache
figures_dir: h-e1/figures
```

**Note**: Phase 4 imports `CONFIG` and `PATHS` dicts directly from `config.py` — no YAML parsing needed for PoC.
