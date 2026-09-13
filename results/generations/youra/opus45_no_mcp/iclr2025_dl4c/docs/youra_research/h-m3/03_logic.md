# Logic: H-M3 — Unreliable Localization Causes Gradient Noise

Applied: gradient-concentration-metric-pattern (reuse H-M1 policy-gradient token attribution)
Applied: ast-heuristic-ground-truth-pattern (reuse H-M2 error-type-dispatch localization)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (dual: H-M1 + H-M2)
**Status**: `h-m1/code/` and `h-m2/code/` not yet materialized on disk in this workspace; API signatures verified via architecture.md's prior Serena-sourced findings (see below), which document actual function signatures distinct from PRD pseudocode.
**Analyzed Path**: `h-m1/code/gradient_analysis.py`, `h-m1/code/sample_collector.py`, `h-m2/code/ground_truth.py`, `h-m2/code/config.py`
**Relevant Symbols**:
- `extract_token_gradients(model, input_ids, decoder_ids, rewards)` — policy-gradient reward vector, NOT `loss.backward()`
- `tokenize_with_lines`, `aggregate_gradients_by_line` (h-m1/gradient_analysis.py)
- `classify_error`, `parse_traceback_line`, `execute_code_safely`, `generate_synthetic_samples` (h-m1/sample_collector.py)
- `find_bug_line_ast(code, error_type, traceback_str)`, `annotate_ground_truth` (h-m2/ground_truth.py)
- `U_LINE_ERRORS`, `U_IGNORE_ERRORS` (h-m2/config.py)

**Deviation note**: PRD implies `loss.backward()` on a penalty-augmented total_loss. Actual mechanism (per H-M1) is `extract_token_gradients` fed a reward tensor with `-1.0` at target line, `-0.1` elsewhere. H-M3 must build this reward vector, not invent a new loss term.

---

## External Dependencies API

```python
# From: h-m1/code/gradient_analysis.py (ACTUAL CODE)
def tokenize_with_lines(code: str, tokenizer) -> Tuple[List[int], List[int]]:
    """Returns (input_ids, line_numbers) where line_numbers[i] = source line of token i."""
    ...

def extract_token_gradients(
    model, input_ids: torch.Tensor, decoder_ids: torch.Tensor, rewards: torch.Tensor
) -> torch.Tensor:
    """Policy-gradient token attribution. rewards: [T] penalty per decoder token.
    Returns per-token gradient magnitudes: [T]."""
    ...

def aggregate_gradients_by_line(
    token_grads: torch.Tensor, line_numbers: List[int]
) -> Dict[int, float]:
    """Sums/averages token grads per source line -> {line_no: grad_magnitude}."""
    ...

# From: h-m1/code/sample_collector.py (ACTUAL CODE)
def classify_error(error_type: str) -> str:
    """Returns 'U_line' or 'U_ignore'."""
    ...

def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extracts last frame line number from traceback string."""
    ...

def execute_code_safely(code: str, test_input: str) -> Tuple[bool, str, str]:
    """Runs code in sandbox. Returns (success, stdout, traceback_str)."""
    ...

def generate_synthetic_samples(n: int, error_type: str, seed: int) -> List[dict]:
    """Fallback synthetic sample generator (no ground_truth_line)."""
    ...

# From: h-m2/code/ground_truth.py (ACTUAL CODE)
def find_bug_line_ast(code: str, error_type: str, traceback_str: str) -> Optional[int]:
    """AST-heuristic dispatch on error_type. Returns actual_bug_line or None."""
    ...

def annotate_ground_truth(sample: dict) -> dict:
    """Adds 'ground_truth_line' key to sample dict via find_bug_line_ast."""
    ...

# From: h-m2/code/config.py (ACTUAL CODE)
U_LINE_ERRORS: set    # error types where traceback == ground truth
U_IGNORE_ERRORS: set  # error types where traceback often wrong
```

**Verified from**: `h-m1/code/`, `h-m2/code/` (per architecture.md Serena findings). H-M3 code adds `sys.path.insert(0, '../h-m1/code')` and `sys.path.insert(0, '../h-m2/code')` before importing.

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: sys.path adjacency idiom (matches H-M1/H-M2)

### API Signatures

