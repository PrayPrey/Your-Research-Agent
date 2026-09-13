---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis",
                 "step-03-hypothesis-generation", "step-04-hypothesis-inventory",
                 "step-05-risk-analysis", "step-06-dependency-graph",
                 "step-07-timeline-planning", "step-08-dialectical-analysis",
                 "step-09-summary"]
status: complete
hypothesis_id: H-ExtrospectiveNLI-v1
created_at: "2026-03-16T14:30:00Z"
completedAt: "2026-03-16T15:00:00Z"
---

# Verification Plan: Extrospective NLI as Grounding-Conditioned Hallucination Detection on HaluEval

**Date:** 2026-03-16
**Hypothesis ID:** H-ExtrospectiveNLI-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — DO NOT RE-VERIFY)

| Claim | Evidence | Status |
|-------|----------|--------|
| NLI-based inconsistency detection achieves 74.4% balanced accuracy on summarization (SummaC) | Laban et al. (2022), SUMMACConv on 6 datasets | BUILD_ON |
| TRUE-style fine-tuned NLI achieves ROC AUC ~81.5 across diverse factuality datasets | Honovich et al. (2022), 11 datasets | BUILD_ON |
| SelfCheckGPT-NLI achieves 93.42 AUC-PR on WikiBio (sampling-based, not grounding-based) | Manakul et al. (2023) — orthogonal signal | BUILD_ON |
| HaluEval provides labeled (context, response, label) triples for Dialogue, QA, Summarization | Li et al. (2023) — benchmark available | BUILD_ON |
| FActScore: 40% atomic facts unsupported at sentence granularity | Min et al. (2023) — motivates sentence-level max aggregation | BUILD_ON |
| DeBERTa-v3-large-mnli is publicly available and cached | cross-encoder/nli-deberta-v3-large HuggingFace, confirmed from h-e1 runs | BUILD_ON |

**Scope Reduction: 54%** — 6 BUILD_ON claims treated as validated baselines/motivation. Only 3 PROVE_NEW claims require new experiments.

### 0.2 Claims Requiring Verification (PROVE_NEW)

| Claim | Evidence Gap |
|-------|-------------|
| No AUROC baseline for zero-shot DeBERTa NLI on HaluEval multi-task | HaluEval paper (Li et al., 2023) tested only LLM-based detectors |
| Optimal NLI scoring framing unestablished for HaluEval | SummaC uses entailment without comparing alternatives |
| Sentence-level vs. response-level aggregation not compared on HaluEval | SummaC demonstrated on summarization only; not validated on dialogue/QA |

### 0.3 Transfer Validation

Not applicable — no cross-domain mechanism transfer involved. DeBERTa NLI is applied in its intended use case (NLI classification).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the post-hoc, generation-free evaluation setting where only existing (context, response, label) triples from HaluEval are used (no LLM generation at experiment time), if cross-encoder/nli-deberta-v3-large is applied with (a) net-contradiction framing (P(contradiction) - P(entailment)) as the primary configuration, (b) sentence-level max aggregation for dialogue and QA, (c) full-document response-level for summarization, and (d) last-3-turn windowed premise for dialogue, then AUROC >= 0.65 will be achieved on HaluEval-Summarization and HaluEval-QA (primary), and AUROC >= 0.60 on HaluEval-Dialogue (exploratory), because DeBERTa's MNLI training encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response without any LLM generation.

### 1.2 Alternative Hypothesis (H0)

No NLI framing achieves AUROC >= 0.65 on both HaluEval-Summarization and HaluEval-QA simultaneously when applied zero-shot without any task-specific training.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HaluEval (standard) | Provides binary-labeled (context, response) pairs for Dialogue, QA, Summarization — maps directly to NLI (premise, hypothesis) without preprocessing. No generation needed. |
| **Model** | cross-encoder/nli-deberta-v3-large | 3-way softmax enables all three framing ablations from a single inference pass. Already cached from h-e1-v2 runs. |

**Dataset Details:**
- Source: pminervini/HaluEval on HuggingFace
- Path: Cached from prior h-e1 pipeline runs; load via datasets.load_dataset('pminervini/HaluEval', split_name)
- Subsets: Dialogue (~12,988 examples), Summarization (10,000), QA (10,000)

