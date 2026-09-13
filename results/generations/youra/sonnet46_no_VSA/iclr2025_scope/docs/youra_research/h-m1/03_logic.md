# Logic: H-M1
# SSD Frobenius Error Scaling Gate Experiment

**Date:** 2026-08-03 | **Phase:** 3 — Logic Design

Applied: Standard PyTorch per-sample Adam optimization loop

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-4: SSD Fitter Core [Complexity: 15, Budget: 4 subtasks]

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Mamba2 Block Init | Fresh SSD block init per (sample, layer, N) in fp32 |
| L-4-2 | Transfer Matrix Materialization | Call SSD block with return_mixer_matrix=True, handle dict/tensor return |
| L-4-3 | Adam Optimization Loop | 10k-step loop, Frobenius loss, record loss_curve every 100 steps |
| L-4-4 | Precision Management | bfloat16→fp32 cast for attn_matrix, fp32 SSD, fp32 gradients |

---

### L-4-1: Mamba2 Block Init

**Parent:** A-4

```python
# ssd_fitter.py
from mamba_ssm import Mamba2

def _init_ssd_block(d_model: int, d_state: int, n_heads: int, device: torch.device) -> Mamba2:
    """Fresh Mamba2 block in fp32 on device. Call once per (sample, layer, N)."""
    # headdim = d_model // n_heads = 4096 // 32 = 128
    # expand=2 → d_inner = d_model * 2 = 8192
    block = Mamba2(
        d_model=d_model,       # 4096
        d_state=d_state,       # 64
        headdim=d_model // n_heads,  # 128
        expand=2,
    ).to(device=device, dtype=torch.float32)
    return block
```

**Tensor shapes:**
- No input tensors; returns initialized `nn.Module` in fp32

**Edge cases:**
- Always call `.to(dtype=torch.float32)` — SSMs sensitive to precision
- Never reuse across samples (fresh init required for unbiased measurement)

---

### L-4-2: Transfer Matrix Materialization

**Parent:** A-4

```python
def _materialize_transfer_matrix(
    block: Mamba2,
    hidden_states: torch.Tensor,  # [1, N, d_model] fp32
) -> torch.Tensor:                # [N, N] fp32
    """Forward block with return_mixer_matrix=True; handle dict or tensor return."""
    out = block(hidden_states, return_mixer_matrix=True)
    if isinstance(out, dict):
        transfer_matrix = out["transfer_matrix"]   # [N, N]
    elif isinstance(out, (tuple, list)):
        # phi-mamba phi_block may return (hidden, transfer_matrix)
        transfer_matrix = out[1]
    else:
        transfer_matrix = out  # direct tensor fallback
    # Ensure [N, N] fp32
    if transfer_matrix.dim() == 3:
        transfer_matrix = transfer_matrix.squeeze(0)  # [1, N, N] → [N, N]
    return transfer_matrix.float()
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [1, N, d_model] | batch=1 |
| transfer_matrix | [N, N] | materialized SSD mixing matrix |

**Edge cases:**
- phi-mamba API may return dict, tuple, or raw tensor — handle all three
- Squeeze batch dim if present
- Always cast to float32

---

### L-4-3: Adam Optimization Loop

**Parent:** A-4

```python
def _run_optimization(
    block: Mamba2,
    hidden_states: torch.Tensor,   # [1, N, d_model] fp32
    attn_matrix: torch.Tensor,     # [N, N] fp32 (pre-cast)
    n_steps: int = 10000,
    lr: float = 1e-3,
    log_every: int = 100,
) -> tuple[float, list[float]]:
    """10k Adam steps. Returns (final_frobenius_error, loss_curve)."""
    # loss_curve has len = n_steps // log_every = 100 entries
    optimizer = torch.optim.Adam(block.parameters(), lr=lr, betas=(0.9, 0.999))
    loss_curve: list[float] = []

    for step in range(n_steps):
        optimizer.zero_grad()
        transfer_matrix = _materialize_transfer_matrix(block, hidden_states)  # [N, N]
        loss = torch.linalg.matrix_norm(transfer_matrix - attn_matrix, ord="fro").mean()
        loss.backward()
        optimizer.step()
        if step % log_every == 0:
            loss_curve.append(loss.item())

    final_error = loss.item()
    return final_error, loss_curve
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [1, N, d_model] | fwd input |
| attn_matrix | [N, N] | target (fp32) |
| transfer_matrix | [N, N] | SSD output per step |
| loss | scalar | Frobenius norm |

