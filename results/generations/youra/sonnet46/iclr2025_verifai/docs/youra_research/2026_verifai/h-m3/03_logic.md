# Logic: h-m3 — P(True) Confidence Elicitation via Logprob Extraction

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m2 code (Read fallback — Serena project activation error)
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-m2/code/src/h_m2/stratify.py`
**Relevant Symbols**:
- `MODEL_IDS: list[str]` — `["NousResearch/Meta-Llama-3-8B", "codellama/CodeLlama-7b-hf", "deepseek-ai/deepseek-coder-6.7b-base"]`
- `MODEL_SHORT_NAMES: dict[str, str]` — maps model_id → short name
- `HARD_THRESHOLD: float = 0.0`, `EASY_THRESHOLD: float = 0.6`
- `load_hm1_pass_at_1(hm1_results_dir: Path | str) -> dict[str, dict[str, float]]`

h-m3 does NOT import h-m2 package directly. Constants are redefined in `config.py`.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/src/h_m2/stratify.py (ACTUAL CODE)

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0   # pass@1 <= this → hard
EASY_THRESHOLD: float = 0.6   # pass@1 >= this → easy

def load_hm1_pass_at_1(
    hm1_results_dir: Path | str,
) -> dict[str, dict[str, float]]:
    """Returns {hf_model_id: {task_id: float}}"""
    ...
```

**Verified from**: `h-m2/code/src/h_m2/stratify.py` (actual implementation)

---

## Applied: Standard HuggingFace CausalLM output_logits extraction (Kadavath 2022 / HF PR #28667)

---

## A-4: P(True) Extractor Core [Complexity: 14, Budget: 4 subtasks]

### API Signatures

```python
# src/h_m3/ptrue_extractor.py

def load_model_and_tokenizer(
    model_id: str,
    device: str,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load CausalLM in float16 with device_map='auto'."""
    ...

def get_true_false_token_ids(
    tokenizer: AutoTokenizer,
) -> tuple[int, int]:
    """Return (true_id, false_id) for ' True'/' False' with leading space."""
    ...

def extract_ptrue_confidence(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problem_prompt: str,
    solution_code: str,
    device: str,
    true_id: int,
    false_id: int,
    prompt_template: str,
) -> float:
    """Return c in [0,1] via output_logits=True, max_new_tokens=1."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs["input_ids"] | [1, seq_len] | Single prompt |
| out.logits[0] | [1, vocab_size] | Tuple of length 1 (max_new_tokens=1) |
| logits | [vocab_size] | Squeezed from out.logits[0][0] |
| log_probs | [vocab_size] | F.log_softmax(logits, dim=-1) |
| c | scalar | softmax([logp_true, logp_false])[0] |

### Pseudo-code

```
get_true_false_token_ids(tokenizer):
    true_id  = tokenizer.encode(" True",  add_special_tokens=False)[0]
    false_id = tokenizer.encode(" False", add_special_tokens=False)[0]
    log: f"true_id={true_id}, false_id={false_id}"
    return true_id, false_id

extract_ptrue_confidence(...):
    prompt = prompt_template.format(problem_prompt=problem_prompt, solution_code=solution_code)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=1,
            return_dict_in_generate=True,
            output_logits=True,
            do_sample=False,
        )
    logits = out.logits[0][0]            # [vocab_size]
    log_probs = F.log_softmax(logits, dim=-1)
    pair = torch.tensor([log_probs[true_id].item(), log_probs[false_id].item()])
    c = torch.softmax(pair, dim=0)[0].item()
    return c                              # float in [0,1]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | token_id_handling | get_true_false_token_ids with leading-space encoding + startup log |
| L-4-2 | generate_call | model.generate with output_logits=True, return_dict_in_generate=True, do_sample=False |
| L-4-3 | logit_indexing | out.logits[0][0] indexing edge case; assert len(out.logits)==1 |
| L-4-4 | normalization | log_softmax → pair tensor → softmax → [0].item(); verify c in [0,1] |

---

## A-5: Inference Loop + Checkpointing [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
def run_ptrue_inference_for_model(
    model_id: str,
    pairs: list[dict],
    device: str,
    checkpoint_path: Path,
    prompt_template: str,
    checkpoint_interval: int = 100,
) -> dict[str, dict]:
    """Run P(True) for all pairs of one model; returns {task_id: {tier, pass_at_1, confidence_scores, correctness_labels}}."""
    ...
