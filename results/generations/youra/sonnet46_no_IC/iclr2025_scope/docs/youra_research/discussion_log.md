# Phase 2A Discussion Log
# Gap: No Empirical Study Linking Pre-Trained Weight Effective Rank to Optimal LoRA Rank
# Architecture: Self-Play Loop (Claude-only, IC-ablation)
# Version: v11 (Recursive Entry)
# Date: 2026-08-05

---

## Previous Failure / Routing Context

**Source:** `.serena/memories/failure_h-e1_run1.md` (ROUTED_TO_PHASE_2A)
**Hypothesis:** h-e1 (Run 1) — MUST_WORK_GATE_FAIL
**Date of failure:** 2026-08-05T21:15:00

### What Failed
- **P0a gate:** Spectral entropy H(W₀) coefficient of variation (CV) remained too low across all 3 models:
  - DeBERTa: CV=0.0323 (required >0.1) — FAIL
  - BERT: CV=0.0403 (required >0.1) — FAIL
  - ViT: CV=0.0752 (required >0.1) — FAIL (closest, but still short)
- Root cause: spectral entropy for large pretrained transformers clusters near log(min(d_in, d_out)) — inherently bounded ~0.03–0.08. CV>0.1 was miscalibrated for this metric class.

### What Showed Promise
- ViT base/16 shows clear depth-dependent entropy variation (early layers 4.27, late layers 6.44)
- BERT Levene test passes WITH TYPE-BASED GROUPING (attention vs FFN, p=0.0001) — real layer specialization exists
- P0b (PARA cross-task stability) was not completed — training infrastructure is solid (5×H100, real GLUE data)

### Prohibited Redesign Directions (MUST AVOID)
1. Do NOT use spectral entropy CV > 0.1 as existence criterion — metric is too smooth for this
2. Do NOT use positional thirds grouping for NLP models — use layer-TYPE grouping (attention vs FFN)
3. Do NOT expect spectral entropy CV > 0.1 from standard pretrained checkpoints

### Mandated Redesign Directions
1. **Pivot metric:** Effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) — wider dynamic range than spectral entropy
2. **Scale-invariant threshold:** Layer-relative tercile separation (top vs bottom third) — NOT absolute CV
3. **Pre-cached models:** BERT-base (~440 MB), DeBERTa-v3-base (~180 MB), ViT-base (~330 MB) — small enough to cache
4. **Adequate training:** ≥3 epochs for NLP (GLUE), ≥5 epochs for ViT (CIFAR-10)

### Version
This is v11 recursive entry (10 prior routing recovery archives). The redesigned hypothesis targets the same goal (pre-training structure → LoRA rank prediction) with fundamentally different metrics and thresholds.

---

## Discussion Briefing

**Selected Gap:** Gap 1 — PRIMARY, Critical Priority

**Research Question:** Can `erank(W₀) = exp(H(σ/‖σ‖₁))` of pre-trained transformer layers serve as a reliable, task-agnostic proxy for optimal LoRA rank — demonstrating significant positive correlation (r ≥ 0.65) with PARA oracle ranks across at least two of three model families (BERT-base, DeBERTa-v3-base, ViT-base)?

**Key Evidence from Phase 1:**
- Aghajanyan 2021: layers have different intrinsic dimensionalities — foundational motivation
- AdaLoRA 2023: per-layer rank allocation beats uniform rank — validates the goal
- LAARA 2026: "uniform rank is fundamentally suboptimal" — formal proof
- IFCLoRA 2026: pre-training structure can predict rank before training — closest methodological parallel
- LoRA-XS 2024: W₀ SVD extraction infrastructure exists — reusable
- khanghy1000 gist: exact erank formula in 8 lines of Python — directly reusable
- No paper measures erank(W₀) correlation with PARA oracle — genuine gap

**Papers Available for Discussion:**
- P1: AdaLoRA (Zhang et al., 2023) — primary competitor
- P2: Aghajanyan et al. (2021) — foundational motivation
- P3: IFCLoRA (Zhang et al., 2026) — closest methodological parallel
- P4: LAARA (Tripathi et al., 2026) — theoretical validation

