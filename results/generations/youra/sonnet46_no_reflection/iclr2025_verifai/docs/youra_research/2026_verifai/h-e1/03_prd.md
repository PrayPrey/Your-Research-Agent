# Product Requirements Document: H-E1
# Locality Score Oracle Existence Proof

**Generated:** 2026-05-20
**Phase:** 3 - Implementation Planning
**Hypothesis:** h-e1 (EXISTENCE / MUST_WORK)
**Source:** 02c_experiment_brief.md (Phase 2C)

---

## 1. Executive Summary

This PRD specifies the implementation requirements for **H-E1: Locality Score Oracle Existence Proof**. The experiment verifies whether step-local Lean4 compiler feedback used as DPO negatives produces a measurably higher locality score (fraction of post-DPO probability mass on premise-consistent tactic categories) than a permutation control. This is a MUST_WORK gate: if LS_A ≤ LS_P, the oracle mechanism is absent and downstream hypotheses (H-M1 through H-M4, H-C1) must be re-evaluated.

**Hypothesis Statement:** Under fixed BFS geometry (≥85% formalization fidelity), DPO training with step-local Lean4 compiler error negatives (Condition A) produces locality score LS_A > LS_P (permutation control) on miniF2F hard subset and Vericoding hard subset.

**Gate:** MUST_WORK — `LS_A > LS_P` (p < 0.05, one-sided t-test)

---

## 2. Problem Statement

The core research question is whether formal feedback (Lean4 compiler errors) functions as a **local logical oracle** — directing probability mass toward premise-consistent tactics — rather than as a generic **policy regularizer**. This experiment measures the locality score, a novel metric quantifying how much the post-DPO probability mass shift concentrates on semantically-aligned tactic categories.

**Success Condition:** `LS_A > LS_P` on both evaluation datasets → oracle mechanism confirmed  
**Failure Condition:** `LS_A ≤ LS_P` → oracle absent → trigger MUST_WORK failure routing

---

## 3. Functional Requirements

### FR-1: Dataset Loading and Hard Subset Construction

**FR-1.1 miniF2F Dataset**
- Load `Tonic/MiniF2F` via HuggingFace `load_dataset`
- Dataset format: `{name, split, formal_statement, goal, header}` in Lean4 syntax
- Total problems: 488 (AMC/AIME/IMO + high-school/undergrad), splits: train/valid/test
- Hard subset definition: Run cold-start SFT evaluation → freeze problems where pass@1 < 20% across 16 rollouts

**FR-1.2 Vericoding Dataset**
- Download from paper release (arXiv:2509.22908 — Bursuc et al. 2025)
- Total problems: 12,504 formally verified code specifications (Lean/Verus/Dafny)
- Filter to Lean4-compatible problems only
- Hard subset: same cold-start SFT pass@1 < 20% protocol as miniF2F

**FR-1.3 LeanDojo Tracing**
- Trace datasets via LeanDojo: `LeanGitRepo(url, commit)` + `trace(repo)`
- Extract `(state, tactic, compiler_error)` triples using `Dojo` context manager
- Each triple must include LeanDojo state ID for alignment verification

**FR-1.4 Tactic Taxonomy**
Pre-specify tactic taxonomy BEFORE any training:
- Category 1: Type errors (`type mismatch`, `application type mismatch`)
- Category 2: Undefined names (`unknown identifier`, `unknown tactic`)
- Category 3: Tactic failures (`tactic failed`, `simp made no progress`)
- Category 4: Premise-consistent tactics = tactics addressing the specific error category

### FR-2: Baseline Model Loading

**FR-2.1 BFS-Prover SFT Checkpoint**
- Load `ByteDance-Seed/BFS-Prover-V2-7B` via HuggingFace transformers
- dtype: `torch.bfloat16`, device_map: `auto`
- This checkpoint serves as:
  - Frozen reference model π_ref for DPO
  - Starting point for each of 3 DPO condition fine-tunes
- Verify checkpoint loads correctly before any training

**FR-2.2 Cold-Start SFT Evaluation (Hard Subset Selection)**
- Run BFS-Prover SFT checkpoint in inference mode on full miniF2F + Vericoding
- 16 rollouts per problem
- Record pass@1 for each problem
- Hard subset = problems with pass@1 < 20%

### FR-3: DPO Pair Construction (3 Conditions)

**FR-3.1 Condition A — Step-Local Grounded (Proposed)**
- Rejected tactic (a_l): Lean4 compiler-error-triggering tactic at proof state s
- Chosen tactic (a_w): correct advancing tactic at same proof state s
- State alignment: 100% — s_w == s_l verified via LeanDojo state IDs
- Include `error_msg` and `error_category` in each pair metadata

