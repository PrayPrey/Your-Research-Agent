# Verification Plan: SE-Distilled Probes with Similarity Augmentation (SEDPs)

**Date:** 2026-03-28
**Hypothesis ID:** H-SEDP-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the condition of transformer-based LLMs performing question-answering tasks, if we train a probe to predict semantic entropy (SE) using hidden state features with semantic similarity structure as an auxiliary training signal, then the probe will achieve (1) single-pass SE prediction with Spearman rho ≥ 0.7 versus true SE, AND (2) cross-model transfer with rho ≥ 0.5, because the similarity structure provides model-agnostic regularization that prevents overfitting to model-specific hidden state patterns.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in cross-model transfer performance between similarity-augmented probes and hidden-state-only probes. Specifically, the Spearman correlation between SEDP predictions and true SE on cross-model test is not significantly greater than that of vanilla SEPs (hidden-only probes).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | Standard benchmark for hallucination detection; diverse question categories; established SE evaluation dataset |
| **Model** | Llama-3-8B-Instruct / Mistral-7B-Instruct-v0.2 | Open-weight models with accessible hidden states; different architectures for transfer testing |

**Dataset Details:**
- Source: https://github.com/sylinrl/TruthfulQA
- Path: huggingface: truthful_qa

**Model Details:**
- Type: decoder-only transformer LLM
- Source: HuggingFace: meta-llama/Meta-Llama-3-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.2

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Full SE (N=20) | AUROC 0.76-0.97 | TruthfulQA, TriviaQA |
| Semantic Entropy Probes | AUROC ~0.85 (within 2-3% of full SE) | TruthfulQA |
| First-Token Entropy | rho = 0.13 with SE | TruthfulQA |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Hidden states contain sufficient information to predict SE | SEPs (Kossen et al. 2024) achieve AUROC close to full SE using only hidden states | No single-pass SE proxy is possible from internal representations |
| A2 | Semantic similarity structure computed on generated text is model-agnostic | True by construction: similarity is computed on output tokens, not internal activations | Would require model-specific similarity computation, defeating transfer purpose |
| A3 | Similarity-augmented training improves generalization to new models | Inspired by KLE's model-agnostic approach; to be empirically validated | SEDP reduces to vanilla SEP with no transfer benefit; still valuable for speedup |
| A4 | TruthfulQA is representative of broader QA uncertainty patterns | Standard benchmark for hallucination; diverse question types | Results may not generalize to other QA domains; need additional benchmarks |
| A5 | DeBERTa-v3 NLI adequately captures semantic equivalence for clustering | Used in original SE paper; state-of-the-art NLI model | SE labels themselves would be noisy, affecting all downstream results |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Cross-model transfer of SE proxies via similarity-augmented training

**Key Innovation:** Using semantic similarity structure as auxiliary training signal to encourage model-agnostic feature learning, enabling probe trained on one model to transfer to another

**Differentiation:**
- vs SEPs (Kossen et al. 2024): SEPs train on hidden states only; SEDP adds similarity auxiliary signal targeting cross-model transfer
- vs Semantic Self-Distillation (Phillips et al. 2026): SSD uses full student model; SEDP uses lightweight probe with similarity augmentation
- vs Pre-trained UQ Heads (Shelmanov et al. 2025): UQ Heads use attention patterns; SEDP uses output-space similarity for architecture-agnostic approach

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | PENDING |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | PENDING |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | PENDING |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | PENDING |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Same-Model SE Prediction Existence

**Statement**: Under the condition of a trained SEDP probe on Llama-3-8B-Instruct, if the probe receives hidden states from the same model, then it produces SE predictions with Spearman rho ≥ 0.3 versus true SE, because hidden states contain information predictive of semantic uncertainty.

**Rationale**: This validates the fundamental assumption that a probe can learn to predict SE from hidden states with similarity augmentation. Without same-model prediction capability, cross-model transfer is impossible. SEPs have demonstrated this is achievable; we extend with similarity.

**Variables**:
- Independent: probe_input_configuration (hidden_states_plus_similarity)
- Dependent: se_correlation (Spearman rho)
- Controlled: TruthfulQA dataset, N=20 SE computation, 2-layer MLP architecture

