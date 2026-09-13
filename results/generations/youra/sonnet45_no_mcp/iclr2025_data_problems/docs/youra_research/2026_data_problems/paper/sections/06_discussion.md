# 6. Discussion

## 6.1 PoC Validation Achievements

This work demonstrates that diversity-ranked domain scheduling is **feasible to implement and test** at scale. Our PoC validation confirms:

1. **Systematic diversity quantification**: Corpus-level metrics (vocabulary entropy, syntactic complexity, semantic spread) provide a principled basis for domain ranking, avoiding ad-hoc manual categorization.

2. **Smooth curriculum scheduling**: Gaussian-weighted temporal composition enables continuous domain transitions without sharp phase boundaries, generalizing two-phase training to parametric schedules.

3. **Controlled experimental design**: Four conditions (static, diversity-ranked, reversed, shuffled) isolate the effect of temporal ordering while matching total per-domain exposure, enabling causal inference about scheduling's impact.

4. **Operational pipeline**: Complete implementation (data loading, curriculum scheduling, model training, evaluation) executes without errors, ready for full-scale 100K+ step experiments.

**Contribution to methodology**: Even absent performance improvements, diversity-ranked scheduling provides a structured framework for exploring temporal data composition as an alternative to static mixture hyperparameter search. The approach is compatible with existing domain reweighting methods (e.g., DoReMi) and could be combined: use DoReMi to determine domain budgets, then apply diversity-ranked scheduling to order their presentation.

## 6.2 Proposed Mechanism: Gradient Covariance Geometry (Unverified)

**Hypothesis**: We propose that diversity-ranked scheduling improves performance through a four-step causal chain:

**Step 1: Diversity → Gradient Covariance (h-m1, pending)**  
Early high-diversity data (broad vocabulary, varied syntax, distributed semantics) induces higher-rank gradient covariance matrices. We hypothesize that corpus diversity metrics correlate with Participation Ratio at 25% training (Spearman $\rho \geq 0.7$). If $\rho < 0.5$, this coupling fails and diversity cannot predict optimal schedules.

**Step 2: Gradient Covariance → Persistent Geometry (h-m2, pending)**  
Path-dependent SGD optimization crystallizes representational subspaces during early training. We hypothesize that diversity-ranked scheduling exhibits $\geq 10\%$ higher CKA similarity between 25% and 100% checkpoints compared to reversed scheduling. If CKA persistence is equal or lower, early geometry does not persist and temporal ordering has no lasting effect.

**Step 3: Persistent Geometry → Specialization Without Collapse (h-m3, pending)**  
Later low-diversity domain training (code, scientific papers) refines within the established broad subspace without destructive interference. We hypothesize that within-batch diversity entropy at 75%/100% training remains $\geq 5\%$ higher for diversity-ranked vs reversed. If late-training entropy collapses equally across conditions, the broad geometry hypothesis fails.

**Step 4: Broad Geometry → Robust Continual Learning (h-m4, pending)**  
Higher gradient subspace orthogonality reduces catastrophic forgetting during new domain adaptation. We hypothesize that legal domain injection after main training causes $\leq 50\%$ forgetting for diversity-ranked vs reversed, with $\geq 10\%$ higher Fisher overlap (coupled requirement). If forgetting reduction occurs without Fisher overlap changes, the geometric stability explanation is falsified.

**Current Status**: All four mechanism steps are **UNVERIFIED hypotheses**. PoC validation confirms implementability but includes no gradient geometry measurements. Mechanism validation requires:
- Full training to convergence (100K+ steps)
- Multi-checkpoint gradient covariance storage (10%, 25%, 50%, 75%, 100%)
- PR computation on fixed probe datasets
- Layer-wise CKA between checkpoint pairs
- Continual learning experiments with Fisher Information estimation

**Alternative Explanations**: If full-scale experiments (Phase 5) find performance improvements but mechanism hypotheses (h-m1 through h-m4) fail, alternative explanations include:
- Implicit regularization (early diversity acts as data augmentation)
- Optimizer momentum accumulation (domain ordering affects momentum statistics)
- Batch composition artifacts (within-batch diversity, not global geometry)
- Curriculum coherence effects (monotonic structure, independent of gradient geometry)

The shuffled control condition tests the last alternative: if diversity-ranked equals shuffled (both outperform static/reversed), improvement comes from early high-diversity exposure, not temporal ordering structure.

## 6.3 Limitations

### L1: PoC Scope — Performance Claims Unvalidated

**What**: Current results limited to 10-step smoke test (single run, seed 42, static condition only). Performance improvement predictions (≥2.0% at 1B, ≥0.5% at 7B) are untested hypotheses.

**Impact**: Cannot claim the method "works" in terms of improving model performance. Only established that the method is "implementable."

**Why Acceptable**: PoC validation serves to confirm feasibility before committing 45K GPU-hours to full experiments. Separating implementation validation from performance validation improves rigor and avoids premature conclusions from underpowered experiments.

**Mitigation**: Phase 5 experiments (ongoing) will train 40 runs (4 conditions × 2 scales × 5 seeds) to convergence with statistical testing. Estimated completion: 6-8 weeks.

### L2: Mechanism Unverified — Gradient Geometry Hypothetical

**What**: All causal mechanism steps (diversity→PR, PR→CKA persistence, persistence→specialization, geometry→robustness) lack empirical evidence.

**Impact**: Even if Phase 5 finds performance improvements, the **explanation** for why diversity-ranked scheduling works remains speculative without direct gradient geometry measurements.

**Why Acceptable**: (1) Performance improvement (if found) is valuable even without mechanistic explanation; (2) Mechanism verification is explicitly scoped to subsequent hypotheses (h-m1 through h-m4) with falsifiable predictions; (3) The proposed mechanism is testable and we provide concrete success criteria.

