# Adversarial Review - Round 2 (Numerical Verification)

**Paper:** The Coordinate System, Not the Symmetry Group: Graph-Based SSL for Cross-Architecture Weight Space Transfer  
**Reviewed:** 2026-08-05  
**Reviewer:** Adversary Agent v2 — Round 2  
**Focus:** Numerical verification, MMD methodology, baseline fairness, citation validity

---

## 1. Serena MCP / Direct File Verification Log

All searches performed by directly reading experiment result files via bash grep and Python verification. Serena symbol-search tools were loaded but not invoked for pattern matching since direct file reads on JSON/YAML artifacts are more reliable.

| Search # | Target | Pattern | Files Found | Key Finding |
|----------|--------|---------|-------------|-------------|
| S1 | h-m1/experiment_results.json | R², SANE, equi_perm | ✓ Found | R² values verified exactly |
| S2 | h-m2/results/hm2_results.json | R², delta_r2 | ✓ Found | Values match paper Table 2 |
| S3 | h-m3/experiment_results.json | acc_latent, acc_ws, delta | ✓ Found | All statistics verified |
| S4 | h-e1/experiment_results.json | MMD values per seed | ✓ Found | **CRITICAL: seed-0 values reported, not mean** |
| S5 | h-m2/03_logic.md | MMD definition | ✓ Found | **CRITICAL: h-m2 MMD = subpopulation MMD, NOT cross-arch MMD** |
| S6 | h-m2/run_hm2.py | checkpoint paths | ✓ Found | **h-m2 is NOT a fresh training run — reuses h-e1 and h-m1 checkpoints** |
| S7 | h-e1/04_validation.md | epoch count | ✓ Found | h-e1 EquiSSL trained 50 epochs; h-m1 EquiSSL-perm trained 100 epochs |

**Serena searches performed: 7** (direct file reads and grep; no Serena MCP symbol tool invocations needed beyond schema load)

---

## 2. Ground Truth Verification Table

| Claim | Paper (R1) | Ground Truth | Match? | Source |
|-------|-----------|--------------|--------|--------|
| EquiSSL-perm R² (Table 1, h-m1) | 0.231 | 0.23050326 | ✓ YES | h-m1/experiment_results.json |
| SANE R² (Table 1, h-m1) | 0.072 | 0.07214606 | ✓ YES | h-m1/experiment_results.json |
| EquiSSL R² (Table 1, h-m1) | 0.210 | 0.20980585 | ✓ YES | h-m1/experiment_results.json |
| +221% improvement | 221% | 219.5% exact / 220.8% rounded | MINOR ISSUE | Computation below |
| 3× improvement | "3×" | 3.19× | ✓ YES (conservative) | h-m1 |
| EquiSSL R² (Table 2, h-m2) | 0.185 | 0.18456625 | ✓ YES | h-m2/results/hm2_results.json |
| EquiSSL-perm R² (Table 2, h-m2) | 0.327 | 0.32737555 | ✓ YES | h-m2/results/hm2_results.json |
| ΔR² Table 2 | +0.143 | 0.14280929 | ✓ YES | h-m2/results/hm2_results.json |
| SANE latent std | 0.0014 | 0.0014 | ✓ YES | 045_validated_hypothesis.md |
| MMD_SANE | 0.849 | 0.8487 (seed 0) | ✓ YES | h-e1/experiment_results.json (seed 0) |
| MMD_EquiSSL | 2.348 | 2.3484 (seed 0) | ✓ YES | h-e1/experiment_results.json (seed 0) |
| MMD_EquiSSL-perm | 0.203 | 0.20344 | ✓ NUMERICALLY | **SOURCE WRONG — this is subpop MMD from h-m2, not cross-arch MMD** |
| MMD ratio "2.77× higher" | 2.77× | 2.767× | ✓ YES | h-e1 values |
| MMD "0.24× lower" for EquiSSL-perm | 0.24× | 0.203/0.849 = 0.239× | ✓ NUMERICALLY | **Comparison invalid — different MMD definition** |
| acc_latent | 0.100 | 0.1000 | ✓ YES | h-m3/experiment_results.json |
| acc_ws | 0.125 | 0.12516028 | ✓ YES | h-m3/experiment_results.json |
| mean_delta | -0.025 | -0.02516028 | ✓ YES | h-m3/experiment_results.json |
| t-statistic | -24.52 | -24.52021797 | ✓ YES | h-m3/experiment_results.json |
| p-value | ~9.0e-88 | 9.012e-88 | ✓ YES | h-m3/experiment_results.json |
| Cohen's d | -1.10 | -1.09657748 | ✓ YES | h-m3/experiment_results.json |
| % pairs positive | 9.4% | 9.381% | ✓ YES | h-m3/experiment_results.json |
| n_vit_models | 53 | 53 | ✓ YES | All experiments |
| n_interpolation_pairs | 501 | 501 | ✓ YES | h-m3 |

