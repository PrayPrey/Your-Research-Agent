# Logic: h-c1

**Applied**: HF Trainer + PEFT LoRA sweep pattern (reused from h-e1)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena has no active project for this workspace (`No active project` error on `get_symbols_overview`) — fell back to direct file reads on `h-e1/code/*.py` (matches architecture.md's documented fallback). All API signatures below verified from actual implementation, not from `h-e1/03_logic.md` specs.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `config.py` (MODELS, MODEL_HF_IDS, RANKS, SEEDS, TrainConfig, AnalysisConfig), `model.py` (load_base_model, load_tokenizer, apply_lora), `data.py` (tokenize_squad — span-tokenization pattern reused), `train.py` (set_seed, evaluate_squad_f1 pattern), `analyze.py` (compute_r_opt, fit_scaling_law, plot_scaling, check_pass_fail), `main.py` (run_sweep pattern)

---

## External Dependencies (Base Hypothesis)

Copied unmodified into `h-c1/code/` (h-e1 has no package structure, flat scripts — per architecture.md decision):

```python
# config.py (copied from h-e1/code/config.py, verbatim)
MODELS: dict[str, float]        # {"pythia-1b": 1.0e9, ...}
MODEL_HF_IDS: dict[str, str]
RANKS: list[int] = [4, 8, 16, 32, 64, 128]
SEEDS: list[int] = [42, 1337, 2024]
TARGET_MODULES: list[str] = ["query_key_value"]

@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 8
    grad_accum: int = 4
    warmup_steps: int = 100
    max_length: int = 384          # h-c1 overrides to 512 at call site
    lr_scheduler: str = "linear"
    grad_clip: float = 1.0
    gradient_checkpointing: bool = True

@dataclass
class AnalysisConfig:
    n_bootstrap: int = 1000
    alpha_ci: float = 0.95

# model.py (copied verbatim)
def load_base_model(model_id: str, device_map: str = "auto") -> PreTrainedModel: ...
def load_tokenizer(model_id: str) -> AutoTokenizer: ...
def apply_lora(model: PreTrainedModel, rank: int, alpha: int | None = None,
                dropout: float = 0.05, target_modules: list[str] | None = None) -> PeftModel: ...

# train.py
def set_seed(seed: int) -> None: ...

# analyze.py (copied verbatim, dataset-agnostic — operates on CSV columns model/rank/seed/f1_score)
def compute_r_opt(sweep_csv: str, output_csv: str | None = None) -> pd.DataFrame: ...
def fit_scaling_law(optimal_ranks: pd.DataFrame, n_bootstrap: int = 1000,
                     output_json: str | None = None) -> dict: ...
def plot_scaling(fit_result: dict, optimal_ranks: pd.DataFrame, output_png: str | None = None) -> None: ...
def check_pass_fail(fit_result: dict) -> dict: ...
```

**Verified from**: `docs/youra_research/h-e1/code/{config,model,train,analyze}.py` (actual implementation).

**Note**: `apply_lora` uses `task_type=TaskType.QUESTION_ANS` and target module `"query_key_value"` — must match h-c1's model too (Pythia QA head).

---

## L-C1-1: HotpotQA Data Pipeline [Complexity: 8, Budget: shared]

**Applied**: HF `datasets.load_dataset` + SQuAD-style offset-mapping tokenization (adapted from `h-e1/data.py::tokenize_squad`)

### API Signatures

```python
# data_hotpot.py
def load_hotpot_qa(cache_dir: str | None = None) -> DatasetDict:
    """load_dataset('hotpotqa/hotpot_qa', 'distractor', cache_dir=cache_dir)"""
    ...

def _concat_context(example: dict) -> str:
    """Concat all context[i] sentences per doc into single string, in order.
    HotpotQA context field: {'title': list[str], 'sentences': list[list[str]]}"""
    ...

def tokenize_hotpot(
    dataset: DatasetDict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 512,
) -> DatasetDict:
    """Concat supporting+distractor docs -> single context string, then
    reuse h-e1 offset-mapping span-tokenization logic verbatim."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 512] | question + concatenated multi-doc context, truncated |
| start_positions, end_positions | [B] | answer span in concatenated context (0 if truncated out) |

### Pseudo-code

```
1. For each example: concat all sentences of all context docs (title-ordered) into context_str
2. answer_start_char = context_str.find(example['answer'])  # locate span in concatenated text
   (HotpotQA has no answer_start offset field like SQuAD; must be computed via string search)
3. Build synthetic {"answer_start": [answer_start_char], "text": [answer]} dict
   matching SQuAD's answers schema -> reuse tokenize_squad's offset-mapping loop unmodified
   (same truncation="only_second", stride=128, return_offsets_mapping=True)
4. If answer not found in context_str (post-truncation or "yes"/"no" answers): start=end=0
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-C1-1 | data_hotpot.py | load_hotpot_qa + tokenize_hotpot (concat docs, string-search span, reuse SQuAD offset logic) |

---

## L-C1-2: HotpotQA Train/Eval Loop [Complexity: 10, Budget: shared]

**Applied**: HF Trainer manual loop (adapted from `h-e1/train.py::train_one_run`) + sentence-level F1 for supporting facts

### API Signatures

```python
# train_hotpot.py
def train_one_run(
    model_id: str,
    rank: int,
    seed: int,
    cfg: TrainConfig,
    output_dir: str = "checkpoints",
    data_cache_dir: str | None = None,
) -> dict:
    """Same loop as h-e1/train.py::train_one_run (epochs/optimizer/scheduler identical).
    Returns {'answer_f1': float, 'sp_f1': float}."""
    ...

def evaluate_hotpot(
    model, val_loader: DataLoader, tokenizer, val_dataset, device,
) -> dict:
    """Span decode identical to h-e1 evaluate_squad_f1. Adds sentence-level
    supporting-facts F1 via sentence-boundary offset matching.
    Returns {'answer_f1': float, 'sp_f1': float}."""
    ...

def compute_sp_f1(predicted_sentences: list[tuple[str, int]], gold_supporting_facts: list[tuple[str, int]]) -> float:
    """Set-based F1 over (title, sent_idx) tuples."""
    ...
```

### Tensor Shapes (only non-obvious)

| Variable | Shape | Note |
|----------|-------|------|
| start_logits, end_logits | [B, 512] | model output over concatenated context |

### Pseudo-code

```
compute_sp_f1(predicted, gold):
    pred_set = set(predicted)   # {(title, sent_idx), ...}
    gold_set = set(gold)
    tp = len(pred_set & gold_set)
    precision = tp / len(pred_set) if pred_set else 0
    recall = tp / len(gold_set) if gold_set else 0
    return 2*precision*recall/(precision+recall) if (precision+recall) else 0

evaluate_hotpot:
    1. Decode answer span same as h-e1 evaluate_squad_f1 -> predictions/references
    2. answer_f1 = evaluate.load('squad')  # HotpotQA uses official squad-style F1, not squad_v2 (no no-answer)
    3. For supporting facts: since model only predicts answer span (no dedicated SP head),
       heuristic: mark sentence containing predicted span as "predicted supporting" (top-1 sentence).
       predicted_sentences = [(title_of_span_sentence, sent_idx_of_span_sentence)] per example
    4. gold_supporting_facts = example['supporting_facts']  # list[(title, sent_idx)]
    5. sp_f1 = mean(compute_sp_f1(pred, gold) for pred, gold in zip(...))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-C1-2 | train_hotpot.py | train_one_run + evaluate_hotpot + compute_sp_f1 (answer F1 via `evaluate.load('squad')`, SP-F1 via top-1-sentence heuristic set overlap) |

---

## Remaining Tasks (C-1, C-4, C-5, C-6, C-7): No new logic needed

- **C-1** (verify+copy h-e1 artifacts): file ops only, no API design needed — `os.path.exists` check + `shutil.copy`.
- **C-4** (`main.py::run_sweep`): identical structure to `h-e1/code/main.py::run_sweep`, just swaps `train_one_run` import to `train_hotpot` and CSV header to `["model","rank","seed","f1_score","sp_f1","timestamp"]`.
- **C-5** (r_opt + scaling fit): calls `compute_r_opt`/`fit_scaling_law` from copied `analyze.py` unmodified, pointed at `h-c1_rank_sweep.csv`.
- **C-6** (`compare.py::load_scaling_fit`, `compare_alphas`): trivial dict I/O + arithmetic, signatures already fully specified in `03_architecture.md`.
- **C-7** (`compare.py::plot_dual_scaling`): matplotlib calls mirroring `h-e1/analyze.py::plot_scaling` pattern (two scatter+fit-line series instead of one), signature already in `03_architecture.md`.

Budget used: 2/2 subtasks (L-C1-1 data pipeline, L-C1-2 train/eval loop) — the only tasks requiring non-trivial pseudo-code.
