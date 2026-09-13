# Phase 2A Discussion Log
**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation — no external LLM)  
**Gap ID:** gap-1  
**Gap Title:** Incomplete Symmetry Coverage — Scaling and Sign-Flip Beyond Permutation  
**Execution Mode:** UNATTENDED  
**Date:** 2026-08-26  

---

### Previous Failure / Routing Context

**Superseded Hypothesis:** h-e1  
**Supersede Date:** 2026-08-26  
**Failure Type:** Phase 4 GATE FAIL — Hard architectural incompatibility  

**Root Cause:** DWSNets (Navon et al. 2023) enforces `assert len(weight_shapes) > 2`, but the Schürholt MNIST zoo uses 2-layer MLPs (784→64→10), producing exactly 2 weight matrices. Hard constraint — no hyperparameter tuning resolves it.

**What Worked (preserve):**
- NFT: ρ=0.113 (lr_recovery), ρ=0.110 (gen_gap), ρ=0.104 (accuracy) — best performer among 4 working encoders
- Unified data loader confirmed working with flat_mlp, flat_mlp_canon, hyper_repr, NFT
- Schürholt MNIST zoo is a valid, loadable benchmark

**Prohibited Directions:**
- DWSNets on M=2 layer zoos (hard constraint)
- `dataset_clf` on single-dataset zoos (degenerate)
- Any approach requiring DWSNets as core equivariant encoder unless zoo switched to 3+ layer nets

**Phase 2A Direction:** New hypothesis must use NFT (or flat_mlp variants) as encoder backbone. Gap 1 (scaling/sign-flip symmetries) is compatible: NFT is permutation-equivariant but does NOT handle scaling/sign-flip.

---

## Briefing Context

**Research Gap:** Weight space learning has focused almost exclusively on permutation symmetry. Scaling symmetry (weight rescaling with compensating downstream rescaling) and sign-flip symmetry (sign-flip equivalence in consecutive ReLU layers) are theoretically characterized but NOT incorporated into property prediction encoders. No empirical ablation measuring their contribution to property prediction accuracy exists.

**Key Papers:**
- Zhou et al. 2023 (NFN): Permutation-equivariant MLP weight processing. No scaling/sign-flip handling.
- Navon et al. 2023 (DWSNets): Broader equivariance theory; scaling characterized but M>2 constraint.
- Schürholt et al. 2022 (Model Zoos): ~50k trained MLPs; test accuracy, gen_gap, lr_recovery ground truth.
- Unterthiner et al. 2020: Layer-wise stats baseline, ρ~0.9 on simple zoos.

**Existing Validated Baseline:** NFT achieves ρ~0.11 on Schürholt zoo (all 3 tasks). Flat MLP also confirmed.

**Feasibility Constraints:** No new benchmarks, no synthetic data, no human evaluation, existing datasets only.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The superseded hypothesis h-e1 collapsed on a hard constraint — DWSNets won't touch 2-layer networks. But NFT works: Spearman ρ~0.11 on three property prediction tasks, right out of the box, on a 2-layer MLP zoo. That's our launch pad.

Gap 1 is compelling because the field has been content to rest on permutation equivariance. But a trained MLP weight vector also lives in a space with scaling equivalences (multiply layer 1 weights by λ, divide layer 2 by λ — same function) and sign-flip equivalences (ReLU preserves equivariance under simultaneous weight sign flips across consecutive layers). If we're encoding weights to predict properties, we're computing in a redundant, non-canonical space. The encoder must "learn around" these redundancies during training.

Unconventional angles:

