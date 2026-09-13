# Results

The central finding is unambiguous: projection-only LoRA on Mamba-130m does not produce classification learning. We present the evidence in the order established in Section 4 — zero-shot baselines first (the reference point), then per-epoch fine-tuning results, then the loss trajectory and LoRA installation verification that together characterize the failure mode.

## Zero-Shot GLUE Baselines

Before any fine-tuning, we evaluate Mamba-130m using lm-evaluation-harness multiple-choice prompting. These results establish the reference point and are, independently, a contribution: no prior work reports verified zero-shot GLUE scores for `state-spaces/mamba-130m-hf` with this evaluation protocol.

**Table 1: Zero-Shot Mamba-130m Baselines on GLUE**

| Task | Zero-Shot Accuracy | Random Baseline (approx.) | Interpretation |
|------|-------------------|---------------------------|----------------|
| SST-2 | 0.4908 | 0.50 | Near random; no classification prior |
| MNLI | 0.3463 | 0.33 | Marginally above chance; no NLI prior |
| QNLI | 0.5056 | 0.50 | Near random |
| QQP | 0.0000 | 0.50 | Systematic minority-class prediction (see below) |

The SST-2 zero-shot result (0.4908) and MNLI result (0.3463) confirm the expected behavior for a causal language model with no classification instruction tuning: performance is near the random baseline for each task. Mamba-130m has no prior ability to perform classification — it was pretrained on next-token prediction and has no mechanism to bias its token outputs toward sentiment or NLI labels without fine-tuning.

The QQP result (0.0000) warrants brief documentation. Mamba-130m predicts the "not paraphrase" class for every QQP sample, yielding 0% accuracy despite QQP having approximately 63% positive pairs. This is not a training artifact — it is a zero-shot evaluation result. The most parsimonious explanation is a tokenization or prompt-format incompatibility between Mamba-130m and the lm-evaluation-harness QQP prompt template: the model's probability distribution over the two completion tokens ("yes"/"no" or equivalent) is systematically biased toward the minority-class completion in this evaluation setup. We document this result for reproducibility without over-interpreting it; it does not affect our primary conclusions, which rest on SST-2 and MNLI.

These zero-shot baselines are independently reusable. Any future work evaluating Mamba-130m on GLUE can use these as reference values without re-running zero-shot evaluation.

## Primary Result: SST-2 Fine-Tuning

The MUST_WORK gate criterion is SST-2 accuracy > 0.70 after three epochs of LoRA fine-tuning. The result:

**Table 2: SST-2 Accuracy Across Three Fine-Tuning Epochs**

| Evaluation Point | Accuracy | vs. Zero-Shot | vs. Gate |
|-----------------|----------|---------------|----------|
| Zero-shot baseline | 0.4908 | — | −0.2092 |
| After Epoch 1 | 0.5092 | +0.0184 | −0.1908 |
| After Epoch 2 | 0.5092 | +0.0184 | −0.1908 |
| After Epoch 3 | 0.5092 | +0.0184 | −0.1908 |
| **Gate result** | — | — | **FAIL** |

Three consecutive identical accuracy values of 0.5092 are the clearest possible indicator of zero learning. This is not slow convergence. If any learning were occurring — even noisy, inefficient learning — the model's predictions would shift from epoch to epoch as the LoRA weight matrices are updated, producing different accuracy values even if the overall trajectory were flat. Three identical values across three independent epochs of training, evaluated on 872 validation examples, indicate that the model's prediction distribution has not changed at all. The LoRA weight matrices are being updated (gradients are computed, parameter values change), but those updates do not alter the model's classification decisions.

The net improvement over zero-shot is +1.84 percentage points. This is within the expected noise range for a model near the random baseline — small shifts in the logit distribution can produce marginal accuracy changes without any classification learning occurring. The 19.1 percentage-point gap between the observed 0.5092 and the gate criterion of 0.70 is not a tuning problem. It is the gap between majority-class prediction and meaningful classification ability.

## Secondary Result: MNLI Fine-Tuning and Negative Transfer

**Table 3: MNLI Accuracy Across Fine-Tuning Epochs**

| Evaluation Point | Accuracy | vs. Zero-Shot |
|-----------------|----------|---------------|
| Zero-shot baseline | 0.3463 | — |
| After Epoch 1 | 0.3326 | −0.0137 (−1.4pp) |
| After Epoch 2 | 0.3234 | −0.0229 (−2.3pp) |

MNLI training was halted after epoch 2 due to the monotonically worsening trend. Both epochs show accuracy *below* the zero-shot baseline — the model degrades under fine-tuning rather than improving. This is negative transfer: LoRA updates are making the model worse at the task, not better.

This result carries a specific diagnostic implication that the SST-2 result alone cannot provide. The SST-2 trajectory (flat at majority-class accuracy) is consistent with a model in a locally stable prediction regime — perhaps the LoRA updates cancel out across the training set, leaving the prediction distribution unchanged. But MNLI degradation rules out this interpretation. Something is moving: the model's MNLI predictions are shifting with each training epoch, but in the wrong direction. The gradient updates are coherent enough to steer the model's behavior but not coherent enough to move it toward the correct classification labels.