**Model Details:**
- Type: Cross-encoder NLI discriminative model
- Source: HuggingFace cross-encoder/nli-deberta-v3-large (public, no gating)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Notes |
|--------|-------------|---------|-------|
| P(True) LLaMA-3-8B-Instruct | AUROC 0.84 (Dialogue), 0.729 (Summarization) | HaluEval (prior run h-e1) | Inaccessible — theoretical reference only |
| SelfCheckGPT-NLI (base Llama-3.1-8B) | AUROC 0.48 (Dialogue), 0.53 (QA) | HaluEval (prior run h-e1) | Available as executed lower bound |
| Lexical NLI baseline (NER overlap) | ~53.0 balanced accuracy (SummaC) | Summarization benchmark | Negative control — trivial to implement |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | >50% of HaluEval hallucinated responses are context-contradictory or unsupported-but-non-entailed | HaluEval sampling-then-filtering construction; ORION F1=0.83 | NLI scores fail to discriminate; AUROC below 0.65 on all tasks |
| A2 | DeBERTa-v3-large-mnli generalizes from MNLI short pairs to HaluEval longer text pairs | TRUE: NLI generalization across 11 heterogeneous datasets; ORION cross-encoder NLI generalizes without fine-tuning | Score distributions poorly calibrated (mode near neutral); AUROC degraded by distribution shift |
| A3 | HaluEval-Dialogue hallucinations are sufficiently localized for sentence-level max to win | FActScore: 40% unsupported atomic facts at sentence level; SummaC: sentence-level +2.4 pts | Sentence-level max provides no AUROC improvement over response-level |
| A4 | Last-3-turn window contains factually relevant context | Dialogue hallucinations typically respond to most recent query; HaluEval includes 'knowledge' field | Last-3-turn AUROC equals or underperforms full-context |
| A5 | HaluEval binary labels are high quality (kappa=0.811) | Li et al. (2023) inter-annotator kappa=0.811 | Label noise suppresses AUROC; noise analysis needed |

### 1.6 Research Gap & Novelty

**Primary Gap:** No prior work reports AUROC for zero-shot DeBERTa NLI applied directly to HaluEval multi-task (Dialogue, QA, Summarization).

**Key Innovations:**
1. **Extrospective NLI paradigm**: applies NLI to existing (context, response) pairs rather than querying the generating model — orthogonal to SelfCheckGPT (self-consistency) and P(True) (introspective confidence)
2. **Structural ceiling analysis**: AUROC_max = p + 0.5*(1-p) — first such analysis on HaluEval, converts main limitation into publishable characterization finding
3. **Self-diagnostic framing ablation**: framing comparison simultaneously characterizes hallucination type distribution and optimizes detection

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | DeBERTa NLI scores systematically differ between hallucinated/non-hallucinated pairs on HaluEval (AUROC > random) | MUST_WORK | None | READY |
| H-M1 | MECHANISM | DeBERTa MNLI training encodes graded support sensitivity — NLI signal is informative for factual inconsistency detection | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Hallucinated responses receive lower entailment / higher contradiction scores vs. grounding context (systematic score separation) | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Net-contradiction framing (P(C)-P(E)) outperforms raw contradiction by delta>=0.02 on >=2/3 HaluEval tasks | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | Sentence-level max aggregation achieves AUROC >= response-level on dialogue/QA (localization advantage) | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: NLI Signal Existence on HaluEval**

**Type:** EXISTENCE
**Statement:** Under the generation-free, post-hoc evaluation setting using HaluEval test sets as-released, if DeBERTa-v3-large-mnli is applied zero-shot to (context, response) pairs across Dialogue, QA, and Summarization tasks, then AUROC > 0.55 will be achieved on at least 2/3 tasks (DeLong test p < 0.05 vs. uniform baseline), because DeBERTa's MNLI training encodes graded support sensitivity that transfers to factual inconsistency detection.

**Rationale:** H-E1 establishes that the NLI signal is non-trivial before investing in framing/aggregation ablations. A positive result (AUROC > random) proves the extrospective NLI paradigm is viable; a negative result immediately falsifies the main hypothesis without wasted downstream experiments. The label audit executed here also feeds the structural ceiling calculation.

**Variables:**
- Independent: P(contradiction) from DeBERTa softmax (response-level, full context, raw contradiction framing)
- Dependent: AUROC (sklearn.metrics.roc_auc_score, binary hallucination label)
- Controlled: Frozen DeBERTa-v3-large-mnli, HaluEval test sets as-released, batch_size=32, max_length=512

**Verification Protocol:**
1. Load HaluEval Dialogue/QA/Summarization test splits from pminervini/HaluEval (cached)
2. Apply DeBERTa-v3-large-mnli in batch (batch_size=32, torch.inference_mode()) to all (premise, hypothesis) pairs
3. Compute AUROC per task using P(contradiction) as hallucination score; run DeLong test vs. AUROC=0.5
4. Execute label audit: stratified sample 200 positive examples per task, manually categorize as (A) contradiction, (B) unsupported-non-contradicted, (C) ambiguous; compute structural ceiling per task
5. Compute Cohen's d for NLI score distribution separation (hallucinated vs. non-hallucinated)

**Success Criteria:**
- Primary: AUROC > 0.55 on at least 2/3 HaluEval tasks; DeLong test p < 0.05
- Secondary: Cohen's d > 0.2 on at least one task (score distributions differ meaningfully)
- Diagnostic: Structural ceiling AUROC_max = p + 0.5*(1-p) computed per task

**Failure Response:** IF AUROC <= 0.55 across ALL three tasks → STOP pipeline, reassess main hypothesis (NLI signal structurally non-informative for HaluEval); PIVOT to SelfCheckGPT-style self-consistency or LLM-based detection

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 5 (sh1_existence), Prediction P1

---

**H-M1: DeBERTa Graded Support Sensitivity**

**Type:** MECHANISM
**Statement:** Under the generation-free evaluation setting, DeBERTa-v3-large-mnli's MNLI pretraining encodes graded support sensitivity sufficient to detect factual inconsistency between grounding context and generated response — demonstrated by NLI score distributions (P(contradiction), P(entailment)) being significantly non-uniform across HaluEval (not concentrated at 1/3 neutral).