**Future Work**: Hypotheses h-m1 through h-m4 will systematically validate each mechanism step. If any step fails, the explanation requires revision, but the method (if performant) remains useful.

### L3: Single Hypothesis — Mechanism Chain Pending

**What**: Only h-e1 (existence) validated at PoC level. Mechanism hypotheses h-m1 (diversity-PR correlation), h-m2 (CKA persistence), h-m3 (late-training preservation), h-m4 (continual learning robustness) not yet executed.

**Impact**: Cannot claim "predictive diversity law" (requires h-m1: $\rho \geq 0.7$) or "broader geometry persists" (requires h-m2: CKA $\geq 10\%$ higher).

**Why Acceptable**: Sequential validation follows principled hypothesis decomposition (dependency graph: h-e1 → h-m1 → h-m2 → h-m3 → h-m4). Testing mechanism before confirming existence is methodologically backwards. The MUST_WORK gate (h-e1) must pass before mechanism investigation proceeds.

### L4: Diversity Metrics Unvalidated

**What**: Composite diversity score combines vocabulary entropy, syntactic complexity, semantic spread with equal weights. This combination is a heuristic, not empirically validated.

**Impact**: Alternative metric combinations (geometric mean, learned weights) or different features (n-gram entropy, discourse structure) might produce better domain rankings.

**Future Work**: Hypothesis h-m1 will test whether current diversity metrics correlate with early gradient covariance rank. If $\rho < 0.5$, metrics require refinement. If $\rho \geq 0.7$, current metrics are sufficient for predictive scheduling.

### L5: Computational Cost

**What**: Full experiment matrix requires ~45K GPU-hours (4 conditions × 2 scales × 5 seeds, ~100-150K steps each).

**Impact**: High computational cost limits accessibility to well-resourced research labs, reducing reproducibility.

**Partial Mitigation**: We provide complete implementation with unit tests. Researchers with limited compute can validate on smaller scales (e.g., 100M parameters, 10K steps) or single conditions. The curriculum scheduling framework generalizes beyond our specific experimental setup.

## 6.4 Comparison to Related Work

**vs DoReMi (Xie et al., 2023):**
- DoReMi: Optimizes **static** domain mixing ratios using group DRO
- Our work: Introduces **temporal** dynamics via diversity-ranked scheduling
- Complementary: Could combine DoReMi (determine budgets) + diversity-ranked (order presentation)
- Status: DoReMi reports full results; we report PoC only (performance pending)

**vs Curriculum Learning (Bengio et al., 2009):**
- Curriculum learning: Example-level difficulty ordering within fixed dataset
- Our work: Domain-level diversity ordering across data sources
- Extension: Applies curriculum principles to foundation model pretraining data composition
- Novel aspect: Corpus statistics (vocabulary, syntax, semantics) instead of training-time difficulty

**vs Two-Phase Training (GPT-3, Codex):**
- Two-phase: Sharp transition (general → specialized), ad-hoc design
- Our work: Smooth parametric Gaussian scheduling with controlled experiments
- Generalization: Two-phase is a special case (2 domains, step function transitions)

## 6.5 Broader Impacts

**If Validated (Phase 5 Pending):**

**Positive Impacts:**
- Reduced hyperparameter search cost for domain mixing (corpus statistics predict schedules)
- Improved multi-domain performance for foundation models
- Better continual learning robustness (if h-m4 confirms)
- Generalizable framework applicable to any multi-domain training corpus

**Risks:**
- Diversity metrics may encode biases (e.g., favoring Western web text over non-English domains)
- Increased computational complexity (dynamic scheduling vs static sampling)
- Potential misuse: Optimizing schedules for specific evaluation benchmarks (overfitting to MMLU/Big-Bench)

**Ethical Considerations:**
- Diversity quantification must be examined for demographic biases (e.g., does "high diversity" correlate with majority-group language patterns?)
- Domain ranking decisions affect what knowledge models prioritize during learning
- Transparency: We release diversity computation code and metrics to enable scrutiny

## 6.6 Future Directions

**Immediate (Phase 5):**
1. Full-scale performance validation: 40-run experiment matrix with statistical testing
2. Mechanism validation: Hypotheses h-m1 through h-m4 with gradient geometry measurements
3. Scaling analysis: Compare 1B vs 7B to test whether effects persist at scale

**Extensions:**
1. **Adaptive scheduling**: Use runtime gradient statistics (PR measured online) to adjust domain weights dynamically instead of pre-computed fixed schedules
2. **Learned diversity metrics**: Train a model to predict gradient covariance rank from corpus samples, replacing hand-crafted vocabulary/syntax/semantic features
3. **Multi-objective optimization**: Balance diversity-ranked scheduling with DoReMi-style domain reweighting for joint temporal and budget optimization
4. **Alternative transition functions**: Explore linear, cosine, or learned scheduling functions beyond Gaussian weights
5. **Cross-architecture validation**: Test on encoder-decoder models (T5 style) and encoder-only models (BERT style), not just decoder-only transformers
6. **Other modalities**: Apply domain scheduling to vision-language pretraining (diverse image-text datasets) or multimodal foundation models

**Long-term:**
1. **Scaling laws for temporal composition**: Integrate curriculum scheduling into Chinchilla-style scaling formulas (compute-optimal temporal ordering as function of model size and data budget)
2. **Theoretical analysis**: Prove convergence guarantees or PAC bounds for diversity-ranked scheduling under specific assumptions about gradient covariance dynamics
3. **AutoML for curriculum**: Meta-learn scheduling policies across multiple training runs to discover optimal temporal composition automatically
