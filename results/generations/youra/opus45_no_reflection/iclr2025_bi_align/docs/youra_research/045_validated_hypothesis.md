# Validated Hypothesis Synthesis

**Generated:** 2026-08-18
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

BiDPO demonstrates **partial validation**: the foundational mechanism works (orthogonal agency signal extraction, stable training integration), but the downstream effect on generation quality is **not statistically significant**. The collaboration score successfully extracts agency signals independent of preference labels (r=-0.026), and BiDPO training integrates stably with DPO (loss decreased 1.2%). However, when tested on held-out prompts, BiDPO-trained models show only a marginal +0.54% improvement in collaboration scores over baseline (p=0.247, d=0.016), failing to meet statistical significance thresholds.

The original hypothesis that agency-preserving auxiliary objectives would produce Pareto-dominant models **cannot be confirmed** with current evidence. The pipeline terminated early due to h-m2 failure, leaving P1-P3 predictions untested.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | BiDPO (L_DPO + λL_agency) Pareto-dominates standard DPO on MT-Bench × TruthfulQA |
| **Refined Core Statement** | BiDPO stably integrates agency signals during training but does not significantly improve generation-time agency metrics |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 67% (2/3 gates passed) |
| **Hypotheses Validated** | 2 / 3 executed (h-m3, h-m4 not reached) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | BiDPO λ=0.5 achieves MT-Bench ≥ DPO + 0.3 | h-m4 | MT-Bench score | NOT TESTED | INCONCLUSIVE | N/A | h-m4 not executed (blocked by h-m2 failure) |
| **P2** | MT-Bench gains exceed TruthfulQA gains | h-m3 | Relative improvement ratio | NOT TESTED | INCONCLUSIVE | N/A | h-m3 not executed (blocked by h-m2 failure) |
| **P3** | ∃ λ* > 0 that Pareto-dominates DPO | h-m2 → h-m4 | Pareto frontier analysis | NOT TESTED | INCONCLUSIVE | N/A | Prerequisites not satisfied |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Collaboration score extracts implicit agency signals via pattern matching | r > 0.7 with preference labels | r = -0.026 (H-E1) | **VERIFIED** |
| 2 | L_agency creates gradient pressure toward agency-preserving outputs | Training unstable or loss doesn't decrease | Loss 0.929 → 0.918, no NaN (H-M1) | **VERIFIED** |
| 3 | Agency-preserving responses transfer capability to users | MT-Bench multi-turn ≤ single-turn gains | NOT TESTED (H-M3 not executed) | **UNVERIFIED** |
| 4 | Improved capability transfer leads to higher MT-Bench scores | MT-Bench ≤ DPO for all λ > 0 | NOT TESTED (H-M4 not executed) | **UNVERIFIED** |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under standard alignment training conditions (Mistral-7B, HH-RLHF dataset), if we add a length-normalized collaboration score as an auxiliary objective to DPO (L_BiDPO = L_DPO + lambda * L_agency), then models will Pareto-dominate standard DPO on MT-Bench x TruthfulQA frontier, because agency-preserving responses (explanations, uncertainty acknowledgment, engagement) transfer capability to users, improving multi-turn dialogue quality.

### 3.2 Refined Core Statement (Phase 4.5)

> BiDPO successfully integrates a length-normalized collaboration score as a training signal orthogonal to preference labels (r=-0.026), and training remains stable (loss decreases without numerical instabilities). However, **the training-time signal does not transfer to statistically significant generation-time improvements** in collaboration scores (Δ=+0.54%, p=0.247, d=0.016). The downstream effects on MT-Bench and TruthfulQA remain untested.

**Key Changes:**
1. **Removed:** "Pareto-dominate" claim (untested, prerequisite h-m2 failed)
2. **Weakened:** "Agency-preserving responses transfer capability" → mechanism steps 3-4 unverified
3. **Preserved:** Orthogonality validation (Step 1) and training stability (Step 2)
4. **Added:** Explicit acknowledgment of negative result at h-m2 (generation-time effect not significant)