**Rationale:** H-M1 validates that DeBERTa generalizes from MNLI's short crowd-sourced sentence pairs to HaluEval's longer domain-specific text pairs. If score distributions are uniformly distributed (mode near 1/3 each class), the mechanism fails at step 1 regardless of downstream framing choices.

**Variables:**
- Independent: DeBERTa model weights (MNLI-trained, frozen)
- Dependent: P(contradiction), P(entailment), P(neutral) score distributions per task
- Controlled: HaluEval test sets, batch_size=32, max_length=512

**Verification Protocol:**
1. Compute full softmax distribution statistics (mean, std, KL divergence from uniform) for P(contradiction), P(neutral), P(entailment) across all HaluEval tasks
2. Test: KL divergence from uniform distribution > 0.05 (nats) for at least P(contradiction) on each task
3. Verify: Mean P(contradiction) for hallucinated examples > mean P(contradiction) for non-hallucinated (Wilcoxon rank-sum test, p < 0.05)
4. Report mean tokens retained per task after 512-token truncation (measures distribution shift severity)
5. Compute proportion of examples receiving near-uniform scores (all probabilities within 0.05 of 1/3) as failure indicator

**Success Criteria:**
- Primary: KL divergence from uniform > 0.05 for at least one class on all 3 tasks
- Secondary: Wilcoxon test p < 0.05 for P(contradiction) difference between hallucinated/non-hallucinated on >=2 tasks

**Failure Response:** IF score distributions are near-uniform on all tasks → PIVOT: investigate whether truncation (512 tokens) is collapsing signal; run without truncation on shorter subsets; if still uniform, mechanism fails

**Dependencies:** H-E1 (existence confirmed)
**Source:** Phase 2A Causal Chain Step 1

---

**H-M2: Score Separation for Hallucinated Pairs**

**Type:** MECHANISM
**Statement:** Factually inconsistent (hallucinated) responses receive lower entailment and/or higher contradiction scores relative to their grounding context on HaluEval, because they introduce content not supported by or contradicting the context — demonstrated by systematic score separation with DeLong test p < 0.05.

**Rationale:** H-M2 tests whether the NLI score difference between hallucinated and non-hallucinated examples is statistically reliable, not just present in expectation. This validates the core detection mechanism before testing framing variants.

**Variables:**
- Independent: Binary hallucination label (1=hallucinated, 0=not)
- Dependent: P(contradiction) and P(entailment) scores per example
- Controlled: Response-level NLI (no sentence splitting), raw contradiction framing, full context premise

**Verification Protocol:**
1. Compare mean P(contradiction) between hallucinated (label=1) and non-hallucinated (label=0) groups using Wilcoxon rank-sum test per task
2. Compare mean P(entailment) between groups (expecting hallucinated < non-hallucinated)
3. Run DeLong test for AUROC comparison vs. uniform baseline (AUROC=0.5) per task
4. Compute bootstrap 95% CIs for AUROC estimates (1000 resamples)
5. Check AUROC direction: if AUROC < 0.5, try 1-score inversion as diagnostic step

**Success Criteria:**
- Primary: Wilcoxon test p < 0.05 for P(contradiction) on >=2/3 tasks; AUROC > 0.5 (DeLong p < 0.05)
- Secondary: Systematic P(entailment) reduction for hallucinated examples on >=2 tasks

**Failure Response:** IF no systematic score difference detected (Wilcoxon p >= 0.05 on all tasks) → mechanism fails at step 2; investigate label quality (audit A5) and truncation effects before declaring failure

**Dependencies:** H-M1
**Source:** Phase 2A Causal Chain Step 2

---

**H-M3: Net-Contradiction Framing Superiority**

**Type:** MECHANISM
**Statement:** Net-contradiction framing (P(contradiction) - P(entailment)) achieves higher AUROC than raw contradiction alone (P(contradiction)) on at least 2/3 HaluEval tasks, with delta >= 0.02 and bootstrap 95% CI excluding 0, because net-contradiction captures both explicit contradictions and unsupported-but-non-entailed content by penalizing entailment and rewarding contradiction simultaneously.

**Rationale:** H-M3 validates the framing innovation: net-contradiction extends coverage beyond raw contradiction by penalizing the neutral class (unsupported-but-consistent content). This distinction matters for HaluEval where hallucinations may be non-entailed without being explicitly contradicted.

**Variables:**
- Independent: NLI scoring framing (contradiction, 1-entailment, net-contradiction)
- Dependent: AUROC per framing per task (pairwise comparison)
- Controlled: Aggregation level held constant at response-level for this comparison; full context premise

**Verification Protocol:**
1. Compute AUROC for all three framings (contradiction, 1-entailment, net-contradiction) on all 3 tasks at response-level
2. Compute pairwise AUROC differences with bootstrap 95% CIs (1000 resamples)
3. Check: net_contradiction AUROC - contradiction_only AUROC >= 0.02 on >=2/3 tasks
4. Check: bootstrap 95% CI for delta excludes 0 on passing tasks
5. Report complete ablation table (3 framings × 3 tasks = 9 cells) for transparency

