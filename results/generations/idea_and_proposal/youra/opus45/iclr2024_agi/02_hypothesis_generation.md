# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-LMSAL-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of multi-step logical reasoning tasks requiring formal verification, if an LLM is fine-tuned using LoRA on reasoning traces with explicit module selection labels (~50K traces), then the LLM will achieve higher accuracy on reasoning benchmarks (FOLIO, ProofWriter, GSM8K) than rule-based dispatch systems (SymbolicAI), because learned module selection adapts to problem characteristics while avoiding the computational complexity barrier of architectural NSI fusion.

**Alternative Hypothesis (H0):**
There is no significant difference in reasoning accuracy between learned module selection (L-MSAL) and rule-based module dispatch (SymbolicAI) on multi-step logical reasoning benchmarks. Any observed differences are attributable to random variation, hyperparameter tuning, or benchmark-specific artifacts rather than the learned selection mechanism itself.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Module Selection Strategy | Independent | Three levels: learned (LoRA fine-tuned on 50K traces), rule-based (SymbolicAI-style keyword matching), random baseline | Categorical: {learned, rule-based, random} |
| Number of Available Modules | Independent | Count of symbolic solvers in module library | 2, 5, or 10 modules (Z3, Prover9, MiniSAT, ASP solvers) |
| Reasoning Accuracy | Dependent | Accuracy (%) = correct_answers / total_questions on benchmark | 50-95% depending on benchmark difficulty |
| Computational Cost | Dependent | Inference time (ms) per problem; GPU memory (GB) during inference | Time: 100-5000ms; Memory: 8-24GB |
| Base LLM | Controlled | Llama-3-8B-Instruct with identical initialization and fixed random seed | Fixed |
| Solver Implementations | Controlled | Fixed versions: Z3 v4.12, Prover9 latest stable | Fixed |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Fine-tuning on module-labeled traces
    ↓ (LoRA adaptation creates module selection capability)
Step 2: Learned module selection during inference
    ↓ (Problem characteristics → optimal solver routing)
Step 3: Solver execution + result integration
    ↓ (External symbolic reasoning → verified output)
