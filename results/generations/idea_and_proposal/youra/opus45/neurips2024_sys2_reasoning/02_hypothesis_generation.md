# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CompDAG-v1
**Confidence Level:** 0.88

**Main Hypothesis:**
Under conditions of contamination-resistant evaluation in semantic parsing tasks, if compositional tasks are modeled as parameterized DAGs with IRT-calibrated difficulty (varying Composition Depth D, Working Memory Load W, and Interference Level I), then models with genuine compositional generalization will exhibit flat (sublinear) accuracy decay with increasing depth, while pattern-matching models will exhibit exponential decay, because compositional generalization requires recursive application of learned primitives rather than memorization of specific input-output patterns.

**Alternative Hypothesis (H0):**
There is no systematic relationship between DAG depth and accuracy decay patterns that distinguishes compositional generalization from pattern matching; accuracy decay is determined primarily by surface features, task format, or random variation rather than underlying compositional structure.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Composition Depth (D) | Independent | Number of nested DAG operations | 1-10 levels |
| Working Memory Load (W) | Independent | Number of intermediate values to track | 1-5 items |
| Interference Level (I) | Independent | Number of distractor nodes in DAG | 0-10 nodes |
| Model Accuracy | Dependent | Exact match accuracy on semantic parsing | 0-100% |
| Accuracy Decay Rate | Dependent | Slope of accuracy vs. depth curve (linear regression coefficient) | Flat (~0) to steep (< -0.1 per level) |
| IRT Calibration Correlation | Dependent | Pearson r between predicted and observed difficulty | Target: r > 0.8 |
| Grammar Primitives | Controlled | Fixed primitive set from SCAN/COGS extensions | ~50-100 primitives |
| DAG Structure Constraints | Controlled | Maximum branching factor, allowed edge types | Fixed per experiment |
| Random Seed | Controlled | Seed for procedural generation | Fixed for reproducibility |

### 1.3 Causal Mechanism

**Causal Chain (N=2 steps):**

```
[DAG Parameterization (D, W, I)]
        ↓ (Link 1)
[Systematic Difficulty Variation via IRT Calibration]
        ↓ (Link 2)
[Differential Accuracy Decay Patterns]
```

**Link 1: DAG Parameterization → Systematic Difficulty Variation**
- **Mechanism:** IRT theory establishes that item parameters predict difficulty. DAG depth (D) directly maps to the number of recursive operations required; working memory load (W) captures cognitive demands; interference (I) measures distractor resistance.
- **Evidence:** FuncBenchGen (2025) successfully used DAG structure with controllable depth to measure function calling capabilities. GeomVerse (Kazemi et al., 2023) demonstrated that depth-controlled procedural generation reliably reveals model limitations at higher reasoning depths.

**Link 2: Systematic Difficulty Variation → Differential Accuracy Decay Patterns**
- **Mechanism:** Models using true compositional generalization apply learned primitives recursively (O(1) cost per composition step), yielding flat/sublinear accuracy decay. Pattern-matching models must retrieve increasingly rare memorized patterns as depth increases (exponential search space), yielding exponential decay.
- **Evidence:** Dziri et al. (2023) "Faith and Fate" showed transformers reduce compositional tasks to "linearized subgraph matching" - a pattern-matching strategy that degrades with task complexity. This implies behavioral signatures differ between the two strategies.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| D, W, I → Difficulty | IRT Literature (Shao et al., 2024) | Item parameters predict difficulty with high reliability | Strong |
| D, W, I → Difficulty | GeomVerse (Kazemi et al., 2023) | Procedural depth control reveals VLM limitations | Strong |
| Difficulty → Decay | Dziri et al. (2023) | Transformers use linearized subgraph matching, not systematic composition | Strong |
| Difficulty → Decay | FuncBenchGen (2025) | DAG-based evaluation with controllable complexity distinguishes model capabilities | Medium |