**Angle 1 — Canonical Pre-Processing:** Before feeding weights into NFT, apply a canonicalization step that normalizes out scaling and sign-flip orbits (normalize each neuron's incoming weight vector to unit norm; choose sign convention based on majority sign). Zero architecture changes. If Spearman ρ improves, causal evidence that these symmetries hurt prediction.

**Angle 2 — Symmetry-Augmented Training:** Train NFT with data augmentation that randomly applies scaling and sign-flip transformations to weight vectors. Forces encoder to learn invariant features without architectural changes.

**Angle 3 — Lightweight Normalization Module:** Add a preprocessing layer before NFT that canonicalizes the scaling orbit (layer-norm on weight matrices) and sign-flip orbit (learned sign-correction layer).

Angle 1 is the most immediately feasible: zero architecture changes, works on existing Schürholt zoo with existing NFT code, produces a clean ablation.

**Key Points:**
- NFT baseline ρ~0.11 is our starting point, not ceiling
- Scaling and sign-flip symmetries create redundancy the encoder must overcome
- Canonical preprocessing (Angle 1) is the fastest, most falsifiable first test
- All angles use existing datasets + benchmarks — pipeline-feasibility satisfied

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's Angle 1 is attractive for simplicity, but the falsifiability architecture needs stress-testing before we commit.

First: the null hypothesis. If canonicalization improves ρ, that's consistent with "these symmetries hurt NFT" — but also with "normalization helps optimization" or "preprocessing removes noise unrelated to symmetry." We need a control: apply random normalization that does NOT remove symmetry-relevant variance (scale each neuron's weights by N(1,ε)) to isolate canonicalization from general normalization effects.

Second: Spearman ρ variance. NFT at ρ~0.11 is not a high bar — but we need confidence intervals before claiming any improvement is real. The zoo has ~50k models, so variance should be manageable, but this must be verified.

Third: sign-flip canonicalization is more complex than it looks. For ReLU networks, sign-flip equivalence holds at the function level only when flipping signs in consecutive layer pairs simultaneously. Flipping only one layer changes the function. The canonicalization must apply simultaneous flips — non-trivial implementation.

Proposed 5-condition experimental structure:
- **Condition A:** Raw weights → NFT (baseline, ρ_baseline)
- **Condition B:** Scaling-canonicalized weights → NFT (ρ_scale)
- **Condition C:** Sign-flip-canonicalized weights → NFT (ρ_sign)
- **Condition D:** Both canonicalizations → NFT (ρ_both)
- **Condition E:** Random normalization control → NFT (ρ_control)

If ρ_both > ρ_baseline AND ρ_both > ρ_control, strong evidence. If ρ_both ≈ ρ_control, normalization artifact.

**Key Points:**
- Need null hypothesis with proper control (random normalization, Condition E)
- Sign-flip canonicalization requires simultaneous layer-pair flips for ReLU
- Bootstrap confidence intervals on Spearman ρ essential
- 5-condition ablation (A-E) gives clean causal attribution

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's 5-condition design is rigorous. But the "so what" question: layer-wise statistics achieve ρ~0.9 (Unterthiner et al.) on simple zoos, while NFT achieves ρ~0.11. If canonicalization brings NFT to ρ=0.20, we're still well below the layer stats baseline. Is this a publishable finding?

Yes — for a specific reason. The scientific question is NOT "beat layer stats on MNIST" but "do scaling/sign-flip symmetries carry measurable information relevant to model properties?" Even a modest improvement from canonicalization is evidence that the symmetry structure of weight space is NOT fully captured by permutation-equivariant encoders. That's theoretically important.

If framed correctly, the impact extends beyond the specific benchmark. The theoretical claim: **model properties correlate with weight-space orbits under the full symmetry group (permutation × scaling × sign-flip), not just the permutation subgroup.** If true, this motivates a whole class of improved encoders across many tasks and architectures.

Most impactful additional experiment: test whether improvement from canonicalization is larger on more complex zoos (SVHN, CIFAR — Schürholt also released these, using deeper networks). If symmetry canonicalization helps more when weight space is more complex, that's a strong mechanism-consistent pattern.

**Key Points:**
- Research impact doesn't require beating layer stats — demonstrating symmetry structure matters is the key claim
- Full symmetry group framing (permutation × scaling × sign-flip) is the theoretical contribution
- Effect size scaling with zoo complexity (MNIST vs SVHN vs CIFAR) would be powerful confirmatory evidence
- Publishable: evidence that permutation-only equivariance is insufficient even for property prediction

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Ground truth check on implementation. From h-e1: Schürholt MNIST zoo loads, NFT processes it, Spearman ρ computes. Unified data loader functional. These are confirmed.