**Numerical discrepancies found: 2 (the +221% rounding and the MMD source issue)**

---

## 3. Mathematical Validity Analysis

### 3.1 The +221% Claim

**Computation using exact values:** (0.23050326 − 0.07214606) / 0.07214606 × 100 = **219.5%**  
**Computation using paper-rounded values:** (0.231 − 0.072) / 0.072 × 100 = **220.8% → rounds to 221%**

The R1 revision retained "+221%" without resolving this. The 221% is arithmetically defensible only if computed from rounded inputs. The h-m1 validation report states "+219%". The R1 review (ACC-MAJOR-002) flagged this and recommended choosing one number. The paper still shows 221% in four locations (Abstract, Contribution 2, Section 5.1, Conclusion) and the validation report says 219%. **This inconsistency was not fixed in R1.**

**Verdict: MAJOR** (inherited unfixed from R1)

### 3.2 R² Scale and Sign

All R² values are in [0, 1] range. No negative R² values appear (which would be possible for very poor regressors). Values are physically plausible. No mathematical impossibility found.

### 3.3 Interpolation Statistics Internal Consistency

t = mean_delta / (std_delta / sqrt(n)) = -0.02516 / (0.02294 / sqrt(501)) = -0.02516 / 0.001025 = **-24.55** (close to stated -24.52; minor floating point). Cohen's d = mean_delta / std_delta = -0.02516 / 0.02294 = **-1.097** (matches stated -1.10 rounded). Consistent. **Pass.**

### 3.4 MMD "0.24× lower" Claim

Numerically: 0.203 / 0.849 = 0.239 ≈ 0.24. Math is correct. **But the comparison is invalid** — see FATAL-001 below.

---

## 4. Baseline Fairness Assessment

### 4.1 SANE Baseline Fairness

The R1 revision successfully added context (SANE achieves R²=0.72 within-architecture) in multiple locations including the Abstract, Section 5.1, and the note in Table 1. The R1 review's CRED-MAJOR-002 appears to be addressed. **PASS.**

### 4.2 EquiSSL (ScaleGMN) vs EquiSSL-perm Training Fairness — NEW FINDING

**This was NOT raised in R1 and is a newly identified issue.**

The h-m2 ablation (Table 2) compares:
- **EquiSSL (scale+perm):** Uses h-e1 checkpoint — trained for **50 epochs**
- **EquiSSL-perm (perm-only):** Uses h-m1 checkpoint — trained for **100 epochs**

The paper describes h-m2 as "a fresh independent training run from scratch." This is factually incorrect. h-m2 is an *evaluation-only* run that loads pre-trained checkpoints from h-e1 (for EquiSSL) and h-m1 (for EquiSSL-perm) and applies linear probes. It does NOT re-train either model. Furthermore, the two checkpoints compared in Table 2 were trained for *different numbers of epochs* (50 vs 100). Since EquiSSL-perm gets 2× more training, the +0.143 ΔR² advantage may partly reflect this training difference rather than the symmetry group choice.

The paper's core claim — that permutation equivariance outperforms scale equivariance for ViT cross-architecture transfer — may be directionally correct, but Table 2 does not provide a fair ablation to support this claim.

### 4.3 MMD Table 3 Baseline Fairness — NEW FINDING (FATAL)

See FATAL-001 below.

---

## 5. FATAL Issues

