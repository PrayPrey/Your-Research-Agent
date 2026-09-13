# Phase 2C Context: H-M3

**Generated:** 2026-08-05 (JIT by Phase 2C Step 1)
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** H-M3
**Type:** MECHANISM (Step 3 of 3-step causal chain; implements H-P1 primary test)
**Gate:** MUST_WORK
**Prerequisites:** H-M1 (PASS), H-M2 (PASS / SUGGESTIVE)

**Statement:**
Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × GroupDRO and ERM), GroupDRO-trained layer4 features exhibit significantly lower background (land/water) linear decodability than ERM-trained layer4 features, measured as sklearn L-BFGS probe accuracy (C=1e9, no regularization) predicting group_array%2 from frozen layer4 features on the full Waterbirds WILDS test set, tested via one-sided paired t-test (p<0.05, n=3 seeds). Tiered criteria: CONFIRMED (p<0.05, d>0), SUGGESTIVE (p<0.10, d>0.5), REJECTED (wrong direction or p>=0.10, d<0.2).

**Rationale:**
This is the primary empirical test of the causal chain (H-M1 → H-M2 → H-M3). If GroupDRO backbone-level gradient propagation (H-M2) reduces background decodability, it must manifest as measurably lower probe accuracy at layer4.

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: Waterbirds WILDS
- Type: standard
- Source: WILDS benchmark (Koh et al. 2021) / izmailovpavel/spurious_feature_learning
- Path: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Background extraction: `background_label = group_array % 2` (0=land, 1=water)
- Test set: Full Waterbirds WILDS test set (N=5794 images, verified in H-M2)
- Hypothesis Fit: Canonical spurious correlation benchmark; background is spurious attribute; all 12 checkpoints trained/evaluated on this dataset

**Model:**
- Name: ResNet-50 (6 checkpoints: ERM×3 + GroupDRO×3 seeds; SAM×3 exploratory)
- Type: CNN feature extractor (backbone only, layer4 frozen)
- Source: izmailovpavel/spurious_feature_learning GitHub / HuggingFace Hub
- Cache: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints`
- Feature extraction: `model.layer4 → AdaptiveAvgPool2d(output_size=(1,1)) → flatten → D=2048`
- Hypothesis Fit: Layer4 is final backbone representation; D=2048 features; standard probing point per Alain & Bengio 2016

---

## Verification Protocol

1. Prerequisite: H-P0 PASS (DFR ≡ ERM backbone confirmed — verified).
2. For each seed in {1,2,3}: load GroupDRO and ERM checkpoints; model.eval() + torch.no_grad().
3. Forward pass FULL Waterbirds WILDS test set through `model.layer4 → AdaptiveAvgPool2d(1,1) → flatten → [N_test, 2048]` feature matrix.
4. Extract `background_label = group_array % 2` from WILDS metadata (0=land, 1=water).
5. Fit `sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)` on (features, background_labels); record `probe_acc = probe.score(features, background_labels)` per checkpoint.
6. Statistical test: `scipy.stats.ttest_rel(erm_accs, groupdro_accs, alternative='greater')`; compute `Cohen's d = (ERM_mean - GroupDRO_mean) / pooled_std`.
7. Exploratory H-P1b: repeat for SAM vs ERM; report direction and Cohen's d only.

---

## Success Criteria

- **CONFIRMED:** p < 0.05 one-sided AND Cohen's d > 0 (direction correct)
- **SUGGESTIVE:** p < 0.10 one-sided AND Cohen's d > 0.5
- **REJECTED:** GroupDRO mean ≥ ERM mean (wrong direction) OR p ≥ 0.10 with Cohen's d < 0.2
- Also verify: ERM mean probe acc > 0.6 (confirms metric discriminability — A2 validation)

**Note from H-M2:** ERM probe acc already measured as [0.8956, 0.8735, 0.8637], GroupDRO as [0.8830, 0.8680, 0.8595]. Paired t-test p=0.0526, Cohen's d=1.64 → SUGGESTIVE verdict in H-M2. H-M3 is the pre-registered formal test with full protocol.

---

## Continuation Context (from H-M2 Validation)

**Prior results (H-M2 FR-3, preliminary):**
- ERM probe accuracies (seeds 1-3): [0.8956, 0.8735, 0.8637]
- GroupDRO probe accuracies (seeds 1-3): [0.8830, 0.8680, 0.8595]
- SAM probe accuracies (seeds 1-3): [0.8804, 0.8616, 0.8759]
- Paired t-test p=0.0526, Cohen's d=1.64 → verdict SUGGESTIVE
- n_test_samples=5794

**Important:** H-M2 measured probe accuracy across all 12 checkpoints as part of FR-3. H-M3 is the formal pre-registered test of the same metric with full statistical analysis. The H-M2 result is a preliminary indication; H-M3 is the primary test.

**Shared setup (reuse from H-M2):**
- Same checkpoints (verified cache path)
- Same Waterbirds WILDS test set (N=5794)
- Same feature extraction protocol (layer4 → D=2048)
- Same probe hyperparameters (L-BFGS, C=1e9, max_iter=1000)

---

## Gate Assessment

- **Gate Type:** MUST_WORK
- **Current Status:** Not yet evaluated (IN_PROGRESS)
- **Prerequisites:** H-M1 (PASS), H-M2 (PASS/SUGGESTIVE)
- **If REJECTED:** Document as definitive negative (WGA improvement head-only); route to Phase 5
