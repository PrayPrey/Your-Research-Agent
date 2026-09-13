# Phase 6.5 Adversarial Review — Change Log

**Generated:** 2026-08-20  
**Rounds:** 2  
**Total revisions:** 13 edits across 6 files

---

## Round 1 Revisions (FATAL + MAJOR fixes)

### 00_abstract.md (3 edits)

**Edit 1: Lead with novelty, qualify scope**
```diff
- Automated ML research pipelines fail when hypotheses violate feasibility constraints during phase transitions, forcing expensive restarts when late-stage implementation discovers infeasibility.
+ We apply Design-by-Contract formal methods to ML research workflow automation, achieving 100% downstream failure reduction through three-layer validation (schema + pattern + compositional contracts) on placeholder hypothesis content with typed interfaces.
```

**Edit 2: Clarify corpus composition**
```diff
- We validate our approach on a 100-case placeholder hypothesis corpus with four feasibility constraints
+ We validate our approach on a 100-case placeholder hypothesis corpus (80 valid, 20 with embedded violations across four feasibility constraints: [...])
```

**Edit 3: Qualify quantitative claims with placeholder scope**
```diff
- demonstrating 100% downstream failure reduction versus schema-only baseline
+ demonstrating 100% downstream failure reduction versus schema-only baseline on placeholder content (generalization to substantive research unproven, external validity deferred to Phase 5)
```

**Edit 4: Hedge novelty claim**
```diff
- This work represents the first application of Design-by-Contract formal methods to ML research automation
+ This work represents the first application of Design-by-Contract to semantic constraint validation in research workflows
```

**Edit 5: Precision (0.01ms not "<1ms")**
```diff
- 25 LOC, <1ms execution time
+ 25 LOC, 0.01ms execution time
```

---

### 01_introduction.md (3 edits)

**Edit 1: Remove uncited stat, compress opening**
```diff
- Automated ML research pipelines promise to accelerate discovery, yet 80% of AI agents fabricate results or violate constraints when unconstrained — a validation crisis that stalls progress before implementation even begins.
+ Automated ML research pipelines fail when hypotheses violate feasibility constraints during phase transitions.
```

**Edit 2: Add gap statement to paragraph 2**
```diff
- The problem runs deeper than lack of validation. Existing research workflow systems rely on schema validation [...]
+ Problem: existing workflow systems rely on schema validation to check structured outputs at phase boundaries, but schema validation checks structure only. Gap: semantic constraints (keywords) and compositional rules (cross-field logic) cannot be expressed. Existing research workflow systems rely on schema validation [...]
```

**Edit 3: Hedge contribution #1 novelty**
```diff
- 1. **First application of Design-by-Contract formal methods to research workflow automation.**
+ 1. **First application of Design-by-Contract to semantic constraint validation in research workflows.** [...] applying contract concepts to semantic and compositional constraints (not just task idempotence as in prior workflow research).
```

**Edit 4: Qualify contribution #3 scope**
```diff
- 3. **Empirical validation on constraint-preserving workflows.** We demonstrate 100% downstream failure reduction on a 100-case placeholder hypothesis corpus with four feasibility constraints
+ 3. **Empirical validation on placeholder workflows.** We demonstrate 100% downstream failure reduction on a 100-case placeholder hypothesis corpus with four feasibility constraints on placeholder content with typed interfaces (external validity to substantive research unproven, deferred to Phase 5)
```

**Edit 5: Fix contribution #4 LOC claim**
```diff
- enabling research teams to adopt contract-based validation with minimal implementation cost (25-27 lines of code per hypothesis)
+ enabling research teams to adopt contract-based validation with minimal implementation cost (25-27 lines of code for the contract layer)
```

---

### 04_experiments.md (2 edits)

**Edit 1: Justify schema-only baseline**
```diff
- **Schema-only validation (primary baseline):** Pydantic BaseModel with typed fields, Field constraints (min_length, Literal enums), but no field validators or model validators. This isolates pure schema expressiveness — what can be validated through type checking and structural constraints alone.
+ **Schema-only validation (primary baseline):** [...] This baseline isolates pure structural schema expressiveness — what can be validated through type checking and structural constraints alone. Field validators are excluded by design choice to measure the expressiveness gap, not because they are unavailable in Pydantic. This creates a conservative baseline (including validators would increase baseline performance and reduce measured gaps).
```

**Edit 2: Expand baseline rationale**
```diff
- **Rationale:** We compare against schema-only rather than manual review because automated pipelines require automated validation. [...]
+ **Rationale:** We compare against structural-schema-only rather than manual review because automated pipelines require automated validation. [...] We exclude field validators from the baseline to isolate what pure schema validation (types, structure) can express versus what requires explicit semantic/compositional checking (the research question).
```

---

### 05_results.md (1 edit)

**Edit 1: Add h-e1 test suite note**
```diff
[After Table 1]
+ Note: h-e1 used 15-violation adversarial subset; h-m2 used 25-case suite with different violation distribution.
```

