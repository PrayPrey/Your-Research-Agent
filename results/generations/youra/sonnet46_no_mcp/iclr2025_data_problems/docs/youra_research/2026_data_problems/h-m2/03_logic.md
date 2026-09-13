# Logic Document: H-M2
# Domain-Stratified Contamination Re-Analysis

**Hypothesis**: H-M2 | **Type**: MECHANISM | **Date**: 2026-05-04

Applied: Domain-stratified-statistical-reanalysis (scipy.stats.mannwhitneyu one-tailed + Cohen's d)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental over H-M1 implementation)
**Status**: API signatures verified from base code (file reads, no MCP available in test environment)
**Analyzed Path**: `docs/youra_research/20260504_data_problems/h-m1/code/`
**Relevant Symbols**:
- `StatsAnalyzer.__init__(self, config: "Config")` — same pattern reused
- `Visualizer.__init__(self, config: "Config")` — same pattern; `_save(name: str)` helper
- `Config` — dataclass with `seed`, `gate_p_threshold`, `figures_dir`, `results_dir`; `load_config()` returns `Config`
- H-M1 `StatsAnalyzer.assert_gate(p_value: float) -> None` — H-M2 version returns `bool` (different signature, intentional)
- H-M1 uses `from __future__ import annotations` + `TYPE_CHECKING` guard for Config import

---

## External Dependencies API

### API Signatures (From Actual H-M1 Code)

H-M2 does NOT import H-M1 modules directly. Data dependency only.

```python
# From: h-m1/code/config.py (ACTUAL CODE)
# H-M1 Config has: seed, gate_p_threshold, figures_dir, results_dir, mmlu_tasks (57 tasks list)
# H-M2 reimplements Config with different fields — no import.

# From: h-m1/code/visualizer.py (ACTUAL CODE)
class Visualizer:
    def __init__(self, config: "Config"):
        self.config = config
        Path(config.figures_dir).mkdir(parents=True, exist_ok=True)  # pattern reused

    def _save(self, name: str) -> None:
        """Save figure to figures_dir/name. Pattern reused in H-M2."""
        ...

# From: h-m1/code/stats_analyzer.py (ACTUAL CODE)
class StatsAnalyzer:
    def __init__(self, config: "Config"):
        self.config = config
    # H-M1 uses kruskal_wallis, dunn_posthoc, spearman_wimbd
    # H-M2 adds: mann_whitney_directional, run_directional_tests, cohens_d
    # H-M2 assert_gate(directional_tests: dict) -> bool  (DIFFERENT from H-M1 which takes p_value: float)
```

**Verified from**: `h-m1/code/` (actual implementation)

---

## A-2: Domain Classifier [Complexity: 9, Budget: 2 subtasks]

Applied: Rule-based deterministic classification (prefix match + explicit frozenset)

### API Signatures

```python
class DomainClassifier:
    """Maps benchmark sub-tasks to academic or commonsense domain."""

    COMMONSENSE_TASKS: frozenset = frozenset({
        # HellaSwag (1)
        "hellaswag",
        # BIG-Bench Hard abstract/commonsense reasoning subtasks (~10)
        "bbh_causal_judgement",
        "bbh_date_understanding",
        "bbh_disambiguation_qa",
        "bbh_formal_fallacies",
        "bbh_geometric_shapes",
        "bbh_hyperbaton",
        "bbh_logical_deduction_five_objects",
        "bbh_logical_deduction_seven_objects",
        "bbh_logical_deduction_three_objects",
        "bbh_movie_recommendation",
        "bbh_navigate",
        "bbh_penguins_in_a_table",
        "bbh_reasoning_about_colored_objects",
        "bbh_ruin_names",
        "bbh_salient_translation_error_detection",
        "bbh_snarks",
        "bbh_sports_understanding",
        "bbh_temporal_sequences",
        "bbh_tracking_shuffled_objects_five_objects",
        "bbh_tracking_shuffled_objects_seven_objects",
        "bbh_tracking_shuffled_objects_three_objects",
        "bbh_web_of_lies",
        "bbh_word_sorting",
    })
    # All 57 MMLU sub-tasks → academic (see H-M1 config.mmlu_tasks for full list)

    def classify(self, subtask_name: str) -> str:
        """Returns 'academic' or 'commonsense'. x: str -> str"""
        ...

    def build_domain_map(self, subtask_names: list[str]) -> dict[str, str]:
        """Returns {subtask_name: 'academic'|'commonsense'} for all 59 subtasks."""
        ...

    def get_groups(
        self,
        matrix: dict,
        domain_map: dict[str, str],
        corpus: str,
    ) -> tuple[list[float], list[float]]:
        """Returns (academic_rates, commonsense_rates) for given corpus.
        matrix: {subtask: {corpus: rate}}
        """
        ...
```

### Pseudo-code

```
classify(subtask_name):
    if subtask_name in COMMONSENSE_TASKS:
        return "commonsense"
    if subtask_name.startswith("bbh_") or subtask_name == "hellaswag":
        return "commonsense"   # fallback for any unlisted bbh_ prefix
    return "academic"

build_domain_map(subtask_names):
    return {name: classify(name) for name in subtask_names}

get_groups(matrix, domain_map, corpus):
    academic_rates = [matrix[t][corpus] for t in matrix if domain_map.get(t) == "academic"]
    commonsense_rates = [matrix[t][corpus] for t in matrix if domain_map.get(t) == "commonsense"]
    return academic_rates, commonsense_rates
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | classify + build_domain_map | Implement COMMONSENSE_TASKS frozenset, classify(), build_domain_map() with full 59-subtask coverage |
| L-2-2 | get_groups | Implement get_groups() extracting per-corpus academic/commonsense rate lists from 59×3 matrix |

---

## A-5: Directional Statistical Tests [Complexity: 13, Budget: 4 subtasks]

Applied: scipy.stats.mannwhitneyu one-tailed + pooled-std Cohen's d

### API Signatures

```python
class StatsAnalyzer:
    def __init__(self, config: "Config"):
        """config.alpha used for direction_confirmed threshold."""
        self.config = config

    def mann_whitney_directional(
        self,
        group_a: list[float],
        group_b: list[float],
        alternative: str = "greater",
    ) -> dict:
        """One-tailed Mann-Whitney U test: group_a {alternative} group_b.
        Returns {stat, p, effect_size_r, direction_confirmed}.
        group_a, group_b: lists of contamination rates
        """
        ...

    def cohens_d(
        self,
        group_a: list[float],
        group_b: list[float],
    ) -> float:
        """Cohen's d = (mean_a - mean_b) / pooled_std. Returns float."""
        ...

    def run_directional_tests(
        self,
        stratified: dict,
    ) -> dict:
        """Runs directional tests for all 3 corpora.
        stratified: {corpus: {domain: mean, domain+"_rates": list[float]}}
        Returns {test_name: {stat, p, effect_size_r, direction_confirmed, cohens_d}}.
        Test directions:
          pile: academic > commonsense  (alternative="greater")
          c4: commonsense > academic    (alternative="greater", swap groups)
          redpajama: academic > commonsense (exploratory, alternative="greater")
        """
        ...

    def assert_gate(self, directional_tests: dict) -> bool:
        """Returns True if ≥2 corpora have direction_confirmed=True.
        directional_tests: output of run_directional_tests()
        """
        ...
```

### Tensor Shapes (rate lists)

| Variable | Shape | Note |
|----------|-------|------|
| group_a / group_b | [N_domain] | N_academic ~48, N_commonsense ~11 |
| stratified | {3 corpora × 2 domains} | 6-cell dict with _rates lists |
| directional_tests | {3 test_names} | one entry per corpus |

### Pseudo-code

```
mann_whitney_directional(group_a, group_b, alternative="greater"):
    from scipy.stats import mannwhitneyu
    stat, p = mannwhitneyu(group_a, group_b, alternative=alternative)
    n1, n2 = len(group_a), len(group_b)
    # rank-biserial effect size r = 1 - 2U/(n1*n2)
    effect_size_r = 1.0 - (2.0 * stat) / (n1 * n2)
    direction_confirmed = bool(p < self.config.alpha)
    return {"stat": stat, "p": p, "effect_size_r": effect_size_r,
            "direction_confirmed": direction_confirmed}

cohens_d(group_a, group_b):
    n1, n2 = len(group_a), len(group_b)
    mean_diff = np.mean(group_a) - np.mean(group_b)
    pooled_std = sqrt(((n1-1)*var(group_a) + (n2-1)*var(group_b)) / (n1+n2-2))
    return mean_diff / pooled_std if pooled_std > 0 else 0.0

run_directional_tests(stratified):
    tests = {}
    # Pile: academic > commonsense
    a_rates = stratified["pile"]["academic_rates"]
    c_rates = stratified["pile"]["commonsense_rates"]
    res = mann_whitney_directional(a_rates, c_rates, "greater")
    res["cohens_d"] = cohens_d(a_rates, c_rates)
    tests["pile_academic_gt_commonsense"] = res

    # C4: commonsense > academic (swap: group_a=commonsense)
    a_rates = stratified["c4"]["academic_rates"]
    c_rates = stratified["c4"]["commonsense_rates"]
    res = mann_whitney_directional(c_rates, a_rates, "greater")  # commonsense as group_a
    res["cohens_d"] = cohens_d(c_rates, a_rates)
    tests["c4_commonsense_gt_academic"] = res

    # RedPajama: academic > commonsense (exploratory)
    a_rates = stratified["redpajama"]["academic_rates"]
    c_rates = stratified["redpajama"]["commonsense_rates"]
    res = mann_whitney_directional(a_rates, c_rates, "greater")
    res["cohens_d"] = cohens_d(a_rates, c_rates)
    tests["redpajama_academic_gt_commonsense"] = res

    return tests

assert_gate(directional_tests):
    confirmed = sum(1 for t in directional_tests.values() if t["direction_confirmed"])
    return confirmed >= self.config.min_corpora_directional_confirmed  # ≥2
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | mann_whitney_directional | scipy.stats.mannwhitneyu call, effect_size_r computation, direction_confirmed flag |
| L-5-2 | run_directional_tests | Wire all 3 corpora with correct direction per corpus; attach cohens_d |
| L-5-3 | cohens_d | Pooled std computation, return float |
| L-5-4 | assert_gate | Count direction_confirmed across tests dict, return bool (≥2) |

---

## A-7: Visualization [Complexity: 11, Budget: 3 subtasks]

Applied: seaborn heatmap + matplotlib multi-panel with H-M1 Visualizer._save() pattern

### API Signatures

```python
DOMAIN_COLORS = {"academic": "#1f77b4", "commonsense": "#ff7f0e"}
FIGURE_DPI = 150

class Visualizer:
    def __init__(self, config: "Config"):
        """config.figures_dir used for all saves."""
        self.config = config
        Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    def _save(self, name: str) -> None:
        """Save plt figure to figures_dir/name and close."""
        ...

    def plot_domain_corpus_heatmap(self, stratified: dict) -> None:
        """2×3 seaborn heatmap: rows=domain (academic/commonsense), cols=corpus (pile/c4/redpajama).
        Values are mean contamination rates (%). Annotated with rate values.
        Saves: figures/domain_corpus_heatmap.png
        stratified: {corpus: {domain: mean_rate}}
        """
        ...

    def plot_domain_boxplots(self, stratified: dict) -> None:
        """3-panel figure (one per corpus): academic vs commonsense rate distributions.
        Mann-Whitney p-value annotated on each panel.
        Saves: figures/domain_boxplots.png
        stratified: {corpus: {domain: mean, domain+"_rates": list[float]}}
        """
        ...

    def plot_top5_per_corpus(
        self,
        top5: dict,
        domain_map: dict[str, str],
    ) -> None:
        """3 horizontal bar charts (one per corpus): top-5 contaminated subtasks.
        Bars color-coded by domain (DOMAIN_COLORS).
        Saves: figures/top5_per_corpus.png
        top5: {corpus: [{"subtask": str, "rate": float, "domain": str}]}
        """
        ...

    def plot_directional_test_summary(self, directional_tests: dict) -> None:
        """Annotated bar chart: p-values per directional test + effect size annotations.
        Horizontal dashed line at alpha=0.05.
        Saves: figures/directional_test_summary.png
        directional_tests: output of StatsAnalyzer.run_directional_tests()
        """
        ...
```

### Pseudo-code

```
plot_domain_corpus_heatmap(stratified):
    # Build 2×3 DataFrame
    domains = ["academic", "commonsense"]
    corpora = ["pile", "c4", "redpajama"]
    data = DataFrame({c: [stratified[c][d]*100 for d in domains] for c in corpora},
                     index=domains)
    fig, ax = subplots(figsize=(8, 4))
    sns.heatmap(data, ax=ax, annot=True, fmt=".2f", cmap="YlOrRd",
                cbar_kws={"label": "Mean Contamination Rate (%)"})
    ax.set_title("Domain × Corpus Contamination Heatmap")
    _save("domain_corpus_heatmap.png")

plot_domain_boxplots(stratified):
    fig, axes = subplots(1, 3, figsize=(14, 5), sharey=True)
    for i, corpus in enumerate(["pile", "c4", "redpajama"]):
        ax = axes[i]
        acad = stratified[corpus]["academic_rates"]
        comm = stratified[corpus]["commonsense_rates"]
        ax.boxplot([acad, comm], labels=["academic", "commonsense"],
                   patch_artist=True, ...)
        # annotate p-value from directional test if available
        ax.set_title(corpus)
    plt.tight_layout()
    _save("domain_boxplots.png")

plot_top5_per_corpus(top5, domain_map):
    fig, axes = subplots(1, 3, figsize=(15, 5))
    for i, corpus in enumerate(["pile", "c4", "redpajama"]):
        items = top5[corpus]  # list of {subtask, rate, domain}
        names = [x["subtask"] for x in items]
        rates = [x["rate"]*100 for x in items]
        colors = [DOMAIN_COLORS[x["domain"]] for x in items]
        axes[i].barh(names, rates, color=colors)
        axes[i].set_title(f"{corpus} Top-5")
    _save("top5_per_corpus.png")

plot_directional_test_summary(directional_tests):
    fig, ax = subplots(figsize=(8, 5))
    test_names = list(directional_tests.keys())
    p_values = [directional_tests[t]["p"] for t in test_names]
    colors = ["green" if directional_tests[t]["direction_confirmed"] else "salmon"
              for t in test_names]
    ax.bar(test_names, p_values, color=colors)
    ax.axhline(y=0.05, color="red", linestyle="--", label="α=0.05")
    # annotate effect_size_r on each bar
    for j, t in enumerate(test_names):
        r = directional_tests[t]["effect_size_r"]
        ax.text(j, p_values[j]+0.002, f"r={r:.2f}", ha="center", fontsize=9)
    ax.set_ylabel("p-value (one-tailed)")
    ax.set_title("Directional Test Summary")
    ax.legend()
    _save("directional_test_summary.png")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_domain_corpus_heatmap | seaborn heatmap 2×3 with rate annotations, save domain_corpus_heatmap.png |
| L-7-2 | plot_domain_boxplots | 3-panel boxplots academic vs commonsense per corpus with p-value annotation |
| L-7-3 | plot_top5_per_corpus + plot_directional_test_summary | Combined: domain-colored top-5 bar charts + p-value summary bar chart with effect size labels |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments / table
- [x] Subtask count within budget (9 total: 4+3+2)
- [x] "Codebase Analysis (Serena)" section included
- [x] "External Dependencies API" section included
- [x] Parameter names verified from H-M1 actual code
- [x] COMMONSENSE_TASKS lists all bbh_ tasks explicitly
- [x] run_directional_tests uses correct direction per corpus (pile: acad>comm, c4: comm>acad swap, rp: acad>comm exploratory)
- [x] assert_gate returns bool (≥2), not void