**FR-3.2 Condition B — Step-Local Ungrounded (Ablation)**
- Rejected tactic (a_l): failed-branch tactic at same proof state s (no compiler error info)
- Chosen tactic (a_w): same as Condition A
- State alignment: 100% — same state s

**FR-3.3 Condition P — Permutation Control**
- Rejected tactic (a_l): tactic with shuffled/permuted compiler error messages
- Chosen tactic (a_w): same as Condition A
- State alignment: 100% — same state s
- Permutation: randomly shuffle error message tokens within the batch

**FR-3.4 Pair Validation**
- Assert 100% state alignment: `assert pair.state_id_chosen == pair.state_id_rejected`
- Abort with error if any alignment violation detected
- Log: `[H-E1] DPO pairs constructed: {N} pairs per condition`

### FR-4: DPO Training (3 Independent Runs)

**FR-4.1 Training Configuration**
- Optimizer: AdamW (weight_decay=0.01, betas=(0.9, 0.999))
- Learning rate: 5e-6 linear decay → 5e-7
- Batch size: 16 (per GPU, gradient accumulation ×2 if OOM)
- Epochs: 1
- DPO β: 10
- Mixed precision: bfloat16
- Seeds: 1 (fixed, EXISTENCE PoC — single run sufficient)
- GPU: single A100 (set `CUDA_VISIBLE_DEVICES` before training)

**FR-4.2 DPO Loss**
```python
loss = -F.logsigmoid(beta * (chosen_logps - ref_chosen_logps
                             - rejected_logps + ref_rejected_logps)).mean()
```
- Use `average_log_prob=False` (sum log-probs, not average) for tactic sequences

**FR-4.3 Training Stability Check**
- Monitor DPO loss throughout training
- If loss > 2× initial loss at epoch end → reduce LR or β → retry
- Log final loss value

**FR-4.4 Three Independent DPO Runs**
- Run A: Condition A pairs (Lean4 compiler error negatives)
- Run B: Condition B pairs (ungrounded step-local negatives)
- Run P: Condition P pairs (permuted error message negatives)
- Each run starts from same BFS-Prover-V2-7B SFT checkpoint

### FR-5: Locality Score Computation

**FR-5.1 Locality Score Definition**
```
locality_score = sum_s [ P_post(premise_consistent | s) - P_pre(premise_consistent | s) ]
               / sum_s [ sum_t [ |P_post(t | s) - P_pre(t | s)| ] ]
```
Where:
- `P_pre` = probability under frozen π_ref (BFS-Prover SFT)
- `P_post` = probability under DPO-trained model for this condition
- `premise_consistent` = tactic tokens addressing the specific error category at state s

**FR-5.2 Computation Protocol**
- Compute LS for each condition (A, B, P) on both evaluation datasets
- Use all hard-subset proof states (failed proof states with pass@1 < 20%)
- LS_A: from Condition A DPO model
- LS_B: from Condition B DPO model
- LS_P: from Condition P DPO model

**FR-5.3 Logging**
```
[H-E1] Locality Score — Condition A: {LS_A:.4f} | Condition B: {LS_B:.4f} | Condition P: {LS_P:.4f}
[H-E1] Gate Check: LS_A > LS_P = {LS_A > LS_P} (p={p_value:.4f})
```

### FR-6: Statistical Testing

**FR-6.1 Primary Gate Test**
- One-sided t-test: LS_A > LS_P
- `scipy.stats.ttest_1samp(locality_scores_A - locality_scores_P, 0, alternative='greater')`
- Gate PASS: p < 0.05 AND LS_A > LS_P
- Gate FAIL: p ≥ 0.05 OR LS_A ≤ LS_P

**FR-6.2 Secondary Test**
- One-sided comparison: LS_A > LS_B (grounded vs ungrounded step-local)

### FR-7: Visualization

**FR-7.1 Required Figure (Mandatory)**
- Bar chart: LS_A vs LS_B vs LS_P on miniF2F hard subset + Vericoding hard subset
- 2 datasets × 3 conditions = 6 bars
- Save to `h-e1/figures/locality_score_comparison.png`

**FR-7.2 Additional Figures**
- Probability mass distribution plot: stacked bar of tactic category distribution (Δ = P_post - P_pre) per condition × dataset
- Error category breakdown: LS per LeanDojo error category (type_error / undefined_name / tactic_failure)
- Locality score per proof state: scatter plot (x: proof state complexity, y: LS)
- Save all to `h-e1/figures/`

### FR-8: Gate Evaluation and Results Logging

**FR-8.1 Gate Check**
```python
def verify_mechanism_active(LS_A, LS_B, LS_P, threshold=0.0):
    return LS_A > LS_P + threshold

if not verify_mechanism_active(LS_A, LS_B, LS_P):
    print("GATE FAIL: H-E1 MUST_WORK not satisfied — oracle mechanism absent")
else:
    print("GATE PASS: H-E1 — locality score confirms oracle mechanism exists")
```

