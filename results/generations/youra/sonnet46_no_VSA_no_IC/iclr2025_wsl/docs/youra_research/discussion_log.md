# Phase 2A Discussion Log
## Gap: Controlled Comparison of Equivariant vs. Plain Architectures for Weight-Space Property Prediction

**Gap ID:** gap2
**Priority:** HIGH+PRIMARY
**Date:** 2026-08-21
**Execution Mode:** UNATTENDED (Self-Play — Claude plays ALL personas)
**Architecture:** Self-Contained Tikitaka Loop (independent-controller ablation)

---

## Briefing Context

### Research Gap

No paper performs a controlled comparison of equivariant vs. plain approaches on the same data under matched compute budgets. Each method uses its own train/test splits. Dayan et al. 2026 proves equivalent expressivity, making **efficiency the key differentiator** — but no benchmark quantifies this.

**Current State:**
- DWSNets [Navon et al. 2023], GNN-NFN [Kofinas et al. 2024], NFN [Zhou et al. 2023] each benchmark independently
- Schürholt's SSL (plain MLP) outperforms random without explicit equivariance
- No unified comparison on ModelZooDataset or equivalent

**Missing Piece:** Benchmark study on shared data training equivariant (DWSNets, GNN-NFN) and plain (flat MLP, NN-token-transformer) encoders with identical data splits, evaluating accuracy prediction, generalization gap prediction, hyperparameter inference, controlling for parameter count and compute budget.

### Reference Papers Available (Phase 1)

- P1: Dayan, Eitan, Maron 2026 — "On the Expressive Power of Permutation-Equivariant Weight-Space Networks" [arXiv:2602.01083] — all equivariant networks equivalent; 34% improvement from theory; efficiency comparison needed
- P2: Schürholt et al. 2021 — "Self-Supervised Representation Learning on Neural Network Weights" [arXiv:2110.15288] — SSL (plain) baseline predicts accuracy/generalization gap from weights; no equivariant comparison on same data
- P3: Navon et al. 2023 — "Equivariant Architectures for Learning in Deep Weight Spaces" [arXiv:2301.12780] — DWSNets; claims advantage over "natural baselines" but different data splits
- P4: Kofinas et al. 2024 — "Graph Neural Networks for Learning Equivariant Representations of Neural Networks" [arXiv:2403.12143] — GNN-NFN; diverse architectures; SOTA property prediction
- P5: Herrmann, Faccio, Schmidhuber 2024 — "Learning Representations of RNN Weight Matrices" [arXiv:2403.11998] — mechanistic vs functionalist comparison on RNN weights; partial model for broader comparison

### Key Dataset

**ModelZooDataset** [Schürholt et al. 2022, arXiv:2209.14764] — standardized model zoo datasets with ground-truth performance metrics. Available at: https://github.com/ModelZoos/ModelZooDataset

### Feasibility Constraints (MANDATORY)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- ONLY existing real datasets and existing benchmarks

### Previous Failure Context

No previous failure context — first Phase 2A execution.

---

## Discussion Log

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The theoretical bombshell from Dayan et al. 2026 changes the framing entirely. If all permutation-equivariant weight-space networks have equivalent expressivity, then the race isn't about *what* can be represented — it's about *how efficiently* we get there. This is a genuinely unexplored empirical territory: nobody has run equivariant (DWSNets, GNN-NFN) and plain (flat MLP, weight-flattened transformer) encoders side-by-side on the *same* ModelZooDataset splits with matched parameter counts.

Here's what makes this exciting beyond a simple ablation: the theoretical equivalence from Dayan et al. actually predicts that equivariant methods should win on *sample efficiency*, not raw performance ceiling. Why? Because the inductive bias from permutation equivariance constrains the hypothesis space — so you need fewer training models to fit the same property prediction function. A plain MLP has to discover this structure from data alone.

My proposed angle: test the hypothesis that **equivariant encoders reach 95% of peak accuracy prediction performance with fewer training examples than parameter-matched plain encoders**, using ModelZooDataset's MNIST/CIFAR model zoos as the training population. The "data efficiency curve" (accuracy vs. number of training models) would be the novel contribution — never been plotted for this comparison.

Two additional unconventional angles:
1. **Permutation augmentation as bridge**: Apply random neuron permutations as data augmentation to train plain MLPs — does augmentation close the gap? This tests whether the equivariance is structural or can be learned.
2. **Latent geometry comparison**: Compare the geometry of latent spaces learned by equivariant vs. plain encoders using existing metrics (centered kernel alignment, linear CKA) — does equivariance produce more structured latent organization on the same data?