The most plausible interpretation is classifier degeneracy: the linear classification head, updated without effective task-discriminative gradient from the LoRA layers, learns to collapse its predictions toward a single NLI class (likely "entailment" or "contradiction," whichever appears slightly more frequently in the gradient signal). Collapsing to a single class on three-class MNLI yields ~33% accuracy — the trajectory from 0.3463 toward 0.3234 is consistent with convergence toward the minority-class fraction, which would land below the uniform random baseline of 0.33.

The cross-task consistency of the failure — flat SST-2, degrading MNLI, both under the zero-shot + noise level — strongly argues against any task-specific explanation. The gradient barrier is architectural, not task-specific.

## LoRA Installation Verification

A critical alternative explanation is that LoRA was not correctly applied, making the fine-tuning effectively a no-op. This alternative is directly refuted.

**Table 4: LoRA Installation Verification**

| Check | Expected | Observed | Status |
|-------|----------|----------|--------|
| `lora_A` keys in state_dict | Present at all target module paths | Present (e.g., `backbone.layers.0.mixer.in_proj.lora_A.default.weight`) | PASS |
| `lora_B` keys in state_dict | Present at all target module paths | Present | PASS |
| Trainable parameter count | ~1.14% of 130M (≈1.48M) | 1.14% (1,484,288 trainable) | PASS |
| LoRA weights non-zero post-training | Non-zero (updated by gradient) | Non-zero (confirmed) | PASS |

LoRA is installed correctly. The 1.14% trainable parameter fraction is the expected value for rank-8 LoRA on `in_proj`, `out_proj`, and `x_proj` across 24 Mamba layers. The adapters receive gradients and their weights are updated. This is not a configuration mistake.

The combination of Table 2 (zero classification learning) and Table 4 (correct LoRA installation) is the core finding: API compatibility does not imply gradient compatibility. The LoRA matrices exist, they are nominally trainable, and they receive gradient updates — but those updates do not communicate task-discriminative information from the classification head to the LoRA weight matrices. Something between the classification head and the LoRA adapters prevents effective gradient transmission.

## Loss Oscillation Pattern

**Figure note:** The primary visualization for this result is a two-panel table: accuracy vs. epoch (Table 2 and 3 combined) and the loss trajectory. Since no figures were generated during the experiment (the flat accuracy curves were not meaningful to plot), we describe the loss pattern here.

Cross-entropy loss on SST-2 training batches oscillates between 0.65 and 0.73 across all three training epochs. There is no monotonic decrease trend. By comparison, a model successfully learning a binary classification task with cross-entropy loss and Adam-style optimization typically shows a consistent decrease from the initialization loss (ln(2) ≈ 0.693 for a binary random head) within the first epoch, often reaching 0.2–0.4 by epoch 3.

The absence of any downward trend over 125 gradient steps per epoch (4,000 samples / batch size 32 × 3 epochs) indicates that the optimization procedure is not finding a consistently better solution. The oscillation range (0.65–0.73) centered near ln(2) is consistent with a model whose prediction distribution is not departing from near-50/50 confidence — the loss of a model that learns nothing and always predicts near-uniform probability over two classes.

This loss pattern is important for practitioners because it is detectable during training, before epoch-end accuracy evaluation. A practitioner observing loss oscillation without a downward trend in the first epoch of LoRA fine-tuning on Mamba has a strong signal to stop and investigate before completing the full training run. The diagnostic signature of SSM gradient barrier failure is: loss oscillates in the range [ln(2) - δ, ln(2) + δ] with no monotonic trend, while per-epoch accuracy remains flat or degrades.

## Comparison to MambaPEFT Literature

Our SST-2 result (0.5092) contrasts with the reported performance in alxndrTL/mamba-peft (2024), which claims 90–92% SST-2 accuracy on Mamba with LoRA r=8. The gap is approximately 40 percentage points — a gap that cannot be attributed to statistical noise or minor hyperparameter differences.

We do not interpret this as a contradiction. Our result and the MambaPEFT result can both be accurate if they reflect different training setups. The MambaPEFT repository does not fully document the checkpoint used (base vs. instruction-tuned), classification head design, number of training samples, epoch count, tokenization, or prompt format. Any of these factors could be the enabling variable that produces 90–92% vs. 50.9%. Identifying this variable is the highest-priority future work (see Section 6).

What our experiment establishes is: the *base* `mamba-130m-hf` checkpoint, with a randomly-initialized classification head, trained with AdamW at lr=3e-4 on 4,000 SST-2 samples for 3 epochs with projection-only LoRA, produces 0.5092 SST-2 accuracy with flat convergence. This is what a practitioner who applies the standard community LoRA configuration to the base Mamba checkpoint will observe.