**Verification Protocol**:
1. Generate N=20 responses per TruthfulQA question using Llama-3-8B-Instruct (temp=0.7)
2. Compute true SE via DeBERTa-v3 NLI clustering for each question
3. Extract final-layer hidden states and compute similarity matrices
4. Train SEDP probe (2-layer MLP, 256 units) on train split (~650 questions)
5. Evaluate Spearman correlation on test split (~160 questions)

**Success Criteria**:
- Primary: Spearman rho ≥ 0.3 (meaningful correlation exists)
- Secondary: rho ≥ 0.7 (matches Phase 2A prediction P1)

**Failure Response**:
- IF rho < 0.3: ABANDON (fundamental approach invalid)
- IF 0.3 ≤ rho < 0.7: EXPLORE (investigate architecture/layer selection)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: SE Label Generation Pipeline

**Statement**: Under the condition of N=20 temperature-sampled responses per question, if we apply NLI-based semantic clustering, then we obtain valid SE labels with meaningful variance (mean cluster count 2-15), because diverse sampling produces semantically distinct response clusters.

**Rationale**: Valid SE labels are prerequisite for all downstream training. Degenerate clustering (all same or all different) would invalidate the entire approach. This validates the data generation pipeline.

**Variables**:
- Independent: N (number of samples), temperature
- Dependent: SE label validity (cluster count distribution)
- Controlled: DeBERTa-v3-large NLI model, TruthfulQA questions

**Verification Protocol**:
1. Generate N=20 responses per question with temperature=0.7
2. Compute pairwise NLI entailment scores for each response set
3. Apply semantic clustering to form equivalence classes
4. Compute mean and variance of cluster counts across all questions
5. Verify cluster count distribution: mean in [2, 15], variance > 0

**Success Criteria**:
- Primary: Mean cluster count in range [2, 15] (not degenerate)
- Secondary: SE variance > 0.1 across questions (meaningful signal)

**Failure Response**:
- IF degenerate clustering: PIVOT to different N or temperature settings

**Dependencies**: H-E1 (existence confirmed first)

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Similarity Structure Informativeness

**Statement**: Under the condition of computed pairwise NLI entailment scores, if we construct similarity matrices for response sets, then the matrices contain informative structure (variance > 0.01), because semantically related responses cluster while unrelated ones separate.

**Rationale**: The similarity auxiliary signal must be informative to provide training benefit. Uniform or random similarity matrices would contribute nothing. This validates the auxiliary signal quality.

**Variables**:
- Independent: similarity_computation_method (NLI entailment)
- Dependent: similarity_informativeness (matrix variance)
- Controlled: DeBERTa-v3-large, response sets from H-M1

**Verification Protocol**:
1. For each question's response set, compute pairwise NLI entailment scores
2. Construct 20x20 similarity matrix per question
3. Compute variance of similarity values within each matrix
4. Aggregate: mean variance across all questions
5. Verify: mean variance > 0.01 (not uniform)

**Success Criteria**:
- Primary: Mean similarity variance > 0.01 (informative structure)
- Secondary: Correlation between similarity structure and SE > 0 (relevant to target)

**Failure Response**:
- IF variance ≤ 0.01: PIVOT to alternative similarity computation (e.g., embedding cosine)

**Dependencies**: H-M1 (valid SE labels required)

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Cross-Model Transfer via Similarity Augmentation

**Statement**: Under the condition of a SEDP probe trained on Llama-3-8B, if we evaluate on Mistral-7B hidden states, then cross-model transfer achieves rho ≥ 0.5, AND SEDP outperforms hidden-only SEP on transfer (SEDP_rho > SEP_rho), because similarity augmentation encourages model-agnostic feature learning.

**Rationale**: This is the core novel contribution. If similarity augmentation doesn't improve cross-model transfer over hidden-only probes, the approach reduces to vanilla SEPs. This directly tests the key innovation.

**Variables**:
- Independent: probe_type (SEDP vs SEP), test_model (Mistral-7B)
- Dependent: cross_model_correlation (Spearman rho on target model)
- Controlled: Same test questions, identical probe architecture, same SE computation

