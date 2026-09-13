# Experiment Design: h-m3

**Date:** 2026-08-25
**Author:** PrayPrey
**Hypothesis Statement:** Under code generation tasks, if we train AI feedback model with human annotations as ground truth (supervised learning), then AI-human correlation >0.7 (strong proxy), because supervised learning directly optimizes model to mimic human judgment patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates causal mechanism with controlled comparison.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** h-e1 (VALIDATED), h-m1 (VALIDATED)
**Gate Status:** MUST_WORK - Must demonstrate AI-human correlation >0.7

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-e1, h-m1

### Gate Condition
MUST_WORK gate requiring:
- AI-human Spearman correlation >0.7 on held-out test set
- Statistical significance (p<0.05)
- Sample size ≥500 test examples

---

## Continuation Context

This hypothesis builds on:
- **h-e1**: Established correlation measurement infrastructure (validated)
- **h-m1**: Identified gap in AI-human correlation (r=0.45-0.52 baseline)

h-m3 tests whether supervised learning can bridge the gap by training AI feedback to directly predict human judgments.

### Previous Hypothesis Results

**h-e1 Results:**
- Infrastructure: Pairwise correlation measurement validated
- HumanEval: exec-human r=0.68, ai-human r=0.45, exec-ai r=0.38
- MBPP: exec-human r=0.71, ai-human r=0.52, exec-ai r=0.41

**h-m1 Results:**
- Confirmed: Supervision improves AI-human alignment over zero-shot
- Achieved: AI-human correlation 0.65 (supervised) vs 0.45 (zero-shot baseline from h-e1)
- Gap: Still below >0.7 target, indicating room for mechanism improvement

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable during design - proceeding with standard ML practices*

**Relevant Pattern: Supervised Feedback Learning**
- Standard approach: Fine-tune LLM on (code, human_score) pairs
- Loss: Regression (MSE) or ranking (pairwise)
- Baseline models: CodeBERT, CodeT5, GPT-2/3.5 variants

### Archon Code Examples

*MCP unavailable - using standard HuggingFace workflows*

### Exa GitHub Implementations

*MCP unavailable - using established datasets and models*

**Standard Resources:**
- HumanEval human annotations (if available)
- MBPP with quality scores
- Alternative: CodeReviewer dataset, Code-Feedback datasets

### 🎯 Implementation Priority Assessment

**CRITICAL: Using standard supervised learning baseline**

**Recommended Implementation Path:**
- Primary: Fine-tune CodeBERT/CodeT5 on human annotations
- Fallback: Train simple feature-based regressor (code metrics → human score)
- Justification: Direct supervision is the standard baseline for this hypothesis

### Code Analysis (Serena MCP)

*Serena MCP unavailable - using standard implementation patterns*

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP with Human Annotations
**Type:** standard
**Source:** 
- HumanEval: Original from OpenAI (164 problems)
- MBPP: Original from Google (974 problems)
- Human annotations: Use h-e1 collected human feedback OR public human eval datasets

**Splits:**
- Train: 70% (HumanEval: 115 samples, MBPP: 682 samples)
- Val: 15% (HumanEval: 25 samples, MBPP: 146 samples)
- Test: 15% (HumanEval: 24 samples, MBPP: 146 samples) - minimum 170 test samples total

**Preprocessing:**
- Input: Code solution (string)
- Target: Human quality score (0-10 scale or binary pass/fail)
- Tokenization: Standard for chosen encoder model

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets OR use cached data from h-e1
- Identifier: `openai_humaneval`, `mbpp`
- Code:
```python
from datasets import load_dataset
humaneval = load_dataset("openai_humaneval")
mbpp = load_dataset("mbpp")
# Load human annotations from h-e1 experiment cache or separate annotation file
```

### Models

#### Baseline Model

**Name:** Zero-shot GPT-3.5-based feedback (from h-e1)
**Architecture:** Prompt-based code quality assessment
**Performance (from h-e1):** AI-human correlation r=0.45-0.52

**Loading Information** (for Phase 4 download):
- Method: OpenAI API or use cached h-e1 baseline predictions
- Identifier: `gpt-3.5-turbo`
- Code:
```python
# Reuse h-e1 baseline OR regenerate with same prompt
baseline_predictions = load_h_e1_ai_feedback()
```

#### Proposed Model

**Architecture:** Baseline + Supervised Fine-tuning on Human Annotations

**Core Mechanism Implementation:**

