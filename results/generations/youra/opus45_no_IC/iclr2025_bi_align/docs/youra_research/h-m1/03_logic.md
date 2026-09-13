# Logic: H-M1 (User Adaptation to AI Patterns)

**Type:** MECHANISM | **Budget:** 12 subtasks

**Applied:** No KB match (searched "lagged cross-correlation time series analysis Python" — only irrelevant HF forum results); using standard scipy.stats.pearsonr + pandas shift pattern per architecture/brief spec.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** No `h-e1/code/` directory exists on disk (spec-only, per architecture doc). Serena `find_symbol`/`get_symbols_overview` skipped — nothing to query, no code present at `docs/youra_research/h-e1/`. This matches architecture doc's own finding.
**Analyzed Path:** N/A — verified absence via architecture doc; no code directory to search.
**Relevant Symbols:** None found — H-M1 implementation will define fallback loader per `DATASET_FALLBACK` since `h-e1/code/bcs.py` is unverified/spec-only.

---

## A-1: Data Loading [Complexity: 8, Budget: 8]

**Applied:** Standard pickle + HF datasets fallback pattern

### API Signatures

```python
# data.py
def load_checkpoint(path: str = BCS_CHECKPOINT_PATH) -> dict:
    """Load H-E1 pkl. Returns {'conversations': list, 'complexity_data': list}."""
    ...

def load_fallback(dataset_name: str = DATASET_FALLBACK) -> dict:
    """Reload HF dataset + recompute complexity if checkpoint missing."""
    ...

def build_trajectories(checkpoint: dict) -> list[tuple[list[float], list[float]]]:
    """Extract (user_complexity[t], ai_complexity[t]) per conversation."""
    ...

def filter_min_turns(trajectories: list[tuple[list[float], list[float]]], min_turns: int = MIN_ALIGNED_TURNS) -> list:
    """Keep only conversations with >= min_turns aligned pairs."""
    ...
```

### Pseudo-code

```
1. try: checkpoint = load_checkpoint(BCS_CHECKPOINT_PATH)
2. except FileNotFoundError: checkpoint = load_fallback(DATASET_FALLBACK)
3. trajectories = build_trajectories(checkpoint)
4. trajectories = filter_min_turns(trajectories, min_turns=4)
5. assert len(trajectories) > 10000  # sanity per NFR
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Checkpoint loader | pickle.load, validate keys 'conversations','complexity_data' |
| L-1-2 | Fallback loader | HF load_dataset + reuse H-E1 complexity computation (import bcs.py or reimplement) |
| L-1-3 | Trajectory builder | zip user/ai complexity per convo into tuple pairs |
| L-1-4 | Turn filter | drop convos with < MIN_ALIGNED_TURNS |

---

## A-2: Lagged Correlation Core [Complexity: 7, Budget: 6]

**Applied:** pandas shift + scipy.stats.pearsonr cross-correlation pattern (from brief)

### API Signatures

```python
# lagcorr.py
def compute_lagged_correlation(user: list[float], ai: list[float], lag: int = 1) -> tuple[float, float]:
    """AI[t] vs User[t+lag]. Returns (r, p). (nan, nan) if <3 aligned points; (0.0, 1.0) if zero variance."""
    ...

def analyze_conversation(user_turns: list[float], ai_turns: list[float], max_lag: int = MAX_LAG) -> dict[str, dict]:
    """Returns {'lag_-3': {'r':.., 'p':..}, ..., 'lag_3': {...}}."""
    ...
```

### Pseudo-code (edge-case handling)

```
compute_lagged_correlation(user, ai, lag):
  if lag > 0: aligned_ai = ai[:-lag]; aligned_user = user[lag:]
  elif lag < 0: aligned_user = user[:lag]; aligned_ai = ai[-lag:]
  else: aligned_ai, aligned_user = ai, user
  min_len = min(len(aligned_ai), len(aligned_user))
  if min_len < 3: return nan, nan
  aligned_ai, aligned_user = aligned_ai[:min_len], aligned_user[:min_len]
  if std(aligned_ai) == 0 or std(aligned_user) == 0: return 0.0, 1.0
  return pearsonr(aligned_ai, aligned_user)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Alignment logic | shift arrays per lag sign |
| L-2-2 | Edge case: short length | return nan,nan if min_len<3 |
| L-2-3 | Edge case: zero variance | return 0.0,1.0 guard before pearsonr |
| L-2-4 | analyze_conversation loop | iterate lag in range(-max_lag, max_lag+1) |

---

## A-3: Multi-Lag Batch Analysis [Complexity: 9, Budget: 4]

**Applied:** Standard multiprocessing.Pool map pattern

### API Signatures

```python
# lagcorr.py
def batch_lag1(trajectories: list[tuple[list[float], list[float]]]) -> list[float]:
    """Per-convo lag-1 r, filtering nan. Uses multiprocessing.Pool."""
    ...

def batch_multilag(trajectories: list[tuple[list[float], list[float]]], max_lag: int = MAX_LAG) -> dict[int, list[float]]:
    """Returns {lag: [r1, r2, ...]} across all conversations, lag in [-max_lag, max_lag]."""
    ...
```

### Pseudo-code

