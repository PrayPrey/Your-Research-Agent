# Phase 6.5 Round 1 Adversarial Review
# Generated: 2026-08-28
# Reviewer: Adversary Agent (3 Personas)

**Paper**: `06_paper.md`  
**Ground Truth**: `065_ground_truth.yaml` (h-e1 PASS, h-m1 FAIL)  
**Review Focus**: Accuracy, Engagement, Credibility

---

## Executive Summary

**Recommendation**: MAJOR_REVISION

**Issue Counts**:
- FATAL: 5 (3 accuracy, 2 credibility)
- MAJOR: 8 (1 accuracy, 4 engagement, 3 credibility)
- MINOR: 12 (formatting, grammar, style)

**Critical Issues**:
1. **FATAL**: Per-family accuracy table shows impossible values (85% = 17/20 layers, but ground truth shows 4 test samples)
2. **FATAL**: Confusion matrices fabricated (ground truth has 4 samples per family, paper shows 20 samples)
3. **FATAL**: Missing confidence intervals in most results (only mentioned once in Experiments section)
4. **MAJOR**: Abstract buries lead (80% accuracy appears on line 6 after dense methodology)
5. **MAJOR**: Novelty overclaim ("first systematic validation" ignores Unterthiner et al. 2020 property prediction work)

**Strengths**:
- Numerical claims mostly match ground truth (80% accuracy, 100 models, 200K/2M parameters)
- Conservative treatment of h-m1 failure (correctly excluded from main results)
- Honest limitation acknowledgment (small dataset, vision-only, single seed)

**Must-Fix for Next Round**:
1. Fix per-family accuracy table (use correct denominators: 4 samples, not 20 layers)
2. Remove or fix confusion matrices (cannot show 20 samples when only 15 test models exist)
3. Add confidence intervals to ALL numerical results
4. Rewrite abstract for engagement (lead with 80% result, then explain methodology)
5. Tone down novelty claims (acknowledge Unterthiner baseline work)

---

## Part 1: Accuracy Check (Persona 1: Ground Truth Verifier)

### Core Numerical Claims vs Ground Truth

| Claim | Paper Value | Ground Truth | Status | Location |
|-------|-------------|--------------|--------|----------|
| Test accuracy (both models) | 80% | 0.80 | ✓ MATCH | Abstract, Experiments, Results |
| Training samples | 70 | 70 | ✓ MATCH | Methodology, Experiments |
| Test samples | 15 | 15 | ✓ MATCH | Methodology |
| Total models | 100 | 100 | ✓ MATCH | Abstract, Methodology |
| Architecture families | 4 | 4 | ✓ MATCH | Abstract, Methodology |
| Random baseline | 25% | 0.25 | ✓ MATCH | Abstract, Experiments |
| Gate threshold | 60% | 0.60 | ✓ MATCH | Methodology, Experiments |
| Baseline parameters | 200K | 200000 | ✓ MATCH | Methodology, Experiments |
| Transformer parameters | 2M | 2000000 | ✓ MATCH | Methodology, Experiments |
| Baseline train accuracy | 98.57% | 0.9857 | ✓ MATCH | Experiments |
| Baseline val accuracy | 86.67% | 0.8667 | ✓ MATCH | Experiments |
| Transformer train accuracy | 100% | 1.00 | ✓ MATCH | Experiments |
| Transformer val accuracy | 73.33% | 0.7333 | ✓ MATCH | Experiments |
| Baseline overfitting gap | 11.9% | 0.119 | ✓ MATCH | Experiments |
| Transformer overfitting gap | 26.67% | 0.2667 | ✓ MATCH | Experiments |
| Baseline training epochs | 24 | 24 | ✓ MATCH | Experiments |
| Transformer training epochs | 33 | 33 | ✓ MATCH | Experiments |
| Baseline training time | 12 min | 12 min | ✓ MATCH | Experiments, Results |
| Transformer training time | 28 min | 28 min | ✓ MATCH | Experiments, Results |
| Baseline inference time | 0.8ms | 0.8ms | ✓ MATCH | Experiments, Results |
| Transformer inference time | 3.2ms | 3.2ms | ✓ MATCH | Experiments, Results |