---

### 06_discussion.md (3 edits)

**Edit 1: Add competing explanations for 100% reduction**
```diff
- **Unexpected result: 100% reduction despite 88% detection.** We predicted ≥80% failure reduction [...]. Two explanations: [...]
+ **Unexpected result: 100% reduction despite 88% detection.** We predicted ≥80% failure reduction [...]. The 100% reduction (vs predicted 80%) suggests either: (1) corpus violations matched detectable patterns (the 12% missed in h-m2 adversarial suite were synonym variations not present in corpus), or (2) test set was too simple (embedded violations used exact blacklist keywords rather than realistic paraphrases). We cannot distinguish without larger-scale validation. The 80% recall measured on adversarial test suite with synonym variations does not apply to placeholder corpus violations, which used exact blacklist keywords enabling 100% detection. Real-world deployment requires LLM-based validation to handle synonym gaps.
```

**Edit 2: Strengthen placeholder limitation**
```diff
- **Placeholder content fidelity.** Our validation tested constraint enforcement logic on placeholder hypotheses with minimal substantive content. This approach enables infrastructure testing (like drone SIL testing) but does not prove results generalize to real research with complex semantic dependencies.
+ **Placeholder content fidelity.** Our validation tested constraint enforcement logic on placeholder hypotheses with minimal substantive content (typed interfaces only). External validity to production workflows unproven. Results demonstrate that constraint enforcement logic functions correctly on typed interfaces but do not prove generalization to real research content with complex semantic dependencies. [...] (deferred Phase 5 baseline comparison).
```

**Edit 3: Justify baseline fairness**
```diff
- Schema-only validation represents current practice in workflow systems (Pydantic-based structured output validation).
+ Our schema-only baseline isolates pure structural validation (types, required fields) to measure expressiveness gap. Production systems often include pattern validators (e.g., Great Expectations uses assertion-based validation); our baseline excludes them by design to test whether contracts add value beyond structure alone.
```

---

### 07_conclusion.md (2 edits)

**Edit 1: Soften opening, qualify result**
```diff
- We opened with research automation's validation crisis: 80% of AI agents fabricate results or violate constraints, causing expensive late-stage failures [...]
- [...] The result: 100% downstream failure reduction on a 100-case placeholder hypothesis corpus with four feasibility constraints.
+ We opened with research automation's validation crisis: automated ML pipelines fail late when constraint violations propagate undetected through phase boundaries. [...]
+ [...] The result: 100% downstream failure reduction on a 100-case placeholder hypothesis corpus with four feasibility constraints on placeholder content with typed interfaces (generalization to substantive research unproven, external validity deferred to Phase 5).
```

**Edit 2: Qualify final contribution statement**
```diff
- From constraint violation crisis to zero downstream failures — that is the contribution of contract-based validation.
+ From constraint violation crisis to zero downstream failures on placeholder workflows — that is the contribution of contract-based validation.
```

---

## Round 2 Revisions (Numerical verification fixes)

### 04_experiments.md (1 edit)

**Edit 1: Fix test suite size (30 → 25)**
```diff
- **Adversarial Test Suite (h-m2):** 30 hand-crafted test cases with known ground-truth violations, designed to measure detection rates per layer. Distribution: 10 structural violations (caught by schema), 10 semantic violations (keyword patterns for C1/C2), 10 compositional violations (cross-field logic for C3/C4).
+ **Adversarial Test Suite (h-m2):** 25 hand-crafted test cases with known ground-truth violations, designed to measure detection rates per layer. Distribution: 10 structural violations (schema baseline testing), plus semantic/compositional violations across constraint types (C1 synthetic: 5 cases, C2 human eval: 5 cases, C3 standard dataset: 2 cases, C4 new benchmark: 3 cases).
```

---

## Summary Statistics

**Total files modified:** 6  
**Total edits:** 13  
**Lines changed:** ~85 lines across Abstract, Introduction, Experiments, Results, Discussion, Conclusion

**Issue severity breakdown:**
- FATAL fixed: 3 (2 R1, 1 R2)
- MAJOR fixed: 9 (R1)
- MINOR deferred: 14 (documented in 065_human_review_notes.md)

**Key themes:**
1. **Scope qualification:** Every quantitative claim now includes placeholder scope + external validity caveat
2. **Novelty hedging:** "First application" claims hedged to "semantic constraint validation" (distinguishes from Graflow)
3. **Baseline justification:** Schema-only excludes validators by design (isolate structural expressiveness), not strawman
4. **Competing explanations:** 100% reduction acknowledged as potentially corpus-specific (synonym gaps in adversarial suite vs exact keywords in corpus)
5. **Numerical accuracy:** Test suite size corrected (25 not 30), distribution updated to match validation reports

---

**Next Phase:** Human review of 14 MINOR issues, then final copy-edit pass.
