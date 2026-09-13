# Validated Hypothesis Synthesis

**Generated:** 2026-04-15
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

Phase 4.5 synthesis refines the original gradient-geometric data scheduling hypothesis based on Phase 4 proof-of-concept validation. The original hypothesis proposed that diversity-ranked domain ordering (high-to-low diversity) during foundation model pretraining improves final performance through path-dependent gradient covariance geometry. Phase 4 PoC validation confirms the approach is **implementable and testable**, with all core components functioning correctly. However, **performance improvement claims and causal mechanism remain unverified**, as full-scale training was deferred to Phase 5 per standard pipeline progression.

**Key Refinements:**
- Original claim of "improves performance significantly" → Refined to "hypothesis pending full-scale validation"
- Mechanism explanation weakened from definitive to hypothesized pending empirical evidence
- All 5 predictions (P1-P5) marked INCONCLUSIVE due to PoC-only execution
- Scope explicitly bounded to feasibility demonstration, not performance confirmation

**Next Steps:** Phase 5 full baseline comparison will test performance claims (≥2.0% at 1B, ≥0.5% at 7B) with statistical rigor (n=5 seeds, p<0.05). If Phase 5 confirms improvements, subsequent mechanism hypotheses (h-m1 through h-m4) will verify gradient geometry explanation.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | Diversity-ranked scheduling improves performance through path-dependent gradient geometry |
| **Refined Core Statement** | Diversity-ranked scheduling is implementable; performance claims pending Phase 5 validation |
| **Predictions Supported** | 0 / 5 (all INCONCLUSIVE - PoC only) |
| **Overall Pass Rate** | 100% (PoC validation) |
| **Hypotheses Validated** | 1 / 1 (h-e1 PoC PASS) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | Diversity-ranked ≥2.0% improvement at 1B (p<0.05) | h-e1 | Composite benchmark | 0.2558 (smoke) | INCONCLUSIVE | LOW | PoC smoke test only (10 steps). Full training pending Phase 5. |
| **P2** | ≥0.5% improvement at 7B (p<0.05) | h-e1 | Composite benchmark | Not tested | INCONCLUSIVE | N/A | Only 1B smoke test executed. 7B validation pending Phase 5. |
| **P3** | PR@25% ≥15% higher, CKA ≥10% higher vs reversed | h-e1 | PR, CKA metrics | Not measured | INCONCLUSIVE | N/A | Geometry analysis not executed in smoke test. |
| **P4** | Forgetting ≤50%, Fisher overlap ≥10% higher | None | Δ accuracy, Fisher | Not tested | INCONCLUSIVE | N/A | Continual learning experiment (h-m4) pending. |
| **P5** | Diversity-PR correlation ρ≥0.7 across 6-8 domains | None | Spearman ρ | Not tested | INCONCLUSIVE | N/A | Cross-domain analysis (h-m1) pending. |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Early high-diversity data shapes gradient covariance geometry | ρ(diversity, PR) < 0.5 | Not measured | UNVERIFIED |
| 2 | Path-dependent optimization crystallizes representational subspaces | CKA persistence ≤ reversed | Not measured | UNVERIFIED |
| 3 | Later specialization operates within established broad subspace | Cumulative-matched shows identical effects | Not tested | UNVERIFIED |
| 4 | Broader geometry enables robust downstream adaptation | Forgetting reduction without Fisher overlap | Not tested | UNVERIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured by corpus statistics: vocabulary entropy, syntactic complexity, semantic spread), then final model performance, continual learning robustness, and out-of-distribution generalization improve significantly, because early high-diversity data establishes broader gradient covariance geometry through path-dependent optimization that persists throughout training.

### 3.2 Refined Core Statement (Phase 4.5)

> Under foundation model pretraining with mixed-domain corpora, diversity-ranked domain scheduling (high-to-low diversity ordering) is implementable and testable as an alternative to static mixture baselines. Proof-of-concept validation confirms the curriculum mechanism executes correctly with proper domain weight transitions using Gaussian scheduling (width=0.3, minimum weight 5%). The hypothesis that this ordering improves final model performance (≥2.0% at 1B scale, ≥0.5% at 7B scale) through path-dependent gradient geometry remains to be validated through full-scale experiments. Current evidence establishes feasibility only; performance claims and mechanistic explanations require Phase 5 baseline comparison with statistical validation (n=5 seeds, p<0.05).

**Key Changes:**
- Performance improvement claim: "improve significantly" → "remains to be validated"
- Mechanism explanation: "because [definitive]" → "hypothesis that [pending verification]"
- Scope: Added explicit qualification limiting claims to feasibility demonstration
- Evidence standard: Added statistical requirements (n=5, p<0.05) for validation

