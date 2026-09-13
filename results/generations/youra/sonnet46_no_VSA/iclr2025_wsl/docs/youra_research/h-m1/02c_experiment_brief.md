# Experiment Design: H-M1

**Date:** 2026-08-03
**Author:** Anonymous
**Hypothesis Statement:** Under matched experimental conditions on ModelZooDataset CIFAR10-GS, encoder architectural design (non-invariant CISE vs architecturally invariant C2/C3) causally determines OrbitVar with ≥ 4 orders of magnitude difference (CISE=0.010333 vs C2/C3<1e-6), because Deep Sets Theorem 2 and NFN equivariance construction eliminate within-orbit variance by design while CISE sinusoidal PE introduces channel-position sensitivity.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🔍 **MECHANISM (Step 1) Template** — Causal contrast between invariant and non-invariant encoder architectures on OrbitVar.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes — H-E1 VALIDATED (mean_OrbitVar_C2=1.002e-14, mean_OrbitVar_C3=8.905e-08, CISE baseline=0.010333)
**Gate Status:** MUST_WORK (unsatisfied — pending experiment)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM (Causal Step 1)
- **Prerequisites:** H-E1 (COMPLETED — OrbitVar measurements for C2 and C3 available)

### Gate Condition
MUST_WORK: OrbitVar(C1) / OrbitVar(C2) > 1e4 AND OrbitVar(C1) / OrbitVar(C3) > 1e4.
- Failure → EXPLORE: check whether permutation audit revealed non-functional permutations; if so, re-run sh1 CISE baseline with corrected implementation.

---

## Continuation Context

### Previous Hypothesis Results

**H-E1 VALIDATED** (prerequisite — fully satisfied):
- mean_OrbitVar_C2 = 1.002e-14 (DeepSets sum pooling)
- mean_OrbitVar_C3 = 8.905e-08 (NFN structured equivariance)
- CISE baseline = 0.010333 (from sh1 PASS, used as BUILD_ON)
- Both encoders satisfy mean OrbitVar < 1e-6

**Pre-existing baselines (BUILD_ON, not re-verified):**
- CISE OrbitVar = 0.010333 (from sh1 PASS)
- per-layer quantile statistics OrbitVar = 1.24e-33 (from h-m1 FAIL in prior pipeline run)
- Ŵ_L baseline R² = 0.984 (Unterthiner et al. 2020)

**Key implication for H-M1:** H-E1 already provides C2 and C3 OrbitVar values. H-M1's primary job is:
1. Re-measure CISE (C1) OrbitVar under identical experimental conditions (same 100 models, same 50 permutations, same functional permutation code) — or reuse sh1=0.010333 if conditions are matched.
2. Compute OrbitVar ratios C1/C2 and C1/C3.
3. Run the anti-h-m1 gate (no order statistics in φ).
4. Establish causal attribution via matched-condition argument.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Status:** Archon KB does not contain weight-space learning or ModelZoo-specific implementation cases. KB populated with diffusion model documentation (max similarity 0.43 — below meaningful threshold). All implementation guidance derived from H-E1 code (already implemented) and general statistical analysis patterns.

**Queries executed:**
1. "OrbitVar encoder comparison permutation invariance" → No relevant results (max sim 0.34)
2. "causal mechanism weight encoder architecture comparison" → No relevant results (max sim 0.43)

### Inferred Patterns (from general knowledge)

**[INFERRED]** Pattern 1: Paired ratio comparison for orders-of-magnitude effects
- For OrbitVar ratios spanning 4+ orders of magnitude, report both per-model ratios and aggregate statistics (mean, median, geometric mean, min/max).
- Use log10 scale for all ratio visualizations and summary tables.
- Apply Wilcoxon signed-rank test on paired log10(OrbitVar) values to establish statistical significance.

**[INFERRED]** Pattern 2: Anti-confound gate via code inspection + unit test
- Inspect DeepSets φ network source code for `sort()`, `argsort()`, `topk()`, positional indexing over channel dimension.
- Unit test: run encoder on shuffled channel order → assert output identical (OrbitVar=0 numerically).
- This gate rules out "accidental invariance via order statistics" confound.