Dr. Sage's suggestion to check SVHN/CIFAR zoos is critical for feasibility. Schürholt zoo release includes multiple families. If SVHN/CIFAR use 3+ layer MLPs, we have immediate deeper-architecture experiments without additional data collection. Worth verifying before designing full experiment.

Implementation assessment:
- *Scaling canonicalization:* Divide each neuron's incoming weights by L2 norm, multiply outgoing weights by same factor. ~20 lines PyTorch.
- *Sign-flip canonicalization:* For each neuron, if majority of incoming weights negative, flip all incoming and outgoing weights simultaneously. O(N) per layer. ~30 lines. Well-defined for M=2; underdetermined for M>2.

**Feasibility verdict:** Both canonicalizations are 1-2 day implementations. 5-condition ablation runs on CPU in hours for MNIST zoo. Total: 2-3 days.

**Risk:** If NFT noise floor is ρ≈0.1, may lack statistical power to detect small improvements. Pre-specify minimum detectable effect size (Δρ ≥ 0.05) and verify zoo size gives sufficient power.

**Key Points:**
- Scaling canonicalization: ~20 lines, trivial
- Sign-flip canonicalization: ~30 lines, requires simultaneous layer-pair flips
- Verify SVHN/CIFAR zoo availability — free deeper-network experiments
- Pre-specify Δρ ≥ 0.05 minimum detectable effect

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion has converged on a strong, feasible hypothesis. Synthesis and strengthening:

**Core Claim:** Canonical preprocessing that removes scaling and sign-flip symmetry orbits from MLP weight vectors — before encoding with NFT — improves Spearman rank correlation with model properties on the Schürholt model zoo benchmark, relative to raw weight encoding.

**Mechanism:** NFT must implicitly learn to ignore scaling and sign-flip redundancy during training. Explicit canonicalization removes this redundancy, freeing encoder capacity to capture property-relevant geometric structure.

**Why this avoids h-e1's failure:** Uses NFT (not DWSNets), operates on M=2 Schürholt MNIST zoo (no layer-count constraint violated), does not use `dataset_clf`.

**Predictions:**
- P1 (primary): Condition D (both canonicalizations) achieves Δρ ≥ 0.05 above Condition A (raw weights) on at least 2 of 3 Schürholt MNIST zoo tasks. Primary metric: accuracy.
- P2: Condition D > Condition E (random norm control) on at least 2 of 3 tasks (symmetry-specific effect confirmed).
- P3 (exploratory): If SVHN/CIFAR available, improvement from canonicalization ≥ MNIST improvement.

**Strengthening:** Frame canonicalization as encoder-agnostic — applicable to ANY equivariant encoder. Broader claim, more impactful if confirmed.

**Key Points:**
- NFT + canonicalization vs NFT alone — minimal, clean comparison
- Avoids DWSNets entirely (h-e1 failure) — M=2 compatible
- P1 gate: Δρ ≥ 0.05 on accuracy task
- Encoder-agnostic framing broadens contribution

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Three concerns before finalization:

**Concern 1 — Statistical power:** NFT baseline ρ=0.11 is low. With ~50k models, power should be sufficient for Δρ=0.05, but bootstrap CIs must be computed on the baseline before committing to the threshold. If 95% CI spans Δρ > 0.05 already, the test has resolution.

**Concern 2 — Normalization confound:** Condition E addresses this partially, but a stronger confound: layer normalization on weights might improve optimization of the downstream linear regressor independent of symmetry. Mitigation: use frozen pre-trained NFT (no fine-tuning on canonicalized inputs); only train final regressor. If improvement persists with frozen encoder, canonicalized inputs are intrinsically more informative.

