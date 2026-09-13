# Phase Readiness Plan (PRP)
# H-M2: Proof Depth Filtering Analysis

**Generated**: 2026-08-20  
**Hypothesis ID**: h-m2  
**Phase**: 3 → 4 Transition  
**Gate**: SHOULD_WORK

---

## 1. Readiness Summary

**Status**: READY for Phase 4 (Implementation)

**Phase 3 Completeness**:
- ✓ PRD finalized (03_prd.md)
- ✓ Architecture designed (03_architecture.md)
- ✓ Logic specified (03_logic.md)
- ✓ Configuration schema defined (03_config.md)
- ✓ Budget allocated (03_budget_allocation.md)
- ✓ Tasks generated (pending: Step 10)

**Blockers**: None

---

## 2. Implementation Scope Verification

### 2.1 Hypothesis Alignment

**Original Hypothesis** (Phase 2B):
> Proof depth filtering (≤3 tactics) drops LLM success by 10-20 percentage points (tests 30% contribution claim)

**Implementation Target** (Phase 3):
- Post-hoc analysis pipeline: LLM prover → tactic extraction → stratified success rates
- Primary metric: Δ = Success_full - Success_shallow
- Gate criteria: 5% < Δ < 30%

**Alignment Check**: ✓ Implementation directly measures hypothesis claim (depth contribution to LLM advantage)

### 2.2 Falsification Coverage

**Falsification Criteria** (from 02c_experiment_brief.md):
- IF Δ < 5%: Reject (depth contributes <8% of gap)
- IF Δ > 30%: Reject (depth explains >60%, contradicts NL dominance)

**Implementation Coverage**:
- ✓ Gate evaluation logic (03_logic.md, Section 7.1)
- ✓ Bootstrap CI for precision (Section 5.2)
- ✓ McNemar test for significance (Section 5.1)
- ✓ PASS/FAIL determination automated

**Verdict**: Full falsification criteria implemented.

---

## 3. Technical Readiness

### 3.1 Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| miniF2F Lean 4 dataset | Available | Public repo, Apache 2.0 license |
| LeanCopilot API | Assumed available | Fallback: DeepSeek-Prover-V1.5 |
| Lean 4.14+ | Available | Install via elan |
| Python 3.10+ | Available | Standard environment |
| scipy/pandas/matplotlib | Available | pip install |

**Risk**: LeanCopilot API access unconfirmed
- **Mitigation**: Architecture includes DeepSeek-Prover fallback
- **Action**: Verify API credentials before Phase 4 start

### 3.2 Infrastructure

**Compute Requirements**:
- CPU: Any modern machine (no GPU required if using cloud LLM API)
- RAM: 8 GB (Lean verification)
- Storage: 200 MB (dataset + outputs)
- Network: Stable (API calls for 244 theorems × 16 attempts)

**Runtime Estimate**: 16-18 hours (mostly API-bound proof collection)

**Checkpoint Strategy**: Resume from last completed theorem (implemented in A-2)

### 3.3 Code Complexity

**Total Estimated LOC**: ~500 lines Python + ~50 lines Lean 4

| Module | LOC | Complexity |
|--------|-----|------------|
| proof_runner.py | 150 | Medium (API client, retry logic) |
| tactic_extractor.py | 100 | Medium (AST parsing + fallback) |
| analyzer.py | 120 | Low (scipy/pandas wrappers) |
| config.py | 40 | Low (dataclass) |
| main.py | 70 | Low (orchestration) |
| Lean 4 metaprogram | 50 | Medium (tactic counting) |

**Feasibility**: Within 30K token budget (Medium tier).

---

## 4. Task Execution Plan

### 4.1 Epic Tasks (5 total)

| ID | Task | Complexity | Budget | Dependencies |
|----|------|------------|--------|--------------|
| A-1 | Infrastructure Setup | 8 | 5K | None |
| A-2 | Proof Collection | 14 | 8K | A-1 |
| A-3 | Tactic Extraction | 12 | 7K | A-2 |
| A-4 | Statistical Analysis | 10 | 6K | A-3 |
| A-5 | Report Generation | 6 | 4K | A-4 |

**Execution Order**: Sequential (A-1 → A-2 → A-3 → A-4 → A-5)

**Rationale**: Data pipeline dependencies (each stage consumes previous output).