Outcome: Higher reasoning accuracy than baselines
```

**Step 1 - Fine-tuning Creates Selection Capability:**
- Mechanism: LoRA (r=16, alpha=32) adapts Llama-3-8B on (problem, module_trace, solution) triplets
- The LLM learns to recognize problem patterns that benefit from specific symbolic solvers
- Training objective: Cross-entropy on module selection + reasoning accuracy

**Step 2 - Learned Selection Routes Problems:**
- Mechanism: During inference, LLM predicts optimal module(s) with confidence scores
- Learned patterns generalize to novel problem distributions better than rule-based matching
- Parallel execution when multiple modules selected

**Step 3 - Solver Execution and Integration:**
- Mechanism: Selected solver(s) execute via tool-calling API; results integrated into natural language
- External solvers provide provable guarantees that neural approximations cannot match
- Batching and caching optimize latency for multi-step problems

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Metagent-P (Zhou 2025) | Planning-verification patterns can be learned; reduces replanning by 34% | Strong |
| Step 2 → Step 3 | SCL (Kim 2025) | R-CCAM architecture with separation achieves zero policy violations, eliminates redundant tool calls | Strong |
| Step 3 → Outcome | Nguyen 2025 | Hybrid LLM-Z3 systems achieve improved accuracy in educational QA with explainability | Medium |

**Key Tension:**
- **Tension:** Šír (2024) argues that general NSI has fundamental computational complexity barriers, but Metagent-P (2025) and SCL (2025) demonstrate practical hybrid systems achieving reliable performance.
- **Resolution:** L-MSAL resolves this by keeping symbolic reasoning EXTERNAL to the neural architecture (interface-based design), rather than attempting architectural fusion. The verification plan tests whether this separation maintains symbolic guarantees while enabling learned orchestration.

### 1.4 Key Assumptions

1. **LLMs can learn effective module selection through supervised fine-tuning**
   - Evidence: LoRA fine-tuning is well-established for task adaptation (Hu et al., 2021); SCL demonstrates modular separation enables reliable execution
   - Consequence if violated: If selection accuracy <70% after fine-tuning, the entire approach fails at foundation level; would need to explore reinforcement learning or larger training sets

2. **External symbolic solvers provide more reliable formal reasoning than neural approximations**
   - Evidence: Šír 2024 shows static tensor graphs are computationally insufficient for general NSI; Z3/Prover9 provide provable guarantees
   - Consequence if violated: If neural-only reasoning matches solver accuracy, the complexity of integration is unjustified; simpler Chain-of-Thought approaches would suffice

3. **Interface overhead is negligible compared to symbolic solver execution time**
   - Evidence: Modern tool-calling APIs add <100ms latency; solver execution typically >500ms for complex problems
   - Consequence if violated: If overhead exceeds 50% of total inference time, latency-sensitive applications become infeasible; would need to explore model distillation or solver optimization

### 1.5 Scope & Boundaries

**Where hypothesis applies:**
- Multi-step logical reasoning tasks (propositional logic, first-order logic)
- Mathematical reasoning requiring symbolic verification (arithmetic, algebra)
- Constraint satisfaction problems expressible in solver-compatible formats
- Benchmarks: FOLIO (first-order logic), ProofWriter (logical deduction), GSM8K (math reasoning)

**Where it does NOT apply:**
- Commonsense reasoning without formal structure (e.g., social reasoning, intuitive physics)
- Creative tasks (writing, ideation) where formal verification is meaningless
- Real-time applications requiring <50ms latency
- Problems without established symbolic solver support (e.g., visual reasoning)

**Known limitations:**
- Requires curated training data with explicit module-problem mappings (~50K traces)
- May not generalize to entirely novel module types not seen during training
- Performance depends on solver coverage for benchmark problem types
- Single A100 GPU requirement limits accessibility for some researchers

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Reasoning Accuracy - Learned vs. Rule-based):**
L-MSAL (learned module selection) will achieve significantly higher reasoning accuracy than SymbolicAI (rule-based dispatch) on held-out test sets.

*Measurement:*
- Accuracy improvement ≥ 5 percentage points (e.g., 78% → 83%) with p < 0.05
- Statistical test: Paired t-test across 3 benchmarks, n ≥ 25 runs per configuration
- Effect size: Cohen's d ≥ 0.5 (medium effect)

*Basis:*
Learned selection adapts to problem characteristics that keyword-matching cannot capture. Prior work (Metagent-P) shows learned patterns reduce errors by 34%.

*Success Criteria for Phase 2B:*
- Primary: Accuracy(L-MSAL) > Accuracy(SymbolicAI) + 5pp with p < 0.05
- Minimum: Accuracy(L-MSAL) > Accuracy(SymbolicAI) with p < 0.10

**Secondary Predictions:**

**P2 (Module Selection Precision):**
L-MSAL will achieve module selection precision ≥ 80% (correct module for problem type) compared to <60% for random baseline.

*Measurement:* Precision = correct_selections / total_selections on labeled validation set

**P3 (Scalability with Module Count):**
Accuracy will improve with more modules (2 → 5 → 10) without proportional increase in computational cost.

*Measurement:* Accuracy vs. module count regression; cost per problem vs. module count

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** Accuracy(L-MSAL) ≤ Accuracy(SymbolicAI) after full training
   - Indicates learned selection provides no advantage over rule-based dispatch

2. **Mechanism Failure:** Module selection precision < 60% (worse than informed random)
   - Indicates fine-tuning did not produce reliable selection capability

3. **Comparative Failure:** Accuracy(L-MSAL) < Accuracy(Pure LLM) on any benchmark
   - Indicates integration overhead outweighs solver benefits

4. **Cost Failure:** Inference time > 10x pure LLM with no accuracy improvement
   - Indicates impractical for real-world deployment

### 1.7 SOTA Baseline (Optional)

*Not applicable - this hypothesis targets novel capability (learned module selection) rather than incremental improvement over existing SOTA performance on specific benchmarks.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Minimum effect size target: Cohen's d = 0.5 (medium)
- Statistical power: 0.8
- Significance level: α = 0.05
- Required runs: n ≥ 25 per condition (learned, rule-based, random)

**Test Specification:**
- Primary test: Paired t-test (same random seeds across conditions)
- Multiple comparison correction: Bonferroni for 3 pairwise comparisons
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

**Reproducibility Requirements:**
- Fixed random seeds for all experiments
- All components open-source (Llama-3, LoRA, Z3)
- Full hyperparameter documentation
- Training and evaluation code released

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does learned module selection (via LoRA fine-tuning on ~50K reasoning traces) produce reliable solver routing (selection precision ≥80%) under multi-step logical reasoning conditions?"
- Maps to: Primary prediction P1, P2
- Verification type: Empirical measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is LoRA fine-tuning on module-labeled reasoning traces the actual cause of improved module selection compared to random initialization?"
- Maps to: Causal mechanism (3 steps → 3 sub-hypotheses)
  - H-M1: Fine-tuning → selection capability
  - H-M2: Selection capability → optimal routing
  - H-M3: Optimal routing → accuracy improvement
- Verification type: Ablation studies, causal analysis
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does L-MSAL outperform SymbolicAI (rule-based dispatch) and pure LLM baseline on FOLIO, ProofWriter, and GSM8K benchmarks?"
- Maps to: Secondary prediction P3
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-LMSAL-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence_for_links table)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2-P3 secondary)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines are identified (SymbolicAI, Pure LLM, Random)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What compute budget is available for fine-tuning (~8 GPU-hours on A100) and evaluation runs (25+ per condition)?

2. **Training Data Generation:** How should module-problem mappings be created for the ~50K training traces? Options:
   - Manual annotation of existing benchmark solutions
   - Automated labeling based on solver success/failure
   - Synthetic generation from problem templates

3. **Evaluation Priority:** Which benchmark should be prioritized first?
   - FOLIO (first-order logic) - most directly tests formal reasoning
   - ProofWriter (logical deduction) - established benchmark
   - GSM8K (math) - largest dataset, most practical relevance

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
