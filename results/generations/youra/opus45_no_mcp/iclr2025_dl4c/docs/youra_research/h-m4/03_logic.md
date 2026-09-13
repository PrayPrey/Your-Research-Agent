# Logic: H-M4 — Gating Removes Noise, Improves Signal

Applied: snr-aggregate-comparison-pattern (compare aggregate metrics between policies)
Applied: policy-gradient-attribution-pattern (reuse H-M3 gradient extraction)

## Codebase Analysis

**Project Type**: incremental_hypothesis (base: H-M3)
**Status**: API verified from H-M3 code
**Relevant Symbols**:
- `measure_sample_noise(model, tokenizer, sample)` → Dict with gt_grad, noise_ratio
- `run_noise_analysis(model, tokenizer, samples)` → {"u_line": [...], "u_ignore": [...]}
- `NoiseSample` dataclass

---

## External Dependencies API

```python
# From: h-m3/code/noise_analysis.py
def measure_sample_noise(
    model, tokenizer, sample: NoiseSample
) -> Optional[Dict[str, float]]:
    """Returns gt_grad, tb_grad, other_grad, gt_concentration, noise_ratio."""
    ...

def run_noise_analysis(
    model, tokenizer, samples: List[NoiseSample]
) -> Dict[str, List[Dict]]:
    """Stratified by error_type -> {"u_line": [...], "u_ignore": [...]}"""
    ...

# From: h-m3/code/sample_builder.py
@dataclass
class NoiseSample:
    code: str
    traceback: str
    error_type: str
    traceback_line: int
    ground_truth_line: int

def collect_stratified_samples(
    model, tokenizer, dataset,
    n_per_category: int = 250, seed: int = 42,
) -> List[NoiseSample]:
    ...
```

---

## A-1: Config setup [Complexity: 3, Budget: 3]

### API Signatures

```python
# h-m4/code/config.py
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
N_SAMPLES = 500

@dataclass
class H_M4_Config:
    seed: int = SEED
    n_bootstrap: int = 1000
    n_permutation: int = 9999
    significance_threshold: float = 0.05
    output_dir: str = "results"
    figures_dir: str = "figures"

def setup_import_paths() -> None:
    """sys.path.insert for ../h-m3/code."""
    ...

def get_config() -> H_M4_Config:
    return H_M4_Config()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | H_M4_Config dataclass | bootstrap/permutation params |
| L-1-2 | sys.path wiring | insert h-m3/code before imports |
| L-1-3 | dirs bootstrap | os.makedirs(output_dir/figures_dir) |

---

## A-2: SNR analysis core [Complexity: 8, Budget: 8]

### API Signatures

```python
# h-m4/code/snr_analysis.py
@dataclass
class SNRResult:
    snr: float
    mean_signal: float
    mean_noise: float
    n_samples: int
    signals: List[float]
    noises: List[float]

def extract_signal_noise(result: Dict[str, float]) -> Tuple[float, float]:
    """Extract signal (gt_grad) and noise (other_grad std) from H-M3 result."""
    signal = result["gt_grad"]
    noise = result.get("other_grad_std", result["other_grad"])
    return signal, noise

def compute_policy_snr(
    results: List[Dict[str, float]], policy: str
) -> SNRResult:
    """Compute aggregate SNR for policy."""
    ...