### 3.3 Causal Mechanism — Verified Chain

```
Original Chain:  Step 1 (gradient covariance) → Step 2 (persistence) → Step 3 (specialization) → Step 4 (robustness)
Verified Chain:  Step 1 [UNVERIFIED] → Step 2 [UNVERIFIED] → Step 3 [UNVERIFIED] → Step 4 [UNVERIFIED]
Status: All mechanism steps require full-scale multi-checkpoint experiments for verification (Phase 5 + h-m1/m2/m3/m4)
```

**Removed/Modified Steps:**
- No steps removed; all remain as hypotheses pending empirical validation
- All steps changed from "because X happens" to "hypothesis that X happens"

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| "Improves performance by ≥2.0% at 1B" | WEAKEN | Only PoC validated, not full training | h-e1: PoC PASS but performance untested |
| "Improves performance by ≥0.5% at 7B" | WEAKEN | No 7B experiments yet | h-e1: Only 1B smoke test executed |
| "Through path-dependent gradient geometry" | WEAKEN | Mechanism not measured | All PR/CKA metrics UNVERIFIED |
| "Establishes broader gradient covariance" | MODIFY | Change to "hypothesized to establish" | No gradient covariance measurements |
| "Enables robust continual learning" | WEAKEN | No continual learning experiments | h-m4 pending |
| "Predictive diversity law (ρ≥0.7)" | WEAKEN | Correlation not tested | h-m1 pending |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Path dependence primacy | Assumed | UNVERIFIED | No early-late comparison yet | Temporal ordering effects may not exist |
| A2: Diversity-covariance coupling | Assumed | UNVERIFIED | PR correlation not measured | Cannot predict schedules from corpus stats |
| A3: Geometric persistence | Assumed | UNVERIFIED | CKA not measured | Path dependence claim weakens |
| A4: Subspace orthogonality benefits | Assumed | UNVERIFIED | Fisher overlap not measured | Geometric stability narrative unconfirmed |
| A5: Scaling persistence | Assumed | UNVERIFIED | Only 1B smoke tested | Effects may vanish at larger scales |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Phase 4 PoC validation confirms the **implementation feasibility** of diversity-ranked curriculum scheduling:

**Confirmed Implementation Components:**
1. **Diversity Computation**: Successfully computed diversity scores for 6 Pile domains using vocabulary entropy, syntactic complexity, and semantic spread metrics (Pile-CC: 0.92, StackExchange: 0.88, Wikipedia: 0.75, ArXiv: 0.58, Github: 0.42, PubMed: 0.35)
2. **Curriculum Scheduler**: Gaussian-weighted domain transitions correctly implemented (width=0.3, minimum weight 5%)
3. **Experimental Conditions**: All 4 conditions operational (static, diversity-ranked, reversed, shuffled)
4. **Model Architecture**: GPT-2 style transformer (760M parameters, 1B scale) trains successfully with curriculum data loader
5. **Evaluation Framework**: lm-evaluation-harness integration functional (MMLU, Big-Bench, domain-specific benchmarks)
6. **Data Pipeline**: Real Pile dataset loading via Hugging Face (mock data initially used, corrected per SDD validation)

**HOWEVER, the causal mechanism remains hypothetical.** The proposed explanation — that gradient covariance geometry drives performance improvements — requires:
- Full-scale training to completion (100K steps at 1B, 150K steps at 7B)
- Multi-checkpoint gradient covariance measurements (PR at 10%, 25%, 50%, 75%, 100%)
- Layer-wise representational similarity tracking (CKA between checkpoints)
- Statistical comparison across experimental conditions (n=5 seeds, paired t-tests)
- Direct measurement of Fisher overlap for continual learning analysis

**Current Status**: The METHOD works (code executes correctly); whether the HYPOTHESIS works (performance improves via gradient geometry) is pending Phase 5 validation.

### 4.2 Unexpected Findings Analysis

**No unexpected findings yet** — smoke test was too brief (10 steps) to reveal meaningful patterns. Full-scale Phase 5 experiments may uncover:
- Non-linear improvement curves across training (expected but not yet observed)
- Domain-specific effects (some domains may benefit more from temporal ordering)
- Scale-dependent phenomena (effects may differ between 1B and 7B)

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Diversity-ranked domain scheduling | DoReMi (Xie et al., 2023) - Domain reweighting | EXTENDS | Static reweighting → temporal dynamics |
| Curriculum learning for language models | Bengio et al., 2009 - Curriculum learning | BUILDS_ON | Task difficulty → domain diversity |
| Gradient covariance rank measurement | Stringer et al., 2019 - Participation Ratio | BUILDS_ON | Neuroscience method → LM training |
| Path-dependent SGD optimization | Established optimization theory | BUILDS_ON | Non-convex basin selection |
| Multi-domain pretraining | GPT-3, PaLM, Llama | EXTENDS | Static mixtures → ordered schedules |

