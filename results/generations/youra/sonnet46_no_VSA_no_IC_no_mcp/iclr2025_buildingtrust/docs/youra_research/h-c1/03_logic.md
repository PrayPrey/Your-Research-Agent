---
title: "Logic: h-c1 — RLHF Calibration Moderation Experiment"
hypothesis_id: h-c1
hypothesis_type: CONDITION
date: 2026-08-25
author: yoon303@ust.ac.kr
---

Applied: Paired-Condition Evaluation API Pattern
Applied: Named-Tuple Result Accumulation Pattern
Applied: Sequential Model Load/Unload for GPU Safety

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (INCREMENTAL from H-E1)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Status**: Patterns derived from H-E1 architecture and established DL evaluation codebases

H-E1 uses a flat module structure with clean function-level APIs:
- `extract_cell(model, tokenizer, dataset, task, config) -> tuple[np.ndarray, np.ndarray]` — returns (confidences, correctness) arrays
- `compute_ece(confidences, correctness, n_bins=15) -> float` — Guo 2017 standard
- `load_model(model_id, config) -> tuple[model, tokenizer]` — float16, device_map="auto"
- `unload_model(model, tokenizer) -> None` — GPU cache clear

H-C1 wraps these into `compute_delta_ece()` and adds `compare_rlhf_moderation()`. No modifications to H-E1 modules needed.

---

## External Dependencies API

Verified signatures from H-E1 codebase (actual code or established pattern):

```python
# h-e1/code/evaluation/logit_extractor.py
def extract_cell(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    dataset: Dataset,
    task: str,                        # "nli"
    config: ExperimentConfig,
    max_samples: int = 1000,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        confidences: shape [N] — max softmax over answer tokens
        correctness: shape [N] — 1.0 if predicted label == gold, else 0.0
    """

# h-e1/code/evaluation/ece.py
def compute_ece(
    confidences: np.ndarray,          # shape [N], values in [0,1]
    correctness: np.ndarray,          # shape [N], values in {0.0, 1.0}
    n_bins: int = 15,
) -> float:
    """Equal-width ECE (Guo 2017). Returns scalar in [0,1]."""

def compute_both(
    model, tokenizer, clean_dataset, adv_dataset,
    task: str, config,
) -> tuple[float, float]:
    """Returns (ece_clean, ece_adv) for a single model × cell."""

# h-e1/code/models/loader.py
def load_model(
    model_id: str,
    config: ExperimentConfig,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Loads in float16 with device_map='auto'."""

def unload_model(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
) -> None:
    """Deletes model/tokenizer, clears GPU cache."""
```

---

## Subtask A-3-1: Chat Model Logit Extraction API

### API Signature

```python
# code/comparison/delta_ece.py

from typing import NamedTuple
import numpy as np

class CellECE(NamedTuple):
    cell_id: str
    model_id: str
    ece_clean: float           # ECE on clean split
    ece_adv: float             # ECE on adversarial split
    delta_ece: float           # ece_adv - ece_clean
    n_clean: int               # samples used for clean
    n_adv: int                 # samples used for adv

def compute_delta_ece(
    model: "AutoModelForCausalLM",
    tokenizer: "AutoTokenizer",
    clean_dataset: "Dataset",            # GLUE MNLI or MultiNLI
    adv_dataset: "Dataset",             # AdvGLUE or ANLI Rk
    cell_id: str,                        # e.g. "NLI-AdvGLUE"
    model_id: str,                       # e.g. "meta-llama/Llama-2-7b-hf"
    task: str = "nli",
    config: "HC1Config" = None,
) -> CellECE:
    """
    Tensor shapes internal to extract_cell():
      logits:       [batch, seq_len, vocab_size]  (raw model output)
      answer_logits:[batch, n_answer_tokens]       (sliced at answer position)
      softmax:      [batch, n_answer_tokens]       (after F.softmax)
      confidence:   [N]                            (max softmax per example)
      correctness:  [N]                            (1.0 if argmax == gold)
    """
```

### Pseudocode