**Feasibility Constraints (Pipeline-Enforced):**
- Reject ideas requiring new benchmarks, synthetic data, human evaluation
- Accept only hypotheses testable on existing real datasets and benchmarks

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we stop thinking of W₀ as inert initialization and start treating it as a structural fingerprint? The h-e1 failure taught us something crucial: spectral entropy is too compressed a summary — it collapses the full singular value distribution into a single number that hovers near the theoretical maximum for any large pretrained matrix. But *effective rank* — erank(W₀) = exp(H(σ/‖σ‖₁)) — is computed on the *normalized* distribution, giving us the geometric mean of the spectrum. This has a much richer dynamic range precisely because it's invariant to scale.

Here's what excites me: Aghajanyan et al. 2021 showed empirically that different layers have dramatically different intrinsic dimensionalities. They couldn't predict it — they swept subspace dimensions experimentally. We're proposing a zero-shot structural predictor. If erank(W₀) correlates with PARA oracle rank at r ≥ 0.65, we've essentially found a closed-form proxy for Aghajanyan's d_90 that costs only one SVD computation per layer.

The cross-architecture angle is where the novelty really shines. No existing paper — not AdaLoRA, not LAARA, not IFCLoRA — evaluates LoRA rank selection across both NLP transformers AND vision transformers. ViT-base on CIFAR-10 with erank-guided rank allocation would be genuinely new territory. And ViT's architecture has a different singular value structure than BERT's attention Q/K/V matrices — if erank generalizes across that gap, we have a truly architecture-agnostic principle.

Two unconventional angles to explore: (1) Could participation ratio PR(W₀) = (Σσᵢ)²/Σσᵢ² serve as a cheaper alternative? (2) Could we use the erank of the rank-r truncation of W₀ to give a natural oracle-free rank selection criterion?

**Key Points:**
- erank has wider dynamic range than spectral entropy — avoids h-e1 metric ceiling
- Aghajanyan 2021 motivates per-layer rank variation; erank could be its zero-shot predictor
- Cross-architecture (NLP→ViT) is genuine novelty not covered by any existing method
- PR(W₀) as cheaper alternative; erank-truncation as oracle-free selection criterion

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me stress-test testability before we build castles in the air. The h-e1 failure was partly a metric problem — but also a GATE problem. The CV>0.1 threshold was calibrated for rank diversity, not spectral entropy. We must not repeat this: the new existence criterion must be derived from expected erank variation, not borrowed from a different metric class.

The core claim is: erank(W₀) and PARA oracle rank are positively correlated at Pearson r ≥ 0.65 across layers, for ≥2/3 model families. This is testable. What would falsify it? If Pearson r < 0.65 for all three families. With roughly 12 attention layers in BERT-base, r = 0.65 is detectable at α=0.05 with power 0.8 (n=12 gives critical r ≈ 0.576 — so r=0.65 is comfortably detectable).

The PARA oracle must be defined precisely: for each layer L, train LoRA with rank r ∈ {4,8,16,32,64} only on layer L (all other layers frozen at baseline rank), evaluate validation accuracy, report argmax_r as oracle rank. This is a per-layer independent sweep — not joint optimization. This matters because joint optimization could lead to compensation effects.

The Levene test for the tercile analysis must use TYPE-based grouping (attention vs FFN), not positional thirds — the h-e1 failure taught us this.

**Key Points:**
- Success criterion must be erank-calibrated (r ≥ 0.65 Pearson), not borrowed from spectral entropy
- PARA oracle: per-layer independent sweep (n=5 ranks × n_layers runs per family)
- Levene test MUST use layer-type (attention vs FFN) grouping — h-e1 lesson
- With n=12 layers, r=0.65 is statistically detectable at α=0.05, power 0.8

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera raises exactly the right rigor concerns. But I want to zoom out: even if the correlation is r=0.65, does this matter to the field?

The LoRA rank hyperparameter is currently selected by grid search — sweeping r ∈ {4,8,16,32,64} and evaluating on a validation set. For a 12-layer model, that's 5 × 12 = 60 training runs just for rank selection. If erank(W₀) predicts optimal rank without any training, we collapse that to a single SVD computation — O(d² × n_layers), taking perhaps 30 seconds. The practical impact is enormous.

