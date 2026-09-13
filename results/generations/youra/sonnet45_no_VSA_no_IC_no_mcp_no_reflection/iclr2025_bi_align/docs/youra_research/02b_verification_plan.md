# Verification Plan: RLHF Preference Entropy Collapse Beyond Performance-Justified Levels

**Date:** 2026-08-28
**Hypothesis ID:** H-EntropyCollapse-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under RLHF training on preference datasets (Anthropic-HH, WebGPT), if models undergo extended alignment optimization beyond initial performance saturation, then preference distribution entropy collapses faster than task performance improves, because users habituate to model output style and converge on preferences even for subjective tasks where diversity is legitimate.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in the entropy-reduction-per-performance-gain ratio (dH/dP) between RLHF training phases. Entropy reduction is fully explained by task quality improvements.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic-HH (Helpful & Harmless) (standard) | Contains pairwise preference comparisons across diverse conversational tasks (QA, creative, opinion, advice). Includes both base model and RLHF-tuned model responses, enabling Part 1 retrospective analysis. Large scale (160K+ comparisons) supports robust entropy calculation. |
| **Model** | Pythia-1B (for Part 2 checkpoint experiment) | Open-source model with published training checkpoints, enabling reproducible RLHF experiments. 1B parameter scale is compute-feasible for multi-checkpoint training (12 GPU-hours estimated). Small enough for rapid iteration, large enough to show RLHF training dynamics. |

**Dataset Details:**
- Source: https://github.com/anthropics/hh-rlhf
- Path: hh-rlhf/helpful-base and hh-rlhf/harmless-base

**Model Details:**
- Type: decoder-only transformer
- Source: EleutherAI Pythia suite

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| InstructGPT (Ouyang et al., 2022) | Preference win rate 85% vs GPT-3 base model | OpenAI human preference data |
| Constitutional AI (Bai et al., 2022) | Harmlessness score improvement with RL from AI feedback | Anthropic-HH |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Preference entropy is a valid proxy for human critical evaluation capacity | Information theory: higher entropy = greater diversity/uncertainty in judgments, indicating active deliberation rather than passive acceptance | If entropy is orthogonal to critical thinking (e.g., users show low entropy but high override rates), the hypothesis mechanism fails |
| A2 | RLHF training can continue beyond performance saturation (inflection point exists) | Many RLHF implementations use fixed step counts (10K-50K) without early stopping based on performance plateaus | If RLHF training always stops before inflection point, the overcorrection phenomenon may not occur in practice |
| A3 | Subjective tasks legitimately support diverse preferences (no single correct answer) | Tasks like creative writing, opinion questions, stylistic preferences have no ground truth — diversity is expected | If all tasks converge to ground truth over time, entropy reduction on subjective tasks could be justified by users learning correct answers |
| A4 | Cross-user preference entropy reflects collective critical diversity, not just population heterogeneity | By controlling for task type and using fixed prompt sets, we isolate entropy changes due to model influence, not shifting user demographics | If entropy changes are driven by population composition shifts (different labelers at different training stages), we're measuring confound, not mechanism |
| A5 | Existing RLHF preference datasets (Anthropic-HH, WebGPT) contain sufficient raw preference distributions to compute entropy (not just aggregated win rates) | Anthropic-HH publishes pairwise comparison data; entropy computable from response frequency distributions | If datasets only publish summary statistics (mean win rate), entropy cannot be calculated — requires access to raw preference counts |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First application of information-theoretic entropy to measure bidirectional alignment failure. Introduces "inflection point detection" methodology for identifying when RLHF training crosses from quality improvement to preference monoculture imposition. Reframes preference variance as signal (critical evaluation capacity) rather than noise (measurement error).

**Key Innovation:** Entropy collapse as bidirectional alignment gap metric. Existing benchmarks measure AI→human alignment (preference agreement), but ignore human→AI alignment (preserved critical diversity). Preference entropy provides quantifiable proxy for collective human agency preservation.

**Differentiation:**
- Traditional RLHF evaluation (InstructGPT, Constitutional AI): Measures preference agreement as success. High consensus = good. Does not measure whether consensus erases legitimate diversity.
- HCI user empowerment metrics: Requires user studies, self-reported measures. Entropy approach uses existing preference data, no new human evaluation.
- Reward hacking detection: Focuses on model exploiting misspecified rewards. Entropy collapse focuses on user behavior homogenization.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | READY |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | READY |
| H-M4 | MECHANISM | MUST_WORK | H-M3 | READY |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Preference Entropy Exists and is Computable

**Statement**: Under RLHF preference datasets (Anthropic-HH), if we have access to raw pairwise comparison data, then we can compute Shannon entropy H = -Σ p_i log(p_i) for preference distributions, because the dataset publishes response frequency counts rather than only aggregated win rates.

**Rationale**: Validates the foundational measurement assumption (A5). Without computable entropy, the entire mechanism chain fails. This existence hypothesis confirms that our primary dependent variable can be reliably extracted from existing benchmarks without new data collection.