**Success Criteria:**
- Primary: net_contradiction delta >= 0.02 vs. contradiction_only on >=2/3 tasks; CI excludes 0
- Secondary: net_contradiction >= 1-entailment on >=2/3 tasks (net-contradiction is best or tied)

**Failure Response:** IF 1-entailment consistently outperforms net-contradiction by delta >= 0.03 → framing innovation not supported; report as ablation finding; primary claim still holds if AUROC >= 0.65

**Dependencies:** H-M2
**Source:** Phase 2A Causal Chain Step 3, Prediction P2

---

**H-M4: Sentence-Level Max Aggregation Localization Advantage**

**Type:** MECHANISM
**Statement:** Sentence-level max aggregation (max contradiction over response sentences) achieves AUROC >= response-level NLI on HaluEval-Dialogue and HaluEval-QA (delta >= 0.01, or non-inferior within 0.02), and the last-3-turn dialogue window achieves non-inferior AUROC vs. full-context truncation (delta >= -0.02), because hallucinations in dialogue/QA are localized to specific sentences rather than pervasive.

**Rationale:** H-M4 tests the localization assumption motivated by FActScore (40% unsupported atomic facts at sentence level). It also validates the dialogue-specific premise windowing strategy. Sentence tokenization quality (NLTK) is a practical implementation risk that must be verified.

**Variables:**
- Independent: Aggregation granularity (response_level, sentence_level_max, sentence_level_mean); Premise window for dialogue (full_context, last_3_turns, last_user_only)
- Dependent: AUROC per granularity × window × task combination
- Controlled: net-contradiction framing held constant; frozen DeBERTa

**Verification Protocol:**
1. Apply NLTK sent_tokenize to all responses; measure mean sentence count per task; verify >1 sentence on >=80% of examples
2. Run sentence-level DeBERTa inference: for each sentence in response, apply (premise, sentence) pair; take max score across sentences
3. Compare response-level vs. sentence_level_max AUROC with bootstrap CIs per task
4. For dialogue: compare full_context vs. last_3_turns vs. last_user_only premise windows
5. Run controlled truncation study for summarization: crop documents to 128/256/384/512 tokens; report AUROC sensitivity

**Success Criteria:**
- Primary: sentence_level_max >= response_level AUROC on Dialogue and QA (or within 0.02 of response-level as non-inferior)
- Secondary: last_3_turns >= full_context AUROC on Dialogue (or non-inferior within 0.02)
- Diagnostic: Truncation sensitivity plateau — identify token threshold where AUROC stabilizes

**Failure Response:** IF response-level outperforms sentence-level max by >= 0.02 on Dialogue AND QA → localization assumption fails for HaluEval; report as finding; primary AUROC claim not affected if response-level achieves >= 0.65

**Dependencies:** H-M3
**Source:** Phase 2A Causal Chain Step 4, Prediction P3 (structural ceiling)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC > 0.55 on >=2/3 tasks; DeLong p < 0.05 | STOP pipeline; reassess main hypothesis |
| H-M1 | MUST_WORK | KL divergence from uniform > 0.05; Wilcoxon p < 0.05 on >=2 tasks | PIVOT: truncation diagnosis; if still fails, mechanism broken |
| H-M2 | MUST_WORK | Systematic score separation on >=2 tasks; AUROC > 0.5 with DeLong p < 0.05 | Investigate label quality + truncation before declaring failure |
| H-M3 | SHOULD_WORK | net_contradiction delta >= 0.02 on >=2/3 tasks | Document as ablation; primary AUROC claim unaffected |
| H-M4 | SHOULD_WORK | sentence_level_max >= response_level (non-inferior within 0.02) on Dialogue+QA | Document as finding; report response-level as primary config instead |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 (+ label audit) | Week 1-2 |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | Week 3-6 |

**Total Duration:** 6 weeks (2 + 4 × 1 week mechanism steps)

---

## Section 4: Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk ID | Source | Description | Severity | Affected Hypotheses |
|---------|--------|-------------|----------|---------------------|
| R1 | A1 | HaluEval hallucinations predominantly unsupported-but-consistent (not context-contradictory) → NLI contradiction scores structurally non-informative | HIGH | H-E1, H-M1, H-M2, H-M3, H-M4 (all) |
| R2 | A2 | DeBERTa MNLI distribution shift to HaluEval longer texts → score distributions cluster near neutral (1/3 each) | HIGH | H-M1, H-M2, H-M3, H-M4 |
| R3 | A3 | Dialogue hallucinations NOT localized at sentence level → sentence-level max provides no benefit | MEDIUM | H-M4 |
| R4 | A4 | HaluEval-Dialogue 'knowledge' field makes all premise windows equivalent → windowing experiment uninformative | LOW-MEDIUM | H-M4 (dialogue) |
| R5 | A5 | Label noise (kappa=0.811, ~18.9% disagreement) suppresses AUROC ceiling | LOW | All (global AUROC floor) |
| R6 | Baseline | Below-chance NLI precedent (SelfCheckGPT 0.48 on Dialogue) — risk of AUROC inversion | LOW-MEDIUM | H-E1 (directional check) |

### 4.2 Mitigation Strategies

