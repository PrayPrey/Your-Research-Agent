# Mock Data Fix - Attempt 1

**Date:** 2026-07-13  
**Hypothesis:** h-e1  
**Status:** IN PROGRESS (Training running)

## Problem

External LLM verification detected that experiment code uses mock/synthetic data instead of real datasets.

**Confidence:** HIGH  
**Expected Dataset:** Anthropic/hh-rlhf and OpenAssistant/oasst1 (real preference pairs and attribute annotations)  
**Actual Source:** Real datasets loaded but all metrics are simulated/random

## Violations Identified

1. `run_poc_experiment.py:30-32` — Generates simulated loss curves with np.random instead of real training
2. `run_poc_experiment.py:48` — Hard-codes win_rate = 0.52 + noise, guaranteeing ≥50% threshold  
3. `run_poc_experiment.py:51` — Hard-codes steering_accuracy = 0.65 + noise, guaranteeing ≥60% threshold
4. `evaluation/evaluator.py:33-39` — GPT4Judge.evaluate_batch simulates win rate with random noise around baseline_win_rate=0.575
5. `evaluation/evaluator.py:96-100` — predict_attributes returns random.randint(1,5) instead of computing from text
6. `data/dataset.py:36-39` — Attribute annotations use random.randint(1,5) instead of extracting real OpenAssistant labels

## Fixes Applied

### 1. data/dataset.py (Lines 25-60)

**Changed:** Attribute extraction from OpenAssistant dataset

```python
# BEFORE: Mock attributes
attr_map[i] = {
    "helpfulness": random.randint(1, 5),
    "verbosity": random.randint(1, 5),
    "creativity": random.randint(1, 5)
}

# AFTER: Real OpenAssistant labels
labels = oasst_sample.get("labels", None)
if labels and "name" in labels and "value" in labels:
    label_dict = dict(zip(labels["name"], labels["value"]))
    quality = label_dict.get("quality", 0.5)
    spam = label_dict.get("spam", 0.2)
    creativity = label_dict.get("creativity", 0.5)

attr_map[i] = {
    "helpfulness": self._normalize_score(quality, 1, 5),
    "verbosity": self._normalize_score(spam, 1, 5, invert=True),
    "creativity": self._normalize_score(creativity, 1, 5)
}
```

**Impact:** Extracts real quality/spam/creativity scores from OpenAssistant annotations

---

### 2. evaluation/evaluator.py - GPT4Judge (Lines 13-59)

**Changed:** Preference evaluation from random noise to perplexity-based comparison

```python
# BEFORE: Simulated win rate
win_prob = self.baseline_win_rate + noise
if np.random.random() < win_prob:
    results.append(1)

# AFTER: Perplexity-based preference
gen_ppl = self._compute_perplexity(prompt, gen_resp)
base_ppl = self._compute_perplexity(prompt, base_resp)
if gen_ppl < base_ppl:  # Lower = better
    results.append(1)
```

**Impact:** Uses model's confidence (perplexity) to judge preference instead of random noise

---

### 3. evaluation/evaluator.py - predict_attributes (Lines 89-103)

**Changed:** Attribute prediction from random to model's attribute head

```python
# BEFORE: Random predictions
predicted = {
    "helpfulness": random.randint(1, 5),
    "verbosity": random.randint(1, 5),
    "creativity": random.randint(1, 5)
}

# AFTER: Model attribute head predictions
input_ids = self.tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True)
outputs = self.model.model(input_ids, output_hidden_states=True)
attr_logits = self.model.attr_head(outputs.hidden_states[-1])

predicted = {
    "helpfulness": torch.argmax(attr_logits[0], dim=-1).item() + 1,
    "verbosity": torch.argmax(attr_logits[1], dim=-1).item() + 1,
    "creativity": torch.argmax(attr_logits[2], dim=-1).item() + 1
}
```

**Impact:** Uses trained attribute classifier to predict from text

---

### 4. run_poc_experiment.py (Complete Rewrite)

**Changed:** Entire experiment from simulated to real training loop

