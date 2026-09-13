# Logic: H-M2 (Statistical Analysis)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No `h-m2/code/` exists. No H-E1 `code/` exists either (H-E1 is green-field too) — only its data artifact `h-e1/results/js_divergence_matrix.npy` is consumed, not any code interface. Serena skipped per green-field rule; verified via architecture doc instead.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation from scratch.

---

## M2-1: Config + Data Loading [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch/NumPy artifact-loading pattern (KB search returned no directly relevant statistical-testing results; using scipy.stats.mannwhitneyu standard pattern per experiment brief).

### API Signatures

```python
# config.py
BENCHMARK_NAMES: list[str] = ["trivia_qa", "natural_questions", "squad", "pop_qa", "halueval_qa", "fever"]
FACTUAL_FAMILY: set[str] = {"trivia_qa", "natural_questions", "squad"}
ENTITY_FAMILY: set[str] = {"pop_qa", "halueval_qa", "fever"}
JS_MATRIX_PATH: str = "h-e1/results/js_divergence_matrix.npy"
FIGURES_DIR: str = "h-m2/figures"
P_VALUE_THRESHOLD: float = 0.05
SAME_FAMILY_MEAN_THRESHOLD: float = 0.15

# data.py
def load_js_matrix(path: str = JS_MATRIX_PATH) -> np.ndarray:
    """Load 6x6 symmetric JS-divergence matrix. Raises FileNotFoundError if missing."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1-1 | Define config constants | Names, families, paths, thresholds |
| L-M2-1-2 | `load_js_matrix` | `np.load(path)`, validate shape == (6,6) |
| L-M2-1-3 | Shape/symmetry validation | Assert `np.allclose(m, m.T)` |
| L-M2-1-4 | Error handling | Raise `FileNotFoundError` with clear message if path missing |

---

## M2-2: Fallback Recompute Path [Complexity: 8, Budget: 8]

**Applied**: scipy.stats.gaussian_kde + scipy.spatial.distance.jensenshannon (per experiment brief reference implementation).

### API Signatures

```python
# data.py
def recompute_js_matrix_fallback(
    names: list[str] = BENCHMARK_NAMES,
    entropy_dir: str = "h-e1/results",
    n_points: int = 1000,
) -> np.ndarray:
    """Fallback: recompute 6x6 JS matrix from H-E1 entropy_{name}.npy arrays via KDE."""
    ...

def _compute_js_divergence(dist_1: np.ndarray, dist_2: np.ndarray, n_points: int = 1000) -> float:
    """KDE both 1D entropy arrays on common support, normalize, return JS-divergence (jensenshannon**2)."""
    ...
```

### Pseudo-code

```
1. for each name in names: entropy[name] = np.load(f"{entropy_dir}/entropy_{name}.npy")  # [S_i] 1D array
2. matrix = zeros((6, 6))
3. for i, j in upper_triangle_pairs(6):
4.     matrix[i,j] = matrix[j,i] = _compute_js_divergence(entropy[names[i]], entropy[names[j]], n_points)
5. return matrix
```

`_compute_js_divergence`: fit `gaussian_kde` per array -> shared `linspace(min, max, n_points)` support -> evaluate both KDEs -> normalize via `np.trapz` -> `jensenshannon(p, q) ** 2`.

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-2-1 | Load entropy arrays | `np.load` per benchmark name, handle missing file |
| L-M2-2-2 | KDE fitting | `gaussian_kde` per distribution |
| L-M2-2-3 | Common support + normalize | `linspace`, `np.trapz` normalization |
| L-M2-2-4 | JS-divergence per pair | `jensenshannon(p, q) ** 2`, fill symmetric matrix |
| L-M2-2-5 | Diagonal handling | Set diagonal to 0 |
| L-M2-2-6 | `load_js_matrix` fallback wiring | try `load_js_matrix`, except `FileNotFoundError`: call fallback |
| L-M2-2-7 | Fallback matrix validation | Assert shape/symmetry same as primary path |
| L-M2-2-8 | Fallback unit smoke test | Compare fallback output shape/range against primary artifact (if present) |

---

## M2-3: Pair Extraction [Complexity: 5, Budget: 5]

### API Signatures

```python
# analysis.py
def extract_pairs(js_matrix: np.ndarray, names: list[str]) -> tuple[list[float], list[float]]:
    """Split upper-triangle of 6x6 matrix into (same_family_js[6], cross_family_js[9])."""
    ...
