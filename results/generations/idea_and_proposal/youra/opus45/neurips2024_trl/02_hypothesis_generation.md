# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SATA-SP-v1
**Confidence Level:** 0.81

**Main Hypothesis:**
Under the condition of table question answering tasks with frozen LLMs, if learned structural prompts derived from TAPAS-style embeddings are prepended to the serialized table input, then the LLM will require fewer in-context examples to achieve comparable accuracy because explicit positional scaffolding reduces the cognitive load on the LLM's reasoning about table structure.

**Alternative Hypothesis (H0):**
Prepending learned structural prompts derived from TAPAS-style embeddings does not significantly reduce the number of in-context examples required for LLMs to achieve comparable accuracy on table QA tasks, and performance improvements (if any) are attributable to increased input length or random variance rather than structural scaffolding.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Structural Prompt Injection | Independent | Presence/absence of learned structural prompts prepended to LLM input; prompt token count | 0 (baseline), 8, 16, 32 tokens |
| Table QA Accuracy | Dependent | Exact match accuracy on WikiTableQuestions benchmark | 60-85% |
| In-Context Example Efficiency | Dependent | Number of in-context examples to achieve 70% accuracy threshold | 0-shot to 8-shot |
| Zero-Shot Transfer Performance | Dependent | Accuracy on unseen table domains (TabFact, FeTaQA) without domain-specific training | 50-75% |
| LLM Base Model | Controlled | Frozen LLM with no parameter updates | GPT-3.5-turbo, Llama-2-7B |
| Table Serialization Format | Controlled | Markdown table format with pipe delimiters | Fixed format |

### 1.3 Causal Mechanism

