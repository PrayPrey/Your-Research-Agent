---
name: 'training_sufficiency'
description: 'LLM-based verification that experiment ran at sufficient scale for PoC conclusions'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - verify_training_sufficiency

# Called By
called_by:
  - 'phase4-coding/steps/step-05c-post-validation.md'
---

# Training Sufficiency Helper

> LLM-based verification that the experiment ran at sufficient scale for PoC-level conclusions.
> Complements mock detection: mock detection asks "is this fake?", sufficiency asks "is this real but inadequate?"
>
> **Examples of what this catches (that mock detection does NOT):**
> - Real CIFAR-10 loaded but `dataset[:50]` used (only 50 samples)
> - Real GPT-2 model but only 2 epochs of fine-tuning
> - Real training loop but completes in 30 seconds due to tiny subset

---

## Main Function

### verify_training_sufficiency

```python
def verify_training_sufficiency(
    results: dict,
    experiment_log_content: str,
    experiment_brief_content: str
) -> dict:
    """
    LLM reads experiment results, log, and 02c brief to determine
    if the experiment ran at sufficient scale for PoC conclusions.

    Args:
        results: Collected experiment results dict (from Section 2)
                 Must contain results["training"]["epochs_completed"],
                 results["training"]["duration_seconds"]
        experiment_log_content: Content of experiment.log (already read)
        experiment_brief_content: Content of 02c_experiment_brief.md (already read)

    Returns:
        Dictionary containing:
            - sufficient: bool - Whether training scale is adequate
            - issues: list - List of specific insufficiency issues
            - epochs_completed: int - Actual epochs from results
            - epochs_expected: int|None - Expected epochs from 02c
            - dataset_full: bool - Whether full dataset was used
            - duration_seconds: float - Actual training duration
            - is_inference_only: bool - Whether experiment is inference-only (exempt)
            - confidence: float - LLM confidence (0.0-1.0)
            - reasoning: str - LLM explanation

    Usage:
        sufficiency = verify_training_sufficiency(
            results=results,
            experiment_log_content=log_content,
            experiment_brief_content=brief_content
        )
        if not sufficiency["sufficient"]:
            # Route to Step 2 with fix task
    """
    training_data = results.get("training", {})
    epochs_completed = training_data.get("epochs_completed", 0)
    duration_seconds = training_data.get("duration_seconds", 0)

    # ── LLM Judgment Prompt ──
    # The LLM reads the provided context and answers these questions:
    #
    # 1. INFERENCE-ONLY CHECK (evaluate first):
    # - Read 02c Training Protocol section
    # - If "no training required", "inference only", "pretrained evaluation",
    # or similar → mark is_inference_only = True
    # - If is_inference_only: epoch and duration checks are WAIVED
    # (only dataset usage check applies)
    #
    # 2. EPOCH CHECK (skip if inference-only):
    # - Read 02c → Training Protocol → Epochs value
    # - Compare against epochs_completed from results
    # - INSUFFICIENT if: epochs_completed < 5 AND epochs_completed < 02c_specified
    # - Exception: If 02c specifies < 5 epochs with justification, accept it
    #
    # 3. DATASET USAGE CHECK (always applies):
    # - Read experiment.log for data loading messages
    # - Look for subsetting indicators in log:
    # * "using N samples" where N is suspiciously small
    # * "subset", "sample()", "--num_samples", "--max_samples"
    # * "head()", "iloc[:N]", "[:N]" patterns in log output
    # * "random_split" with tiny fraction
    # - Compare logged dataset size against 02c expected dataset info
    # - INSUFFICIENT if: clear evidence of dataset subsetting
    #
    # 4. DURATION CHECK (skip if inference-only):
    # - INSUFFICIENT if: duration < 300 seconds (5 minutes)
    # - Exception: Very small models/datasets where fast training is expected
    # - LLM should use judgment based on 02c model/dataset scale
    #
    # Judgment format:
    # **Verdict:** SUFFICIENT or INSUFFICIENT
    # **Is Inference Only:** YES or NO
    # **Confidence:** (0.0 - 1.0)
    # **Issues:** (list of specific issues or "None")
    # - epochs: {completed} vs {expected} (minimum 5)
    # - dataset: full | subset ({details})
    # - duration: {seconds}s vs minimum 300s
    # **Reasoning:** (explanation)

    sufficiency_result = {
        "sufficient": True, # LLM sets this
        "issues": [], # List of specific insufficiency issues
        "epochs_completed": epochs_completed,
        "epochs_expected": None, # Extracted from 02c by LLM
        "dataset_full": True, # LLM judges from log
        "duration_seconds": duration_seconds,
        "is_inference_only": False, # LLM determines from 02c
        "confidence": 0.0,
        "reasoning": ""
    }

    return sufficiency_result
```

---

## Insufficiency Patterns (LLM Guidance)

The LLM should flag as INSUFFICIENT when:

1. **Too Few Epochs:**
   - 02c specifies 100 epochs, experiment ran 2
   - Training-based experiment with < 5 epochs completed
   - Log shows "epoch 1/1" or "epoch 2/2" for a training experiment

2. **Dataset Subsetting:**
   - Log shows "Loading 100 samples" when 02c specifies CIFAR-10 (50,000)
   - Code used `dataset[:100]` or `random_split(dataset, [100, len-100])`
   - `--num_samples 50` or `--max_samples 100` in command

3. **Suspiciously Short Duration:**
   - Training experiment completed in 30 seconds
   - Full CIFAR-10 + ResNet should take > 5 minutes even on GPU
   - Duration doesn't match model/dataset scale from 02c

The LLM should NOT flag as INSUFFICIENT when:

1. **Inference-Only Experiments:**
   - 02c says "No training required (using pretrained model)"
   - Experiment evaluates pretrained model on test set
   - Short duration is expected for inference

2. **Legitimately Small Experiments:**
   - 02c specifies small dataset by design (e.g., TruthfulQA with ~800 samples)
   - 02c specifies few epochs with justification
   - Small model that genuinely trains fast