**Verification Protocol**:
1. Train both SEDP (hidden+similarity) and SEP (hidden-only) on Llama-3-8B
2. Generate Mistral-7B responses for same TruthfulQA test questions
3. Compute true SE for Mistral-7B responses
4. Apply both probes to Mistral-7B hidden states (with dimension projection if needed)
5. Compare correlations: SEDP_rho vs SEP_rho using paired t-test

**Success Criteria**:
- Primary: SEDP cross-model rho ≥ 0.5
- Secondary: SEDP_rho > SEP_rho (p < 0.05)

**Failure Response**:
- IF SEDP_rho < 0.3: ABANDON cross-model transfer goal
- IF SEDP_rho ≈ SEP_rho: EXPLORE alternative augmentation strategies

**Dependencies**: H-M2 (informative similarity structure required)

**Source**: Phase 2A Causal Steps 4-5, Prediction P2

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Likelihood |
|------|--------|---------------------|----------|------------|
| R1 | A1 | H-E1, H-M1, H-M2, H-M3 | High | Low |
| R2 | A2 | H-M3 | Medium | Low |
| R3 | A3 | H-M3 | High | Medium |
| R4 | A4 | All | Medium | Medium |
| R5 | A5 | H-M1, H-M2 | High | Low |

### 3.2 Risk Details & Mitigation Strategies

---

**Risk R1: Hidden States Lack Sufficient SE Information**

**Source Assumption:** A1 - Hidden states contain sufficient information to predict SE

**Description:** If hidden states do not encode information predictive of semantic uncertainty, probing will fail regardless of architecture or training approach.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3

**Severity:** High (foundational assumption)

**Mitigation Strategy:**
1. **Prevention:** Use validated approach from SEPs paper (Kossen et al. 2024) which demonstrated this is achievable
2. **Detection:** Monitor H-E1 same-model correlation; if rho < 0.3, assumption violated
3. **Response:**
   - PIVOT: Try different hidden layers (intermediate vs final)
   - SCOPE: Focus on attention patterns instead of hidden states
   - ABORT: If all layers fail, fundamental approach invalid

**Early Warning Indicators:**
- Training loss not decreasing
- Correlation near zero on validation set

---

**Risk R2: Similarity Not Truly Model-Agnostic**

**Source Assumption:** A2 - Semantic similarity computed on generated text is model-agnostic

**Description:** If similarity computation somehow depends on model-specific characteristics (e.g., tokenization artifacts), transfer benefit may be illusory.

**Affected Hypotheses:** H-M3

**Severity:** Medium (affects transfer, not existence)

**Mitigation Strategy:**
1. **Prevention:** Compute similarity on detokenized text, not token sequences
2. **Detection:** Compare similarity distributions across models; should be similar
3. **Response:**
   - PIVOT: Use character-level or sentence-level similarity
   - SCOPE: Accept model-specific similarity but verify transfer still works

**Early Warning Indicators:**
- Systematic differences in similarity distributions between Llama and Mistral
- High variance in cross-model similarity correlations

---

**Risk R3: Similarity Augmentation Provides No Transfer Benefit**

**Source Assumption:** A3 - Similarity-augmented training improves generalization to new models

**Description:** The core hypothesis may be wrong: similarity auxiliary signal might not encourage model-agnostic features. SEDP would then be equivalent to vanilla SEP.

**Affected Hypotheses:** H-M3 (core hypothesis)

**Severity:** High (key innovation at risk)

**Mitigation Strategy:**
1. **Prevention:** Design ablation study comparing SEDP vs SEP on cross-model transfer
2. **Detection:** Statistical comparison of transfer performance (paired t-test)
3. **Response:**
   - PIVOT: Try alternative augmentation strategies (contrastive loss, multi-model training)
   - SCOPE: Accept per-model probes (still valuable for 10x speedup)
   - ABORT: If no transfer benefit, focus on single-model efficiency gains

**Early Warning Indicators:**
- SEDP and SEP achieve similar cross-model rho
- Similarity features have low weight in trained probe

---

**Risk R4: TruthfulQA Not Representative of Broader QA**

**Source Assumption:** A4 - TruthfulQA is representative of broader QA uncertainty patterns

