# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-12 07:42:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap1
- **Gap Title**: Lack of Standardized Dataset Deprecation and Versioning Workflows
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All convergence criteria met: specific claim, mechanism, testable predictions, novelty, feasibility, objections addressed. All personas reached STRONG verdicts across all dimensions.

### Key Insights

1. **NPM-inspired semantic versioning**: Borrowing from software package managers provides proven deprecation patterns that can be adapted to datasets, where "breaking changes" are statistical (distribution shifts causing performance degradation) rather than syntactic (API changes).

2. **Two-phase adaptive calibration**: Solves the bootstrapping problem for new datasets by starting with literature-derived conservative defaults (7%/2%/0.5% for MAJOR/MINOR/PATCH) and refining to dataset-specific thresholds after sufficient training data (≥20 models).

3. **Hybrid detection approach**: Automated statistical tests (KS, MMD) catch distribution drift, while manual metadata review catches semantic/ethical changes (license, data collection methods) that statistics miss.

4. **Complementary evidence strategy**: Using both proxy metrics (GitHub Issues analysis at scale) and direct metrics (controlled reproduction experiments) provides stronger evidence than either alone.

### Breakthrough Moments

1. **Exchange 1-2**: Dr. Nova's creative reframing - datasets aren't code, they need different versioning semantics. This led to the NPM analogy and semantic versioning adapted to drift detection.

2. **Exchange 7**: Dr. Nova's adaptive threshold insight - instead of arbitrary fixed thresholds, learn optimal thresholds per dataset based on observed performance impacts. This solved Prof. Rex's "arbitrary 5%" concern.

3. **Exchange 10**: Prof. Pax's feasibility confirmation - all components implementable with existing tools (scipy, sklearn, DVC/HF APIs), 5-10 min computational overhead. This removed feasibility concerns.

4. **Exchange 12-13**: Prof. Rex's P2b challenge and Dr. Nova's enhancement - adding direct reproducibility test (controlled experiment with 40 researchers) alongside proxy metric (GitHub Issues) strengthened the evidence base.

---

## Final Hypothesis

### Title
**Semantic Dataset Versioning with Adaptive Drift-Based Deprecation (SVAD)**

### Hypothesis ID
H-SVAD-v1

### Core Claim
Under ML dataset management contexts, if we implement SVAD that combines automated drift detection (KS test + MMD on PCA-reduced features) with adaptive threshold calibration and dependency-aware deprecation workflows, then reproducibility rates will improve by 15-25% compared to manual versioning practices, because automated detection and notification of breaking changes makes silent reproducibility failures explicit and actionable.

### Mechanism

**Four-step causal chain:**

1. **Detection layer**: Statistical tests (KS test, MMD) compare dataset v_new vs v_old on PCA-reduced features → compute drift score
   - *Evidence*: González-Cebrián et al. (2024) validated PCA + drift metrics; computationally feasible (O(n log n))
   - *Falsifier*: If drift detection misses known breaking changes (ImageNet→ImageNet-v2), mechanism fails

2. **Classification layer**: Drift score vs adaptive thresholds (cold-start at 7%/2%/0.5%, refined per-dataset after ≥20 models) → MAJOR/MINOR/PATCH version bump
   - *Evidence*: Two-phase calibration with literature-derived defaults
   - *Falsifier*: If classification accuracy <75% on historical changes, threshold mechanism unreliable

3. **Notification layer**: MAJOR bump triggers 90-day deprecation workflow → automated notifications to dependent models via dependency graph
   - *Evidence*: DVC/MLflow already track lineage; extension to dataset versions is engineering effort
   - *Falsifier*: If notifications don't reach researchers or are ignored, workflow fails

4. **Reproducibility gain**: Researchers receive explicit version warnings → re-run experiments with version-pinned environment → reproducibility improves
   - *Evidence*: Hypothesis predicts >50% reduction in silent failures (P2) and ≥90% success rate (P2b)
   - *Falsifier*: If P2/P2b fail (no significant improvement), causal chain doesn't produce expected outcome

**Why this works**: Current practice lacks automated detection, leading to silent reproducibility failures (e.g., ImageNet→ImageNet-v2 causing unnoticed performance drops). SVAD makes breaking changes explicit and actionable through automated detection + semantic versioning + deprecation workflow.

---

## Predictions

### P1: Drift Detection Accuracy (PRIMARY)
**Statement**: SVAD will correctly classify ≥85% of known historical dataset version changes as MAJOR/MINOR/PATCH with precision ≥70% and recall ≥85%

**Test Method**: Apply SVAD to 15 datasets with documented version histories (ImageNet, CIFAR, GLUE, COCO, MS-MARCO, SQuAD, WMT, MNIST, Fashion-MNIST, etc.); compare automated classification against expert labels

**Success Criterion**: Precision ≥70%, Recall ≥85%, F1 ≥75%

**Falsification**: If precision <60% OR recall <75%, drift detection unreliable for production use

### P2: Proxy Reproducibility Metric
**Statement**: SVAD deployment will reduce "silent reproducibility failures" (GitHub Issues mentioning "cannot reproduce" + "dataset") by >50%

**Test Method**: Analyze GitHub Issues corpus (2019-2025); simulate SVAD deployment via temporal analysis; measure issue rate reduction

**Success Criterion**: >50% reduction in reproducibility-related dataset issues

**Falsification**: If reduction <30%, proxy metric doesn't show substantial impact

