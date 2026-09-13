---
workflow: phase2b-planning
version: 7.7.0
generated_at: 2026-04-19T13:50:00
hypothesis_id: H-GeomAlign-v1
research_mode: incremental
stepsCompleted: [step-00, step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08, step-09, step-10]
total_hypotheses: 5
execution_duration: 6-8 weeks
---

# Phase 2B: Verification Planning

## Section 0: Established Facts & Scope Reduction

### Established Facts Registry (BUILD_ON)

Claims that have been validated and should NOT be re-verified in Phase 2B-4:

1. **RLHF datasets contain validated labels**: HH-RLHF datasets (Bai et al., 2022) contain 160K+ human-annotated chosen/rejected pairs with validated preference labels
2. **Explicit annotation criteria**: Human annotators in HH-RLHF evaluated responses under explicit helpfulness/harmlessness criteria
3. **Previous failure analysis**: Phase 0 ROUTE_TO_0 analysis identified 6 failure points from H-E1 attempt (overly-broad scope, unvalidated proxy labels)

### Scope Reduction Analysis

- **Total claims in hypothesis**: 4
- **BUILD_ON (skip verification)**: 3 claims
- **PROVE_NEW (require verification)**: 1 claim (geometric manifold structure)
- **Scope reduction**: 75%

### Phase 2B-4 Instructions

Focus experiments on harmless subset of HH-RLHF where rejection judgments encode safety violations, not just helpfulness preferences.

---

## Section 1: Main Hypothesis Overview

### 1.1 Core Hypothesis

**Hypothesis ID**: H-GeomAlign-v1  
**Confidence Level**: 0.75

**Core Hypothesis Statement**:

Under the scope of RLHF harmless-preference evaluation, if we analyze the HH-RLHF dataset's chosen/rejected response pairs in embedding space, then we will discover a multi-dimensional geometric manifold where rejected responses cluster along interpretable failure axes with distances encoding violation severity, because human annotators consistently detect implicit alignment violations that induce stable structure across 160K+ pairwise judgments.

**Alternative Hypothesis (H0)**:

There is no statistically significant geometric structure in rejected vs. chosen responses beyond what is explained by surface lexical patterns, model-specific stylistic artifacts, or a single dominant toxicity axis.

### 1.2 Variables

**Independent Variables**:
- Dataset source (HH-RLHF, WebGPT, Summarization from Feedback)
- Encoder model (RoBERTa-base, DeBERTa-v3-base, SentenceTransformer-mpnet)
- Violation type (toxicity, misinformation, instruction-following)

**Dependent Variables (Primary)**:
- Classification F1 score (0-1, harmonic mean of precision/recall)
- AUROC after lexical ablation (0.5-1.0)
- Spearman correlation severity-distance (-1 to 1)

**Controlled Variables**:
- Train/test split (80/20 stratified by violation type)
- Random seed (42, 123, 456)
- Embedding extraction (CLS token pooling)

### 1.3 Causal Mechanism (4-Step Chain)

**Step 1**: Human annotators evaluate response pairs under helpfulness/harmlessness criteria, rejecting responses that violate safety principles
- **Evidence**: HH-RLHF annotation guidelines (Bai et al., 2022)
- **Falsifier**: Base-rate audit shows <40% genuine violations

**Step 2**: Aggregation of 160K+ rejection judgments creates high-density sampling of alignment failure space
- **Evidence**: HH-RLHF dataset size and methodology
- **Falsifier**: Rejected responses show random distribution in embedding space

**Step 3**: Rejected responses form clusters with geometric properties (distance = severity, PC directions = violation types)
- **Evidence**: Geometric separability tests (MANOVA, PCA)
- **Falsifier**: Single dominant PC >80% variance OR PC axes fail to align across encoders

**Step 4**: Geometric structure is stable across encoders and generalizes to new model families
- **Evidence**: Cross-encoder PC alignment (cosine ≥0.70), cross-dataset transfer (F1 ≥0.65)
- **Falsifier**: Transfer F1 <0.55 OR encoder-specific PC rotation (cosine <0.60)

**Key Tension**: Whether rejected responses encode genuine alignment violations vs. marginal preference differences - resolved by base-rate audit threshold (p ≥ 0.40)

### 1.4 Key Assumptions

| ID | Assumption | Supporting Evidence | Consequence if Violated |
|----|------------|-------------------|------------------------|
| A1 | Base-rate sufficiency: HH-RLHF harmless subset contains ≥40% genuine policy violations | HH-RLHF paper describes explicit harmlessness criteria | Label noise dominates, manifold structure cannot be learned |
| A2 | Semantic encoding: Pretrained LM embeddings capture alignment features beyond surface patterns | Lexical ablation tests (Exp 5, 7) | Detector becomes refusal-template classifier |
| A3 | Cross-model stability: Alignment failure patterns transfer across models | Cross-dataset transfer experiments (Exp 3, 6) | Structure is model-specific artifact |
| A4 | Encoder invariance: Geometric structure exists in data, not as encoder artifact | Cross-encoder PC alignment test (Exp 12) | Manifold is representation-dependent illusion |
| A5 | Violation orthogonality: Different failure types occupy distinct embedding regions | Multi-axis separability test (Exp 8) | Structure collapses to single dominant axis |

### 1.5 Scope

**Applies To**:
- RLHF preference datasets with harmlessness annotations (HH-RLHF, WebGPT, Summarization from Feedback)
- Conversational AI safety evaluation using existing pretrained encoders
- Cross-model harmlessness assessment without new annotation
- Violation types present in training data (toxicity, misinformation, instruction-following)