**Key Points:**
- Dayan 2026 proves expressivity equivalence → efficiency is the differentiator
- Sample efficiency curve is the unexplored and publishable claim
- ModelZooDataset provides the shared benchmark needed
- Permutation augmentation provides a natural baseline bridge

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is compelling, but we need to be precise about what "efficiency" means and ensure the predictions are falsifiable. Let me stress-test the experimental design.

The sample efficiency claim is testable, but the operationalization needs care. On ModelZooDataset's MNIST model zoo, Schürholt et al. 2021 trained on approximately 4,000 models (standard split). To test the efficiency curve, we need to vary the training set size systematically: e.g., {100, 250, 500, 1000, 2000, 4000} models, and measure test-set accuracy prediction R² for each. This is doable with existing data.

**Critical falsifiability concerns:**

First, "parameter-matched" needs a precise definition. DWSNets uses a specific architecture with permutation-equivariant layers that have different computational structure than flat MLPs. We should control for *parameter count* (total trainable parameters) rather than FLOPs, since FLOPs depend on weight size. At each parameter count, the equivariant and plain models should have comparable capacity.

Second, the success criterion for "equivariant encoders are more sample efficient" must be pre-specified. I propose: equivariant achieves R² ≥ 0.90 of its peak performance at ≤50% of the training data required for plain MLP to achieve the same R² threshold. This is falsifiable — if equivariant needs 2000 models and plain MLP needs 3000, equivariant wins; if both need ~2000, the null holds.

Third, Schürholt's plain SSL (2021) already achieves meaningful accuracy prediction *without* equivariance. The baseline is not "random" — it's SSL on flattened weights. This actually strengthens the hypothesis if equivariance provides further gain, but it sharpens what we're testing.

**On the permutation augmentation angle:** This is scientifically valuable but complicates the comparison. I'd recommend running it as a third condition: (1) equivariant, (2) plain-flat, (3) plain-flat + permutation augmentation. This cleanly tests whether structural equivariance is better than augmented equivariance.

**Key Points:**
- Training size ablation: {100, 250, 500, 1000, 2000, 4000} models — all in existing ModelZooDataset
- Success criterion: equivariant reaches 90% of peak R² at ≤50% training data vs. plain
- Three conditions: equivariant / plain / plain+augmentation
- Metric: R² for accuracy prediction; also generalization gap prediction as secondary

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both Dr. Nova and Prof. Vera have identified a clean, high-impact problem. Let me evaluate the significance and sharpen the contribution framing.

The field has a reproducibility crisis around weight-space method comparisons. DWSNets, GNN-NFN, NFN — all published with strong results, but on different datasets, different train/test splits, different tasks, and different compute budgets. Dayan et al. 2026 highlights theoretical equivalence but cannot empirically adjudicate whether one approach is more practical. This comparison study fills a critical infrastructure gap.

**Impact Assessment:**
- **Direct beneficiaries**: Practitioners choosing between equivariant and plain encoders for model zoo applications (e.g., model selection at Hugging Face scale)
- **Indirect impact**: Clarifies whether symmetry exploitation is "worth the engineering complexity" — DWSNets and GNN-NFN require careful architecture-specific design, while plain MLPs are off-the-shelf
- **Publication venue**: NeurIPS/ICML datasets & benchmarks track, or a comparison/analysis paper — competitive with similar "empirical study" papers that have strong methodology

**Sharpening the claim for significance:**

The most impactful framing isn't just "equivariant wins on sample efficiency" — it's a *predictive* claim: **equivariant inductive bias has measurable value specifically in the low-data regime** (few training models), while converging to similar performance in the high-data regime (many training models). This would be the first quantitative answer to "when does it matter whether you use equivariant weight-space encoding?"

This matters because real-world model zoos are often small. The Schürholt RNN zoo has ~1000 models. The NFN transformer zoo has ~125K but for a narrow architecture family. The efficient regime is the practical regime.

**Three testable predictions that have clear impact:**
1. Equivariant encoders achieve ≥10% higher R² for accuracy prediction at training sizes ≤500 models
2. The performance gap narrows to <5% at full dataset (4000+ models)
3. Plain encoder + permutation augmentation fills 50-70% of the gap (validating that the benefit is structural, not magic)

**Key Points:**
- Framing: "when does equivariant inductive bias matter?" — answers a field-wide practical question
- Low-data regime is the publishable finding; high-data convergence is the null boundary
- Prediction 3 (augmentation) provides mechanism explanation
- All 3 predictions testable on existing ModelZooDataset

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The discussion is converging on a strong hypothesis. Let me ground this in implementation reality and flag any execution risks.

**Feasibility Assessment: HIGH**

