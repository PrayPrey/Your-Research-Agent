# Gap Selection - Phase 2A Initialization

**Selected Gap:** Gap 2 - Interaction Effects Between Filtering, Mixing, and Selection Strategies

## Selection Criteria

Priority: **P1-CRITICAL** (HIGH + PRIMARY)
Evidence: 7 sources (4 papers, 3 repos)
Impact: Directly addresses user's main RQ "how do strategies impact FM performance"

## Gap Details

**Current State:** Research treats filtering, mixing, selection as independent optimization problems. DATAMASK (2025) discovered quality-only selection shows diminishing returns while diversity-only selection remains effective. No comprehensive study examines interaction effects.

**Missing Piece:** Empirical analysis of how combining different data curation strategies affects downstream performance.

**Related Papers:**
- arXiv 2403.16952 (Data Mixing Laws)
- arXiv 2507.00038 (V-Information)
- arXiv 2311.04016 (Dataset Indicators)
- DATAMASK (ByteDance, 2025)

**Implementation Resources:**
- ByteDance-Seed/DATAMASK (20★)
- sail-sg/regmix (194★)
- HazyResearch/aioli (32★)

## Failure Context (Serena Memory)

**Previous Hypothesis:** h-e1 (FAIL - MUST_WORK_GATE_FAIL)

**Root Causes:**
1. Stage semantics indirect — "Pre-training/RAG/Agent" don't parameterize quality thresholds
2. PoC scale insufficient (<100 steps, 100K tokens, mock eval)
3. Threshold-stage coupling assumption wrong

**Lessons for This Gap:**
- Avoid stage-conditioned parameterization
- Use metric-driven formulation (accuracy vs F1 vs success_rate)
- Real evaluation required (not mock)
- Scale matters (10M tokens, 5 epochs minimum)

**Prohibited Approaches:**
- Stage-conditioned quality thresholds
- Weak heuristic filters (fact density, imperative ratio)
- Mock evaluation for stage-specific metrics
- PoC scale <100K tokens without real benchmarks

**What Showed Promise:**
- Modular data → filter → train → evaluate → BO pipeline
- BoTorch multi-objective optimization
- Cosine similarity configuration comparison