**Concern 3 — Sign-flip underdetermination for M>2:** For a 2-layer network, only one consecutive layer pair exists — sign-flip canonicalization is well-defined. For M>2, greedy layer-by-layer approach is not globally canonical. For MNIST zoo (M=2), problem is well-defined; flag M>2 extension as future work.

**Mitigation Strategy:**
1. Bootstrap ρ CIs on baseline before experiment commitment
2. Run frozen NFT encoder variant alongside fine-tuned variant
3. Scope sign-flip to M=2 (MNIST zoo) explicitly; flag M>2 as future work
4. Add Condition F: canonicalization applied to flat_mlp baseline (no equivariant encoder) — tests encoder-specificity

**Key Points:**
- Bootstrap ρ CIs mandatory before experiment commitment
- Frozen encoder test separates symmetry effect from optimization effect
- Sign-flip for M=2 well-defined; M>2 is future work
- Condition F (flat_mlp + canonicalization) tests encoder-specificity

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's frozen encoder suggestion is elegant — cleanly separates "canonical inputs are more informative" from "NFT trains better on canonical inputs." Both are valid claims; we should test both.

Pushing on novelty further: the core contribution as framed ("canonicalization improves NFT property prediction") is useful but narrow. The more interesting framing: **property-relevant information in model zoo weights is geometrically concentrated in the symmetry-reduced canonical representation.** This is a geometric claim about where property signal lives in weight space.

Additional experiment to make this geometric claim concrete: after canonicalization, compute PCA of canonical weight vectors and show property labels correlate more strongly with first few principal components than raw weight PCA. ~10 lines, runs alongside other conditions, provides mechanism-level evidence independent of encoder performance.

This also addresses "your improvement might be task-specific" reviewer concern: if PCA concentration holds across all 3 tasks, it suggests universal geometric property of model zoo weight spaces.

Propose **Condition G:** PCA on canonical vs. raw weights, R² with property labels.

**Key Points:**
- Geometric claim (canonical representations concentrate property signal) is more novel than ρ improvement alone
- PCA experiment (Condition G) costs ~10 lines, provides mechanism-level evidence
- Cross-zoo (P3) depends on SVHN/CIFAR availability — verify
- Combined: predictive evidence (ρ improvement) + geometric evidence (PCA concentration) = strong paper

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Incorporating all refinements. Assessing convergence against all 6 criteria:

**SPECIFIC — Core Claim:** Under the Schürholt MNIST model zoo (2-layer MLP, ~50k models), if weight vectors are canonicalized to remove scaling and sign-flip symmetry orbits before encoding with NFT, then Spearman ρ with model properties (accuracy, gen_gap, lr_recovery) increases by Δρ ≥ 0.05, because canonical representations concentrate property-relevant geometric information by eliminating symmetry-induced variance. ✅

**MECHANISM:** (1) Raw weights contain within-orbit variance from scaling/sign-flip symmetries — functionally irrelevant but geometrically present; (2) NFT must implicitly learn to ignore this variance, reducing capacity for property-predictive features; (3) Canonicalization collapses orbits to canonical representatives, concentrating property-relevant information. Evidence: Condition G (PCA concentration) tests mechanism directly. ✅

**PREDICTIONS:** P1 (Δρ ≥ 0.05, primary, at least 2/3 tasks), P2 (Condition D > Condition E), P3 (deeper zoos show larger improvement, conditional). ✅

**NOVELTY:** First empirical measurement of scaling+sign-flip contribution to property prediction. First demonstration that symmetry canonicalization improves equivariant encoder performance. Encoder-agnostic preprocessing. ✅

**FEASIBILITY:** NFT codebase confirmed working. Schürholt MNIST zoo loads. Canonicalization: 50-60 lines. Full experiment on CPU in hours. ✅

**OBJECTIONS ADDRESSED:** Statistical power (bootstrap CIs), normalization confound (frozen encoder test, Condition E), sign-flip underdetermination (scoped to M=2), encoder-specificity (Condition F), mechanism directness (Condition G). ✅