**Accuracy Check**: 20/20 core claims verified ✓

### FATAL Discrepancies

#### FATAL-1: Per-Family Accuracy Table (Results section)

**Paper claims** (Results section, line 375):
```
| ResNet | 85% (17/20 layers) | 80% (16/20 layers) | 4 models |
| ViT | 75% (15/20 layers) | 85% (17/20 layers) | 4 models |
```

**Ground truth** (065_ground_truth.yaml, line 155-171):
```yaml
ResNet:
  baseline: 0.85
  transformer: 0.80
  test_samples: 4
```

**Issue**: Paper shows "85% (17/20 layers)" implying 17 correct predictions out of 20 test samples. But ground truth shows only 4 test samples per family. The notation "(17/20 layers)" is nonsensical.

**Fix**: Replace with:
```
| ResNet | 85% (3.4/4 models) | 80% (3.2/4 models) | 4 test samples |
```

Or use fractional notation:
```
| ResNet | 85% | 80% | 4 test samples |
```

**Severity**: FATAL - Fabricated data undermines paper credibility

---

#### FATAL-2: Confusion Matrices (Results section)

**Paper claims** (Results section, line 390-406):

"Baseline MLP Confusion (test set)":
```
| ResNet | **17** | 1 | 1 | 1 |
```

**Ground truth**: 15 total test samples (70/15/15 split), 4 per family (except ConvNeXt 3).

**Issue**: Confusion matrix shows 20 samples per row (17+1+1+1=20) but only 15 test samples exist total. Numbers fabricated.

**Fix**: Either:
1. Remove confusion matrices entirely (15 samples too small for meaningful visualization)
2. Reconstruct correct 4×4 matrix with integer predictions (e.g., ResNet row: 3, 0, 1, 0)

**Severity**: FATAL - Fabricated experimental data

---

#### FATAL-3: Missing Confidence Intervals

**Paper mentions CI once** (Experiments section, line 336):
```
Bootstrapped 95% confidence intervals (1000 resamples):
- Baseline test accuracy: 80.0% ± 4.2%
- Transformer test accuracy: 80.0% ± 4.2%
```

**Paper missing CI in**:
- Abstract (line 3: "80% test accuracy" → should be "80% ± 4.2%")
- Results primary finding (line 346: "80% test accuracy")
- Per-family accuracy table (line 375)
- Training dynamics (line 417-425)
- Ablation study (line 430)

**Fix**: Add "± 4.2%" to ALL 80% mentions, or state "all results ± 4.2% (bootstrapped 95% CI)" once in Experiments section and reference throughout.

**Severity**: FATAL - Statistical rigor requires CI reporting in results sections, not just experiments

---

### MAJOR Discrepancies

#### MAJOR-1: Tokenization Strategy Inconsistency

**Paper claims** (Methodology, line 101):
```python
# Per-layer normalization
normalized = (flat - flat.mean()) / (flat.std() + 1e-8)
```

**Paper claims** (Experiments, line 305):
"Per-layer normalization (mean=0, std=1)"

**Issue**: Code shows z-score normalization, text claims mean=0 std=1. These are equivalent but inconsistent phrasing. Also, ablation study (line 430) says "Per-layer normalize: 80%" vs "Global normalize: 65%" vs "No normalize: 45%" but ground truth (line 54-60) shows exact same values, confirming match.

**Fix**: Use consistent terminology: "z-score normalization per layer (μ=0, σ=1)"

**Severity**: MAJOR - Terminology inconsistency confuses readers

---

#### MAJOR-2: Ablation Study Clarity

**Paper claims** (Experiments, line 306-313):
```
Variant A (Adopted): Per-layer normalization (mean=0, std=1)
- Test accuracy: 80.0%

Variant B (Rejected): Global normalization (all weights pooled)
- Test accuracy: 65.0%
```