**Pseudo-code:**
```
optimizer = Adam(block.params, lr=1e-3, betas=(0.9,0.999))
for step in 0..9999:
    T = block(hidden_states, return_mixer_matrix=True)  # [N,N]
    loss = ||T - A||_F
    loss.backward(); optimizer.step()
    if step % 100 == 0: loss_curve.append(loss.item())
return loss.item(), loss_curve
```

**Edge cases:**
- Do NOT use `torch.no_grad()` inside loop — gradients required
- `loss.mean()` handles case where matrix_norm returns batched scalar

---

### L-4-4: Precision Management (fit_and_measure)

**Parent:** A-4

```python
class SSDFitter:
    def __init__(self, cfg: "Config"):
        self.cfg = cfg
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def fit_and_measure(
        self,
        attn_matrix: torch.Tensor,   # [N, N] bfloat16
        hidden_states: torch.Tensor,  # [1, N, d_model] any dtype
        log_loss_curve: bool = False,
    ) -> tuple[float, list[float]]:
        """Fit SSD to attn_matrix. Returns (frobenius_error, loss_curve)."""
        N = attn_matrix.shape[0]
        # Precision: cast both to fp32 before optimization
        attn_fp32 = attn_matrix.float().to(self.device)       # [N, N] fp32
        h_fp32 = hidden_states.float().to(self.device)        # [1, N, d_model] fp32

        block = _init_ssd_block(
            self.cfg.d_model, self.cfg.d_state, self.cfg.n_heads, self.device
        )
        error, loss_curve = _run_optimization(
            block, h_fp32, attn_fp32,
            n_steps=self.cfg.n_opt_steps,
            lr=self.cfg.lr,
            log_every=100,
        )
        if not log_loss_curve:
            loss_curve = []
        # Free GPU memory immediately
        del block, attn_fp32, h_fp32
        torch.cuda.empty_cache()
        return error, loss_curve
```

**Edge cases:**
- Always cast attn_matrix from bfloat16 to float32 before loss computation
- del + empty_cache after each fit to prevent GPU OOM across 500×32 iterations

---

## A-3: Teacher Attention Extraction [Complexity: 14, Budget: 4 subtasks]

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | LLaMA-3-8B Loading | bfloat16, device_map="cuda", attn_implementation="eager" |
| L-3-2 | Forward Pass with output_attentions | Extract all_attentions list, 32 layers |
| L-3-3 | Head Selection | 1 random head per layer per sample, fixed seed per sample |
| L-3-4 | OOM Guard | no_grad, del attn_weights, empty_cache per sample |

---

### L-3-1: LLaMA-3-8B Loading

**Parent:** A-3

```python
# data.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_teacher(model_id: str = "meta-llama/Llama-3-8B") -> tuple:
    """Returns (model, tokenizer). bfloat16, eager attention for dense matrices."""
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="eager",  # required: flash-attn does not return attention weights
    )
    model.eval()
    return model, tokenizer
```

**Edge cases:**
- `attn_implementation="eager"` is mandatory — flash-attn suppresses attention matrix output
- `model.eval()` prevents dropout affecting attention weights

---

### L-3-2: Forward Pass with output_attentions

**Parent:** A-3

```python
def _forward_with_attentions(
    model,
    input_ids: torch.Tensor,  # [1, N]
) -> list[torch.Tensor]:      # list of 32 tensors, each [1, n_heads, N, N] bfloat16
    """Single forward pass; returns all_attentions list."""
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            output_attentions=True,
            use_cache=False,
        )
    # outputs.attentions: tuple of 32 tensors [1, n_heads, N, N]
    return list(outputs.attentions)
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, N] | single sample |
| outputs.attentions[i] | [1, n_heads, N, N] | per-layer, bfloat16 |

**Edge cases:**
- `use_cache=False` prevents KV-cache allocation for large N
- outputs.attentions is a tuple; convert to list for indexing

---

### L-3-3: Head Selection

**Parent:** A-3

```python
def _select_head(
    attn_weights: torch.Tensor,  # [1, n_heads, N, N] bfloat16
    layer_idx: int,
    sample_idx: int,
    base_seed: int = 42,
) -> torch.Tensor:               # [N, N] bfloat16
    """Select 1 random head. Seed is deterministic per (sample, layer)."""
    rng = torch.Generator()
    rng.manual_seed(base_seed + sample_idx * 32 + layer_idx)
    n_heads = attn_weights.shape[1]
    head_idx = torch.randint(0, n_heads, (1,), generator=rng).item()
    return attn_weights[0, head_idx]  # [N, N] bfloat16