### 4.4 Theoretical Contributions

**Pending Phase 5 validation, the proposed contributions are:**

1. **Methodological Contribution**: First systematic framework for diversity-ranked domain scheduling with predictive corpus statistics
   - Novel: Temporal composition as first-class design principle (vs static mixing)
   - Testable: Predictive diversity law enables a priori schedule optimization
   - Practical: Avoids expensive hyperparameter search for domain ratios

2. **Theoretical Contribution**: Connection between corpus diversity and gradient geometry in foundation model training
   - Proposed mechanism: Diversity → gradient covariance rank → representational subspace persistence
   - Falsifiable: Specific predictions (PR correlation ρ≥0.7, CKA persistence ≥10%)
   - Novel: Links data properties to optimization dynamics via measurable geometry

3. **Empirical Contribution** (if Phase 5 confirms): Performance improvement through temporal data composition
   - Significance: ≥2.0% improvement competitive with static mixture baselines
   - Scope: 1B to 7B scale transformer language models
   - Practical: Applicable to any multi-domain training corpus

**Note**: All contributions are contingent on Phase 5 full-scale validation confirming (1) performance improvements meet success criteria, and (2) mechanism hypotheses (h-m1 through h-m4) verify gradient geometry explanation.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Diversity-ranked scheduling existence | MUST_WORK | PASS | 100% (22/22 tests) | Curriculum mechanism is implementable; full validation pending |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 1 (h-e1 only) |
| **Fully Validated** | 0 (PoC only) |
| **PoC Validated** | 1 (h-e1) |
| **Failed** | 0 |
| **Total Tasks Completed** | 16 / 16 (includes mock data fix) |
| **SDD Compliance Rate** | 100% (15/15 implementation tasks) |
| **Test Pass Rate** | 100% (22/22 unit tests) |
| **Smoke Test Composite Score** | 0.2558 (10-step training, not indicative of final performance) |

### 5.3 Optimal Hyperparameters

