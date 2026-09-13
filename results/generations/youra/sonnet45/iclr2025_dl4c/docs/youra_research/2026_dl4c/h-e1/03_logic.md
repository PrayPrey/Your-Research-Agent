# Logic Design: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-18
**Author:** Phase 3 Logic Agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## Knowledge Base Patterns Applied

Applied: HuggingFace Accelerate big model inference pattern (sequential loading, memory management)
Applied: GPU memory flush pattern (gc.collect + torch.cuda.empty_cache)
Applied: Python built-in profiling pattern (cProfile, tracemalloc)

---

## A-3: Model Management [Complexity: 15, Budget: 4]

Applied: HuggingFace Accelerate big model inference + GPU memory flush

### API Signatures

```python
from typing import Tuple, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelManager:
    """Sequential model loading and code generation manager."""

    def __init__(self, config: 'ExperimentConfig'):
        """Initialize with config."""
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self, model_name: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load model and tokenizer to GPU. Returns (model, tokenizer)."""
        ...

    def unload_model(self) -> None:
        """Free GPU memory after model use."""
        ...

    def generate_sample(self, prompt: str) -> str:
        """Generate single code sample. prompt: str -> code: str"""
        ...

    def generate_batch(self, task: dict, n: int) -> List[str]:
        """Generate n samples for task. Returns list of n code strings."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, seq_len] | Tokenized prompt |
| attention_mask | [1, seq_len] | Attention mask |
| output_ids | [1, gen_len] | Generated tokens |

### Pseudo-code

```
load_model(model_name):
1. tokenizer = AutoTokenizer.from_pretrained(model_name)
2. model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
3. model.eval()
4. return (model, tokenizer)

unload_model():
1. del self.model, self.tokenizer
2. gc.collect()
3. torch.cuda.empty_cache()

generate_sample(prompt):
1. inputs = tokenizer(prompt, return_tensors="pt").to(device)
2. outputs = model.generate(inputs, temperature=0.8, top_p=0.95, max_new_tokens=512, do_sample=True)
3. code = tokenizer.decode(outputs[0], skip_special_tokens=True)
4. return code[len(prompt):]  # Strip prompt

generate_batch(task, n):
1. prompt = task["prompt"]
2. samples = []
3. for i in range(n):
4.     code = generate_sample(prompt)
5.     samples.append(code)
6. return samples
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Model loading API | AutoModelForCausalLM.from_pretrained with device_map="auto" |
| L-3-2 | Generation API | model.generate with temperature=0.8, top_p=0.95, max_new_tokens=512 |
| L-3-3 | Sequential memory management | unload_model() with gc.collect + torch.cuda.empty_cache |
| L-3-4 | Error handling | Try-catch for model loading failures, skip model on error |

---

## A-4: Profiling Pipeline [Complexity: 16, Budget: 4]

Applied: Python built-in profiling (cProfile, tracemalloc)

### API Signatures

```python
from typing import List, Tuple, Dict
import cProfile
import tracemalloc
from radon.complexity import cc_visit
from lizard import analyze_file

class CodeProfiler:
    """Multi-dimensional code profiling (correctness, complexity, efficiency)."""

    def __init__(self, timeout: float = 3.0, n_workers: int = 4):
        """Initialize profiler with timeout and worker config."""
        self.timeout = timeout
        self.n_workers = n_workers

    def profile_correctness(self, samples: List[str], tests: str) -> float:
        """Execute samples against tests. Returns pass@k score (0-1)."""
        ...

    def profile_complexity(self, samples: List[str]) -> Tuple[float, float]:
        """Compute complexity metrics. Returns (cyclomatic, ast_depth)."""
        ...

    def profile_efficiency(self, samples: List[str]) -> Tuple[float, float]:
        """Profile runtime and memory. Returns (runtime_ms, memory_kb)."""
        ...

    def extract_signature(self, task: dict, samples: List[str]) -> Dict[str, float]:
        """Extract full performance signature. Returns dict with all metrics."""
        ...
```

### Tensor Shapes

N/A (operates on Python strings and scalars)

### Pseudo-code