**FR-8.2 Results File**
- Write `h-e1/04_validation.md` with: LS values, p-value, gate result, raw scores per dataset

---

## 4. Data Specification

### Dataset 1: miniF2F Hard Subset
| Field | Value |
|-------|-------|
| Name | miniF2F hard subset |
| Source | `Tonic/MiniF2F` (HuggingFace) |
| Full size | 488 problems |
| Hard subset size | TBD after cold-start SFT (expected ~100-150 problems) |
| Format | `{name, split, formal_statement, goal, header}` |
| Loading | `load_dataset("Tonic/MiniF2F")` |
| License | MIT |

### Dataset 2: Vericoding Hard Subset
| Field | Value |
|-------|-------|
| Name | Vericoding hard subset |
| Source | arXiv:2509.22908 (Bursuc et al. 2025) — manual download |
| Full size | 12,504 problems |
| Hard subset size | TBD after cold-start SFT |
| Format | Lean4-compatible formally verified code specs |
| Loading | Direct download from paper release URL |

### Model: BFS-Prover SFT Checkpoint
| Field | Value |
|-------|-------|
| HuggingFace ID | `ByteDance-Seed/BFS-Prover-V2-7B` |
| Base | Qwen2.5-Math-7B |
| Parameters | 7B |
| Role | Frozen π_ref + starting point for 3 DPO conditions |

---

## 5. Non-Functional Requirements

**NFR-1: Reproducibility**
- Fixed seed (seed=1) for all random operations
- All model checkpoints saved after training
- Full hyperparameter logging to experiment log file

**NFR-2: GPU Resource Management**
- Single GPU only (A100 80GB)
- Set `CUDA_VISIBLE_DEVICES` before any Python/training script
- Select GPU with lowest memory usage (`nvidia-smi`)

**NFR-3: State Alignment Integrity**
- 100% state alignment in all DPO pairs — no exceptions
- Assert and abort if alignment violation detected (not warn-and-continue)

**NFR-4: Tactic Taxonomy Immutability**
- Tactic taxonomy MUST be pre-specified before any training begins
- Taxonomy cannot change between conditions A/B/P

**NFR-5: Training Duration**
- Each DPO run: ~2-4 hours on A100 for 1-epoch DPO of 7B model
- Total experiment: ~6-12 hours for 3 conditions

**NFR-6: Experiment Scale**
- Use full hard subsets (all problems with pass@1 < 20%) — NOT subsampled
- Minimum expected hard subset: 50+ problems per dataset
- Locality score computed over all hard-subset proof states

---

## 6. Success Criteria

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| Code runs without error | DPO training + LS computation completes | prerequisite |
| LS_A > LS_P (miniF2F) | strict direction | MUST_WORK |
| LS_A > LS_P (Vericoding) | strict direction | MUST_WORK |
| p-value (one-sided) | < 0.05 | MUST_WORK |
| LS_A > LS_B | secondary (informational) | informational |

**PoC Pass:** Both MUST_WORK criteria satisfied on both datasets  
**PoC Fail:** Any MUST_WORK criterion fails → trigger failure routing → H-M hypotheses re-evaluated

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.40.0
datasets>=2.18.0
lean-dojo>=2.0.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
accelerate>=0.27.0
trl>=0.8.0  # for DPO trainer (optional — may use custom DPO loop)
deepspeed>=0.14.0  # for ZeRO-3 if multi-GPU needed
```

### 7.2 External Repositories (Reference)
- `ByteDance-Seed/BFS-Prover-V2` — BFS training infrastructure reference
- `lean-dojo/LeanDojo-v2` — Lean4 proof state extraction framework
- `dvlab-research/step-dpo` — Step-level DPO pair construction reference
- `eric-mitchell/direct-preference-optimization` — Canonical DPO loss reference
- `openai/miniF2F` — miniF2F dataset (via HuggingFace: `Tonic/MiniF2F`)

### 7.3 System Requirements
- Lean 4 installation (for LeanDojo tracing)
- CUDA 12.0+
- Python 3.10+
- ~200GB disk space (model checkpoints × 4 + dataset + LeanDojo traces)

---

## 8. Out of Scope

- Multi-GPU distributed training (single A100 sufficient for 7B model)
- Hyperparameter sweeps (β, lr) — fixed per BFS-Prover-V2 paper
- BFS proof search evaluation (pass@1 on full benchmark) — this is H-M3's responsibility
- Z3 SMT counterexamples (this is Condition A only with Lean4; Z3 bridge is for future hypotheses)
- Vericoding download automation (manual download required from paper release)

---

*PRD generated inline from Phase 2C experiment brief (02c_experiment_brief.md)*  
*Source repositories: BFS-Prover-V2, LeanDojo-v2, Step-DPO, eric-mitchell/DPO, openai/miniF2F*
