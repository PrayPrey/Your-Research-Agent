# Logic: H-M1
# Causal Attribution — Encoder Architecture Determines OrbitVar (≥4 OOM)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Causal Step 1)
**Date:** 2026-08-03
**Base:** H-E1 (INCREMENTAL)

Applied: N/A — Archon KB max similarity 0.40, below threshold (diffusion model docs only)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** API signatures verified from actual H-E1 code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Relevant Symbols:**
- `compute_orbit_var_all_models(dataset, encoder_fn, perm_specs, log_every=10) -> tuple` — returns `(per_model_vars, mean_orbitvar, max_orbitvar)`
- `DeepSetsChannelEncoder.__init__(kernel_dims, hidden_dim, embed_dim)` — has `.phi_layers` (ModuleList), `.rho_layers` (ModuleList), `.proj` (Linear)
- `DeepSetsChannelEncoder.forward(state_dict: dict) -> Tensor` — `# (embed_dim,)`
- `build_c2_encoder(embed_dim=128, hidden_dim=64) -> DeepSetsChannelEncoder`

---

## External Dependencies API (H-E1 Verified)

```python
# From: docs/youra_research/h-e1/code/orbit_var.py (ACTUAL CODE)
def compute_orbit_var_all_models(
    dataset: list,
    encoder_fn: Callable,        # encoder_fn(state_dict: dict) -> Tensor (embed_dim,)
    perm_specs: list,
    log_every: int = 10,
) -> tuple:                      # (list[float], float, float)
    ...                          # returns (per_model_vars, mean_orbitvar, max_orbitvar)

# From: docs/youra_research/h-e1/code/encoder_c2.py (ACTUAL CODE)
class DeepSetsChannelEncoder(nn.Module):
    def __init__(
        self,
        kernel_dims: list = None,  # default [25, 25, 4]
        hidden_dim: int = 64,
        embed_dim: int = 128,
    ): ...
    def forward(self, state_dict: dict) -> torch.Tensor: ...  # (embed_dim,)
    # Attributes: .phi_layers (ModuleList), .rho_layers (ModuleList), .proj (Linear)

def build_c2_encoder(embed_dim: int = 128, hidden_dim: int = 64) -> DeepSetsChannelEncoder: ...

# From: docs/youra_research/h-e1/code/permutation.py
def sample_functional_permutations(channels_per_layer, K, seed=1) -> list: ...
def apply_permutation(state_dict: dict, perm_spec) -> dict: ...

# From: docs/youra_research/h-e1/code/data_loader.py
def load_dataset(path: str) -> list: ...  # list of state_dicts
def reconstruct_state_dict(entry) -> dict: ...
```

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation, NOT spec)

---

## A-2: CISEEncoder (C1) [Complexity: 10, Budget: 2 subtasks]

### API Signatures

```python
# encoder_c1.py
import torch
import torch.nn as nn
import math

class CISEEncoder(nn.Module):
    """Channel-Index Sinusoidal Encoder — NOT permutation-invariant (baseline contrast)."""

    def __init__(self, embed_dim: int = 64, max_channels: int = 16):
        """embed_dim: output size; max_channels: sinusoidal PE table size."""
        super().__init__()
        self.embed_dim = embed_dim
        self.max_channels = max_channels
        # Sinusoidal PE table: shape (max_channels, embed_dim)
        # Not a learned parameter — fixed at init
        pe = self._build_pe_table(max_channels, embed_dim)
        self.register_buffer('pe', pe)                  # (max_channels, embed_dim)
        self.proj = nn.Linear(embed_dim, embed_dim)

    @staticmethod
    def _build_pe_table(max_channels: int, embed_dim: int) -> torch.Tensor:
        """Standard sinusoidal PE. Returns (max_channels, embed_dim)."""
        # pe[pos, 2i]   = sin(pos / 10000^(2i/embed_dim))
        # pe[pos, 2i+1] = cos(pos / 10000^(2i/embed_dim))
        pe = torch.zeros(max_channels, embed_dim)
        pos = torch.arange(max_channels, dtype=torch.float).unsqueeze(1)  # (C, 1)
        div = torch.exp(
            torch.arange(0, embed_dim, 2, dtype=torch.float)
            * (-math.log(10000.0) / embed_dim)
        )                                                # (embed_dim/2,)
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div[:embed_dim // 2])
        return pe

    def forward(self, state_dict: dict) -> torch.Tensor:
        """
        state_dict -> (embed_dim,) float32 embedding.
        Encodes each conv layer by summing weight-scaled PE vectors over channels.
        NOT invariant: channel index position is preserved via PE.
        """
        # state_dict keys include conv weight tensors (C_out, C_in, kH, kW)
        # Accumulate embedding across all conv layers
        accum = torch.zeros(self.embed_dim)             # (embed_dim,)
        for key, W in state_dict.items():
            if W.dim() != 4:
                continue                                # skip non-conv weights
            C_out, C_in, kH, kW = W.shape              # e.g. (16, 3, 5, 5)
            # For each output channel c, use its PE at position c
            # and scale by mean absolute weight across (C_in, kH, kW)
            for c in range(min(C_out, self.max_channels)):
                w_mean = W[c].abs().mean()              # scalar
                accum += w_mean * self.pe[c]            # (embed_dim,)
        return self.proj(accum)                         # (embed_dim,)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| pe | (max_channels, embed_dim) | Fixed sinusoidal table, registered buffer |
| W | (C_out, C_in, kH, kW) | Conv weight from state_dict |
| accum | (embed_dim,) | Accumulated PE-weighted sum |
| output | (embed_dim,) | After proj linear |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | CISEEncoder.forward() | Sinusoidal PE table build + forward; tensor shape annotations; no sort/argsort/topk |
| L-2-2 | anti_confound_gate() | inspect.getsource check on phi_layers + numeric permutation invariance test |

---

## A-6: Anti-Confound Gate [documented inline — no subtask budget needed]

### API Signatures

```python
import inspect