### P2b: Direct Reproducibility Metric (PRIMARY)
**Statement**: In controlled reproduction experiments, SVAD-enabled environments will achieve ≥90% reproduction success rate vs <70% for manual versioning

**Test Method**: 2×20 controlled experiment: 40 researchers attempt to reproduce 20 papers from Papers With Code; random assignment to SVAD vs Manual conditions; measure success rate and time to reproduction

**Success Criterion**: SVAD success ≥90%, Manual <70%, Fisher's exact test p<0.05, statistical power 0.80

**Falsification**: If SVAD success <80% OR no significant difference (p≥0.05), direct reproducibility impact not demonstrated

### P3: Error Rate Control
**Statement**: SVAD will achieve <5% false negative rate while maintaining <20% false positive rate

**Test Method**: Hold out 20% of 15 datasets (~30 version transitions); apply calibrated SVAD; measure FN and FP rates

**Success Criterion**: FN <5%, FP <20%

**Falsification**: If FN ≥10% OR FP ≥30%, error rates too high for safety-critical applications

### P4: Metadata Change Detection
**Statement**: Hybrid SVAD system (automated stats + manual metadata review) will detect 100% of critical metadata changes requiring manual review

**Test Method**: Create 50 synthetic version pairs with metadata-only changes; test on real cases (ImageNet licensing, LAION-5B policy updates)

**Success Criterion**: 100% detection rate for critical metadata changes flagged for manual review

**Falsification**: If any critical ethical/legal change is missed, safety net fails

---

## Novelty

**Key Innovation**: First unified system combining (1) automated drift detection, (2) semantic versioning (MAJOR/MINOR/PATCH), (3) adaptive per-dataset thresholds, and (4) dependency-aware deprecation workflows.

**Differentiation from Prior Work**:

| Prior Work | What They Did | What SVAD Adds |
|------------|---------------|----------------|
| González-Cebrián et al. (2024) | Drift detection for versioning events | Semantic meaning (MAJOR vs MINOR) + deprecation workflows |
| DVC (15.5K stars) | Snapshot-based dataset versioning | Semantic versioning + automated breaking change detection |
| HuggingFace (21.4K stars) | Revision-based versioning | Automated drift detection + deprecation workflows |
| NPM semantic versioning | Software package version management | Adapted to datasets where "breaking" = statistical drift causing performance degradation |

---

## Experimental Design

### Dataset Corpus
15 datasets with documented version histories:
- Computer Vision: ImageNet/ImageNet-v2, CIFAR-10/CIFAR-10.1, COCO, MNIST, Fashion-MNIST
- NLP: GLUE/SuperGLUE, MS-MARCO, SQuAD, WMT
- Diverse domains to test generalization

### Baselines
1. **Manual versioning** (current practice): Researchers document versions in README files
2. **DVC snapshot versioning**: Git-like snapshots without semantic meaning
3. **HuggingFace revision system**: Revision IDs without automated detection

### Experimental Protocol

**Experiment Suite 1: Drift Detection Validation**
- Apply SVAD to ALL historical version transitions (not cherry-picked)
- Measure: Precision, Recall, F1 for MAJOR/MINOR/PATCH classification
- Success: Precision ≥70%, Recall ≥85%, F1 ≥75%

**Experiment Suite 2: Reproducibility Impact**
- 2a. Proxy metric: GitHub Issues analysis (2019-2025)
- 2b. Direct metric: 2×20 controlled experiment (40 researchers, 20 papers)
- Success: >50% reduction (proxy), ≥90% vs <70% (direct, p<0.05)

**Experiment Suite 3: Error Rate Control**
- Test on 20% held-out datasets (~30 version transitions)
- Success: FN <5%, FP <20%

**Experiment Suite 4: Metadata Change Detection**
- Test on 50 synthetic + real metadata-only changes
- Success: 100% detection rate for critical changes

---

## Limitations

### Scope Boundaries
**Applies to**:
- Archival datasets with infrequent updates (ImageNet, CIFAR, GLUE)
- ML repositories with dependency tracking (DVC, HuggingFace, MLflow)
- Domains where distribution shift is measurable (vision, NLP, RL)

**Does NOT apply to**:
- Streaming datasets with continuous drift (Twitter feeds, real-time sensors)
- Proprietary datasets without public version histories
- Cross-repository dependencies (requires shared metadata standard - future work)
- Metadata-only changes handled by hybrid manual review

### Known Limitations
1. **Bootstrapping period**: New datasets lack historical performance data for threshold calibration (mitigated by cold-start defaults)
2. **Non-Python ecosystems**: Initially targets Python (R, Julia future work)
3. **Adoption barrier**: Technical infrastructure doesn't guarantee behavioral change (mitigated by demonstrating value via P2b)
4. **Threshold maintenance**: Governance model for long-term threshold updates needs validation

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All personas reached STRONG verdicts after 15 exchanges |
| **Clarity Verified** | Yes |
| **Novelty** | STRONG - First unified semantic versioning system for datasets |
| **Falsifiability** | STRONG - Four prediction sets with explicit success/failure criteria |
| **Significance** | STRONG - Addresses ICLR 2025 workshop gap, enables future research |
| **Feasibility** | STRONG - Implementable with existing tools, no fundamental barriers |
| **Remaining Objections** | Adoption barrier, threshold maintenance, cross-repo dependencies (acknowledged) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