```

### Pseudo-code

```
run_ptrue_inference_for_model(model_id, pairs, device, checkpoint_path, prompt_template, checkpoint_interval):
    # Resume logic
    results = {}
    if checkpoint_path.exists():
        results = json.load(checkpoint_path)
        done_keys = set(results.keys())
    else:
        done_keys = set()

    model, tokenizer = load_model_and_tokenizer(model_id, device)
    true_id, false_id = get_true_false_token_ids(tokenizer)

    for i, pair in enumerate(tqdm(pairs)):
        key = f"{pair['task_id']}__sol{pair['sol_idx']}"
        if key in done_keys:
            continue

        c = extract_ptrue_confidence(
            model, tokenizer,
            pair["problem_prompt"], pair["solution_code"],
            device, true_id, false_id, prompt_template
        )

        task_entry = results.setdefault(pair["task_id"], {
            "tier": pair["tier"],
            "pass_at_1": pair["pass_at_1"],
            "confidence_scores": [],
            "correctness_labels": [],
        })
        task_entry["confidence_scores"].append(c)
        task_entry["correctness_labels"].append(pair["correctness"])

        if (i + 1) % checkpoint_interval == 0:
            json.dump(results, checkpoint_path.open("w"))

    json.dump(results, checkpoint_path.open("w"))  # final save
    del model; torch.cuda.empty_cache()
    return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | loop_logic | pairs iteration with tqdm, key construction, per-task result accumulation |
| L-5-2 | checkpoint_resume | load existing checkpoint → skip done keys; save every checkpoint_interval + final |

---

## A-6: Mechanism Verification [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
def verify_ptrue_mechanism(
    confidence_scores_by_model: dict[str, list[float]],
    out_logits_sample: list,
) -> tuple[bool, dict]:
    """Check 4 mechanism indicators (FR-8); returns (all_pass, indicators_dict)."""
    ...
```

### Pseudo-code

```
verify_ptrue_mechanism(confidence_scores_by_model, out_logits_sample):
    indicators = {
        "logits_extracted":    out_logits_sample is not None and len(out_logits_sample) > 0,
        "vocab_size_correct":  out_logits_sample[0][0].shape[0] > 30000,
        "c_values_in_range":   all(0.0 <= c <= 1.0
                                   for scores in confidence_scores_by_model.values()
                                   for c in scores),
        "non_degenerate":      all(np.std(scores) > 0.05
                                   for scores in confidence_scores_by_model.values()),
    }
    return all(indicators.values()), indicators

# Fallback retry (FR-9) — called from main() if gate FAIL:
# Re-run run_ptrue_inference_for_model with prompt_template=PTRUE_PROMPT_FALLBACK
# Save fallback checkpoint separately (checkpoint_path.with_suffix('.fallback.json'))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | four_indicators | implement indicators dict with correct indexing for out_logits_sample |
| L-6-2 | fallback_retry | main() logic: if gate FAIL → re-run with PTRUE_PROMPT_FALLBACK, separate checkpoint |

---

## A-2: Data Loader [Complexity: 10, Budget: 2 subtasks]

### API Signatures

```python
# src/h_m3/data_loader.py

def load_tier_assignments(hm2_results_dir: Path) -> pd.DataFrame:
    """Load tier_assignments.csv; cols: [problem_id, model, tier, pass_at_1]."""
    ...

def filter_hard_easy_tiers(df: pd.DataFrame) -> pd.DataFrame:
    """Filter rows where tier in {'hard', 'easy'}."""
    ...

def load_solutions_jsonl(
    hm1_results_dir: Path,
    model_short: str,
) -> dict[str, list[dict]]:
    """Load solutions_{model_short}.jsonl; returns {task_id: [sol_dict × k]}."""
    ...

def load_evalplus_problems() -> dict[str, dict]:
    """Load HumanEval+ and MBPP+ via evalplus; returns {task_id: {prompt, ...}}."""
    ...

def build_pair_iterator(
    tier_df: pd.DataFrame,
    solutions: dict[str, dict[str, list[dict]]],
    problems: dict[str, dict],
) -> list[dict]:
    """Build flat list of pair dicts for all (model, task_id, sol_idx) combinations."""
    ...
```

### JSONL Schema (solutions_{model_short}.jsonl)

Each line is a JSON object:
```json
{
  "task_id": "HumanEval/0",
  "model": "llama3_8b",
  "solution": "def f(x):\n    ...",
  "correctness": 0,
  "pass_at_1": 0.4
}
```

### Pseudo-code

```
build_pair_iterator(tier_df, solutions, problems):
    pairs = []
    for row in tier_df.itertuples():
        model_short = MODEL_SHORT_NAMES[row.model]
        task_sols = solutions[model_short].get(row.problem_id, [])
        problem_prompt = problems[row.problem_id]["prompt"]
        for sol_idx, sol_dict in enumerate(task_sols):
            pairs.append({
                "model": row.model,
                "model_short": model_short,
                "task_id": row.problem_id,
                "sol_idx": sol_idx,
                "tier": row.tier,
                "pass_at_1": row.pass_at_1,
                "solution_code": sol_dict["solution"],
                "correctness": sol_dict["correctness"],
                "problem_prompt": problem_prompt,
            })
    return pairs
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | build_pair_iterator | nested iteration: tier_df rows → solutions list → flat pair dicts |
| L-2-2 | load_solutions_jsonl | JSONL line-by-line read; group by task_id; schema: task_id, solution, correctness, pass_at_1 |