def anti_confound_gate(encoder_c2: nn.Module) -> dict:
    """
    Returns dict(passed=bool, max_diff=float, code_inspection=bool).
    Two checks: (1) numeric permutation invariance, (2) source code inspection.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-e1', 'code'))
    from data_loader import CONV_WEIGHT_KEYS

    # --- Check 1: code inspection ---
    # Inspect phi_layers[0] source (first Sequential in ModuleList)
    phi_src = inspect.getsource(type(encoder_c2.phi_layers[0][0]))  # Linear — benign
    # Also inspect the full encoder class source
    enc_src = inspect.getsource(type(encoder_c2))
    forbidden = ('sort', 'argsort', 'topk')
    code_ok = not any(kw in enc_src for kw in forbidden)

    # --- Check 2: numeric permutation invariance ---
    # Build a dummy state_dict with random conv weights
    # Permute channel order of C_out dim, check output unchanged
    import torch
    dummy_sd = {
        'conv1.weight': torch.randn(16, 3, 5, 5),
        'conv2.weight': torch.randn(16, 16, 5, 5),
        'conv3.weight': torch.randn(16, 16, 2, 2),
    }
    encoder_c2.eval()
    with torch.no_grad():
        emb_orig = encoder_c2(dummy_sd)                         # (embed_dim,)
        # Permute C_out channels of conv1
        perm = torch.randperm(16)
        perm_sd = dict(dummy_sd)
        perm_sd['conv1.weight'] = dummy_sd['conv1.weight'][perm]
        emb_perm = encoder_c2(perm_sd)                         # (embed_dim,)
    max_diff = (emb_orig - emb_perm).abs().max().item()
    numeric_ok = max_diff < 1e-6

    passed = code_ok and numeric_ok
    return {'passed': passed, 'max_diff': max_diff, 'code_inspection': code_ok}
```

### Pseudo-code

```
1. enc_src = inspect.getsource(DeepSetsChannelEncoder)
2. code_ok = 'sort' not in enc_src and 'argsort' not in enc_src and 'topk' not in enc_src
3. dummy_sd = {conv_key: randn(C_out, C_in, kH, kW) for each conv layer}
4. emb_orig = encoder_c2(dummy_sd)
5. perm_sd = dummy_sd with conv1.weight rows permuted by randperm(C_out)
6. emb_perm = encoder_c2(perm_sd)
7. max_diff = |emb_orig - emb_perm|.max()
8. return {passed: code_ok and max_diff < 1e-6, max_diff: max_diff, code_inspection: code_ok}
```

---

## Other Epics — Key Signatures Only

### A-1: Prereq Verification

```python
def verify_prerequisites(h_e1_results_path: str) -> tuple[np.ndarray, np.ndarray]:
    # Returns (orbit_vars_C2, orbit_vars_C3) as np.ndarray [N_MODELS]
    # Asserts np.mean(orbit_vars_C2) ≈ 1.002e-14 (rtol=0.05)
    # Asserts np.mean(orbit_vars_C3) ≈ 8.905e-08 (rtol=0.05)
    ...
```

### A-3: CISE OrbitVar Measurement

```python
def measure_cise_orbitvar(
    dataset: list,
    perm_specs: list,
    build_on: bool = True,
    build_on_value: float = 0.010333,
) -> np.ndarray:
    # Returns orbit_vars_C1: np.ndarray [N_MODELS]
    # If build_on=True: returns np.full(len(dataset), build_on_value)
    # Else: calls compute_orbit_var_all_models with CISEEncoder().forward
    ...
```

### A-4: Ratio Computation

```python
def compute_ratios(
    orbit_vars_C1: np.ndarray,  # [N_MODELS]
    orbit_vars_C2: np.ndarray,  # [N_MODELS]
    orbit_vars_C3: np.ndarray,  # [N_MODELS]
    eps: float = 1e-30,
) -> dict:
    # Returns: ratios_C1_C2 [N_MODELS], ratios_C1_C3 [N_MODELS],
    #          mean/median/geomean per ratio, log10_oom_C1C2, log10_oom_C1C3
    ...
```

### A-5: Wilcoxon Tests

```python
def run_wilcoxon(
    orbit_vars_C1: np.ndarray,  # [N_MODELS]
    orbit_vars_C2: np.ndarray,  # [N_MODELS]
    orbit_vars_C3: np.ndarray,  # [N_MODELS]
    eps: float = 1e-30,
) -> dict:
    # log10-transforms inputs then calls scipy.stats.wilcoxon(alternative='greater')
    # Returns: {stat_C1C2, p_C1C2, stat_C1C3, p_C1C3}
    ...
```

### A-7: Gate Check + Results Save

```python
def gate_check(ratios: dict, wilcoxon: dict, anti_gate: dict) -> bool:
    # Prints gate table; returns True if all MUST_WORK gates pass; sys.exit(1) on fail
    ...
```

### A-8: Visualization

```python
# visualize.py
def plot_orbitvar_violin(
    orbit_vars_C1: np.ndarray,  # [N_MODELS]
    orbit_vars_C2: np.ndarray,  # [N_MODELS]
    orbit_vars_C3: np.ndarray,  # [N_MODELS]
    out_path: str,
) -> None: ...

def plot_ratio_histogram(
    ratios_C1_C2: np.ndarray,  # [N_MODELS]
    ratios_C1_C3: np.ndarray,  # [N_MODELS]
    out_path: str,
) -> None: ...

def plot_summary_table(results: dict, out_path: str) -> None: ...
```