```

**Edge cases:**
- Seed formula `base_seed + sample_idx * 32 + layer_idx` guarantees unique seed per (sample, layer) — no collision for 500 samples × 32 layers
- Return squeeze batch dim (index [0])

---

### L-3-4: OOM Guard (extract_attention_matrices)

**Parent:** A-3

```python
def extract_attention_matrices(
    model,
    input_ids: torch.Tensor,  # [1, N]
    sample_idx: int,
    cfg: "Config",
) -> torch.Tensor:            # [n_layers, N, N] bfloat16, on CPU
    """Extract 1 head per layer. Moves each layer result to CPU immediately."""
    all_attentions = _forward_with_attentions(model, input_ids)
    # all_attentions: list[32] of [1, n_heads, N, N]

    result = []
    for layer_idx, attn_weights in enumerate(all_attentions):
        head_attn = _select_head(attn_weights, layer_idx, sample_idx, cfg.seed)
        result.append(head_attn.cpu())   # move to CPU to free GPU memory
        del attn_weights
    del all_attentions
    torch.cuda.empty_cache()

    return torch.stack(result, dim=0)  # [n_layers, N, N] bfloat16 on CPU
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, N] | single sample |
| per-layer result | [N, N] | bfloat16, moved to CPU |
| return | [32, N, N] | stacked, CPU bfloat16 |

**Edge cases:**
- Move each layer tensor to CPU before processing next layer — prevents GPU OOM at N=8192 (8192×8192×32×bfloat16 ≈ 32GB)
- del both layer tensor and full list before empty_cache

---

## A-7: Experiment Orchestration [Complexity: 13, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Outer Loop Structure | lengths→samples→layers loop, accumulate errors_by_N |
| L-7-2 | Intermediate Checkpointing | Save errors_by_N.pkl every 50 samples, resume if checkpoint exists |

---

### L-7-1: Outer Loop Structure

**Parent:** A-7

```python
# experiment.py
from tqdm import tqdm
import pickle, json
from pathlib import Path

class Experiment:
    def __init__(self, cfg: "Config"):
        self.cfg = cfg
        self.pipeline = DataPipeline(cfg)
        self.fitter = SSDFitter(cfg)

    def run(self) -> dict:
        """Main loop: lengths → samples → layers. Returns errors_by_N dict."""
        model, tokenizer = self.pipeline.load_teacher()
        errors_by_N: dict[int, list[float]] = {N: [] for N in self.cfg.target_lengths}
        toeplitz_by_N: dict[int, list[float]] = {N: [] for N in self.cfg.target_lengths}
        layer_errors_8k: list[float] = [0.0] * self.cfg.n_layers  # accumulate mean at N=8192

        for seq_len in self.cfg.target_lengths:
            input_ids_batch = self.pipeline.sample_sequences(seq_len)  # [n_samples, seq_len]
            for sample_idx in tqdm(range(self.cfg.n_samples), desc=f"N={seq_len}"):
                input_ids = input_ids_batch[sample_idx:sample_idx+1].cuda()  # [1, seq_len]
                attn_matrices = self.pipeline.extract_attention_matrices(
                    model, input_ids, sample_idx, self.cfg
                )  # [n_layers, seq_len, seq_len] bfloat16 CPU

                for layer_idx in range(self.cfg.n_layers):
                    attn = attn_matrices[layer_idx]  # [N, N] bfloat16
                    # hidden_states: zeros placeholder (SSD optimized freely)
                    hidden = torch.zeros(1, seq_len, self.cfg.d_model)
                    log_curve = (sample_idx < 5)  # diagnostic: first 5 samples only
                    error, loss_curve = self.fitter.fit_and_measure(attn, hidden, log_curve)
                    errors_by_N[seq_len].append(error)
                    toeplitz_by_N[seq_len].append(self.fitter.toeplitz_error(attn))
                    if seq_len == 8192:
                        layer_errors_8k[layer_idx] += error / self.cfg.n_samples

                if sample_idx % 50 == 49:
                    self._checkpoint(errors_by_N, sample_idx, seq_len)

        return {
            "errors_by_N": errors_by_N,
            "toeplitz_by_N": toeplitz_by_N,
            "layer_errors_8k": layer_errors_8k,
        }
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| input_ids_batch | [500, N] | all samples for one seq_len |
| attn_matrices | [32, N, N] | CPU bfloat16 per sample |
| hidden | [1, N, 4096] | zeros placeholder |

**Edge cases:**
- hidden_states are zeros — SSD optimizes freely per sample (measurement study, not distillation)
- layer_errors_8k accumulates mean incrementally to avoid storing all errors

---

### L-7-2: Intermediate Checkpointing

**Parent:** A-7

```python
def _checkpoint(
    self,
    errors_by_N: dict[int, list[float]],
    sample_idx: int,
    seq_len: int,
) -> None:
    """Save checkpoint every 50 samples."""
    ckpt_path = Path(self.cfg.results_dir) / f"ckpt_N{seq_len}_s{sample_idx}.pkl"
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ckpt_path, "wb") as f:
        pickle.dump({"errors_by_N": errors_by_N, "sample_idx": sample_idx, "seq_len": seq_len}, f)