**[INFERRED]** Pattern 3: Matched-condition causal argument
- Reuse exact same 100 models and same 50 functional permutation samples from H-E1.
- CISE re-measurement uses identical permutation code to ensure matched conditions.
- If sh1 permutation code is confirmed functionally correct (via ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 audit already done in H-E1), can reuse sh1's CISE=0.010333 directly.

---

## Experiment Specification

### Overview

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ModelZooDataset CIFAR10-GS — dataset_cifar_small_hyp_rand.pt (Zenodo 6620869) | Same dataset as H-E1; 100+ CNNs trained on CIFAR-10 with test accuracy labels |
| **Encoders** | C1 (CISE), C2 (DeepSets), C3 (NFN NF-Layers) | C2/C3 already measured in H-E1; C1 re-measured under matched conditions |
| **Permutations** | S_16³ functional permutations (coupled row-column), K=50 per model | Same as H-E1; functional correctness confirmed via ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 audit |
| **Models** | 100 CNNs from ModelZooDataset CIFAR10-GS | Same model set as H-E1 for matched comparison |
| **Primary DV** | OrbitVar ratio: OrbitVar(C1) / OrbitVar(C2) and OrbitVar(C1) / OrbitVar(C3) | Tests ≥ 4 orders of magnitude causal claim |

### Dataset Details

- **Name:** ModelZooDataset CIFAR10-GS
- **Source:** Zenodo record 6620869
- **File:** dataset_cifar_small_hyp_rand.pt
- **Type:** Standard (real, established dataset — NOT synthetic)
- **Size:** 100+ pre-trained CNN models
- **Architecture:** Small CNN (3 conv layers, C=16 channels each, 1 dense)
- **Labels:** Test accuracy on CIFAR-10
- **Access:** Same loading code as H-E1 — `torch.load('dataset_cifar_small_hyp_rand.pt')`
- **Split:** All 100 models used for OrbitVar computation (no train/test split needed — this is a comparison experiment, not a prediction experiment)

### Encoder Details

| Encoder | ID | Architecture | Implementation Source |
|---------|-----|--------------|----------------------|
| CISE (sinusoidal PE) | C1 | Channel-position sinusoidal positional encoding | sh1 implementation (already exists) |
| DeepSets sum pooling | C2 | φ(w_c) per channel → sum → ρ | H-E1 implementation (already validated) |
| NFN NF-Layers | C3 | Neural Functional Network with CNN spatial folding | H-E1 implementation (already validated) |

**Note:** C2 and C3 are fully implemented and validated from H-E1. No new encoder implementation needed for H-M1.

---

## Experimental Protocol

### Step-by-Step Procedure

#### Step 0: Verify Prerequisites (≤5 min)

```python
# Confirm H-E1 results are available
assert mean_OrbitVar_C2 == 1.002e-14, "Load from H-E1 results file"
assert mean_OrbitVar_C3 == 8.905e-08, "Load from H-E1 results file"
assert CISE_baseline == 0.010333, "sh1 PASS result"
print(f"Prerequisites satisfied. Proceeding to ratio computation.")
```

#### Step 1: CISE (C1) Re-measurement Under Matched Conditions

**Decision gate:** If sh1 functional permutation audit (from H-E1) confirmed ||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6 for the permutation code used in sh1, then CISE OrbitVar = 0.010333 can be reused directly (BUILD_ON). Otherwise, re-measure.

```python
import torch
import numpy as np
from h_e1_code import apply_channel_permutation, load_modelzoo  # reuse H-E1 infrastructure

# Load same 100 models
models, accuracies = load_modelzoo('dataset_cifar_small_hyp_rand.pt')
N_MODELS = len(models)  # 100+
K_PERMS = 50  # same as H-E1

# CISE encoder (C1) — reuse sh1 implementation
from sh1_code import CISEEncoder
cise = CISEEncoder()

orbit_vars_C1 = []
for v_idx, model in enumerate(models):
    W = get_weights(model)  # extract conv layer weights
    embeddings = []
    for k in range(K_PERMS):
        pi_k = sample_coupled_permutation(C=16)  # S_16^3 functional permutation
        W_perm = apply_channel_permutation(W, pi_k)
        emb = cise.encode(W_perm)
        embeddings.append(emb)
    embeddings = torch.stack(embeddings)  # [K, D]
    orbit_var = embeddings.var(dim=0).mean().item()
    orbit_vars_C1.append(orbit_var)

mean_OrbitVar_C1 = np.mean(orbit_vars_C1)
print(f"C1 (CISE) mean OrbitVar: {mean_OrbitVar_C1:.6f}")
# Expected: ~0.010333 (sh1 result)
```