**Description:** Results on TruthfulQA may not generalize to other QA benchmarks or real-world applications.

**Affected Hypotheses:** All (external validity)

**Severity:** Medium (limits generalization, not validity)

**Mitigation Strategy:**
1. **Prevention:** Acknowledge limitation in scope; plan future validation on TriviaQA, SciQ
2. **Detection:** If resources permit, run validation on secondary benchmark
3. **Response:**
   - SCOPE: Frame results as TruthfulQA-specific with transfer hypothesis
   - EXTEND: Add secondary benchmark in Phase 5 if initial results promising

**Early Warning Indicators:**
- Unusual SE distribution compared to literature
- Poor calibration on specific question categories

---

**Risk R5: DeBERTa NLI Produces Noisy SE Labels**

**Source Assumption:** A5 - DeBERTa-v3 NLI adequately captures semantic equivalence for clustering

**Description:** If NLI-based clustering produces unreliable SE labels, all downstream training is compromised.

**Affected Hypotheses:** H-M1, H-M2 (data quality)

**Severity:** High (affects all training)

**Mitigation Strategy:**
1. **Prevention:** Use same NLI model as original SE paper (validated approach)
2. **Detection:** Check SE label statistics (cluster count distribution, variance)
3. **Response:**
   - PIVOT: Try alternative NLI models (RoBERTa-large-MNLI)
   - SCOPE: Focus on high-confidence SE labels only

**Early Warning Indicators:**
- Degenerate clustering (all same or all different)
- SE variance near zero

---

### 3.3 Risk Summary

| ID | Risk | Severity | Likelihood | Priority | Mitigation |
|----|------|----------|------------|----------|------------|
| R1 | Hidden states lack SE info | High | Low | Medium | Use validated SEP approach |
| R2 | Similarity not model-agnostic | Medium | Low | Low | Compute on detokenized text |
| R3 | No transfer benefit from similarity | High | Medium | **Critical** | Ablation study SEDP vs SEP |
| R4 | TruthfulQA not representative | Medium | Medium | Medium | Acknowledge scope limitation |
| R5 | Noisy SE labels from NLI | High | Low | Medium | Use validated DeBERTa-v3 |

**Risk Counts:**
- Critical: 1 (R3)
- High: 2 (R1, R5)
- Medium: 2 (R2, R4)
- Low: 0

---

## 4. Dependency Graph