```
profile_correctness(samples, tests):
1. passed = 0
2. for sample in samples:
3.     exec_result = execute_with_timeout(sample + tests, timeout=3.0)
4.     if exec_result.success: passed += 1
5. n, c = len(samples), passed
6. k = min(n, 10)  # pass@10
7. pass_k = 1 - comb(n-c, k) / comb(n, k)
8. return pass_k

profile_complexity(samples):
1. cyclo_scores = []
2. ast_depths = []
3. for sample in samples:
4.     cc_results = cc_visit(sample)  # radon
5.     cyclo_scores.append(mean([r.complexity for r in cc_results]))
6.     lizard_result = analyze_file.analyze_source_code("", sample)
7.     ast_depths.append(lizard_result.average_nloc)
8. return (mean(cyclo_scores), mean(ast_depths))

profile_efficiency(samples):
1. runtimes = []
2. memories = []
3. for sample in samples:
4.     if not is_correct(sample): continue
5.     # Runtime profiling
6.     profiler = cProfile.Profile()
7.     profiler.enable()
8.     exec(sample)
9.     profiler.disable()
10.    runtimes.append(profiler.get_total_time() * 1000)  # ms
11.    # Memory profiling
12.    tracemalloc.start()
13.    exec(sample)
14.    current, peak = tracemalloc.get_traced_memory()
15.    tracemalloc.stop()
16.    memories.append(peak / 1024)  # kb
17. return (mean(runtimes), mean(memories))

extract_signature(task, samples):
1. tests = task["test"]
2. correctness = profile_correctness(samples, tests)
3. cyclo, ast_depth = profile_complexity(samples)
4. runtime, memory = profile_efficiency(samples)
5. return {
6.     "correctness": correctness,
7.     "cyclomatic": cyclo,
8.     "ast_depth": ast_depth,
9.     "runtime_ms": runtime,
10.    "memory_kb": memory
11. }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Correctness profiling | Test execution with timeout, pass@k unbiased estimator |
| L-4-2 | Complexity profiling | radon cc_visit for cyclomatic, lizard for AST depth |
| L-4-3 | Efficiency profiling | cProfile for runtime, tracemalloc for memory |
| L-4-4 | Parallel execution | multiprocessing.Pool with n_workers=4 for test execution |

---

## Supporting APIs (Low-Complexity Tasks)

### ConfigModule (A-1)

```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class ExperimentConfig:
    """Hardcoded experiment configuration."""

    MODELS: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("codellama/CodeLlama-7b-hf", "baseline"),
        ("codellama/CodeLlama-7b-Python-hf", "execution"),
        ("WisdomShell/SelfCodeAlign-7B", "execution"),
        ("WisdomShell/StepCoder-7B", "execution"),
        ("alignment-lab/CodeLlama-7b-DPO", "preference"),
        ("alignment-lab/CodeLlama-7b-RLAIF", "preference"),
    ])
    TEMPERATURE: float = 0.8
    TOP_P: float = 0.95
    MAX_TOKENS: int = 512
    NUM_SAMPLES: int = 64
    RANDOM_SEED: int = 42
    TIMEOUT: float = 3.0
    N_WORKERS: int = 4
    K_CLUSTERS: int = 3
    COHENS_D_THRESHOLD: float = 1.5
```

### DataModule (A-2)

```python
from typing import Dict
from datasets import load_dataset

class HumanEvalPlusLoader:
    """HumanEval+ dataset loader."""

    def __init__(self):
        """Initialize loader."""
        self.dataset = None

    def load_dataset(self) -> Dict[str, dict]:
        """Load HumanEval+ from evalplus. Returns dict[task_id -> task_data]."""
        ...

    def get_problem(self, task_id: str) -> dict:
        """Get single problem by ID. Returns dict with prompt, test, canonical_solution."""
        ...
```

### ClusteringModule (A-5)

```python
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import ttest_ind

