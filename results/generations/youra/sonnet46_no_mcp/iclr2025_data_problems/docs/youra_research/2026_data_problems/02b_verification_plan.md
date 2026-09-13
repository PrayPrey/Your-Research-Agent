---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
hypothesis_id: H-ContamMatrix-v1
research_mode: incremental
created_at: "2026-05-04T00:00:00"
completedAt: "2026-05-04T00:00:00"
---

# Verification Plan: Cross-Corpus Contamination Atlas

**Date:** 2026-05-04
**Hypothesis ID:** H-ContamMatrix-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

### 0.1 BUILD_ON Claims (DO NOT Re-Verify)

| Claim | Evidence |
|-------|----------|
| 13-gram containment is asymmetric and appropriate for test-vs-corpus comparison | WIMBD (Elazar et al., 2023) arXiv:2310.20707 |
| MMLU has 57 sub-tasks covering diverse academic domains | Hendrycks et al. (2020) arXiv:2009.03300 |
| The Pile v1, C4, and RedPajama are publicly available training corpora | Gao 2020, Dodge 2021, TogetherComputer 2023 |
| allenai/wimbd provides open-source 13-gram contamination tooling for The Pile | GitHub: allenai/wimbd |

### 0.2 PROVE_NEW Claims (Experimental Targets)

| Claim | Target Sub-Hypothesis |
|-------|-----------------------|
| No unified cross-corpus × cross-benchmark contamination matrix exists | H-E1 (existence of variance) |
| Contamination rates vary significantly across benchmark sub-tasks and corpora | H-M1, H-M2 (mechanism) |
| 13-gram containment and Jaccard similarity rankings correlate | H-M3 (metric consistency) |

**Scope Reduction: 50%** — 4 of 7 claims are pre-established; Phase 2B targets only the 3 PROVE_NEW claims.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under experimental conditions of pinned benchmark and corpus versions, if 13-gram containment rates are computed between MMLU (57 sub-tasks), HellaSwag, and BIG-Bench Hard test sets (question+choices concatenation) and The Pile v1, C4 en.noclean, and RedPajama-v1 training corpora, then contamination rates will vary significantly across sub-tasks (Kruskal-Wallis p < 0.05) and across corpora (Kruskal-Wallis p < 0.05), and sub-task contamination rankings will correlate positively and significantly between 13-gram containment and Jaccard similarity (Spearman ρ, p < 0.05), because different corpora have structurally different source compositions leading to corpus-specific contamination signatures in specialized benchmark sub-tasks.

### 1.2 Alternative Hypothesis (H0)

13-gram contamination rates do not differ significantly across benchmark sub-tasks or across training corpora (Kruskal-Wallis p >= 0.05), and contamination rankings by 13-gram containment and Jaccard similarity are uncorrelated (Spearman p >= 0.05), indicating that contamination is uniformly distributed regardless of sub-task domain or corpus source composition.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU + HellaSwag + BIG-Bench Hard × The Pile v1 + C4 en.noclean + RedPajama-v1 (standard) | Primary benchmarks and corpora studied in contamination literature; enables direct comparison with WIMBD and GPT-4 TR results |
| **Model** | N/A — no model inference required | CPU-only n-gram analysis; no model weights needed; enables broad reproducibility |

**Dataset Details:**
- Source: Hugging Face datasets (all public)
- Path: cais/mmlu, Rowan/hellaswag, lukaemon/bbh, EleutherAI/pile, allenai/c4, togethercomputer/RedPajama-Data-1T

**Model Details:**
- Type: text-analysis pipeline
- Source: allenai/wimbd + custom Python (tokenize → shingle → MinHash)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| WIMBD 13-gram containment (Pile × MMLU) | ~1-10% for some MMLU sub-tasks | The Pile v1 × MMLU |
| GPT-4 TR Jaccard contamination analysis | Near-zero for most benchmarks | Undisclosed training data × select benchmarks |
| Dodge et al. (2021) C4 contamination documentation | Partial overlap documentation | C4 × various NLP datasets |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Benchmark test set versions on Hugging Face match FM pretraining versions | Most major FMs trained before HF versions finalized | Slight under/over-estimation; rankings robust to minor version differences |
| A2 | 13-gram containment is a valid proxy for "has this test instance been seen during training" | WIMBD validates this proxy empirically | Contamination rates are proxies, not exact measurements — acknowledged limitation |
| A3 | Full corpus text is accessible for streaming (Hugging Face datasets API) | Pile/C4/RedPajama all available via HF; confirmed in Phase 1 | If streaming fails: fallback to pre-downloaded sample |
| A4 | MinHash LSH approximation is sufficiently accurate for rank-level analysis | MinHash LSH well-characterized; rank ordering sufficient for Spearman | Exact counts have small error; rank-based conclusions robust |
| A5 | Question+choices concatenation is appropriate unit for MC benchmark contamination | Used by WIMBD in benchmark analysis | Sensitivity analysis (question-only) will quantify impact |