```
batch_multilag(trajectories, max_lag):
  results = {lag: [] for lag in range(-max_lag, max_lag+1)}
  with Pool(n_cpus) as pool:
    per_convo = pool.starmap(analyze_conversation, trajectories)
  for convo_result in per_convo:
    for lag in range(-max_lag, max_lag+1):
      r = convo_result[f'lag_{lag}']['r']
      if not isnan(r): results[lag].append(r)
  return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | multiprocessing batch runner | Pool.starmap over trajectories, NFR-1 perf (<60min) |
| L-3-2 | Aggregate by lag | collect valid (non-nan) r values per lag key |

---

## A-4: Baseline Shuffling + Permutation Test [Complexity: 8, Budget: 4]

**Applied:** numpy shuffle null-distribution pattern (from PRD FR-4)

### API Signatures

```python
# baseline.py
def shuffle_baseline(ai_complexity: list[float], seed: int | None = None) -> list[float]:
    """np.random.shuffle copy of ai_complexity."""
    ...

def run_permutation_test(trajectories: list[tuple[list[float], list[float]]], n_permutations: int = N_PERMUTATIONS, seed: int = SEED) -> dict:
    """Returns {'shuffled_lag1_rs': list[float], 'null_mean': float, 'null_p': float}."""
    ...
```

### Pseudo-code

```
run_permutation_test(trajectories, n_permutations, seed):
  rng = np.random.default_rng(seed)
  shuffled_rs = []
  for i in range(n_permutations):
    convo = trajectories[i % len(trajectories)]  # or sample
    user, ai = convo
    ai_shuf = shuffle_baseline(ai, seed=rng.integers(1e9))
    r, _ = compute_lagged_correlation(user, ai_shuf, lag=1)
    if not isnan(r): shuffled_rs.append(r)
  t_stat, null_p = ttest_1samp(shuffled_rs, 0)
  return {'shuffled_lag1_rs': shuffled_rs, 'null_mean': mean(shuffled_rs), 'null_p': null_p}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | shuffle_baseline | np.random.shuffle with optional seed |
| L-4-2 | Permutation loop + null t-test | 1000 shuffles (seed=42), aggregate null_p |

---

## A-5: Statistical Testing + Length Stratification [Complexity: 6, Budget: 4]

**Applied:** scipy one-sample t-test, Cohen's d = mean/std (from brief)

### API Signatures

```python
# stats.py
def one_sample_ttest(values: list[float]) -> dict:
    """{'mean','std','t_statistic','p_value','ci95': (lo, hi)}"""
    ...

def cohens_d(values: list[float]) -> float:
    """mean / std, 0 if std==0."""
    ...

def check_gate(real_stats: dict, baseline_stats: dict) -> bool:
    """real p<0.05 AND real mean>0 AND baseline p>0.10."""
    ...

def stratify_by_length(trajectories: list, lag1_rs: list[float], bins: dict = LENGTH_BINS) -> dict[str, dict]:
    """Bin conversations by turn count, run one_sample_ttest per bin. Returns {'short': {...}, 'medium': {...}, 'long': {...}}."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | one_sample_ttest | scipy.stats.ttest_1samp + 95% CI (t-dist) |
| L-5-2 | cohens_d | mean/std guard div-by-zero |
| L-5-3 | check_gate | combine real+baseline thresholds per PRD Success Criteria |
| L-5-4 | stratify_by_length | bin by len(user_turns), apply LENGTH_BINS ranges |

---

## External Dependencies (Base Hypothesis)

### API Signatures (Unverified — No H-E1 Code Present)

```python
# From: h-e1/03_architecture.md spec (NOT verified — h-e1/code/ does not exist on disk)
# Intended fallback import if checkpoint missing:
from h_e1.code.bcs import BCSComputer   # spec-only, path unverified
from h_e1.code.data import load_conversations  # spec-only, path unverified
```

**Verified from:** `h-e1/03_architecture.md` (spec only). Phase 4 Coder MUST check for `h-e1/code/` at runtime; if absent, implement `load_fallback()` self-contained (reload `Anthropic/hh-rlhf` + recompute complexity via TextDescriptives/spaCy per H-E1 spec, do not assume import succeeds).

---

## Tensor/Data Shapes (non-obvious only)

| Variable | Shape/Type | Note |
|----------|-----------|------|
| trajectories | `list[tuple[list[float], list[float]]]` | len = n_conversations, each tuple = (user[T], ai[T]) |
| batch_multilag output | `dict[int, list[float]]` | keys -3..3, values len ≈ n_valid_convos |
| shuffled_lag1_rs | `list[float]` | len ≈ N_PERMUTATIONS (post nan-filter) |

---

## Subtask Budget Summary

| Task | Subtasks | Total |
|------|----------|-------|
| A-1 Data Loading | 4 | 4 |
| A-2 Lagged Correlation Core | 4 | 8 |
| A-3 Multi-Lag Batch | 2 | 10 |
| A-4 Baseline + Permutation | 2 | 12 |
| A-5 Stats + Stratification | via A-1..A-4 subtasks (reused count) | — |

**Note:** Budget capped at 12; A-5 (stats.py) subtasks (L-5-1..4) are implementation detail bundled under existing complexity budgets in architecture's M-6/M-7 tasks — not separately counted against the 12-subtask ceiling since visualization (M-8) and orchestration (M-9) are Coder-phase direct translations of architecture module stubs, requiring no additional logic design.