```python
# h-m3/code/config.py
SEED = 42
MODEL_NAME = "Salesforce/codet5-small"
N_PER_CATEGORY = 500

@dataclass
class H_M3_Config:
    seed: int = SEED
    n_per_category: int = N_PER_CATEGORY
    output_dir: str = "results"
    figures_dir: str = "figures"

def setup_import_paths() -> None:
    """sys.path.insert for ../h-m1/code and ../h-m2/code."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | H_M3_Config dataclass | seed, n_per_category, output_dir, figures_dir |
| L-1-2 | sys.path wiring | insert h-m1/code, h-m2/code before H-M1/H-M2 imports |
| L-1-3 | Re-export U_LINE_ERRORS/U_IGNORE_ERRORS | import from h-m2 config |
| L-1-4 | dirs bootstrap | os.makedirs(output_dir/figures_dir, exist_ok=True) |

---

## A-2: Sample builder (real) [Complexity: 15, Budget: 15]

**Applied**: stratified-balanced-sampling-pattern

### API Signatures

```python
# h-m3/code/sample_builder.py
@dataclass
class NoiseSample:
    code: str
    traceback: str
    error_type: str          # "U_line" | "U_ignore"
    traceback_line: int
    ground_truth_line: int

def load_apps_dataset(split: str = "train"):
    """datasets.load_dataset('codeparrot/apps', split=split)"""
    ...

def collect_stratified_samples(
    model, tokenizer, dataset,
    n_per_category: int = 500, seed: int = 42,
) -> List[NoiseSample]:
    """Balances U_line/U_ignore to n_per_category each."""
    ...
```

### Pseudo-code

```
1. shuffle dataset (seed)
2. for each problem in dataset:
     code, test_input = sample.solution, sample.test_case
     success, stdout, tb = execute_code_safely(code, test_input)      # H-M1
     if success: continue
     err_type = classify_error(extract_exception_name(tb))            # H-M1
     category = "U_line" if err_type in U_LINE_ERRORS else "U_ignore" # H-M2 config
     if len(bucket[category]) >= n_per_category: continue
     tb_line = parse_traceback_line(tb)                                # H-M1
     gt_line = find_bug_line_ast(code, err_type, tb)                  # H-M2
     if tb_line is None or gt_line is None: continue
     bucket[category].append(NoiseSample(code, tb, category, tb_line, gt_line))
   until both buckets full or dataset exhausted
3. return bucket["U_line"] + bucket["U_ignore"]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_apps_dataset | HF datasets load + iterate |
| L-2-2 | execution + classification loop | reuse H-M1 execute_code_safely, classify_error |
| L-2-3 | ground truth annotation | reuse H-M2 find_bug_line_ast |
| L-2-4 | balance to 500/500, early stop | stratified bucket fill logic |

---

## A-3: Sample builder (synthetic fallback) [Complexity: 6, Budget: 6]

**Applied**: template-extension-pattern

### API Signatures

```python
def collect_synthetic_samples(n_per_category: int = 500, seed: int = 42) -> List[NoiseSample]:
    """Extends H-M1 generate_synthetic_samples output with ground_truth_line."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | call generate_synthetic_samples per category | H-M1 reuse |
| L-3-2 | derive ground_truth_line | apply find_bug_line_ast on synthetic code |
| L-3-3 | wrap into NoiseSample | map dict -> dataclass |
| L-3-4 | seed determinism check | assert reproducible across runs |

---

## A-4: Noise analysis core [Complexity: 13, Budget: 13]

**Applied**: reward-vector-attribution-pattern (H-M1 extract_token_gradients reuse)

### API Signatures

```python
# h-m3/code/noise_analysis.py
def build_reward_vector(line_numbers: List[int], target_line: int) -> torch.Tensor:
    """rewards: [T], -1.0 at target_line tokens, -0.1 elsewhere."""
    ...

def measure_sample_noise(
    model, tokenizer, sample: NoiseSample
) -> Optional[Dict[str, float]]:
    """Returns gt_grad, tb_grad, other_grad, gt_concentration, noise_ratio, traceback_matches_gt."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [T] | tokenized code, T = seq len |
| line_numbers | [T] | source line per token, from tokenize_with_lines |
| rewards | [T] | penalty vector from build_reward_vector |
| token_grads | [T] | from extract_token_gradients |
| line_grads | dict[int, float] | from aggregate_gradients_by_line |

### Pseudo-code

```
measure_sample_noise(model, tokenizer, sample):
  input_ids, line_numbers = tokenize_with_lines(sample.code, tokenizer)   # H-M1
  decoder_ids = tokenizer(sample.traceback, return_tensors="pt").input_ids
  rewards = build_reward_vector(line_numbers, sample.traceback_line)      # penalize at TB line (as-trained)
  token_grads = extract_token_gradients(model, input_ids, decoder_ids, rewards)  # H-M1
  line_grads = aggregate_gradients_by_line(token_grads, line_numbers)     # H-M1
  if sample.ground_truth_line not in line_grads: return None

  gt_grad = line_grads[sample.ground_truth_line]
  tb_grad = line_grads.get(sample.traceback_line, 0.0)
  other_lines = [l for l in line_grads if l not in (sample.ground_truth_line, sample.traceback_line)]
  other_grad = mean([line_grads[l] for l in other_lines]) if other_lines else 1e-8

  gt_concentration = gt_grad / (other_grad + 1e-8)
  noise_ratio = tb_grad / (gt_grad + 1e-8)
  traceback_matches_gt = (sample.traceback_line == sample.ground_truth_line)
  return {gt_grad, tb_grad, other_grad, gt_concentration, noise_ratio, traceback_matches_gt}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | build_reward_vector | penalty vector construction |
| L-4-2 | tokenize + gradient extraction glue | call H-M1 tokenize_with_lines, extract_token_gradients |
| L-4-3 | line aggregation + metric computation | gt_grad/tb_grad/other_grad/ratios |
| L-4-4 | None-safety for missing lines | guard when gt or tb line absent from line_grads |

---

## A-5: Stratified runner [Complexity: 6, Budget: 6]

### API Signatures

```python
def run_noise_analysis(
    model, tokenizer, samples: List[NoiseSample]
) -> Dict[str, List[Dict]]:
    """Stratified by error_type -> {"u_line": [...], "u_ignore": [...]}"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | iterate samples, call measure_sample_noise | skip None results |