### 4.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Same-Model SE Prediction     │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: None                │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 1 - Pipeline Validation]
    ┌─────────────────────────────────────┐
    │  H-M1: SE Label Generation          │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: H-E1                │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Signal Quality]
    ┌─────────────────────────────────────┐
    │  H-M2: Similarity Informativeness   │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: H-M1                │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Core Innovation]
    ┌─────────────────────────────────────┐
    │  H-M3: Cross-Model Transfer         │
    │  Gate: SHOULD_WORK                  │
    │  Prerequisites: H-M2                │
    └─────────────────────────────────────┘
                      │
                      ▼
              [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Levels: 4 (sequential, no parallelization)
═══════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Title | Prerequisites | Gate Type |
|-------|------------|-------|---------------|-----------|
| 0 | H-E1 | Same-Model SE Prediction | None | MUST_WORK |
| 1 | H-M1 | SE Label Generation Pipeline | H-E1 | MUST_WORK |
| 2 | H-M2 | Similarity Structure Informativeness | H-M1 | MUST_WORK |
| 3 | H-M3 | Cross-Model Transfer via Similarity | H-M2 | SHOULD_WORK |

### 4.3 Verification Phases

**Phase 1 - Foundation (H-E1)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Probe produces SE predictions with rho > 0.3 | MUST_WORK |

→ **Gate 1**: If H-E1 fails (rho < 0.3) → STOP, fundamental approach invalid.

**Phase 2 - Pipeline Validation (H-M1, H-M2)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-M1 | Valid SE labels (cluster count 2-15) | MUST_WORK |
| H-M2 | Informative similarity (variance > 0.01) | MUST_WORK |

→ **Gate 2**: H-M1 and H-M2 must pass. Failure = data pipeline issue.

**Phase 3 - Core Hypothesis (H-M3)**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-M3 | Cross-model rho ≥ 0.5, SEDP > SEP | SHOULD_WORK |

→ **Gate 3**: H-M3 failure = similarity augmentation doesn't help transfer. Fall back to per-model probes.

---

## 5. Execution Plan

### 5.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 5.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | rho ≥ 0.3 same-model | ABANDON entire approach |
| H-M1 | MUST_WORK | Cluster count in [2, 15] | PIVOT to different N/temp |
| H-M2 | MUST_WORK | Similarity variance > 0.01 | PIVOT to alt. similarity |
| H-M3 | SHOULD_WORK | Cross-model rho ≥ 0.5 | SCOPE to per-model probes |

### 5.3 Timeline

| Phase | Hypotheses | Duration | GPU Hours |
|-------|------------|----------|-----------|
| Phase 1 | H-E1 | 1-2 days | 2-3 |
| Phase 2 | H-M1, H-M2 | 1 day | 1-2 |
| Phase 3 | H-M3 | 2-3 days | 3-4 |

**Total Duration:** 4-6 days
**Total GPU Hours:** 6-9 hours (single GPU)

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses (SEDP Cross-Model Transfer)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Day 1-2   │ Day 3     │ Day 4     │ Day 5-6   │
──────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 1: Foundation   │           │           │           │           │
  H-E1 (Existence)    │ ██████████│           │           │           │
  [Gate 1: MUST_WORK] │           │ ◆         │           │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 2: Pipeline     │           │           │           │           │
  H-M1 (SE Labels)    │           │ █████     │           │           │
  H-M2 (Similarity)   │           │      █████│           │           │
  [Gate 2: MUST_WORK] │           │           │ ◆         │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 3: Transfer     │           │           │           │           │
  H-M3 (Cross-Model)  │           │           │ ██████████│███████████│
  [Gate 3: SHOULD]    │           │           │           │          ◆│
══════════════════════╧═══════════╧═══════════╧═══════════╧═══════════╧
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 4-6 days | Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3

Total Duration: 4-6 days
  - H-E1 (Foundation): 2 days
  - H-M1 + H-M2 (Pipeline): 1 day
  - H-M3 (Transfer): 2-3 days

Slack Available: 0 days (all sequential)

Bottleneck Analysis:
  - H-M3 (Cross-Model Transfer) is longest single task
  - Requires both Llama and Mistral inference
  - Mitigation: Prepare Mistral data during H-E1/H-M1

Gate Decision Points:
  - Gate 1 (Day 2): H-E1 pass → continue; fail → STOP
  - Gate 2 (Day 3): H-M1+H-M2 pass → continue; fail → PIVOT
  - Gate 3 (Day 6): H-M3 pass → full success; fail → SCOPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 (Foundation) - Day 1-2
- Train SEDP probe on Llama-3-8B
- Evaluate same-model SE correlation
- Success: rho ≥ 0.3

**Step 2**: Evaluate Gate 1
- If PASS (rho ≥ 0.3): Proceed to Phase 2
- If FAIL (rho < 0.3): STOP - fundamental approach invalid

**Step 3**: Execute H-M1 (SE Labels) - Day 3
- Validate SE label generation pipeline
- Check cluster count distribution
- Success: mean cluster count in [2, 15]

**Step 4**: Execute H-M2 (Similarity) - Day 3
- Validate similarity matrix informativeness
- Check variance statistics
- Success: variance > 0.01

**Step 5**: Evaluate Gate 2
- If PASS: Proceed to Phase 3
- If FAIL: PIVOT to alternative pipeline configuration

**Step 6**: Execute H-M3 (Cross-Model Transfer) - Day 4-6
- Train both SEDP and SEP probes on Llama
- Generate Mistral responses and hidden states
- Apply probes to Mistral, compare performance
- Success: SEDP rho ≥ 0.5, SEDP > SEP (p < 0.05)

**Step 7**: Evaluate Gate 3
- If PASS: Full success - similarity augmentation works
- If PARTIAL (SEDP works but ≈ SEP): Document limitation
- If FAIL (rho < 0.3): SCOPE to per-model probes

**Final**: Verification complete → Proceed to Phase 5 (Baseline Comparison)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Similarity-augmented probes (SEDPs) enable cross-model transfer of semantic entropy prediction, achieving rho ≥ 0.5 when trained on Llama and tested on Mistral.

**Supporting Evidence:**
1. Hidden states contain sufficient information to predict SE (demonstrated by SEPs, Kossen et al. 2024)
2. Semantic similarity computed on generated text is model-agnostic by construction
3. Knowledge distillation from multi-sample SE to single-pass probe is achievable (SSD paper)

**Strengths:**
- Builds on three established foundations: SEPs, SSD, KLE
- Clear causal mechanism with 5 testable steps
- Addresses real production barrier (5-10x SE compute cost)
- Similarity is model-agnostic by design (computed on text outputs)
- Fallback value: even without transfer, achieves 10x speedup per-model

**Expected Outcomes:**
- Primary: SEDP achieves rho ≥ 0.7 same-model, rho ≥ 0.5 cross-model
- Secondary: SEDP outperforms SEP on cross-model transfer (p < 0.05)
- Tertiary: ≥10x inference speedup over full SE computation

---

### 6.2 Antithesis (H0)

**Null Hypothesis:** There is no significant difference in cross-model transfer performance between similarity-augmented probes and hidden-state-only probes. Cross-model SE prediction is fundamentally limited by model-specific hidden state representations.

**Counter-Arguments:**
1. Hidden states are inherently model-specific (different architectures, dimensions, training data)
2. Prior failed approaches (PD-3 rho=-0.03, MTLD rho=-0.25, FTE rho=0.13) suggest SE proxies are difficult
3. Similarity auxiliary signal may only help same-model performance, not transfer
4. No prior work has demonstrated successful cross-model SE probe transfer

**Potential Failure Points:**
- H-E1: Probe fails to learn SE signal (rho < 0.3)
- H-M1: Degenerate SE clustering invalidates training labels
- H-M2: Similarity matrix uninformative (variance ≤ 0.01)
- H-M3: SEDP ≈ SEP on cross-model (no significant difference)

**Conditions Under Which H0 Would Be Supported:**
- SEDP cross-model rho < 0.3 (transfer fundamentally fails)
- SEDP rho ≈ SEP rho with no significant difference (similarity provides no benefit)
- Hidden state dimension projection loses critical information

---

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-SEDP-v1 presents a testable claim that similarity augmentation enables cross-model SE probe transfer. However, the null hypothesis raises valid concerns regarding the inherent model-specificity of hidden state representations and the lack of prior evidence for cross-model transfer.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes probe learning before testing transfer
2. **Pipeline validation (H-M1, H-M2):** Ensures data quality before mechanism test
3. **Ablation study (H-M3):** Directly compares SEDP vs SEP to test key claim
4. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1, H-M2)
- H-M3: SEDP rho ≥ 0.5 on cross-model
- H-M3: SEDP > SEP with p < 0.05

