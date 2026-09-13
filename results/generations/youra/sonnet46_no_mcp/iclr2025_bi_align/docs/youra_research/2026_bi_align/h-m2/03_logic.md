# H-M2 Logic Design: Round-Stratified Coefficient Shift

**Generated:** 2026-05-03
**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL / SHOULD_WORK)

Applied: bootstrap-ci-percentile-stratified
Applied: shared-scaler-fit-on-round1
Applied: incremental-hypothesis-pipeline-reuse

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1 + H-M1)
**Status**: API signatures verified from actual base code
**Analyzed Path**: `h-e1/code/` and `h-m1/code/run_experiment.py`
**Relevant Symbols**:
- `QEarlyModel.fit(X_r1: np.ndarray, y_r1: np.ndarray) -> None`
- `QEarlyModel.calibrate(X: np.ndarray, y: np.ndarray) -> None`
- `QEarlyModel.predict_proba(X: np.ndarray) -> np.ndarray`  # returns [N, 2]
- `build_feature_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]`  # X: [N,3], y: [N,]
- `bootstrap_coefficient_ci(round_dfs, q_early_model, feature_matrix_fn, n_iter, seed)` — H-E1 version; H-M2 uses new `bootstrap_ci()` on `RoundSplit` objects
- `HE1_CODE_DIR = Path(__file__).parent.parent.parent / "h-e1" / "code"` — verified sys.path pattern from h-m1

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/q_early.py (ACTUAL CODE)
class QEarlyModel:
    def fit(self, X_r1: np.ndarray, y_r1: np.ndarray) -> None: ...
    def calibrate(self, X: np.ndarray, y: np.ndarray) -> None: ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray: ...  # [N, 2]

# From: h-e1/code/features.py (ACTUAL CODE)
def build_feature_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    # Returns X: [N, 3] StandardScaled, y: [N,] (verbosity-median pseudo-labels)
    # NOTE: fits its OWN internal scaler — H-M2 must NOT call this for late round
    # H-M2 fits scaler on round-1 raw features manually, then transforms round-3
    ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE - sys.path pattern)
HE1_CODE_DIR = Path(__file__).parent.parent.parent / "h-e1" / "code"
if HE1_CODE_DIR.exists() and str(HE1_CODE_DIR) not in sys.path:
    sys.path.insert(1, str(HE1_CODE_DIR))