### 1.6 Research Gap & Novelty

**Gap:** No unified cross-corpus × cross-benchmark contamination rate matrix exists. WIMBD covers The Pile only; GPT-4 TR uses Jaccard on select benchmarks with undisclosed corpus; no systematic 3-corpus analysis with dual-metric comparison.

**Novel Contribution:** First unified 3-corpus × 3-benchmark contamination rate matrix using both 13-gram containment and Jaccard similarity simultaneously, revealing corpus-specific contamination signatures driven by structural differences in corpus source composition.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Existence of Significant Cross-Sub-Task Contamination Variance**

**Statement**: Under pinned benchmark and corpus versions, if 13-gram containment rates are computed across all 57 MMLU sub-tasks + HellaSwag + BIG-Bench Hard against The Pile v1, then contamination rates will vary significantly across sub-tasks (Kruskal-Wallis p < 0.05) because benchmark sub-tasks span different academic and commonsense domains that are unevenly represented in training corpora.

**Rationale**: This is the foundational existence check — confirming that contamination is not uniform across sub-tasks is prerequisite to all mechanism hypotheses. WIMBD's own findings of sub-task variation within The Pile support this; H-E1 extends confirmation to all three corpora.

**Variables** (from Phase 2A):
- Independent: Benchmark sub-task identity (59 levels: 57 MMLU + HellaSwag + BBH)
- Dependent: 13-gram containment rate per sub-task [0,1]
- Controlled: n-gram size=13, corpus=The Pile v1 (primary), pinned versions, question+choices format

**Verification Protocol**:
1. Load all 59 benchmark sub-tasks from HF (cais/mmlu, Rowan/hellaswag, lukaemon/bbh); format as question+choices concatenation
2. Build MinHash LSH index for The Pile v1 via allenai/wimbd streaming
3. Query index for each test instance; aggregate 13-gram containment rate per sub-task
4. Run Kruskal-Wallis H-test on contamination rates across 59 sub-tasks
5. Verify at least one sub-task pair shows contamination rate difference > 5 percentage points

**Success Criteria** (PoC: Direction-based):
- Primary: Kruskal-Wallis p < 0.05 for sub-task variance
- Secondary: At least one sub-task pair shows > 5 pp contamination rate difference

**Failure Response**:
- IF fails: PIVOT — reassess whether 13-gram granularity is appropriate; try shorter n-gram (n=8); re-examine text preprocessing

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (sh1_existence), Prediction P1

---

**H-M1: Corpus Source Composition Drives Differential Contamination Signatures**

**Statement**: Under pinned versions, if 13-gram containment rates are computed for the full 59×3 matrix (59 benchmark sub-tasks × 3 corpora), then contamination rates will vary significantly across the three corpora (Kruskal-Wallis p < 0.05) because The Pile, C4, and RedPajama have structurally different source compositions (academic vs. web-filtered vs. curated-multi-source) that produce systematically different n-gram overlap with domain-specific benchmark content.

**Rationale**: This is the core mechanism hypothesis — it tests whether corpus-level structural differences (documented in corpus papers) translate into measurable contamination signature differences. Success establishes the corpus-as-variable framework central to the paper.

**Variables** (from Phase 2A):
- Independent: Corpus identity (3 levels: Pile/C4/RedPajama)
- Dependent: Mean 13-gram containment rate per corpus (averaged over all sub-tasks)
- Controlled: Same 59 sub-tasks, pinned versions, identical MinHash parameters

**Verification Protocol**:
1. Extend H-E1 pipeline to build MinHash LSH indices for C4 en.noclean and RedPajama-v1 via streaming
2. Query all three indices for each of the 59 benchmark sub-tasks; construct 59×3 contamination matrix
3. Run Kruskal-Wallis H-test on per-corpus mean contamination rates across all sub-tasks
4. Verify at least one corpus pair shows mean contamination rate difference > 2 percentage points
5. Sanity-check Pile × MMLU rates against WIMBD published values (consistency check)

