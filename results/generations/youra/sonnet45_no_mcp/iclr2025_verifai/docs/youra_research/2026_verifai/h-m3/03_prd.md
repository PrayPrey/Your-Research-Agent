# Product Requirements Document: h-m3 Hybrid Termination Detection

**Date:** 2026-04-20
**Hypothesis:** h-m3
**Type:** MECHANISM
**Author:** Anonymous

---

## 1. Executive Summary

### 1.1 Purpose
Implement a three-signal hybrid termination detector for neural theorem proving that combines confidence instability, symbolic divergence signals, and search tree metrics to identify probable non-termination more accurately than single-signal approaches.

### 1.2 Success Criteria
- Hybrid detector outperforms all single-signal ablations (F1 score comparison)
- Achieves correlation r > 0.5 with ground truth timeout labels
- Completes evaluation on 100-theorem dataset from h-m1

### 1.3 Hypothesis Statement
When confidence instability (std dev of entropy > threshold) is combined with symbolic signals (state hash collisions, exponential growth) and search tree metrics (high backtrack frequency), if these signals exceed thresholds, then budget reduction is triggered, because the three-signal hybrid provides stronger evidence of probable non-termination than any single signal.

---

## 2. Problem Statement

### 2.1 Current State
- h-m1 validated confidence variance correlates with timeouts (r=0.80)
- h-m2 validated divergence classification methodology with tree tracking
- Single-signal detectors exist but may have limitations

### 2.2 Target State
- Hybrid detector combining three independent signal types
- Voting-based combination (k-of-n threshold)
- Comprehensive ablation study comparing all signal combinations

### 2.3 Gap Analysis
**Missing Components:**
- Symbolic signal extraction (state hash collisions, exponential growth)
- Hybrid voting logic implementation
- Ablation framework for 7 model variants
- Threshold selection strategy from data

---

## 3. Functional Requirements

### FR-1: Dataset Loading
**Priority:** P0 (Critical)
**Description:** Load LeanDojo Benchmark and h-m1 results for evaluation
- Load h-m1 results CSV (100 experiments, 37 timeouts)
- Extract theorem IDs and ground truth timeout labels
- Access confidence trajectories from h-m1 data

### FR-2: Confidence Signal Extraction (from h-m1)
**Priority:** P0 (Critical)
**Description:** Reuse confidence variance extraction from h-m1
- Calculate std dev of entropy from confidence trajectories
- Load pre-computed variance values from h-m1 results
- Threshold: 0.25 (median of timeout group)

### FR-3: Symbolic Signal Extraction (NEW)
**Priority:** P0 (Critical)
**Description:** Extract symbolic divergence signals from proof states
- **State Hash Collisions:** Count duplicate state hashes using `hash(frozenset(state.pp.items()))`
- **Exponential Growth:** Fit exponential trend to proof state sizes over time
- Threshold selection: Use median values from timeout-labeled theorems

### FR-4: Search Tree Signal Extraction (from h-m2)
**Priority:** P0 (Critical)
**Description:** Extract search tree metrics using h-m2 infrastructure
- Backtrack frequency: `backtrack_count / max(len(tree.nodes), 1)`
- Reuse ExtendedTimeoutRunnerWithTree from h-m2
- Threshold selection: TBD from h-m2 data analysis

### FR-5: Hybrid Voting Detector
**Priority:** P0 (Critical)
**Description:** Implement k-of-3 voting-based termination detector
- Voting threshold: k=2 (at least 2 of 3 signals trigger)
- Individual signal triggers:
  - Confidence alert: variance > threshold
  - Symbolic alert: collisions > threshold OR growth > threshold
  - Search alert: backtrack_freq > threshold
- Return: Boolean termination decision

### FR-6: Baseline Ablation Models
**Priority:** P0 (Critical)
**Description:** Implement single-signal baseline detectors
- **Confidence-only:** variance > 0.25 (from h-m1)
- **Symbolic-only:** collisions OR growth exceed thresholds
- **Search-tree-only:** backtrack_freq > threshold