```yaml
# Phase 4 PoC Configuration (LIGHT tier)
model:
  scale_1b:
    layers: 24
    hidden_dim: 1536
    attention_heads: 16
    context_length: 2048
    parameters: 760300032
  scale_7b:
    layers: 32
    hidden_dim: 4096
    attention_heads: 32
    context_length: 2048

training:
  optimizer: AdamW
  learning_rate_1b: 3e-4
  learning_rate_7b: 1.5e-4
  warmup_steps: 2000
  gradient_clip: 1.0
  batch_size_1b: 512
  batch_size_7b: 1024
  total_steps_1b: 100000
  total_steps_7b: 150000

curriculum:
  scheduling_function: Gaussian
  gaussian_width: 0.3
  minimum_weight: 0.05
  domains:
    pile_cc: {diversity: 0.92, rank: 1}
    stackexchange: {diversity: 0.88, rank: 2}
    wikipedia: {diversity: 0.75, rank: 3}
    arxiv: {diversity: 0.58, rank: 4}
    github: {diversity: 0.42, rank: 5}
    pubmed: {diversity: 0.35, rank: 6}

experimental_conditions:
  - static: {sampling: uniform, weight: 0.1667}
  - diversity_ranked: {scheduling: high_to_low, transition: gaussian}
  - reversed: {scheduling: low_to_high, transition: gaussian}
  - shuffled: {scheduling: random_order, transition: gaussian}

evaluation:
  benchmarks: [MMLU, BigBench, HellaSwag, HumanEval, ScienceQA]
  checkpoints: [0.1, 0.25, 0.5, 0.75, 1.0]
  shots: 5
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| CurriculumDataLoader | h-e1 | h-e1/code/data/curriculum_loader.py | Yes |
| GPT2Model (1B/7B configs) | h-e1 | h-e1/code/models/gpt2_model.py | Yes |
| Diversity score computation | h-e1 | h-e1/code/config.py | Yes |
| Multi-condition training loop | h-e1 | h-e1/code/train.py | Yes |
| Benchmark evaluation harness | h-e1 | h-e1/code/evaluate.py | Yes |
| Experiment orchestration | h-e1 | h-e1/code/run_experiment.py | Yes |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Full training 100K steps | Performance ≥2.0% improvement | Smoke test 10 steps only | SCOPE_CHANGE | PoC validation - full training deferred to Phase 5 |
| **h-e1** | Statistical testing (n=5 seeds) | p<0.05 significance | Single run (seed=42) | SCOPE_CHANGE | PoC mode - statistical validation deferred |
| **h-e1** | Participation Ratio at checkpoints | PR@25% measured | Not measured | IMPLEMENTATION_GAP | Geometry analysis not executed in smoke test |
| **h-e1** | CKA similarity (25%→100%) | CKA measured | Not measured | IMPLEMENTATION_GAP | Multi-checkpoint analysis not executed |
| **h-e1** | 4 conditions × 2 scales × 5 seeds = 40 runs | All 40 runs completed | 1 run completed (static, 1B, seed 42) | SCOPE_CHANGE | PoC executes single run for feasibility check |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

**Interpretation**: All deviations are SCOPE_CHANGE or IMPLEMENTATION_GAP (technical), not HYPOTHESIS_ISSUE. This means the hypothesis itself remains viable; deviations reflect Phase 4 PoC scope (feasibility check) rather than fundamental flaws.

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| N/A | h-e1 smoke test | No figures generated in PoC | Phase 5 will generate required visualizations |

**Note**: Phase 4 PoC did not generate publication-quality figures. Phase 5 will produce:
- Performance comparison bar chart (4 conditions × 2 scales with error bars)
- Domain sampling schedule line plot
- Training curves (validation perplexity vs steps)
- Participation Ratio evolution over checkpoints
- CKA similarity heatmap

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Phase 4 PoC Validation Only — Performance Claims Unverified

- **What:** Current evidence limited to proof-of-concept smoke test (10 training steps, single run with seed=42). Performance improvement predictions (P1: ≥2.0% at 1B, P2: ≥0.5% at 7B) remain untested.
- **Why This Matters:** Cannot yet claim the method "works" in terms of improving model performance. Only established that the method is "implementable."
- **Root Cause:** Phase 4 is designed for implementation feasibility validation per YouRA pipeline structure. Full baseline comparison with statistical validation (n=5 seeds, p<0.05) is Phase 5 responsibility.
- **Impact on Claims:** All performance improvement claims are **hypotheses pending Phase 5**, not validated findings. Refined core statement explicitly qualifies claims as "pending validation."
- **Why Acceptable:** This is standard pipeline progression — Phase 4 confirms "the code runs correctly," Phase 5 confirms "the hypothesis is correct." Separating feasibility from validation improves rigor (avoids premature conclusions from underpowered experiments).

#### L2: Causal Mechanism Unverified — Gradient Geometry Explanation Hypothetical

- **What:** All 4 causal mechanism steps (gradient covariance shaping → persistence → specialization → robustness) are UNVERIFIED. No PR, CKA, or Fisher overlap measurements taken.
- **Why This Matters:** Even if Phase 5 finds performance improvements, the **explanation** for why diversity-ranked scheduling works remains speculative without direct gradient geometry evidence.
- **Root Cause:** Gradient geometry measurements require multi-checkpoint analysis across full training runs (compute/store gradients at 10%, 25%, 50%, 75%, 100% checkpoints for all conditions). This is computationally expensive and not required for PoC validation.
- **Impact on Claims:** Cannot yet claim "path-dependent gradient geometry" as the causal mechanism. Mechanistic explanation remains a hypothesis (testable via h-m1 through h-m4).
- **Why Acceptable:** (1) Performance improvement (if found in Phase 5) is valuable even without mechanistic explanation. (2) Mechanism verification is explicitly scoped to subsequent hypotheses (h-m1: diversity-PR correlation, h-m2: CKA persistence, h-m3: late-training preservation, h-m4: continual learning robustness). (3) Falsifiable predictions enable post-hoc mechanism testing.

#### L3: Single Hypothesis Executed — Mechanism Hypotheses Pending

- **What:** Only h-e1 (EXISTENCE) validated; mechanism hypotheses (h-m1 through h-m4) not yet executed.
- **Why This Matters:** Cannot confirm diversity-PR correlation (h-m1), geometric persistence (h-m2/h-m3), or continual learning benefits (h-m4). Predictive diversity law and detailed mechanism understanding pending.
- **Root Cause:** Dependency graph requires h-e1 PASS before proceeding to mechanism hypotheses. This is a MUST_WORK gate — if existence claim fails, mechanism investigation is premature.
- **Impact on Claims:** Cannot claim "predictive diversity law enables a priori schedule optimization" until h-m1 confirms ρ(diversity, PR) ≥ 0.7. Cannot claim "broader geometry persists" until h-m2 confirms CKA persistence.
- **Why Acceptable:** Sequential validation follows principled hypothesis decomposition. Testing mechanism before confirming existence would be methodologically backwards. If Phase 5 confirms h-e1 performance improvement, h-m1 through h-m4 become high-priority next experiments.

#### L4: Mock Data Fix Required — Initial Implementation Used Synthetic Data

- **What:** Phase 4 initial implementation used mock/synthetic data (torch.randint for domain data, random uniform for evaluation scores). Validator detected violation; coder corrected by implementing real Pile dataset loading via load_pile_domains() and lm-evaluation-harness integration.
- **Why This Matters:** Smoke test results (composite score 0.2558) are from minimal real training (10 steps), not from full-scale experiments. These metrics are for pipeline validation only, not publishable results.
- **Root Cause:** Phase 4 coder initially used placeholder data for rapid PoC development. SDD validation protocol correctly caught and required correction before PoC approval.
- **Impact on Claims:** Smoke test metrics do NOT represent hypothesis performance. They confirm "evaluation framework executes correctly," not "diversity-ranked scheduling improves scores."
- **Why Acceptable:** The fix ensures Phase 5 will use real data and real evaluation. Smoke test serves its intended purpose (integration check). SDD protocol worked as designed (caught mock data, enforced correction).

#### L5: Computational Constraints — Full Experiment Matrix Deferred

- **What:** Planned experiment matrix is 4 conditions × 2 scales × 5 seeds = 40 runs. Phase 4 executed 1 run (static, 1B, seed 42). Estimated compute: ~45K GPU-hours for full matrix.
- **Why This Matters:** Statistical significance (p<0.05) requires n=5 seeds. Cannot detect effect sizes reliably with single run.
- **Root Cause:** PoC validation prioritizes feasibility check over statistical power. Running full 40-run matrix during Phase 4 would conflate implementation debugging with hypothesis testing.
- **Impact on Claims:** No statistical inference possible from current results. Effect size estimates would be unreliable.
- **Why Acceptable:** Phase 4 is explicitly scoped for single-run smoke test. Phase 5 is explicitly scoped for full statistical validation. This separation prevents wasted compute on potentially broken implementations.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Training scale | 1B (smoke tested) | 7B, 13B+ scales | Only 1B PoC executed; 7B pending Phase 5 |
| Training duration | Minimal (10 steps) | Full training (100K+ steps) | Smoke test ≠ converged model |
| Dataset type | The Pile (6 domains) | Other multi-domain corpora | Implementation tied to Pile domain structure |
| Domain count | 6 domains | Fewer/more domains | Curriculum scheduler assumes ≥4 domains for smooth transitions |
| Architecture | GPT-2 style decoder | Encoder, encoder-decoder, other architectures | Only transformer decoder tested |
| Diversity metrics | Vocabulary entropy + syntactic complexity + semantic spread | Alternative diversity measures | Specific metric combination not validated against alternatives |
| Curriculum smoothness | Gaussian (width=0.3) | Other transition functions (linear, step, cosine) | Single smoothness parameter tested |
| Optimizer | AdamW | Other optimizers (SGD, Adagrad, LAMB) | Momentum dynamics may differ |

### 6.3 Assumption Violation Impact

**All 5 key assumptions remain UNVERIFIED:**

- **A1 (Path dependence primacy):** If early-late gradient contributions are symmetric, temporal ordering effects may not exist. **Impact**: Core hypothesis would fail. **Mitigation**: Shuffled control condition in Phase 5 tests this directly.

- **A2 (Diversity-covariance coupling):** If ρ(diversity, PR) < 0.5, corpus statistics cannot predict optimal schedules. **Impact**: Predictive diversity law collapses to post-hoc explanation. **Mitigation**: h-m1 cross-domain analysis will measure correlation.

- **A3 (Geometric persistence):** If CKA similarity between early and final ≤ reversed schedules, path dependence claim weakens. **Impact**: Mechanism explanation requires revision (effect exists but not via persistence). **Mitigation**: h-m2 multi-checkpoint CKA measurements.

- **A4 (Subspace orthogonality benefits):** If forgetting reduction occurs without Fisher overlap changes, geometric stability narrative is falsified. **Impact**: Need alternative mechanism (e.g., implicit regularization). **Mitigation**: h-m4 continual learning experiments with coupled requirement.

- **A5 (Scaling persistence):** If effects vanish entirely at 7B scale, contribution narrows to small-model regularization only. **Impact**: Practical relevance limited to <1B models. **Mitigation**: Phase 5 includes 7B validation with n=5 power analysis.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

**No alternative explanations yet** — smoke test was too brief to generate competing hypotheses. Phase 5 may reveal unexpected patterns requiring alternative mechanistic explanations (e.g., optimizer momentum accumulation, implicit data augmentation effects, batch composition artifacts).

**Planned competing explanation tests:**
1. **Cumulative-matched reversed control**: Tests whether improvement comes from domain exposure distribution vs temporal ordering
2. **Shuffled schedule control**: Tests whether monotonic curriculum structure matters vs early-domain weighting alone

### 7.2 From Unverified Assumptions

1. **A2 Validation: Diversity-PR Correlation (h-m1)**
   - **Current Status:** UNVERIFIED — Phase 1 cross-domain analysis not executed
   - **Proposed Test:** Run 6-8 single-domain early-phase experiments (10% training each), measure PR@10% for each domain, compute Spearman ρ(diversity rank, PR rank)
   - **Success Criterion:** ρ ≥ 0.7, statistically significant
   - **If Violated (ρ < 0.5):** Predictive diversity law collapses; would need empirical hyperparameter tuning rather than corpus-statistics-based prediction
   - **Priority:** HIGH — foundational to predictive framework claim

2. **A3 Validation: Geometric Persistence (h-m2)**
   - **Current Status:** UNVERIFIED — CKA measurements not taken
   - **Proposed Test:** Compute layer-wise CKA similarity between checkpoints (25%→100%) for diversity-ranked vs reversed conditions
   - **Success Criterion:** CKA persistence ≥10% higher for diversity-ranked across ≥70% of layers
   - **If Violated:** Path dependence claim weakens; early geometry may not persist through later training
   - **Priority:** HIGH — tests core hypothesis about optimization dynamics

3. **A4 Validation: Subspace Orthogonality Benefits (h-m4)**
   - **Current Status:** UNVERIFIED — no continual learning experiments
   - **Proposed Test:** Inject fixed-budget legal domain after main training, measure catastrophic forgetting (Δ accuracy on original benchmarks) and Fisher overlap
   - **Success Criterion:** Forgetting ≤50% of reversed AND Fisher overlap ≥10% higher (coupled requirement)
   - **If Violated:** Geometric stability narrative falsified; forgetting reduction may occur via different mechanism
   - **Priority:** MEDIUM — extends hypothesis to continual learning setting

4. **A5 Validation: Scaling Persistence (Phase 5 at 7B)**
   - **Current Status:** UNVERIFIED — only 1B smoke test
   - **Proposed Test:** Full Phase 5 validation at 7B scale (n=5 seeds, statistical testing)
   - **Success Criterion:** ≥0.5% absolute improvement, statistically significant, power ≥70%
   - **If Violated:** Effects vanish at scale; contribution limited to small models
   - **Priority:** HIGH — critical for practical relevance

### 7.3 From Scope Extension Opportunities

1. **Extension to 13B+ Scale**
   - **Current Scope:** 1B (smoke tested), 7B (planned for Phase 5)
   - **Extension:** Test at 13B or larger scales
   - **Feasibility Evidence:** Scaling laws suggest curriculum effects diminish but don't necessarily vanish
   - **Required Resources:** ~30 days training per 13B run, 32+ A100 GPUs
   - **Expected Challenge:** Computational cost limits statistical power (may only afford n=3 seeds)
   - **Priority:** MEDIUM — interesting for scaling law analysis but not critical for core claim

2. **Extension to Alternative Diversity Metrics**
   - **Current Scope:** Fixed combination of vocabulary entropy, syntactic complexity, semantic spread
   - **Extension:** Test individual metrics separately (ablation study), evaluate metric importance
   - **Feasibility:** Diversity computation code is modular; can substitute metrics easily
   - **Purpose:** Determine if all three components are necessary or if simpler metrics suffice
   - **Priority:** MEDIUM — refines understanding but doesn't change core claim

3. **Extension to Non-Pile Multi-Domain Corpora**
   - **Current Scope:** The Pile (6 specific domains: Pile-CC, StackExchange, Wikipedia, ArXiv, Github, PubMed)
   - **Extension:** Test on RedPajama, other multi-domain corpora with different domain characteristics
   - **Challenge:** Requires recomputation of diversity scores and domain boundary definitions
   - **Purpose:** Tests generalization beyond Pile-specific domain taxonomy
   - **Priority:** MEDIUM — strengthens generalization claim

4. **Extension to Alternative Curriculum Transition Functions**
   - **Current Scope:** Gaussian transitions (width=0.3)
   - **Extension:** Test linear, step function, cosine, or learned transition schedules
   - **Feasibility:** Scheduler is modular; easy to implement alternative functions
   - **Purpose:** Determine sensitivity to transition smoothness
   - **Priority:** LOW — optimization of existing approach rather than fundamental question

5. **Extension to Different Optimizer Families**
   - **Current Scope:** AdamW only
   - **Extension:** Test with SGD, Adagrad, LAMB to assess optimizer dependence
   - **Rationale:** Momentum accumulation dynamics may differ across optimizers
   - **Purpose:** Determine if results are optimizer-specific or general property
   - **Priority:** LOW — interesting for mechanistic understanding but not critical

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Hook Strategy:** Puzzle + Practical Failure

**Suggested Hook:**
> "Foundation model pretraining uses static domain mixing ratios (e.g., 60% web text, 20% code, 20% books) determined through expensive hyperparameter sweeps. But optimization is path-dependent—early gradient updates shape the representational geometry for all subsequent learning. Does the TEMPORAL ORDER in which we present domains matter as much as their proportions?"

**Why This Hook Works:**
1. **Immediate practical relevance**: Every foundation model researcher faces domain mixing decisions
2. **Tension**: Static mixing (current practice) vs temporal dynamics (overlooked dimension)
3. **Theoretical grounding**: Path dependence is established (not controversial); temporal ordering is unexplored
4. **Natural question**: Sets up the research without overclaiming

**Alternative Hook (if Phase 5 confirms strong results):**
> "Reordering training domains from high to low diversity improves GPT-style model performance by 2.0% absolute—competitive with static mixture optimization—without hyperparameter search. The key insight: gradient covariance geometry crystallizes early, making the first 25% of training disproportionately influential."

### 8.2 Key Insight (Experiment-Verified)

**Current Status (Phase 4 PoC):**
> Diversity-ranked domain scheduling is implementable and testable as a systematic alternative to static mixture hyperparameter search, with smooth curriculum transitions enabling controlled domain-ordering experiments.

**Evidence:** h-e1 PoC validation (22/22 tests pass, curriculum mechanism executes correctly)

**If Phase 5 Confirms Performance Improvement, Update to:**
> Temporal domain ordering enables performance improvements competitive with static mixture optimization, suggesting that gradient geometry formation during early training has persistent effects—making "when we see data" as important as "how much data we see."

**Evidence (hypothetical, pending Phase 5):** h-e1 full validation (≥2.0% improvement at 1B, ≥0.5% at 7B, p<0.05)

### 8.3 Strongest Claims (Paper-Ready)

**Current Status (Phase 4 PoC) — Feasibility Claims Only:**

1. **"Diversity-ranked curriculum scheduling is implementable for multi-domain foundation model pretraining with smooth Gaussian transitions."**
   - Evidence: h-e1 PoC (22/22 tests, curriculum loader functional)
   - Confidence: HIGH
   - Suggested Section: Methods

2. **"Corpus diversity can be quantified using vocabulary entropy, syntactic complexity, and semantic spread to rank training domains."**
   - Evidence: Diversity scores computed for 6 Pile domains with clear ranking
   - Confidence: MEDIUM (metrics not validated against alternatives)
   - Suggested Section: Methods

3. **"The approach enables controlled experiments comparing temporal domain orderings (diversity-ranked, reversed, shuffled) while holding total per-domain exposure constant."**
   - Evidence: All 4 experimental conditions implemented correctly
   - Confidence: HIGH
   - Suggested Section: Experimental Design

**If Phase 5 Confirms, Add Performance Claims:**

4. **"Diversity-ranked scheduling improves multi-domain benchmark performance by ≥2.0% absolute at 1B scale compared to best static mixture baseline (p<0.05)."** [PENDING PHASE 5]
   - Evidence: Full experiment matrix (n=5 seeds, statistical testing)
   - Confidence: TBD based on Phase 5 results
   - Suggested Section: Results

5. **"The improvement persists at 7B scale (≥0.5% absolute), demonstrating scaling robustness."** [PENDING PHASE 5]
   - Evidence: 7B validation (n=5 seeds, power analysis)
   - Confidence: TBD based on Phase 5 results
   - Suggested Section: Results

**If h-m1 through h-m4 Confirm, Add Mechanism Claims:**

6. **"Corpus diversity correlates with early gradient covariance rank (ρ≥0.7), enabling predictive schedule optimization from corpus statistics."** [PENDING h-m1]

7. **"Early-established gradient geometry persists through training (CKA ≥10% higher), confirming path-dependent optimization dynamics."** [PENDING h-m2]

### 8.4 Honest Limitations (Must Include in Paper)

1. **"Results are limited to The Pile corpus (6 domains); generalization to other multi-domain corpora requires validation."**
   - Why Acceptable: The Pile is widely used; provides sufficient proof of concept
   - Suggested Framing: "We validate on The Pile to enable replication; extension to other corpora (RedPajama, custom mixtures) is natural future work."

2. **"Causal mechanism (gradient geometry explanation) is hypothesized but not fully verified in the current work."** [IF MECHANISM HYPOTHESES NOT COMPLETED]
   - Why Acceptable: Performance improvement (if found) is valuable even without mechanistic understanding; falsifiable predictions enable post-hoc testing
   - Suggested Framing: "We provide a falsifiable mechanistic hypothesis with specific predictions (PR correlation, CKA persistence). Full verification requires additional gradient geometry experiments."

3. **"Diversity metric combination (vocabulary + syntactic + semantic) not validated against alternative formulations."**
   - Why Acceptable: Chosen metrics are theoretically motivated and computationally tractable
   - Suggested Framing: "Our diversity formulation captures lexical, syntactic, and semantic variation. Alternative metrics (e.g., perplexity-based, compression-based) may yield different rankings and are worth exploring."

4. **"Curriculum transition function (Gaussian, width=0.3) not optimized; other transition schedules may perform better."**
   - Why Acceptable: Demonstrates the approach; optimal transition is a hyperparameter
   - Suggested Framing: "We use smooth Gaussian transitions for interpretability. Learned or adaptive schedules could further improve results."

### 8.5 Evidence Highlights (Most Persuasive)

**Current Status (Phase 4 PoC):**

1. **Implementation Integrity: 22/22 Unit Tests Pass**
   - Data: All curriculum conditions, model architectures, evaluation pipelines validated
   - "So What": Establishes implementation trustworthiness; results (when available) won't be artifacts of buggy code
   - Suggested Figure/Table: Table of test coverage (configuration, curriculum, model, evaluation)

2. **Diversity Score Ranking: Clear High-to-Low Ordering**
   - Data: Pile-CC (0.92) > StackExchange (0.88) > Wikipedia (0.75) > ArXiv (0.58) > Github (0.42) > PubMed (0.35)
   - "So What": Demonstrates diversity metric captures intuitive domain characteristics (web > code, general > specialized)
   - Suggested Figure/Table: Bar chart of diversity scores by domain with metric breakdown

3. **Curriculum Execution: Smooth Domain Weight Transitions**
   - Data: Gaussian-weighted domain sampling probabilities over training progress (0-100%)
   - "So What": Shows the method implements gradual curriculum (not abrupt phase transitions), maintaining some exposure to all domains throughout
   - Suggested Figure: Line plot of domain weights vs training progress for diversity-ranked condition

**If Phase 5 Confirms, Add Performance Evidence:**

4. **Performance Improvement: Diversity-Ranked > Static Baseline** [PENDING]
   - Data: Composite benchmark scores (MMLU, Big-Bench, domain-specific) across 4 conditions
   - "So What": Core claim validation — temporal ordering matters
   - Suggested Figure: Bar chart with error bars (4 conditions × 2 scales)

5. **Statistical Significance: Effect Robust Across Seeds** [PENDING]
   - Data: Paired t-test results (p<0.05), confidence intervals, effect sizes
   - "So What": Not a lucky seed — effect is reproducible
   - Suggested Figure/Table: Statistical testing table with p-values, CIs, Bonferroni correction

**If h-m1 through h-m4 Confirm, Add Mechanism Evidence:**

6. **Diversity-PR Correlation: ρ≥0.7 Across Domains** [PENDING h-m1]
   - Data: Scatter plot of diversity scores vs PR@10% for 6-8 domains
   - "So What": Validates predictive diversity law — corpus statistics predict gradient geometry
   - Suggested Figure: Scatter plot with correlation coefficient

7. **Geometric Persistence: CKA Higher for Diversity-Ranked** [PENDING h-m2]
   - Data: Layer-wise CKA similarity (25%→100%) for diversity-ranked vs reversed
   - "So What": Confirms early geometry persists — supports path dependence claim
   - Suggested Figure: Heatmap of CKA by layer and condition

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `verification_state.yaml` | N/A | Pipeline state tracking |
| `03_refinement.yaml` | Main hypothesis | Original hypothesis from Phase 2A |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design specification |
| `h-e1/03_tasks.yaml` | h-e1 | Implementation task definitions |
| `h-e1/04_checkpoint.yaml` | h-e1 | Phase 4 workflow state and metrics |
| `h-e1/04_validation.md` | h-e1 | Phase 4 validation report |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Generated by Phase 4.5 Hypothesis Synthesis v2.0*
*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
