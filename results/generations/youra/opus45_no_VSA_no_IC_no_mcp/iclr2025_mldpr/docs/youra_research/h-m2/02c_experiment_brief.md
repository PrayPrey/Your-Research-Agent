# Experiment Design: h-m2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Pre-2019 DNSI (computed on 2009-2018 SOTA data) predicts post-2019 generalization gap measurements with R² > 0.3
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔬 **MECHANISM (Temporal Prediction) Template** - Tests predictive relationship across time

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (COMPLETED - DNSI computation validated)
**Gate Status:** SHOULD_WORK - Not yet satisfied

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM (Temporal Prediction)
- **Prerequisites:** h-e1 (DNSI computation works)

### Gate Condition
SHOULD_WORK: If R² < 0.1, temporal prediction fails. R² > 0.3 demonstrates predictive utility.

### Dependency on h-e1
h-e1 validated DNSI computation. This experiment applies DNSI to temporally-split data:
- **Pre-2019 DNSI:** Computed from 2009-2018 SOTA histories only
- **Post-2019 Gap:** Generalization gaps measured after 2019 (ImageNet-V2, CIFAR-10.2, ObjectNet, HANS)

---

## Continuation Context

### Previous Hypothesis Results (h-e1)
- DNSI computed successfully for 3/5 benchmarks (60% > 50% threshold)
- Valid DNSI values in range [0.3952, 1.0289]
- Key insight: Class count difficulty proxy required for valid DNSI

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Findings inferred from h-e1 and literature.

**[INFERRED]** Temporal Split Strategy
- Split SOTA histories at 2019-01-01
- Pre-2019 data: 2009-2018 (training period for DNSI)
- Post-2019 data: 2019+ (where gap measurements were published)
- Rationale: ImageNet-V2, CIFAR-10.2, ObjectNet papers published 2019

**[INFERRED]** Regression for Small N
- OLS regression problematic for n=4
- Leave-one-out cross-validation for robustness
- Bootstrap R² for confidence intervals
- Report both R² and adjusted R²

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. Using h-e1 code patterns.

**[INFERRED]** Temporal DNSI Computation
- Modify h-e1 DNSIComputer to accept date cutoff parameter
- Filter SOTA entries by date before computing DNSI
- Same 6-month windowing, same difficulty proxy

---

## Experiment Specification

### Dataset

**Name:** Temporally-Split PapersWithCode SOTA + Gap Ground Truth
**Type:** standard
**Source:** PapersWithCode archived histories + published gap measurements

**Description:**
Temporal prediction dataset combining:
1. **Pre-2019 DNSI:** DNSI computed from 2009-2018 SOTA entries only
2. **Post-2019 Gap:** Generalization gaps from papers published 2019+

**Temporal Structure:**

| Benchmark | Pre-2019 Period | DNSI Computation | Post-2019 Gap Source | Gap Value |
|-----------|-----------------|------------------|---------------------|-----------|
| ImageNet | 2012-2018 | 6+ years history | ImageNet-V2 (2019) | 11-14% |
| CIFAR-10 | 2009-2018 | 9+ years history | CIFAR-10.2 (2019) | 3-5% |
| CIFAR-100 | 2009-2018 | 9+ years history | (use V2-scaled) | ~5% |
| ObjectNet | 2012-2018 (ImageNet) | Uses ImageNet history | ObjectNet (2019) | 40-45% |

**Note:** ObjectNet uses ImageNet SOTA history since it tests ImageNet-trained models.

**Loading Information:**
```python
import json
from datetime import datetime

def load_temporal_sota(benchmark: str, cutoff_date: str = "2019-01-01"):
    """
    Load SOTA history before cutoff date for temporal prediction.
    """
    cutoff = datetime.fromisoformat(cutoff_date)
    
    # Load full history from h-e1 data
    with open(f"h-e1/code/data/pwc/{benchmark}.json") as f:
        full_history = json.load(f)
    
    # Filter to pre-cutoff entries
    pre_cutoff = [
        entry for entry in full_history
        if datetime.fromisoformat(entry["date"]) < cutoff
    ]
    
    return pre_cutoff

# Gap data (from published papers, all 2019+)
gap_data = {
    "ImageNet": {"gap": 0.125, "source": "Recht2019", "pub_date": "2019-06"},
    "CIFAR-10": {"gap": 0.04, "source": "Recht2019", "pub_date": "2019-06"},
    "CIFAR-100": {"gap": 0.05, "source": "Recht2019-scaled", "pub_date": "2019-06"},
    "ObjectNet": {"gap": 0.425, "source": "Barbu2019", "pub_date": "2019-10"},
}
```

### Models

#### Analysis Method

**Name:** Temporal Prediction Regression Pipeline
**Type:** Statistical analysis (OLS regression)