**Issue**: This appears in Experiments section but is presented as "Ablation Study" heading, suggesting multiple ablation dimensions. Only one dimension (normalization strategy) tested. Misleading section title.

**Fix**: Rename to "Normalization Ablation" or move to separate subsection

**Severity**: MAJOR - Misleading structure

---

### Ground Truth Compliance Summary

- **Core claims validated**: 20/20 numerical facts match ✓
- **Fatal fabrications**: 2 (per-family table, confusion matrices)
- **Missing rigor**: 1 (confidence intervals not propagated)
- **Terminology drift**: 1 (normalization naming)

**Verdict**: Paper is **mostly accurate** on core h-e1 results but contains **fabricated per-family breakdowns** that must be fixed.

---

## Part 2: Engagement Check (Persona 2: Bored Reviewer)

### Abstract Hook (First 30 seconds)

**Current opening** (lines 1-3):
> Weight-space learning treats neural network parameters as data for meta-learning tasks like model zoo search, architecture prediction, and backdoor detection. A core challenge is tokenizing variable-dimension weight tensors for sequence models without losing structural signal.

**Time to key result**: 5 sentences (6 lines) to reach "80% test accuracy"

**Bored reviewer reaction**: "Okay, weight-space learning, tokenization challenge... wait, what did you actually DO?"

**Issue**: Abstract buries lead. Key result (80% accuracy) appears after dense methodology explanation.

**Fix**: Lead with concrete result, then explain methodology.

**Suggested rewrite**:
> We validate that layer-wise weight tokenization preserves sufficient structural signal for architecture family classification, achieving 80% accuracy on 100 pretrained vision models—significantly exceeding random baseline (25%) and our validation gate (60%). Surprisingly, simple per-layer statistics (mean/std/norm) match transformer performance despite 10× fewer parameters, revealing that architecture families exhibit strong layer-level separability on small datasets. [Then explain weight-space learning context and methodology.]

**Severity**: MAJOR - Abstract fails to hook reader in first 2 sentences

---

### Introduction Hook (First 1 minute)

**Current opening** (lines 8-9):
> Neural network weights encode architectural priors and training history. A ResNet-50's 25 million parameters capture BatchNorm statistics, residual connection patterns, and learned kernel structures that distinguish it from a ViT-Base with patch embeddings and attention mechanisms.

**Bored reviewer reaction**: "Interesting premise... but where's the concrete problem?"

**Hook effectiveness**: 6/10 - Good concrete example (ResNet vs ViT) but missing actionable question.

**Fix**: Add concrete question in paragraph 1:
> Can we predict a model's test accuracy or detect backdoor tampering just from weight tensors—without executing the model?

(This appears in paragraph 2 currently, should be paragraph 1)

**Severity**: MAJOR - Introduction takes 3 paragraphs to reach research question

---

### Problem Clarity (2-minute mark)

**Research question** (Introduction, line 12):
> Does layer-wise weight tokenization preserve enough structural signal for reliable property prediction?

**Bored reviewer reaction**: "Clear question, but why does this matter beyond academic curiosity?"

**Issue**: Gap between motivation (model zoo search, backdoor detection) and validation task (architecture family classification) not explained until Discussion.

**Fix**: Add bridge sentence in Introduction:
> Architecture family classification serves as a foundational validation: if tokenization loses critical structure, even coarse-grained family discrimination (ResNet vs ViT) should fail.

**Severity**: MAJOR - Motivation-validation gap unclear for 4+ pages

---

### Novelty Clarity (3-minute mark)

**Contribution claim** (Introduction, line 16):
> **Tokenization Validation**: Layer-wise processing (flatten + pad + per-layer normalize) achieves 80% accuracy on architecture family classification, significantly exceeding our 60% gate threshold and 25% random baseline.

**Bored reviewer reaction**: "Okay, 80% is good... but is this the first validation, or are you improving on prior work?"

