# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-16T20:56:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1-gradient-norm-proxy
- **Gap Title**: Unexplored Use of Per-Sample Gradient Norm Magnitude as Label-Free Minority Group Proxy
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Pipeline Context**: Reflection 3 (ROUTE_TO_0) — two previous attempts: SAM/flatness FAIL, oscillation_index SUPERSEDED

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty), Prof. Vera (Falsifiability), Dr. Sage (Significance), Prof. Pax (Feasibility), Dr. Ally (Advocate), Prof. Rex (Critic)

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met — specific core claim, NHT-grounded mechanism, 3 testable predictions, label-free DFR novelty, confirmed-infrastructure feasibility, temporal/decomposition objections resolved as sub-experiments

### Key Insights
- **Gradient norm is a continuous minority proxy**: JTT uses binary misclassification; gradient norm (normalized by feature magnitude) captures borderline minority samples that are correctly classified but have elevated prediction error — a richer signal
- **NHT mechanism grounding**: The NHT framework (Khanh & Hoa, 2026) predicts minority samples RESIST the high-norm shortcut basin M_sc, producing persistently elevated gradient norms — this is shortcut resistance, not shortcut inflation
- **Label-free DFR framing**: The key insight from the discussion is the pivot from "better-than-JTT" to "label-free DFR" — the impact narrative is closing DFR's last annotation gap, not marginally improving JTT
- **Feature-norm normalization is critical**: Decomposition ||∇_W ℓ_i|| ∝ ||h(x_i)|| × ||p_i - y_i|| shows the signal must be normalized to isolate prediction error from feature scale effects

### Breakthrough Moments
1. Dr. Sage (Exchange 5): Pivoted from "vs JTT" framing to "label-free DFR" framing — correct impact narrative
2. Prof. Pax (Exchange 10): Decomposition of gradient norm into prediction error × feature scale → motivated normalization (g_tilde_i)
3. Prof. Rex (Exchange 13): Clarified NHT temporal mechanism — high-norm minority samples RESIST the shortcut, they are not driving it
4. Dr. Ally (Exchange 15): Per-epoch data (E1: 6.10 → E4: 14.73) shows INCREASING trend — supports resistance over inflation interpretation

---

## Final Hypothesis

### Title
**Gradient-Norm-Informed Last-Layer Retraining (GNR-LLR) for Label-Free Spurious Correlation Robustification**

### Hypothesis ID
H-GNR-LLR-v1

### Core Claim
Under ERM+SGD training on spuriously correlated image classification benchmarks (Waterbirds primary, CelebA secondary), if normalized per-sample last-layer gradient norms (g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)||) computed at early training epochs (T_id ∈ {3, 5}) are used to construct a pseudo-group-balanced subset (top-k% high-norm as pseudo-minority, bottom-k% low-norm as pseudo-majority) for ERM feature extractor freezing + classification head retraining (GNR-LLR), then worst-group accuracy (WGA) on Waterbirds will be ≥ 88% and on CelebA ≥ 82%, because minority-group samples that cannot be fit by the spurious-feature shortcut produce persistently elevated gradient norms (6–14x majority) reflecting structured-feature resistance under NHT norm-hierarchy dynamics.

### Mechanism
1. **Shortcut fitting (epochs 1–T_id)**: ERM learns spurious correlation → majority samples fit easily (low loss, low gradient norm) → minority samples cannot be fit by shortcut → residual |p_i - y_i| stays elevated → high gradient norm
2. **Signal normalization**: g_tilde_i = ||∇_W ℓ_i|| / ||h(x_i)|| isolates prediction-error component from feature-scale differences
3. **Pseudo-balance construction**: Top-k% high g_tilde_i → enriched for minority group → pseudo-group-balanced subset approximates DFR's balanced retraining set
4. **Head correction**: Freeze ERM features (already encode core features, per DFR) → retrain classifier head on pseudo-balanced subset → spurious head weighting corrected → high WGA

### Null Hypothesis (H0)
There is no significant difference in WGA between GNR-LLR and JTT on Waterbirds or CelebA. Gradient norm provides no additional actionable minority proxy information beyond JTT's binary misclassification.

---

## Predictions

### P1 (Primary): WGA ≥ 88% on Waterbirds
- **Test**: GNR-LLR at T_id=5, k=25%, last-layer retraining, λ=1e-4, 5 seeds
- **Success**: Mean WGA ≥ 88%, p < 0.05 vs. JTT (86.7%)
- **Failure**: Mean WGA ≤ 85% or indistinguishable from JTT

### P2: AUC Independence from Misclassification
- **Test**: AUC(g_tilde → minority group label) vs AUC(misclassification → minority group label) at T_id=5
- **Success**: AUC(g_tilde) > AUC(misclassification), DeLong test p < 0.05
- **Failure**: AUC(g_tilde) ≤ AUC(misclassification)

### P3: Temporal and Normalization Persistence
- **Test**: Normalized norm ratio at T_id=5 and at T_id=10 (post shortcut norm peak)
- **Success**: Ratio ≥ 3x at T_id=5; ≥ 1.2x at T_id=10
- **Failure**: Ratio < 1.5x at T_id=5 (feature scale only); or < 1.2x at T_id=10 (phase-locked)

---

## Novelty
GNR-LLR is the first published method using per-sample gradient norm magnitude for pseudo-group-balanced subset construction in DFR-style last-layer retraining without group label supervision:
- **vs. JTT**: continuous signal, principled T_id selection, NHT mechanism
- **vs. DFR**: eliminates group-annotated validation set — closes the last annotation gap in the DFR family
- **vs. LfF**: single-network approach (2x compute saving), no modified loss function
- **vs. LFR**: normalized gradient norm vs. raw loss magnitude — captures both prediction error and feature activation

---

## Experimental Design

| Component | Specification |
|-----------|--------------|
| Dataset | Waterbirds (primary, n_train=4795, n_test=5794); CelebA (secondary) |
| Model | ResNet-50 (ImageNet pretrained, confirmed working) |
| Stage 1 | Train ERM 20 epochs, log g_tilde_i at {1,3,5,10,20} epochs |
| Stage 2 | Freeze features, retrain last layer 100 epochs on pseudo-balanced subset |
| k sweep | {10%, 20%, 30%} of training data selected as pseudo-minority/majority |
| T_id sweep | {1, 3, 5, 10} epochs |
| λ sweep | {0, 1e-4 (primary), 5e-4} |
| Seeds | 5 seeds per condition |
| Primary metric | WGA = min(WGA_group0..3) on Waterbirds test set |
| Infrastructure | h-e1/code + gradient_analysis.py + evaluate.py (confirmed working) |

---

## Limitations
- Temporal window: signal requires early training epochs (1–10); later epochs lose disparity
- Pseudo-balance approximation: gradient norm induces approximate, not exact, group balance — ~5pp WGA gap vs. DFR expected
- CelebA validation deferred to secondary experiment (different group structure, validation needed)
- Per-sample gradient norms are O(N × d_head) per epoch vs. O(N) for JTT — modest additional overhead

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | 3 empirical sub-tests (E1: temporal, E2: balance, E3: CelebA) — all become Phase 2B sub-hypotheses |
| **Next Phase** | Phase 2B — decompose into H-E (existence), H-M (mechanism), H-C (condition) sub-hypotheses |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Pipeline: YouRA | Spurious Correlations & Shortcut Learning | Reflection 3*