### FATAL-001: Table 3 Mixes Two Incompatible MMD Definitions

**Location:** Section 5.4, Table 3 ("MMD Between CNN Train Zoo and ViT Test Zoo")

**What the paper claims:** Table 3 presents MMD(CNN train zoo → ViT test zoo) for three methods: SANE=0.849, EquiSSL=2.348, EquiSSL-perm=0.203.

**What the data actually shows:**
- SANE=0.849 and EquiSSL=2.348 come from **h-e1**, which measured **cross-architecture MMD** between CNN training zoo latents and ViT test zoo latents (exactly as the table header states).
- EquiSSL-perm=0.203 comes from **h-m2**, which measured **within-ViT-zoo subpopulation MMD** between high-accuracy and low-accuracy ViT models (a completely different quantity).

**Evidence:**
- h-e1/03_logic.md and h-e1/04_validation.md: "MMD(SANE→ViT) / MMD(EquiSSL→ViT)" — cross-architecture
- h-m2/03_logic.md line 284-294: `compute_mmd_subpop` — "MMD between high/low accuracy ViT subpopulations"
- h-m2 run_hm2.py: EquiSSL-perm MMD is labeled `mmd_perm` from `compare_mmd_subpop`, not from cross-architecture computation
- h-e1 experiment_results.json: Only contains EquiSSL (monomial), not EquiSSL-perm — no cross-arch MMD for EquiSSL-perm exists anywhere in the codebase

**Why this is FATAL:** A cross-architecture MMD and a within-zoo subpopulation MMD are fundamentally different quantities with different units, scales, and interpretations. Placing them in the same table under the same column header is a methodological error. The table as presented cannot be interpreted as any consistent comparison. The conclusion "EquiSSL-perm achieves lower distribution shift (MMD=0.203) than SANE (MMD=0.849)" is not supported by the data, because 0.203 measures something different from 0.849.

**Impact on paper:** Section 5.4 uses Table 3 to argue that EquiSSL-perm achieves lower MMD than SANE while achieving higher R² — presenting this as evidence of "genuine alignment" vs. SANE's collapse. This argument partially breaks down: the 0.203 figure does not measure cross-architecture alignment for EquiSSL-perm.

**Required fix:** Either (a) report only the two values where cross-arch MMD exists (SANE=0.849, EquiSSL=2.348) and note that no cross-arch MMD was computed for EquiSSL-perm; or (b) recompute cross-arch MMD for EquiSSL-perm using the h-m1 checkpoint and update all values consistently; or (c) remove the MMD table entirely and rely solely on R² results. At minimum, the EquiSSL-perm row must be removed or relabeled with the correct measurement definition.

---

## 6. MAJOR Issues

### MAJOR-001: Table 2 Comparison is Unfair — Different Training Epochs (NEW)

**Location:** Section 5.2, Table 2

The ablation in Table 2 compares EquiSSL (from h-e1, 50 epochs) vs EquiSSL-perm (from h-m1, 100 epochs). The paper describes h-m2 as "a fresh independent training run from scratch" — this is factually inaccurate. h-m2 is evaluation-only, loading existing checkpoints from h-e1 and h-m1 respectively.

The claim that "EquiSSL-perm outperforms EquiSSL by ΔR²=+0.143" is presented as evidence for the symmetry group hypothesis. But with a 2× training epoch advantage for EquiSSL-perm, this result cannot cleanly isolate symmetry group as the variable. A properly controlled ablation would train both models for the same number of epochs from the same initialization.

The directional result (perm > scale) is also confirmed in h-m1 Table 1 (ΔR²=0.021), which uses the same epoch count for both. However, Table 2 overstates the effect size due to the confound.

**Required fix:** Add a note to Table 2 disclosing that EquiSSL uses the h-e1 checkpoint (50 epochs) while EquiSSL-perm uses the h-m1 checkpoint (100 epochs), and that the magnitude of ΔR²=+0.143 may be partially attributable to this training discrepancy. The caption currently says "fresh independent training run from scratch" which is incorrect and should be corrected.

### MAJOR-002: +221% Not Fixed From R1 (INHERITED UNFIXED)