```
compute_delta_ece(model, tokenizer, clean_dataset, adv_dataset, cell_id, model_id, task, config):
    max_samples = config.subsample_clean if config else 1000

    # Clean split
    conf_clean, corr_clean = extract_cell(model, tokenizer, clean_dataset, task, config, max_samples)
    ece_clean = compute_ece(conf_clean, corr_clean, n_bins=15)
    n_clean = len(conf_clean)

    # Adversarial split
    conf_adv, corr_adv = extract_cell(model, tokenizer, adv_dataset, task, config, max_samples)
    ece_adv = compute_ece(conf_adv, corr_adv, n_bins=15)
    n_adv = len(conf_adv)

    delta_ece = ece_adv - ece_clean

    return CellECE(cell_id, model_id, ece_clean, ece_adv, delta_ece, n_clean, n_adv)
```

---

## Subtask A-3-2: Chat Model Prompt Handling

### Chat Template Difference

```python
# Llama-2-chat uses a special chat template; for MCQ NLI we bypass it
# and use the same raw prompt as base model to ensure controlled comparison.

ANSWER_TOKENS_NLI = ["entailment", "neutral", "contradiction"]

def get_answer_token_ids(tokenizer: AutoTokenizer) -> list[int]:
    """
    Map NLI answer strings to single token IDs.
    Both Llama-2-7b-hf and Llama-2-7b-chat-hf share the same tokenizer vocabulary,
    so token IDs are identical for both models.

    Returns: list[int] of length 3, one token ID per answer class
    """
    ids = []
    for ans in ANSWER_TOKENS_NLI:
        # tokenize without special tokens, take first token
        tok_ids = tokenizer.encode(" " + ans, add_special_tokens=False)
        assert len(tok_ids) >= 1, f"Answer token '{ans}' tokenized to empty"
        ids.append(tok_ids[0])
    return ids  # e.g. [13780, 20444, 27039] (Llama-2 vocab)

# Prompt template (identical for base and chat — controlled comparison):
NLI_PROMPT_TEMPLATE = (
    "Premise: {premise}\n"
    "Hypothesis: {hypothesis}\n"
    "Does the hypothesis entail, contradict, or is neutral with the premise?\n"
    "Answer:"
)
# Answer token is extracted at position [-1] of the generated logits
```

### Verification

```python
def verify_answer_tokens(tokenizer, model, sample_dataset, n_check=10) -> bool:
    """Pre-flight: verify logits at answer position are non-degenerate."""
    token_ids = get_answer_token_ids(tokenizer)
    for ex in sample_dataset.select(range(n_check)):
        prompt = NLI_PROMPT_TEMPLATE.format(**ex)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model(**inputs)
        logits_last = out.logits[0, -1, :]          # [vocab_size]
        answer_logits = logits_last[token_ids]       # [3]
        probs = torch.softmax(answer_logits, dim=-1) # [3]
        max_prob = probs.max().item()
        if max_prob > 0.999:
            return False  # degenerate — chat model not responding to MC format
    return True
```

---

## Subtask A-5-1: ΔECE Computation Full API

### Tensor Shape Annotations

```python
def compute_ece(
    confidences: np.ndarray,   # shape [N], dtype float32, range [0,1]
    correctness: np.ndarray,   # shape [N], dtype float32, values {0.0, 1.0}
    n_bins: int = 15,
) -> float:
    """
    Internal shapes:
        bin_edges:  [n_bins+1]  = linspace(0, 1, 16)
        bin_mask:   [N]         boolean mask for each bin
        bin_acc:    scalar      mean correctness in bin
        bin_conf:   scalar      mean confidence in bin
        bin_weight: scalar      fraction of samples in bin
    Returns scalar ECE in [0,1].
    """
    bin_edges = np.linspace(0, 1, n_bins + 1)    # [16]
    ece = 0.0
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i+1]
        mask = (confidences >= lo) & (confidences < hi)  # [N] bool
        if mask.sum() == 0:
            continue
        acc = correctness[mask].mean()                   # scalar
        conf = confidences[mask].mean()                  # scalar
        weight = mask.sum() / len(confidences)           # scalar
        ece += weight * abs(acc - conf)
    return float(ece)
```

---

## Subtask A-5-2: Moderation Comparison & Activation Verification

### API Signatures