**R1 — Hallucination Type Distribution Mismatch (HIGH)**
- Prevention: Pre-register structural ceiling formula before execution; label audit as mandatory H-E1 subtask
- Detection: Label audit (200 positive samples/task) — if >50% classified as "unsupported-non-contradicted," AUROC ceiling is low
- Response: STRUCTURAL CEILING REFRAME — report AUROC_max = p + 0.5*(1-p) per task; compare empirical AUROC to ceiling; publish as HaluEval characterization even if absolute AUROC < 0.65
- Early Warning: If p_contradictory < 0.3 from label audit → expect AUROC_max < 0.65; manage expectations before reporting

**R2 — MNLI Distribution Shift (HIGH)**
- Prevention: Run controlled truncation study; monitor mean tokens retained
- Detection: Check KL divergence from uniform distribution (H-M1 verification); if near-uniform, shift is severe
- Response: CONTROLLED TRUNCATION EXPERIMENT — crop to 128/256/384/512 tokens; report AUROC sensitivity curve; investigate whether shorter context improves signal
- Early Warning: >70% of summarization examples hitting 512-token truncation limit → expect degraded performance

**R3 — No Sentence-Level Localization (MEDIUM)**
- Prevention: Verify mean sentence count per task (>1.5 sentences needed)
- Detection: If sentence_level_max ≈ response_level AUROC (delta < 0.01), localization assumption violated
- Response: REPORT AS FINDING — response-level NLI is sufficient for HaluEval; update primary configuration documentation; framing/model claims remain valid
- Early Warning: NLTK sent_tokenize produces 1 segment on >50% examples → sentence-level experiment is degenerate

**R4 — Dialogue Windowing Equivalence (LOW-MEDIUM)**
- Prevention: Inspect HaluEval-Dialogue data fields before experiment; verify 'knowledge' vs. 'conversation' field semantics
- Detection: If all three window variants produce AUROC within 0.01 of each other, windows are equivalent
- Response: DOCUMENT AS FINDING — report that HaluEval-Dialogue's knowledge field dominates; windowing is a structural property of the dataset
- Early Warning: HaluEval-Dialogue using static 'knowledge' field (not conversation history) → window comparison is uninformative

**R5 — Label Noise (LOW)**
- Prevention: Report bootstrap 95% CIs for all AUROC estimates
- Detection: Compare AUROC lower bound (from CI) vs. threshold; if lower bound < 0.65, significance is borderline
- Response: REPORT WITH CONFIDENCE INTERVALS — note kappa=0.811 in limitations; bootstrap CIs quantify impact
- Early Warning: Wide bootstrap CIs (> ±0.05) → label noise may be dominating

**R6 — AUROC Inversion (LOW-MEDIUM)**
- Prevention: Pre-register direction check (AUROC > 0.5) as mandatory first check
- Detection: If AUROC < 0.5 on any task, try 1-score inversion diagnostic
- Response: INVERSION CHECK — if inverted AUROC > 0.55, report with flipped sign and explain; if still < 0.5, signal is genuinely non-informative
- Early Warning: AUROC < 0.5 on 2+ tasks simultaneously → likely genuine non-informativeness, not inversion

### 4.3 Risk Summary Table

| ID | Risk | Severity | Likelihood | Priority | Mitigation |
|----|------|----------|------------|----------|------------|
| R1 | Hallucination type mismatch | HIGH | MEDIUM | 1 | Mandatory label audit + structural ceiling |
| R2 | MNLI distribution shift | HIGH | MEDIUM | 2 | Truncation study + KL divergence check |
| R3 | No sentence localization | MEDIUM | LOW-MEDIUM | 3 | Report as finding; response-level fallback |
| R4 | Dialogue window equivalence | LOW-MEDIUM | LOW | 4 | Data field inspection; document dataset property |
| R5 | Label noise | LOW | LOW | 5 | Bootstrap CIs; note in limitations |
| R6 | AUROC inversion | LOW-MEDIUM | LOW | 4 | Directional check; 1-score diagnostic |

---

## Section 5: Dependency Graph & Execution Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses, Sequential Chain
═══════════════════════════════════════════════════════════════════

[Level 0 — Foundation]
    H-E1: NLI Signal Existence
    Gate: MUST_WORK
         │
         ▼ GATE 1: AUROC > 0.55 on >=2/3 tasks
         │
[Level 1 — Step 1 Mechanism]
    H-M1: Graded Support Sensitivity ← H-E1
    Gate: MUST_WORK
         │
         ▼ GATE 2a: KL divergence > 0.05; Wilcoxon p < 0.05
         │
[Level 2 — Step 2 Mechanism]
    H-M2: Score Separation ← H-M1
    Gate: MUST_WORK
         │
         ▼ GATE 2b: Systematic separation on >=2 tasks
         │
[Level 3 — Step 3 Mechanism]
    H-M3: Net-Contradiction Framing ← H-M2
    Gate: SHOULD_WORK
         │
         ▼ GATE 2c: delta >= 0.02 on >=2/3 tasks
         │