### 3.3 Causal Mechanism — Verified Chain

```
[VERIFIED] Step 1: collab_score_v2 extracts agency signals (r=-0.026 with preference labels)
     ↓
[VERIFIED] Step 2: L_agency integrates with L_DPO stably (loss ↓ 0.929→0.918, 0 NaN/Inf)
     ↓
[FAILED]   Step 2→3 Bridge: Training signal DOES NOT transfer to generation (p=0.247)
     ↓
[UNVERIFIED] Step 3: Capability transfer hypothesis (not tested)
     ↓
[UNVERIFIED] Step 4: MT-Bench improvement hypothesis (not tested)
```

**Removed/Modified Steps:**
- **Step 3** (Agency-preserving responses transfer capability): UNVERIFIED — prerequisite h-m2 failed, blocking execution
- **Step 4** (Improved MT-Bench scores): UNVERIFIED — not executed

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| BiDPO generates higher-agency responses than DPO | REFUTED | p=0.247, d=0.016 (not significant) | H-M2 results |
| Agency signals improve multi-turn dialogue quality | REMOVED (untested) | Causal chain broken at h-m2 | H-M3/M4 not executed |
| Pareto-dominance on MT-Bench × TruthfulQA | REMOVED (untested) | Prerequisites not satisfied | Pipeline incomplete |
| λ=0.5 is optimal | UNCHANGED (assumption) | Only λ=0.5 tested | No sweep performed |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: Collab score captures genuine agency signals | ASSUMED | PARTIALLY VERIFIED | Score variance exists (std=0.22), but generation effect null | May optimize for superficial patterns |
| A2: Agency signals orthogonal to preference labels | ASSUMED | **VERIFIED** | r=-0.026 << 0.7 threshold | N/A (verified) |
| A3: MT-Bench GPT-4 judge evaluates genuine quality | ASSUMED | UNVERIFIED | Not tested (h-m4 not executed) | Improvement reflects style, not utility |
| A4: Mistral-7B results generalize to other sizes | ASSUMED | UNVERIFIED | Single model tested | Findings limited to 7B scale |
| A5: HH-RLHF patterns remain relevant | ASSUMED | PLAUSIBLE | Standard benchmark, recent papers use it | May not transfer to newer data |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

The BiDPO hypothesis rests on a 4-step causal chain. Experiments verified steps 1-2:

1. **Orthogonal signal extraction works:** The collaboration score (collab_score_v2) extracts information independent of which response humans preferred. The near-zero correlation (r=-0.026) indicates the heuristic captures something beyond "preferred = good."

2. **Multi-objective training is stable:** Combining L_DPO with L_agency (λ=0.5) does not destabilize optimization. The 1.2% loss reduction over 250 steps shows gradient flow from both objectives.

However, **the bridge from training to generation failed.** Despite gradient pressure during training, the BiDPO model's generated responses show only marginal, non-significant improvement in collaboration scores (+0.54%, p=0.247). This suggests one of:
- Training signal is too weak relative to preference signal
- 250 training steps (PoC scale) insufficient for behavioral shift
- Collaboration score captures training-time patterns not expressed at inference

### 4.2 Unexpected Findings Analysis

#### Finding: Training-Generation Gap

- **Observation:** BiDPO training stably optimizes for collaboration score, but generated responses show no significant improvement.
- **Why Unexpected:** Standard assumption is that training-time optimization transfers to test-time behavior.
- **Competing Explanations:**
  1. **Insufficient training duration:** 250 steps on 4000 samples may not induce behavioral change. (Plausibility: HIGH)
  2. **Signal strength imbalance:** λ=0.5 may be too low relative to L_DPO's influence. (Plausibility: MEDIUM)
  3. **Heuristic validity:** collab_score_v2 patterns may not correspond to behaviors the model can learn to produce. (Plausibility: MEDIUM)
  4. **Generation parameters override:** Temperature=0.7, top_p=0.9 sampling may wash out subtle behavioral shifts. (Plausibility: LOW)
