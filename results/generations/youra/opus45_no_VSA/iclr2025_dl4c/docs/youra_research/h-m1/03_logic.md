# Logic: H-M1 (M-2 Refinement Trace Extraction)

**Applied**: MINE (Donsker-Varadhan) pattern — reused from architecture spec. Self-refine loop pattern reused from H-E1 `refine.py` (verified below).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: H-E1 code EXISTS on disk (contrary to architecture doc's earlier "not found" note — code has since been implemented). API signatures verified from actual implementation.
**Analyzed Path**: `docs/youra_research/h-e1/code/{refine.py, model.py, data.py, config.py}`
**Relevant Symbols**: `execute_and_get_feedback`, `single_shot`, `self_refine` (refine.py); `load_base_model` (model.py); `load_humaneval_plus` (data.py); `Config` (config.py)

### Spec-vs-code mismatches found (CRITICAL — use actual code signatures)

| Item | 03_architecture.md assumed | Actual H-E1 code |
|------|---------------------------|-------------------|
| `execute_and_get_feedback` return | `tuple[bool, str]` | `tuple[float, str]` — `(pass_rate, error_msg)`, not `(passed, msg)` |
| Model loader | `load_h_e1_models` returning trained CE/RL models by path | H-E1 only exposes `load_base_model(cfg) -> (model, tokenizer)`; no `load_ce_model`/`load_rl_model`. Trained weights presumably saved under `cfg.checkpoint_dir` (LoRA adapters, per `wrap_lora` in model.py) — **H-M1 must load base model then apply saved LoRA adapter weights from checkpoint_dir/ce and checkpoint_dir/rl (verify adapter save path in H-E1 train.py before running)** |
| Problem loader | `load_problems()` | `load_humaneval_plus(cfg: Config) -> dict[str, Any]` (data.py) |
| Refine config | separate `MINEConfig.refine_k` | H-E1's `Config.refine_k` (default 3) — reuse same field name |
| Generation | not specified | `single_shot` is greedy (`do_sample=False`), ignores `cfg.temperature` |

## M-2: Refinement Trace Extraction [Complexity: 12, Budget: 2 subtasks]

**Applied**: Self-refine loop reused verbatim from H-E1 `refine.py::self_refine`; H-M1 wraps it to also capture per-iteration (feedback, edit, edit_length) instead of only final code.

### API Signatures

```python
# h-m1/code/traces.py
from h_e1.code.config import Config  # reuse H-E1's Config, not a new MINEConfig field set
from h_e1.code.refine import single_shot, execute_and_get_feedback
from h_e1.code.data import load_humaneval_plus
from h_e1.code.model import load_base_model
import difflib

def load_lora_model(base_model, tokenizer, adapter_path: str):
    """Load base model + PEFT LoRA adapter from checkpoint_dir/{ce,rl}."""
    ...  # PeftModel.from_pretrained(base_model, adapter_path)

def compute_code_diff(prev_code: str, new_code: str) -> str:
    """Unified diff string between two code versions."""
    return "\n".join(difflib.unified_diff(
        prev_code.splitlines(), new_code.splitlines(), lineterm=""
    ))

def extract_refinement_pairs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    problems: dict,          # from load_humaneval_plus()
    cfg: Config,
    seed: int,
) -> list[dict]:
    """K=cfg.refine_k self-refine loop per problem; extract (feedback, edit) pairs.
    Returns list of dicts: {problem_id, iteration, seed, feedback, edit, edit_length}."""
```

### Tensor / Data Shapes

| Variable | Type/Shape | Note |
|----------|-----------|------|
| `feedback` | `str` | `error_msg` from `execute_and_get_feedback`, "" if pass_rate==1.0 |
| `edit` | `str` | unified diff string, output of `compute_code_diff` |
| `edit_length` | `int` | `len(edit.splitlines())` or `len(edit)` chars — pick chars for finer granularity |
| per-condition sample count | 164 problems × 3 seeds × ≤3 iterations | early-exit on pass_rate==1.0 reduces actual count below max |

### Pseudo-code: extract_refinement_pairs

```
for problem_id, problem in problems.items():
    prompt = problem["prompt"]; tests = problem["test_cases"]  # verify key names in load_humaneval_plus output
    code = single_shot(model, tokenizer, prompt, cfg)
    for i in range(cfg.refine_k):
        pass_rate, err_msg = execute_and_get_feedback(code, tests)
        if pass_rate == 1.0:
            break
        refine_prompt = build_refine_prompt(prompt, code, err_msg)  # mirror self_refine's f-string
        new_code = single_shot(model, tokenizer, refine_prompt, cfg)
        edit = compute_code_diff(code, new_code)
        pairs.append({
            "problem_id": problem_id, "iteration": i, "seed": seed,
            "feedback": err_msg, "edit": edit, "edit_length": len(edit),
        })
        code = new_code
return pairs
```

**Note**: `feedback` is captured BEFORE the refine step that produces `edit` (feedback caused this edit) — pair feedback[i] with edit[i] where edit[i] = diff(code_before_step_i, code_after_step_i).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M-2-1 | Trace loop + diff | `extract_refinement_pairs` + `compute_code_diff`, wraps H-E1's `single_shot`/`execute_and_get_feedback` (reused, not reimplemented) |
| L-M-2-2 | Multi-seed orchestration | Loop over `cfg.seeds` × both models (CE/RL via `load_lora_model`), aggregate into per-condition list[dict] for embed.py |

## External Dependencies (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/refine.py (ACTUAL CODE)
def execute_and_get_feedback(code: str, tests: list[str]) -> tuple[float, str]:
    """Runs code against tests via subprocess. Returns (pass_rate, error_msg)."""

def single_shot(model, tokenizer, prompt: str, cfg: Config) -> str:
    """Greedy generation (do_sample=False), max_new_tokens=cfg.max_new_tokens."""

def self_refine(model, tokenizer, prompt: str, tests: list[str], cfg: Config) -> str:
    """Reference loop — H-M1 reimplements with pair extraction, same refine_prompt format."""

# From: docs/youra_research/h-e1/code/model.py
def load_base_model(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Loads Salesforce/codet5p-220m + tokenizer, fp16."""

# From: docs/youra_research/h-e1/code/data.py
def load_humaneval_plus(cfg: Config) -> dict[str, Any]:
    """Returns 164 HumanEval+ problems, cached under cfg.cache_dir."""

# From: docs/youra_research/h-e1/code/config.py
@dataclass
class Config:
    model_id: str = "Salesforce/codet5p-220m"
    refine_k: int = 3
    max_new_tokens: int = 512
    seed: int = 42
    checkpoint_dir: Path  # property -> base_dir/checkpoints — verify CE/RL adapter subfolder names before load
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation). **Action item for Phase 4 coder**: confirm exact adapter save path used in H-E1's `train.py` (not read in this pass — out of M-2 budget) before implementing `load_lora_model`.