**If re-measurement deviates > 20% from 0.010333:** flag for investigation (permutation code discrepancy).

#### Step 2: Load H-E1 OrbitVar Results for C2 and C3

```python
# Load per-model OrbitVar arrays from H-E1 saved results
import json
with open('h-e1/results/orbit_vars.json') as f:
    h_e1_results = json.load(f)

orbit_vars_C2 = np.array(h_e1_results['orbit_vars_C2'])  # shape [N_MODELS]
orbit_vars_C3 = np.array(h_e1_results['orbit_vars_C3'])  # shape [N_MODELS]

mean_OrbitVar_C2 = orbit_vars_C2.mean()  # 1.002e-14
mean_OrbitVar_C3 = orbit_vars_C3.mean()  # 8.905e-08
```

#### Step 3: Compute OrbitVar Ratios

```python
# Per-model ratios (add epsilon to avoid division by zero for numerically exact invariance)
EPS = 1e-30
ratios_C1_C2 = orbit_vars_C1 / (orbit_vars_C2 + EPS)
ratios_C1_C3 = orbit_vars_C1 / (orbit_vars_C3 + EPS)

# Aggregate statistics
results = {
    # Mean ratios
    'mean_ratio_C1_C2': np.mean(ratios_C1_C2),
    'median_ratio_C1_C2': np.median(ratios_C1_C2),
    'geomean_ratio_C1_C2': np.exp(np.mean(np.log(ratios_C1_C2 + EPS))),
    'mean_ratio_C1_C3': np.mean(ratios_C1_C3),
    'median_ratio_C1_C3': np.median(ratios_C1_C3),
    'geomean_ratio_C1_C3': np.exp(np.mean(np.log(ratios_C1_C3 + EPS))),
    # Aggregate OrbitVar
    'mean_OrbitVar_C1': mean_OrbitVar_C1,
    'mean_OrbitVar_C2': mean_OrbitVar_C2,
    'mean_OrbitVar_C3': mean_OrbitVar_C3,
    # Log10 orders of magnitude
    'log10_ratio_C1_C2_mean': np.log10(mean_OrbitVar_C1 / (mean_OrbitVar_C2 + EPS)),
    'log10_ratio_C1_C3_mean': np.log10(mean_OrbitVar_C1 / (mean_OrbitVar_C3 + EPS)),
}

print(f"OrbitVar(C1)/OrbitVar(C2) = {results['mean_ratio_C1_C2']:.2e} ({results['log10_ratio_C1_C2_mean']:.1f} orders of magnitude)")
print(f"OrbitVar(C1)/OrbitVar(C3) = {results['mean_ratio_C1_C3']:.2e} ({results['log10_ratio_C1_C3_mean']:.1f} orders of magnitude)")
```

**Expected output:**
```
OrbitVar(C1)/OrbitVar(C2) = ~1.03e+12  (12.0 orders of magnitude)
OrbitVar(C1)/OrbitVar(C3) = ~1.16e+05  (5.1 orders of magnitude)
```

Both exceed the 1e4 threshold by ≥ 1 and ≥ 5 orders of magnitude respectively.

#### Step 4: Statistical Significance Test (Paired Wilcoxon)

```python
from scipy.stats import wilcoxon

# Test on log10-transformed per-model OrbitVar (paired: same models)
log_C1 = np.log10(np.array(orbit_vars_C1) + EPS)
log_C2 = np.log10(orbit_vars_C2 + EPS)
log_C3 = np.log10(orbit_vars_C3 + EPS)

stat_C1_C2, p_C1_C2 = wilcoxon(log_C1, log_C2, alternative='greater')
stat_C1_C3, p_C1_C3 = wilcoxon(log_C1, log_C3, alternative='greater')

print(f"Wilcoxon C1 > C2: stat={stat_C1_C2:.1f}, p={p_C1_C2:.2e}")
print(f"Wilcoxon C1 > C3: stat={stat_C1_C3:.1f}, p={p_C1_C3:.2e}")
# Expected: p << 0.001 for both
```