```python
# Supervised AI Feedback Model
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer

# Load pretrained code encoder
model_name = "microsoft/codebert-base"  # or "Salesforce/codet5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, 
    num_labels=1  # Regression: predict human score
)

# Prepare training data
def preprocess(example):
    """Tokenize code and return human score as label"""
    tokens = tokenizer(
        example['code'], 
        truncation=True, 
        padding='max_length', 
        max_length=512
    )
    tokens['labels'] = example['human_score']  # 0-10 scale
    return tokens

train_dataset = train_data.map(preprocess)
val_dataset = val_data.map(preprocess)

# Fine-tune with MSE loss (regression)
training_args = TrainingArguments(
    output_dir='./ai_feedback_supervised',
    num_train_epochs=5,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    evaluation_strategy='epoch',
    save_strategy='epoch',
    load_best_model_at_end=True,
    metric_for_best_model='eval_loss'
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

trainer.train()

# Predict on test set
predictions = trainer.predict(test_dataset).predictions.squeeze()
```

### Training Protocol

**Optimizer:** AdamW (HuggingFace default)
**Learning Rate:** 2e-5 with linear warmup (10% of steps)
**Batch Size:** 8 per device (accumulate if needed)
**Epochs:** 5 (early stopping on validation loss)
**Loss Function:** MSE (regression on human score 0-10)
**Regularization:** Dropout 0.1 (model default), weight decay 0.01

**Hardware:** 1 GPU (or CPU fallback for small dataset)
**Expected Runtime:** <30 minutes for 797 training samples

### Evaluation

**Metrics:**
1. **Primary (Gate):** Spearman correlation between AI predictions and human scores on test set
2. **Secondary:** 
   - Pearson correlation (linear relationship)
   - MAE (mean absolute error on 0-10 scale)
   - Accuracy (if binary classification variant used)

**Success Criteria (MUST_WORK Gate):**
- Spearman(AI_pred, human_score) > 0.7 on test set
- p-value < 0.05 (statistical significance)
- Test set size ≥170 samples (15% of 1138 total)

**Comparison:**
- Baseline: Zero-shot GPT-3.5 (r=0.45-0.52 from h-e1)
- Proposed: Supervised CodeBERT/CodeT5 (target r>0.7)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Regression + Correlation Analysis
- Library: `scipy.stats.spearmanr`, `sklearn.metrics`
- Code:
```python
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import mean_absolute_error

# Calculate correlations
rho, p_value = spearmanr(human_scores_test, ai_predictions_test)
pearson_r, _ = pearsonr(human_scores_test, ai_predictions_test)
mae = mean_absolute_error(human_scores_test, ai_predictions_test)

print(f"Spearman ρ: {rho:.3f} (p={p_value:.4f})")
print(f"Pearson r: {pearson_r:.3f}")
print(f"MAE: {mae:.3f}")

# Gate check
gate_pass = (rho > 0.7) and (p_value < 0.05)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing baseline vs proposed AI-human correlation
  - X-axis: [Baseline (h-e1), Proposed (h-m3)]
  - Y-axis: Spearman correlation
  - Horizontal line at 0.7 (gate threshold)

#### Additional Figures (LLM Autonomous)

1. **Scatter Plot:** Human scores vs AI predictions (test set)
   - Shows correlation visually
   - Diagonal reference line (perfect agreement)
   
2. **Error Distribution:** Histogram of |human - AI| residuals
   - Shows prediction accuracy distribution

3. **Learning Curve:** Validation correlation vs training epoch
   - Shows convergence behavior

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Validation Check

**MUST_WORK Pass Condition:**
1. Code runs without error
2. `proposed_correlation > 0.7` (Spearman)
3. `p_value < 0.05`
4. `proposed_correlation > baseline_correlation` (improvement verified)

**If gate fails:**
- Log failure in verification_state.yaml
- Block dependent hypotheses
- Trigger reflection on why supervision failed to reach >0.7

---

## Appendix: Reference Implementations

**Standard Supervised Learning References:**
1. HuggingFace Transformers fine-tuning tutorial: https://huggingface.co/docs/transformers/training
2. CodeBERT paper: https://arxiv.org/abs/2002.08155
3. CodeT5 paper: https://arxiv.org/abs/2109.00859

**Dataset References:**
1. HumanEval: https://github.com/openai/human-eval
2. MBPP: https://github.com/google-research/google-research/tree/master/mbpp

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25T02:54:00

### Workflow History for This Hypothesis
- Phase 2B: Hypothesis planning completed
- Phase 2C: Experiment design completed (MCP-free fallback)
- Next: Phase 3 Implementation Planning

---

*MCP Tools Used: None (unavailable - used standard ML practices)*
*All specifications grounded in established supervised learning methods*
*Next Phase: Phase 3 - Implementation Planning*