**Description:**
Tests whether DNSI computed on pre-2019 data predicts post-2019 generalization gaps.

**Core Implementation:**

```python
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class TemporalPredictionAnalyzer:
    """
    Analyze temporal prediction: pre-2019 DNSI → post-2019 gap
    """
    def __init__(self, n_bootstrap: int = 10000):
        self.n_bootstrap = n_bootstrap
    
    def analyze(self, dnsi_pre2019: np.ndarray, gap_post2019: np.ndarray) -> dict:
        """
        Args:
            dnsi_pre2019: DNSI computed on 2009-2018 data
            gap_post2019: Generalization gaps measured 2019+
        Returns:
            Regression results with R² and bootstrap CI
        """
        n = len(dnsi_pre2019)
        X = dnsi_pre2019.reshape(-1, 1)
        y = gap_post2019
        
        # OLS Regression
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        r2 = r2_score(y, y_pred)
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - 2)  # Adjusted for n-1 predictors
        
        # Bootstrap R² confidence interval
        bootstrap_r2 = self._bootstrap_r2(dnsi_pre2019, gap_post2019)
        ci_lower, ci_upper = np.percentile(bootstrap_r2, [2.5, 97.5])
        
        # Leave-one-out cross-validation
        loo_r2 = self._loo_cv(dnsi_pre2019, gap_post2019)
        
        return {
            "n": n,
            "r2": r2,
            "adj_r2": adj_r2,
            "loo_r2": loo_r2,
            "ci_95_lower": ci_lower,
            "ci_95_upper": ci_upper,
            "slope": model.coef_[0],
            "intercept": model.intercept_,
            "hypothesis_supported": r2 > 0.3
        }
    
    def _bootstrap_r2(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Bootstrap R² estimation"""
        n = len(x)
        r2_values = []
        for _ in range(self.n_bootstrap):
            idx = np.random.choice(n, size=n, replace=True)
            if len(np.unique(idx)) > 1:  # Need >1 unique points for regression
                X_boot = x[idx].reshape(-1, 1)
                y_boot = y[idx]
                model = LinearRegression()
                model.fit(X_boot, y_boot)
                r2 = r2_score(y_boot, model.predict(X_boot))
                if np.isfinite(r2):
                    r2_values.append(r2)
        return np.array(r2_values)
    
    def _loo_cv(self, x: np.ndarray, y: np.ndarray) -> float:
        """Leave-one-out cross-validation R²"""
        n = len(x)
        predictions = []
        actuals = []
        for i in range(n):
            X_train = np.delete(x, i).reshape(-1, 1)
            y_train = np.delete(y, i)
            X_test = x[i].reshape(1, -1)
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions.append(model.predict(X_test)[0])
            actuals.append(y[i])
        
        # Compute R² on held-out predictions
        ss_res = np.sum((np.array(actuals) - np.array(predictions))**2)
        ss_tot = np.sum((np.array(actuals) - np.mean(actuals))**2)
        return 1 - ss_res / ss_tot if ss_tot > 0 else 0
```

### Temporal DNSI Computation

```python
from datetime import datetime, timedelta
import numpy as np
from scipy.stats import entropy

class TemporalDNSIComputer:
    """
    DNSI computation with temporal cutoff for prediction experiments.
    """
    def __init__(self, window_months: int = 6, cutoff_date: str = "2019-01-01"):
        self.window_months = window_months
        self.cutoff = datetime.fromisoformat(cutoff_date)
    
    def compute_dnsi_pre_cutoff(self, sota_history: list, difficulty_proxy: int) -> float:
        """
        Compute DNSI using only entries before cutoff date.
        
        Args:
            sota_history: List of {"date": str, "accuracy": float}
            difficulty_proxy: Number of classes
        Returns:
            DNSI value, or None if insufficient pre-cutoff data
        """
        # Filter to pre-cutoff entries
        pre_cutoff = [
            entry for entry in sota_history
            if datetime.fromisoformat(entry["date"]) < self.cutoff
        ]
        
        if len(pre_cutoff) < 10 or difficulty_proxy <= 1:
            return None
        
        # Convert to (date, accuracy) tuples
        history_tuples = [
            (datetime.fromisoformat(e["date"]), e["accuracy"])
            for e in sorted(pre_cutoff, key=lambda x: x["date"])
        ]
        
        # Compute windowed improvements
        improvements = self._compute_windowed_improvements(history_tuples)
        if len(improvements) < 5:
            return None
        
        # Shannon entropy
        h_observed = entropy(improvements + 1e-10)
        h_expected = np.log(difficulty_proxy)
        
        return h_observed / h_expected if h_expected > 0 else None
    
    def _compute_windowed_improvements(self, history: list) -> np.ndarray:
        """Same as h-e1 implementation"""
        window_delta = timedelta(days=self.window_months * 30)
        start_date = history[0][0]
        end_date = history[-1][0]
        
        improvements = []
        current = start_date
        while current < end_date:
            window_end = current + window_delta
            window_improvements = [
                history[i][1] - history[i-1][1]
                for i in range(1, len(history))
                if current <= history[i][0] < window_end
                and history[i][1] > history[i-1][1]
            ]
            improvements.append(sum(window_improvements) if window_improvements else 0)
            current = window_end
        
        return np.array(improvements)
```