class AlignmentClusterer:
    """PCA + k-means clustering with effect size computation."""

    def __init__(self, k: int = 3, random_state: int = 42):
        """Initialize with k clusters and random seed."""
        self.k = k
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3, random_state=random_state)
        self.kmeans = KMeans(n_clusters=k, random_state=random_state)

    def prepare_features(self, signatures: List[dict]) -> np.ndarray:
        """Convert signature dicts to feature matrix. Returns X: [N, 5]"""
        ...

    def fit_pca(self, X: np.ndarray) -> np.ndarray:
        """PCA transform to 3D. X: [N, 5] -> X_pca: [N, 3]"""
        ...

    def fit_kmeans(self, X_pca: np.ndarray) -> np.ndarray:
        """K-means clustering. X_pca: [N, 3] -> labels: [N]"""
        ...

    def compute_cohens_d(self, X_pca: np.ndarray, labels: np.ndarray) -> float:
        """Compute Cohen's d effect size. Returns scalar d."""
        ...

    def compute_silhouette(self, X_pca: np.ndarray, labels: np.ndarray) -> float:
        """Silhouette score. Returns scalar in [-1, 1]."""
        ...

    def compute_purity(self, labels: np.ndarray, alignment_types: List[str]) -> float:
        """Cluster purity by alignment type. Returns scalar in [0, 1]."""
        ...
```

### VisualizerModule (A-6)

```python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List

class ResultVisualizer:
    """Generate 6 publication-quality figures."""

    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = output_dir

    def plot_3d_scatter(
        self,
        X_pca: np.ndarray,
        labels: np.ndarray,
        alignment_types: List[str]
    ) -> None:
        """3D scatter plot of PCA space. Saves to 3d_scatter.png"""
        ...

    def plot_heatmap(
        self,
        signatures: List[dict],
        model_names: List[str]
    ) -> None:
        """Model × Dimension heatmap. Saves to heatmap.png"""
        ...

    def plot_boxplots(
        self,
        signatures: List[dict],
        alignment_types: List[str]
    ) -> None:
        """Metric distributions by alignment. Saves to boxplots.png"""
        ...

    def plot_dendrogram(
        self,
        X: np.ndarray,
        model_names: List[str]
    ) -> None:
        """Hierarchical clustering dendrogram. Saves to dendrogram.png"""
        ...

    def plot_effect_size(
        self,
        cohens_d: float,
        ci_lower: float,
        ci_upper: float
    ) -> None:
        """Cohen's d with confidence interval. Saves to effect_size.png"""
        ...

    def plot_gate_metrics(
        self,
        target: float,
        actual: float
    ) -> None:
        """Gate comparison bar chart. Saves to gate_metrics.png"""
        ...
```

### Experiment Orchestration (A-7)

```python
from typing import List, Dict
import pandas as pd

def run_experiment(config: ExperimentConfig) -> None:
    """Main experiment loop."""

    # 1. Load data
    loader = HumanEvalPlusLoader()
    tasks = loader.load_dataset()

    # 2. Initialize components
    model_manager = ModelManager(config)
    profiler = CodeProfiler(timeout=config.TIMEOUT, n_workers=config.N_WORKERS)
    clusterer = AlignmentClusterer(k=config.K_CLUSTERS, random_state=config.RANDOM_SEED)
    visualizer = ResultVisualizer(output_dir="h-e1/figures")

    # 3. Profile all models
    all_signatures = []
    model_names = []
    alignment_types = []

    for model_name, alignment_type in config.MODELS:
        print(f"Processing {model_name}...")

        # Load model
        model_manager.load_model(model_name)

        # Generate and profile
        task_signatures = []
        for task_id, task in tasks.items():
            samples = model_manager.generate_batch(task, config.NUM_SAMPLES)
            signature = profiler.extract_signature(task, samples)
            task_signatures.append(signature)

        # Aggregate across tasks
        avg_signature = aggregate_signatures(task_signatures)
        all_signatures.append(avg_signature)
        model_names.append(model_name)
        alignment_types.append(alignment_type)

        # Free memory
        model_manager.unload_model()

    # 4. Clustering analysis
    X = clusterer.prepare_features(all_signatures)
    X_pca = clusterer.fit_pca(X)
    labels = clusterer.fit_kmeans(X_pca)

    # 5. Compute metrics
    cohens_d = clusterer.compute_cohens_d(X_pca, labels)
    silhouette = clusterer.compute_silhouette(X_pca, labels)
    purity = clusterer.compute_purity(labels, alignment_types)

    # 6. Visualization
    visualizer.plot_3d_scatter(X_pca, labels, alignment_types)
    visualizer.plot_heatmap(all_signatures, model_names)
    visualizer.plot_boxplots(all_signatures, alignment_types)
    visualizer.plot_dendrogram(X, model_names)
    visualizer.plot_effect_size(cohens_d, 0.0, 0.0)  # Placeholder CI
    visualizer.plot_gate_metrics(config.COHENS_D_THRESHOLD, cohens_d)

    # 7. Save results
    save_results(all_signatures, model_names, alignment_types, cohens_d, silhouette, purity)

    # 8. Gate evaluation
    print(f"\nGate Evaluation:")
    print(f"Cohen's d: {cohens_d:.3f}")
    print(f"Threshold: {config.COHENS_D_THRESHOLD}")
    print(f"Status: {'PASS' if cohens_d > config.COHENS_D_THRESHOLD else 'FAIL'}")