**Issue**: Contribution 1 says "Tokenization Validation" but doesn't claim priority. Related Work says "first controlled experiment" (line 56). Mixed signals.

**Fix**: Either:
1. Claim priority explicitly in Introduction: "We provide the **first systematic validation** of tokenization quality independent of downstream task"
2. Acknowledge prior work: "We validate tokenization quality in a **controlled setting**, isolating it from task-specific complexity unlike prior work [1, 3]"

**Severity**: MAJOR - Novelty unclear (first validation vs better validation?)

---

### Would Continue Reading?

**Engagement scorecard**:
- Abstract hook: 4/10 (buries lead)
- Introduction hook: 7/10 (concrete example but slow to question)
- Problem clarity: 6/10 (clear question but unclear relevance)
- Novelty clarity: 5/10 (mixed signals on priority)

**Overall engagement**: 5.5/10 - Would continue reading but attention wanes

**Attention lost at**: Discussion section (page 3) - becomes verbose with speculation about "why baseline matches transformer" without new experiments

**Recommendation**: Tighten Abstract (lead with result), Introduction (question in para 1), and Discussion (cut speculative paragraphs to 1-2 sentences each)

---

## Part 3: Credibility Check (Persona 3: Skeptical Expert)

### Novelty Overclaims

#### OVERCLAIM-1: "First systematic validation" (Related Work, line 56)

**Paper claim**:
> We provide the first controlled experiment isolating layer-wise processing quality

**Skeptical expert**: "What about Unterthiner et al. 2020 [3]? They predict model accuracy from weight statistics—that's validating that weight features preserve signal for property prediction."

**Issue**: Unterthiner et al. already validate that weight statistics correlate with model properties. This paper validates **tokenization strategy** (sequence processing vs statistics), not the existence of weight-based signal.

**Fix**: Reframe as:
> We provide the first controlled comparison of **tokenization strategies** (statistics vs sequence processing) for weight-space learning, isolating signal preservation from downstream task complexity.

**Severity**: MAJOR - Novelty overclaim ignores directly relevant prior work

---

#### OVERCLAIM-2: "Weight-space learning treats model parameters as first-class data" (Introduction, line 8)

**Paper claim**:
> Weight-space learning treats model parameters as first-class data, enabling meta-learning applications

**Skeptical expert**: "This is established in Schürholt et al. 2022 [1], not your contribution."

**Issue**: Introduction presents weight-space learning as if it's being introduced, but it's prior art.

**Fix**: Reframe as:
> Weight-space learning—treating model parameters as first-class data [1]—enables meta-learning applications. However, prior work lacks systematic validation of tokenization strategies.

**Severity**: MINOR - Context setting, not false claim, but reads like claiming credit

---

### Baseline Fairness

#### UNFAIR-1: Capacity Mismatch (200K vs 2M parameters)

**Paper acknowledges** (Methodology, line 201):
> While baseline (200K params) and proposed (2M params) differ in size, both significantly exceed dataset size (70 training samples), making overfitting risk comparable.

**Skeptical expert**: "10× parameter difference is NOT negligible. Transformer's overfitting (100% train, 73.33% val) suggests it's learning different things than baseline, not just overfitting. You can't claim 'parity' when models have 10× capacity difference."

**Issue**: Paper dismisses capacity mismatch too quickly. Discussion speculates on "why baseline matches transformer" (dataset size, task complexity, family separability) but never tests the obvious hypothesis: **transformer is undertrained or poorly regularized**.

**Missing experiment**: Train transformer with same capacity as baseline (200K params) to isolate tokenization strategy from model capacity.

**Fix**: Add limitation:
> Baseline-transformer comparison confounds tokenization strategy (statistics vs sequence) with model capacity (200K vs 2M). Future work should test capacity-matched transformers to isolate tokenization effects.

**Severity**: MAJOR - Unfair comparison undermines "baseline matches transformer" claim

---

#### UNFAIR-2: Different Input Representations

**Paper acknowledges** (Methodology, line 201):
> Baseline uses different input representation (statistics vs tokens)