**Variables**:
- Independent: Dataset access level (raw counts vs aggregated stats)
- Dependent: Entropy computability (binary: yes/no)
- Controlled: Dataset source (Anthropic-HH fixed)

**Verification Protocol**:
1. Download Anthropic-HH pairwise comparison data from public repository.
2. Parse response frequency distributions for sample prompts (n=100).
3. Compute Shannon entropy H for each prompt's preference distribution.
4. Validate entropy range [0, log(2)] for binary comparisons.
5. Report entropy computation success rate across sample.

**Success Criteria**:
- Primary: Entropy computable for ≥95% of sampled prompts
- Secondary: Computed entropy shows variance (not all zero or constant)

**Failure Response**:
- IF fails: ABANDON (mechanism untestable without entropy measure)

**Dependencies**: None

**Source**: Phase 2A Section 5 (SH1 Existence)

---

#### H-M1: Base Model High-Variance Establishes Baseline Entropy

**Statement**: Under base model outputs (Pythia-1B pretrained, no RLHF), if we collect preference comparisons on diverse conversational prompts, then preference entropy will be high (H > 0.6 bits for binary choices), because users express diverse legitimate preferences on unaligned model outputs.

**Rationale**: Establishes the starting state of the causal chain (Step 1). High baseline entropy validates that diversity exists before RLHF intervention, confirming this is not a ceiling effect where entropy was already low.

**Variables**:
- Independent: Model training stage (base vs RLHF-tuned)
- Dependent: Preference entropy H (bits)
- Controlled: Prompt set (fixed 1K from Anthropic-HH), user population

**Verification Protocol**:
1. Load base Pythia-1B model (checkpoint: step-0, no RLHF).
2. Generate responses for 1K Anthropic-HH prompts.
3. Collect pairwise preferences (base vs RLHF-tuned responses, n=50 labelers per prompt).
4. Compute preference entropy H for base model responses.
5. Compare to RLHF-tuned entropy (expectation: base > RLHF).

**Success Criteria**:
- Primary: Base model entropy H > 0.6 bits (above midpoint of [0, 1] range for binary)
- Secondary: Base entropy > RLHF-tuned entropy (directional confirmation)

**Failure Response**:
- IF fails: EXPLORE (check if prompts too objective, or population too homogeneous)

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Causal Step 1

---

#### H-M2: Early RLHF Shows Justified Entropy Reduction

**Statement**: Under early RLHF training (steps 1K-5K), if model quality improves (win rate increases), then entropy decreases proportionally to performance gains (ΔH/ΔP approximately constant), because users converge on preferences as model outputs become less ambiguous.

**Rationale**: Validates the "justified reduction" phase (Step 2). Confirms that initial entropy decrease is explained by quality improvement, not premature monoculture. Sets baseline ΔH/ΔP ratio for detecting inflection point in H-M3.

**Variables**:
- Independent: RLHF training steps (1K, 5K checkpoints)
- Dependent: Entropy H, Performance P (win rate), ΔH/ΔP ratio
- Controlled: Prompt set, user population, preference collection protocol

**Verification Protocol**:
1. Train Pythia-1B with RLHF (PPO) for 5K steps, save checkpoints at 1K, 5K.
2. Collect preferences for each checkpoint on fixed prompt set (n=1K).
3. Compute entropy H and win rate P at each checkpoint.
4. Calculate ΔH/ΔP between checkpoints (base→1K, 1K→5K).
5. Verify ΔH/ΔP ratio remains stable (coefficient of variation <20%).

**Success Criteria**:
- Primary: ΔH/ΔP ratio stable across early checkpoints (CV <20%)
- Secondary: Both H decreases and P increases (negative correlation confirmed)

**Failure Response**:
- IF fails: PIVOT (check if inflection occurs earlier than expected, revise 10K target)

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Causal Step 2

---

#### H-M3: Late RLHF Shows Inflection Point (Entropy Acceleration)

**Statement**: Under continued RLHF training (steps 10K-20K), if performance saturates (ΔP approaches zero), then entropy reduction accelerates (|ΔH/ΔP| increases by ≥50% vs early-stage baseline), because users habituate to model style and converge even without quality improvements.

**Rationale**: Core mechanism hypothesis (Step 3). Detects the inflection point where RLHF crosses from justified to problematic entropy collapse. The ≥50% increase in |ΔH/ΔP| is the primary falsification criterion distinguishing overcorrection from linear reduction.

**Variables**:
- Independent: RLHF training steps (10K, 20K checkpoints)
- Dependent: Entropy H, Performance P, ΔH/ΔP ratio
- Controlled: Same as H-M2

**Verification Protocol**:
1. Continue RLHF training to 20K steps, save checkpoints at 10K, 20K.
2. Compute H, P at each late checkpoint using same protocol as H-M2.
3. Calculate late-stage ΔH/ΔP (10K→20K).
4. Compare to early-stage baseline from H-M2: Compute ratio (late |ΔH/ΔP|) / (early |ΔH/ΔP|).
5. Apply segmented regression to detect change point in ΔH/ΔP slope.