**Success Criteria** (PoC: Direction-based):
- Primary: Kruskal-Wallis p < 0.05 for corpus variance
- Secondary: At least one corpus pair shows mean contamination > 2 pp difference; Pile × MMLU rates consistent with WIMBD

**Failure Response**:
- IF fails: EXPLORE — corpus composition effect may be weaker than sub-task effect; document corpus variance as non-significant finding; proceed to H-M2 and H-M3 as independent tests

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 1–2, Prediction P2

---

**H-M2: Domain-Specific Sub-Tasks Show Corpus-Type-Predictable Contamination Patterns**

**Statement**: Under the full 59×3 contamination matrix, if contamination rates are stratified by benchmark domain type (MMLU academic/professional sub-tasks vs. commonsense HellaSwag/BIG-Bench Hard), then domain-specific sub-tasks will show higher contamination in academically-weighted corpora (The Pile) and commonsense sub-tasks will show higher contamination in web-heavy corpora (C4), because corpus source composition predicts which sub-task domains appear most frequently in each corpus.

**Rationale**: This hypothesis tests the mechanistic specificity of H-M1 — not just that corpora differ overall, but that the pattern of which sub-tasks are contaminated is predictable from corpus source composition. This is the "corpus-specific contamination signature" framing central to the paper's novelty.

**Variables** (from Phase 2A):
- Independent: Corpus identity × Sub-task domain type (academic vs. commonsense)
- Dependent: 13-gram contamination rate per (corpus, domain-type) stratum
- Controlled: Same matrix from H-M1, same preprocessing

**Verification Protocol**:
1. Classify 59 sub-tasks into domain types: MMLU academic/professional (medicine, law, STEM) vs. commonsense (HellaSwag, BIG-Bench Hard abstract reasoning)
2. Compute mean contamination rate per (corpus, domain-type) cell from H-M1 matrix
3. Test whether Pile × academic > Pile × commonsense AND C4 × commonsense > C4 × academic (directional prediction)
4. Compute interaction effect (corpus × domain-type) to assess pattern significance
5. Identify top-5 most contaminated sub-tasks per corpus and verify domain alignment with corpus source

**Success Criteria** (PoC: Direction-based):
- Primary: Directional pattern holds for at least 2 of 3 corpora (academic vs. commonsense contamination differential in expected direction)
- Secondary: At least 1 sub-task with near-100% contamination identified per corpus

**Failure Response**:
- IF fails: Document as "contamination signatures not domain-predictable"; document null result; proceed to H-M3 as independent test; narrow scope claim in paper

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 2, Open Questions

---

**H-M3: 13-gram Containment and Jaccard Similarity Produce Consistent Sub-Task Rankings**

**Statement**: Under the full 59×3 matrix, if both 13-gram containment and Jaccard similarity are computed for the same (sub-task, corpus) pairs, then sub-task contamination rankings by the two metrics will correlate positively and significantly (Spearman ρ > 0 with p < 0.05 for at least 2 of 3 corpora) because both metrics derive from n-gram set intersection and the normalization difference (test-size vs. union-size) does not change relative rankings for small test sets against large corpora.

**Rationale**: This hypothesis validates the methodological contribution of using dual metrics — confirming that 13-gram containment and Jaccard similarity are consistent produces the first apples-to-apples metric comparison on the same data, resolving the ambiguity in prior work about which metric to use.

**Variables** (from Phase 2A):
- Independent: Metric type (13-gram containment vs. Jaccard similarity)
- Dependent: Spearman ρ between metric rankings across sub-tasks
- Controlled: Same (sub-task, corpus) pairs, same text preprocessing

**Verification Protocol**:
1. For each (sub-task, corpus) cell already computed in H-M1: compute Jaccard similarity |test∩corpus|/|test∪corpus| using same MinHash approximation
2. For each corpus, rank all 59 sub-tasks by 13-gram containment rate and separately by Jaccard similarity
3. Compute Spearman ρ between the two ranking vectors per corpus (3 Spearman tests total)
4. Apply Bonferroni correction (α=0.05/3=0.0167) for multiple tests
5. Report ρ value, 95% confidence interval, and p-value for each corpus; report overall correlation across all 177 cells

**Success Criteria** (PoC: Direction-based):
- Primary: Spearman ρ > 0 with p < 0.05 for at least 2 of 3 corpora
- Secondary: Overall Spearman ρ across all 177 cells is significantly positive

