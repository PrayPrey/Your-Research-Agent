# Configuration: H-M4 (Probe vs Output-Level Baselines)

Applied: Standard PyTorch/HuggingFace generate() defaults (no direct KB pattern match for uncertainty-baseline configs)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: config classes verified from base code
**Config Files Found**: `h-m3/code/config.py` (`HM3Config` dataclass, frozen)
**Pattern Used**: dataclass (frozen)

H-M3 does not persist a probe checkpoint — H-M4 retrains the identical probe in-process (same seed=42, C=1e-3, StandardScaler) rather than loading from disk.

---

## B-1: Reuse H-M3 Probe [Complexity: 8, Budget: 8]

**Applied**: Retrain-in-process pattern (no checkpoint persistence in base hypothesis)

### Configuration (uses shared `HM4Config` below)

Fields used: `seed`, `probe_c`, `probe_max_iter`, `probe_solver`, `probe_class_weight`, `h_m1_cache_folder`, `h_m3_code_path`, `n_train`, `n_val`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | sys.path setup | Insert `h_m3_code_path` for probe/data imports |
| C-1-2 | Load hidden states | `load_hidden_states(h_m1_cache_folder)` train+val |
| C-1-3 | Retrain probe | `LinearCorrectnessProbe` fit with scaled train features |
| C-1-4 | Score val set | Return `(probe_val_scores, y_val)` |

---

## B-2: Model Loading [Complexity: 5, Budget: 5]

**Applied**: Standard `from_pretrained` with fp16 + device_map="auto"

### Configuration
Fields used: `model_id`, `torch_dtype` (fixed `"float16"`).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Load tokenizer | `AutoTokenizer.from_pretrained(model_id)` |
| C-2-2 | Load model | `AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=float16, device_map="auto")` |
| C-2-3 | Set pad token | `tokenizer.pad_token = tokenizer.eos_token` if unset |
| C-2-4 | Eval mode | `model.eval()` |

---

## B-3: Generation Loop [Complexity: 10, Budget: 10]

**Applied**: `output_scores=True, return_dict_in_generate=True`, greedy decoding

### Configuration
Fields used: `max_new_tokens`, `do_sample=False` (fixed), `n_val`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | Prompt formatting | Apply Llama-3-Instruct chat template per question |
| C-3-2 | Batched/looped generate | `model.generate(**inputs, max_new_tokens=50, do_sample=False, output_scores=True, return_dict_in_generate=True)` |
| C-3-3 | Extract scores/ids | Stack `outputs.scores` -> `[gen_len, vocab]`, slice generated token ids |
| C-3-4 | Collect per-example dict | `{"id", "text", "scores", "generated_ids"}` |

---

## B-4: Token Entropy Computation [Complexity: 6, Budget: 6]

**Applied**: `H_t = -Σ p log p` per token, mean over sequence, negated for confidence

### Configuration
No new fields (pure function on logits tensor).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | Softmax/log_softmax | `F.softmax`, `F.log_softmax` on `[gen_len, vocab]` |
| C-4-2 | Per-token entropy | `-(probs * log_probs).sum(-1)` |
| C-4-3 | Mean + negate | `-token_entropy.mean()` (higher = more confident) |
| C-4-4 | Batch aggregation | Collect into `entropy_scores: np.ndarray` |

---

## B-5: Sequence NLL Computation [Complexity: 6, Budget: 6]

**Applied**: Gather log-probs of generated tokens, average, negate

### Configuration
No new fields (pure function on logits + token_ids).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | log_softmax | `F.log_softmax(scores, dim=-1)` |
| C-5-2 | Gather token log-probs | `.gather(1, token_ids.unsqueeze(1))` |
| C-5-3 | Mean + negate | `avg_nll = -log_probs.mean()`; confidence = `-avg_nll` |
| C-5-4 | Batch aggregation | Collect into `nll_scores: np.ndarray` |

---

## B-6: Correctness Labeling [Complexity: 6, Budget: 6]

**Applied**: Exact-match scoring against gold answers (recomputed fresh, not reused from H-M1/H-M3 cache)

### Configuration
Fields used: `exact_match_normalize=True` (lowercase + strip punctuation, fixed).

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | Normalize text | lowercase, strip punctuation/whitespace |
| C-6-2 | Compare vs gold answers | any-match across gold answer aliases |
| C-6-3 | Binary label | 1 if match else 0 |
| C-6-4 | Consistency check | Ensure label array aligns index-wise with entropy/NLL/probe scores |