### FR-7: Pairwise Combination Models
**Priority:** P1 (Important)
**Description:** Implement 2-signal combination detectors
- Confidence + Symbolic
- Confidence + Search-tree
- Symbolic + Search-tree
- Combination logic: OR or AND (to be determined)

### FR-8: Evaluation Metrics
**Priority:** P0 (Critical)
**Description:** Compute classification and correlation metrics
- **Precision:** `TP / (TP + FP)` - of flagged theorems, how many timed out?
- **Recall:** `TP / (TP + FN)` - of timeouts, how many were flagged?
- **F1 Score:** `2 * (precision * recall) / (precision + recall)`
- **Correlation:** Pearson r and Spearman ρ with ground truth
- Library: `sklearn.metrics`, `scipy.stats`

### FR-9: Ablation Comparison Framework
**Priority:** P0 (Critical)
**Description:** Systematic evaluation of all 7 model variants
- Run each model on same 100-theorem dataset
- Collect metrics: precision, recall, F1, correlation
- Generate comparison table and visualizations
- Identify best-performing model

### FR-10: Threshold Selection
**Priority:** P1 (Important)
**Description:** Data-driven threshold tuning
- Use median values from timeout group for each signal
- No hyperparameter search (PoC uses fixed thresholds)
- Document threshold values in results

---

## 4. Non-Functional Requirements

### NFR-1: Reusability
- Reuse h-m1 confidence extraction pipeline (proven)
- Reuse h-m2 tree tracking infrastructure (proven)
- Minimize new code (only symbolic signals + voting)

### NFR-2: Reproducibility
- Use same 100 theorems from h-e1 → h-m1 → h-m2
- Fixed random seeds (if applicable)
- Document all threshold values

### NFR-3: Performance
- Evaluation completes within reasonable time
- No LeanDojo runtime integration (offline analysis)

### NFR-4: Code Quality (LIGHT Tier - Minimal Infrastructure)
- **Configuration:** Hardcoded thresholds or simple argparse
- **Logging:** print statements + CSV output
- **Testing:** Smoke test only (verify code runs without error)
- **Documentation:** Inline comments for non-obvious logic

---

## 5. Data Requirements

### 5.1 Input Data
| Data Source | Format | Location | Purpose |
|-------------|--------|----------|---------|
| h-m1 results | CSV | `h-m1/results/h_m1_results.csv` | Ground truth labels, confidence variance |
| h-m2 tree data | Python objects | Re-run with h-m2 infrastructure | Search tree metrics |
| LeanDojo theorems | Benchmark | 100 theorem IDs from h-m1 | Evaluation dataset |

### 5.2 Output Data
| Output | Format | Location | Content |
|--------|--------|----------|---------|
| Results CSV | CSV | `h-m3/results/h_m3_results.csv` | All metrics per model |
| Figures | PNG | `h-m3/figures/` | Ablation comparison, signal distributions |
| Threshold log | TXT | `h-m3/results/thresholds.txt` | Selected threshold values |

---

## 6. Success Metrics

### 6.1 PoC Pass Condition (Direction-based)
1. **Code runs without error** ✓
2. **Hybrid model F1 > all single-signal F1 scores** ✓

### 6.2 Gate Condition (SHOULD_WORK)
- **Type:** SHOULD_WORK
- **Pass:** Combined model outperforms all single-signal ablations
- **Fail Action:** Refine signal combination strategy (document limitation, proceed)

### 6.3 Expected Performance
- **Confidence-only baseline:** r ≈ 0.80 (from h-m1)
- **Hybrid target:** r > 0.5, F1 improvement over baselines

---

## 7. Dependencies and Constraints

### 7.1 Prerequisites
- h-m1: COMPLETED ✓ (confidence signal validated)
- h-m2: COMPLETED ✓ (tree tracking infrastructure validated)