```python
class ModerationResult(NamedTuple):
    cell_id: str
    delta_ece_base: float       # ΔECE for Llama-2-7b-hf
    delta_ece_chat: float       # ΔECE for Llama-2-7b-chat-hf
    ddece: float                # delta_ece_base - delta_ece_chat (positive = moderation)
    moderation_confirmed: bool  # ddece > 0

def compare_rlhf_moderation(
    base: CellECE,              # CellECE for Llama-2-7b-hf
    chat: CellECE,              # CellECE for Llama-2-7b-chat-hf
) -> ModerationResult:
    assert base.cell_id == chat.cell_id, "Cell ID mismatch"
    ddece = base.delta_ece - chat.delta_ece
    return ModerationResult(
        cell_id=base.cell_id,
        delta_ece_base=base.delta_ece,
        delta_ece_chat=chat.delta_ece,
        ddece=ddece,
        moderation_confirmed=(ddece > 0),
    )

def verify_activation(
    base_results: dict[str, CellECE],   # cell_id -> CellECE (base model)
    chat_results: dict[str, CellECE],   # cell_id -> CellECE (chat model)
) -> tuple[bool, dict[str, bool]]:
    """
    4 indicator checks from PRD FR-3.3.
    Returns (activated: bool, indicators: dict)
    activated = all(indicators.values())
    """
    # Pick NLI-AdvGLUE cell as reference
    ref_base = base_results["NLI-AdvGLUE"]
    ref_chat = chat_results["NLI-AdvGLUE"]
    indicators = {
        "base_ece_valid": not np.isnan(ref_base.ece_adv),
        "chat_ece_valid": not np.isnan(ref_chat.ece_adv),
        "models_differ": abs(ref_base.ece_adv - ref_chat.ece_adv) > 0.001,
        "moderation_direction": ref_chat.delta_ece < ref_base.delta_ece,
    }
    activated = all(indicators.values())
    return activated, indicators

def compute_moderation_rate(
    moderation_results: list[ModerationResult],
) -> float:
    """Fraction of cells where moderation_confirmed is True."""
    if not moderation_results:
        return 0.0
    return sum(r.moderation_confirmed for r in moderation_results) / len(moderation_results)
```

---

## Subtask A-8-1: Main Orchestration Loop

### Pseudocode

```python
def main(config: HC1Config = None) -> bool:
    config = config or HC1Config()
    os.makedirs(config.results_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    # Step 1: Load all datasets once
    datasets = load_hc1_datasets(
        seed=config.seed,
        subsample_clean=config.subsample_clean,
        subsample_adv=config.subsample_adv,
    )
    # datasets keys: "mnli", "advglue_mnli", "multi_nli", "anli_r1", "anli_r2", "anli_r3"

    # Step 2: Evaluate each model sequentially (GPU memory safety)
    all_cell_results: dict[str, dict[str, CellECE]] = {}
    # all_cell_results[model_id][cell_id] = CellECE

    for model_id in config.models:
        model, tokenizer = load_model(model_id, config)

        # Pre-flight: verify answer tokens non-degenerate
        assert verify_answer_tokens(tokenizer, model, datasets["advglue_mnli"])

        cell_results: dict[str, CellECE] = {}
        for cell_id, (clean_key, adv_key) in config.eval_cells.items():
            cell_ece = compute_delta_ece(
                model, tokenizer,
                datasets[clean_key], datasets[adv_key],
                cell_id=cell_id, model_id=model_id,
                task="nli", config=config,
            )
            cell_results[cell_id] = cell_ece
            print(f"  {cell_id}: ΔECE={cell_ece.delta_ece:.4f}")

        all_cell_results[model_id] = cell_results
        unload_model(model, tokenizer)  # free GPU before next model

    # Step 3: Paired comparison
    base_id = "meta-llama/Llama-2-7b-hf"
    chat_id = "meta-llama/Llama-2-7b-chat-hf"
    base_results = all_cell_results[base_id]
    chat_results = all_cell_results[chat_id]

    moderation_results = [
        compare_rlhf_moderation(base_results[cid], chat_results[cid])
        for cid in config.eval_cells
    ]

    # Step 4: Mechanism activation
    activated, indicators = verify_activation(base_results, chat_results)

    # Step 5: Gate evaluation
    moderation_rate = compute_moderation_rate(moderation_results)
    nli_ddece = next(r.ddece for r in moderation_results if r.cell_id == "NLI-AdvGLUE")
    gate_passed = (moderation_rate >= config.moderation_rate_threshold and
                   nli_ddece > config.ddece_nli_threshold)

    # Step 6: H-E1 consistency check (warn, don't fail)
    _check_he1_consistency(base_results, config)

    # Step 7: Persist results
    save_results(all_cell_results, moderation_results, moderation_rate,
                 gate_passed, indicators, config)
    write_validation_report(moderation_results, moderation_rate,
                            gate_passed, indicators, nli_ddece, config)

    # Step 8: Figures
    fig1_paired_bar(moderation_results, f"{config.figures_dir}/fig1_paired_delta_ece.png")
    fig2_reliability_grid(base_results, chat_results, f"{config.figures_dir}/fig2_reliability_diagrams.png")
    fig3_ddece_scatter(moderation_results, f"{config.figures_dir}/fig3_ddece_scatter.png")
    fig4_anli_gradient(moderation_results, f"{config.figures_dir}/fig4_anli_gradient.png")

    return gate_passed
```