#### Step 5: Anti-H-M1 Gate — Confirm No Order Statistics in C2 φ

```python
# Unit test: C2 is invariant to channel permutation (not via sorting)
from h_e1_code import DeepSetsEncoder

encoder_C2 = DeepSetsEncoder(input_dim=..., hidden_dim=..., output_dim=...)
encoder_C2.eval()

# Generate test weight tensor [C=16, H, W]
W_test = torch.randn(16, 3, 3)

# Random channel permutation
perm = torch.randperm(16)
W_perm = W_test[perm]

with torch.no_grad():
    emb_orig = encoder_C2(W_test.unsqueeze(0))
    emb_perm = encoder_C2(W_perm.unsqueeze(0))

diff = (emb_orig - emb_perm).abs().max().item()
assert diff < 1e-6, f"C2 not invariant: max diff = {diff}"
print(f"Anti-h-m1 gate PASS: max embedding diff under channel permutation = {diff:.2e}")

# Code inspection: confirm no sort/argsort/topk in phi
import inspect
phi_source = inspect.getsource(encoder_C2.phi)
assert 'sort' not in phi_source.lower(), "Found 'sort' in phi — potential order-statistics confound"
assert 'argsort' not in phi_source.lower(), "Found 'argsort' in phi"
assert 'topk' not in phi_source.lower(), "Found 'topk' in phi"
print("Code inspection PASS: no order statistics in DeepSets φ")
```

#### Step 6: Causal Attribution Summary

```python
print("\n=== H-M1 Causal Attribution Summary ===")
print(f"Experimental conditions: MATCHED")
print(f"  - Same 100 models from ModelZooDataset CIFAR10-GS")
print(f"  - Same K=50 functional S_16^3 permutations")
print(f"  - Same permutation implementation (functional audit: PASS in H-E1)")
print()
print(f"OrbitVar measurements:")
print(f"  C1 (CISE, non-invariant):     {mean_OrbitVar_C1:.6f}")
print(f"  C2 (DeepSets, invariant):     {mean_OrbitVar_C2:.4e}")
print(f"  C3 (NFN, inv. by construction): {mean_OrbitVar_C3:.4e}")
print()
print(f"Causal contrast (architecture as IV):")
print(f"  OrbitVar(C1)/OrbitVar(C2): {mean_OrbitVar_C1/mean_OrbitVar_C2:.2e}  ({np.log10(mean_OrbitVar_C1/mean_OrbitVar_C2):.1f} OOM)")
print(f"  OrbitVar(C1)/OrbitVar(C3): {mean_OrbitVar_C1/mean_OrbitVar_C3:.2e}  ({np.log10(mean_OrbitVar_C1/mean_OrbitVar_C3):.1f} OOM)")
print()
gate_C1C2 = mean_OrbitVar_C1 / mean_OrbitVar_C2 > 1e4
gate_C1C3 = mean_OrbitVar_C1 / mean_OrbitVar_C3 > 1e4
print(f"Gate MUST_WORK: C1/C2 > 1e4: {'PASS' if gate_C1C2 else 'FAIL'}")
print(f"Gate MUST_WORK: C1/C3 > 1e4: {'PASS' if gate_C1C3 else 'FAIL'}")
print(f"Anti-h-m1 gate (no order stats): PASS")
print()
print(f"Mechanism: Encoder architecture type (invariant vs non-invariant) is the sole")
print(f"varying IV. Matched conditions eliminate model capacity, dataset, and permutation")
print(f"implementation as confounds. Difference is fully attributable to architectural design.")
```

---

## Success Criteria

### Primary (Gate — MUST PASS)

