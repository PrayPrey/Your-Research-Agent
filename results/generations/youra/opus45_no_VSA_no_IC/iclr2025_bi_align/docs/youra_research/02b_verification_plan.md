# Phase 2B: Verification Plan
## H-AMode-v1: Alignment Mode Hypothesis

Generated: 2026-08-24T03:35:00Z
Archon Project: `2b73ce34-d36a-49f1-8447-69e3511a5eaa`

---

## Main Hypothesis

**ID:** H-AMode-v1

**Statement:** Under the scope of Chatbot Arena pairwise battles, if we classify samples into four alignment modes based on human vote entropy (high/low) crossed with RM ensemble variance (high/low) via median split, then Mode 3 (Misaligned-Confident: high entropy, low variance) will constitute >10% of samples.

**Null Hypothesis:** Mode distribution is uniform (25% each) OR Mode 3 < 5%.

---

## Sub-Hypotheses

### H-E1: Mode 3 Existence (MUST_WORK)

| Field | Value |
|-------|-------|
| Type | EXISTENCE |
| Statement | Mode 3 (high human entropy, low RM variance) constitutes >10% of Chatbot Arena samples |
| Gate | MUST_WORK |
| Prerequisites | None |
| Status | READY |
| Success Criterion | Proportion statistically > 10% (one-sided binomial test, p < 0.05) |
| Falsification | Proportion < 5% or not statistically different from 10% |
| Dataset | Chatbot Arena Battles (lmsys/chatbot_arena_conversations) |
| Sample Size | Full test set or minimum 2000+ battles with vote distributions |

### H-M1: Semantic Similarity Mechanism (SHOULD_WORK)

| Field | Value |
|-------|-------|
| Type | MECHANISM |
| Statement | Mode 3 response pairs have lower semantic similarity than Mode 1 pairs |
| Gate | SHOULD_WORK |
| Prerequisites | H-E1 |
| Status | NOT_STARTED |
| Success Criterion | Cohen's d > 0.3 for similarity difference |
| Falsification | No significant difference or d < 0.1 |
| Model | sentence-transformers/all-MiniLM-L6-v2 |

### H-C1: Prompt Type Scope (SHOULD_WORK)

| Field | Value |
|-------|-------|
| Type | CONDITION |
| Statement | Mode 3 proportion is higher for subjective prompts than objective prompts |
| Gate | SHOULD_WORK |
| Prerequisites | H-E1 |
| Status | NOT_STARTED |
| Success Criterion | Ratio > 1.5 (subjective:objective Mode 3 rate) |
| Falsification | Ratio < 1.0 (opposite direction) |

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK) ─┬─→ H-M1 (SHOULD_WORK)
                  └─→ H-C1 (SHOULD_WORK)
```

- H-E1 must complete first (mode classification required)
- H-M1 and H-C1 can run in parallel after H-E1

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data lacks vote distributions | Medium | High | Use arena-hard subset or sample battles with 3+ votes |
| RM variance not comparable | Low | Medium | Z-score normalization across models |
| Mode 3 < 10% (falsification) | Medium | High | Report as honest negative; check threshold sensitivity |
| Semantic similarity insensitive | Low | Medium | Sensitivity analysis with multiple embedding models |

---

## Timeline

| Phase | Hypothesis | Duration | Parallel |
|-------|------------|----------|----------|
| 2C | H-E1 | 1 day | - |
| 3 | H-E1 | 1 day | - |
| 4 | H-E1 | 2 days | - |
| 2C | H-M1, H-C1 | 1 day | Yes |
| 3 | H-M1, H-C1 | 1 day | Yes |
| 4 | H-M1, H-C1 | 2 days | Yes |
| 5 | Baseline | 2 days | - |

**Total:** ~10 days

---

## Dialectical Analysis

| Thesis | Antithesis | Synthesis |
|--------|------------|-----------|
| Mode 3 reveals RM overconfidence | Could be noise/spam | A1 assumes Arena quality controls; entropy stability test |
| Semantic similarity explains mechanism | RMs may use other features | H-M1 is SHOULD_WORK; mechanism failure doesn't block |
| Subjective prompts drive Mode 3 | Classification is subjective | Use Arena tags or keyword heuristics |

---

## Archon Task Mapping

| Hypothesis | Task ID |
|------------|---------|
| H-E1 | `54aff3dd-f45a-44ba-83d8-5776d551c13d` |
| H-M1 | `0c71339b-6aad-41c9-acd9-754cdb679d75` |
| H-C1 | `70347b7e-115e-47a0-af6a-ee09f2b24224` |
| Phase 2B | `bcf7bcf3-b13d-45d3-bcb3-d3a37537ca87` |

---

## Next Steps

1. Phase 2C: Design experiment specification for H-E1
2. Phase 3: Generate implementation plan for H-E1
3. Phase 4: Execute and validate H-E1
4. Repeat 2C-4 for H-M1 and H-C1 (parallel)
5. Phase 5: Baseline comparison