**Location:** Abstract, Contribution (2), Section 5.1, Conclusion

R1 review flagged (ACC-MAJOR-002) that the exact improvement is 219.5%, not 221%. Using rounded inputs gives 220.8% which rounds to 221%, but the h-m1 validation report states 219%. The paper still shows "+221%" in 4 locations. The inconsistency between the paper's stated 221% and the validation report's 219% remains unresolved.

**Required fix:** Choose one value and apply consistently. Recommend "approximately 220%" or use ">219%" to be conservative. If using rounded inputs (0.231 − 0.072)/0.072, state this explicitly.

### MAJOR-003: Paper Describes h-m2 as "Fresh Training Run From Scratch" — Factually Wrong (NEW)

**Location:** Introduction note block, Table 1 caption (line 181), Table 2 caption (line 199)

Multiple locations in the R1 revision state that h-m2 is "a fresh independent run from scratch." This is factually incorrect: h-m2 loads pre-existing checkpoints from h-e1 (EquiSSL) and h-m1 (EquiSSL-perm). No new model training occurs in h-m2. This is not a minor characterization issue — the "fresh from scratch" language is used to explain why Table 2 values differ from Table 1, which is actually explained by the different source checkpoints (h-e1 50-epoch vs h-m1 100-epoch), not by stochastic variation across independent training runs.

**Required fix:** Correct the description of h-m2 to: "h-m2 uses pre-trained checkpoints — EquiSSL from h-e1 (50-epoch checkpoint) and EquiSSL-perm from h-m1 (100-epoch checkpoint) — applied to fresh linear probe evaluation." Remove all "from scratch" language.

---

## 7. Human Review Notes (Minor)

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| H1 | All acc_latent values in h-m3 | acc_latent = exactly 0.1 for ALL 501 pairs — this is exact random chance for CIFAR-10 (10 classes), not "near-random." The decoder outputs constant random-class distribution. The paper says "near-random chance (acc=0.100)" which technically covers this, but the stronger statement "exactly at random chance for all 501 pairs" would be more accurate and interpretable | State "exactly random chance (acc=0.100 = 1/10 for all 501 pairs)" |
| H2 | References | The R1 revision correctly hedges [Anonymous2025LayerNorm] with "citation unverified at time of submission" in 3 locations and in the References entry. The hedging appears sufficient relative to R1's CRED-MAJOR-004 concern — the citation is no longer load-bearing. | No change required |
| H3 | Section 5.4 / Appendix A | Appendix states "mmd_comparison.png (h-e1) shows the MMD measurement results side-by-side for SANE and EquiSSL" — this is correct (h-e1 only has SANE and EquiSSL, not EquiSSL-perm). But this makes FATAL-001 even more apparent: the appendix correctly shows only h-e1 data (2 methods), while Table 3 presents 3 methods. | After fixing FATAL-001, update appendix description to match corrected Table 3 |
| H4 | Kofinas citation | "ICLR 2024 Oral" — this specific claim should be verified as part of submission. ICLR 2024 Oral papers are publicly listed. | Verify "Oral" designation before submission |
| H5 | Ballerini citation | arXiv:2502.09623 correctly formatted. The description ("diverse NeRF architectures, cross-architecture property transfer") matches the ground truth's note "verified in Semantic Scholar." | No change required |
| H6 | h-m2 Table 2 SANE row | SANE R²=0.072 in Table 2 comes from h-m2 results (sane_r2=0.0721). Consistent with h-m1 (0.07214606). ✓ | OK |

---

## 8. Summary for Revision Agent

### Issues Status from R1 Review