**Conditions for Antithesis Support:**
- H-E1 fails (rho < 0.3): Fundamental approach invalid
- H-M3 fails (SEDP ≈ SEP): Similarity provides no transfer benefit
- Cross-model rho < 0.3: Transfer infeasible

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, SEDP works
2. **Partial Support:** H-M3 partial (SEDP works but ≈ SEP) → Per-model probes recommended
3. **Graceful Degradation:** Transfer fails but same-model works → Still 10x speedup value
4. **No Support:** H-E1 fails → Antithesis supported, approach abandoned

---

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Probe can learn SE | May not converge | H-E1 gate test (rho ≥ 0.3) |
| Pipeline | SE labels valid | Degenerate clustering | H-M1 validation (cluster 2-15) |
| Signal | Similarity informative | May be uniform | H-M2 validation (var > 0.01) |
| Transfer | Cross-model works | Model-specific limits | H-M3 ablation (SEDP vs SEP) |
| Comparison | SEDP > SEP | No difference | Statistical test (p < 0.05) |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.85

**Rationale:** The plan directly addresses both thesis and antithesis through sequential gates with explicit pass/fail criteria. The ablation study (SEDP vs SEP) is specifically designed to test the H0 claim. Even negative results provide scientific value by documenting what doesn't work for cross-model transfer.

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** SEDP enables cross-model SE transfer via similarity-augmented training
- ID: H-SEDP-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M: 3)
- Phases: 3 phases over 4-6 days
- Critical Gates: 3 decision points (MUST_WORK: 3, SHOULD_WORK: 1)