@staticmethod
def _load_checkpoint(results_dir: str, seq_len: int) -> tuple[dict | None, int]:
    """Find latest checkpoint for seq_len. Returns (errors_by_N, resume_sample_idx) or (None, 0)."""
    ckpt_files = sorted(Path(results_dir).glob(f"ckpt_N{seq_len}_s*.pkl"))
    if not ckpt_files:
        return None, 0
    with open(ckpt_files[-1], "rb") as f:
        data = pickle.load(f)
    return data["errors_by_N"], data["sample_idx"] + 1
```

**Edge cases:**
- `sorted()` on glob gives alphabetical order; use zero-padded sample_idx if n_samples > 99 (500 samples: `s0499` needs padding — use `f"s{sample_idx:04d}"`)
- `mkdir(parents=True, exist_ok=True)` handles missing results dir

---

## A-5: Mechanism Verification [Complexity: 9, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | verify_mechanism_activated | Shape, convergence, finite-loss checks |

---

### L-5-1: verify_mechanism_activated

**Parent:** A-5

```python
# ssd_fitter.py
def verify_mechanism_activated(
    transfer_matrix: torch.Tensor,  # [N, N] fp32
    attn_matrix: torch.Tensor,      # [N, N] fp32
    seq_len: int,
    loss_curve: list[float],        # len = n_steps // 100
) -> tuple[bool, dict]:
    """Returns (all_checks_pass, diagnostics_dict)."""
    checks: dict[str, bool] = {}

    checks["shape_correct"] = (
        transfer_matrix.shape == (seq_len, seq_len)
        and attn_matrix.shape == (seq_len, seq_len)
    )
    checks["matrix_differs_from_attention"] = not torch.allclose(
        transfer_matrix, attn_matrix, atol=1e-3
    )
    checks["loss_finite"] = (
        len(loss_curve) > 0
        and all(math.isfinite(v) for v in loss_curve)
    )
    if len(loss_curve) >= 2:
        initial, final = loss_curve[0], loss_curve[-1]
        checks["loss_decreased_10pct"] = (
            initial > 0 and (initial - final) / initial >= 0.10
        )
    else:
        checks["loss_decreased_10pct"] = False

    all_pass = all(checks.values())
    return all_pass, checks