### 4.2 Parallel Opportunities

**None**: Pipeline is inherently sequential.

**Rationale**: Stage N requires output from Stage N-1 (proofs → tactic counts → statistics).

### 4.3 Validation Checkpoints

**Checkpoint 1** (after A-1): Environment functional
- Lean 4 installed, API credentials verified
- miniF2F dataset cloned, test split accessible

**Checkpoint 2** (after A-2): Proofs collected
- proofs.json contains ≥30 successful proofs (statistical power check)
- If <30: BLOCK hypothesis, report insufficient data

**Checkpoint 3** (after A-3): Tactic counts extracted
- tactic_counts.csv has valid counts (no negatives, no NaNs)
- Fallback accuracy ≥80% (if AST parsing failed)

**Checkpoint 4** (after A-4): Statistics computed
- Δ computed, McNemar p-value, bootstrap CI
- Gate outcome determined (PASS/FAIL)

**Checkpoint 5** (after A-5): Report generated
- 04_validation.md written, all deliverables present

---

## 5. Risk Assessment

### 5.1 Technical Risks

**R1: Insufficient solved problems (<30)**
- **Probability**: 30% (depends on LLM baseline)
- **Impact**: HIGH (blocks statistical validation)
- **Mitigation**: Use H-E1 or H-M1 proof logs if available
- **Fallback**: Report hypothesis as BLOCKED (not FAILED)

**R2: Tactic extraction failure**
- **Probability**: 20% (Lean 4 metaprogramming complexity)
- **Impact**: MEDIUM (fallback to script counting available)
- **Mitigation**: Dual-path implementation (AST + regex)
- **Validation**: 10% manual spot-check (≥80% accuracy required)