[Level 4 — Step 4 Mechanism]
    H-M4: Sentence-Level Aggregation ← H-M3
    Gate: SHOULD_WORK
         │
         ▼ GATE 2d: sentence_level_max >= response_level

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Phases: Phase 4 PoC → Phase 6 Paper Writing
═══════════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Execution Block |
|-------|-----------|---------------|-----------|-----------------|
| 0 | H-E1 | None | MUST_WORK | Phase 1 (Foundation) |
| 1 | H-M1 | H-E1 | MUST_WORK | Phase 2 (Mechanism) |
| 2 | H-M2 | H-M1 | MUST_WORK | Phase 2 (Mechanism) |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Phase 2 (Mechanism) |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Phase 2 (Mechanism) |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses | 6 Weeks Total
═══════════════════════════════════════════════════════════════════════════════
Phase / Hypothesis │ W1-2     │ W3-4     │ W5       │ W6       │
───────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1 + Label Audit│ ████████ │          │          │          │
  [Gate 1: MUST_WORK]│         │ ◆        │          │          │
───────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms
  H-M1              │         │ ████████ │          │          │
  H-M2              │         │          │ ████     │          │
  H-M3              │         │          │ ████     │          │
  H-M4              │         │          │          │ ████████ │
  [Gate 2: MUST/SHOULD]│      │          │          │          │ ◆
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks | Critical Path: 6 weeks | Slack: 0 weeks
═══════════════════════════════════════════════════════════════════════════════
```

**Note:** H-M1, H-M2, H-M3 can be co-executed in Phase 4 as they all run on the same 81-condition ablation grid. They are logically sequential (each validates a causal step) but experimentally parallelizable within a single unified inference run.

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1 + label audit) + 4 × 1 week (H-M1-4)
Slack: 0 weeks (all sequential)

MUST_WORK gates: H-E1, H-M1, H-M2 (3 mandatory gates)
SHOULD_WORK gates: H-M3, H-M4 (2 optional gates)

Efficiency: H-M1/M2/M3 share the same 81-condition inference run
→ Practical Phase 4 duration may compress to 3-4 weeks with batch execution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
- Condition: 0 (not required)

Verification Phases: 2
1. Foundation: H-E1 + label audit (2 weeks)
2. Mechanisms: H-M1 through H-M4 (4 weeks)

Dataset: HaluEval — 32,988 examples total
- Dialogue: ~12,988 | QA: 10,000 | Summarization: 10,000
Model: cross-encoder/nli-deberta-v3-large (cached)
Inference: 81 conditions × ~33K examples (batch_size=32)
  + label audit: 600 manual annotations (200/task)

Total Duration: 6 weeks
Critical Path: 6 weeks
Execution: Sequential logical chain; parallel within Phase 4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
         → Load HaluEval test sets
         → Run DeBERTa response-level inference
         → Compute AUROC, DeLong test
         → Execute label audit (200 positives/task)
         → Compute structural ceiling per task
Step 2: Evaluate Gate 1 (MUST_WORK)
         → PASS: Proceed to Phase 2
         → FAIL: STOP, reassess main hypothesis
Step 3: Execute H-M1 + H-M2 + H-M3 (Weeks 3-5, unified batch)
         → Run full 81-condition ablation
         → Compute AUROC per framing × granularity × window × task
         → Validate score distributions (H-M1)
         → Validate score separation (H-M2)
         → Validate framing superiority (H-M3)
Step 4: Execute H-M4 (Week 6)
         → Sentence-level inference (NLTK sent_tokenize)
         → Aggregation comparison (max vs. mean vs. response-level)
         → Truncation sensitivity study (128/256/384/512 tokens)
         → Dialogue window comparison
Step 5: Evaluate Gates 2a-2d
         → MUST_WORK (H-M1, H-M2): FAIL → escalate/pivot
         → SHOULD_WORK (H-M3, H-M4): FAIL → document as finding
Step 6: Structural ceiling analysis
         → Combine label audit results with empirical AUROC
         → Compute efficiency: empirical / ceiling ratio
         → Report: near-ceiling = strong support; far-below = scope limitation
Final:   Phase 4 PoC validation complete → Phase 6 Paper Writing
```

---

## Section 6: Dialectical Analysis

### 6.1 Thesis

**Core Claim:** DeBERTa-v3-large-mnli with net-contradiction framing and sentence-level max aggregation achieves AUROC >= 0.65 on HaluEval-Summarization and HaluEval-QA under zero-shot, generation-free evaluation.

**Supporting Evidence:**
1. DeBERTa trained on >433K MNLI/SNLI premise-hypothesis pairs — encodes graded support sensitivity
2. SummaC (Laban et al., 2022): NLI achieves 74.4% balanced accuracy on summarization factual consistency
3. TRUE (Honovich et al., 2022): Fine-tuned NLI achieves ROC AUC ~81.5 across 11 heterogeneous factuality datasets
4. ORION (Gerner et al., 2025): NLI cross-encoder achieves F1=0.83 on RAGTruth without task training
5. HaluEval (context, response) structure maps directly to NLI (premise, hypothesis) — no preprocessing gap
6. Net-contradiction framing theoretically captures both explicit contradictions AND unsupported-but-non-entailed content
7. FActScore: 40% atomic facts unsupported at sentence granularity — motivates sentence-level max localization