**Key Tension:**
- **Tension:** Sainz et al. (2023) argue that benchmark contamination fundamentally undermines evaluation validity, but procedural generation (LiveBench, GeomVerse) assumes fresh instances eliminate contamination. If contamination occurs at the level of compositional primitives rather than complete examples, procedural generation may not fully address the problem.
- **Resolution:** This verification plan tests whether controlling at the primitive level (fixed grammar) while varying compositional structure provides meaningful contamination resistance. The IRT calibration step will reveal if difficulty predictions hold across fresh instances.

### 1.4 Key Assumptions

1. **Compositional generalization = functional composition (DAG traversal)**
   - Supporting evidence: Category theory formalizes compositionality as functorial mappings (Phillips, 2022); FuncBenchGen models tool use as DAG traversal
   - Consequence if violated: DAG structure may not capture all aspects of compositional reasoning (e.g., semantic compositionality may differ from syntactic)

2. **DAG depth is a valid proxy for compositional complexity**
   - Supporting evidence: GeomVerse demonstrates depth correlates with reasoning chain length; cognitive science links working memory to composition limits
   - Consequence if violated: Need alternative complexity metrics; depth alone may be insufficient

3. **Hierarchical IRT handles DAG dependencies adequately**
   - Supporting evidence: Network psychometric models exist for dependent items; Apro & Tajti (2025) show IRT works for programming tasks
   - Consequence if violated: Standard IRT calibration will fail; need specialized psychometric models for graph-structured tasks

4. **Semantic parsing represents compositional reasoning broadly**
   - Supporting evidence: SCAN/COGS established as compositionality benchmarks; semantic parsing requires systematic mapping of syntax to semantics
   - Consequence if violated: Results may not generalize to other compositional domains (math, visual reasoning)

5. **Accuracy decay pattern distinguishes strategies reliably**
   - Supporting evidence: Dziri et al. (2023) show transformers fail systematically at higher depths; pattern-matching has inherent scaling limits
   - Consequence if violated: Need additional behavioral probes beyond decay curves to distinguish strategies

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Semantic parsing tasks (command → logical form)
- Compositional language understanding with clear formal structure
- Evaluation of pre-trained language models (encoder-decoder, decoder-only)
- Laboratory/benchmark settings with controlled generation

**Where Hypothesis Does NOT Apply:**
- Open-domain, real-world reasoning without clear compositional structure
- Tasks where "compositional" is ambiguous or ill-defined
- Domains requiring world knowledge beyond compositional rules
- Training methodology optimization (this is evaluation-focused)

**Known Limitations:**
- Requires domain-specific grammar design for each task family
- Synthetic tasks may not fully capture real-world compositional challenges
- IRT calibration requires pilot study with human or model performance data
- Results are correlational (decay patterns) rather than mechanistic (internal representations)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Depth Decay Diagnostic):**
Models with genuine compositional generalization will exhibit accuracy decay with depth D that is sublinear (slope ≈ 0 or logarithmic), while models relying on pattern matching will exhibit exponential decay (accuracy halving every 2-3 depth levels).

*Measurement*:
- Generate tasks at depth D = 1, 2, 3, 4, 5, 6, 8, 10
- Compute accuracy at each depth level (n ≥ 100 samples per level)
- Fit linear and exponential models to accuracy vs. depth
- Compare model fit (R²) and decay coefficients
- Success: Clear separation between flat/sublinear and exponential decay patterns

*Basis*:
- Dziri et al. (2023) showed transformers fail at multi-step compositional reasoning
- GeomVerse showed VLM performance degrades systematically with problem depth
- FuncBenchGen showed DAG complexity distinguishes model capabilities

*Success Criteria for Phase 2B*:
- Primary: Decay slope difference > 0.05 between model types with p < 0.05
- Falsification: All models show similar decay patterns (slope difference < 0.02)

**Secondary Predictions:**

**P2 (IRT Calibration Validity):**
Predicted task difficulty from hierarchical IRT model (using D, W, I parameters) will correlate with observed difficulty (error rate) with r > 0.8.