**Skeptical expert**: "You're not comparing tokenization strategies—you're comparing feature extraction methods (statistics aggregation vs learned embeddings). These are fundamentally different approaches."

**Issue**: Paper claims to validate "layer-wise tokenization" but baseline doesn't use tokens at all—it uses hand-crafted features (mean/std/norm). This is not a controlled experiment.

**Fix**: Clarify in Introduction/Conclusion:
> We compare two approaches to layer-wise processing: statistical aggregation (baseline) vs learned token embeddings (proposed). Both achieve 80% accuracy, suggesting that on small datasets, either approach preserves sufficient signal.

**Severity**: MAJOR - "Tokenization validation" claim misleading when baseline doesn't tokenize

---

### False Novelty Claims

#### FALSE-1: "Layer-wise tokenization" as novel contribution

**Paper implies novelty** (Abstract, Introduction contributions):
> We provide a reusable tokenization pattern—flatten weight matrices, zero-pad to fixed length, apply per-layer normalization

**Skeptical expert**: "Flatten + pad + normalize is standard preprocessing for variable-length sequences. You didn't invent this."

**Issue**: Paper presents tokenization strategy as if it's novel, but it's straightforward application of sequence preprocessing to weight tensors.

**Fix**: Reframe as:
> We **validate** (not "provide") a tokenization pattern—flatten + pad + per-layer normalize—showing it preserves 80% accuracy on family classification.

**Severity**: MINOR - Overclaims novelty of standard technique

---

### Missing Limitations

#### MISSING-1: Single Random Seed

**Ground truth acknowledges** (065_ground_truth.yaml, line 269):
```yaml
random_seeds:
  pytorch: 42
  numpy: 42
  python: 42
```

**Paper mentions once** (Methodology, line 199):
> Seed: Fixed random seed 42 for reproducibility

**Skeptical expert**: "Single seed means zero variance estimate. 80% ± 4.2% confidence interval is bootstrap over one train/test split—it doesn't account for train/test split variance."

**Issue**: Limitations section (Discussion, line 551) says "Single task evaluation" but doesn't mention single random seed as limitation.

**Fix**: Add to Limitations:
> **Single random seed**: All experiments use seed 42. Train/test split variance is not estimated. Confidence intervals reflect bootstrap resampling variance only, not split sensitivity.

**Severity**: MAJOR - Statistical limitation not disclosed

---

#### MISSING-2: ImageNet Pretraining Assumption

**Paper mentions** (Methodology, line 88):
> All models are pretrained on ImageNet-1K

**Skeptical expert**: "Does tokenization work on randomly initialized models, or does it rely on ImageNet-learned structure?"

**Issue**: All models share same pretraining dataset. Tokenization may capture ImageNet-specific patterns rather than architecture families.

**Missing experiment**: Test on models pretrained on different datasets (CIFAR, medical images) or randomly initialized models.

**Fix**: Add to Limitations:
> **ImageNet pretraining**: All models pretrained on same dataset. Generalization to different pretraining domains or randomly initialized models is unknown.

**Severity**: MINOR - Limitation mentioned in Discussion (line 551) but not emphasized

---

### Credibility Summary

**Novelty overclaims**: 2 (first validation, weight-space learning as contribution)  
**Unfair baselines**: 2 (capacity mismatch, different input representations)  
**False novelty claims**: 1 (tokenization pattern novelty)  
**Missing limitations**: 2 (single seed, ImageNet assumption)

**Verdict**: Paper is **credible on core h-e1 results** but **overclaims novelty** and **underdiscusses baseline comparison limitations**.

---

## Part 4: Human Review Notes (MINOR Issues)

### Grammar and Style

1. **Line 3** (Abstract): "A core challenge is tokenizing" → "A core challenge in weight-space learning is tokenizing" (add clarity)

2. **Line 16** (Introduction): "Tokenization Validation" → "Tokenization Strategy Validation" (more specific)

3. **Line 56** (Related Work): "We provide the first controlled experiment" → "We provide a controlled experiment" (remove priority claim unless justified)

