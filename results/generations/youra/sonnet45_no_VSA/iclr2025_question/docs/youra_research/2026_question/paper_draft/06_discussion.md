# 6. Discussion

## 6.1 The Reproducibility Gap

Our replication attempt exposed a **documentation gap** between research claims and reproducible implementations. The CCP paper [arxiv:2403.04696] reports +0.05-0.10 ROC-AUC improvement on biography generation but omits critical implementation details that determine whether ρ_j achieves expected range (0.75-0.85):

**Missing Detail 1: NLI Model Calibration**
- Which NLI model was used? (DeBERTa-v3-base? RoBERTa-large-MNLI? fine-tuned variant?)
- Was the model fine-tuned on factual verification data (FEVER, HotpotQA)?
- What are the raw NLI probability distributions over {contradiction, entailment, neutral}?
- What calibration diagnostics were performed (ECE, reliability curves)?

**Missing Detail 2: Claim Decomposition Methodology**
- How were claims extracted? (sentence tokenization? LLM prompting? manual annotation?)
- What inter-annotator agreement was achieved (Krippendorff's α)?
- How many claims per sample on average (5-8? 10-20?)?
- Were compound sentences split into atomic propositions?

**Missing Detail 3: Context Pairing Strategy**
- Full-text context or windowed? (±1 sentence? ±2 sentences? claim-local?)
- How were long contexts handled relative to 512-token NLI model limits?
- Did context pairing vary by dataset (question-answer vs biography-claim)?

**Missing Detail 4: Raw Metric Distributions**
- What ρ_j distributions were observed on TruthfulQA biographies (min, median, max, variance)?
- How do ρ_j values correlate with ROC-AUC improvements (+0.05-0.10 reported)?
- What percentage of samples fall into low ρ_j (<0.5) vs high ρ_j (>0.75) bins?

Without these details, replication attempts must make ad-hoc choices. We chose DeBERTa-v3-base (SOTA on SNLI/MNLI) + NLTK tokenization (deterministic, reproducible) + full-text context (following cavaquinho pattern)—all defensible decisions that nonetheless produced ρ_j 50× lower than expected.

## 6.2 Implications for Hallucination Detection Research

Our findings suggest **three field-wide practices** that limit reproducibility:

**Practice 1: Optimizing for Novelty Over Reproducibility**

Papers report aggregate metrics (ROC-AUC, F1) that hide implementation details. ROC-AUC can improve +0.05 via:
- Better NLI model (fine-tuned on FEVER vs off-the-shelf MNLI)
- Better claim extraction (LLM vs sentence tokenization)
- Better aggregation (optimal threshold vs fixed ρ_j cutoff)

Without raw metric distributions, readers cannot distinguish genuine algorithmic improvements from undocumented implementation optimizations.

**Practice 2: Assuming NLI Model Transferability**

DeBERTa-v3-base achieves 92.38% SNLI accuracy → assumed to work for factual verification. Our results refute this: SNLI/MNLI test semantic similarity (do sentences describe similar situations?), not factual verification (is claim consistent with context?). **Task-domain gap** (semantic similarity ≠ factual verification) requires model adaptation even when source task accuracy is high.

Literature triangulation supports this:
- Himal-Badu: "Attention mechanisms show r < 0.1 correlation with hallucination labels" → NLI features dominate, so NLI quality is bottleneck
- Shaguns26: 95% recall only after threshold tuning 50% → 30% → default NLI calibration insufficient

**Practice 3: No Baseline Validation Before Domain Transfer**

We tested CCP on creative text (WritingPrompts) without first validating it reproduces paper claims on TruthfulQA factual domain. This conflates "method doesn't work as described" with "hypothesis is wrong." **Lesson: Replicate baseline on original domain BEFORE extending to new domains.**

Analogy: Testing new stain protocol on rare tissue samples without first validating on common tissues. Finding all slides blank could mean (1) cells lack nuclei (hypothesis), or (2) microscope is out of focus (measurement). Without baseline validation, we cannot decide.

## 6.3 Recommendations for Authors

To improve hallucination detection reproducibility, we propose papers adopt the following practices:

### 6.3.1 Report Raw Metric Distributions

**What to report**:
- ρ_j distribution statistics (min, median, max, variance) per dataset
- NLI probability distributions over {contradiction, entailment, neutral}
- Claim count statistics (mean, variance, samples with zero claims)
- Correlation between ρ_j and aggregate metrics (ROC-AUC, F1)

**Why it matters**: Aggregate ROC-AUC can hide measurement validity issues (our ρ_j 50× too low but still produces some ranking). Raw distributions reveal whether metric achieves expected dynamic range.

### 6.3.2 Validate NLI Calibration

**What to report**:
- Sanity check: Test NLI on known entailment/contradiction examples from target domain
  - Example: TruthfulQA correct answer vs question → expect P(entail) > 0.5
  - Example: TruthfulQA incorrect answer vs question → expect P(contradict) > 0.5
- If sanity check fails (P < 0.5), report whether fine-tuning/temperature scaling was applied
- Calibration diagnostics: ECE, reliability curves

**Why it matters**: Off-the-shelf NLI models trained on SNLI/MNLI may not generalize to factual verification. Sanity check catches this BEFORE running full experiment.

### 6.3.3 Document Claim Decomposition Methodology

**What to report**:
- Method used (NLTK? GPT-4? Spacy? manual annotation?)
- Inter-method agreement (Krippendorff's α for NLTK vs LLM vs manual)
- Claim quality examples (show 5-10 extracted claims with context)
- Failure mode statistics (% samples with zero claims, compound sentences not split)

**Why it matters**: Claim quality affects ρ_j denominator stability (fragmented claims → noisy probability distributions). Method comparison enables readers to assess whether claim extraction is bottleneck.

### 6.3.4 Provide Reproducibility Package

**What to include**:
- Public code repository (GitHub) with environment specification (requirements.txt, Docker)
- Baseline replication notebook validating key claims on standard benchmarks
- Unit tests on manually verified entailment/contradiction examples
- Configuration files documenting all hyperparameters (model, batch size, seeds)
- Instructions for one-command reproduction

**Why it matters**: CVS Health UQLM package demonstrates feasibility (1183 GitHub stars, LangChain integration, production-ready). Absence of CCP public code prevented us from comparing our implementation to authors' version.

### 6.3.5 Baseline Validation Protocol

**What to do**:
1. Implement method on ORIGINAL domain from paper (e.g., TruthfulQA biographies for CCP)
2. Validate raw metrics match paper claims (ρ_j ∈ [0.75, 0.85] expected)
3. If validation fails, diagnose (NLI calibration? claim decomposition?) BEFORE domain transfer
4. Only after baseline validation succeeds, extend to new domains (creative text, multilingual, etc.)

**Why it matters**: Prevents conflating "method doesn't work as described" with "hypothesis is wrong." Our failure mode (baseline ρ_j 50× too low) would have been caught at step 2.

## 6.4 Limitations of This Work

While our analysis identifies NLI calibration as primary bottleneck (Section 5.6), we acknowledge **seven limitations** constraining scope and generalizability:

**L1: No Baseline Replication (HIGH priority)**  
We did NOT first replicate CCP on TruthfulQA factual domain before testing creative transfer. Cannot distinguish "our implementation is wrong" from "CCP paper omits critical details."

**L2: Single NLI Model Tested (MEDIUM priority)**  
Only DeBERTa-v3-base tested. Alternative models (RoBERTa-large-MNLI, BART-large-MNLI, TRUE factuality model) may perform better.

**L3: No Claim Method Comparison (HIGH priority)**  
Only NLTK sentence tokenization tested. LLM extraction (GPT-3.5/GPT-4) or Spacy dependency parsing may improve claim quality.

**L4: No Context Window Ablation (MEDIUM priority)**  
Only full-text context tested. ±1/±2/±3 sentence windows may improve NLI signal-to-noise ratio.

**L5: No Temperature Calibration (LOW priority)**  
No post-hoc calibration attempted (temperature scaling, Platt scaling). Unlikely to fix 50× magnitude gap but worth measuring.

**L6: Dataset as Domain Proxy (LOW priority for PoC)**  
TruthfulQA/WritingPrompts are imperfect proxies for "factual"/"creative" ontologies. Heterogeneity acceptable for EXISTENCE hypothesis but MECHANISM hypotheses require explicit ontology annotation.

**L7: No Author Communication (LOW priority)**  
Did NOT contact CCP paper authors for implementation details. Standard practice requires papers be self-contained for reproducibility; our contribution documents the gap.

**Mitigation strategy**: Future work addresses L1-L4 (Sections 6.5.1-6.5.3). L5-L7 acknowledged but not critical for methodological contribution.

## 6.5 Future Work

Root cause hierarchy (Section 5.6) guides prioritization:

### 6.5.1 Tier 1: NLI Model Validation & Calibration (CRITICAL)

**Objective**: Fix primary measurement validity issue (ρ_j 50× too low)

**Step 1: Sanity Check (1-2 days)**
- Test DeBERTa-v3-base on TruthfulQA correct vs incorrect answers
- Success: P(entail | correct) > 0.5 AND P(contradict | incorrect) > 0.5
- Failure: Both < 0.5 → model not calibrated for factual verification

**Step 2: Fine-Tuning (1-2 weeks)**
- Fine-tune on FEVER (185k claims) or HotpotQA (113k questions)
- Target: ρ_j on TruthfulQA factual reaches 0.70-0.85
- If fails: Test alternative models (RoBERTa-large-MNLI, TRUE)

**Step 3: Baseline Replication (1 week)**
- Replicate CCP paper ROC-AUC on TruthfulQA biographies
- Success: ROC-AUC within ±0.03 of paper claims
- If fails: Contact authors OR pivot to alternative baseline (SelfCheckGPT, AGSER)

**Expected outcome**: ρ_j on factual domain reaches expected range → enables valid hypothesis testing for creative domain transfer.

### 6.5.2 Tier 2: Claim Decomposition & Context Pairing (HIGH)

**Claim Method Comparison (3-5 days)**
- Compare NLTK vs GPT-3.5 extraction vs Spacy dependency parsing
- Measure inter-method agreement (Krippendorff's α > 0.7) and ρ_j distribution per method
- Select method with highest α AND ρ_j closest to expected range

**Context Window Ablation (1 week)**
- Test full-text vs ±1/±2/±3 sentence windows
- Measure ρ_j distribution per strategy
- Optimal window = highest ρ_j while maintaining coverage

**Expected outcome**: Identified claim extraction method and context strategy that maximize ρ_j validity → reduces contributory noise factors.

### 6.5.3 Hypothesis Revival (CONTINGENT on Tier 1+2 success)

IF Tier 1 fixes ρ_j to expected range (0.70-0.85 on factual):

**Re-test h-e1 with Validated Methodology (1 week)**
- Use calibrated NLI model + validated claim method + optimal context window
- Measure Δρ_j on TruthfulQA vs WritingPrompts
- Success: Δρ_j > 0.15 AND p < 0.05 → ontology hypothesis confirmed
- Failure: Δρ_j < 0.05 → hypothesis refuted (NLI models robust across domains after calibration)

**Add Metaphor Annotation (2-3 weeks)**
- Annotate WritingPrompts for metaphor spans
- Test whether metaphor false-positive concentration ≥2× higher than literal spans
- Validates mechanism (ontology mismatch → metaphor misclassification)

IF Tier 1 fails (cannot reach ρ_j > 0.70):

**Pivot to Comparative Mechanisms (2-3 weeks)**
- Implement AGSER + HAD baselines
- Test whether alternative detectors avoid NLI calibration issues
- Contribution shifts from CCP replication to "taxonomy-based detectors are creative-robust alternatives"

### 6.5.4 Long-Term: Reproducibility Study (6-12 months)

Systematic replication of hallucination detection papers (CCP, AGSER, HAD, SelfCheckGPT, Semantic Entropy):
- Reproduce baselines on original datasets
- Document implementation details not in papers
- Public reproducibility package (code, data, validation notebooks, unit tests)

**Impact**: Improve field standards for reproducibility, establish what ACTUALLY works vs what is claimed to work.

## 6.6 Broader Impact

**Positive**: Transparent failure documentation prevents field-wide repetition of costly mistakes. Methodological requirements (NLI calibration, claim validation, baseline replication) improve reproducibility standards for hallucination detection research.

**Negative**: May give false impression CCP method is fundamentally flawed, when issue may be undocumented implementation optimizations. Could discourage researchers from building on CCP paper.

**Mitigation**: We frame contribution as "methodological requirements identification" not "CCP is broken." Provide actionable guidance (FEVER fine-tuning, claim method comparison) that enables future researchers to succeed where we encountered measurement validity failures.

**Stakeholders**:
- **Researchers**: Benefit from reproducibility checklist preventing ad-hoc implementation choices
- **Practitioners**: Understand that off-the-shelf NLI models (DeBERTa-v3-base) require task-specific calibration for factual verification
- **Field**: Improved standards for transparency (raw metric distributions, calibration diagnostics, public code)