**Failure Response**:
- IF fails: EXPLORE — investigate whether metric disagreement is corpus-specific; report which corpora show agreement vs. disagreement; reframe as "metric sensitivity analysis" if systematic disagreement found

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3, Prediction P3, Prof. Vera's analysis

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Kruskal-Wallis p < 0.05 for sub-task variance | STOP — reassess hypothesis; try alternative n-gram size |
| H-M1 | MUST_WORK | Kruskal-Wallis p < 0.05 for corpus variance | EXPLORE — document null corpus effect; continue to H-M2, H-M3 independently |
| H-M2 | SHOULD_WORK | Domain-predictable pattern holds for ≥2 of 3 corpora | DOCUMENT limitation — narrow scope claim; does not block H-M3 |
| H-M3 | SHOULD_WORK | Spearman ρ > 0, p < 0.05 for ≥2 of 3 corpora | EXPLORE — report metric sensitivity; reframe as sensitivity analysis |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Benchmark Version Mismatch**

**Source Assumption:** A1 — Benchmark test set versions on HF match FM pretraining versions.

**Description:** Minor version differences between HF dataset versions and the exact versions used during FM pretraining could cause slight contamination rate under/over-estimation.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (all — contamination rates are the primary measurement)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pin all benchmark versions explicitly (cais/mmlu v1.0.0, Rowan/hellaswag standard split, lukaemon/bbh) in code and in paper
2. **Detection:** Compare our Pile × MMLU rates against WIMBD published values as sanity check; significant deviation (>5 pp) signals version mismatch
3. **Response:** Document version pinning as a study-level limitation; rank-level conclusions (Spearman ρ) are robust to small absolute rate shifts

**Early Warning Indicators:**
- Our Pile × MMLU rates deviate >5 pp from WIMBD's published rates for matching sub-tasks
- Unexpected near-100% contamination rates for many sub-tasks simultaneously

---

**Risk R2: 13-gram Proxy Invalidity**

**Source Assumption:** A2 — 13-gram containment is a valid proxy for training-time exposure.

**Description:** If 13-gram matching systematically misclassifies contamination (too many false positives due to common phrases, or false negatives due to paraphrasing), the contamination matrix may not reflect true training-time exposure.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (all — the entire measurement framework depends on this proxy)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use n=13 (WIMBD standard, empirically validated); explicitly acknowledge proxy limitation as per all n-gram contamination work
2. **Detection:** Spot-check: manually verify 5-10 high-contamination (sub-task, corpus) cells by searching corpus text directly for test questions
3. **Response:** Frame results as "n-gram overlap rates" not "true contamination rates"; the comparative findings (which sub-tasks/corpora show higher rates) remain valid even if absolute values are approximate

**Early Warning Indicators:**
- Spot-check reveals high-contamination cells with no actual test text in corpus
- All three corpora show identical rates for all sub-tasks (suggests metric artifact)

---

**Risk R3: Corpus Streaming Failure**

**Source Assumption:** A3 — Full corpus text accessible via HF streaming API.

**Description:** C4 en.noclean (~300 GB) and RedPajama-v1 (~1.2 TB) are large; streaming may be slow, rate-limited, or fail partway through index construction. The Pile v1 is handled by WIMBD natively.

**Affected Hypotheses:** H-M1, H-M2, H-M3 (H-E1 can use Pile only via WIMBD; C4/RedPajama required for H-M1+)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Test streaming connectivity before full run; allocate dedicated compute with stable network; use HF datasets streaming=True with retry logic
2. **Detection:** Monitor index construction progress; checkpoint MinHash indices after each corpus shard
3. **Response (PIVOT):** If full streaming fails, use pre-sampled subset (10% random sample via HF streaming); document as limitation; rank-level findings should hold for large enough sample; report sample size prominently

**Early Warning Indicators:**
- HF streaming rate <100 MB/s sustained
- Index construction stalls or raises connection errors after first shard
- Memory errors during MinHash LSH construction

---

**Risk R4: MinHash LSH Approximation Error**

**Source Assumption:** A4 — MinHash LSH is sufficiently accurate for rank-level analysis.

**Description:** MinHash LSH introduces ~1-5% approximation error in exact 13-gram containment counts. For absolute rates this is minor; for rank-level Spearman analysis this should be negligible, but extreme approximation errors could affect borderline cases.