```

### Pseudo-code

```
1. same, cross = [], []
2. for i in range(n):
3.   for j in range(i+1, n):
4.     val = js_matrix[i, j]
5.     both_factual = names[i] in FACTUAL_FAMILY and names[j] in FACTUAL_FAMILY
6.     both_entity  = names[i] in ENTITY_FAMILY  and names[j] in ENTITY_FAMILY
7.     (same if (both_factual or both_entity) else cross).append(val)
8. return same, cross  # len(same)==6, len(cross)==9
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-3-1 | Upper-triangle iteration | `i in range(n), j in range(i+1,n)` |
| L-M2-3-2 | Family membership check | `both_factual` / `both_entity` boolean logic |
| L-M2-3-3 | Same/cross list assembly | Append to respective lists |
| L-M2-3-4 | Count assertion | `assert len(same)==6 and len(cross)==9` |
| L-M2-3-5 | Pair-to-name mapping (debug) | Optional list of (name_i, name_j, category) for logging |

---

## M2-4: Mann-Whitney U + Cliff's Delta [Complexity: 6, Budget: 6]

### API Signatures

```python
# analysis.py
def cliffs_delta(x: list[float], y: list[float]) -> float:
    """Cliff's delta effect size for x vs y. Range [-1, 1]."""
    ...

def test_error_family_hypothesis(js_matrix: np.ndarray, names: list[str] = BENCHMARK_NAMES) -> dict:
    """Mann-Whitney U (one-sided, alternative='less': same < cross) + Cliff's delta.
    Returns: p_value, same_family_mean, cross_family_mean, same_family_values,
    cross_family_values, effect_size_cliffs_d, n_same, n_cross."""
    ...
```

### Pseudo-code

```
1. same, cross = extract_pairs(js_matrix, names)
2. statistic, p_value = scipy.stats.mannwhitneyu(same, cross, alternative='less')
3. effect_size = cliffs_delta(same, cross)  # sum(sign(yj - xi)) / (n1*n2)
4. return dict(p_value=p_value, same_family_mean=np.mean(same), cross_family_mean=np.mean(cross),
               same_family_values=same, cross_family_values=cross,
               effect_size_cliffs_d=effect_size, n_same=len(same), n_cross=len(cross))
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-4-1 | `cliffs_delta` core loop | Pairwise comparison count / (n1*n2) |
| L-M2-4-2 | `cliffs_delta` vectorized variant | Optional broadcasting for speed (6x9=54 comparisons, trivial either way) |
| L-M2-4-3 | `mannwhitneyu` call | `alternative='less'`, capture statistic + p_value |
| L-M2-4-4 | Result dict assembly | All 8 keys per spec |
| L-M2-4-5 | CI for Cliff's delta (for forest plot) | Bootstrap or normal-approx CI on effect size |
| L-M2-4-6 | Edge-case guard | Handle ties / empty groups defensively (asserts, not required in nominal path) |

---

## M2-5: Box Plot + Violin Visualization [Complexity: 5, Budget: 5]

### API Signatures

```python
# visualize.py
def plot_family_boxplot(same: list[float], cross: list[float], out_path: str) -> None:
    """Box plot: same-family vs cross-family JS-divergence. Saves to out_path."""
    ...