**Does NOT Apply To**:
- Helpfulness-only preferences (outside harmlessness scope)
- Novel violation types not in HH-RLHF (jailbreak attacks, prompt injection)
- Non-conversational tasks (code generation, reasoning, tool use)
- Models with radically different response distributions

**Known Limitations**:
- Requires base-rate ≥40% genuine violations for geometric structure
- Transfer degrades under extreme distribution shift
- Annotation bias from HH-RLHF annotator pool may limit cultural/temporal generalization
- Single-language analysis (English only)

### 1.6 Testable Predictions

**P1 (PRIMARY)**: Euclidean distance in embedding space between rejected and chosen responses correlates with human-judged violation severity (Spearman ρ ≥ 0.65)
- **Test Method**: Sample 300 triplets (low, medium, high severity); measure manifold distance to chosen centroid; compute Spearman correlation
- **Success Criterion**: Spearman ρ ≥ 0.65 AND triplet ordering preserved in ≥80% of cases
- **Falsification**: If ρ < 0.50 or ordering preservation <60%, continuous structure claim rejected

**P2 (PRIMARY)**: Rejected responses cluster along ≥3 orthogonal axes corresponding to distinct violation types (toxicity, misinformation, instruction-following)
- **Test Method**: MANOVA on embeddings labeled by violation type; compute effect sizes for each PC
- **Success Criterion**: ≥3 PCs with Cohen's d ≥ 0.5; no single PC explains >80% variance
- **Falsification**: If only 1-2 PCs with d ≥ 0.5, or single PC >80% variance, multi-dimensional claim rejected

**P3**: Geometric structure is encoder-robust (intrinsic to data, not encoder-specific)
- **Test Method**: Extract PCs from RoBERTa, DeBERTa, SentenceTransformer; compute pairwise cosine similarity of PC directions
- **Success Criterion**: Top-3 PC cosine similarity ≥ 0.70 for all encoder pairs
- **Falsification**: If any pair <0.60, structure is representation-dependent artifact

### 1.7 Experimental Setup

**Dataset**: HH-RLHF harmless subset + WebGPT + Summarization from Feedback
- **Source**: Anthropic, OpenAI (publicly available)
- **Path**: https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Hypothesis Fit**: Contains 160K+ validated chosen/rejected pairs with explicit harmlessness annotations

**Model**: RoBERTa-base (primary) + DeBERTa-v3-base + SentenceTransformer
- **Type**: Pretrained encoder
- **Source**: HuggingFace Transformers
- **Hypothesis Fit**: Semantic encoders capture alignment-relevant features for geometric analysis

**Baselines**:
1. TF-IDF Logistic Regression (surface feature baseline)
2. Bradley-Terry Reward Model (standard RLHF approach)
3. Random Classifier (AUROC = 0.5 baseline)

### 1.8 Related Work

| Method | Expected Performance | Dataset | Why Insufficient |
|--------|---------------------|---------|------------------|
| TF-IDF + Logistic Regression | F1 ≈ 0.60-0.65 | HH-RLHF | Surface features lack semantic understanding |
| Bradley-Terry Reward Model | F1 ≈ 0.70-0.75 | HH-RLHF | Black-box without interpretable structure |

**Best Baseline Performance**: F1 ≈ 0.70 (reward model), but lacks interpretability and geometric insights

### 1.9 Novelty & Gap

**Preserved Novelty**: First work to frame RLHF preference data as containing discoverable geometric structure of alignment failures, enabling reusable cross-model safety evaluation without new annotation

**Key Innovation**: Transition from black-box reward modeling to interpretable geometric alignment maps with explicit semantic axes (distance = severity, direction = violation type)

**Differentiation from Prior Work**:
- Prior RLHF trains reward models (black box) → We extract interpretable geometric structure
- Prior reward models require retraining per model → Manifold structure generalizes cross-model
- Prior work consumes preference data for training → We treat it as persistent benchmark infrastructure

---

## Section 2: Sub-Hypothesis Inventory