### 7.2 External Dependencies
- LeanDojo library (pip install lean-dojo)
- scikit-learn (metrics)
- scipy (correlation tests)
- numpy (signal processing)

### 7.3 Reusable Components
- h-m1 confidence extraction code
- h-m2 ExtendedTimeoutRunnerWithTree
- h-m1 results CSV (ground truth)

### 7.4 Constraints
- **No training required** - rule-based detector
- **Offline analysis only** - no LeanDojo runtime integration
- **100-theorem dataset** - controlled comparison with h-m1/h-m2
- **MECHANISM hypothesis** - FULL tier, 30 task budget

---

## 8. Out of Scope

- ❌ Integration into LeanDojo runtime (Phase 4+ scope)
- ❌ Hyperparameter optimization (PoC uses median thresholds)
- ❌ Real-time termination detection (offline analysis only)
- ❌ Model training (rule-based detector, no ML)
- ❌ Extended timeout experiments (reuse h-m1 data)

---

## 9. Acceptance Criteria

### 9.1 Code Completion
- [ ] Symbolic signal extraction implemented and tested
- [ ] Hybrid voting detector implemented
- [ ] All 7 ablation models implemented
- [ ] Evaluation metrics computed correctly
- [ ] Results CSV generated

### 9.2 Validation
- [ ] Code runs without runtime errors
- [ ] Hybrid F1 > all single-signal F1 scores
- [ ] Correlation r > 0.5 with ground truth
- [ ] All required visualizations generated

### 9.3 Documentation
- [ ] Threshold values documented
- [ ] Signal extraction logic documented
- [ ] Results interpretation provided

---

## 10. Implementation Notes

### 10.1 Architecture Considerations
- Build on h-m2 codebase (most comprehensive infrastructure)
- Add symbolic signal module as new component
- Implement voting detector as standalone class
- Use ablation framework pattern from experiment brief

### 10.2 Testing Strategy (LIGHT Tier - Minimal)
- **Smoke test:** Verify code runs on 5 sample theorems
- **No unit tests required** (LIGHT tier)
- **Manual validation:** Check output format correctness

### 10.3 Risk Mitigation
- **Low risk:** 80% infrastructure proven (h-m1, h-m2)
- **New code:** Only 20% (symbolic signals + voting)
- **Fallback:** Use h-m1 infrastructure if h-m2 has issues

---

## Appendix A: Ablation Model Specifications

| Model ID | Signals Used | Combination Logic |
|----------|--------------|-------------------|
| `confidence_only` | Confidence variance | `variance > 0.25` |
| `symbolic_only` | Hash collisions, Growth | `collisions > thresh OR growth > thresh` |
| `search_only` | Backtrack frequency | `backtrack_freq > thresh` |
| `conf_symb` | Confidence + Symbolic | `conf_alert OR symb_alert` |
| `conf_search` | Confidence + Search | `conf_alert OR search_alert` |
| `symb_search` | Symbolic + Search | `symb_alert OR search_alert` |
| `hybrid_all` | All three | `at least 2 of 3 trigger` |

---

## Appendix B: Signal Extraction Pseudocode

```python
# Signal 1: Confidence (from h-m1)
entropy_traj = [entropy(probs) for probs in confidence_trajectory]
variance = np.std(entropy_traj)

# Signal 2: Symbolic (new)
state_hashes = [hash(frozenset(s.pp.items())) for s in states]
collisions = len(state_hashes) - len(set(state_hashes))
state_sizes = [len(s.goals) for s in states]
growth_rate = fit_exponential_trend(state_sizes)

# Signal 3: Search tree (from h-m2)
backtrack_count = sum(1 for e in tree.edges if e.is_backtrack)
backtrack_freq = backtrack_count / max(len(tree.nodes), 1)
```

---

**Generated by:** Phase 3 Implementation Planning
**Next Phase:** Architecture design via architecture-agent