**Success Criteria**:
- Primary: |ΔH/ΔP| increases by ≥50% in late stage vs early stage
- Secondary: Inflection point detected at 10K steps ±2K (segmented regression)

**Failure Response**:
- IF fails: ABANDON (no inflection point = H0 supported, entropy reduction linear with performance)

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Causal Step 3, Prediction P1

---

#### H-M4: Subjective Tasks Show Greater Entropy Collapse

**Statement**: Under task stratification (objective factual QA vs subjective creative/opinion), if we compare ΔH/ΔP ratios between task types, then subjective tasks show ≥1.5x larger entropy reduction, because diversity loss on subjective tasks indicates monoculture imposition rather than justified consensus.

**Rationale**: Distinguishes legitimate from problematic entropy collapse (Step 4). Objective tasks should converge (users agree on correct answers), but subjective tasks should preserve diversity (no ground truth). Differential entropy reduction validates the "preference monoculture" interpretation.

**Variables**:
- Independent: Task type (objective vs subjective classification)
- Dependent: ΔH/ΔP ratio (base → RLHF-20K)
- Controlled: Prompt set balanced across task types

**Verification Protocol**:
1. Classify Anthropic-HH prompts into objective (factual QA, n=500) vs subjective (creative, opinion, n=500).
2. Compute ΔH/ΔP separately for each task type (base → RLHF-20K).
3. Calculate ratio: (subjective ΔH/ΔP) / (objective ΔH/ΔP).
4. Test statistical significance (bootstrap 95% CI excludes 1.0).
5. Validate that objective task entropy reduction is performance-justified (lower residual).

**Success Criteria**:
- Primary: Subjective ΔH/ΔP ≥1.5x objective ΔH/ΔP
- Secondary: Objective task ΔH/ΔP explained by performance gains (within 10% of baseline expectation)

**Failure Response**:
- IF fails: EXPLORE (check task classification validity, or refine objective/subjective boundary)

**Dependencies**: H-M3

**Source**: Phase 2A Section 1.3 Causal Step 4, Prediction P2

---

### 2.3 Risk Analysis

#### Assumption-Risk Mapping

| Risk ID | Source | Risk Description | Severity | Affected Hypotheses |
|---------|--------|------------------|----------|---------------------|
| R1 | A1 | Entropy orthogonal to critical thinking (entropy measures confusion, not agency) | High | H-E1, H-M1-M4 |
| R2 | A2 | RLHF stops before inflection point (early stopping prevents overcorrection) | High | H-M3 |
| R3 | A3 | Subjective tasks converge to ground truth (users learn "correct" creative style) | Medium | H-M4 |
| R4 | A4 | Population shifts drive entropy changes (confound: different labelers, not model influence) | High | H-M1-M4 |
| R5 | A5 | Datasets lack raw distributions (only aggregated win rates available) | Critical | All |

#### Mitigation Strategies

**Risk R1: Entropy Measurement Validity**

**Source Assumption:** A1 - Preference entropy is a valid proxy for human critical evaluation capacity

**Description:** If entropy measures user confusion rather than critical diversity, low entropy could indicate task clarity, not agency loss. The hypothesis mechanism fails if entropy is orthogonal to critical thinking (e.g., users show low entropy but high override rates when given override options).

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3, H-M4

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use task stratification (H-M4) to separate objective tasks (clarity-driven convergence) from subjective tasks (monoculture-driven convergence)
2. **Detection:** Monitor override rates in validation set. If entropy low but override high → confusion, not convergence
3. **Response:**
   - PIVOT: Add auxiliary measure (user confidence ratings, response time) to distinguish confusion from convergence
   - SCOPE: Restrict claims to "preference homogenization" rather than "agency loss"
   - ABORT: If subjective tasks show no differential entropy reduction (H-M4 fails), mechanism unsupported

**Early Warning Indicators:**
- Entropy decreases uniformly across all task types (no objective/subjective distinction)
- User confidence scores decrease as entropy decreases (indicates confusion)

---

**Risk R2: Inflection Point Non-Existence**

**Source Assumption:** A2 - RLHF training can continue beyond performance saturation (inflection point exists)

**Description:** If RLHF implementations always stop before inflection point (performance-based early stopping), the overcorrection phenomenon may not occur in practice. Hypothesis proves theoretical risk but lacks practical relevance.

**Affected Hypotheses:** H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use fixed-step RLHF training (20K steps) without early stopping to ensure late-stage training occurs
2. **Detection:** Monitor performance plateau. If P saturates before 10K steps, inflection window missed
3. **Response:**
   - PIVOT: Extend training to 30K-50K steps if saturation occurs early
   - SCOPE: Document finding as "inflection point exists but occurs beyond typical training duration"
   - ABORT: If ΔH/ΔP remains constant across all checkpoints (H-M3 falsified), supports H0 (linear reduction)