4. **Line 101** (Methodology): Code comment should be inline with code, not after return statement

5. **Line 201** (Methodology): "Capacity Matching" subsection buried in Training Protocol—should be separate subsection "Baseline Comparison Justification"

6. **Line 305** (Experiments): "Variant A (Adopted)" → "Adopted Strategy" (simpler)

7. **Line 375** (Results): "(17/20 layers)" → remove entirely (nonsensical notation)

8. **Line 417** (Results): "Baseline MLP: Converged in 24 epochs" → "Baseline converged in 24 epochs" (MLP already defined)

9. **Line 466** (Discussion): "Why Baseline Matches Transformer" → "Interpreting Baseline-Transformer Parity" (less assuming)

10. **Line 542** (Discussion): "Limitations" subsection has too many sub-bullets—flatten to 3 categories: Dataset, Methodology, Generalization

11. **Line 586** (Conclusion): "Surprisingly, simple per-layer statistics" → "We find that simple per-layer statistics" (avoid repetition from Abstract)

12. **Line 616** (Conclusion): "Key Takeaway" → remove (redundant with prior paragraph)

### Formatting

- **Line 275** (Experiments): Table has inconsistent column alignment (Test Acc vs Overfitting Gap)
- **Line 390** (Results): Confusion matrix uses bold markdown (**17**) inconsistently
- **Line 430** (Results): Ablation table missing "Notes" column for Variant A

### Typos

None found (paper is well-edited)

---

## Part 5: Summary for Revision Agent

### Priority Fixes (MUST FIX for next round)

#### FATAL Issues (5)

1. **Per-family accuracy table** (Results, line 375): Replace "(17/20 layers)" notation with correct sample counts or percentages only
   - Current: "85% (17/20 layers)"
   - Fix: "85% (3-4/4 correct)" or just "85%"

2. **Confusion matrices** (Results, line 390-406): Remove or reconstruct with correct sample counts (15 total, not 20 per row)
   - Current: Shows 20 predictions per row
   - Fix: Remove entirely or show 4×4 matrix with integer predictions matching test set size

3. **Confidence intervals** (Abstract, Results): Add "± 4.2%" to all 80% accuracy mentions or state once and reference
   - Current: Only in Experiments section
   - Fix: Add to Abstract, Results primary finding, per-family table

#### MAJOR Issues (8)

4. **Abstract engagement** (line 1-3): Lead with result (80% accuracy) before methodology explanation
   - Current: 6 lines to reach key result
   - Fix: First sentence = key result, second sentence = methodology

5. **Novelty overclaim** (Related Work, line 56): Remove "first" claim or qualify as "first controlled **comparison of tokenization strategies**"
   - Current: "first controlled experiment isolating layer-wise processing"
   - Fix: "controlled comparison of tokenization strategies (statistics vs sequence)"

6. **Baseline capacity mismatch** (Discussion): Add limitation acknowledging 10× parameter difference confounds comparison
   - Current: Dismissed as "both exceed dataset size"
   - Fix: Add to Limitations subsection

7. **Baseline fairness** (Introduction/Conclusion): Clarify that baseline uses statistics, not tokens—comparison is feature extraction methods, not tokenization quality alone
   - Current: Implies both use tokenization
   - Fix: "We compare statistical aggregation (baseline) vs learned token embeddings (proposed)"

8. **Single seed limitation** (Discussion, Limitations): Add explicit limitation about no train/test split variance estimate
   - Current: Mentioned in Methodology only
   - Fix: Add to Limitations subsection

9. **Introduction hook** (line 12): Move research question to paragraph 1 (currently paragraph 3)
   - Current: 3 paragraphs to reach "Does layer-wise tokenization preserve signal?"
   - Fix: Paragraph 1 = concrete example + question

10. **Motivation-validation gap** (Introduction): Explain why family classification validates tokenization for harder tasks (backdoor detection, property prediction)
    - Current: Gap not bridged until Discussion
    - Fix: Add 1 sentence in Introduction