def compare_policies(
    u_line_results: List[Dict], u_ignore_results: List[Dict]
) -> Dict[str, SNRResult]:
    """
    fine_always: all U_line + U_ignore
    fine_gated: U_line only
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| signals | [N] | float list, gradient at GT |
| noises | [N] | float list, gradient variance elsewhere |
| snr | scalar | mean(signals) / mean(noises) |

### Pseudo-code

```
compute_policy_snr(results, policy):
  signals, noises = [], []
  for r in results:
    if r is not None:
      signal, noise = extract_signal_noise(r)
      signals.append(signal)
      noises.append(noise)
  mean_signal = mean(signals)
  mean_noise = mean(noises) + 1e-8
  snr = mean_signal / mean_noise
  return SNRResult(snr, mean_signal, mean_noise, len(signals), signals, noises)

compare_policies(u_line, u_ignore):
  all_results = u_line + u_ignore
  snr_always = compute_policy_snr(all_results, "fine_always")
  snr_gated = compute_policy_snr(u_line, "fine_gated")
  return {"fine_always": snr_always, "fine_gated": snr_gated}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | SNRResult dataclass | signal/noise aggregates |
| L-2-2 | extract_signal_noise | parse H-M3 result dict |
| L-2-3 | compute_policy_snr | aggregate signals/noises to SNR |
| L-2-4 | compare_policies | compute both policies |

---

## A-3: Statistical tests [Complexity: 7, Budget: 7]

### API Signatures

```python
# h-m4/code/stats_tests.py
def bootstrap_snr_ci(
    signals: List[float], noises: List[float], n_boot: int = 1000, alpha: float = 0.05
) -> Tuple[float, float]:
    """95% CI for SNR via bootstrap."""
    ...

def permutation_test(
    snr_gated: SNRResult, snr_always: SNRResult, n_perm: int = 9999
) -> float:
    """Permutation test for SNR difference. Returns p-value."""
    ...

def compute_improvement(snr_gated: float, snr_always: float) -> float:
    """Percentage improvement: (gated - always) / always * 100."""
    ...
```

### Pseudo-code

```
bootstrap_snr_ci(signals, noises, n_boot, alpha):
  snrs = []
  for _ in range(n_boot):
    idx = random.choice(len(signals), len(signals), replace=True)
    s = mean([signals[i] for i in idx])
    n = mean([noises[i] for i in idx]) + 1e-8
    snrs.append(s / n)
  return percentile(snrs, alpha/2*100), percentile(snrs, (1-alpha/2)*100)

permutation_test(snr_gated, snr_always, n_perm):
  observed_diff = snr_gated.snr - snr_always.snr
  combined_signals = snr_gated.signals + snr_always.signals
  combined_noises = snr_gated.noises + snr_always.noises
  n_gated = len(snr_gated.signals)
  count = 0
  for _ in range(n_perm):
    perm = shuffle(range(len(combined_signals)))
    s1 = mean([combined_signals[i] for i in perm[:n_gated]]) / mean([combined_noises[i] for i in perm[:n_gated]])
    s2 = mean([combined_signals[i] for i in perm[n_gated:]]) / mean([combined_noises[i] for i in perm[n_gated:]])
    if abs(s1 - s2) >= abs(observed_diff):
      count += 1
  return (count + 1) / (n_perm + 1)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | bootstrap_snr_ci | resample signals/noises, compute SNR |
| L-3-2 | permutation_test | shuffle combined, compare diff |
| L-3-3 | compute_improvement | percentage calculation |
| L-3-4 | summary dict | aggregate all stats into results |

---

## A-4: Visualization suite [Complexity: 8, Budget: 8]

### API Signatures

```python
# h-m4/code/visualization.py
def plot_snr_comparison(snr_always: SNRResult, snr_gated: SNRResult, 
                        ci_always: Tuple, ci_gated: Tuple, path: str) -> None:
    """Bar chart: SNR for each policy with error bars."""
    ...

def plot_snr_bootstrap_distribution(always_dist: List[float], gated_dist: List[float], path: str) -> None:
    """Boxplot of bootstrap SNR distributions."""
    ...

def plot_signal_noise_scatter(u_line: List[Dict], u_ignore: List[Dict], path: str) -> None:
    """Scatter: signal vs noise, colored by error type."""
    ...

def plot_error_type_contribution(u_line: List[Dict], u_ignore: List[Dict], path: str) -> None:
    """Stacked bar: contribution of each error type to SNR."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | plot_snr_comparison | bar chart with CI error bars |
| L-4-2 | plot_snr_bootstrap_distribution | boxplot of bootstrap samples |
| L-4-3 | plot_signal_noise_scatter | scatter by error type |
| L-4-4 | plot_error_type_contribution | stacked contribution |

---

## A-5: End-to-end pipeline [Complexity: 5, Budget: 5]

### API Signatures

```python
# h-m4/code/run_experiment.py
def main() -> None:
    """Load model -> collect samples (H-M3) -> run_noise_analysis (H-M3) ->
    compare_policies -> stats -> figures -> dump metrics.json."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | model/tokenizer load | AutoModel/AutoTokenizer |
| L-5-2 | sample collection | call H-M3 collect_stratified_samples |
| L-5-3 | analysis + stats + figures | wire A-2, A-3, A-4 |
| L-5-4 | dump metrics.json | results output |

---

## A-6: Validation run [Complexity: 4, Budget: 4]

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | execute run_experiment.main() | full pipeline |
| L-6-2 | verify PoC criteria | SNR_gated > SNR_always, p < 0.05 |
| L-6-3 | verify figures exist | 4 files in figures_dir |
| L-6-4 | verify metrics.json schema | required keys present |