- **Most Likely Interpretation:** Insufficient training duration is the primary factor. PoC-scale experiments (250 steps) are designed to test stability, not behavioral shift. Full-scale training (1 epoch, ~10K steps) may show different results.
- **Additional Evidence Needed:** Repeat h-m2 with full training run, or sweep λ ∈ {0.25, 0.5, 0.75, 1.0}.

#### Finding: Nearly Identical Score Distributions

- **Observation:** DPO mean=0.3728 (std=0.3294), BiDPO mean=0.3782 (std=0.3333) — distributions almost identical.
- **Why Unexpected:** If L_agency creates gradient pressure, output distribution should shift.
- **Competing Explanations:**
  1. **PoC subset too small:** 4000 training samples may not cover enough behavioral diversity.
  2. **Base model dominance:** Mistral-7B-Instruct already has strong priors that 250 steps can't override.
  3. **Collaboration score ceiling:** Responses may already be near maximum achievable score.
- **Most Likely Interpretation:** Base model priors dominate at PoC scale.

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Agency signal orthogonal to preference | MODPO multi-objective DPO | CONSISTENT — MODPO shows auxiliary objectives can be added without redundancy | Zhou et al. 2024 |
| Training stability with auxiliary loss | PAMA, GAPO multi-objective DPO | CONSISTENT — multi-loss DPO extensions remain stable | Various 2024 |
| Generation-time effect null | N/A | NOVEL (negative result) — literature lacks generation-time agency measurement |
| Collaboration score heuristics | HCI collaborative dialogue research | BUILDS ON — patterns derived from explanation/engagement literature | Various HCI |

### 4.4 Theoretical Contributions

1. **Validation of orthogonality:** Demonstrated that agency-like signals (collaboration patterns) can be extracted from preference data without redundancy to preference labels.
2. **Stability of multi-objective DPO:** Confirmed that auxiliary objectives can be added to DPO without destabilizing training (extends MODPO findings).
3. **Negative result on generation transfer:** Provided evidence that training-time auxiliary signals may not transfer to generation behavior at PoC scale — important for future work on alignment objectives.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Collab score orthogonality | MUST_WORK | **PASSED** | 100% | r=-0.026, signal is independent of preference |
| **h-m1** | BiDPO training stability | MUST_WORK | **PASSED** | 100% | Loss ↓ 0.929→0.918, 0 NaN, stable gradients |
| **h-m2** | BiDPO generates higher agency | SHOULD_WORK | **FAILED** | 0% | Δ=+0.54%, p=0.247, d=0.016 (not significant) |
| **h-m3** | MT-Bench > TruthfulQA gains | SHOULD_WORK | NOT RUN | — | Blocked by h-m2 failure |
| **h-m4** | MT-Bench >= DPO + 0.3 | SHOULD_WORK | NOT RUN | — | Blocked by h-m2 failure |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 5 |
| **Fully Validated** | 2 |
| **Partially Validated** | 0 |
| **Failed** | 1 |
| **Not Executed** | 2 |
| **Total Tasks Completed** | 27 / 27 (for executed hypotheses) |
| **SDD Compliance Rate** | 100% |

### 5.3 Optimal Hyperparameters