**Early Warning Indicators:**
- Performance saturates before 5K steps (early plateau)
- Training instability after 15K steps (indicates over-optimization)

---

**Risk R3: Subjective Task Ground Truth Emergence**

**Source Assumption:** A3 - Subjective tasks legitimately support diverse preferences (no single correct answer)

**Description:** If users learn "correct" creative/opinion styles over time (e.g., professional writing norms, consensus opinion formation), entropy reduction on subjective tasks could be justified by users converging to discovered ground truth rather than imposed monoculture.

**Affected Hypotheses:** H-M4

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Use diverse subjective task categories (creative writing, opinion, stylistic preference) to reduce single-norm convergence risk
2. **Detection:** Compare entropy reduction rates across subjective subcategories. If uniform → legitimate, if variable → monoculture
3. **Response:**
   - PIVOT: Refine subjective task definition to exclude "emerging consensus" tasks (e.g., professional standards)
   - SCOPE: Narrow claims to "pure opinion" tasks where no consensus should exist
   - ABORT: If objective and subjective tasks show identical entropy reduction patterns (within 20% difference), monoculture claim unsupported

**Early Warning Indicators:**
- Subjective task entropy reduction correlates with task "professionalization" indicators
- Expert labelers show lower entropy than novice labelers on subjective tasks

---

**Risk R4: Population Confound**

**Source Assumption:** A4 - Cross-user preference entropy reflects collective critical diversity, not just population heterogeneity

**Description:** If entropy changes are driven by population composition shifts (different labelers at different training stages), we measure confound, not mechanism. Without within-user entropy tracking, we cannot distinguish model influence from demographic drift.

**Affected Hypotheses:** H-M1, H-M2, H-M3, H-M4

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use same labeler pool across all checkpoints, or demographically match samples if pool unavailable
2. **Detection:** Collect labeler metadata (demographics, expertise). Test if entropy changes correlate with population shifts
3. **Response:**
   - PIVOT: Add labeler-fixed-effects analysis to isolate model influence from population heterogeneity
   - SCOPE: Restrict claims to "population-level entropy reduction" with confound caveat
   - ABORT: If entropy reduction fully explained by population shifts (labeler-fixed-effects null), mechanism confounded

**Early Warning Indicators:**
- Labeler demographics change significantly across checkpoints
- Entropy reduction correlates with labeler turnover rate

---

**Risk R5: Raw Data Unavailability**

**Source Assumption:** A5 - Existing RLHF preference datasets (Anthropic-HH, WebGPT) contain sufficient raw preference distributions to compute entropy (not just aggregated win rates)

**Description:** If datasets only publish summary statistics (mean win rate), entropy cannot be calculated. Entire measurement approach fails without raw preference counts.

**Affected Hypotheses:** All (H-E1, H-M1, H-M2, H-M3, H-M4)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Verify dataset raw data availability during H-E1 verification before committing to full experiment
2. **Detection:** Immediate - download and inspect Anthropic-HH data structure in H-E1
3. **Response:**
   - PIVOT: If Anthropic-HH lacks raw data, collect new preference data on small scale (n=500 prompts, 50 labelers each)
   - SCOPE: Reduce to proof-of-concept with limited dataset (sacrifice statistical power for feasibility)
   - ABORT: If no raw data available and new collection infeasible (exceeds resource constraints), mechanism untestable

**Early Warning Indicators:**
- Anthropic-HH repository contains only aggregated metrics in README
- Dataset documentation mentions "privacy-preserving aggregation"

---

#### Risk Summary

| Category | Count | Severity Distribution |
|----------|-------|----------------------|
| Critical | 1 | R5 |
| High | 3 | R1, R2, R4 |
| Medium | 1 | R3 |
| Low | 0 | - |

**Total Risks:** 5 (mapped 1:1 from assumptions A1-A5)

**Highest Priority Mitigations:**
1. R5: Verify raw data availability in H-E1 (immediate gate)
2. R2: Use fixed-step training without early stopping
3. R1/R4: Implement task stratification and labeler controls

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1: Preference Entropy Exists and is Computable
         │
         │ (MUST PASS gate - entire approach depends on this)
         ▼
[Level 1 - Baseline Establishment]
    H-M1: Base Model High-Variance Establishes Baseline Entropy
         │
         │ (MUST PASS gate - confirms starting state)
         ▼
[Level 2 - Justified Reduction]
    H-M2: Early RLHF Shows Justified Entropy Reduction
         │
         │ (MUST PASS gate - sets baseline ΔH/ΔP ratio)
         ▼
[Level 3 - Inflection Point]
    H-M3: Late RLHF Shows Inflection Point (Entropy Acceleration)
         │
         │ (MUST PASS gate - core mechanism hypothesis)
         ▼
[Level 4 - Monoculture Evidence]
    H-M4: Subjective Tasks Show Greater Entropy Collapse
         │
         │ (MUST PASS gate - distinguishes legitimate from problematic)
         ▼