The core experiment is technically straightforward:
- ModelZooDataset MNIST model zoo: ~4,860 trained CNNs with ground-truth test accuracy — publicly available at https://github.com/ModelZoos/ModelZooDataset
- DWSNets: fully open-sourced at https://github.com/AvivNavon/DWSNets with training scripts
- NFN: pip-installable at https://github.com/AllanYangZhou/nfn
- Schürholt SSL baseline: code at https://github.com/HSG-AIML/NeurIPS_2021-Weight_Space_Learning

**The flat MLP baseline** needs implementation, but it's trivial: flatten all weights per model into a vector, pass through standard MLP with same parameter count. This is ~50 lines of PyTorch.

**Concrete execution plan:**
1. Download ModelZooDataset MNIST zoo
2. Implement 5 training size conditions: {100, 250, 500, 1000, full}
3. For each condition, train: (a) DWSNets, (b) plain MLP (matched params), (c) plain MLP + perm augmentation
4. Evaluate: R² for test accuracy prediction (primary), generalization gap prediction (secondary)
5. Plot: sample efficiency curves for all 3 conditions

**Risk flags:**
- DWSNets expects specific weight format — need to verify MNIST zoo checkpoint format compatibility (likely fine, but confirm before running)
- Parameter matching across architecturally different models is non-trivial: DWSNets equivariant layers have different structure. Solution: use model size categories (small/medium/large) rather than exact parameter count
- Runtime: training 5 sizes × 3 conditions × multiple seeds → ~15 experiments. At ~1 hour each on GPU, this is ~15-20 GPU hours. Very feasible.

**One concern about scope**: Should we include GNN-NFN (Kofinas 2024) as a fourth condition? It handles diverse architectures better but adds complexity. I recommend including it as it is already implemented and pip-installable, adding one condition at minimal cost — makes the comparison more complete and the paper more citable.

**Key Points:**
- All code exists, all data exists — zero new collection required
- 15-20 GPU hours total — feasible single-machine experiment
- Add GNN-NFN as fourth condition: equivariant, GNN-NFN, plain, plain+aug
- Parameter matching: use parameter count ranges, not exact matching

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We have strong convergent signal from all four perspectives. Let me synthesize and strengthen the emerging hypothesis into a clean, testable form.

**Synthesized Hypothesis:**

*Under the weight-space property prediction setting using the ModelZooDataset MNIST model zoo, if we train equivariant (DWSNets, GNN-NFN) versus plain (flat-MLP, flat-MLP+permutation-augmentation) weight-space encoders at matched parameter budgets across a systematically varied training set size, then equivariant encoders will demonstrate superior sample efficiency — reaching ≥90% of their peak accuracy-prediction R² at ≤50% of the training set size required by plain encoders — because permutation equivariance provides a structural inductive bias that constrains the hypothesis space to symmetry-consistent functions, reducing the effective sample complexity of learning weight-space property mappings.*

**Why this is strong:**
1. **Grounded in theory**: Dayan et al. 2026 proves expressivity equivalence — sample efficiency is the *only* remaining differentiator, making this a direct empirical test of the theoretical implication
2. **Testable with existing resources**: ModelZooDataset, DWSNets code, NFN code, Schürholt baseline — all public
3. **Quantitative success criterion**: The 90%/50% threshold is pre-specified and falsifiable
4. **Mechanism is testable via third condition**: plain+permutation-augmentation isolates whether the benefit is structural (inductive bias) or can be mimicked by augmentation

**Strengthening moves:**
- Include generalization gap prediction as secondary DV (Schürholt 2021 uses both)
- Report hyperparameter sensitivity: run each condition with 3 random seeds for error bars
- The latent geometry comparison (CKA) proposed by Dr. Nova adds mechanistic insight without new data

**What makes this novel vs. prior work:**
- DWSNets 2023: uses its own MNIST zoo, different splits, no plain comparison
- Schürholt 2021: plain SSL only, no equivariant condition
- GNN-NFN 2024: benchmarks on its own architectures, different splits
- **This work**: first controlled comparison on shared splits at multiple training sizes

**Key Points:**
- Core hypothesis: equivariant encoders are more sample-efficient than plain encoders on ModelZooDataset
- Quantified: 90%/50% R² threshold rule
- Mechanism test: permutation augmentation condition
- Novel contribution: first controlled comparison with shared data splits

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'll apply adversarial pressure to identify the weakest points in the hypothesis.

**Concern 1: The effect size may be trivially small or null**

Schürholt et al. 2021's plain SSL already achieves R² ≈ 0.83 for accuracy prediction on the MNIST zoo. DWSNets reports R² ≈ 0.89 on its *own* zoo split (not identical to Schürholt's). The gap is ~0.06 R² — small. If we're measuring "sample efficiency" curves and this gap exists but is tiny, the finding might be "equivariant is marginally better but not practically meaningful." **Mitigation**: The 90%/50% criterion focuses on *relative* sample efficiency, not absolute performance. Even if both methods plateau at R²=0.89, if equivariant gets there with 1000 models and plain needs 4000, that's a 4× efficiency gain — practically meaningful.