**Affected Hypotheses:** H-M3 most directly (Spearman ρ relies on rank stability); H-E1/H-M1/H-M2 less sensitive (Kruskal-Wallis on relative rates)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Use standard MinHash parameters (128+ hash functions); validate against WIMBD's exact implementation where possible
2. **Detection:** For 5 randomly selected (sub-task, corpus) cells, compare MinHash estimate against exact count; verify error <5%
3. **Response:** If approximation error exceeds 5%, increase hash function count (256 or 512); document approximation bounds; Spearman analysis on ranks is inherently robust to small absolute errors

**Early Warning Indicators:**
- Spot validation shows MinHash estimates deviating >10% from exact counts
- Spearman ρ values show high variance across bootstrap resamples

---

**Risk R5: Text Format Assumption**

**Source Assumption:** A5 — Question+choices concatenation is appropriate for MC benchmark contamination measurement.

**Description:** If test contamination primarily comes from question stems alone (not choices), the question+choices format may over-estimate contamination by including choice-specific n-grams rarely seen in training.

**Affected Hypotheses:** All (format choice affects all 177 matrix cells)

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Plan sensitivity analysis (question-only vs. question+choices) from the start; include both formats in implementation
2. **Detection:** Run sensitivity analysis on all 57 MMLU sub-tasks (as specified by Prof. Rex); compare rankings between formats
3. **Response:** If rankings differ significantly (Spearman ρ < 0.5 between formats), report both results; primary results use question+choices (WIMBD standard); sensitivity analysis as appendix

**Early Warning Indicators:**
- Question+choices contamination rates are consistently 2x higher than question-only rates across all sub-tasks

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Mitigation |
|------|--------|---------------------|----------|------------|
| R1: Version mismatch | A1 | H-E1, H-M1, H-M2, H-M3 | Medium | Pin versions; sanity-check vs. WIMBD |
| R2: Proxy invalidity | A2 | H-E1, H-M1, H-M2, H-M3 | High | Spot-check; frame as n-gram overlap |
| R3: Streaming failure | A3 | H-M1, H-M2, H-M3 | High | Checkpoint indices; fallback to sample |
| R4: MinHash error | A4 | H-M3 (primary), H-E1/M1/M2 | Medium | Validate against exact; increase hash count |
| R5: Format assumption | A5 | All | Low | Sensitivity analysis question-only vs. +choices |

**Risk Summary:** 0 Critical, 2 High, 2 Medium, 1 Low. Both high risks (R2, R3) have concrete mitigation strategies and fallback paths. No risk identified as blocking the core research question.

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1: Existence of Sub-Task Contamination Variance
    (No dependencies — can begin immediately)
         │
         ▼  [Gate 1: MUST_WORK — p < 0.05 required]
[Level 1 - Core Mechanism: Corpus Signatures]
    H-M1: Corpus Source Composition → Differential Contamination
    Prerequisites: H-E1
         │
         ▼  [Gate 2: MUST_WORK — corpus variance p < 0.05]
[Level 2 - Mechanism: Domain Specificity]
    H-M2: Domain-Predictable Corpus-Specific Contamination Patterns
    Prerequisites: H-M1
         │
         ▼  [Gate 2b: SHOULD_WORK — directional pattern ≥2/3 corpora]
[Level 3 - Mechanism: Metric Consistency]
    H-M3: 13-gram Containment / Jaccard Similarity Ranking Consistency
    Prerequisites: H-M2
         │
         ▼  [Gate 3: SHOULD_WORK — Spearman ρ > 0, p < 0.05 for ≥2/3]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 | All Sequential | No Parallelization
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | If Fail |
|-------|-----------|---------------|-----------|---------|
| 0 | H-E1 | None | MUST_WORK | STOP — reassess entire approach |
| 1 | H-M1 | H-E1 | MUST_WORK | EXPLORE — document null corpus effect |
| 2 | H-M2 | H-M1 | SHOULD_WORK | DOCUMENT — narrow scope claim |
| 3 | H-M3 | H-M2 | SHOULD_WORK | EXPLORE — reframe as sensitivity analysis |

### 5.3 Verification Phases

**Phase 1 — Foundation** (H-E1 must pass before proceeding)
→ Gate 1: If H-E1 fails → STOP, reassess entire hypothesis

