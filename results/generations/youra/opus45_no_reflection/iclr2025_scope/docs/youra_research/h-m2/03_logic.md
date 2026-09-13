# Logic: H-M2 (Token-Level vs Matrix-Level Distillation Drift)

**Hypothesis:** Token-level representations remain stable across lengths while matrix-level degrades

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code — new API design; no base hypothesis code artifacts found for H-M1
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

Applied: EmbedDistillLoss pattern (L2/cosine distance + optional linear projection for dim mismatch) — carried from architecture doc; KB search returned no closer match (generic diffusers/distributed hits, not relevant), so standard PyTorch hidden-state comparison pattern used.

---

## B-3: Student Model Loading (MOHAWK + CAB) [Complexity: 10, Budget: 4 subtasks]

**Applied**: Standard PyTorch `from_pretrained` + custom exception fallback

### API Signatures

```python
class CABUnavailableError(Exception):
    """Raised when CAB checkpoint cannot be loaded."""

def load_student(config: AnalysisConfig, variant: str) -> nn.Module:
    """Load phi-mamba student. variant: 'mohawk' | 'cab'. Raises CABUnavailableError for cab on failure."""
    ...

def get_student_dim(model: nn.Module) -> int:
    """Return hidden dim from model.config."""
    ...

def _load_mohawk(config: AnalysisConfig) -> nn.Module: ...
def _load_cab(config: AnalysisConfig) -> nn.Module: ...
```

### Pseudo-code

```
load_student(config, variant):
    if variant == "mohawk":
        return _load_mohawk(config)  # AutoModelForCausalLM.from_pretrained(mohawk_name, fp16, device_map="auto")
    if variant == "cab":
        try:
            return _load_cab(config)  # AutoModelForCausalLM.from_pretrained(cab_name, fp16, device_map="auto")
        except (OSError, EnvironmentError) as e:
            raise CABUnavailableError(str(e)) from e
    raise ValueError(f"unknown variant {variant}")
```

Caller (`run_full_analysis`) catches `CABUnavailableError`, logs fallback note, skips cab condition (per NFR-3 graceful fallback — no custom training implemented in PoC).

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `load_student` + `_load_mohawk`/`_load_cab` | fp16 load, device_map="auto", variant dispatch |
| L-3-2 | `get_student_dim` + `CABUnavailableError` fallback wiring | expose hidden dim, exception propagation for caller-level skip |

---

## B-7: Analysis Pipeline Orchestration [Complexity: 13, Budget: 4 subtasks]

**Applied**: Standard PyTorch batched inference loop, no_grad + aggregation

### API Signatures

```python
def extract_hidden_states(
    model: nn.Module, input_ids: Tensor, layers: List[int]
) -> Dict[int, Tensor]:
    """Forward with output_hidden_states=True. Returns {layer_idx: [B, N, D]}."""
    ...

def compute_drift_per_layer(
    teacher_hidden: Dict[int, Tensor],
    student_hidden: Dict[int, Tensor],
    projection: Optional[nn.Linear],
) -> Dict[int, dict]:
    """Per layer L2 + cosine drift. Returns {layer_idx: {"l2": float, "cosine": float}}."""
    ...

def run_variant(
    config: AnalysisConfig,
    teacher: nn.Module,
    tokenizer,
    student: nn.Module,
    variant: str,
    docs: List[str],
) -> Dict[int, dict]:
    """Loop target_lengths -> batches -> extract+drift. Returns {length: {"l2", "cosine", "per_layer"}}."""
    ...

def run_full_analysis(config: AnalysisConfig) -> dict:
    """Load teacher+students, run both variants, compute slope/gate/variance. Returns {"mohawk", "cab", "gate"}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, N] | B=batch_size (8), N=length (512/1024/1536/2048) |
| teacher_hidden[l] | [B, N, 2048] | per middle layer (8,12,16) |
| student_hidden[l] | [B, N, D_s] | D_s = student hidden dim, pre-projection |
| projected student_hidden[l] | [B, N, 2048] | after `nn.Linear(D_s, 2048)` if D_s != 2048 |
| l2_drift per layer | scalar float | `norm(h_t - h_s, p=2, dim=-1)` -> [B, N] -> `.mean()` |

### Pseudo-code

```
run_variant(config, teacher, tokenizer, student, variant, docs):
    student_dim = get_student_dim(student)
    projection = get_projection(student_dim, config.teacher_dim, device)
    results = {}
    for length in config.target_lengths:
        batches = build_batches(docs, tokenizer, length, config.batch_size)
        l2_acc, cos_acc, per_layer_acc = [], [], defaultdict(list)
        for batch in batches:
            with torch.no_grad():
                t_hidden = extract_hidden_states(teacher, batch["input_ids"], config.middle_layers)
                s_hidden = extract_hidden_states(student, batch["input_ids"], config.middle_layers)
                layer_drift = compute_drift_per_layer(t_hidden, s_hidden, projection)
            for layer, d in layer_drift.items():
                per_layer_acc[layer].append(d)
            l2_acc.append(mean(d["l2"] for d in layer_drift.values()))
            cos_acc.append(mean(d["cosine"] for d in layer_drift.values()))
        results[length] = {
            "l2": mean(l2_acc), "cosine": mean(cos_acc),
            "per_layer": {l: {"l2": mean(x["l2"] for x in v), "cosine": mean(x["cosine"] for x in v)}
                          for l, v in per_layer_acc.items()},
        }
    return results

run_full_analysis(config):
    teacher, tokenizer = load_teacher(config)
    docs = get_long_documents(config, tokenizer)
    out = {}
    for variant in ["mohawk", "cab"]:
        try:
            student = load_student(config, variant)
        except CABUnavailableError:
            continue  # skip cab, note fallback
        out[variant] = run_variant(config, teacher, tokenizer, student, variant, docs)
    lengths = config.target_lengths
    mohawk_slope = compute_slope(lengths, [out["mohawk"][l]["l2"] for l in lengths])
    cab_slope = compute_slope(lengths, [out["cab"][l]["l2"] for l in lengths])
    gate = evaluate_gate(mohawk_slope["slope"], cab_slope["slope"],
                          {l: out["cab"][l]["l2"] for l in lengths})
    return {"mohawk": {**out["mohawk"], "slope": mohawk_slope},
            "cab": {**out["cab"], "slope": cab_slope}, "gate": gate}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | `extract_hidden_states` + `run_variant` inner batch loop | forward pass, per-length aggregation over batches |
| L-7-2 | `run_full_analysis` outer orchestration | load models/docs, run both variants, slope+gate compute, CAB fallback skip |

---

## External Dependencies

None — green-field, no base hypothesis code to call into. All APIs above are new.