**Expected Outcomes:**
- P1: AUROC >= 0.65 on Summarization and QA simultaneously (primary)
- P2: Net-contradiction outperforms raw contradiction by >= 0.02 on >=2/3 tasks
- P3: Empirical AUROC >= 70% of structural ceiling on Summarization and QA

### 6.2 Antithesis

**H0:** No NLI framing achieves AUROC >= 0.65 on both HaluEval-Summarization and HaluEval-QA simultaneously.

**Counter-Arguments:**
1. HaluEval labels "unverifiable information" — hallucinations may be unsupported-but-consistent, creating a structural ceiling below 0.65 if p_contradictory < 0.6
2. MNLI training uses short crowd-sourced pairs (~15 tokens avg); HaluEval texts are 200-500 tokens — distribution shift may collapse NLI scores toward neutral
3. SelfCheckGPT-NLI AUROC 0.48 on HaluEval-Dialogue — negative empirical precedent for NLI-based signals on this benchmark
4. SummaC's 74.4% balanced accuracy is NOT AUROC and is measured on SUMMAC benchmark (not HaluEval) — performance transfer unvalidated
5. Zero-shot NLI may not adapt to dialogue pragmatic structure (grounding vs. consistency)

**Conditions Under Which H0 Would Be Supported:**
- If p_contradictory < 0.3 in label audit → structural ceiling AUROC_max < 0.65 mathematically
- If DeBERTa scores are near-uniform on HaluEval (KL divergence < 0.05) → mechanism fails at step 1
- If AUROC < 0.65 across all three framing variants on both Summarization and QA simultaneously

**Antithesis Weakness:** SelfCheckGPT-NLI uses SELF-consistency signal (compares response to other responses), not external grounding. Its failure on Dialogue is orthogonal to extrospective NLI — different signal type, different failure mode.

### 6.3 Synthesis

The verification plan resolves the thesis-antithesis dialectic through a self-diagnostic design:

**Resolution Path:**
1. **Label audit (mandatory in H-E1):** Measures p_contradictory per task — directly quantifies the antithesis's core concern. If p_contradictory < 0.3, the structural ceiling explains low AUROC without invalidating the methodology.
2. **Structural ceiling formula:** AUROC_max = p + 0.5*(1-p) converts the antithesis's objection into a bounded, testable claim. Near-ceiling performance (empirical >= 70% of ceiling) is publishable even if absolute AUROC < 0.65.
3. **H-E1 gate:** Early detection of antithesis support — if AUROC < 0.55 on all tasks, pipeline stops before wasting downstream effort.
4. **Pre-registered primary config:** Prevents post-hoc tuning that would undermine the antithesis's reproducibility concern.

**Nuanced Outcome Possibilities:**
- **Full Thesis Support:** AUROC >= 0.65 on Summarization + QA; net-contradiction wins; sentence-level localizes → Publish as novel extrospective NLI paradigm demonstration
- **Partial Support (High Ceiling):** AUROC >= 0.65 on one task; structural ceiling analysis shows near-ceiling on both → Publish framing ablation + ceiling analysis as primary contribution
- **Structural Limitation (Low Ceiling):** AUROC < 0.65 but >= 70% of ceiling → Publish as HaluEval hallucination type characterization: "NLI is near-optimal for context-contradictory hallucinations; the benchmark's ceiling is the limiting factor"
- **Antithesis Supported:** AUROC < 0.55 on all tasks → Fundamental NLI failure on HaluEval; pivot to SelfCheckGPT/LLM-based approaches; structural ceiling analysis still published

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Signal informativeness | MNLI encoding generalizes to HaluEval | Distribution shift degrades NLI calibration | H-E1 gate + KL divergence check |
| Hallucination type compatibility | >50% are context-contradictory or non-entailed | HaluEval labels "unverifiable" content | Label audit + structural ceiling |
| Framing innovation | Net-contradiction extends coverage | All framings may be equivalent | Framing ablation (81 conditions) |
| Localization claim | Sentence-level max isolates signal | HaluEval responses too short for localization | Response length analysis + fallback |
| SelfCheckGPT precedent | Orthogonal signal type (external vs. self) | AUROC 0.48 on Dialogue negative precedent | Signal orthogonality argument + direction check |

**Overall Robustness Score:** HIGH — self-diagnostic design ensures publishable findings regardless of outcome.
**Confidence in Verification Plan:** 0.72 (from Phase 2A)

---

## Section 7: Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-ExtrospectiveNLI-v1 — zero-shot DeBERTa NLI on HaluEval multi-task achieves AUROC >= 0.65 on Summarization and QA under generation-free evaluation
- Confidence: 0.72 | Mode: Incremental (54% scope reduction from BUILD_ON claims)

**Verification Structure:**
- Sub-Hypotheses: 5 total (H-E1 + H-M1 through H-M4)
- Phases: 2 phases (Foundation + Mechanisms) over 6 weeks
- Critical Gates: 3 MUST_WORK + 2 SHOULD_WORK = 5 decision points
- Execution: Sequential logical chain; batch parallelizable within Phase 4

**Risk Assessment:** MEDIUM
- Primary concern R1: Hallucination type distribution mismatch → addressed by mandatory label audit
- Secondary concern R2: MNLI distribution shift → addressed by truncation study + KL divergence monitoring