**Phase 2 — Core Mechanisms** (H-M1 is critical; H-M2/H-M3 are supporting)
→ Gate 2: H-M1 must pass. H-M2/H-M3 failures narrow scope but do not invalidate core claim.

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses / 6 Weeks
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2     │ W3-4     │ W5       │ W6
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1            │ █████████│          │          │
  [Gate 1]        │         ◆│          │          │
──────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms
  H-M1            │          │ █████████│          │
  [Gate 2]        │          │         ◆│          │
  H-M2            │          │          │ █████████│
  [Gate 2b]       │          │          │         ◆│
  H-M3            │          │          │          │ █████████
  [Gate 3]        │          │          │          │         ◆
═══════════════════════════════════════════════════════════════════
Legend: █ = Active work │ ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Duration Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) = 6 weeks

Slack Available: 0 weeks (fully sequential)

Notes:
  H-M1 gets 2 weeks (3 corpus indices to build — streaming time for
  C4/RedPajama requires extra allocation per Prof. Rex's concern)
  H-M2, H-M3 each get 1 week (reuse matrix from H-M1; mainly analysis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
  Existence: 1 (H-E1)
  Mechanism: 3 (H-M1, H-M2, H-M3)
  Condition: 0 (not needed — scope boundaries are exclusions)

Verification Phases: 2 (Foundation + Mechanisms)
Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain

Compute Requirements:
  H-E1: CPU only, The Pile via allenai/wimbd (~4-8 hrs)
  H-M1: CPU only, C4 + RedPajama streaming index build (~12-24 hrs each)
  H-M2/H-M3: CPU only, analysis on pre-built matrix (<1 hr)
  No GPU required for any hypothesis.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

- **Step 1:** Execute H-E1 — build Pile MinHash index, query 59 sub-tasks, run Kruskal-Wallis (Week 1-2)
- **Step 2:** Evaluate Gate 1 — if p < 0.05, proceed; else STOP and reassess
- **Step 3:** Execute H-M1 — build C4 and RedPajama indices, construct 59×3 matrix, run corpus-level Kruskal-Wallis (Week 3-4)
- **Step 4:** Evaluate Gate 2 — if p < 0.05, proceed; else EXPLORE and document
- **Step 5:** Execute H-M2 — stratify matrix by domain type, test directional predictions (Week 5)
- **Step 6:** Execute H-M3 — compute Jaccard for all 177 cells, run Spearman ρ analysis (Week 6)
- **Final:** All gates evaluated; verification complete; proceed to Phase 2C experiment design

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Different training corpora (The Pile v1, C4 en.noclean, RedPajama-v1) produce corpus-specific contamination signatures in NLP benchmark sub-tasks, measurable as statistically significant variance in 13-gram containment rates across sub-tasks and across corpora, with consistent rankings across dual metrics (13-gram containment and Jaccard similarity).

**Supporting Evidence:**
1. Corpus documentation confirms structurally different source compositions: The Pile (academic+diverse web), C4 (quality-filtered CommonCrawl), RedPajama (curated multi-source) — compositional differences are established facts, not hypotheses
2. WIMBD (Elazar et al., 2023) found significant sub-task contamination variation within The Pile alone — our claim extends this cross-corpus
3. Both 13-gram containment and Jaccard derive from n-gram set intersection; metric asymmetry in normalization does not change relative rankings for small test sets vs. large corpora (Prof. Vera's formal analysis)

**Strengths:**
- Grounded in established corpus documentation (BUILD_ON facts)
- Extends validated methodology (WIMBD) to new scope (3 corpora)
- Three independently falsifiable predictions with pre-specified statistical tests
- CPU-only pipeline ensures broad reproducibility

**Expected Outcomes:**
- Primary: Kruskal-Wallis p < 0.05 for sub-task variance (H-E1, H-M1)
- Secondary: Domain-predictable corpus contamination pattern (H-M2)
- Tertiary: Spearman ρ > 0 for ≥2/3 corpora (H-M3)

### 6.2 Antithesis

**Null Hypothesis (H0):** 13-gram contamination rates do not differ significantly across benchmark sub-tasks or across training corpora (Kruskal-Wallis p >= 0.05), and contamination rankings by 13-gram containment and Jaccard similarity are uncorrelated (Spearman p >= 0.05). Contamination is uniformly distributed regardless of sub-task domain or corpus source composition.

**Counter-Arguments:**
1. **Uniform contamination argument:** If training corpora are sufficiently large and diverse, any benchmark sub-task will appear at similar low rates regardless of domain or corpus — the law of large numbers may wash out structural differences
2. **Metric noise argument:** MinHash LSH approximation error + the small absolute size of test sets relative to trillion-token corpora may produce noisy rate estimates where variance is statistical artifact, not signal
3. **Scope limitation argument:** The three selected corpora may be more similar than their documentation suggests — C4 and RedPajama both derive from CommonCrawl, which may dominate their contamination profiles and mask structural differences

**Potential Failure Points:**
- R2 (proxy invalidity): If 13-gram matching captures only coincidental phrase overlap, variance reflects linguistic patterns not true contamination
- R3 (streaming failure): If C4/RedPajama indices are built on partial data, corpus-level variance may be noise artifact from sampling
- Corpus-level effect is weaker than sub-task effect (key_tension from Phase 2A): sub-task variance (P1) may be significant but corpus variance (P2) may not be, partially supporting H0

**Conditions Under Which H0 Would Be Supported:**
- Kruskal-Wallis p >= 0.05 for sub-task variance (H-E1 fails — strongest H0 support)
- All three corpus mean contamination rates within 1 percentage point of each other (P2 falsification)
- Spearman ρ <= 0 or non-significant for ≥2 corpora (P3 falsification)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ContamMatrix-v1 presents a well-grounded testable claim that corpus structural differences produce measurable contamination signatures. However, the null hypothesis raises valid concerns about the magnitude of corpus-level effects versus sub-task effects — the Phase 2A key_tension correctly identifies this as the primary uncertainty.

**Resolution Path:**

The verification plan resolves this dialectic through:
1. **Foundation first (H-E1):** Confirms sub-task variance before testing corpus-level claims — if H-E1 fails, H0 is supported and the project stops with a meaningful null result
2. **Sequential gate evaluation:** H-M1 directly tests the corpus-level claim; failure narrows the thesis to "sub-task contamination varies but is not corpus-specific"
3. **Independent metric test (H-M3):** Tests methodological claim independently of corpus signature claim — even partial antithesis support on H-M2 does not invalidate H-M3

**Nuanced Outcome Possibilities:**
1. **Full Support (all 4 pass):** Complete thesis validated — corpus-specific contamination signatures confirmed with dual-metric consistency → full paper contribution
2. **Partial Support — sub-task not corpus (H-E1 pass, H-M1 fail):** Sub-task variance confirmed but corpus effect not detected → refined thesis: "benchmark sub-tasks show contamination variance; corpus composition effect is not the primary driver" → still a publishable finding with narrowed claim
3. **Metric Agreement Only (H-E1+H-M1 pass, H-M3 pass):** Contamination signatures confirmed, metric consistency confirmed, domain prediction not confirmed → methodologically valid contribution without domain-specificity claim
4. **No Support (H-E1 fail):** H0 supported — contamination is effectively uniform at 13-gram granularity → important null result for the community; route to Phase 0 for hypothesis revision

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence of variance | Sub-task contamination is non-uniform | Large corpus + uniform language = uniform rates | H-E1 Kruskal-Wallis test (non-parametric) |
| Corpus-level signatures | Source composition drives differential overlap | C4/RedPajama both CommonCrawl-derived — may be similar | H-M1 cross-corpus comparison; explicit corpus documentation |
| Domain specificity | Academic corpora contaminate academic sub-tasks more | Domain labeling is coarse; overlap may not follow domain lines | H-M2 directional test across 3 corpus × domain-type strata |
| Metric consistency | Both metrics capture same contamination signal | Normalization difference may create systematic disagreement | H-M3 Spearman ρ with per-corpus and overall analysis |
| Reproducibility | Open-source tools + pinned versions → replicable | MinHash approximation introduces non-determinism | Sensitivity analysis + exact spot-check validation |

**Overall Robustness Score:** High — three independently falsifiable predictions, non-parametric statistical tests, pre-specified thresholds, sensitivity analysis planned, CPU-only reproducible pipeline.

**Confidence in Verification Plan:** 0.80 (matches Phase 2A confidence)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-ContamMatrix-v1 — Corpus-specific contamination signatures in NLP benchmarks, measurable via cross-corpus × cross-benchmark 13-gram contamination matrix
- ID: H-ContamMatrix-v1 | Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 50% scope reduction from BUILD_ON facts)
- Sub-Hypotheses: 4 total — H-E1 (existence), H-M1/H-M2/H-M3 (mechanism chain)
- Phases: 2 phases over 6 weeks
- Critical Gates: 4 decision points (Gate 1: MUST_WORK; Gates 2/2b/3: MUST_WORK + 2×SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: Corpus streaming time for C4/RedPajama (R3); 13-gram proxy as approximation (R2)
- Both mitigated: Streaming checkpointing + fallback sampling; proxy framing + spot validation

**Immediate Action:** Begin Phase 2C experiment design for H-E1; execute H-E1 first (The Pile via WIMBD, CPU-only, ~4-8 hrs compute)

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses defined across 2 verification phases
- H0 explicitly addressed: uniform contamination thesis directly falsified by P1/P2/P3
- 5 risks identified with concrete mitigation strategies and fallback paths
- 6-week execution plan with gate-based decision points
- Sensitivity analysis planned from the start (question-only vs. question+choices; all 57 MMLU sub-tasks)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Does measurable and significantly varying 13-gram contamination exist across 59 benchmark sub-tasks?
- Gate 1: MUST PASS — Kruskal-Wallis p < 0.05

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Do contamination rates vary significantly across The Pile, C4, RedPajama? (W3-4)
- H-M2: Is the corpus-contamination pattern domain-predictable? (W5)
- H-M3: Do 13-gram containment and Jaccard produce consistent sub-task rankings? (W6)
- Gate 2 (H-M1): MUST_WORK; Gates 2b/3 (H-M2/H-M3): SHOULD_WORK

**Critical Decision Points:**

1. **Gate 1 (H-E1 — Foundation):** H-E1 Kruskal-Wallis p < 0.05
   - FAIL → STOP — reassess whether 13-gram granularity is appropriate; explore alternative metrics
   - PASS → Proceed to Phase 2 mechanisms

2. **Gate 2 (H-M1 — Core Mechanism):** Corpus variance p < 0.05
   - CRITICAL FAIL → EXPLORE — document null corpus effect; narrow thesis to sub-task variance only; H-M2/H-M3 may still proceed independently
   - PASS → Proceed to H-M2

3. **Gate 2b (H-M2 — Domain Specificity):** Directional pattern for ≥2/3 corpora
   - FAIL → DOCUMENT limitation — narrow domain-specificity claim; does not block H-M3

4. **Gate 3 (H-M3 — Metric Consistency):** Spearman ρ > 0 for ≥2/3 corpora
   - FAIL → EXPLORE — reframe as metric sensitivity analysis; report disagreement pattern

**Open Questions:**
- Will C4 and RedPajama show higher or lower contamination than The Pile for domain-specific MMLU sub-tasks? (Phase 2A open question)
- Does the Spearman correlation between 13-gram containment and Jaccard vary by benchmark type (MC vs. completion)? (Phase 2A open question)
- Are there specific MMLU sub-tasks with near-100% contamination in any corpus? (Phase 2A open question)
- How much does corpus streaming time for C4 (~300 GB) and RedPajama (~1.2 TB) affect practical feasibility?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 2C experiment design for H-E1 (highest priority — foundational gate)
   - Set up HF streaming connectivity test before full run; validate WIMBD installation
   - Plan corpus streaming schedule: build one index at a time, checkpoint per shard

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path (2 + 2 + 1 + 1)
   - Reserve buffer: +1 week for C4/RedPajama streaming delays (Prof. Rex's concern)
   - H-M2/H-M3 reuse H-M1 matrix: marginal additional compute

3. **Failure Management:**
   - Document all gate results (pass AND fail) with raw statistics
   - For partial failures: execute EXPLORE strategy, narrow claims, proceed
   - For H-E1 failure: full STOP + route to Phase 0 brainstorm

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `03_refinement.yaml` (H-ContamMatrix-v1, schema v10.0.0)
- Discussion: 7 exchanges, 6 agents (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex)
- Convergence: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 2 (LLM-native fallback — no MCP servers available in this execution)
- Tools used: Inline scientific method reasoning (H-E1 verification + H-M integrated chain)
- Note: No ClearThought/Archon/Exa available; all reasoning performed inline with equivalent quality

**Appendix C: Hypothesis Count Decision**
- Phase 2A causal_chain_count = 3 → 3 mechanism hypotheses (H-M1, H-M2, H-M3)
- Condition hypotheses (H-C): NOT included — scope boundaries in Section 1.5 are exclusion criteria (closed corpora, semantic similarity), not testable boundary conditions
- Total: 1 (H-E1) + 3 (H-M) = 4 sub-hypotheses (within range 2-6 per workflow config)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-05-04*


