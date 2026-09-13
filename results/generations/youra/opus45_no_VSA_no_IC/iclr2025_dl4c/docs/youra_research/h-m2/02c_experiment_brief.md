# Phase 2C Experiment Brief
## H-M2: Scale-Ensemble Outperformance

Generated: 2026-08-24T06:15:00Z

---

## Hypothesis Under Test

**ID**: H-M2
**Type**: MECHANISM
**Gate**: SHOULD_WORK

**Statement**: Scale-ensemble (majority vote) outperforms the best individual judge by ≥3%

**Statistical Test**: McNemar test comparing ensemble vs best single judge
**Success Criterion**: Ensemble accuracy > best single by ≥3%
**Falsification Criterion**: Improvement < 2% or ensemble worse than best single

**Prerequisites**: H-E1 (VALIDATED - Chi-square p=3.27e-08 confirms scale-dependent error patterns)

---

## Research Foundation

### Key Papers

1. **Majority Voting for Code Generation** (Launer et al., 2026)
   - Functional Majority Voting (FMV) substantially boosts performance on LiveCodeBench
   - Uses runtime execution signatures for consensus
   - Validates ensemble approach for code evaluation

2. **SE-Jury: LLM-as-Ensemble-Judge** (Zhou et al., 2025)
   - First ensemble-judge metric for software artifacts
   - Defines five distinct evaluation strategies
   - Shows ensemble judges narrow gap with human evaluation

3. **Enhancing LLM Code Generation with Ensembles** (Mahmud et al., 2025)
   - Ensemble achieves 90.2% on HumanEval vs 83.5% for best single (GPT-4o)
   - 6.7% improvement validates ≥3% hypothesis threshold
   - Uses CodeBLEU + behavioral equivalence for voting

4. **Blind to the Pivotal Vote** (Shu, 2026)
   - LLM judge panels show correlated errors
   - Accuracy gain concentrates on pivotal (one-vote margin) queries
   - +10.4 to +23.3pp improvement on pivotal queries

---

## Experimental Design

### Dataset

**Primary**: HumanEval+ (164 problems, 80x test coverage)
- Source: evalplus/humanevalplus (cached from H-E1)
- Ground truth: EvalPlus execution verdicts
- Full dataset used (no subsampling)

**Replication**: MBPP+ (500 problems)
- Source: evalplus/mbppplus
- Used if primary results require validation

### Models (Judges)

Reuse H-E1 judge outputs (already collected):

| Tier | Model | Role |
|------|-------|------|
| 7B | DeepSeek-Coder-7B-Instruct | Scale tier 1 |
| 70B | CodeLlama-70B-Instruct | Scale tier 2 |
| Proprietary | GPT-4 | Scale tier 3 (ceiling) |

### Ensemble Strategies

1. **Majority Vote (3-way)**: Simple majority across all 3 scale tiers
2. **Weighted Majority**: Weight by per-tier accuracy from H-E1
3. **Unanimous Agreement**: Flag confidence when all agree

### Baselines

1. **Best Single Judge**: Highest-accuracy individual model (likely GPT-4)
2. **Random Ensemble**: Random selection among judges (expected: avg of individuals)
3. **CodeBERTScore**: Static similarity baseline (~58%)

---

## Implementation Specification

### Input Format

```python
@dataclass
class JudgeVerdict:
    problem_id: str
    model: str  # "7b", "70b", "proprietary"
    verdict: bool  # True=correct, False=incorrect
    ground_truth: bool  # From EvalPlus execution

@dataclass
class EnsembleInput:
    problem_id: str
    verdicts: Dict[str, bool]  # model -> verdict
    ground_truth: bool
```

### Algorithm

```python
def majority_vote(verdicts: Dict[str, bool]) -> bool:
    """Simple majority vote across 3 judges."""
    votes = list(verdicts.values())
    return sum(votes) >= 2  # 2 of 3 agree

def weighted_majority(verdicts: Dict[str, bool], 
                      weights: Dict[str, float]) -> bool:
    """Weighted vote by model accuracy."""
    weighted_sum = sum(
        weights[m] * (1 if v else 0) 
        for m, v in verdicts.items()
    )
    return weighted_sum > 0.5 * sum(weights.values())
```