### 2.1 Inventory Table

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (5 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Type | Statement (Brief) | Prerequisites | Gate | Source |
|----|------|-------------------|---------------|------|--------|
| H-E1 | Existence | Base-rate validation: HH-RLHF harmless subset contains ≥40% genuine violations | None | MUST_WORK | Phase 2A P1, Causal Step 1 |
| H-M1 | Mechanism | Annotation quality: Human annotators consistently detect violations | H-E1 | SHOULD_WORK | Causal Step 1 |
| H-M2 | Mechanism | Embedding separability: Rejected responses cluster (not random) | H-M1 | SHOULD_WORK | Causal Step 2, P2 |
| H-M3 | Mechanism | Geometric properties: Distance=severity, PCs=violation types | H-M2 | SHOULD_WORK | Causal Step 3, P1+P2 |
| H-M4 | Mechanism | Cross-encoder robustness: Structure is encoder-invariant | H-M3 | DETERMINES_SUCCESS | Causal Step 4, P3 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 2.2 Hypothesis Specifications

---

#### H-E1: Base-Rate Validation

**Type**: EXISTENCE  
**Statement**: Under the scope of HH-RLHF harmless-preference annotation, if we perform blinded human audit of rejected samples, then we will find ≥40% contain genuine safety policy violations (not marginal preferences), because annotators used explicit harmlessness criteria that distinguish violations from style differences.

**Rationale**: The entire geometric manifold framing depends on rejected responses encoding genuine alignment failures. If base-rate <40%, label noise dominates and geometric structure cannot emerge. This is the foundational gate experiment.

**Variables**:
- Independent: Sample source (rejected vs chosen)
- Dependent: Proportion of genuine violations (0-1)
- Controlled: Blinded annotation protocol, inter-rater agreement (κ ≥ 0.75)

**Verification Protocol**:
1. Sample 500 rejected responses from HH-RLHF harmless subset using stratified random sampling
2. Conduct blinded human audit with 3 independent annotators using explicit violation criteria
3. Calculate inter-annotator agreement (Cohen's κ) and proportion of genuine violations
4. Test H0: p < 0.40 vs H1: p ≥ 0.40 using binomial test (α=0.05)

**Success Criteria**:
- Primary: p ≥ 0.40 genuine violations (binomial test p-value < 0.05)
- Secondary: Inter-annotator agreement κ ≥ 0.75

**Gate**: MUST_WORK  
**Failure Response**: If p < 0.40, PIVOT to narrower preference prediction framing or ABANDON geometric manifold claims

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Causal Step 1 falsifier, Assumption A1

---

#### H-M1: Annotation Consistency

**Type**: MECHANISM (Step 1)  
**Statement**: Under controlled annotation conditions, if human annotators evaluate response pairs using HH-RLHF harmlessness criteria, then inter-annotator agreement will be substantial (κ ≥ 0.70) and align with original HH-RLHF labels (≥75% agreement), because explicit criteria reduce subjective variation in violation detection.

**Rationale**: Validates that human judgment process produces consistent signal. Low agreement would indicate label noise undermines downstream geometric analysis.

**Variables**:
- Independent: Annotation protocol (explicit criteria vs intuitive judgment)
- Dependent: Inter-annotator agreement (Cohen's κ), alignment with HH-RLHF (proportion)
- Controlled: Annotator training, sample selection (stratified by violation type)

**Verification Protocol**:
1. Recruit 3 annotators and provide HH-RLHF annotation guidelines training
2. Sample 300 response pairs from HH-RLHF harmless subset (100 per violation type)
3. Collect independent annotations for chosen/rejected classification
4. Compute Cohen's κ across annotators and proportion agreement with original labels
5. Test against H0: κ < 0.60 vs H1: κ ≥ 0.70

**Success Criteria**:
- Primary: Cohen's κ ≥ 0.70 across annotators
- Secondary: ≥75% agreement with original HH-RLHF labels

**Gate**: SHOULD_WORK  
**Failure Response**: If κ < 0.60, EXPLORE refined criteria or PIVOT to expert-only annotation subset

**Dependencies**: H-E1 (requires genuine violations to judge)

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Embedding Separability

**Type**: MECHANISM (Step 2)  
**Statement**: Under semantic embedding space representation, if we extract embeddings from 160K+ HH-RLHF chosen/rejected pairs using pretrained encoders (RoBERTa-base), then rejected responses will form distinct clusters (not random distribution) with MANOVA effect size d ≥ 0.5, because aggregated human judgments create high-density sampling of alignment failure space.

**Rationale**: Tests whether aggregation of judgments induces geometric structure. Random distribution would falsify manifold emergence claim from causal step 2.

**Variables**:
- Independent: Response type (chosen vs rejected)
- Dependent: Embedding cluster separability (MANOVA effect size)
- Controlled: Encoder model (RoBERTa-base), embedding extraction method (CLS pooling), train/test split (80/20)

**Verification Protocol**:
1. Extract CLS token embeddings from RoBERTa-base for all HH-RLHF harmless pairs
2. Apply PCA dimensionality reduction to visualize embedding space distribution
3. Perform MANOVA test on chosen vs rejected embeddings
4. Compute effect size (Cohen's d) for group separation
5. Test H0: random distribution (d < 0.3) vs H1: structured clustering (d ≥ 0.5)

**Success Criteria**:
- Primary: MANOVA effect size d ≥ 0.5 (medium-to-large effect)
- Secondary: Visual inspection confirms non-random clustering in PCA space

**Gate**: SHOULD_WORK  
**Failure Response**: If d < 0.3, EXPLORE alternative encoders or ABANDON geometric framing

**Dependencies**: H-M1 (requires consistent annotations)

**Source**: Phase 2A Causal Step 2 falsifier, Prediction P2

---

#### H-M3: Geometric Properties

**Type**: MECHANISM (Step 3)  
**Statement**: Under embedding space geometry, if we analyze rejected response clusters, then (a) Euclidean distance from chosen centroid will correlate with human-judged severity (Spearman ρ ≥ 0.65), and (b) ≥3 principal components will encode distinct violation types with no single PC >80% variance, because human annotators detect multi-dimensional alignment failures.

**Rationale**: Validates the core geometric manifold claim—that structure has interpretable properties (distance=severity, direction=type). This distinguishes geometric structure from mere separability.

**Variables**:
- Independent: Violation severity (low/medium/high), violation type (toxicity/misinformation/instruction)
- Dependent: Manifold distance (continuous), PC loadings (multi-dimensional)
- Controlled: Encoder (RoBERTa-base), distance metric (Euclidean), severity annotation protocol

**Verification Protocol**:
1. Sample 300 rejected response triplets (100 low, 100 medium, 100 high severity)
2. Compute Euclidean distance from each rejected response to chosen centroid
3. Collect human severity judgments (blinded 3-point scale)
4. Calculate Spearman rank correlation between distance and severity
5. Perform PCA on rejected embeddings and test: ≥3 PCs with Cohen's d ≥ 0.5, no single PC >80% variance
6. Validate PC interpretability by mapping to violation types

**Success Criteria**:
- Primary: Spearman ρ ≥ 0.65 (severity-distance correlation), ≥3 PCs with d ≥ 0.5
- Secondary: Triplet ordering preserved ≥80%, no single PC explains >80% variance

**Gate**: SHOULD_WORK  
**Failure Response**: If ρ < 0.50 or only 1-2 PCs, DOWNGRADE to separability-only claim

**Dependencies**: H-M2 (requires clustering exists)

**Source**: Phase 2A Causal Step 3, Predictions P1+P2

---

#### H-M4: Cross-Encoder Robustness

**Type**: MECHANISM (Step 4)  
**Statement**: Under multi-encoder validation, if we extract principal components from RoBERTa, DeBERTa, and SentenceTransformer embeddings, then top-3 PC directions will align across encoders (pairwise cosine similarity ≥ 0.70), because geometric structure is data-intrinsic rather than encoder-specific artifact.

**Rationale**: Distinguishes genuine data structure from representation artifacts. Low PC alignment would indicate manifold is encoder-dependent, limiting reusability claims.

**Variables**:
- Independent: Encoder model (RoBERTa-base, DeBERTa-v3-base, SentenceTransformer-mpnet)
- Dependent: PC alignment (cosine similarity), cross-encoder transfer F1
- Controlled: Embedding extraction (CLS pooling), PC computation method

**Verification Protocol**:
1. Extract embeddings from three encoders (RoBERTa, DeBERTa, SentenceTransformer) for HH-RLHF dataset
2. Compute top-3 PCs independently for each encoder's rejected embeddings
3. Calculate pairwise cosine similarity of corresponding PC directions across encoder pairs
4. Test cross-encoder transfer: train classifier on RoBERTa embeddings, evaluate on DeBERTa/SentenceTransformer
5. Validate H0: cosine < 0.60 (encoder-specific) vs H1: cosine ≥ 0.70 (data-intrinsic)

**Success Criteria**:
- Primary: Top-3 PC cosine similarity ≥ 0.70 for all encoder pairs
- Secondary: Cross-encoder transfer F1 ≥ 0.65

**Gate**: DETERMINES_SUCCESS  
**Failure Response**: If cosine < 0.60, DOWNGRADE to single-encoder claim or EXPLORE encoder-agnostic methods

**Dependencies**: H-M3 (requires geometric properties validated)

**Source**: Phase 2A Causal Step 4 falsifier, Prediction P3, Assumption A4

---

---

## Section 3: Risk Analysis

### 3.1 Risk-Hypothesis Mapping

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING (5 Risks from Phase 2A Assumptions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Risk | Source | Description | Affected Hypotheses | Severity |
|------|--------|-------------|---------------------|----------|
| R1 | A1 | Base-rate insufficiency (p < 0.40) | H-E1, all H-M | Critical |
| R2 | A2 | Surface pattern dominance (embeddings lack semantics) | H-M2, H-M3 | High |
| R3 | A3 | Model-specific structure (no cross-model transfer) | H-M4 | High |
| R4 | A4 | Encoder artifact (not data-intrinsic) | H-M4 | High |
| R5 | A5 | Single-axis collapse (no multi-dimensional structure) | H-M2, H-M3 | Medium |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 3.2 Risk Mitigation Strategies

---

**Risk R1: Base-Rate Insufficiency**

**Source Assumption**: A1 - HH-RLHF harmless subset contains ≥40% genuine policy violations

**Description**: If base-rate audit (H-E1) shows <40% genuine violations, label noise dominates and geometric manifold structure cannot reliably emerge from data.

**Affected Hypotheses**: H-E1 (directly), H-M1-M4 (indirectly—all depend on genuine violations)

**Severity**: Critical (entire geometric framing depends on this)

**Mitigation Strategy**:
1. **Prevention**: Use stratified sampling from harmless subset focusing on explicit rejection reasons; pilot test with 50 samples before full audit
2. **Detection**: Monitor inter-annotator agreement (κ < 0.75 indicates label ambiguity); track proportion of marginal vs clear violations
3. **Response**:
   - PIVOT (if 0.30 ≤ p < 0.40): Narrow to high-confidence violation subset (explicit safety keywords)
   - SCOPE (if 0.20 ≤ p < 0.30): Downgrade to preference prediction framing (abandon geometric claims)
   - ABORT (if p < 0.20): Insufficient signal—select different dataset

**Early Warning Indicators**:
- κ < 0.70 in pilot audit
- >50% rejections marked as "marginal preference" vs "clear violation"
- High disagreement on severity judgments

---

**Risk R2: Surface Pattern Dominance**

**Source Assumption**: A2 - Pretrained LM embeddings capture alignment features beyond surface patterns

**Description**: Embeddings may encode refusal templates ("I cannot", "As an AI") rather than semantic alignment violations, making detector a lexical classifier.

**Affected Hypotheses**: H-M2 (separability test), H-M3 (geometric properties)

**Severity**: High (undermines semantic manifold claim)

**Mitigation Strategy**:
1. **Prevention**: Include lexical ablation experiments (Exp 5, 7) in verification protocol; test paraphrastic invariance
2. **Detection**: Compare F1 before/after masking refusal tokens; measure correlation with surface features (length, sentiment)
3. **Response**:
   - PIVOT: Use counterfactual paraphrasing to filter surface patterns
   - SCOPE: Document as "refusal-augmented" detector with explicit limitations
   - EXPLORE: Test alternative encoders (instruction-tuned models may have better semantic encoding)

**Early Warning Indicators**:
- F1 drops >0.15 after lexical ablation
- High correlation (r > 0.60) with surface features (response length, keyword counts)
- Paraphrased violations misclassified as safe

---

**Risk R3: Model-Specific Structure**

**Source Assumption**: A3 - Alignment failure patterns are sufficiently model-agnostic to transfer

**Description**: Structure may be specific to HH-RLHF training data distribution rather than general alignment violations, limiting cross-dataset generalization.

**Affected Hypotheses**: H-M4 (cross-encoder robustness requires cross-model stability)

**Severity**: High (impacts reusability claims)

**Mitigation Strategy**:
1. **Prevention**: Test on diverse datasets (WebGPT, Summarization from Feedback) during H-M4 verification
2. **Detection**: Monitor cross-dataset transfer F1; if <0.55, indicates model-specific artifacts
3. **Response**:
   - PIVOT: Restrict claims to HH-RLHF-trained models only
   - EXPLORE: Identify transferable vs dataset-specific violation patterns
   - SCOPE: Document as "HH-RLHF-aligned model" detector with transfer limitations

**Early Warning Indicators**:
- Cross-dataset transfer F1 < 0.60
- PC directions rotate significantly (cosine < 0.50) across datasets
- High false positive rate on out-of-distribution safety violations

---

**Risk R4: Encoder Artifact Structure**

**Source Assumption**: A4 - Geometric structure exists in data, not as encoder artifact

**Description**: Manifold structure may be representation-dependent illusion rather than intrinsic data property, limiting cross-encoder generalization.

**Affected Hypotheses**: H-M4 (cross-encoder PC alignment test)

**Severity**: High (falsifies data-intrinsic structure claim)

**Mitigation Strategy**:
1. **Prevention**: Test 3 diverse encoders (RoBERTa, DeBERTa, SentenceTransformer) with different architectures
2. **Detection**: Compute PC cosine similarity across encoder pairs; <0.60 indicates encoder-specific structure
3. **Response**:
   - PIVOT: Downgrade to single-encoder manifold claim with explicit scope
   - EXPLORE: Test encoder-agnostic methods (graph-based, kernel methods)
   - SCOPE: Document as "RoBERTa embedding space" findings with generalization caveats

**Early Warning Indicators**:
- PC cosine similarity < 0.65 for any encoder pair
- Cluster membership changes significantly across encoders (Rand index < 0.70)
- Severity-distance correlation varies widely (Δρ > 0.20) across encoders

---

**Risk R5: Single-Axis Collapse**

**Source Assumption**: A5 - Different failure types occupy distinct embedding regions

**Description**: Structure may collapse to single dominant toxicity axis rather than multi-dimensional manifold, limiting zero-shot detection of diverse violation types.

**Affected Hypotheses**: H-M2 (multi-axis test), H-M3 (PC interpretability)

**Severity**: Medium (reduces utility but doesn't invalidate core geometric claim)

**Mitigation Strategy**:
1. **Prevention**: Ensure stratified sampling across violation types (toxicity, misinformation, instruction-following) in H-E1
2. **Detection**: Test MANOVA for multi-group separability; single PC >80% variance indicates collapse
3. **Response**:
   - PIVOT: Focus on dominant axis (toxicity) with explicit scope limitations
   - EXPLORE: Test finer-grained violation taxonomies
   - SCOPE: Document as "toxicity-dominant manifold" with future multi-type directions

**Early Warning Indicators**:
- Single PC explains >75% variance
- Only 1-2 PCs with Cohen's d ≥ 0.5
- MANOVA shows no significant separation across violation types (p > 0.05)

---

### 3.3 Risk Summary Table

| Risk | Severity | Likelihood | Mitigation Readiness | Contingency Plan |
|------|----------|-----------|---------------------|------------------|
| R1 - Base-rate | Critical | Medium | High (pilot audit, stratified sampling) | Narrow subset or pivot framing |
| R2 - Surface patterns | High | Medium | High (lexical ablation built-in) | Document limitations, explore alternatives |
| R3 - Model-specific | High | Low | Medium (cross-dataset tests) | Restrict scope to HH-RLHF models |
| R4 - Encoder artifact | High | Low | High (3 diverse encoders) | Single-encoder claim |
| R5 - Single-axis | Medium | Medium | Medium (stratified sampling) | Focus on dominant axis |

---

## Section 4: Dependency Graph (DAG)

### 4.1 Dependency Hierarchy

═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Base-Rate Validation
         │
         │ (Gate 1: MUST_WORK)
         ▼
[Level 1 - Mechanism Step 1]
    H-M1: Annotation Consistency ← H-E1
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2: Embedding Separability ← H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3: Geometric Properties ← H-M2
         │
         │ (Gate 2: SHOULD_WORK)
         ▼
[Level 4 - Mechanism Step 4]
    H-M4: Cross-Encoder Robustness ← H-M3
         │
         │ (Gate 3: DETERMINES_SUCCESS)
         ▼
    [Terminal: Verification Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Depth: 4 levels
Parallelization: None (all sequential dependencies)
═══════════════════════════════════════════════════════════

### 4.2 Verification Phases with Gate Conditions

**Phase 1: Foundation (Week 1-2)**

| Hypothesis | Test | Gate | Failure Action |
|------------|------|------|----------------|
| H-E1 | Base-rate audit: p ≥ 0.40 genuine violations | MUST_WORK | STOP - reassess entire hypothesis or pivot framing |

→ **Gate 1**: If H-E1 fails (p < 0.40), entire geometric manifold claim is invalid. Must PIVOT to narrower subset or ABANDON geometric framing.

---

**Phase 2: Core Mechanisms (Week 3-6)**

| Hypothesis | Dependencies | Gate | Failure Action |
|------------|--------------|------|----------------|
| H-M1 | H-E1 | SHOULD_WORK | EXPLORE refined criteria or expert-only subset |
| H-M2 | H-M1 | SHOULD_WORK | EXPLORE alternative encoders or ABANDON geometric framing |
| H-M3 | H-M2 | SHOULD_WORK | DOWNGRADE to separability-only claim |
| H-M4 | H-M3 | DETERMINES_SUCCESS | DOWNGRADE to single-encoder claim or EXPLORE encoder-agnostic methods |

→ **Gate 2** (after H-M3): Core geometric properties validated. Failure at H-M3 = downgrade to simple separability claim.

→ **Gate 3** (after H-M4): Cross-encoder robustness determines reusability claims. Failure = limit scope to single encoder.

---

**Dependency Rules**:
- **Strict Sequential**: Each H-M{N+1} requires H-M{N} success
- **No Parallelization**: Cannot test H-M3 until H-M2 passes
- **Early Termination**: H-E1 or H-M2 failure triggers immediate reassessment

---

## Section 5: Timeline Planning (Gantt)

### 5.1 Gantt Timeline Visualization

═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses (6 Weeks Total)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Week 1-2 │ Week 3-4 │ Week 5   │ Week 6   │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation  │          │          │          │          │
  H-E1: Base-rate    │ ████████ │          │          │          │
  [Gate 1: MUST]     │          │ ◆        │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms  │          │          │          │          │
  H-M1: Annotation   │          │ ████████ │          │          │
  H-M2: Separability │          │          │ ████     │          │
  H-M3: Geometry     │          │          │          │ ████     │
  [Gate 2: SHOULD]   │          │          │          │     ◆    │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 3: Robustness  │          │          │          │          │
  H-M4: Cross-Enc    │          │          │          │      ████│
  [Gate 3: SUCCESS]  │          │          │          │         ◆│
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks (2 for H-E1, 4 for mechanisms)
═══════════════════════════════════════════════════════════════════════════════

### 5.2 Critical Path Analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Critical Path**: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Total Duration**: 6 weeks
  - Formula: 2 (H-E1 foundation) + 4 (mechanism chain)
  - Breakdown:
    - H-E1: 2 weeks (base-rate audit, blinded annotation)
    - H-M1: 2 weeks (annotation consistency validation)
    - H-M2: 1 week (embedding separability test)
    - H-M3: 1 week (geometric properties validation)
    - H-M4: 1 week (cross-encoder robustness)

**Slack Available**: 0 weeks (all sequential dependencies, no parallelization)

**Bottlenecks**:
- H-E1 (2 weeks): Human annotation bottleneck—requires 3 independent annotators for 500 samples
- H-M1 (2 weeks): Additional human validation—300 pairs with training
- H-M2-M4 (1 week each): Computational experiments—can be accelerated with more GPUs

**Acceleration Opportunities**:
- Parallel annotation in H-E1 (reduce from 2 weeks to 1 week with 6 annotators)
- Batch H-M2-M4 experiments (reduce from 3 weeks to 2 weeks with pipeline optimization)
- Optimistic: 4 weeks total with full parallelization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.3 Resource Summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total Hypotheses**: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0

**Human Resources**:
- Annotators: 3 (for H-E1 base-rate audit, H-M1 consistency)
- Training time: 2 hours per annotator
- Total annotation effort: ~150 hours (500 + 300 samples × 3 annotators)

**Computational Resources**:
- GPU: 1× NVIDIA A100 (or equivalent)
- Storage: ~50GB (HH-RLHF dataset + embeddings)
- Compute time: ~20 GPU-hours (embedding extraction, PCA, MANOVA)

**Datasets**:
- Primary: HH-RLHF harmless subset (160K+ pairs)
- Transfer validation: WebGPT, Summarization from Feedback

**Software Dependencies**:
- PyTorch, Transformers (HuggingFace)
- scikit-learn (PCA, MANOVA)
- scipy (statistical tests)

**Risk Mitigation Budget**:
- Pilot testing: +1 week (50 samples for base-rate validation)
- Contingency: +1 week (if H-E1 requires subset refinement)

**Total Estimated Duration**: 6 weeks (baseline) to 8 weeks (with contingency)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.4 Execution Order

**Sequential Execution (No Parallelization)**:

1. **Week 1-2**: H-E1 (Base-rate validation) → Gate 1
2. **Week 3-4**: H-M1 (Annotation consistency) → proceed
3. **Week 5**: H-M2 (Embedding separability) → proceed
4. **Week 6**: H-M3 (Geometric properties) → Gate 2
5. **Week 6-7**: H-M4 (Cross-encoder robustness) → Gate 3

**Gate Decision Points**:
- **Gate 1 (Week 2)**: If H-E1 fails → STOP, reassess entire hypothesis
- **Gate 2 (Week 6)**: If H-M3 fails → DOWNGRADE to separability-only claim
- **Gate 3 (Week 7)**: If H-M4 fails → LIMIT scope to single encoder

---

## Section 6: Dialectical Analysis

### 6.1 Thesis-Antithesis-Synthesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS (Main Hypothesis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim**: RLHF preference data encodes a multi-dimensional geometric manifold of alignment failures where distance reflects severity and principal component directions reflect violation types.

**Supporting Evidence**:
1. Human annotators in HH-RLHF used explicit harmlessness criteria (Bai et al., 2022)
2. Aggregation of 160K+ pairwise judgments creates high-density sampling of failure space
3. Pretrained encoders capture semantic features beyond surface lexical patterns
4. Similar geometric structure discovery successful in anomaly detection domains

**Strengths**:
- Clear causal mechanism: human judgment → aggregation → geometric emergence
- Testable predictions with quantitative thresholds (ρ ≥ 0.65, d ≥ 0.5, cosine ≥ 0.70)
- Addresses fundamental scalability problem in alignment evaluation
- Paradigm shift from consumable training data to persistent benchmark infrastructure

**Expected Outcomes**:
- Primary: Severity-distance correlation ρ ≥ 0.65 with triplet ordering ≥80%
- Secondary: Multi-dimensional structure (≥3 PCs, no single >80% variance)
- Tertiary: Encoder-robust structure (cross-encoder PC cosine ≥ 0.70)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS (Null Hypothesis H0)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0)**: There is no statistically significant geometric structure in rejected vs. chosen responses beyond what is explained by surface lexical patterns, model-specific stylistic artifacts, or a single dominant toxicity axis.

**Counter-Arguments**:
1. **Surface pattern dominance**: Rejected responses may simply contain refusal templates ("I cannot", "As an AI") that embeddings trivially separate—this is lexical classification, not semantic manifold discovery
2. **Base-rate insufficiency**: If <40% of rejected samples contain genuine violations, label noise dominates and geometric structure cannot reliably emerge
3. **Single-axis collapse**: Structure may reduce to simple toxicity detection (single PC >80% variance), not multi-dimensional alignment manifold
4. **Encoder artifacts**: Geometric properties may be representation-dependent illusions specific to RoBERTa's learned space, not intrinsic data structure
5. **Model-specific patterns**: Structure may reflect HH-RLHF's particular training distribution rather than general alignment violations

**Plausible Failure Modes**:
- Base-rate audit shows p < 0.40 (R1: Critical risk)
- Lexical ablation drops F1 >0.15 (R2: High risk)
- Single PC explains >80% variance (R5: Medium risk)
- Cross-encoder PC cosine <0.60 (R4: High risk)

**Baseline Insufficiency**:
- TF-IDF logistic regression achieves F1 ≈ 0.65 with surface features alone
- Bradley-Terry reward model achieves F1 ≈ 0.70 without geometric interpretability
- If proposed approach doesn't exceed F1 ≈ 0.75 with interpretable structure, incremental gain insufficient

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment**:

The geometric manifold hypothesis makes a strong claim that requires addressing legitimate null hypothesis concerns. The verification plan incorporates these concerns through:

1. **Base-rate gate (H-E1)**: Directly tests whether genuine violations exist at sufficient rate (p ≥ 0.40). Failure triggers immediate pivot or abandonment.

2. **Lexical ablation controls**: Built into H-M2/H-M3 verification to distinguish semantic from surface pattern detection. Success requires maintained performance (drop ≤0.10) after masking refusal tokens.

3. **Multi-dimensional validation**: H-M3 explicitly tests for ≥3 orthogonal axes with no single dominant component, falsifying single-axis collapse claim.

4. **Encoder robustness**: H-M4 cross-encoder PC alignment (≥0.70 cosine) distinguishes data-intrinsic from representation-dependent structure.

**Reconciliation**: If all gates pass, the hypothesis demonstrates geometric structure that is:
- Grounded in genuine violations (not noise)
- Semantic (not lexical patterns)
- Multi-dimensional (not single-axis)
- Data-intrinsic (not encoder artifacts)

This would validate the paradigm shift from reward modeling to geometric alignment maps.

**If Partial Success**:
- H-E1 + H-M1 + H-M2 pass, H-M3 fails → Downgrade to "separability detection" claim
- H-E1 + H-M1 + H-M2 + H-M3 pass, H-M4 fails → Limit to "RoBERTa-specific manifold" with reusability caveats
- H-E1 fails → Abandon geometric framing, pivot to preference prediction

**Robustness**: The 4-tiered verification structure ensures contribution even with partial validation, ranging from incremental detection tools (Tier 1) to paradigm-shifting geometric insights (Tier 4).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 6.2 Robustness Assessment

**Strengths of Verification Plan**:
- Sequential gates prevent cascade of invalid conclusions
- Multiple falsification criteria at each step
- Built-in downgrade paths preserve partial contributions
- Explicit scope boundaries prevent overstatement

**Remaining Uncertainties**:
- Actual base-rate in HH-RLHF harmless subset (hypothesis: ≥40%, risk: <40%)
- Degree of lexical vs semantic encoding in pretrained embeddings
- Generalization beyond HH-RLHF to other preference datasets
- Cultural and temporal generalization of annotation criteria

**Confidence Level**: 0.75 (from Phase 2A) reflects:
- HIGH confidence in core causal mechanism (human judgment → geometric structure)
- MEDIUM confidence in base-rate sufficiency (requires empirical validation)
- MEDIUM confidence in cross-encoder robustness (3 encoders tested, but not exhaustive)

---

## Section 7: Executive Summary

### 7.1 Executive Summary

**Main Hypothesis**: H-GeomAlign-v1 - Geometric Structure of Alignment Failures in RLHF Preference Data
- ID: H-GeomAlign-v1, Confidence: 0.75
- Core claim: Multi-dimensional manifold where distance = severity, PCs = violation types

**Verification Structure**:
- Mode: Incremental (Phase 2A pre-mapping)
- Sub-Hypotheses: 5 total
  - H-E: 1 (Base-rate validation)
  - H-M: 4 (Mechanism chain matching 4-step causal model)
- Phases: 3 phases over 6 weeks (optimistic) to 8 weeks (with contingency)
- Critical Gates: 3 decision points (Gate 1: MUST_WORK, Gate 2: SHOULD_WORK, Gate 3: DETERMINES_SUCCESS)

**Risk Assessment**: Medium-High
- Primary concerns: Base-rate insufficiency (R1: Critical), Surface pattern dominance (R2: High)
- Mitigation: Pilot audit, lexical ablation controls, cross-encoder validation

**Immediate Action**: Begin Phase 1 with H-E1 base-rate audit (2 weeks, 500 samples, 3 annotators)

---

### 7.2 Key Achievements

**Verification Plan Achievements**:
- 5 hypotheses systematically decomposed from 4-step causal chain
- Each hypothesis includes verification protocol, success criteria, and failure response
- Complete risk analysis with mitigation strategies for all 5 assumptions
- DAG and Gantt timeline with realistic resource allocation
- Dialectical analysis balancing thesis against null hypothesis

**Phase 2A Integration**:
- Established facts properly scoped (3 BUILD_ON claims excluded)
- Variables, predictions, and causal mechanism directly mapped to sub-hypotheses
- H0 used as antithesis foundation for robust evaluation

---

### 7.3 Verification Execution Order

**Phase 1: Foundation (Week 1-2)**
- H-E1: Base-rate validation (p ≥ 0.40 genuine violations)
- Gate 1: MUST PASS → If fail, STOP and reassess entire hypothesis

**Phase 2: Core Mechanisms (Week 3-6)**
- H-M1: Annotation consistency (κ ≥ 0.70)
- H-M2: Embedding separability (MANOVA d ≥ 0.5)
- H-M3: Geometric properties (ρ ≥ 0.65, ≥3 PCs)
- H-M4: Cross-encoder robustness (PC cosine ≥ 0.70)
- Gate 2 (after H-M3): Core properties validated
- Gate 3 (after H-M4): Reusability determined

**Decision Points**:
- Gate 1 failure → PIVOT to narrower subset or ABANDON geometric framing
- Gate 2 failure → DOWNGRADE to separability-only claim
- Gate 3 failure → LIMIT scope to single-encoder manifold

---

### 7.4 Recommendations

**Immediate Next Steps**:
1. Recruit 3 annotators and provide HH-RLHF annotation guidelines training (2 hours each)
2. Develop base-rate audit protocol with blinded evaluation forms
3. Set up GPU environment (1× A100 or equivalent) for embedding extraction
4. Download HH-RLHF harmless subset and prepare stratified sampling script

**Phase 2C Integration**:
- Per-hypothesis context files will be generated JIT by Phase 2C workflow
- verification_state.yaml tracks hypothesis status for automated progression
- Each hypothesis enters Phase 2C → 3 → 4 cycle independently

**Resource Allocation**:
- Human: 3 annotators × 150 hours total (H-E1 + H-M1)
- Compute: 1 GPU × 20 hours (embedding extraction, PCA, MANOVA)
- Storage: 50GB (datasets + embeddings)
- Timeline: 6-8 weeks with contingency

---

### 7.5 Open Questions

**For Future Investigation**:
1. What is the minimum viable base-rate for manifold emergence? (sensitivity analysis around p=0.40 threshold)
2. Can zero-shot detection work for novel violation types via geometric proximity?
3. How does manifold structure evolve across model generations (GPT-3 → GPT-4 → Claude)?
4. What is the cultural and temporal stability of annotation criteria?

**Beyond Scope (Future Work)**:
- Jailbreak attack detection (novel violation type not in HH-RLHF)
- Non-conversational tasks (code generation, reasoning)
- Multilingual alignment manifolds (current: English only)

---

## Section 8: Finalization

### 8.1 Verification State

**verification_state.yaml**: Generated with 5 sub-hypotheses
- H-E1: Status READY (no prerequisites)
- H-M1 to H-M4: Status NOT_STARTED (sequential dependencies)
- Gate conditions configured (MUST_WORK, SHOULD_WORK, DETERMINES_SUCCESS)

**File Location**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/verification_state.yaml`

---

### 8.2 Pipeline Integration

**Phase 2B Output Files**:
- ✓ `02b_verification_plan.md` - Complete verification roadmap (this file)
- ✓ `verification_state.yaml` - State tracking for hypothesis loop (to be generated)

**Next Phase**: Phase 2C - Experiment Design
- Input: verification_state.yaml, 02b_verification_plan.md
- Process: For each READY hypothesis, generate detailed experiment design
- Output: Per-hypothesis 02c_experiment_design.md files

---

### 8.3 Completion Status

✅ **Phase 2B Planning Complete**

**Outputs Generated**:
- Main verification plan: 02b_verification_plan.md
- Sub-hypotheses: 5 (H-E1, H-M1-M4)
- Risk mitigation: 5 strategies for A1-A5 assumptions
- DAG + Gantt: 6-week timeline with 3 gates
- Dialectical analysis: Thesis-Antithesis-Synthesis evaluation

**Ready for Phase 2C**: Hypothesis verification loop can begin with H-E1

---

*Phase 2B Verification Planning v7.7.0 | Generated 2026-04-19 | Unattended Mode*
