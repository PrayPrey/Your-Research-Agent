# Hypothesis H-E1: lean-auto Baseline Measurement

**Type**: EXISTENCE  
**Gate**: MUST_WORK (foundation for all comparisons)  
**Status**: Phase 2C Complete - Ready for Phase 3

---

## Hypothesis Statement

Pure automated prover (lean-auto) achieves 10-25% baseline success on miniF2F Lean 4 subset

**Predicted Success Rate**: 15% ± 5% (37 ± 12 problems out of 244)

---

## Phase 2C Outputs

This folder contains the complete experiment design specification for H-E1:

### Core Documents

1. **experiment_brief.md** (611 lines)
   - Complete experiment specification
   - 14 sections covering all aspects of the baseline measurement
   - Statistical analysis plan, risk assessment, timeline
   - Reference: Main document for understanding the experiment

2. **dataset_spec.yaml** (152 lines)
   - Structured dataset specification
   - miniF2F Lean 4 test set (N=244, standard type)
   - Baseline configuration (lean-auto settings)
   - Metrics and expected outcomes
   - Reference: Machine-readable config for Phase 3/4

3. **evaluation_protocol.md** (545 lines)
   - Step-by-step execution protocol
   - Infrastructure setup, pilot run, full evaluation
   - Logging, checkpointing, error handling
   - Statistical analysis and validation
   - Reference: Operational manual for Phase 4 execution

4. **implementation_notes.md** (331 lines)
   - Technical implementation considerations
   - Timeout mechanisms, tactic count extraction
   - Harness architecture, checkpointing strategy
   - Known limitations and mitigation strategies
   - Reference: Engineering guide for Phase 3/4

5. **metadata.yaml** (175 lines)
   - Structured metadata for hypothesis h-e1
   - Phase status tracking
   - Archon integration (task ID, project ID)
   - Timeline, risks, downstream dependencies
   - Reference: Pipeline state for automation

### File Summary

| File | Size | Purpose |
|------|------|---------|
| experiment_brief.md | 19KB | Complete experiment specification |
| dataset_spec.yaml | 5KB | Dataset and baseline config |
| evaluation_protocol.md | 16KB | Step-by-step execution protocol |
| implementation_notes.md | 10KB | Technical implementation guide |
| metadata.yaml | 4KB | Pipeline metadata and tracking |
| README.md | 2KB | This file (overview) |

**Total**: 6 files, ~56KB of documentation

---

## Key Design Decisions

### 1. Full Test Set (N=244)

**Decision**: Use complete miniF2F test set, not a small sample

**Rationale**:
- Statistical power: 95% CI ±4.5% at N=244 vs ±14% at N=50
- Literature alignment: Matches published baselines
- Avoids synthetic data (real olympiad problems)

**Trade-off**: Longer execution time (2-3 hours) vs better statistical validity

### 2. Standard Dataset Type

**Decision**: Use real, established benchmark (miniF2F) vs synthetic data

**Rationale**:
- Synthetic datasets produce meaningless results (e.g., completing in <1s)
- miniF2F is widely-used baseline in theorem proving literature
- Enables comparison with published baselines

**Critical**: Experiments with synthetic data would fail to test real theorem proving capability

### 3. 300s Timeout

**Decision**: 300s per problem (vs 10s used in Mathlib4 evaluations)

**Rationale**:
- Olympiad problems harder than library theorems
- Literature standard for miniF2F (300-600s range)
- Matches lean-auto paper methodology (scaled for difficulty)

**Validation**: Pilot run + 600s sensitivity analysis

### 4. Zero-Shot Evaluation

**Decision**: No premise selection (pure automated baseline)

**Rationale**:
- Isolates automated prover capability
- Fair comparison with LLM-guided approach (both zero-shot)
- Avoids confounding from ideal premise selection

**Trade-off**: Lower success rate (~15% vs 36% with premises) vs cleaner comparison

---

## Integration with Pipeline

### Upstream Dependencies

- **Phase 2B**: Verification plan complete ✓
- **Main Hypothesis**: H-MechanisticBaseline-v1 defined ✓
- **Prerequisites**: None (independent baseline measurement)

### Downstream Impact

**Blocks**:
- **H-M3**: Random Mathlib baseline (needs h-e1 success rate for Δ comparison)
- **H-C1**: Tactic budget equalization (needs h-e1 tactic count distribution)

**Enables**:
- **Phase 5**: Baseline comparison (LLM vs lean-auto)
- **Main Hypothesis**: Mechanistic gap attribution (needs baseline foundation)

**Critical Path**: h-e1 must complete before H-M3 or H-C1 can execute

---

## Next Steps (Phase 3)

### Implementation Planning Tasks

1. **PRD Generation**: Translate experiment brief into product requirements
2. **Architecture Design**: Specify evaluation harness components
   - Problem loader module
   - Worker pool manager
   - Timeout enforcement
   - Logging subsystem
   - Checkpoint/recovery
3. **Complexity Assessment**: Estimate implementation effort
4. **PRP Creation**: Step-by-step implementation plan
5. **Archon Task Update**: Link PRD/Architecture to task b1cf534c-c7ff-48e5-a432-1d260d9ec129

### Estimated Timeline

- **Phase 3** (Implementation Planning): 5 days
- **Phase 4** (Coding + Validation): 7 days
- **Total to Baseline Measured**: 12 days

### Success Criteria

**Phase 2C** (Current):
- [x] Experiment brief complete (611 lines, 14 sections)
- [x] Dataset specification (miniF2F, N=244, standard type)
- [x] Evaluation protocol documented
- [x] Implementation notes written
- [x] Metadata and tracking in place

**Phase 3** (Next):
- [ ] PRD generated (requirements for evaluation harness)
- [ ] Architecture specification (component design)
- [ ] Complexity tier assigned (SIMPLE/MEDIUM/COMPLEX)
- [ ] PRP created (implementation steps)
- [ ] Archon tasks updated

**Phase 4** (Execution):
- [ ] Evaluation harness implemented
- [ ] Pilot run validates infrastructure (N=20, 2-5 solves)
- [ ] Full run completes (N=244)
- [ ] Baseline measured (10-25% success rate)

---

## References

### Literature

- lean-auto paper: Qian et al. (2025) - 36.6% on Mathlib4 with premises
- miniF2F benchmark: Zheng et al. (2021) - 244 test problems
- miniF2F-v2: Roozbeh et al. (2026) - Fixed unprovable statements
- AlphaProof: DeepMind (2024) - Evaluation version

### Tools

- lean-auto: https://github.com/leanprover-community/lean-auto
- miniF2F: https://github.com/google-deepmind/miniF2F
- Lean 4: v4.15.0 (pinned)

### Archon

- **Project ID**: 622e5a6a-846d-475f-bd6a-8c6080c60cbb
- **Task ID**: b1cf534c-c7ff-48e5-a432-1d260d9ec129
- **Task Title**: H-E1: lean-auto Baseline Measurement

---

## Contact

**Generated**: 2026-08-20  
**Workflow**: Phase 2C Experiment Design  
**Pipeline**: Mechanistic LLM Theorem Proving Baseline  
**Mode**: UNATTENDED (batch execution)