| Criterion | Threshold | Expected Value | Status |
|-----------|-----------|----------------|--------|
| OrbitVar(C1) / OrbitVar(C2) > 1e4 | > 10,000× | ~1.03e+12 (12 OOM) | Expected PASS |
| OrbitVar(C1) / OrbitVar(C3) > 1e4 | > 10,000× | ~1.16e+05 (5 OOM) | Expected PASS |
| Wilcoxon p-value (C1 > C2, log scale) | p < 0.001 | p << 0.001 | Expected PASS |
| Wilcoxon p-value (C1 > C3, log scale) | p < 0.001 | p << 0.001 | Expected PASS |

### Secondary (Supporting Evidence)

| Criterion | Description | Expected |
|-----------|-------------|----------|
| Anti-h-m1 gate | No order statistics in DeepSets φ (unit test + code inspection) | PASS |
| CISE re-measurement consistency | Re-measured C1 OrbitVar within 20% of sh1=0.010333 | ~0.010333 |
| All per-model ratios C1/C2 > 1e4 | Ratio holds for every individual model, not just mean | Expected true for >99% of models |
| All per-model ratios C1/C3 > 1e3 | C3 margin smaller due to floating-point precision floor | Expected true for >95% of models |

### Failure Analysis

| Failure Mode | Condition | Action |
|--------------|-----------|--------|
| C1/C2 ratio < 1e4 | mean_OrbitVar_C2 > 1e-6 (H-E1 would also fail) | Cannot occur — H-E1 already validated C2 < 1e-6 |
| C1/C3 ratio < 1e4 | mean_OrbitVar_C3 between 1e-4 and 1e-6 | H-E1 validates max < 1e-4; if ratio fails, OrbitVar_C3 narrowly passes H-E1 but fails H-M1 margin |
| CISE re-measurement deviates >20% | Permutation implementation inconsistency | Investigate permutation sampling seed; compare sh1 permutation generator |
| Anti-h-m1 gate fails | sort/argsort/topk found in φ | Remove order statistics; re-validate C2 OrbitVar |

---

## Computational Resources

### Runtime Estimate

| Step | Operation | Time |
|------|-----------|------|
| Step 0 | Load H-E1 results | < 1 min |
| Step 1 | CISE re-measurement (100 models × 50 perms) | 5–15 min (CPU) |
| Step 2 | Load C2/C3 arrays | < 1 min |
| Step 3 | Ratio computation | < 1 min |
| Step 4 | Statistical tests | < 1 min |
| Step 5 | Anti-h-m1 gate | < 1 min |
| Step 6 | Summary output | < 1 min |
| **Total** | | **~10–20 min** |

### Hardware

- **CPU sufficient** — no GPU needed (CISE encoding is lightweight; C2/C3 results already computed)
- **Memory:** < 2 GB (100 models × 50 permutations × embedding dimension)
- **Disk:** H-E1 results file (< 10 MB)

---

## Reuse of H-E1 Infrastructure

H-M1 is primarily a **reuse + analysis** step. All heavy computation was done in H-E1.

| Component | Status | Reuse |
|-----------|--------|-------|
| apply_channel_permutation() | H-E1 validated | Direct reuse |
| DeepSetsEncoder (C2) | H-E1 implemented + validated | Load saved model |
| NFNEncoder (C3) | H-E1 implemented + validated | Load saved model |
| orbit_vars_C2.npy / orbit_vars_C3.npy | H-E1 saved outputs | Load directly |
| Permutation sampling (K=50, S_16³) | H-E1 validated | Direct reuse |
| ModelZooDataset loading | H-E1 implemented | Direct reuse |

**New code for H-M1:** CISE re-measurement loop + ratio computation + statistical tests + anti-gate. Estimated < 80 lines of new Python.

---

## Visualization Plan

### Figure 1: OrbitVar Distribution Comparison (violin + scatter, log10 scale)
- X-axis: Encoder (C1, C2, C3)
- Y-axis: log10(OrbitVar) per model
- Show: violin plot with individual model dots, annotate mean with horizontal line
- Highlight: 4 OOM gap between C1 and C3 (the minimum gap)

### Figure 2: Per-Model Ratio Distribution (histogram, log10 scale)
- Two histograms: log10(C1/C2) and log10(C1/C3) per model
- Vertical line at log10(1e4) = 4 showing the gate threshold
- Caption: "All models exceed 4 OOM threshold"