| R1 Issue | Status in R1 Revision | R2 Action |
|----------|----------------------|-----------|
| ACC-MAJOR-001 (Table 1 vs Table 2 EquiSSL inconsistency) | Addressed — note added to Table 1 and Table 2 captions | ✓ Addressed — but h-m2 description remains factually wrong (MAJOR-003) |
| ACC-MAJOR-002 (+221% vs +219%) | NOT FIXED | ↑ Promoted to MAJOR-002 |
| ACC-MAJOR-003 (unverified citation) | Addressed — citation hedged in body text and references | ✓ Sufficient hedging confirmed |
| ENG-MAJOR-001 (abstract missing base R² values) | Addressed — Abstract now includes R²=0.072 and R²=0.231 | ✓ Addressed |
| CRED-MAJOR-001 (R² range 0.231–0.327) | Addressed — Contribution (3) now explains both runs separately | ✓ Addressed |
| CRED-MAJOR-002 (SANE within-arch R²=0.72 not disclosed) | Addressed — multiple locations now include this context | ✓ Addressed |
| CRED-MAJOR-003 (establishing baseline claim) | Addressed — downgraded to "initial proof-of-concept evidence" | ✓ Addressed |
| CRED-MAJOR-004 (unverified citation load-bearing) | Addressed | ✓ Addressed |

### New Issues Found in R2

| Issue | Severity | Action Required |
|-------|----------|----------------|
| FATAL-001: Table 3 mixes cross-arch MMD and subpopulation MMD | FATAL | Remove EquiSSL-perm row from Table 3, OR recompute cross-arch MMD for EquiSSL-perm, OR remove Table 3 |
| MAJOR-001: Table 2 training epoch discrepancy (50 vs 100 epochs) | MAJOR | Add disclosure note to Table 2 caption; correct "fresh training run" language |
| MAJOR-002: +221% not fixed | MAJOR | Choose one consistent percentage; recommend "~220%" |
| MAJOR-003: h-m2 described as "fresh from scratch" — factually wrong | MAJOR | Correct all instances; explain h-m2 uses pre-trained checkpoints |

### Priority Fix List for Revision Agent

1. **[FATAL-001]** Fix Table 3: Remove EquiSSL-perm row (0.203) from Table 3 since it measures subpopulation MMD, not cross-architecture MMD. State in the table note: "Cross-architecture MMD was not computed for EquiSSL-perm; h-m2 reports within-ViT-zoo subpopulation MMD (0.203) which is not directly comparable." The core argument (SANE's low MMD is due to latent collapse) remains valid for the two methods that were measured consistently.

2. **[MAJOR-003]** Correct all instances of "fresh independent training run from scratch" for h-m2. Replace with accurate description: h-m2 applies fresh linear probe evaluation to pre-trained checkpoints (EquiSSL from h-e1, EquiSSL-perm from h-m1). This also explains why absolute values differ between Table 1 and Table 2 — it is not stochasticity in a re-run, it is different training regimes (50 vs 100 epochs).

3. **[MAJOR-001]** Add to Table 2 caption: "Note: EquiSSL encoder was trained for 50 epochs (h-e1 checkpoint); EquiSSL-perm encoder was trained for 100 epochs (h-m1 checkpoint). The epoch discrepancy may partially contribute to the observed ΔR²=+0.143 advantage for EquiSSL-perm. The h-m1 comparison (Table 1) using same-epoch conditions shows a smaller but directionally consistent advantage (ΔR²=+0.021)."

4. **[MAJOR-002]** Change "+221%" to "+220%" (or ">219%") in Abstract, Contribution (2), Section 5.1, and Conclusion. State computation method explicitly.

---

## Appendix: MMD Definition Evidence

From h-e1/04_validation.md:
> "MMD_SANE (train→ViT, SANE latent space) | 0.8487"
> "MMD_EquiSSL (train→ViT, EquiSSL latent space) | 2.3484"

From h-m2/03_logic.md line 284:
```python
def compute_mmd_subpop(z, accuracy_labels, threshold):
    """MMD between high/low accuracy ViT subpopulations. Returns scalar."""
```

From h-m2/results/hm2_results.json:
```json
"mmd": {
    "mmd_equi": 0.43048572540283203,
    "mmd_perm": 0.20343995094299316,
    "ratio": 0.4725823388281269
}
```

Note: The h-m2 EquiSSL subpopulation MMD (0.4305) differs from the h-e1 cross-architecture EquiSSL MMD (2.3484) — confirming these are different measurements. Table 3 reports h-e1's 2.348 for EquiSSL but h-m2's 0.203 for EquiSSL-perm, mixing the two incompatible metrics.