**R3: API rate limits / downtime**
- **Probability**: 15%
- **Impact**: MEDIUM (delays proof collection, but doesn't block)
- **Mitigation**: Retry logic (3× exponential backoff), checkpoint/resume
- **Fallback**: Local LLM prover (requires GPU)

### 5.2 Validity Threats

**V1: Difficulty confound** (shallow problems easier)
- **Test**: Compare lean-auto success on shallow vs deep strata
- **Data needed**: H-E1 lean-auto results (if available)
- **Action**: Implement confound check in A-4 (optional, if data exists)

**V2: Search bias** (LLM prefers shallow proofs)
- **Limitation**: Post-hoc filtering ≠ controlled ablation
- **Documentation**: Report in 04_validation.md limitations section
- **Impact**: Doesn't invalidate result, but weakens causal claim

### 5.3 Gate Risks

**Borderline outcomes** (Δ near 5% or 30% threshold):
- **Probability**: 20%
- **Handling**: Report 95% CI, flag as borderline, defer to Phase 4.5 synthesis
- **Decision rule**: Use CI overlap with threshold to determine PASS/FAIL

---

## 6. Phase 4 Entry Criteria

### 6.1 Mandatory Criteria

**C1**: All Phase 3 documents finalized
- ✓ PRD, Architecture, Logic, Config, Budget, PRP

**C2**: Budget allocated
- ✓ 30K tokens (Medium tier)

**C3**: Tasks generated
- ⏳ Pending (Step 10 of Phase 3)

**C4**: No technical blockers
- ✓ All dependencies available or have fallbacks

**C5**: Hypothesis testable
- ✓ Clear falsification criteria (Δ < 5% or Δ > 30%)

**Status**: 4/5 criteria met (C3 pending task generation)

### 6.2 Optional Enhancements

**E1**: Confound control (lean-auto depth comparison)
- Status: Optional (requires H-E1 data)
- Action: Check verification_state for H-E1 completion

**E2**: Pilot study (N=20 theorems)
- Status: Skipped (pipeline complexity low, pilot not needed)
- Rationale: Validation checkpoint after A-3 sufficient

**E3**: Multiple LLM provers
- Status: Out of scope (single baseline comparison)
- Rationale: Focus on depth mechanism, not prover comparison

---

## 7. Success Criteria

### 7.1 Implementation Success

**IS1**: All 5 Epic tasks completed (A-1 through A-5)

**IS2**: Pipeline executes end-to-end without manual intervention

**IS3**: All deliverables generated:
- proofs.json (successful proofs)
- tactic_counts.csv (extracted depths)
- results.json (success rates, Δ, statistics)
- depth_histogram.png (visualization)
- 04_validation.md (report)

**IS4**: Statistical power check passed (≥30 solved problems)

**IS5**: Tactic extraction validated (≥80% accuracy if fallback used)

### 7.2 Hypothesis Outcome Success

**HO1**: Gate outcome determined (PASS or FAIL)

**HO2**: Effect size measured (Δ with 95% CI)

**HO3**: Statistical significance tested (McNemar p-value reported)

**HO4**: Limitations documented (confounds, validity threats)

**HO5**: Next steps defined (Phase 4.5 integration or reflection)

---

## 8. Timeline

**Phase 4 Duration**: 2 days (per 02c_experiment_brief.md)

| Day | Tasks | Milestones |
|-----|-------|------------|
| Day 1 | A-1, A-2 (partial) | Environment setup, proof collection started |
| Day 2 | A-2 (complete), A-3, A-4, A-5 | Pipeline complete, report generated |

**Bottleneck**: A-2 (proof collection, 6-8 hours runtime)

**Parallelization**: None (sequential pipeline)

**Buffer**: 6 hours (for API delays, retry logic)

---

## 9. Phase 4 Execution Notes

### 9.1 For Implementation Agent (Phase 4)

**Context to carry forward**:
- This is a MECHANISM hypothesis (tests 30% depth contribution claim)
- Gate is SHOULD_WORK (not MUST_WORK) → FAIL is acceptable outcome
- Post-hoc analysis (not a controlled ablation) → document as limitation
- Use fallback tactic counting if AST parsing complex (time vs accuracy tradeoff)

**Key decisions already made**:
- Use minimum proof depth per problem (if ANY shallow proof exists → shallow-solvable)
- Shallow threshold: ≤3 tactics
- Statistical tests: McNemar + bootstrap CI (10K resamples)
- API config: pass@16, 60s timeout, 1024 tokens

**Avoid scope creep**:
- Don't extend beyond miniF2F (244 theorems)
- Don't implement multiple depth thresholds (only ≤3)
- Don't compare multiple LLM provers (single baseline)
- Don't train/fine-tune models (post-hoc analysis only)

### 9.2 For Validator Agent (Phase 4)

**Static checks**:
- Config validation (k ≥ 1, timeout > 0, valid paths)
- CSV schema (non-negative tactic counts, no missing theorem names)
- Results schema (0 ≤ success_full ≤ 1, delta ≥ 0)

**Runtime checks**:
- Statistical power (≥30 solved problems)
- Tactic extraction accuracy (≥80% if fallback used)
- Gate evaluation correctness (5% < Δ < 30% → PASS)

**Integration checks**:
- Proof count matches (proofs.json → tactic_counts.csv)
- Theorem names consistent (miniF2F → proofs → results)
- Reproducibility (random seed, version logging)

---

## 10. Handoff Checklist

**Phase 3 → Phase 4 Handoff**:

- [x] PRD approved (03_prd.md)
- [x] Architecture designed (03_architecture.md)
- [x] Logic specified (03_logic.md)
- [x] Configuration schema (03_config.md)
- [x] Budget allocated (03_budget_allocation.md)
- [x] PRP generated (03_prp.md)
- [ ] Tasks generated (03_tasks.yaml) — **PENDING Step 10**

**Ready to proceed**: After task generation (Step 10).

---

## 11. Open Questions for Phase 4

**Q1**: Which LLM prover API to use (LeanCopilot vs DeepSeek-Prover)?
- **Decision**: Try LeanCopilot first, fallback to DeepSeek-Prover if unavailable
- **Action**: Check API credentials at start of A-1

**Q2**: Should we analyze lean-auto depth distribution (confound control)?
- **Decision**: Yes, if H-E1 data available in verification_state
- **Action**: Check after A-2 completes

**Q3**: What if Δ is exactly 5% or 30% (threshold boundary)?
- **Decision**: PASS (inclusive bounds: [5%, 30%])
- **Action**: Flag as borderline in report, review in Phase 4.5

**Q4**: What if <30 problems solved (insufficient power)?
- **Decision**: Report BLOCKED (not FAILED), check H-E1/H-M1 for reusable proofs
- **Action**: Power check after A-2, halt if underpowered

---

**PRP Status**: COMPLETE  
**Phase 4 Authorization**: READY (pending task generation in Step 10)