**Risk Assessment:** Medium
- Primary concerns: R3 (similarity may not improve transfer), R1 (hidden states may lack SE info)

**Scope Reduction:** 45% (5 BUILD_ON claims from Phase 2A)

**Immediate Action:** Begin Phase 1 with H-E1 (same-model SE prediction)

---

### 7.2 Key Achievements

- 4 hypotheses across 3 verification phases
- H0 directly addressed via ablation study (SEDP vs SEP)
- Clear pass/fail criteria at each gate
- Dialectical analysis confirms robustness (Medium-High)

---

### 7.3 Verification Execution Order

**Phase 1: Foundation** (2 days)
- H-E1: Probe produces SE predictions with rho ≥ 0.3
- Gate 1: MUST_WORK → If fail, STOP

**Phase 2: Pipeline** (1 day)
- H-M1: Valid SE labels (cluster count 2-15)
- H-M2: Informative similarity (variance > 0.01)
- Gate 2: MUST_WORK → If fail, PIVOT

**Phase 3: Transfer** (2-3 days)
- H-M3: Cross-model rho ≥ 0.5, SEDP > SEP
- Gate 3: SHOULD_WORK → If fail, SCOPE to per-model

---

### 7.4 Critical Decision Points

1. **Gate 1 (Day 2):** H-E1 must pass
   - FAIL (rho < 0.3) → STOP, fundamental approach invalid
   - PASS (rho ≥ 0.3) → Proceed to Phase 2

2. **Gate 2 (Day 3):** H-M1 + H-M2 must pass
   - FAIL → PIVOT to different N/temp or similarity method
   - PASS → Proceed to Phase 3

3. **Gate 3 (Day 6):** H-M3 determines success level
   - FULL PASS (rho ≥ 0.5, SEDP > SEP) → Thesis validated
   - PARTIAL (SEDP works but ≈ SEP) → Document limitation
   - FAIL (rho < 0.3) → SCOPE to per-model probes

---

### 7.5 Open Questions

- Optimal hidden layer selection (final vs intermediate)?
- Effect of similarity aggregation method (mean, max, learned pooling)?
- Generalization to other model families (Qwen, Gemma)?
- Performance on longer-form generation beyond single-answer QA?

---

### 7.6 Recommendations

**Immediate Actions:**
- Start Phase 1 with H-E1 (Day 1)
- Prepare Mistral data generation in parallel (for H-M3)
- Set up experiment tracking infrastructure

**Resource Allocation:**
- Allocate 4-6 days for critical path
- Reserve 1-2 days buffer for PIVOT scenarios
- GPU: Single GPU sufficient (6-9 GPU-hours total)

**Failure Management:**
- Document all failures with detailed analysis
- Execute PIVOT strategies before ABANDON
- Write Serena Memory for any ROUTE_TO_0 outcomes

---

## Appendices

### A. Phase 2A Reference
- **Source:** `docs/youra_research/20260325_question/03_refinement.yaml`
- **Hypothesis ID:** H-SEDP-v1
- **Schema Version:** v10.0.0

### B. MCP Tool Usage Summary
- **Total MCP calls:** 6
- **Tools used:**
  - `mcp__clearThought__scientificmethod`: 3x (hypothesis + experiment design)
  - `mcp__clearThought__structuredargumentation`: 3x (thesis + antithesis + synthesis)

### C. Hypothesis Quick Reference
| ID | Type | Gate | Success Criterion |
|----|------|------|-------------------|
| H-E1 | Existence | MUST_WORK | rho ≥ 0.3 same-model |
| H-M1 | Mechanism | MUST_WORK | Cluster count [2, 15] |
| H-M2 | Mechanism | MUST_WORK | Variance > 0.01 |
| H-M3 | Mechanism | SHOULD_WORK | rho ≥ 0.5 cross-model |

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-28*