---

## Subtask A-8-2: H-E1 Consistency Check & sys.path Setup

```python
import sys, os

def setup_he1_imports(he1_code_path: str = None) -> None:
    """Add H-E1 code directory to sys.path for direct imports."""
    if he1_code_path is None:
        # Resolve relative to this file's location
        this_dir = os.path.dirname(os.path.abspath(__file__))
        he1_code_path = os.path.normpath(
            os.path.join(this_dir, "../../h-e1/code")
        )
    if he1_code_path not in sys.path:
        sys.path.insert(0, he1_code_path)
    # Verify importable
    try:
        import evaluation.ece  # noqa
    except ImportError as e:
        raise RuntimeError(
            f"H-E1 code not importable from {he1_code_path}: {e}\n"
            "Check that h-e1/code/ exists with evaluation/ece.py"
        )

def _check_he1_consistency(
    base_results: dict[str, CellECE],
    config: "HC1Config",
) -> None:
    """
    Warn (never fail) if base model ECE differs from H-E1 reference values.
    Tolerance: ±0.005 (config.he1_consistency_tolerance)
    """
    nli_cell = base_results.get("NLI-AdvGLUE")
    if nli_cell is None:
        print("WARN: NLI-AdvGLUE cell missing — cannot check H-E1 consistency")
        return

    # Check clean ECE
    diff_clean = abs(nli_cell.ece_clean - config.he1_base_ece_clean_nli)
    if diff_clean > config.he1_consistency_tolerance:
        print(
            f"WARN: Base ECE_clean={nli_cell.ece_clean:.4f} differs from "
            f"H-E1 reference {config.he1_base_ece_clean_nli:.4f} "
            f"by {diff_clean:.4f} > tolerance {config.he1_consistency_tolerance}"
        )

    # Check ΔECE
    diff_delta = abs(nli_cell.delta_ece - config.he1_base_delta_ece_nli)
    if diff_delta > config.he1_consistency_tolerance:
        print(
            f"WARN: Base ΔECE={nli_cell.delta_ece:.4f} differs from "
            f"H-E1 reference {config.he1_base_delta_ece_nli:.4f} "
            f"by {diff_delta:.4f} > tolerance {config.he1_consistency_tolerance}"
        )
```

---

## Data Flow Summary

```
Datasets (load once)
    │
    ├── clean splits: "mnli" [N≤1000], "multi_nli" [N≤1000]
    └── adv splits:   "advglue_mnli" [N≤1000], "anli_r1/r2/r3" [N≤1000]
        │
        ▼ (per model, sequential)
extract_cell() → confidences[N], correctness[N]
compute_ece()  → scalar ECE
        │
        ▼
compute_delta_ece() → CellECE(cell_id, model_id, ece_clean, ece_adv, delta_ece, n_clean, n_adv)
        │
        ▼ (after both models done)
compare_rlhf_moderation() → ModerationResult(cell_id, delta_ece_base, delta_ece_chat, ddece, moderation_confirmed)
        │
        ├── compute_moderation_rate() → float  (gate metric 1)
        ├── verify_activation()       → bool   (mechanism check)
        └── gate_passed               → bool   (moderation_rate ≥ 0.60 AND ddece_NLI > 0.01)
```