```

**Verified from**: actual implementation files (not specs)

---

## A-4: Round Predictor Fitting [Complexity: 9, Budget: 2 subtasks]

Applied: shared-scaler-fit-on-round1

### API Signatures

```python
def fit_round_predictor(
    split: RoundSplit,
    shared_scaler: Optional[StandardScaler] = None,
) -> RoundModel:
    """Fit LogisticRegression on [X_train | q_train]. Returns RoundModel."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | SharedScaler | If `shared_scaler` is None, instantiate `StandardScaler`, fit on `split.X_train` raw features (shape `[N, 3]`), store in returned `RoundModel.scaler`. If provided, skip fit — transform only. Augment: `X_scaled = scaler.transform(X_train)`, then `X_aug = np.hstack([X_scaled, split.q_train[:, None]])` → `[N, 4]`. Extract `coefs = clf.coef_[0]`; `coefs[:3]` = `[β_L, β_H, β_S]`; `coefs[3]` = `beta_q`. |
| L-4-2 | QEarlyReuse | Call `q_early_model.predict_proba(split.X_train)[:, 1:2]` (shape `[N, 1]`) to get quality scores. Concatenate with scaled stylistic features before `LogisticRegression.fit()`. For test AUC: transform `split.X_test` with `shared_scaler`, augment with `q_early_model.predict_proba(split.X_test)[:, 1:2]`, call `roc_auc_score(split.y_test, clf.predict_proba(X_aug_test)[:, 1])`. |

### Pseudo-code

```
fit_round_predictor(split, shared_scaler=None):
    X_raw = split.X_train          # [N, 3]
    if shared_scaler is None:
        scaler = StandardScaler().fit(X_raw)
    else:
        scaler = shared_scaler
    X_s = scaler.transform(X_raw)  # [N, 3]
    q = q_early_model.predict_proba(X_raw)[:, 1:2]  # [N, 1]
    X_aug = np.hstack([X_s, q])    # [N, 4]
    clf = LogisticRegression(**LR_PARAMS).fit(X_aug, split.y_train)
    coefs = clf.coef_[0]           # [4,]
    auc = roc_auc_score(y_test, clf.predict_proba(X_aug_test)[:, 1])
    return RoundModel(clf, scaler, coefs[:3], coefs[3], auc)
```

---

## A-5: Bootstrap CI [Complexity: 12, Budget: 2 subtasks]

Applied: bootstrap-ci-percentile-stratified

### API Signatures

```python
def bootstrap_ci(
    split: RoundSplit,
    shared_scaler: StandardScaler,
    n_resamples: int = 2000,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Stratified bootstrap on split.X_train / y_train.
    Returns (ci_low, ci_high, boot_coefs): shapes (3,), (3,), (n_resamples, 3).
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | BootstrapLoop | `rng = np.random.default_rng(random_state)`. For each of `n_resamples` iterations: stratified resample via `np.concatenate([rng.choice(pos_idx, len(pos_idx), replace=True), rng.choice(neg_idx, len(neg_idx), replace=True)])`. Scale with `shared_scaler.transform(X_boot)`. Augment with q_scores. Fit `LogisticRegression`. Store `clf.coef_[0, :3]` → `boot_coefs[i]`. Handle degenerate case (single class) by zeroing coefficients. |
| L-5-2 | CIPercentileAndNonOverlap | Compute `ci_low = np.percentile(boot_coefs, 2.5, axis=0)` and `ci_high = np.percentile(boot_coefs, 97.5, axis=0)`, both shape `(3,)`. Non-overlap test in `compare_coefficients()`: for each feature `j`, check `early_ci[1, j] < late_ci[0, j]` (late CI entirely above early CI). Increment `n_directional` counter for each passing feature. |

### Pseudo-code

```
bootstrap_ci(split, shared_scaler, n_resamples=2000, random_state=42):
    rng = np.random.default_rng(random_state)
    pos_idx = np.where(split.y_train == 1)[0]
    neg_idx = np.where(split.y_train == 0)[0]
    boot_coefs = np.zeros((n_resamples, 3))
    for i in range(n_resamples):
        idx = np.concatenate([
            rng.choice(pos_idx, len(pos_idx), replace=True),
            rng.choice(neg_idx, len(neg_idx), replace=True),
        ])
        X_b = shared_scaler.transform(split.X_train[idx])  # [N, 3]
        q_b = q_early_model.predict_proba(split.X_train[idx])[:, 1:2]
        X_aug = np.hstack([X_b, q_b])                       # [N, 4]
        y_b = split.y_train[idx]
        try:
            lr = LogisticRegression(**LR_PARAMS).fit(X_aug, y_b)
            boot_coefs[i] = lr.coef_[0, :3]
        except Exception:
            boot_coefs[i] = np.zeros(3)
    ci_low  = np.percentile(boot_coefs, 2.5,  axis=0)  # (3,)
    ci_high = np.percentile(boot_coefs, 97.5, axis=0)  # (3,)
    return ci_low, ci_high, boot_coefs
```

---

## A-6: Coefficient Comparison [Complexity: 11, Budget: 2 subtasks]

Applied: non-overlap-ci-directional-gate

### API Signatures

```python
def compare_coefficients(
    early_model: RoundModel,
    late_model: RoundModel,
    early_split: RoundSplit,
    late_split: RoundSplit,
    shared_scaler: StandardScaler,
    n_resamples: int = 2000,
    random_state: int = 42,
) -> ComparisonResult:
    """Run bootstrap CIs, compute deltas + gate metrics. Returns ComparisonResult."""
    ...

def evaluate_gate(result: ComparisonResult) -> Dict:
    """
    PASS if n_directional >= 2, PARTIAL if == 1, FAIL if == 0.
    Returns: {gate_status: str, n_directional: int, sign_consistent: bool, beta_q_stable: bool}
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | DeltasAndConsistency | `deltas = late_model.coefs - early_model.coefs` → shape `(3,)`. `sign_consistent = bool(np.all(deltas > 0))`. `beta_q_stable = bool(abs(late_model.beta_q - early_model.beta_q) < BETA_Q_STABILITY_THRESHOLD)`. Count non-overlapping CIs: for `j` in `[0,1,2]`, check `early_ci[1,j] < late_ci[0,j]`; increment `n_directional`. Pack into `ComparisonResult`. |
| L-6-2 | EvaluateGate | `if result.n_directional >= 2: status = "PASS"`. `elif result.n_directional == 1: status = "PARTIAL"`. `else: status = "FAIL"`. Return dict with `gate_status`, `n_directional`, `sign_consistent`, `beta_q_stable`. Also log: `"Coefficient comparison: β_L=[{e:.4f},{l:.4f}] δ={d:.4f}; ... n_directional={n}/3"`. |

### Pseudo-code

```
compare_coefficients(early_model, late_model, early_split, late_split, shared_scaler, ...):
    e_low, e_high, boot_early = bootstrap_ci(early_split, shared_scaler, n_resamples, random_state)
    l_low, l_high, boot_late  = bootstrap_ci(late_split,  shared_scaler, n_resamples, random_state)
    early_ci = np.stack([e_low, e_high])   # (2, 3)
    late_ci  = np.stack([l_low, l_high])   # (2, 3)
    deltas = late_model.coefs - early_model.coefs  # (3,)
    n_directional = sum(early_ci[1, j] < late_ci[0, j] for j in range(3))
    sign_consistent = bool(np.all(deltas > 0))
    beta_q_stable = bool(abs(late_model.beta_q - early_model.beta_q) < BETA_Q_STABILITY_THRESHOLD)
    return ComparisonResult(
        early_coefs=early_model.coefs, late_coefs=late_model.coefs,
        deltas=deltas, early_ci=early_ci, late_ci=late_ci,
        n_directional=n_directional, sign_consistent=sign_consistent,
        beta_q_stable=beta_q_stable, ..., boot_early=boot_early, boot_late=boot_late,
    )

evaluate_gate(result):
    if result.n_directional >= 2:   status = "PASS"
    elif result.n_directional == 1: status = "PARTIAL"
    else:                           status = "FAIL"
    return {"gate_status": status, "n_directional": result.n_directional,
            "sign_consistent": result.sign_consistent, "beta_q_stable": result.beta_q_stable}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_train (raw) | [N, 3] | Stylistic deltas before scaling |
| X_aug | [N, 4] | Scaled stylistic + q_early score |
| coefs | [4,] | `coef_[0]`; `[:3]` = stylistic, `[3]` = β_Q |
| boot_coefs | [2000, 3] | Stylistic coefs only per resample |
| early_ci / late_ci | [2, 3] | Row 0 = low, row 1 = high |
| deltas | [3,] | late_coefs - early_coefs |