*Measurement*:
- Pilot study: Evaluate diverse model ensemble on 500+ generated tasks
- Fit 3-parameter hierarchical IRT model to response data
- Compute correlation between model predictions and held-out difficulty estimates
- Success: r > 0.8, demonstrating DAG parameters capture difficulty systematically

**P3 (Contamination Resistance):**
Models trained on fixed compositional primitives but tested on novel DAG structures (fresh instances) will show consistent decay patterns regardless of when instances were generated.

*Measurement*:
- Generate test sets at T1, T2 (1 month apart) using same grammar but different seeds
- Compare model performance and decay patterns across time points
- Success: No significant difference in decay patterns (p > 0.1)

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure (Decay Pattern):** All tested models show similar decay patterns regardless of architecture or known compositional capabilities, with decay slope difference < 0.02 between models.

2. **Calibration Failure:** IRT calibration correlation r < 0.5, indicating DAG parameters do not systematically predict task difficulty.

3. **Mechanism Failure:** Ablation studies show depth (D) has no significant effect on accuracy (p > 0.1) when controlling for surface features.

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - This hypothesis concerns benchmark creation methodology rather than model performance improvement.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Tasks per depth level: n ≥ 100 (for stable accuracy estimates)
- Depth levels: 8 (D = 1, 2, 3, 4, 5, 6, 8, 10)
- Total tasks per model: n ≥ 800
- Models to evaluate: 5-10 (diverse architectures)
- Pilot study for IRT calibration: 500+ tasks with multiple model responses

**Test Specification:**
- Primary analysis: Linear mixed-effects model with depth as fixed effect, model as random effect
- Decay pattern comparison: Likelihood ratio test comparing linear vs. exponential fits
- IRT calibration: Pearson correlation with bootstrap 95% CI
- Significance level: α = 0.05 (two-tailed for calibration, one-tailed for decay comparison)

**Report Format:**
- Decay curves with 95% confidence bands
- Model comparison table with fit statistics (R², AIC, BIC)
- IRT parameter estimates with standard errors
- Calibration scatter plot with regression line

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Does the proposed DAG-based benchmark generator produce tasks with systematically varying difficulty that correlate with IRT predictions (r > 0.8)?

*Verification type:* Empirical (pilot study with human/model calibration)
*Critical:* MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
Does composition depth (D) causally determine accuracy in a way that differs between compositional and pattern-matching strategies?

*Maps to:* 2 causal links in the mechanism
- H-M1: DAG parameters → Systematic difficulty (IRT calibration validation)
- H-M2: Difficulty variation → Differential decay patterns (decay curve analysis)

*Verification type:* Causal analysis (ablation, controlled comparison)
*Critical:* Determines explanatory power of the framework

**SH3 (Comparison):**
Does CompDAG provide better discrimination between model compositional capabilities than existing benchmarks (SCAN, COGS, static benchmarks)?

*Verification type:* Comparative empirical
*Critical:* Determines practical value over alternatives

**Total sub-hypotheses for Phase 2B:** 2 + 2 = 4 (SH1, H-M1, H-M2, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CompDAG-v1
- [x] Confidence level specified: 0.88
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=2 steps, evidence table provided)
- [x] Causal chain length (N=2) determined and stored
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 provided, with P1 as primary)
- [x] Falsification criteria are defined (3 conditions)
- [x] Baselines are identified for comparison (SCAN, COGS, FuncBenchGen)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Grammar Design:** What specific extensions to SCAN/COGS grammar are needed for CompDAG? Should we use existing grammars or design new ones?

2. **IRT Model Selection:** Which hierarchical IRT variant best handles DAG dependencies? Need to evaluate multidimensional IRT vs. network psychometric models.

3. **Model Selection for Pilot:** Which models should be included in the pilot study for IRT calibration? Need mix of architectures (encoder-decoder, decoder-only) and scales.

4. **Verification Priority:** Should we validate IRT calibration (SH1) first, or run decay pattern analysis (SH2) in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-13*