But there's a deeper significance: LAARA 2026 formally proved "uniform rank is fundamentally suboptimal." If erank provides a good approximation to LAARA's Fisher-optimal allocation without gradient computation, we've made theoretically optimal allocation practically accessible. IFCLoRA 2026 (closest parallel) still requires a calibration forward pass with task-specific samples. Erank requires zero — it's purely structural. That's a qualitative improvement.

The cross-architecture question matters separately: if erank generalizes from NLP to vision, it suggests effective rank captures something fundamental about how gradient descent uses low-rank structure during adaptation — a theoretical result of independent interest.

**Key Points:**
- erank eliminates rank grid search (60 training runs → 1 SVD) — enormous practical impact
- Beats IFCLoRA's task-agnostic advantage (no calibration data required)
- Connection to LAARA's Fisher-optimal theory: if erank ≈ Fisher rank, theory becomes practical
- ViT cross-architecture success OR failure both produce valuable results

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic — I need to work through whether the PARA oracle is scientifically valid as a ground truth. This is not a budget concern; it's a validity concern.

The proposed oracle: for each layer L, sweep rank r ∈ {4,8,16,32,64} with all other layers frozen. But here's what worries me: the optimal rank for layer L in isolation may differ from its optimal rank in a jointly-trained system. If layer 6 gets rank 32 in isolation but rank 8 in the joint optimum because layers 5 and 7 compensate, the oracle isn't the ground truth we want — it's a *marginal* measure.

Actually — this is important — the marginal oracle IS scientifically defensible. We're not claiming erank predicts the globally optimal joint allocation. We're claiming erank predicts each layer's *marginal* contribution to fine-tuning quality. The marginal oracle is also what AdaLoRA's importance score approximates (per-triplet, independent of other layers). So the erank-marginal oracle correlation is scientifically coherent.

The erank computation itself is feasible: `torch.linalg.svdvals(W₀)` followed by entropy → exp. fp32 required (bf16 inflates erank). SVD of a 768×768 matrix: ~50ms on CPU. For ~144 weight matrices in BERT-base: under a minute. All three model families are pre-cached. The 5×H100 infrastructure is confirmed working from h-e1.