### Statistical Analysis

```python
from mlxtend.evaluate import mcnemar_table, mcnemar

def compare_ensemble_vs_best(
    y_true: np.ndarray,
    y_ensemble: np.ndarray,
    y_best_single: np.ndarray
) -> dict:
    """McNemar test for paired comparison."""
    
    # Build contingency table
    tb = mcnemar_table(y_true, y_ensemble, y_best_single)
    
    # McNemar test (exact for small samples)
    chi2, p_value = mcnemar(tb, exact=True)
    
    # Compute accuracy difference
    acc_ensemble = (y_ensemble == y_true).mean()
    acc_best = (y_best_single == y_true).mean()
    improvement = acc_ensemble - acc_best
    
    return {
        "contingency_table": tb,
        "chi2": chi2,
        "p_value": p_value,
        "acc_ensemble": acc_ensemble,
        "acc_best_single": acc_best,
        "improvement_pct": improvement * 100,
        "hypothesis_supported": improvement >= 0.03 and p_value < 0.05
    }
```

---

## Success Metrics

| Metric | Success | Partial | Fail |
|--------|---------|---------|------|
| Accuracy improvement | ≥3% | 2-3% | <2% |
| McNemar p-value | <0.05 | <0.10 | ≥0.10 |
| Sample size | 164 (full) | N/A | <100 |

### Expected Outcomes (from literature)

- Mahmud et al. achieved +6.7% on HumanEval with ensemble
- Shu showed +10.4pp on pivotal votes
- Conservative expectation: +3-5% improvement

---

## Data Flow

```
H-E1 Judge Outputs (cached)
        │
        ▼
┌───────────────────┐
│ Load per-problem  │
│ verdicts for each │
│ judge tier        │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Compute ensemble  │
│ verdict (majority │
│ vote)             │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Identify best     │
│ single judge      │
│ (by accuracy)     │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ McNemar test:     │
│ ensemble vs best  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Report: accuracy  │
│ delta, p-value,   │
│ hypothesis result │
└───────────────────┘
```

---

## Controlled Variables

- **Fixed prompt**: Same as H-E1 (pilot-selected)
- **Temperature**: 0 (deterministic)
- **Ground truth**: EvalPlus execution
- **Sample**: Full HumanEval+ (164 problems)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Insufficient improvement | Report weighted majority as alternative |
| Correlated errors across tiers | Expected from H-E1; this is the mechanism being tested |
| Small sample size (164) | Use exact binomial test in McNemar; replicate on MBPP+ |
| Best single already ≥95% | Ceiling effect documented; focus on error reduction ratio |

---

## Output Artifacts

1. **Contingency table**: 2x2 showing ensemble vs best-single agreement/disagreement
2. **McNemar test results**: chi², p-value
3. **Accuracy metrics**: Per-judge and ensemble accuracies
4. **Pivot analysis**: Accuracy on unanimous vs split verdict cases
5. **Hypothesis verdict**: SUPPORTED/REFUTED with evidence

---

## Dependencies

### Python Packages
- `mlxtend>=0.23.0` (McNemar test)
- `numpy`, `pandas` (data manipulation)
- `evalplus` (dataset loading, cached)

### Data Dependencies
- H-E1 judge outputs (per-problem verdicts for 3 scale tiers)
- EvalPlus execution ground truth

---

## Estimated Compute

| Component | Cost |
|-----------|------|
| Data loading | Cached from H-E1 |
| Ensemble computation | <1 min CPU |
| Statistical tests | <1 sec |
| **Total** | **<5 min, no GPU** |

---

## Phase 2C Completion Checklist

- [x] Hypothesis clearly stated with success/fail criteria
- [x] Dataset specified (HumanEval+ full, 164 problems)
- [x] Models specified (reuse H-E1 judges)
- [x] Statistical test defined (McNemar)
- [x] Algorithm pseudocode provided
- [x] Baselines defined
- [x] Risk mitigation documented
- [x] Literature grounding (4 relevant papers)
- [x] Compute estimate (<5 min)
- [x] No synthetic data (uses real benchmark + real model outputs)
