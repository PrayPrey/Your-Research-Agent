# Phase 2C: Experiment Design Brief
# Hypothesis h-m1: NL Hint Ablation

**Generated**: 2026-08-20T04:15:00Z  
**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Archon Task ID**: 100fc27f-e71c-43b4-abd4-fd896677e021

---

## Hypothesis Statement

**h-m1**: NL hint removal drops LLM success by 25-35 percentage points (tests 60% contribution claim)

**Predicted Effect**:
- Baseline (with NL): 65%
- Ablated (no NL): 35%
- Delta: 30 percentage points

**Falsification Criterion**: IF Δ < 10%, reject 60% NL contribution claim

---

## Executive Summary

This experiment tests the mechanistic claim that natural language hints contribute 60% of LLM-guided theorem prover advantage by ablating NL comments/docstrings from Lean 4 formal statements and measuring performance drop. Uses miniF2F-v2c (competition-level, 244 test problems) as benchmark, comparing LeanCopilot performance on original vs NL-stripped versions.

**Key Risk**: NL comment removal may break Lean type-checking if comments are semantically load-bearing. Mitigation: 20-problem pilot validates ablation feasibility before full run.

**Dataset**: miniF2F-v2c (real, standard benchmark, Type: standard)  
**Sample Size**: 244 problems (statistically meaningful, full test set)

---

## Research Context

### From Phase 2A/2B
- **Main hypothesis**: LLM-guided provers (65%) vs automated provers (15%) gap explained by 3 mechanisms: NL understanding (60%), proof depth (30%), corpus patterns (10%)
- **h-m1 role**: Tests core NL mechanism via controlled ablation
- **Prerequisites**: None (independent from H-E1 baseline measurement)
- **Gate type**: MUST_WORK (failure blocks entire mechanistic attribution framework)