**Self-Diagnostic Design:** Publishable findings regardless of AUROC outcome:
- If AUROC >= 0.65: Novel extrospective NLI paradigm validated on HaluEval
- If AUROC < 0.65 but near-ceiling: Structural ceiling characterization is primary contribution
- If AUROC << 0.65: HaluEval hallucination type distribution characterization is published finding

**Immediate Action:** Begin Phase 4 with H-E1 + mandatory label audit.

### 7.2 Final Summary

**Key Achievements:**
- 5 sub-hypotheses defined across 2 phases with clear verification protocols
- H0 addressed: No NLI framing achieves >= 0.65 simultaneously zero-shot
- Structural ceiling formula converts main limitation into publishable contribution
- Pre-registered primary configuration prevents post-hoc framing selection

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: DeBERTa NLI signal existence on HaluEval + mandatory label audit
- Gate 1: MUST PASS → STOP if AUROC <= 0.55 on all tasks

**Phase 2: Core Mechanisms** (4 weeks — batch parallelizable)
- H-M1: Graded support sensitivity validation (score distribution analysis)
- H-M2: Score separation validation (systematic hallucinated vs. non-hallucinated)
- H-M3: Net-contradiction framing superiority (framing ablation)
- H-M4: Sentence-level max aggregation + truncation study + dialogue windowing
- Gate 2: H-M1 and H-M2 MUST PASS; H-M3, H-M4 SHOULD PASS

**Critical Decision Points:**

1. **Gate 1 (H-E1, MUST_WORK):**
   - PASS → Proceed to Phase 2 mechanisms
   - FAIL (AUROC <= 0.55 on all tasks) → STOP, reassess main hypothesis; pivot to generative approaches

2. **Gate 2a (H-M1, MUST_WORK):**
   - PASS → Continue mechanism chain
   - FAIL (near-uniform scores) → Truncation diagnosis; if still fails, mechanism broken at step 1

3. **Gate 2b (H-M2, MUST_WORK):**
   - PASS → Validate framing + aggregation (H-M3, H-M4)
   - FAIL (no systematic separation) → Investigate label quality; narrow scope to task subset

4. **Gate 2c (H-M3, SHOULD_WORK):**
   - PASS → Net-contradiction innovation validated
   - FAIL → Report as ablation; primary AUROC claim unaffected if threshold met

5. **Gate 2d (H-M4, SHOULD_WORK):**
   - PASS → Sentence-level localization validated
   - FAIL → Response-level is sufficient; update primary configuration documentation

**Open Questions (from Phase 2A):**
- What proportion of HaluEval hallucinated responses are context-contradictory vs. unsupported-but-consistent? → Resolved by label audit in H-E1
- How much does DeBERTa truncation (512 tokens) suppress AUROC for summarization? → Resolved by truncation study in H-M4
- Does last-3-turn window improve AUROC over full-context by delta >= 0.03? → Resolved in H-M4 dialogue windowing
- Is the NLI signal (external grounding) orthogonal to self-consistency? → Addressed theoretically; empirical comparison deferred to Phase 5

### 7.3 Recommendations

1. **Immediate Actions:**
   - Begin Phase 4 with H-E1 + integrated label audit
   - Load HaluEval from cache (pminervini/HaluEval); verify cross-encoder/nli-deberta-v3-large availability
   - Pre-register primary configuration (net-contradiction, sentence_level_max, last_3_turns) in experiment code before analysis

2. **Resource Allocation:**
   - Allocate 6 weeks critical path; batch execution (H-M1/M2/M3 unified) may compress to 4-5 weeks
   - 600 manual label annotations (200/task) required for label audit — plan time accordingly
   - Single GPU sufficient (DeBERTa inference, batch_size=32)

3. **Failure Management:**
   - If Gate 1 fails: Write Serena memory file with structural ceiling findings; pivot to Phase 0 brainstorm
   - If Gate 2a/2b fails: Investigate truncation + label quality before declaring failure
   - If Gate 2c/2d fails: Document as finding; framing/aggregation ablation still publishable

### 7.4 Appendices

**Appendix A: Phase 2A Reference**
- Source: docs/youra_research/20260315_question/03_refinement.yaml (H-ExtrospectiveNLI-v1)
- Schema: v10.0.0 Free-Parse | Discussion: 15 exchanges, 6 agents, convergence: ALL 6 criteria met
- Phase 2A output: VALIDATED (all criteria: specific claim, mechanism, predictions, novelty, feasibility, objections addressed)

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 6 (3 scientificmethod, 1 collaborativereasoning, 2 structuredargumentation)
- Tools: mcp__clearThought__scientificmethod (3×), mcp__clearThought__collaborativereasoning (1×), mcp__clearThought__structuredargumentation (3×: thesis + antithesis + synthesis)
- Archon: Project found + Phase 2B task updated to doing

**Appendix C: Scope Reduction Summary**
- Total Phase 2A claims: 9 (6 BUILD_ON + 3 PROVE_NEW)
- Scope reduction: 54% — BUILD_ON claims serve as motivation/baselines only
- PROVE_NEW claims fully covered by: H-E1 (AUROC measurement), H-M3 (framing ablation), H-M4 (aggregation comparison)

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-03-16*