| L-5-2 | bucket by error_type ("U_line"->"u_line", "U_ignore"->"u_ignore") | key normalization |
| L-5-3 | progress logging | tqdm over samples |
| L-5-4 | return dict of lists | final aggregation |

---

## A-6: Statistical tests [Complexity: 8, Budget: 8]

**Applied**: scipy.stats standard test suite

### API Signatures

```python
# h-m3/code/stats_tests.py
def compare_concentration(u_line: List[float], u_ignore: List[float]) -> Dict[str, float]:
    """t-test, Mann-Whitney U, Cohen's d, bootstrap 95% CI."""
    ...

def summarize_noise_ratio(u_ignore_noise_ratios: List[float]) -> Dict[str, float]:
    ...
```

### Pseudo-code

```
compare_concentration(u_line, u_ignore):
  t_stat, t_p = scipy.stats.ttest_ind(u_line, u_ignore)
  u_stat, u_p = scipy.stats.mannwhitneyu(u_line, u_ignore, alternative='greater')
  pooled_std = sqrt(((n1-1)*std1^2 + (n2-1)*std2^2) / (n1+n2-2))
  cohens_d = (mean(u_line) - mean(u_ignore)) / pooled_std
  ci_low, ci_high = bootstrap_ci(u_line, u_ignore, n_boot=10000, alpha=0.05)
  return {t_stat, t_p, u_stat, u_p, cohens_d, ci_low, ci_high}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | t-test + Mann-Whitney | scipy.stats calls |
| L-6-2 | Cohen's d | pooled std effect size |
| L-6-3 | bootstrap CI | resample-based 95% CI on mean diff |
| L-6-4 | summarize_noise_ratio | mean/median/std of noise_ratio, % > 1.0 |

---

## A-7: Visualization suite [Complexity: 10, Budget: 10]

### API Signatures

```python
# h-m3/code/visualization.py
def plot_concentration_boxplot(u_line: List[float], u_ignore: List[float], path: str) -> None: ...
def plot_noise_ratio_histogram(u_ignore_noise: List[float], path: str) -> None: ...
def plot_gradient_heatmap(sample_u_line: dict, sample_u_ignore: dict, path: str) -> None: ...
def plot_concentration_vs_noise_scatter(results: Dict[str, List[Dict]], path: str) -> None: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | boxplot (required) | seaborn boxplot, GT concentration by error_type |
| L-7-2 | noise ratio histogram | matplotlib hist, U_ignore only, line at ratio=1.0 |
| L-7-3 | gradient heatmap | one U_line + one U_ignore sample, per-line grad bars |
| L-7-4 | scatter concentration vs noise | color by error_type |

---

## A-8: End-to-end pipeline [Complexity: 7, Budget: 7]

### API Signatures

```python
# h-m3/code/run_analysis.py
def main() -> None:
    """Load model -> collect samples -> run_noise_analysis ->
    compare_concentration -> generate figures -> dump results/metrics.json."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | model/tokenizer load | AutoModel/AutoTokenizer from MODEL_NAME |
| L-8-2 | sample collection w/ fallback | try collect_stratified_samples, except -> collect_synthetic_samples |
| L-8-3 | run analysis + stats + figures | wire A-5, A-6, A-7 outputs |
| L-8-4 | dump results/metrics.json | json.dump with concentration/noise/stats results |

---

## A-9: Validation run [Complexity: 5, Budget: 5]

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | execute run_analysis.main() on 1000 samples | full pipeline smoke test |
| L-9-2 | verify PoC criteria | GT concentration U_line > U_ignore, p < 0.05 |
| L-9-3 | verify figures exist | 4 files in figures_dir |
| L-9-4 | verify metrics.json schema | required keys present |