### Literature Foundation (Exa Search)
**miniF2F-v2 Dataset** (https://github.com/roozbeh-yz/miniF2F_v2):
- **v2c variant**: Competition-level (IMO, AMC problems), formal/informal statements aligned
- **244 test problems**: All provable, fully verified, docstrings included
- **Lean 4.17-4.26**: Modern Lean 4 versions, Mathlib-compatible
- **Evaluation protocol**: @32 sampling budget (32 tactic generations per problem), 300s timeout standard

**LeanCopilot System** (https://github.com/lean-dojo/LeanCopilot):
- **suggest_tactics**: LLM-based tactic suggestion (ReProver default model)
- **search_proof**: Combines LLM tactics + AESOP rule-based search
- **Context inputs**: Goal state (hypotheses + target), potentially NL docstrings
- **Deployment**: Local inference (no cloud dependencies), configurable beam search

**Critical Finding**: Google DeepMind miniF2F fork includes "natural language docstrings taken from source problems to make identification of misformalizations easier" — confirms NL hints are embedded in formal statements as comments/docstrings.

---

## Experimental Design

### Dataset Specification

**Primary Dataset**: miniF2F-v2c (AlphaProof benchmark)

| Property | Value |
|----------|-------|
| **Name** | miniF2F-v2c (competition-level) |
| **Type** | standard (real, established benchmark) |
| **Source** | HuggingFace: roozbeh-yz/miniF2F_v2, config: v2c |
| **Split** | test (244 problems) |
| **Format** | Lean 4 theorem declarations with docstrings |
| **Size** | 244 problems (full test set) |
| **Lean Version** | 4.17-4.26 compatible (use 4.17 for consistency) |
| **Mathlib** | Implicit via dataset (no separate download) |

**Sample Size Justification**: 244 problems = full standard test set. Δ=30% effect, α=0.05, power=0.8 requires ~42 problems per condition. 244 provides 5.8× margin for stratification and edge cases.

**No Synthetic Data**: This is a real, curated benchmark from mathematical competitions. Type = standard (established dataset).

---

### Experimental Conditions

#### Condition 1: Baseline (NL-Intact)
- **Config**: Original miniF2F-v2c Lean files
- **NL Hints**: Preserved (docstrings + inline comments)
- **Prover**: LeanCopilot (search_proof tactic)
- **Model**: ReProver (default)
- **Budget**: @32 sampling (32 tactic generations/problem)
- **Timeout**: 300s per problem
- **Expected Success**: 60-70% (literature: 65% predicted)

#### Condition 2: Ablated (NL-Removed)
- **Config**: Preprocessed Lean files with NL stripped
- **NL Removal**: 
  1. Strip `/--! ... -/` docstrings (problem descriptions)
  2. Strip `-- ...` inline comments
  3. Preserve Lean code structure (theorem name, type, := by)
- **Prover**: LeanCopilot (same config as Baseline)
- **Budget**: @32 sampling (equalized)
- **Timeout**: 300s per problem
- **Expected Success**: 30-40% (65% - 30% drop)

**Ablation Verification** (20-problem pilot):
- Sample 20 problems randomly from test set
- Apply NL removal preprocessing
- Verify Lean type-checks (lake build --lean)
- Measure success on pilot subset
- **Go/No-Go**: IF >3 type-check failures OR pilot Δ < 5%, escalate fallback

**Fallback Plan** (if NL removal breaks type-checking):
- Pivot to informal Mathlib documentation removal (strip external docs, keep code comments)
- Report limitation: Cannot isolate inline NL hints from semantic annotations

---

### Data Preparation Pipeline

**Step 1: Dataset Download**
```python
from datasets import load_dataset
ds = load_dataset("roozbeh-yz/miniF2F_v2", "v2c")
test_problems = ds["test"]  # 244 rows
# Schema: {formal_statement: str, informal_statement: str, ...}
```

**Step 2: NL Ablation Preprocessing**
```python
import re

def strip_nl_hints(lean_code: str) -> str:
    """Remove docstrings and comments from Lean 4 code."""
    # Strip /--! docstrings -/
    lean_code = re.sub(r'/--!.*?-/', '', lean_code, flags=re.DOTALL)
    # Strip -- inline comments
    lean_code = re.sub(r'--[^\n]*', '', lean_code)
    # Preserve theorem structure
    return lean_code.strip()

# Generate ablated dataset
ablated_problems = [
    {**p, "formal_statement": strip_nl_hints(p["formal_statement"])}
    for p in test_problems
]
```

**Step 3: Pilot Validation** (20 problems)
```bash
# Sample 20 problems randomly
# Write to Test_Ablated_Pilot.lean
# Run: lake build Test_Ablated_Pilot.lean
# Check: 0 errors expected (if >3, abort and escalate)
```

**Step 4: Full Dataset Generation**
- Write Baseline: `MiniF2F_v2c_Test.lean` (original)
- Write Ablated: `MiniF2F_v2c_Test_NoNL.lean` (stripped)
- Verify both compile with Lean 4.17

---

### Baseline Experiments

**Baseline 1: LeanCopilot on Original miniF2F-v2c**
- **Purpose**: Measure LLM performance with NL hints
- **Config**: search_proof tactic, @32 sampling, 300s timeout
- **Metrics**: Success rate (% proved), avg tactics/proof, proof depth distribution

**Baseline 2: LeanCopilot on NL-Ablated miniF2F-v2c**
- **Purpose**: Measure LLM performance without NL hints
- **Config**: Identical to Baseline 1 (only input differs)
- **Metrics**: Success rate, avg tactics/proof, proof depth distribution

**Comparison Baseline** (optional, from H-E1 if available):
- lean-auto (automated hammer) success rate on same dataset
- Provides triangulation: LLM-with-NL > LLM-without-NL > lean-auto

---

### Evaluation Metrics

**Primary Metric**: Success Rate Delta (Δ)
- **Definition**: % proved in Baseline - % proved in Ablated
- **Predicted**: 30 percentage points (65% - 35%)
- **Falsification**: Δ < 10% → reject 60% NL contribution claim
- **Success**: 25% ≤ Δ ≤ 35% → confirm 60% contribution (±5% tolerance)

**Secondary Metrics**:
- **Proof Length**: Avg tactics per successful proof (tests depth confound)
- **Timeout Rate**: % problems hitting 300s limit (ablation may increase search time)
- **Error Types**: Type-check failures, tactic failures, timeouts (diagnostic)

**Stratification** (if metadata available):
- **By Source**: AMC (informal language) vs IMO (formal) → expect larger Δ on AMC
- **By Difficulty**: Easy/Medium/Hard → test if NL helps more on hard problems
- **By Proof Type**: Algebra, Geometry, Number Theory → domain-specific effects

---

### Statistical Analysis Plan

**Hypothesis Test**: Paired comparison (same 244 problems, two conditions)
- **Null**: Δ = 0 (NL hints have no effect)
- **Alternative**: Δ > 25% (NL hints contribute ≥60% of gap)
- **Test**: McNemar's test (paired proportions, same problems)
- **Significance**: α = 0.05
- **Power**: 1-β = 0.8 (achieved with N=244, Δ=30%)

**Effect Size**: Cohen's h (proportions)
- **Predicted**: h = 0.63 (large effect)
- **Minimum Detectable**: h = 0.3 (medium effect, Δ ≈ 15%)

**Confidence Interval**: 95% CI on Δ
- **Bootstrap**: 10,000 resamples (accounts for problem-level variance)
- **Expected**: [0.25, 0.35] (narrow, N=244 provides precision)

**Stratified Analysis** (if feasible):
- Separate Δ by problem source (AMC vs IMO)
- Test interaction: Does NL effect vary by domain?
- Bonferroni correction: α = 0.025 per stratum (2 comparisons)

---

## Implementation Requirements

### Infrastructure

**Compute**: 
- 1× GPU (NVIDIA A5000 or equivalent, 24GB VRAM)
- 32 CPU cores
- 128GB RAM (LeanCopilot + Lean elaborator memory)

**Software Stack**:
- Lean 4.17.0 (toolchain)
- Mathlib (latest compatible with miniF2F-v2c)
- LeanCopilot (https://github.com/lean-dojo/LeanCopilot)
- ReProver model (default, included with LeanCopilot)
- Python 3.9+ (dataset loading, preprocessing)

**Estimated Runtime**:
- Pilot (20 problems × 2 conditions × 300s): ~3 hours
- Full experiment (244 problems × 2 conditions × 300s): ~41 hours (1.7 days)
- **Total**: 2 days (with pilot validation)

---

### Code Modules

**Module 1: Dataset Loader**
- Download miniF2F-v2c from HuggingFace
- Parse Lean formal_statement field
- Export to .lean files (one theorem per line)

**Module 2: NL Ablation Preprocessor**
- Regex-based docstring/comment removal
- Preserve Lean syntax (theorem, type, := by)
- Validation: Lean type-checker (lake build)

**Module 3: LeanCopilot Evaluation Harness**
- Iterate over test problems
- Apply search_proof tactic with @32 sampling, 300s timeout
- Log: success (bool), tactics_used (int), wall_time (float), error_type (str)
- Save: results.jsonl (one row per problem)

**Module 4: Statistical Analysis**
- Compute success rates (Baseline vs Ablated)
- McNemar's test (paired proportions)
- Bootstrap CI on Δ
- Stratified analysis (if metadata available)
- Generate plots: success rate by condition, Δ distribution

---

## Validation Criteria

### Technical Validation
- [ ] Pilot: ≤3 type-check failures (out of 20) after NL removal
- [ ] Pilot: Δ ≥ 5% (sanity check: ablation has measurable effect)
- [ ] Full run: Both datasets compile without errors
- [ ] Full run: All 244 problems evaluated in both conditions

### Scientific Validation
- [ ] **Primary**: 25% ≤ Δ ≤ 35% (confirms 60% NL contribution)
- [ ] **Falsification**: IF Δ < 10%, reject NL hypothesis
- [ ] **Statistical**: p < 0.05 (McNemar's test)
- [ ] **Robustness**: 95% CI excludes 0 (NL effect is real)

### Gate Decision (MUST_WORK)
- **PASS**: Δ ≥ 25% AND p < 0.05 → h-m1 validated, proceed to Phase 3
- **FAIL**: Δ < 10% OR p ≥ 0.05 → reject NL mechanism, terminate h-m1
- **INCONCLUSIVE**: 10% ≤ Δ < 25% → weaker effect than predicted, re-evaluate attribution percentages

---

## Risk Mitigation

### Risk 1: Type-Check Failures After NL Removal
- **Probability**: 30%
- **Impact**: HIGH (blocks experiment)
- **Mitigation**: 20-problem pilot BEFORE full run
- **Fallback**: Pivot to informal Mathlib docs removal (external docs only)

### Risk 2: No Measurable Effect (Δ < 10%)
- **Probability**: 20%
- **Impact**: HIGH (falsifies NL hypothesis)
- **Mitigation**: Accept falsification, report negative result
- **Implication**: Revise main hypothesis (NL contributes <30%, not 60%)

### Risk 3: Confound — NL Removal Also Removes Semantic Type Info
- **Probability**: 40%
- **Impact**: MEDIUM (conflates NL understanding with type hints)
- **Mitigation**: Manual inspection of 20 ablated examples
- **Diagnostic**: IF type signatures preserved but success drops, NL effect is real

### Risk 4: Hardware Availability (GPU contention)
- **Probability**: 30%
- **Impact**: LOW (delays timeline)
- **Mitigation**: Queue jobs overnight, request dedicated GPU allocation

---

## Expected Outputs

### Deliverables
1. **Dataset Artifacts**:
   - `MiniF2F_v2c_Test.lean` (original, 244 problems)
   - `MiniF2F_v2c_Test_NoNL.lean` (ablated, 244 problems)
   - `ablation_pilot_results.json` (20-problem validation)

2. **Evaluation Results**:
   - `baseline_results.jsonl` (244 rows: problem_id, success, tactics, time)
   - `ablated_results.jsonl` (244 rows: same schema)
   - `comparison_stats.json` (Δ, p-value, CI, stratified results)

3. **Analysis Report** (04_validation.md):
   - Success rates: Baseline vs Ablated
   - Statistical tests: McNemar's, bootstrap CI
   - Stratification: AMC vs IMO (if metadata available)
   - Falsification verdict: PASS/FAIL/INCONCLUSIVE
   - Gate decision: h-m1 status

4. **Visualizations**:
   - Bar chart: Success rate by condition
   - Scatter: Per-problem success (Baseline vs Ablated)
   - Histogram: Δ bootstrap distribution

---

## Phase 3 Handoff

**If h-m1 PASSES (Δ ≥ 25%)**:
- **PRD Inputs**: 
  - LeanCopilot integration requirements
  - miniF2F-v2c dataset loading pipeline
  - NL ablation preprocessing module
  - @32 sampling budget, 300s timeout config
- **Architecture Inputs**:
  - Dataset download → Preprocessing → LeanCopilot evaluation → Statistical analysis
  - Module boundaries: loader, preprocessor, harness, analyzer
- **PRP Complexity**: Tier 1 (LOW) — existing LeanCopilot infrastructure, regex preprocessing, standard HuggingFace dataset

**If h-m1 FAILS (Δ < 10%)**:
- Report negative result in 04_validation.md
- Revise main hypothesis: NL contributes <30% (not 60%)
- Continue with h-m2, h-m3 (other mechanisms may still hold)

---

## References

### Datasets
- **miniF2F-v2c**: https://huggingface.co/datasets/roozbeh-yz/miniF2F_v2
- **Original miniF2F**: https://github.com/openai/miniF2F
- **DeepMind AlphaProof fork**: https://github.com/google-deepmind/miniF2F

### Tools
- **LeanCopilot**: https://github.com/lean-dojo/LeanCopilot
- **ReProver model**: https://leandojo.org (default with LeanCopilot)
- **Lean 4**: https://leanprover.github.io

### Literature
- **miniF2F-v2 Paper**: https://arxiv.org/abs/2511.03108 (NeurIPS 2025)
- **LeanCopilot Paper**: https://arxiv.org/abs/2404.12534 (ICML 2024)
- **Original miniF2F**: https://arxiv.org/abs/2109.00110 (ICLR 2022)

---

**Phase 2C Complete for h-m1**  
**Next Phase**: Phase 3 Implementation Planning (PRD, Architecture, PRP, Archon tasks)