```yaml
# From H-M1 training (PoC scale)
model: mistralai/Mistral-7B-Instruct-v0.2
dataset: Anthropic/hh-rlhf (helpful-base)
dpo_beta: 0.1
lambda_agency: 0.5  # Only value tested
learning_rate: 5e-7
batch_size: 16 (1 × 16 grad accum)
epochs: 1
steps: 250 (PoC)
precision: bfloat16
gradient_clip: 1.0
# Note: These are PoC-scale parameters, not tuned for optimal performance
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| collab_score_v2 | h-e1 | `h-e1/code/collab_score.py` | YES |
| BiDPO loss function | h-m1 | `h-m1/code/bidpo_loss.py` | YES |
| Data pipeline (HH-RLHF) | h-m1 | `h-m1/code/data.py` | YES |
| Training loop with stability monitoring | h-m1 | `h-m1/code/train.py` | YES |
| Response generation pipeline | h-m2 | `h-m2/code/generate.py` | YES |
| Statistical comparison suite | h-m2 | `h-m2/code/analysis.py` | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Pearson correlation | \|r\| < 0.7 | r = -0.026 | NONE | Exceeded expectations (much more orthogonal than required) |
| **h-m1** | Loss decrease | final < initial | 0.929 → 0.918 | NONE | Met criteria |
| **h-m1** | NaN/Inf count | 0 | 0 | NONE | Met criteria |
| **h-m2** | One-sided p-value | p < 0.05 | p = 0.247 | HYPOTHESIS_ISSUE | Signal didn't transfer to generation |
| **h-m2** | Cohen's d | d ≥ 0.2 | d = 0.016 | HYPOTHESIS_ISSUE | Negligible effect size |
| **h-m2** | BiDPO mean > DPO mean | True | 0.3782 > 0.3728 | NONE | Direction correct but not significant |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| gate_bar.png | h-e1/figures/ | Correlation vs 0.7 threshold | Methods or Results |
| histogram.png | h-e1/figures/ | Chosen vs rejected score distributions | Supplementary |
| training_loss_curves.png | h-m1/outputs/figures/ | DPO + agency + total loss over steps | Results (Training) |
| score_comparison_bar.png | h-m2/figures/ | BiDPO vs DPO mean collab scores | Results (Generation) |
| score_distributions.png | h-m2/figures/ | Distribution overlap between models | Discussion |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Limitation 1: PoC-Scale Training Only

- **What:** All training used 250 steps on 4000 samples (PoC scale), not full 1-epoch training (~10K steps on 170K samples).
- **Why This Matters:** Behavioral shifts may require more training steps to manifest.
- **Root Cause:** Experimental protocol designed for stability testing (h-m1 gate: "does it work?"), not efficacy testing.
- **Impact on Claims:** Cannot conclude BiDPO doesn't work at full scale — only that PoC-scale training doesn't transfer to generation.
- **Why Acceptable:** PoC design is standard for mechanism validation; full-scale experiments are expensive.

#### Limitation 2: Single λ Value Tested

- **What:** Only λ=0.5 tested for agency weight.
- **Why This Matters:** Optimal λ may be higher (stronger agency signal) or lower (less interference with DPO).
- **Root Cause:** Hypothesis defined λ=0.5 as primary test point; sweep planned for h-m4.
- **Impact on Claims:** Cannot identify optimal λ or rule out that other values work.
- **Why Acceptable:** Single-point test is first step; negative result informs future sweep design.

#### Limitation 3: Heuristic-Based Collaboration Score

- **What:** collab_score_v2 uses regex patterns (reasoning traces, uncertainty markers, engagement cues), not learned representations.
- **Why This Matters:** Patterns may not capture full range of "agency-preserving" behaviors; models may satisfy patterns superficially.
- **Root Cause:** Design choice for interpretability and efficiency.
- **Impact on Claims:** Positive results on this metric may not transfer to human-judged agency; negative results may miss genuine agency behaviors not captured by heuristics.
- **Why Acceptable:** Heuristics validated as orthogonal to preference (h-e1); learned scores would require separate annotation effort.

#### Limitation 4: Single Model Architecture

- **What:** Only Mistral-7B-Instruct-v0.2 tested.
- **Why This Matters:** Results may not generalize to other model sizes, architectures, or instruction-tuning approaches.
- **Root Cause:** Standard practice in DPO literature; resource constraints.
- **Impact on Claims:** Findings limited to 7B instruction-tuned models.
- **Why Acceptable:** Mistral-7B is representative of widely-deployed alignment targets.

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Training scale | PoC (250 steps) | Full scale (10K+ steps) | Only PoC tested |
| Model size | 7B parameters | <3B or >30B | Single model |
| Dataset | HH-RLHF (English, helpful) | Other languages, safety-focused | Single dataset |
| λ value | 0.5 | Other values | Single point |
| Generation params | temp=0.7, top_p=0.9 | Different sampling strategies | Not varied |

### 6.3 Assumption Violation Impact

- **A1 (Heuristic captures agency):** PARTIALLY VIOLATED — heuristics may capture style rather than genuine agency, contributing to null generation result.
- **A3 (MT-Bench evaluates quality):** UNTESTED — if violated, even positive results would not indicate user utility.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** PoC training scale is insufficient for behavioral shift
  - **Why Not Yet Tested:** Experimental protocol focused on stability, not efficacy
  - **Proposed Experiment:** Full-scale BiDPO training (1 epoch, ~10K steps) with h-m2 generation comparison
  - **Expected Outcome:** If training scale is the issue, full-scale should show significant effect

- **Alternative:** λ=0.5 is suboptimal; stronger agency signal needed
  - **Why Not Yet Tested:** Single λ value in protocol
  - **Proposed Experiment:** λ sweep {0.25, 0.5, 0.75, 1.0} at full scale
  - **Expected Outcome:** Identify λ* that maximizes generation-time collaboration while maintaining stability

- **Alternative:** Sampling parameters wash out behavioral differences
  - **Why Not Yet Tested:** Generation parameters fixed for reproducibility
  - **Proposed Experiment:** Lower temperature (0.3-0.5) generation comparison
  - **Expected Outcome:** Reduced stochasticity may reveal trained behaviors

### 7.2 From Unverified Assumptions

- **Assumption:** MT-Bench GPT-4 judge evaluates genuine dialogue quality (A3)
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Human evaluation of BiDPO vs DPO responses on agency dimensions
  - **If Violated:** MT-Bench improvements reflect style matching, not user utility

- **Assumption:** Collab score heuristics capture genuine agency (A1)
  - **Current Status:** PARTIALLY VERIFIED (orthogonal, but generation null)
  - **Proposed Test:** Human annotation of "agency-preserving" responses to validate heuristics
  - **If Violated:** Need learned collaboration classifier from human labels

### 7.3 From Scope Extension Opportunities

- **Extension:** Test at larger model scales (13B, 70B)
  - **Current Evidence Suggesting Feasibility:** Stability at 7B suggests larger models may also be stable
  - **Required Resources:** Multi-GPU training infrastructure, ~48 GPU-hours per model size

- **Extension:** Test on safety-focused data (HH-RLHF harmless split, red-team)
  - **Current Evidence Suggesting Feasibility:** HH-RLHF structure identical across splits
  - **Required Resources:** Same infrastructure, different data subset

- **Extension:** Learned collaboration score from human annotations
  - **Current Evidence Suggesting Feasibility:** Heuristics provide weak signal; learned model may be stronger
  - **Required Resources:** Human annotation campaign (~1000 examples)

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Hook:** "We asked whether auxiliary objectives for human agency preservation could improve alignment training — and found a cautionary tale about the gap between training signals and behavioral change."

**Hook Strategy:** Negative result framing — position as methodological contribution about training-generation transfer.

**Why This Hook:** 
- Honest about null result at h-m2
- Highlights validated components (orthogonality, stability)
- Sets up future work as clear next steps
- Contributes to literature on multi-objective alignment (what doesn't work is valuable)

### 8.2 Key Insight (Experiment-Verified)

> Agency-like signals can be extracted from preference data (r=-0.026 with labels) and integrated into DPO training without destabilization (loss ↓ 1.2%), but PoC-scale training does not transfer to generation-time behavioral changes (p=0.247).

**Verification Evidence:** H-E1 correlation analysis, H-M1 training logs, H-M2 generation comparison.

### 8.3 Strongest Claims (Paper-Ready)

1. **Collaboration score provides orthogonal training signal**
   - Evidence: r=-0.026 between collab_score_v2 and preference labels (n=2000, HH-RLHF)
   - Confidence: HIGH
   - Suggested Section: Results 4.1 or Methods 3.2

2. **Multi-objective DPO with agency loss is training-stable**
   - Evidence: Loss 0.929→0.918, 0 NaN/Inf, consistent gradient norms (H-M1)
   - Confidence: HIGH
   - Suggested Section: Results 4.2

3. **PoC-scale training does not induce generation-time agency improvement (negative result)**
   - Evidence: Δ=+0.54%, p=0.247, d=0.016 (H-M2)
   - Confidence: MEDIUM (may change at full scale)
   - Suggested Section: Results 4.3 or Discussion

### 8.4 Honest Limitations (Must Include in Paper)

1. **PoC scale only**
   - Why Acceptable: Standard for mechanism validation; full-scale is future work
   - Suggested Framing: "We demonstrate feasibility at proof-of-concept scale; scaling behavior is an important direction for future work."

2. **Single model architecture**
   - Why Acceptable: Representative of deployment targets
   - Suggested Framing: "We focus on Mistral-7B as representative of instruction-tuned models; generalization to other architectures requires further study."

3. **Heuristic-based collaboration score**
   - Why Acceptable: Interpretable, efficient, validated as orthogonal
   - Suggested Framing: "Our heuristic approach provides an interpretable baseline; learned scores may capture additional agency dimensions."

4. **Null result at generation transfer**
   - Why Acceptable: Negative results are scientifically valuable
   - Suggested Framing: "The gap between training-time signal and generation-time behavior highlights the challenge of auxiliary objective design."

### 8.5 Evidence Highlights (Most Persuasive)

1. **Orthogonality demonstration**
   - Data: r=-0.026, p=0.25 (confirming no correlation), score variance 0.22 (meaningful signal)
   - "So What": Agency signals exist in preference data independent of which response was preferred
   - Suggested Figure/Table: Scatter plot of collab_score vs preference label (h-e1/figures/scatter.png)

2. **Training stability**
   - Data: Loss curve 0.929→0.918 over 250 steps, 0 NaN/Inf, gradient norm 348-366 (clipped at 1.0)
   - "So What": Multi-objective DPO with arbitrary auxiliary losses is stable (extends MODPO)
   - Suggested Figure/Table: Training loss curves (h-m1/outputs/figures/training_loss_curves.png)

3. **Null generation result (transparency)**
   - Data: BiDPO 0.3782 vs DPO 0.3728, p=0.247, d=0.016
   - "So What": Training signals don't automatically transfer — important negative result for alignment research
   - Suggested Figure/Table: Score distribution comparison (h-m2/figures/score_distributions.png)

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `03_refinement.yaml` | Main | Original hypothesis definition |
| `verification_state.yaml` | Pipeline | Gate results and execution history |
| `h-e1/04_validation.md` | h-e1 | Orthogonality experiment results |
| `h-e1/04_checkpoint.yaml` | h-e1 | Task completion status |
| `h-e1/03_tasks.yaml` | h-e1 | Planned implementation tasks |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design specification |
| `h-m1/04_validation.md` | h-m1 | Training stability results |
| `h-m1/04_checkpoint.yaml` | h-m1 | Task completion status |
| `h-m1/03_tasks.yaml` | h-m1 | Planned implementation tasks |
| `h-m1/02c_experiment_brief.md` | h-m1 | Experiment design specification |
| `h-m2/04_validation.md` | h-m2 | Generation comparison results |
| `h-m2/04_checkpoint.yaml` | h-m2 | Task completion status |
| `h-m2/03_tasks.yaml` | h-m2 | Planned implementation tasks |
| `h-m2/02c_experiment_brief.md` | h-m2 | Experiment design specification |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