def plot_family_violin(same: list[float], cross: list[float], out_path: str) -> None:
    """Violin plot with individual points overlaid (stripplot/jitter)."""
    ...
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-5-1 | Box plot base | `matplotlib`/`seaborn` boxplot, 2 categories |
| L-M2-5-2 | Box plot styling | Labels, title, threshold line at 0.15 |
| L-M2-5-3 | Violin plot base | `seaborn.violinplot` |
| L-M2-5-4 | Overlay individual points | `seaborn.stripplot` jittered on top of violin |
| L-M2-5-5 | Save + close figures | `plt.savefig(out_path, dpi=150, bbox_inches='tight'); plt.close()` |

---

## M2-6: Heatmap + Forest Plot Visualization [Complexity: 6, Budget: 6]

### API Signatures

```python
# visualize.py
def plot_js_heatmap_with_families(js_matrix: np.ndarray, names: list[str], out_path: str) -> None:
    """6x6 heatmap annotated with family boundary lines/blocks."""
    ...

def plot_effect_size_forest(effect_size: float, ci: tuple[float, float], out_path: str) -> None:
    """Forest plot: point estimate (Cliff's delta) + CI whiskers."""
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-6-1 | Heatmap base | `seaborn.heatmap(js_matrix, xticklabels=names, yticklabels=names)` |
| L-M2-6-2 | Family boundary annotation | Draw rect/lines separating Factual (0-2) vs Entity (3-5) blocks |
| L-M2-6-3 | Heatmap colorbar/labels | Title, colorbar label "JS-divergence" |
| L-M2-6-4 | Forest plot point + CI | `errorbar` with single point + horizontal CI whisker |
| L-M2-6-5 | Forest plot reference lines | Vertical line at 0 (no effect) and -0.5 (large effect threshold) |
| L-M2-6-6 | Save + close both figures | `dpi=150, bbox_inches='tight'` |

---

## M2-7: Pipeline Orchestration + Gate Logging [Complexity: 5, Budget: 5]

### API Signatures

```python
# run.py
def main() -> None:
    """load js_matrix -> test_error_family_hypothesis -> visualize -> log gate decision."""
    ...
```

### Pseudo-code

```
1. js_matrix = load_js_matrix()  # or recompute_js_matrix_fallback() on FileNotFoundError
2. result = test_error_family_hypothesis(js_matrix, BENCHMARK_NAMES)
3. plot_family_boxplot(result["same_family_values"], result["cross_family_values"], f"{FIGURES_DIR}/boxplot.png")
4. plot_family_violin(result["same_family_values"], result["cross_family_values"], f"{FIGURES_DIR}/violin.png")
5. plot_js_heatmap_with_families(js_matrix, BENCHMARK_NAMES, f"{FIGURES_DIR}/heatmap.png")
6. plot_effect_size_forest(result["effect_size_cliffs_d"], ci, f"{FIGURES_DIR}/forest.png")
7. gate_pass = result["p_value"] < P_VALUE_THRESHOLD and result["same_family_mean"] < SAME_FAMILY_MEAN_THRESHOLD
8. append gate_pass, result to 04_validation.md
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-7-1 | Load-with-fallback wiring | try primary load, except -> fallback recompute |
| L-M2-7-2 | Run analysis + visualization calls | Sequential calls per pseudo-code |
| L-M2-7-3 | Gate decision logic | `p<0.05 and same_family_mean<0.15` boolean |
| L-M2-7-4 | Gate logging to 04_validation.md | Write result dict + gate_pass + PASS/EXPLORE label |
| L-M2-7-5 | `__main__` entrypoint | `if __name__ == "__main__": main()` |

---

## Data Flow

`js_divergence_matrix.npy` (6x6) -> `load_js_matrix` (fallback: `recompute_js_matrix_fallback`) -> `extract_pairs` (6 same / 9 cross) -> `test_error_family_hypothesis` (Mann-Whitney U + Cliff's delta) -> gate decision (p<0.05 and same_family_mean<0.15) -> `visualize.py` (4 figures to `h-m2/figures/`) -> `04_validation.md` log.
