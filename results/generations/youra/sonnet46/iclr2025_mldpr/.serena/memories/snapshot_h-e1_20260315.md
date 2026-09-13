# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-15T04:35:00Z
**Hypothesis:** h-e1
**Statement:** A DTS-weighted documentation completeness scoring system is buildable from public API metadata across HuggingFace Hub, OpenML, and UCI ML Repository, achieving ≥70% field coverage retrieval rate across the target corpus of ~105K datasets.
**Final Status:** CONDITIONAL_PASS
**Gate Result:** CONDITIONAL_PASS (gate.satisfied=true)

## Results

- Validation: CONDITIONAL_PASS
- Gate Type: MUST_WORK
- Coverage rate: 0.918 (threshold ≥0.70 — PASS)
- Pearson r: 0.577 (simulated annotations, PoC constraint — PENDING real annotation)
- n_datasets: 760 (HF:498, OpenML:200, UCI:62)
- mechanism_activated: true (all 4 indicators)

## Key Findings

1. HF and OpenML APIs provide sufficient metadata coverage for DTS scoring
2. UCI field mapping needs refinement (ucimlrepo returns differently structured metadata)
3. Preprocessing and Uses sections have near-zero coverage across all repos
4. DTS weighting scheme (collection=2.1, preprocessing=1.8) penalizes mean score despite high coverage
5. System is buildable and mechanism is correctly implemented

## Code Artifacts

- scorer.py, collect_hf.py, collect_openml.py, collect_uci.py
- validation.py, visualization.py, evaluate.py, experiment.py
- 53 tests passing (test_scorer.py, test_evaluate.py, test_validation.py)

---
*Per-hypothesis snapshot for Phase 2A reference*
*Written at: 2026-03-15T04:35:00Z*