```

**Edge cases:**
- Guard `initial > 0` before division (prevents ZeroDivisionError if initial loss is 0)
- `math.isfinite` catches both NaN and Inf
- Returns False (not raises) on shape mismatch — caller decides whether to abort

---

## A-6: Toeplitz Baseline [Complexity: 9, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | toeplitz_error | Project onto Toeplitz structure via diagonal averaging, compute Frobenius distance |

---

### L-6-1: toeplitz_error

**Parent:** A-6

```python
# ssd_fitter.py
def toeplitz_error(attn_matrix: torch.Tensor) -> float:
    """Best Toeplitz approximation via diagonal averaging. Returns Frobenius distance."""
    # attn_matrix: [N, N] any dtype → work in fp32
    A = attn_matrix.float()
    N = A.shape[0]
    T = torch.zeros_like(A)

    # Average each diagonal (offset d from -N+1 to N-1) → constant value for that diagonal
    for d in range(-(N - 1), N):
        diag_vals = torch.diagonal(A, offset=d)   # [N - |d|]
        mean_val = diag_vals.mean()
        # Fill corresponding diagonal of T
        idx = torch.arange(len(diag_vals))
        if d >= 0:
            T[idx, idx + d] = mean_val
        else:
            T[idx - d, idx] = mean_val

    error = torch.linalg.matrix_norm(A - T, ord="fro").item()
    return error
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| A | [N, N] | fp32 input |
| T | [N, N] | Toeplitz approximant |
| error | scalar | Frobenius distance |

**Pseudo-code:**
```
For each diagonal offset d in [-(N-1), N-1]:
    mean_val = mean of A's d-th diagonal
    set T's d-th diagonal to mean_val
return ||A - T||_F
```

**Edge cases:**
- Loop is O(N^2) total work — acceptable for N≤8192 as one-time computation per (sample, layer)
- Works for non-square input if needed (uses `torch.diagonal` offset API)

---

## A-8: Scaling Analysis & Gate [Complexity: 9, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | compute_scaling_metrics | log-log slope, pct90, GateResult, gate_pass decision |

---

### L-8-1: compute_scaling_metrics

**Parent:** A-8

```python
# analysis.py
import numpy as np
from dataclasses import dataclass

@dataclass
class GateResult:
    log_slope: float       # β from log-log regression
    pct90: float           # 90th percentile at N=8192
    gate_pass: bool        # True if slope<=0.5 AND pct90<=0.3
    decision: str          # "PASS" or "STOP"
    mean_errors: dict[int, float]  # {N: mean_error}

def compute_scaling_metrics(
    errors_by_N: dict[int, list[float]],
    slope_threshold: float = 0.5,
    pct90_threshold: float = 0.3,
) -> GateResult:
    """Compute gate metrics from raw error dict."""
    Ns = sorted(errors_by_N.keys())                          # [512, 1024, 2048, 4096, 8192]
    mean_errors = {N: float(np.mean(errors_by_N[N])) for N in Ns}

    log_Ns = np.log(Ns)
    log_Es = np.log([mean_errors[N] for N in Ns])
    log_slope = float(np.polyfit(log_Ns, log_Es, 1)[0])     # β

    pct90 = float(np.percentile(errors_by_N[8192], 90))

    gate_pass = (log_slope <= slope_threshold) and (pct90 <= pct90_threshold)
    return GateResult(
        log_slope=log_slope,
        pct90=pct90,
        gate_pass=gate_pass,
        decision="PASS" if gate_pass else "STOP",
        mean_errors=mean_errors,
    )
```

**Edge cases:**
- `np.log` requires all mean_errors > 0; guard: if any mean == 0, clamp to 1e-9 before log
- `errors_by_N[8192]` must exist — caller ensures 8192 in target_lengths
- `np.polyfit` returns coefficients [slope, intercept]; index [0] is slope

---

## Summary

| Subtask ID | Title | Parent | File |
|------------|-------|--------|------|
| L-4-1 | Mamba2 Block Init | A-4 | ssd_fitter.py |
| L-4-2 | Transfer Matrix Materialization | A-4 | ssd_fitter.py |
| L-4-3 | Adam Optimization Loop | A-4 | ssd_fitter.py |
| L-4-4 | Precision Management (fit_and_measure) | A-4 | ssd_fitter.py |
| L-3-1 | LLaMA-3-8B Loading | A-3 | data.py |
| L-3-2 | Forward Pass with output_attentions | A-3 | data.py |
| L-3-3 | Head Selection | A-3 | data.py |
| L-3-4 | OOM Guard (extract_attention_matrices) | A-3 | data.py |
| L-7-1 | Outer Loop Structure | A-7 | experiment.py |
| L-7-2 | Intermediate Checkpointing | A-7 | experiment.py |
| L-5-1 | verify_mechanism_activated | A-5 | ssd_fitter.py |
| L-6-1 | toeplitz_error | A-6 | ssd_fitter.py |
| L-8-1 | compute_scaling_metrics | A-8 | analysis.py |