**Concern 2: ModelZooDataset MNIST zoo may be too small to detect the effect reliably**

4,860 models sounds large, but when we subsample to 100-500 training models, variance across random splits will be high. With 3 seeds, the confidence intervals at small training sizes may overlap substantially. **Mitigation**: Use bootstrap confidence intervals with 10+ seeds at small sizes (computationally cheap since models are small). The CIFAR-10 zoo (also in ModelZooDataset) can be used for replication.

**Concern 3: Parameter matching is harder than it sounds**

DWSNets equivariant layers have specific architectural constraints (parameter sharing across equivariant dimensions) that make direct parameter count matching non-trivial. A "parameter-matched" MLP may have a fundamentally different architecture depth/width. **Mitigation**: Prof. Pax's suggestion of using parameter count *ranges* (e.g., <50K, 50K-200K, >200K) rather than exact matching is correct. Run sensitivity analysis: does the efficiency gap persist across size ranges?

**Concern 4: What if augmentation fully closes the gap?**

If plain-MLP + permutation augmentation performs identically to DWSNets equivariant, the finding would be "you don't need equivariant architectures, just augment." This might be seen as a negative result. **Mitigation**: This is actually a publishable finding either way. If augmentation closes the gap, it validates that equivariance is the mechanism *and* provides a practical alternative that avoids architectural constraints. Frame it as "we quantify the value of structural vs. learned symmetry."

**Remaining concerns after mitigation:**
- Need CIFAR zoo replication to avoid single-dataset conclusions
- Must pre-register success criteria before running experiments to avoid p-hacking
- Confidence interval analysis is essential at small training sizes

**Overall verdict**: The hypothesis is testable, novel, and the major concerns have clear mitigations. I recommend proceeding to Phase 2B with the controlled comparison design.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "data efficiency curve" for equivariant vs. plain weight-space encoders has never been reported. Dayan et al. 2026's expressivity equivalence result makes this empirical test theoretically motivated and timely — the community needs this comparison. The permutation augmentation as third condition is an unconventional angle that adds mechanistic depth.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The 90%/50% success criterion is pre-specified and falsifiable. The experimental design (shared ModelZooDataset splits, multiple training sizes, multiple seeds) is rigorous. Three conditions provide clean attribution. The only risk is statistical power at smallest training sizes, which bootstrap resampling addresses.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Answers a field-wide practical question: "when does equivariant inductive bias matter?" The low-data regime finding directly informs practitioners choosing encoders for small model zoos. Publication-worthy as an empirical analysis paper at NeurIPS/ICML.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All code and data are publicly available. Estimated 15-20 GPU hours. The flat MLP baseline is trivial to implement. Main technical risk (parameter matching) has a clear resolution via parameter count ranges. This can be completed in 1-2 weeks of focused effort.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is both theoretically motivated and empirically tractable. The core claim: **equivariant weight-space encoders (DWSNets, GNN-NFN) are more sample-efficient than plain encoders (flat MLP, flat MLP + permutation augmentation) for model property prediction on the ModelZooDataset MNIST model zoo, specifically in the low-data regime (≤500 training models), because permutation equivariance constrains the hypothesis space to symmetry-consistent functions.**

The proposed experiment trains all four encoder types (DWSNets, GNN-NFN, plain MLP, plain MLP+augmentation) at matched parameter budget ranges across 5 training sizes (100, 250, 500, 1000, full ~4860) on the shared ModelZooDataset MNIST zoo split. Primary metric: R² for test-set accuracy prediction. Secondary: generalization gap prediction R². Success criterion (pre-specified): equivariant encoders reach 90% of their peak R² at ≤50% training size required by plain MLP.

The permutation augmentation condition is the key mechanistic test: if augmentation closes the gap, structural equivariance is not required but the mechanism is confirmed. If not, structural inductive bias provides irreplaceable sample efficiency. Either result is publishable and clarifies when architectural equivariance is worth the engineering complexity.

This study would be the first controlled comparison on shared data splits, filling the reproducibility gap that Dayan et al. 2026 theoretically motivates and that Schürholt 2021 and Navon 2023 leave open empirically.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Small training size confidence intervals may be wide — must use bootstrap with 10+ seeds at sizes ≤250
- Single dataset (MNIST zoo) is insufficient — CIFAR-10 zoo replication is mandatory for generalization claim
- **Mitigation Strategy:** Pre-register the success criterion (90%/50% R² threshold) and include both MNIST and CIFAR zoos in Phase 2B experimental design. Use bootstrap CIs throughout.