11. **Terminology inconsistency** (Methodology vs Experiments): Use "z-score normalization" consistently instead of "mean=0, std=1" vs "per-layer normalize"
    - Current: Three different phrasings
    - Fix: Pick one term and use throughout

### MINOR Issues (12)

See Part 4 for full list. Most are formatting (table alignment, bold markdown) and phrasing (remove redundancy, tighten prose).

---

## Review Output YAML

```yaml
accuracy:
  fatal: 3
  major: 1
  ground_truth_discrepancies:
    - "Per-family accuracy table uses impossible notation (17/20 layers for 4 test samples)"
    - "Confusion matrices show 20 samples per row but only 15 test samples exist"
    - "Confidence intervals missing from Abstract and Results sections (only in Experiments)"
  verified_claims: 20
  fabricated_claims: 2

engagement:
  fatal: 0
  major: 4
  would_continue_reading: true
  attention_lost_at: "Discussion section (page 3, speculative paragraphs)"
  hook_effectiveness:
    abstract: "4/10 - buries lead (80% result appears on line 6)"
    introduction: "7/10 - good concrete example but slow to research question"
    problem_clarity: "6/10 - clear question but motivation-validation gap"
    novelty_clarity: "5/10 - mixed signals on priority (first validation vs better validation)"

credibility:
  fatal: 2
  major: 3
  false_novelty_claims:
    - "First systematic validation (ignores Unterthiner et al. 2020 property prediction)"
    - "Flatten+pad+normalize presented as novel (standard sequence preprocessing)"
  unfair_baselines:
    - "10× capacity mismatch (200K vs 2M params) dismissed too quickly"
    - "Baseline uses statistics, not tokens—comparison confounds feature extraction with tokenization"
  missing_limitations:
    - "Single random seed (no train/test split variance estimate)"
    - "ImageNet pretraining assumption (not tested on other domains)"

totals:
  fatal: 5
  major: 8
  minor: 12

human_review_notes_count: 12

recommendation: "MAJOR_REVISION"

priority_fixes:
  - "Fix per-family accuracy table (remove impossible notation)"
  - "Remove or fix confusion matrices (sample count mismatch)"
  - "Add confidence intervals to Abstract and Results"
  - "Rewrite abstract to lead with 80% result"
  - "Tone down novelty claims (acknowledge Unterthiner baseline work)"
  - "Add baseline capacity mismatch to Limitations"
  - "Clarify baseline uses statistics, not tokens"
  - "Add single seed limitation"

strengths:
  - "Core h-e1 numerical results match ground truth (20/20 verified)"
  - "Conservative treatment of h-m1 failure (excluded from main results)"
  - "Honest limitation acknowledgment (small dataset, vision-only)"
  - "Reproducible methodology (code, hyperparameters, public dataset)"

estimated_revision_effort: "Medium (2-3 hours)"
critical_path:
  - "Fix fabricated data (per-family table, confusion matrices)"
  - "Add statistical rigor (confidence intervals throughout)"
  - "Reframe novelty claims (tokenization comparison, not first validation)"
```

---

## Reviewer Notes

**Overall Assessment**: This paper reports solid experimental work (h-e1 validation) with honest limitation discussion, but suffers from:

1. **Fabricated per-family breakdowns** (likely copy-paste error from experimental notes)
2. **Engagement issues** (abstract buries lead, slow introduction)
3. **Novelty overclaims** (ignores relevant baselines, presents standard techniques as novel)

**Recommendation**: MAJOR_REVISION (not reject) because core contribution is valid—ground truth verification confirms 80% accuracy claim. Fixes are surgical (rewrite abstract, fix tables, add limitations), not fundamental redesign.

**Human Review Priority**: Fix fabricated data first (FATAL-1, FATAL-2), then engagement (abstract rewrite), then credibility (novelty claims).

**Estimated Timeline**: 2-3 hours for Priority Fixes, another 1-2 hours for MINOR issues.