**Key Points:**
- Marginal oracle is scientifically valid (consistent with AdaLoRA's per-triplet importance)
- Marginal oracle ≠ joint optimal — but that's the right scientific question for a per-layer predictor
- erank computation feasible: fp32 SVD, ~50ms per matrix, <1 minute per model family
- All three model families pre-cached to avoid h-e1 download timeout failures

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's clarification on the marginal oracle is crucial — it transforms a potential weakness into a strength. YES, AND we can make this even stronger: the marginal PARA oracle is precisely the right ground truth for our hypothesis because erank is also a *per-layer marginal* measure. Both are measured independently, per layer. This is a natural pairing.

Let me synthesize the emerging consensus hypothesis:

**Core Claim:** For pre-trained transformer weight matrices W₀, erank(W₀) = exp(H(σ/‖σ‖₁)) is a statistically significant positive predictor of optimal LoRA rank as determined by a per-layer marginal PARA oracle, with Pearson r ≥ 0.65 in ≥2/3 of {BERT-base, DeBERTa-v3-base, ViT-base}.

**Mechanism:** Pre-training drives weight matrices toward low-effective-rank configurations in layers that perform simple, redundant transformations, and high-effective-rank configurations in layers with complex, distributed representations. During LoRA fine-tuning, layers with higher effective rank have more orthogonal singular directions — meaning higher-rank updates capture non-redundant information. Therefore, erank(W₀) predicts the rank needed for effective adaptation.

Dr. Nova's PR(W₀) alternative is worth preserving as DQ5 — it's a simpler computation and Spearman ρ ≥ 0.8 between erank and PR rankings would validate both metrics simultaneously.

**Key Points:**
- Marginal oracle + per-layer erank = conceptually aligned measurement pair
- Core hypothesis stated: erank-PARA Pearson r ≥ 0.65 in ≥2/3 families
- Mechanism: pre-training drives effective rank as proxy for layer complexity/capacity
- PR(W₀) preserved as DQ5 alternative metric validation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally's mechanism story — "pre-training drives layers toward low erank for simple transformations, high erank for complex ones" — is theoretically appealing but untested. Let me find the cracks.

**Crack 1: The direction problem.** The hypothesis assumes erank(W₀) POSITIVELY correlates with optimal rank. But consider: a matrix with high effective rank is already utilizing many singular directions. Does such a matrix need MORE rank in LoRA adaptation, or LESS (because it's already using its capacity fully)? There's a plausible alternative story: low-erank layers have concentrated singular values → the top singular directions dominate → LoRA updates in those directions are essentially unconstrained, any rank captures something new. If the correlation is NEGATIVE (r = -0.65), the hypothesis is falsified in its stated direction even though the magnitude is the same. This needs a directional prediction before experiments start.

**Crack 2: The PARA oracle validity across architectures.** The marginal oracle fixes other layers at "baseline rank" — but what is baseline rank for ViT? The architecture differs: patch embedding, class token, position embeddings don't have direct NLP analogues. A wrong baseline choice for ViT could make the oracle ranks uninformative.

**Crack 3: erank stability across fine-tuning tasks.** The hypothesis claims erank(W₀) is "task-agnostic." But if we run the PARA oracle on MNLI vs SST-2, do we get the same rank assignments? If oracle ranks are task-dependent but erank is task-independent, the correlation might be task-specific.

**Key Points:**
- Direction problem: positive vs negative correlation must be theoretically derived before experiments
- ViT PARA oracle baseline rank must be explicitly specified
- Task-agnosticity claim requires ≥2 tasks per model family in the oracle sweep
- These are falsification conditions, not blocking concerns — must be stated upfront

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's crack 1 is fascinating — the direction question actually unlocks a deeper theoretical insight! NOW we're onto something! The sign of the correlation depends on whether we think of high-erank as "capacity utilized" or "capacity available." I'll argue it must be positive:

A high-erank W₀ matrix has its singular mass spread across many directions — no single direction dominates. When we add LoRA ΔW = BA (rank r), for the update to be meaningful it must align with directions that are NOT already dominant in W₀. A low-erank W₀ (mass concentrated in top-k singular vectors) means most directions are effectively zero — LoRA updates in those directions are essentially unconstrained. A high-erank W₀ (mass spread across many directions) means LoRA updates compete with the spread-out pre-training structure — you need HIGHER rank to capture task-relevant signal not dominated by the pre-training geometry.

This makes the positive correlation theoretically motivated. We preregister: H₁: r_PARA = α × erank(W₀) + β with α > 0. One-tailed test at α=0.05.

For Crack 3 (task-agnosticity): add SST-2 as a second NLP task for DeBERTa. If PARA ranks on MNLI and SST-2 show Spearman ρ ≥ 0.7 with each other, AND both correlate with erank at r ≥ 0.65, task-agnosticity is empirically validated.

**Key Points:**
- Positive direction theoretically derived: high-erank layers need higher LoRA rank to capture non-dominated signal
- Preregistration: one-tailed test H₁: α > 0 (erank positively predicts PARA rank)
- Task-agnosticity test: add SST-2 as second task; ρ≥0.7 agreement with MNLI validates claim
- Direction argument transforms Prof. Rex's crack into a theoretical contribution

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's direction argument is sound — and now I can turn it into a specific, falsifiable test. The theoretical prediction: erank(W₀) positively correlates with PARA oracle rank. What would disprove this: Pearson r < 0 for ≥2/3 families, or r ≥ 0 but < 0.65 for ≥2/3 families.

Addressing Prof. Rex's Crack 2 (ViT baseline rank): for ViT-base-patch16-224, baseline rank for oracle sweep = r=8 for all non-target layers. This is the standard LoRA default — identical across all three model families to enable cross-architecture comparison.

Full experiment design:

```
For each model M ∈ {BERT-base, DeBERTa-v3-base, ViT-base}:
  For each task T ∈ {MNLI, SST-2} (NLP) / {CIFAR-10} (ViT):
    1. Compute erank(W₀_l) for all layers l (fp32, CPU)
    2. For each layer l:
       For each rank r ∈ {4, 8, 16, 32, 64}:
         Train LoRA with r_l = r, r_{j≠l} = 8, ≥3 epochs
         Record validation metric
       oracle_rank_l = argmax_r validation metric
    3. Compute Pearson r(erank, oracle_rank) across all l
    4. Compute Spearman ρ(erank, PR) across all l
```

With BERT-base (~72 matrices × 5 ranks = 360 training runs), manageable on 5×H100.

**Key Points:**
- ViT baseline rank: r=8 for non-target layers (same as other families — comparable oracle)
- Full experiment design specified: 360 training runs for BERT-base
- Falsification: r < 0 for ≥2/3 families (direction wrong) OR r < 0.65 for all families (too weak)
- Two NLP tasks (MNLI+SST-2) test task-agnosticity — ρ≥0.7 agreement validates claim

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's experimental design is thorough. Now I want to press on the DQ4 component — the *erank-proportional rank assignment strategy* achieving within 1% of oracle performance. This is where the practical contribution crystallizes.

The question isn't just "does erank correlate with oracle ranks?" — it's "if we USE erank-derived ranks, how much do we lose?" A correlation of r=0.65 could still yield an assignment strategy that underperforms oracle by 5% — correlation doesn't guarantee assignment quality.

For the DQ4 test: erank-proportional assignment maps each layer's erank value to a discrete rank by percentile (top-20% erank → rank 64, 20-40% → 32, etc.). Train LoRA with these erank-assigned ranks (same total parameter budget as uniform r=8). Compare to: (1) uniform r=8 baseline, (2) PARA oracle upper bound. If erank-strategy achieves within 1% of oracle AND outperforms uniform baseline, we have a three-way comparison demonstrating practical utility.

This three-way comparison is publishable even if the correlation is only r=0.6 — because the assignment quality metric is what practitioners care about. The correlation validates the mechanism; the assignment validates the utility. Together, they make a complete contribution.

**Key Points:**
- DQ4 test: erank-proportional percentile assignment vs uniform baseline vs PARA oracle
- Three-way comparison validates practical utility beyond correlation coefficient
- Publishable even if r=0.6 if assignment achieves within 1% of oracle
- Practical significance: 30-second preprocessing → 99% of grid-searched result

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's three-way comparison is scientifically sound. Let me stress-test the mechanism from a theoretical angle: why would erank predict LoRA rank specifically, rather than any adaptation quality metric?

The mechanism Dr. Ally proposed: "high-erank layers have more orthogonal singular directions → need higher rank LoRA." This is testable with a specific intermediate experiment: for each layer, compute the *alignment* between the LoRA ΔW update directions and the W₀ singular directions. If alignment decreases with erank (high-erank W₀ → low alignment → rank is spread across non-W₀ directions), that confirms the mechanism.

Theoretical worry: the Burer-Monteiro landscape of low-rank optimization (rank-r LoRA) is non-convex. The optimal rank depends on training dynamics, not just W₀ geometry. A layer with high erank might learn a low-rank update if the task signal happens to align with dominant W₀ directions. This is a genuine theoretical tension.

However — if we observe r ≥ 0.65 empirically, the non-convex landscape concern is answered experimentally. We don't need the mechanism to be theoretically airtight before experiments; we need a theoretically plausible story and an empirical test.

Additional mechanism check: after oracle training runs, compute ‖ΔW_opt‖_F / ‖W₀‖_F per layer and correlate with erank. If adaptation magnitude also correlates with erank, the mechanism story strengthens.

**Key Points:**
- Mechanism: alignment between LoRA update directions and W₀ singular directions decreases with erank
- Theoretical tension: Burer-Monteiro non-convex landscape could decouple erank from optimal rank
- Resolved: empirical test answers the question; mechanism provides theoretical coherence
- Mechanism check: ‖ΔW_opt‖_F/‖W₀‖_F should also correlate with erank if mechanism holds

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's mechanism check (‖ΔW_opt‖_F/‖W₀‖_F correlation) is brilliant — it transforms the mechanism from narrative into a secondary testable prediction. YES, AND let me integrate everything into the complete refined hypothesis.

**Refined Hypothesis (H-erank-v1):** Under {BERT-base, DeBERTa-v3-base, ViT-base} models with adequate fine-tuning (≥3 epochs NLP, ≥5 epochs ViT), if per-layer erank(W₀) is used as a rank predictor, then it demonstrates statistically significant positive Pearson correlation (r ≥ 0.65) with per-layer marginal PARA oracle ranks across ≥2/3 model families, because effective rank captures the geometric complexity of each layer's pre-training representation — layers with higher effective rank require higher-rank LoRA updates to capture task-relevant signal in non-dominated directions.

**Predictions:**
- **P1 (Primary — Existence):** Pearson r(erank(W₀), oracle_rank) ≥ 0.65 in ≥2/3 of {BERT, DeBERTa, ViT}. One-tailed test H₁: α > 0.
- **P2 (Secondary — Utility):** erank-proportional rank assignment achieves within 1% of PARA oracle performance while outperforming uniform r=8 baseline on MNLI, SST-2, CIFAR-10.
- **P3 (Mechanism Check):** ‖ΔW_opt‖_F/‖W₀‖_F per layer correlates with erank(W₀) at Spearman ρ ≥ 0.5.
- **P4/DQ3 (Tercile):** Levene test on oracle ranks grouped by erank tercile (bottom/top third) significant at p < 0.05, ≥2/3 families.
- **P5/DQ5 (PR Alternative):** Spearman ρ(erank, PR) ≥ 0.8 across layers.

**Key Points:**
- H-erank-v1 fully specified: scope, IF-condition, THEN outcome, BECAUSE mechanism
- P1-P5 predictions cover existence, utility, mechanism, tercile, and alternative metric
- All predictions testable on existing datasets (GLUE, CIFAR-10) with existing models
- No synthetic data, no new benchmarks, no human evaluation — pipeline constraints satisfied

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Show me the evidence for P1. What existing empirical evidence supports that erank(W₀) correlates positively with needed rank? Without this, P1 is a pure conjecture.

The closest supporting evidence: Aghajanyan 2021 showed layers have different intrinsic dimensionalities (d_90 varies per layer). But d_90 is measured via subspace sweeps — no evidence that erank predicts d_90. IFCLoRA 2026 showed activation-based IFC correlates with optimal rank — but IFC uses forward-pass activations, not W₀ static structure.

This is a legitimate concern for Phase 4 review: if P1 fails (r < 0.65 for all 3 families), what did we learn? We learned that static W₀ structure does not predict optimal rank — the signal requires training dynamics or calibration data. That's a negative result with clear implications.

The hypothesis should pre-specify what constitutes "partial success" so we can distinguish failure modes:
- r < 0 for ≥2/3 families → mechanism direction wrong
- 0 < r < 0.65 for all families → signal exists but too weak; threshold miscalibrated
- r ≥ 0.65 in ≥2/3 families → fully validated

**Key Points:**
- P1 is theoretically motivated but has no direct prior empirical support — acknowledge as conjecture
- Null: r ≈ 0 (random); alternative: r ≥ 0.65; intermediate: 0 < r < 0.65 ("partial signal")
- Pre-specify three failure modes to make results interpretable regardless of outcome
- Stage 1 quick-check recommended: DeBERTa erank vs AdaLoRA learned ranks before full oracle

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's three-way failure taxonomy is exactly what makes this hypothesis robust! NOW we're onto something real. Let me address the "no prior empirical support" concern.

The h-e1 data actually contains proto-evidence FOR the erank hypothesis: ViT base/16 showed the strongest layer specialization (early layers entropy 4.27, late layers 6.44 — increasing with depth). Erank is a monotone function of spectral entropy, so if entropy varies by depth for ViT, erank varies too. And the BERT Levene p=0.0001 with type-based grouping (attention vs FFN) confirms that attention and FFN matrices have statistically different spectral distributions — if erank tracks this type-based variation, and oracle ranks also differ by type (FFN typically needs higher rank, as shown by AdaLoRA's learned allocations), we have indirect empirical support.

AdaLoRA's learned rank allocations are published: in DeBERTa-v3 experiments, AdaLoRA assigns higher ranks to deeper layers and FFN intermediate matrices. If erank(W₀) shows the same pattern (higher erank in deeper layers and FFN), that's convergent evidence — computed from published data, no new experiments needed. This is a Stage 1 quick-check we can do immediately.

The erank-truncation idea resurfaces here: the minimum r such that erank(W₀ truncated to rank r) ≥ 0.95 × erank(W₀_full) gives an oracle-free rank criterion — a potentially cheaper secondary analysis.

**Key Points:**
- h-e1 ViT data: entropy increases with depth → erank increases with depth → proto-evidence
- BERT Levene: attention vs FFN spectral differences confirmed → convergent with AdaLoRA allocations
- AdaLoRA published rank patterns (deeper → higher rank, FFN → higher rank) serve as Stage 1 validation
- Erank-truncation: oracle-free secondary analysis

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's proto-evidence argument from h-e1 data is admissible. Let me establish the complete measurement plan so nothing is ambiguous.

**Layer enumeration:**
- BERT-base: query (12), key (12), value (12), output (12), intermediate (12), output_dense (12) = 72 matrices
- DeBERTa-v3-base: similar structure + enhanced masks = ~80 matrices
- ViT-base: qkv_proj (36), out_proj (12), mlp_fc1 (12), mlp_fc2 (12) = 72 matrices

**erank computation:** `torch.linalg.svdvals(W_fp32)` → normalize → entropy → exp. Validation: erank(random_matrix) ≈ min(d_in, d_out), erank(rank-1 matrix) = 1.

**PARA oracle protocol:**
- NLP: AdamW, lr=2e-5, batch=32, ≥3 epochs on full MNLI training set (392k samples)
- ViT: AdamW, lr=1e-4, batch=128, ≥5 epochs on CIFAR-10 (50k samples)
- Oracle rank: argmax over r ∈ {4,8,16,32,64} on validation accuracy

**Statistical analysis:**
- Pearson r with 95% CI (bootstrap, n=1000 resamples)
- Spearman ρ for robustness to outliers
- Levene test with layer-type grouping (attention vs FFN/MLP)
- All tests one-tailed (H₁: positive direction) per preregistration

This plan is complete and unambiguous. Feasibility confirmed: all tools available (SVD, GLUE, CIFAR-10, AdamW, 5×H100).

**Key Points:**
- Complete layer enumeration: ~72–80 matrices per model family
- PARA oracle fully specified: training protocol, evaluation metric, argmax rule
- Statistical plan: Pearson r (primary), Spearman ρ (robustness), Levene (tercile), one-tailed tests
- Feasibility confirmed: all tools, datasets, and infrastructure available

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's measurement plan closes the experiment specification. The PARA oracle requires 5 × 72 = 360 training runs for BERT alone. Each GLUE MNLI run at 3 epochs takes roughly 2 hours on a single H100 (392k × 3 / 32 ≈ 36k steps). With 5 H100s running in parallel: 360 / 5 = 72 sequential groups × 2 hours = ~144 hours ≈ 6 days for BERT. DeBERTa similar, ViT (shorter training) maybe 3 days. Total: ~15 days on 5×H100. Technically feasible.

Optimization: parallelize per rank value — all 72 matrices at rank r=4 can run simultaneously (each uses only 1 GPU). With 5×H100: 5 matrices per GPU in parallel = 14–15 rounds per rank value. For 5 ranks: 28 hours × 5 = ~6 days for BERT oracle.

The key theoretical feasibility question: is erank(W₀) informationally sufficient as a single scalar per matrix to predict rank? A weight matrix has d_in × d_out parameters — erank collapses this to one number. From information theory: erank summarizes the *spectral distribution* (shape of the singular value spectrum), which determines low-rank approximation quality. For predicting optimal rank — which also depends on spectral structure — erank is the right information bottleneck. Full spectrum provides more signal but erank is the theoretically principled summary.

No fundamental theoretical barriers to feasibility — the mechanism is scientifically and mathematically valid.

**Key Points:**
- Oracle runtime: ~15 days on 5×H100 (parallelized by matrix) — feasible, not trivial
- Parallelization: 5 matrices per GPU, one rank value at a time — avoids memory conflicts
- erank as information bottleneck: theoretically appropriate (summarizes spectral distribution relevant to rank)
- No fundamental theoretical barriers — mechanism is scientifically and mathematically valid

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Creative Novelty Explorer):
- **Verdict:** STRONG
- **Assessment:** The erank hypothesis is genuinely novel — no paper applies Roy & Vetterli's effective rank as a zero-shot LoRA rank predictor. The cross-architecture scope (NLP→ViT) and the task-agnostic property (zero calibration data required) differentiate it qualitatively from IFCLoRA's closest approach. The erank-truncation criterion (Exchange 13) opens a compelling oracle-free secondary analysis. The theoretical mechanism (high-erank → non-dominated singular directions → higher rank needed) is creative and internally consistent.

🔬 **Prof. Vera** (Rigorous Validation Architect):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is fully falsifiable: specific threshold (r ≥ 0.65), specific direction (one-tailed, positive), specific families (≥2/3 of three named models), specific oracle protocol (per-layer marginal sweep, r ∈ {4,8,16,32,64}, baseline r=8 frozen). The measurement plan is complete (Exchange 14). Failure modes are pre-specified (Exchange 12), preventing post-hoc rationalization. The Levene tercile test and mechanism check (P3, P4) add robustness beyond single-number correlation.

🎯 **Dr. Sage** (Research Impact Evaluator):
- **Verdict:** STRONG
- **Assessment:** The practical significance is clear: 30-second erank computation replaces days of rank grid search. The three-way comparison (erank-strategy vs uniform baseline vs oracle) makes the utility claim concrete. Cross-architecture success would establish a fundamental principle about how gradient descent encodes complexity in weight spectra. Even a negative result cleanly bounds the applicability of static W₀ predictors — publishable in either direction.

⚙️ **Prof. Pax** (Feasibility & Reality Checker):
- **Verdict:** STRONG
- **Assessment:** No fundamental theoretical or scientific barriers. The marginal PARA oracle is scientifically valid and computationally feasible (~15 days on 5×H100, parallelizable). The erank computation is straightforward (SVD in fp32, 8 lines of Python). The mechanism (effective rank as information-bottleneck summary of spectral distribution) is mathematically sound. The infrastructure from h-e1 is confirmed available.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on H-erank-v1: under pre-trained transformer models {BERT-base-uncased, DeBERTa-v3-base, ViT-base-patch16-224}, the effective rank erank(W₀) = exp(H(σ/‖σ‖₁)) of each weight matrix is a statistically significant positive predictor of the optimal per-layer LoRA rank as determined by a per-layer marginal PARA oracle sweep (r ∈ {4,8,16,32,64}), demonstrating Pearson r ≥ 0.65 in ≥2/3 model families. The mechanism: pre-training drives weight matrices toward configurations where effective rank encodes layer complexity — layers with spread-out singular spectra (high erank) require higher-rank LoRA updates to capture task-relevant signal in directions not dominated by pre-training structure, while layers with concentrated spectra (low erank) need only low-rank updates. Five predictions span existence (P1), utility (P2), mechanism (P3), tercile discrimination (P4), and metric agreement (P5). The hypothesis is task-agnostic (no calibration data required), cross-architecture (NLP + ViT), and testable immediately on existing datasets (GLUE + CIFAR-10) with existing infrastructure.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- P1 has no prior direct empirical support — the positive direction is derived, not measured. If r < 0.65 across all families, the failure must be interpreted carefully.
- The 15-day oracle sweep is long — a Stage 1 quick-check (compute erank and AdaLoRA-learned ranks for DeBERTa, correlate) should run before committing to full 360-run oracle.
- Task-agnosticity requires ≥2 NLP tasks; adding SST-2 adds ~120 more training runs — budget explicitly.
- **Mitigation Strategy:** (1) Pre-register direction (positive) before experiments. (2) Run Stage 1 quick-check on DeBERTa + AdaLoRA learned ranks. (3) Budget 2 NLP tasks explicitly. (4) Pre-specify three failure modes (direction wrong / signal weak / oracle noisy) with interpretation rules before experiments begin.