def aggregate_signatures(signatures: List[Dict[str, float]]) -> Dict[str, float]:
    """Average signatures across tasks."""
    keys = signatures[0].keys()
    return {k: np.mean([s[k] for s in signatures]) for k in keys}


def save_results(
    signatures: List[dict],
    model_names: List[str],
    alignment_types: List[str],
    cohens_d: float,
    silhouette: float,
    purity: float
) -> None:
    """Save signatures and metrics to CSV."""

    # Signatures CSV
    df_sigs = pd.DataFrame(signatures)
    df_sigs["model"] = model_names
    df_sigs["alignment_type"] = alignment_types
    df_sigs.to_csv("h-e1/results/signatures.csv", index=False)

    # Metrics CSV
    df_metrics = pd.DataFrame({
        "metric": ["cohens_d", "silhouette", "purity"],
        "value": [cohens_d, silhouette, purity]
    })
    df_metrics.to_csv("h-e1/results/metrics.csv", index=False)

    print("\nResults saved to h-e1/results/")
```

---

## Key Design Decisions

### Memory Management
- Sequential model loading to avoid GPU OOM
- Explicit unload with gc.collect + torch.cuda.empty_cache
- Only one model in GPU memory at a time

### Sampling Strategy
- Temperature=0.8 for diversity (not greedy)
- Top_p=0.95 for nucleus sampling
- 64 samples per task (sufficient for pass@k estimation)

### Profiling Parallelization
- Test execution parallelized (4 workers)
- Model generation sequential (GPU constraint)
- Complexity/efficiency profiling on-demand (not cached)

### Clustering Pipeline
- StandardScaler before PCA (different metric scales)
- PCA to 3D for visualization
- KMeans k=3 (matches 3 alignment types)
- Cohen's d as primary metric (effect size > statistical significance)

---

## Error Handling

```python
# Model loading
try:
    model_manager.load_model(model_name)
except Exception as e:
    print(f"Failed to load {model_name}: {e}")
    continue  # Skip to next model

# Test execution
try:
    exec(sample + tests)
    passed += 1
except (TimeoutError, Exception):
    pass  # Mark as failed

# Metric computation
try:
    cohens_d = clusterer.compute_cohens_d(X_pca, labels)
except ZeroDivisionError:
    cohens_d = 0.0  # No variance case
```

---

## Validation Checklist

**Pre-execution:**
- [ ] GPU available (nvidia-smi)
- [ ] CUDA_VISIBLE_DEVICES set to single GPU
- [ ] All 6 models accessible on HuggingFace
- [ ] Python packages installed (evalplus, transformers, torch, radon, lizard, sklearn, scipy, matplotlib, pandas)

**Post-execution:**
- [ ] 6 models profiled successfully
- [ ] Cohen's d computed
- [ ] 6 figures saved to h-e1/figures/
- [ ] Gate status logged (PASS/FAIL)

---

**End of Logic Design**

*Ready for Phase 3 Config Design (03c_config.md) and Phase 4 Implementation (04_*.py)*