**Convergence judgment: ALL 6 CRITERIA MET. Discussion CONVERGED at Exchange 8.**

**Key Points:**
- All 6 convergence criteria satisfied
- 7-condition experiment (A-G) provides clean causal attribution
- Hypothesis is fully specified, falsifiable, immediately testable
- Ready for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The geometric claim — property-relevant information concentrates in the symmetry-reduced canonical representation — is genuinely novel. Prior work on NFN/DWSNets characterized symmetry groups theoretically but never measured their contribution empirically via a preprocessing ablation. The PCA concentration sub-experiment (Condition G) makes this a mechanistic finding, not just an engineering improvement. The encoder-agnostic framing broadens the contribution scope significantly.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The 7-condition ablation (A raw, B scaling-only, C sign-flip-only, D both, E random-norm control, F flat_mlp+canon, G PCA-concentration) provides clean causal attribution. P1 is quantitative (Δρ ≥ 0.05), P2 isolates the symmetry-specific effect from normalization artifact, and the frozen-encoder variant separates representation quality from optimization dynamics. Bootstrap CIs on Spearman ρ ensure statistical validity.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The theoretical framing — full symmetry group (permutation × scaling × sign-flip) vs. permutation subgroup — questions the completeness of the dominant NFN/DWSNets paradigm. Even if the MNIST improvement is modest in absolute terms, demonstrating that permutation-only equivariance leaves measurable prediction accuracy on the table is theoretically important with broad implications for weight space encoder design.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation is realistic. Scaling canonicalization (~20 lines), sign-flip canonicalization for M=2 (~30 lines), 7-condition experiment, bootstrap CI computation — all achievable in 2-3 days. Schürholt MNIST zoo and NFT codebase confirmed working. No new data collection required. CPU runtime: hours. M=2 scope restriction sidesteps the underdetermination issue cleanly.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **SymCanon-WSL: Symmetry Canonicalization for Weight Space Property Prediction.**

Under the Schürholt model zoo benchmark (MNIST MLP zoo, 2-layer networks, ~50k models), if MLP weight vectors are canonicalized to remove scaling and sign-flip symmetry orbits before encoding with a permutation-equivariant encoder (NFT), then Spearman rank correlation with held-out model properties (test accuracy, generalization gap, learning rate recovery) increases by Δρ ≥ 0.05 relative to raw weight encoding, because canonical representations concentrate property-relevant geometric information by eliminating symmetry-induced variance that dilutes the prediction signal.

The causal mechanism: (1) raw weights contain within-orbit variance from scaling/sign-flip symmetries — functionally irrelevant but geometrically present; (2) NFT must allocate capacity to learn implicit invariance to this variance, reducing capacity for property-predictive features; (3) explicit canonicalization collapses orbits to canonical representatives, concentrating property-relevant information and freeing encoder capacity.

The 7-condition ablation provides clean causal attribution. Primary prediction P1: Condition D achieves Δρ ≥ 0.05 above Condition A on at least 2/3 tasks. P2 tests symmetry-specificity (D > E). P3 tests cross-zoo generalization (exploratory). Condition G (PCA concentration) provides mechanism-level geometric evidence.

This hypothesis avoids all known failure modes from h-e1: uses NFT (not DWSNets), operates on M=2 Schürholt MNIST zoo (no layer-count constraint violated), does not use `dataset_clf`.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- NFT baseline ρ=0.11 leaves limited room; bootstrap CI check mandatory before committing to Δρ ≥ 0.05 threshold
- Sign-flip canonicalization scoped to M=2; M>2 extension requires additional algorithm design (future work)
- Frozen-encoder experiment must be included to distinguish representation quality from optimization dynamics
- SVHN/CIFAR zoo availability unverified — P3 flagged as exploratory
- **Mitigation Strategy:** Execute bootstrap CI check first (day 1); if CI too wide, reconsider threshold or switch to RMSE metric. Run frozen-encoder variant alongside fine-tuned. Explicitly scope sign-flip to M=2 in write-ups. Flag P3 as exploratory.