[Terminal - Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 (100% serial)
═══════════════════════════════════════════════════════════
```

**Dependency Analysis:**
- **Total Depth:** 5 levels (sequential chain)
- **Parallelization:** None (each hypothesis depends on previous)
- **Bottleneck:** H-M3 (inflection point detection) - longest verification (~4 weeks for RLHF training to 20K steps)
- **Early Exit:** Failure at any gate stops verification (each hypothesis is MUST PASS)

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_PASS | Entropy computable for ≥95% of prompts | ABANDON (mechanism untestable) |
| H-M1 | MUST_PASS | Base entropy H > 0.6 bits | EXPLORE (check prompt objectivity or population homogeneity) |
| H-M2 | MUST_PASS | ΔH/ΔP ratio stable (CV <20%) in early training | PIVOT (check if inflection occurs earlier, revise 10K target) |
| H-M3 | MUST_PASS | |ΔH/ΔP| increases ≥50% in late vs early stage | ABANDON (no inflection = H0 supported, linear reduction) |
| H-M4 | MUST_PASS | Subjective ΔH/ΔP ≥1.5x objective ΔH/ΔP | EXPLORE (refine task classification or boundary) |

### 3.3 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses (8 Weeks)
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis        │ W1  │ W2  │ W3  │ W4  │ W5  │ W6  │ W7  │ W8  │
────────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
PHASE 1: Foundation
  H-E1: Entropy Exists  │ ████│     │     │     │     │     │     │     │
  [Gate 1: MUST PASS]   │     │  ◆  │     │     │     │     │     │     │
────────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
PHASE 2: Mechanisms
  H-M1: Base Baseline   │     │ ████│     │     │     │     │     │     │
  [Gate M1: MUST PASS]  │     │     │  ◆  │     │     │     │     │     │
  H-M2: Early Justified │     │     │ ████│████ │     │     │     │     │
  H-M3: Inflection Pt   │     │     │     │ ████│████ │████ │     │     │
  [Gate M2-M3: CRITICAL]│     │     │     │     │     │     │  ◆  │     │
  H-M4: Subjective Task │     │     │     │     │     │     │ ████│     │
  [Gate M4: MUST PASS]  │     │     │     │     │     │     │     │  ◆  │
────────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
Critical Path: All hypotheses (100% serial, no parallel work)
Bottleneck: H-M3 (3 weeks RLHF training to 20K steps + checkpoint analysis)
═══════════════════════════════════════════════════════════════════════════
```

**Phase Breakdown:**

| Phase | Hypotheses | Duration | Key Activities |
|-------|------------|----------|----------------|
| Phase 1: Foundation | H-E1 | 1 week | Download Anthropic-HH, parse pairwise data, compute entropy for sample prompts, validate measurement |
| Phase 2.1: Baseline | H-M1 | 1 week | Load base Pythia-1B, generate responses, collect preferences (n=50 labelers × 1K prompts), compute baseline entropy |
| Phase 2.2: Early RLHF | H-M2 | 2 weeks | RLHF training 0→5K steps (checkpoints at 1K, 5K), preference collection per checkpoint, compute ΔH/ΔP ratio |
| Phase 2.3: Late RLHF | H-M3 | 3 weeks | RLHF training 5K→20K steps (checkpoints at 10K, 20K), preference collection, inflection point detection via segmented regression |
| Phase 2.4: Stratification | H-M4 | 1 week | Classify prompts objective/subjective, recompute ΔH/ΔP per task type, statistical significance test (bootstrap 95% CI) |

**Total Duration:** 8 weeks

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 (all sequential)

**Resource Requirements:**
- **Compute:** 1× GPU (NVIDIA A100 or equivalent) for RLHF training (Weeks 3-7)
- **Human Labeling:** 50 labelers × 1K prompts × 5 checkpoints = 250K pairwise comparisons (can reuse existing Anthropic-HH labels for base vs RLHF-tuned, new labels needed for intermediate checkpoints)
- **Storage:** ~50GB (model checkpoints + preference datasets)

---
## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** RLHF training induces preference entropy collapse beyond performance-justified levels. Under extended RLHF optimization (10K-20K steps), entropy reduction accelerates beyond performance gains (inflection point), particularly on subjective tasks, indicating preference monoculture imposition rather than legitimate consensus.

**Supporting Evidence:**
1. **Causal Mechanism** (Phase 2A Section 1.3): Four-step chain from base high-variance → early justified reduction → late inflection point → subjective task monoculture. Each step builds on prior RLHF literature (InstructGPT, Constitutional AI) while identifying novel overcorrection phase.
2. **Key Assumptions** (A1-A5): Entropy as critical evaluation proxy (information theory), inflection point existence (fixed-step training without early stopping), subjective task diversity legitimacy (no ground truth), cross-user entropy as collective measure (controlled demographics), raw data availability (Anthropic-HH pairwise comparisons).
3. **Testable Predictions** (P1-P3): Inflection point at 10K steps ±2K with |ΔH/ΔP| increase ≥50%, subjective ΔH/ΔP ≥1.5x objective, RLHF shows 30%+ excess entropy reduction vs performance-predicted baseline.

**Strengths:**
- **Grounded in Established Theory:** Builds on validated RLHF training dynamics (preference agreement improves) while adding novel entropy lens. Information-theoretic entropy is standard diversity measure.
- **Clear Causal Mechanism:** Four-step chain with explicit falsifiers per step. Inflection point detection via segmented regression is standard change-point analysis method.
- **Quantitative Falsification:** Primary prediction (≥50% ΔH/ΔP increase) and secondary prediction (≥1.5x task stratification) provide clear thresholds. H0 rejection requires both criteria.
- **Leverages Existing Data:** Uses public Anthropic-HH dataset, reducing data collection burden. Entropy computable from existing pairwise comparison structure.

**Expected Outcomes:**
- Primary: Inflection point detected at RLHF-10K steps (±2K) where entropy reduction decouples from performance gains
- Secondary: Subjective tasks show greater entropy collapse than objective tasks when controlling for performance
- Tertiary: RLHF-tuned models show excess entropy reduction (30%+) beyond objective task baseline expectation

---

### 4.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in the entropy-reduction-per-performance-gain ratio (dH/dP) between RLHF training phases. Entropy reduction is fully explained by task quality improvements. No inflection point exists — convergence is linear.

**Counter-Arguments:**
1. **Baseline Limitations:** Prior work (InstructGPT, Constitutional AI) measures preference agreement as success but does NOT measure entropy. Absence of entropy measurement ≠ evidence of overcorrection absence. Baselines may have undetected monoculture.
2. **Assumption Violations:** Each assumption (A1-A5) carries high risk. R1 (entropy validity): Entropy may measure confusion, not agency. R2 (inflection existence): Early stopping may prevent overcorrection in practice. R4 (population confound): Different labelers across checkpoints could explain entropy changes without model influence.
3. **Scope Limitations:** Hypothesis applies only to conversational AI with preference datasets. Does not generalize to SFT (no RL), pure math solvers (objective ground truth), or non-text domains. Narrow applicability limits impact.
4. **Alternative Explanation:** Users may legitimately converge on preferences as they learn "correct" styles through exposure to RLHF outputs. Subjective task entropy reduction could reflect emerging professional norms (e.g., "good" creative writing standards), not imposed monoculture.

**Potential Confounds:**
- **Population Heterogeneity:** Cross-user entropy conflates individual critical thinking with demographic diversity. Cannot distinguish "users agree because AI correct" from "users agree because stopped evaluating critically."
- **Task Classification Subjectivity:** Objective vs subjective boundary requires judgment. Misclassification would invalidate H-M4 task stratification analysis.
- **Dataset-Specific:** Anthropic-HH may have unique properties (e.g., labeler training, prompt selection bias) not generalizable to other RLHF datasets.

**H0-Supporting Scenarios:**
- **Scenario 1:** ΔH/ΔP remains constant (±10%) across all checkpoints → no inflection point, linear reduction, H0 supported
- **Scenario 2:** Objective and subjective tasks show similar ΔH/ΔP ratios (within 20%) → no differential monoculture, convergence legitimate
- **Scenario 3:** Entropy reduction fully explained by performance baseline (within 10% residual) → no excess collapse, quality-driven

---

### 4.3 Synthesis

**Balanced Assessment:**

The thesis proposes a testable mechanism for detecting RLHF overcorrection via entropy inflection point, grounded in established information theory and validated RLHF training dynamics. The antithesis correctly identifies high-risk assumptions (R1 entropy validity, R4 population confound) and scope limitations (narrow applicability), but does not invalidate the core testable predictions.

**Key Tensions Requiring Resolution:**

1. **Entropy Interpretation (Thesis A1 vs Antithesis R1):**
   - **Tension:** Does low entropy indicate critical convergence (thesis) or user confusion (antithesis)?
   - **Resolution:** Task stratification (H-M4) addresses this. If objective tasks show lower entropy (justified consensus) while subjective tasks show comparable reduction (imposed monoculture), thesis supported. If both show identical patterns, antithesis prevails.
   - **Robustness:** Auxiliary measure (user confidence ratings, response time) can distinguish confusion from convergence if added to validation set.

2. **Inflection Point Existence (Thesis A2 vs Antithesis R2):**
   - **Tension:** Does RLHF training continue beyond performance saturation in practice (thesis), or does early stopping prevent overcorrection (antithesis)?
   - **Resolution:** Controlled experiment with fixed 20K-step training (no early stopping) tests theoretical risk. If inflection found, overcorrection possible. If not found, H0 supported.
   - **Practical Relevance:** Even if early stopping prevents inflection in current practice, identifying the threshold informs future safety guidelines (e.g., "stop training at performance plateau").

3. **Population Confound (Thesis A4 vs Antithesis R4):**
   - **Tension:** Does entropy change reflect model influence (thesis) or demographic shifts (antithesis)?
   - **Resolution:** Labeler-fixed-effects analysis or matched sampling controls for population heterogeneity. If entropy reduction persists after controlling for labeler demographics, thesis supported.
   - **Limitation Acknowledged:** Cross-user entropy cannot definitively separate individual critical thinking from collective diversity. Claim must be scoped to "population-level preference homogenization" with confound caveat.

**Synthesis Conclusion:**

The hypothesis is **testable and falsifiable** with clear success criteria (≥50% ΔH/ΔP increase, ≥1.5x task stratification). The antithesis identifies legitimate risks (R1, R2, R4) but these are **addressable via experimental design** (task stratification, fixed-step training, labeler controls). The core mechanism (inflection point detection) survives dialectical challenge if both primary (H-M3) and secondary (H-M4) predictions hold.

**Robustness Assessment:**

- **Strong If:** Both H-M3 (inflection point) and H-M4 (task stratification) pass → mechanism validated, overcorrection demonstrated
- **Moderate If:** H-M3 passes but H-M4 fails → inflection exists but monoculture interpretation unclear (alternative: legitimate convergence)
- **Weak If:** H-M3 fails → no inflection point, H0 supported, entropy reduction linear with performance (antithesis prevails)

**Recommended Contingencies:**

1. If H-M3 fails: Extend training to 30K-50K steps to check if inflection occurs later than expected
2. If H-M4 fails: Refine objective/subjective boundary, or add auxiliary measures (confidence, override rates) to distinguish convergence types
3. If R4 confound detected: Add labeler-fixed-effects to isolate model influence, accept narrower claim scope

---

## 5. Executive Summary

**Main Hypothesis:** RLHF training on preference datasets induces entropy collapse beyond performance-justified levels, with inflection point where entropy reduction accelerates beyond quality gains, particularly on subjective tasks.
- ID: H-EntropyCollapse-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (builds on Phase 2A)
- Sub-Hypotheses: 5 total (H-E1, H-M1-4)
- Duration: 8 weeks sequential execution
- Critical Gates: 5 MUST_PASS decision points
- Bottleneck: H-M3 (3 weeks RLHF training to 20K steps)

**Risk Assessment:** High
- Critical: R5 (raw data availability) — immediate gate in H-E1
- High Priority: R1 (entropy validity), R2 (inflection existence), R4 (population confound)
- Mitigation: Task stratification (H-M4), fixed-step training, labeler controls

**Key Innovation:** First application of information-theoretic entropy to measure bidirectional alignment failure. Distinguishes legitimate convergence (objective tasks) from preference monoculture (subjective tasks).

**Scope Reduction:** 33% efficiency gain (2 of 3 Phase 2A claims are BUILD_ON, only 1 PROVE_NEW requires verification)

**Immediate Action:** Begin Phase 1 - Verify entropy computability on Anthropic-HH dataset (H-E1, Week 1)

---

## 6. Conclusions

### 6.1 Verification Readiness

**Status: READY for Phase 2C (Experiment Design)**

- ✅ 5 sub-hypotheses defined with clear verification protocols
- ✅ Each hypothesis has MUST_PASS gate with explicit success criteria
- ✅ Risk analysis complete with mitigation strategies for all 5 assumptions
- ✅ Dependency graph (DAG) shows sequential critical path
- ✅ Timeline allocated (8 weeks with resource estimates)
- ✅ Dialectical analysis confirms testability and falsifiability

**Falsification Criteria Established:**
- H-M3 (inflection point): If ΔH/ΔP remains constant (±10%) → H0 supported, ABANDON
- H-M4 (task stratification): If subjective ≈ objective (within 20%) → monoculture claim unsupported, EXPLORE

### 6.2 Critical Path

**Execution Order:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4 (100% serial)

**Early Exit Conditions:**
- H-E1 fails (entropy not computable) → ABANDON entire hypothesis
- H-M1 fails (base entropy too low) → EXPLORE prompt/population issues
- H-M2 fails (ΔH/ΔP unstable early) → PIVOT to earlier inflection point
- H-M3 fails (no inflection) → ABANDON (H0 supported)
- H-M4 fails (no task difference) → EXPLORE task boundary refinement

### 6.3 Decision Points

| Week | Gate | Decision | If PASS | If FAIL |
|------|------|----------|---------|---------|
| 1 | H-E1 | Entropy computable? | Proceed to H-M1 | ABANDON (untestable) |
| 2 | H-M1 | Base entropy high? | Proceed to H-M2 | EXPLORE (prompts/population) |
| 4 | H-M2 | Early ΔH/ΔP stable? | Proceed to H-M3 | PIVOT (revise inflection target) |
| 7 | H-M3 | Inflection detected? | Proceed to H-M4 | ABANDON (H0 supported) |
| 8 | H-M4 | Task difference found? | VALIDATED | EXPLORE (task classification) |

---

## 7. Recommendations

### 7.1 Immediate Next Steps

1. **Week 1:** Execute H-E1 verification
   - Download Anthropic-HH from https://github.com/anthropics/hh-rlhf
   - Parse pairwise comparison data structure
   - Compute entropy for n=100 sample prompts
   - Validate entropy range [0, log(2)] for binary comparisons
   - **Decision Gate:** If ≥95% computable → proceed; else ABANDON

2. **Week 2-3:** Prepare RLHF training infrastructure
   - Set up Pythia-1B training environment (GPU allocation)
   - Implement PPO training loop with checkpoint saving (1K, 5K, 10K, 20K steps)
   - Prepare preference collection protocol (Mechanical Turk or equivalent)
   - Recruit n=50 labelers, collect demographic metadata for R4 control

3. **Week 4-7:** Execute mechanism verification (H-M1-M3)
   - Collect baseline preferences (H-M1)
   - Run RLHF training with checkpoints (H-M2-M3)
   - Compute entropy and performance at each checkpoint
   - Perform segmented regression for inflection point detection

### 7.2 Risk Mitigation Priorities

**Priority 1 (Critical):** Verify R5 (raw data availability) in H-E1
- **Action:** Inspect Anthropic-HH data structure before committing resources
- **Contingency:** If raw data unavailable, collect new preferences (n=500 prompts, small-scale proof-of-concept)

**Priority 2 (High):** Control R4 (population confound)
- **Action:** Use same labeler pool across checkpoints or demographically match samples
- **Validation:** Collect labeler metadata, test if entropy correlates with turnover

**Priority 3 (High):** Address R1 (entropy validity)
- **Action:** Implement task stratification (H-M4) as primary mitigation
- **Enhancement:** Add auxiliary measures (user confidence, response time) if H-M4 shows ambiguous results

### 7.3 Open Questions for Phase 2C

1. **Experiment Design Refinement:** Can we design entropy-preserving RLHF variants for comparison in Phase 5? (e.g., entropy-regularized reward function)
2. **Generalization:** Does inflection point location (10K vs 20K steps) vary predictably with model size or dataset size?
3. **Causal Intervention:** Can we test causality by manipulating training duration (stop at 5K vs continue to 20K) in A/B design?

---

## 8. Appendices

### Appendix A: Established Facts (Scope Reduction)

**BUILD_ON Claims (DO NOT re-verify):**
1. RLHF training reduces preference variance compared to base models (Ouyang et al. InstructGPT, Bai et al. Constitutional AI)
2. Preference entropy is a valid information-theoretic measure of diversity (Shannon entropy established metric)

**PROVE_NEW Claim (requires verification):**
1. Current RLHF benchmarks measure preference agreement, not preference diversity (Phase 1 gap analysis — absent human agency metrics)

**Scope Reduction:** 33% (2 of 3 claims skip verification)

### Appendix B: Phase 2A Alignment

**Phase 2A Output Source:** 03_refinement.yaml (10.0.0 schema)

**Mapping Completeness:**
- Core Statement → Section 1 Hypothesis Overview ✓
- Variables (IV/DV/CV) → Hypothesis Specifications ✓
- Causal Mechanism (4 steps) → H-M1-M4 ✓
- Key Assumptions (A1-A5) → Risk Analysis (R1-R5) ✓
- Testable Predictions (P1-P3) → Success Criteria ✓
- Alternative Hypothesis H0 → Dialectical Antithesis ✓
- Experimental Setup (Dataset, Model) → Section 1.3 ✓

**No Gaps:** All Phase 2A sections incorporated

### Appendix C: Hypothesis Type Distribution

| Type | Count | Purpose | IDs |
|------|-------|---------|-----|
| EXISTENCE | 1 | Validate phenomenon exists | H-E1 |
| MECHANISM | 4 | Test causal chain steps | H-M1-M4 |
| CONDITION | 0 | Boundary conditions (optional, not needed) | - |

**Total:** 5 hypotheses (range: 2-7 dynamic based on causal chain length)

**Note:** H-CP (Comparison) hypotheses moved to Phase 5 Baseline Comparison.

### Appendix D: Resource Summary

**Compute Requirements:**
- 1× GPU (NVIDIA A100 or equivalent): Weeks 3-7 (RLHF training)
- Estimated GPU-hours: ~120 hours (20K RLHF steps + checkpoints)

**Human Labeling:**
- 50 labelers × 1K prompts × 5 checkpoints = 250K pairwise comparisons
- Labeling Cost Estimate (at $0.10/comparison): $25,000
- **Cost Reduction:** Reuse existing Anthropic-HH labels for base vs final RLHF-tuned; new labels needed only for intermediate checkpoints (reduces to ~100K comparisons, $10,000)

**Storage:**
- Model checkpoints: 5 checkpoints × 10GB = 50GB
- Preference datasets: ~5GB

**Timeline:** 8 weeks sequential execution (no parallelization)

---

**END OF VERIFICATION PLAN**