---

## B-7: AUROC + Delta Computation [Complexity: 5, Budget: 5]

**Applied**: `sklearn.metrics.roc_auc_score`, gate check against `delta_gate` threshold

### Configuration
Fields used: `delta_gate`, `probe_auroc_min`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | Per-method AUROC | `roc_auc_score(labels, scores)` x3 |
| C-7-2 | Deltas | `probe_auroc - entropy_auroc`, `probe_auroc - nll_auroc` |
| C-7-3 | Gate check | both deltas `>= delta_gate` (0.05) |
| C-7-4 | Probe sanity check | `probe_auroc >= probe_auroc_min` (0.88) |

---

## B-8: Visualization Suite [Complexity: 7, Budget: 7]

**Applied**: matplotlib bar/ROC/hist/scatter, standard sklearn `roc_curve`

### Configuration
Fields used: `figures_dir`, `gate_comparison_fig`, `roc_curve_fig`, `dist_fig`, `scatter_fig`, `delta_gate`.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Gate bar chart | AUROC bars w/ `delta_gate` threshold line -> `gate_comparison_fig` |
| C-8-2 | ROC overlay | 3-method ROC curves -> `roc_curve_fig` |
| C-8-3 | Confidence distributions | probe vs entropy histograms by label -> `dist_fig` |
| C-8-4 | Score scatter | probe vs entropy, colored by label -> `scatter_fig` |

---

## B-9: End-to-End Orchestration [Complexity: 6, Budget: 6]

**Applied**: Single `run.py::main()` entrypoint, writes `results.json` + figures

### Configuration
Fields used: `results_json`, all above.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | Wire pipeline | probe scores -> generation -> baselines -> labels -> eval -> viz |
| C-9-2 | Save results.json | AUROCs, deltas, gate pass/fail |
| C-9-3 | Save figures | write all 4 figures to `figures_dir` |
| C-9-4 | Return summary dict | for logging/CLI |

---

## Shared Config (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class HM4Config:
    seed: int = 42
    model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"

    # H-M1 cache / H-M3 probe reuse (verified from h-m3/code/config.py)
    h_m1_cache_folder: str = "../h-m1/code/cache"
    h_m3_code_path: str = "../h-m3/code"
    n_train: int = 9500
    n_val: int = 1700

    # Probe params (identical to H-M3, retrained in-process)
    probe_c: float = 1e-3
    probe_max_iter: int = 2000
    probe_solver: str = "lbfgs"
    probe_class_weight: str = "balanced"

    # Generation
    max_new_tokens: int = 50
    do_sample: bool = False

    # Gates
    delta_gate: float = 0.05
    probe_auroc_min: float = 0.88

    figures_dir: str = "figures"
    gate_comparison_fig: str = "figures/gate_comparison.png"
    roc_curve_fig: str = "figures/roc_curve.png"
    dist_fig: str = "figures/confidence_distributions.png"
    scatter_fig: str = "figures/score_scatter.png"
    results_json: str = "results.json"
```

---

## Inherited Configuration (Base Hypothesis: H-M3)

### Config Class (From Actual Code)

```python
# From: h-m3/code/config.py (ACTUAL CODE, frozen dataclass)
@dataclass(frozen=True)
class HM3Config:
    seed: int = 42
    d_model: int = 4096
    n_train: int = 9500
    n_val: int = 1700
    layer: str = "l19"
    h_m1_cache_folder: str = "../h-m1/code/cache"

    probe_C: float = 1e-3            # note: field name is `probe_C` (capital C) in H-M3
    probe_max_iter: int = 2000
    probe_solver: str = "lbfgs"
    probe_class_weight: str = "balanced"
```

**Inherited/matched fields**: `seed`, `n_train`, `n_val`, `h_m1_cache_folder`, `probe_C -> probe_c`, `probe_max_iter`, `probe_solver`, `probe_class_weight`.

**Note**: H-M3 field is `probe_C` (capital C); H-M4's `HM4Config` uses `probe_c` for consistency with lowercase snake_case elsewhere — Phase 4 Coder must pass value `1e-3` to whichever name is used when calling into `h-m3/code/probe.py` and `data.py` (those modules take positional/keyword args, not the config object directly).

**Verified from**: `docs/youra_research/h-m3/code/config.py` (actual implementation).