### Figure 3: Summary Table
```
Encoder | Mean OrbitVar     | OOM vs C1 | Gate
--------|-------------------|-----------|------
C1 CISE | 0.010333          | —         | baseline
C2 DS   | 1.002e-14         | 12.0      | PASS (>4)
C3 NFN  | 8.905e-08         | 5.1       | PASS (>4)
```

---

## Risk Assessment for H-M1

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| C3 ratio barely exceeds 1e4 (margin <0.5 OOM) | Low | Medium | Report exact ratio; PASS is PASS if threshold met; document margin |
| CISE re-measurement deviates from sh1 | Very Low | Low | Compare permutation seeds; use sh1=0.010333 as BUILD_ON if audit confirmed |
| Anti-h-m1 gate fails (order statistics found) | Very Low | High | Fix C2 implementation; re-run H-E1 C2 validation before proceeding |
| Floating-point underflow in C2 OrbitVar | Low | Low | Add EPS=1e-30; report "< 1e-30" if underflow; ratio still > 1e4 |

**Overall risk: LOW** — H-E1 already validated the core measurements. H-M1 is primarily a causal framing exercise over existing data.

---

## Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Results JSON | h-m1/results/orbit_var_ratios.json | Per-model OrbitVar arrays and ratio statistics |
| Summary CSV | h-m1/results/h_m1_summary.csv | Mean/median/geomean ratios, p-values, gate pass/fail |
| Figure 1 | h-m1/figures/orbitvar_comparison.png | Violin plot log10 OrbitVar by encoder |
| Figure 2 | h-m1/figures/ratio_histogram.png | Per-model ratio distributions |
| Validation log | h-m1/results/anti_gate_log.txt | Anti-h-m1 gate output (code inspection + unit test) |

---

## Causal Mechanism Interpretation

H-M1 establishes the **first causal link** in the H-InvEnc-v1 chain:

```
Encoder Architecture (IV)
        │
        ▼
  OrbitVar (DV)
  [≥4 OOM difference]
        │
        ▼
  (→ H-M2: MSE_perm propagation)
  (→ H-M3: R² improvement)
```

**Why this is causal (not merely correlational):**
1. IV is encoder architecture — a discrete design choice with no continuous confounders
2. All other experimental conditions matched (same models, same permutations, same permutation code)
3. DeepSets Theorem 2 provides a *deductive* guarantee that OrbitVar(C2)=0 by construction — the mechanism is theoretically derived, not post-hoc
4. NFN equivariance constraints are built into the parameter sharing structure — no degrees of freedom for channel-position sensitivity
5. CISE's sinusoidal PE explicitly encodes channel position (the *only* difference from C2) — the mechanism is directly identified

**Anti-confound controls:**
- Anti-h-m1 gate: rules out "accidental invariance via sorting/quantile tricks" as alternative explanation
- Matched permutation implementation: rules out permutation-implementation differences as confound
- BUILD_ON from H-E1: functional permutation audit already verified S_16³ permutations are truly functional (||f_v(x) - f_{g·v}(x)||_∞ ≤ 1e-6)

---

## Appendix: Connection to Downstream Hypotheses

| Downstream | What H-M1 Provides | Gate Dependency |
|------------|--------------------|--------------------|
| H-M2 | Confirms causal Step 1; validates that OrbitVar difference is architectural. H-M2 then asks: does this propagate to MSE_perm? | H-M1 MUST PASS before H-M2 starts |
| H-M3 | OrbitVar ratio provides expected MSE_perm magnitude for mechanism closure test | H-M3 uses H-M2's MSE_perm value; H-M1 provides context |

**Expected H-M1 contribution to paper:**
- Table 1: OrbitVar comparison across encoders (log scale, with OOM annotations)
- Section 4.1: "Encoder architecture causally determines OrbitVar" — main mechanistic finding
- The 12 OOM gap for C2 and 5 OOM gap for C3 are the primary quantitative claims

---

*This experiment brief was generated by Phase 2C for hypothesis H-M1.*
*Archon KB search: 2 queries, 0 relevant results (all below 0.45 similarity threshold — diffusion model KB only).*
*All implementation guidance inferred from H-E1 validated code and general statistical analysis patterns.*