```
Step 1: TAPAS Structural Encoding
  ↓
  TAPAS-style embeddings capture 2D positional relationships (row/column indices)
  ↓
Step 2: Cross-Modal Projection
  ↓
  Lightweight projection network translates structural embeddings to prompt tokens
  ↓
Step 3: Cognitive Scaffolding
  ↓
  Prepended structural prompts provide explicit positional information to LLM
  ↓
[OUTCOME]: Reduced in-context example requirements + improved zero-shot transfer
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | TaPas (Herzig et al., 2020) | Structural attention with position embeddings improves table QA from 55% to 67.2% on SQA | Strong |
| Step 2 → Step 3 | Vision-Language Adapters (BLIP-2, LLaVA) | Cross-modal projection networks successfully translate visual features to language model space | Medium |
| Step 3 → Outcome | Schema-ICL (Chen et al., 2025) | Explicit schema scaffolding improves LLM reasoning by up to 36.19% on GPQA | Strong |

**Key Tension:**
- **Tension:** Table Meets LLM (2023) shows self-augmentation prompting improves performance by 2-5%, but Schema-ICL (2025) shows schema scaffolding can achieve 36% gains. The magnitude of improvement from structural scaffolding in table domain is uncertain.
- **Resolution:** This verification plan tests whether learned structural prompts (combining both approaches) achieve gains closer to Schema-ICL's 36% or Table Meets LLM's modest 2-5%, specifically measuring in-context efficiency rather than raw accuracy.

### 1.4 Key Assumptions

1. **TAPAS Structural Sufficiency:** TAPAS-style row/column position embeddings capture sufficient structural information for diverse table types
   - Evidence: TAPAS achieves 67.2% on SQA with structural attention
   - Consequence if violated: Need richer structural encoding (e.g., graph-based, hierarchical)

2. **Projection Learnability:** A lightweight projection network (2-3 layers) can learn effective mapping from structural embeddings to prompt tokens
   - Evidence: Vision adapters (Q-Former in BLIP-2) successfully project visual features to language space
   - Consequence if violated: Require more complex adapter architecture or direct fine-tuning

3. **LLM Structural Receptivity:** Frozen LLMs can utilize prepended structural information without architecture modifications
   - Evidence: Prefix tuning and prompt tuning show LLMs respond to learned soft prompts
   - Consequence if violated: Need to modify LLM architecture or use different injection method

4. **Structural Bottleneck Primacy:** Structural understanding is a primary bottleneck in LLM table reasoning
   - Evidence: Table Meets LLM SUC benchmark shows systematic failures on structural tasks
   - Consequence if violated: Other factors (semantic understanding, numerical reasoning) may dominate

### 1.5 Scope & Boundaries

**Applies To:**
- Standard relational tables with clear row/column structure
- Tables with ≤100 rows and ≤20 columns (within LLM context limits)
- Table QA, fact verification, and simple data retrieval tasks
- Frozen LLMs without task-specific fine-tuning

**Does NOT Apply To:**
- Nested/hierarchical tables (JSON-tables, multi-level headers)
- Multi-sheet spreadsheets with cross-sheet references
- Semi-structured documents (forms, receipts, invoices)
- Tasks requiring complex multi-hop reasoning across tables
- Very large tables exceeding LLM context window

**Known Limitations:**
- Requires adapter training on diverse table corpora (estimated: 10k-100k tables)
- Adds inference latency from structural encoding step (~50-100ms)
- Structural prompt tokens consume context window budget
- May not transfer to fundamentally different table structures

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (In-Context Efficiency vs SOTA ~75% baseline):**
Our SATA-SP approach will achieve equivalent accuracy (≥70%) on WikiTableQuestions with 50% fewer in-context examples compared to baseline prompting methods.

*Measurement:*
- Compare number of in-context examples to reach 70% accuracy
- Baseline: Direct prompting requires N examples
- Target: SATA-SP requires ≤N/2 examples with p < 0.05

*Basis:*
WikiTableQuestions SOTA methods achieve 67.6% (Repanda) to 84.3% (Combined approach). Our target is in-context efficiency improvement, not raw accuracy improvement.

*Success Criteria for Phase 2B:*
- Primary: ≥50% reduction in required in-context examples (p < 0.05)
- Falsification: <25% reduction OR accuracy drop >5% with structural prompts

**Secondary Predictions:**

**P2 (Zero-Shot Transfer):**
SATA-SP will achieve ≥60% accuracy on zero-shot transfer to TabFact and FeTaQA benchmarks without domain-specific adapter training, compared to ≤50% for baseline prompting.

**P3 (Structural Complexity Benefit):**
The relative improvement from SATA-SP will be larger for structurally complex tables (>10 columns, >50 rows) compared to simple tables (<5 columns, <20 rows), demonstrating that structural scaffolding specifically addresses structural complexity.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** In-context efficiency improvement < 25% (less than half the target)
2. **Mechanism Failure:** Ablation shows removing structural prompts has no significant effect
3. **Comparative Failure:** Performance worse than baseline prompting on any benchmark
4. **Transfer Failure:** Zero-shot transfer accuracy < 50%

### 1.7 SOTA Baseline (SOTA Comparison Mode)

| Method | Performance | Year | Notes |
|--------|-------------|------|-------|
| Repanda (baseline) | 67.6% | 2024 | Program-based |
| Commented Code (Qwen2.5-7B) | 70.9% | 2026 | Code generation |
| Combined Approach | 84.3% | 2026 | End-to-end + code |
| Chain-of-Table | ~75% | 2024 | Iterative operations |

**Statistics:** SOTA Mean ~75%, Performance Tier: Medium (70-90%), Ceiling Room ~16%

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 per condition
**Statistical Test:** Independent samples t-test, α = 0.05 (Bonferroni corrected for 3 benchmarks)
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does structural prompt injection improve LLM table understanding efficiency?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism (TAPAS encoding → projection → scaffolding) the actual cause of efficiency improvement?"
- Maps to: Causal mechanism (N=3 steps)
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: TAPAS embeddings capture necessary structural information
  - H-M2: Projection network learns effective cross-modal mapping
  - H-M3: LLMs utilize structural prompts for improved reasoning
- Verification type: Ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does SATA-SP provide advantages over existing methods (Chain-of-Table, direct prompting)?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses for Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-SATA-SP-v1)
- [x] Confidence level specified (0.81)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length (N=3) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist with primary marked
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Requirements:** Minimum training corpus size for adapter (estimate: 10k-100k tables)
2. **Adapter Architecture:** Optimal projection depth (2 vs 3 layers) and prompt token count (8/16/32)
3. **LLM Selection:** Priority testing on GPT-3.5-turbo and Llama-2-7B
4. **Evaluation Priority:** Recommend SH1 first as gate for full investigation

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-13*