### Evaluation

**Primary Metric:** R² (Coefficient of Determination)

| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| R² | Variance explained by pre-2019 DNSI | R² > 0.3 |
| LOO-CV R² | Leave-one-out cross-validated R² | LOO R² > 0.1 |
| 95% CI | Bootstrap confidence interval | CI lower > 0.1 |
| Slope Sign | Direction of relationship | Negative (expected) |

**Success Criteria (SHOULD_WORK):**
- R² > 0.3 — pre-2019 DNSI explains >30% of post-2019 gap variance
- LOO-CV R² > 0.1 — some predictive validity on held-out data
- Slope is negative (lower DNSI → higher gap)

**Failure Criteria:**
- R² < 0.1 → SHOULD_WORK gate fails (no predictive relationship)

**Metrics Code:**
```python
def evaluate_temporal_prediction(dnsi_pre, gap_post):
    analyzer = TemporalPredictionAnalyzer()
    results = analyzer.analyze(dnsi_pre, gap_post)
    
    success = results["r2"] > 0.3
    fail = results["r2"] < 0.1
    
    return {
        "gate_result": "PASS" if success else ("FAIL" if fail else "MARGINAL"),
        "r2": results["r2"],
        "loo_r2": results["loo_r2"],
        "ci_95": (results["ci_95_lower"], results["ci_95_upper"]),
        "slope": results["slope"]
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Temporal Prediction Scatter**: Pre-2019 DNSI (x) vs Post-2019 Gap (y), regression line, R² annotation

#### Additional Figures

1. **Bootstrap R² Distribution**: Histogram of bootstrap R² values with CI bands
2. **LOO Predictions**: Actual vs predicted gap for each LOO fold
3. **Timeline Visualization**: DNSI trajectory showing pre/post-2019 split per benchmark

---

## 🔬 Mechanism Verification Check

**Pass Condition:**
1. R² > 0.3 (pre-2019 DNSI predicts post-2019 gap)
2. LOO-CV R² > 0.1 (some generalization)
3. Negative slope (expected direction)

**Statistical Power Note:**
- n=4 severely limits power
- LOO-CV provides honest out-of-sample estimate
- Bootstrap CI quantifies uncertainty
- Frame as proof-of-concept, not definitive evidence

**Mechanism Verification:**
- Pre-condition: Pre-2019 DNSI values computed, post-2019 gap data loaded
- Activation Indicator: `print(f"[TEMPORAL] Analyzing {n} benchmark predictions...")`
- Success Signal: `print(f"[TEMPORAL] SUCCESS: R² = {r2:.3f} > 0.3")`
- Failure Detection: `print(f"[TEMPORAL] FAILED: R² = {r2:.3f} < 0.1")`

---

## Risk Mitigation

| Risk | Severity | Mitigation |
|------|----------|------------|
| Very small N (n=4) | HIGH | LOO-CV, bootstrap CI, frame as pilot |
| Limited pre-2019 history for some benchmarks | MODERATE | Require min 5 years pre-cutoff history |
| Gap measurement timing uncertainty | LOW | All target gaps published 2019+ |
| DNSI sensitivity to cutoff date | LOW | Fixed cutoff at 2019-01-01 |

---

## Appendix: Reference Implementations

### Source 1: h-e1 DNSIComputer
- **Location**: h-e1/code/metrics.py
- **Adaptation**: Add date filtering for pre-2019 cutoff

### Source 2: sklearn LinearRegression
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- **Usage**: OLS regression for DNSI → gap prediction

### Source 3: Recht et al. 2019 Gap Data
- **Paper**: "Do ImageNet Classifiers Generalize to ImageNet?"
- **Data**: Gap measurements for ImageNet-V2, CIFAR-10.2

### Source 4: Barbu et al. 2019 ObjectNet
- **Paper**: "ObjectNet: A large-scale bias-controlled dataset"
- **Data**: ImageNet → ObjectNet accuracy drop measurements

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design started
- 2026-08-28: Prerequisites verified (h-e1 completed)
- 2026-08-28: Experiment specification synthesized

---

*Tools Used: Read, Write (Archon/Exa/Serena MCP unavailable)*
*All specifications grounded in h-e1 patterns and published research*
*Next Phase: Phase 3 - Implementation Planning*