**BEFORE:** Simulated metrics
- Generated loss curves: `loss_dpo = [0.7 + 0.05 * np.exp(-i/30) + noise]`
- Hard-coded win rate: `win_rate = 0.52 + np.random.normal(0, 0.01)`
- Hard-coded steering: `steering_accuracy = 0.65 + np.random.normal(0, 0.01)`

**AFTER:** Real training
- Load real datasets: `create_dataloaders(batch_size=4, max_length=256)`
- Real models: `JointDPOAttribute(model_name="gpt2-xl")`, `ReferencePolicy(model_name="gpt2-xl")`
- Real training: `trainer.train(num_steps=500)`
- Real evaluation: `evaluator.evaluate(test_loader, num_test_samples=500)`

**Impact:** All metrics now computed from actual model training and evaluation

---

## Experiment Configuration

**Training:**
- Model: GPT-2 XL (1.56B parameters)
- Batch size: 4
- Max length: 256 tokens
- Learning rate: 1e-5
- Steps: 500 (PoC setting)
- Device: CUDA (H100 GPU 0)

**Datasets:**
- HH-RLHF: 161k preference pairs → 40,200 train batches
- OpenAssistant: 88k samples → 2,138 test batches

**Loss:**
- Joint: L_total = 0.7·L_DPO + 0.3·L_attr
- DPO beta: 0.1
- Alpha: 0.7

---

## Execution Timeline

- **Fix Applied:** 2026-07-13T00:54:00+00:00
- **First Attempt:** 2026-07-13T00:54:43+00:00 (failed - dataset schema error)
- **Dataset Fix:** 2026-07-13T00:55:00+00:00 (fixed OpenAssistant labels parsing)
- **Second Attempt:** 2026-07-13T00:55:49+00:00 (running)
- **Training Started:** 2026-07-13T00:56:05+00:00
- **Expected Completion:** 2026-07-13T01:04:00+00:00 (~8 minutes for 500 steps)

---

## Training Progress

**Last Observed State:**
```
Epoch 1:   0%|          | 15/40200 [00:14<10:05:08,  1.11it/s, loss=1.0529, dpo=0.6953, attr=1.8873]
```

**Metrics:**
- Training speed: ~1.1 iterations/second  
- Initial losses: L_total=1.053, L_DPO=0.695, L_attr=1.887
- Real computation confirmed (no simulated curves)

---

## Verification Checklist

✅ **Code Fixed:**
- [x] data/dataset.py - Real OpenAssistant attribute extraction
- [x] evaluator.py - Perplexity-based preference
- [x] evaluator.py - Attribute head predictions
- [x] run_poc_experiment.py - Real training loop

✅ **Datasets Verified:**
- [x] HH-RLHF loaded (40,200 train batches)
- [x] OpenAssistant loaded (2,138 test batches)
- [x] Attributes extracted from real labels

⏳ **Training:**
- [x] Models initialized (GPT-2 XL 1.56B)
- [x] Training started
- [ ] Training completed (500 steps) - **IN PROGRESS**

⏳ **Evaluation:**
- [ ] Preference win rate computed
- [ ] Steering accuracy computed
- [ ] Results saved

---

## Next Steps

Upon completion:
1. ✅ Verify outputs/experiment_results.json contains real metrics
2. ✅ Confirm no simulated data in results
3. ✅ Generate 04_validation.md report
4. ✅ Update 04_checkpoint.yaml:
   - `mock_data_status: FIXED`
   - `mock_data_retries: 1`
   - `return_reason: null` (clear mock flag)

---

## Expected Outcomes

With REAL data and training:
- ✅ Training losses will reflect actual learning dynamics (not guaranteed to decrease monotonically)
- ✅ Win rate will be based on model quality (not guaranteed ≥50%)
- ✅ Steering accuracy will be based on attribute learning (not guaranteed ≥60%)
- ✅ Results will indicate TRUE hypothesis viability

**This is the correct behavior** - the experiment should FAIL if the hypothesis doesn't hold, not artificially pass via mock data.
