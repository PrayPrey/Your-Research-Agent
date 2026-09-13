# Logic: H-M3 — Latent Space Interpolation via EquiSSL-perm Decoder

**Date:** 2026-08-05
**Phase:** 3 — Logic Design

Applied: frozen-encoder evaluation pipeline (stateless graph encoder, no-grad inference)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-M1 + H-E1)
**Status**: API signatures verified from actual code
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `EquiSSLEncoder.forward(data: Data) -> Tensor` — returns L2-normalized z of shape `(B, latent_dim)`
- `GraphDecoder.forward(z: Tensor, structure: dict) -> Tensor` — returns `(B, max_edge_dim)` statistics vector, NOT raw weights
- `checkpoint_to_graph(state_dict: dict) -> Data` — builds PyG Data with node stats `(n_layers, 4)`, edge stats `(n_edges, 4)`, and `structure` dict containing `n_layers`, `layer_sizes`, `layers`, `offsets`

---

## External Dependencies API

### From actual code (verified)

```python
# docs/youra_research/h-m1/code/models/equissl_encoder.py
class EquiSSLEncoder(nn.Module):
    def __init__(
        self,
        node_in_dim: int = 4,
        edge_in_dim: int = 4,
        hidden_dim: int = 256,
        latent_dim: int = 128,
        num_layers: int = 4,
        symmetry: str = 'monomial',
        pool: str = 'mean'
    ): ...

    def forward(self, data: Data) -> torch.Tensor:
        """data: PyG Data with x:(N,4), edge_index:(2,E), edge_attr:(E,4), batch:(N,)
        Returns: z  # (B, latent_dim), L2-normalized"""

# docs/youra_research/h-m1/code/models/graph_decoder.py
class GraphDecoder(nn.Module):
    def __init__(
        self,
        latent_dim: int = 128,
        hidden_dim: int = 256,
        max_edge_dim: int = 512
    ): ...

    def forward(self, z: torch.Tensor, structure: dict) -> torch.Tensor:
        """z: (B, latent_dim) -> out: (B, max_edge_dim)
        structure: {'n_layers', 'layer_sizes', 'layers', 'offsets'}
        Returns STATISTICS RECONSTRUCTION VECTOR, not raw weight tensors."""

# docs/youra_research/h-m1/code/data/multizoo_graph_dataset.py
def checkpoint_to_graph(state_dict: dict) -> Data:
    """state_dict -> PyG Data
    Data.x:         (n_layers, 4)   — per-layer [mean, std, l2_norm, max_abs]
    Data.edge_attr: (n_edges, 4)    — cross-layer stats
    Data.edge_index:(2, n_edges)
    Data.structure: dict with n_layers, layer_sizes (out_dims), layers, offsets
    """
```

**Verified from**: `docs/youra_research/h-m1/code/` actual implementation files.

---

## A-4: Interpolator [Complexity: 15, Budget: 4 subtasks]

Applied: frozen-encoder evaluation pipeline (stateless graph encoder, no-grad inference)

### API Signatures

```python
# interpolation/interpolator.py

def encode_checkpoint(
    encoder: EquiSSLEncoder,
    state_dict: dict,
    device: str
) -> torch.Tensor:
    """state_dict -> z  # (latent_dim,)"""

def decode_latent_to_state_dict(
    decoder: GraphDecoder,
    z: torch.Tensor,           # (latent_dim,)
    reference_state_dict: dict,
    device: str
) -> dict:
    """z -> reconstructed state_dict matching reference_state_dict structure.
    GraphDecoder returns (max_edge_dim,) statistics; this maps back to weight tensors."""

def latent_interpolate(
    encoder: EquiSSLEncoder,
    decoder: GraphDecoder,
    state_dict_a: dict,
    state_dict_b: dict,
    device: str,
    alpha: float = 0.5
) -> dict:
    """Encode both, interpolate in latent space, decode -> state_dict."""

def weight_space_average(
    state_dict_a: dict,
    state_dict_b: dict
) -> dict:
    """Naive weight averaging baseline."""
```

---

### L-4-1: encode_checkpoint [1/4 subtasks]

```python
def encode_checkpoint(
    encoder: EquiSSLEncoder,
    state_dict: dict,
    device: str
) -> torch.Tensor:
    # state_dict: raw PyTorch checkpoint dict
    # returns: z  # (latent_dim,) — L2-normalized
    graph = checkpoint_to_graph(state_dict)
    # graph.x:         (n_layers, 4)
    # graph.edge_attr: (n_edges, 4)
    # graph.edge_index:(2, n_edges)
    graph = graph.to(device)
    # Add batch dim (single graph, no batch vector needed — encoder handles missing batch)
    with torch.no_grad():
        z = encoder(graph)   # (1, latent_dim) — encoder uses batch from data.batch
    return z.squeeze(0)      # (latent_dim,)
```

**Shapes**:
| Variable | Shape | Note |
|----------|-------|------|
| graph.x | (n_layers, 4) | per-layer stats |
| graph.edge_attr | (n_edges, 4) | n_edges = (n_layers-1) + n_layers self-loops |
| z (from encoder) | (1, latent_dim) | encoder returns (B, latent_dim) |
| return | (latent_dim,) | squeezed |

**Edge cases**:
- Empty/malformed state_dict: `checkpoint_to_graph` returns dummy 2-node graph; result z will be near-zero — acceptable, pair will have low accuracy regardless.

---

### L-4-2: decode_latent_to_state_dict [2/4 subtasks] ← CRITICAL

**Key insight**: `GraphDecoder.forward()` outputs a `(max_edge_dim,)` reconstruction of the *edge_attr statistics vector* (not raw weights). The decoder was trained to reconstruct the mean-pooled edge_attr summary. To get a runnable state_dict, we must map the statistics output back to per-layer weight tensors using the reference state_dict's shapes.

**Approach**: The decoder output encodes statistical summaries. We treat it as a learned latent code and project it directly to the flattened weight space of the reference architecture via per-layer linear slicing. Specifically: the reference state_dict tells us the exact weight shapes; we slice `max_edge_dim` output into per-layer segments proportional to parameter count, then reshape each slice to the target shape.

```python
def decode_latent_to_state_dict(
    decoder: GraphDecoder,
    z: torch.Tensor,           # (latent_dim,)
    reference_state_dict: dict,
    device: str
) -> dict:
    """
    Algorithm:
    1. Decoder forward: stats_vec = decoder(z.unsqueeze(0), structure=None)  # (1, max_edge_dim)
       Note: GraphDecoder.forward ignores structure arg (just runs mlp(z))
    2. stats_vec = stats_vec.squeeze(0)  # (max_edge_dim,)
    3. Compute per-key shapes and total param count from reference_state_dict
    4. Truncate/pad stats_vec to total_params
    5. Slice into per-key tensors, reshape to match reference shapes
    6. Return new state_dict with original keys and reconstructed tensors
    """
```

**Pseudo-code**:
```
1. with torch.no_grad():
       stats_vec = decoder(z.unsqueeze(0), {})   # (1, max_edge_dim) — structure ignored
       stats_vec = stats_vec.squeeze(0)           # (max_edge_dim,)

2. Build ordered list of (key, shape, n_params) from reference_state_dict:
       param_specs = [(k, v.shape, v.numel()) for k, v in reference_state_dict.items()]
       total_params = sum(n for _, _, n in param_specs)

3. Map stats_vec -> flattened weight vector:
       max_edge_dim = stats_vec.shape[0]   # e.g., 512
       if total_params <= max_edge_dim:
           flat = stats_vec[:total_params]
       else:
           # Repeat-tile stats_vec to cover total_params
           repeats = (total_params // max_edge_dim) + 1
           flat = stats_vec.repeat(repeats)[:total_params]
           # ponytail: tiling is naive; per-layer MLP projection is better if accuracy collapses

4. Build reconstructed state_dict:
       new_sd = {}
       offset = 0
       for key, shape, n in param_specs:
           new_sd[key] = flat[offset:offset+n].reshape(shape).detach().cpu()
           offset += n

5. Return new_sd
```

**Shapes**:
| Variable | Shape | Note |
|----------|-------|------|
| z input | (latent_dim,) | = (128,) |
| z.unsqueeze(0) | (1, 128) | batch dim for decoder |
| stats_vec | (1, max_edge_dim) | = (1, 512) from decoder mlp |
| flat | (total_params,) | sliced/tiled from stats_vec |
| new_sd[key] | matches reference shape | e.g., (256, 784) for fc1.weight |

**Edge cases**:
- `total_params > max_edge_dim` (common for MLP with 784 input): tiling handles it; reconstructed weights will have periodic structure — acceptable for PoC.
- Mismatched key names vs reference: use `reference_state_dict.keys()` directly, no remapping.
- `reference_state_dict` must come from same task architecture as the pair being evaluated.

---

### L-4-3: latent_interpolate [3/4 subtasks]

```python
def latent_interpolate(
    encoder: EquiSSLEncoder,
    decoder: GraphDecoder,
    state_dict_a: dict,
    state_dict_b: dict,
    device: str,
    alpha: float = 0.5
) -> dict:
    """
    Full pipeline: encode A, encode B, interpolate, decode -> state_dict.
    Uses state_dict_a as the reference architecture for shape reconstruction.
    """
```

**Pseudo-code**:
```
1. z_a = encode_checkpoint(encoder, state_dict_a, device)  # (latent_dim,)
2. z_b = encode_checkpoint(encoder, state_dict_b, device)  # (latent_dim,)
3. z_mid = (1.0 - alpha) * z_a + alpha * z_b              # (latent_dim,)
   # Note: z_a, z_b are L2-normalized; z_mid is NOT re-normalized (deliberate)
   # ponytail: not re-normalizing z_mid; re-normalize if decoder behaves poorly off unit sphere
4. decoded_sd = decode_latent_to_state_dict(decoder, z_mid, state_dict_a, device)
5. return decoded_sd
```

**Shapes**:
| Variable | Shape |
|----------|-------|
| z_a, z_b | (latent_dim,) = (128,) |
| z_mid | (latent_dim,) |

---

### L-4-4: weight_space_average [4/4 subtasks]

```python
def weight_space_average(
    state_dict_a: dict,
    state_dict_b: dict
) -> dict:
    """Baseline: element-wise average of all parameters."""
    return {k: (state_dict_a[k].float() + state_dict_b[k].float()) / 2.0
            for k in state_dict_a}
```

No pseudo-code needed — one line.

**Edge case**: keys in `state_dict_a` not in `state_dict_b` → both come from same-task same-architecture pairs (enforced by pair builder), so key mismatch should not occur. Add assertion in caller if needed.

---

## A-8: Main Runner [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# run_hm3.py

def main() -> None:
    """Orchestrates full H-M3 experiment."""

def _save_results(results: list[dict], out_path: str) -> None:
    """Serialize per-pair results to JSON."""

def _write_validation_report(stats: dict, results: list[dict], out_path: str) -> None:
    """Write 04_validation.md from stats."""
```

---

### L-8-1: run_hm3 main loop [1/2 subtasks]

```python
def main() -> None:
```

**Pseudo-code**:
```
1. Path setup
   project_root = Path(__file__).parent.parent.parent  # TEST_wsl/
   sys.path.insert(0, str(project_root / 'docs/youra_research/h-m1/code'))
   sys.path.insert(0, str(project_root / 'docs/youra_research/h-e1/code'))

2. Build or load pair list
   pairs_path = project_root / 'docs/youra_research/h-m3/data/mlp_pairs.json'
   if pairs_path.exists():
       pairs = load_pairs(pairs_path)
   else:
       pairs = build_mlp_pairs(multizoo_root, min_pairs=500, seed=42)
       save_pairs(pairs, pairs_path)
   assert len(pairs) >= 500

3. Load frozen models
   device = 'cuda' if torch.cuda.is_available() else 'cpu'
   encoder = load_frozen_encoder(ENCODER_CKPT, device)   # eval(), no_grad
   decoder = load_frozen_decoder(DECODER_CKPT, device)   # eval(), no_grad

4. Build test loaders (one per task, reused across pairs)
   test_loaders = {task: get_test_loader(task, DATA_ROOT) for task in TASKS}

5. Main evaluation loop
   results = []
   for pair in tqdm(pairs, desc='Evaluating pairs'):
       sd_a = load_mlp_checkpoint(pair['path_a'], device='cpu')
       sd_b = load_mlp_checkpoint(pair['path_b'], device='cpu')
       task = pair['task']

       # Latent interpolation
       sd_latent = latent_interpolate(encoder, decoder, sd_a, sd_b, device)
       acc_latent = evaluate_state_dict(sd_latent, task, test_loaders[task],
                                        device, TASK_MLP_CONFIGS)

       # Weight-space average
       sd_ws = weight_space_average(sd_a, sd_b)
       acc_ws = evaluate_state_dict(sd_ws, task, test_loaders[task],
                                    device, TASK_MLP_CONFIGS)

       results.append({
           'pair_id': pair['pair_id'],
           'task': task,
           'path_a': pair['path_a'],
           'path_b': pair['path_b'],
           'acc_a': pair['acc_a'],
           'acc_b': pair['acc_b'],
           'acc_latent': acc_latent,
           'acc_ws': acc_ws,
           'delta': acc_latent - acc_ws,
       })

6. Statistics + figures
   stats = compute_statistics(results)
   generate_all_figures(results, stats, FIGURES_DIR)

7. Save outputs
   _save_results(results, RESULTS_DIR / 'hm3_results.json')
   _write_validation_report(stats, results, H_M3_DIR / '04_validation.md')
   print(f"Gate: {'PASS' if stats['gate_pass'] else 'DOCUMENT'}")
   print(f"mean(Δacc)={stats['mean_delta']:.4f}, p={stats['p_value']:.4f}, d={stats['cohen_d']:.3f}")
```

**Error handling**:
- Per-pair exceptions: wrap inner loop body in `try/except`, log and skip pair, continue — don't abort full run.
- Checkpoint load failure: log `pair_id` and continue.
- Minimum pair count check after loop: warn if `len(results) < 500`.

---

### L-8-2: result serialization [2/2 subtasks]

#### hm3_results.json schema

```json
{
  "metadata": {
    "experiment": "H-M3",
    "date": "2026-08-05",
    "n_pairs": 500,
    "encoder_ckpt": "h-m1/checkpoints/equi_perm_seed0.pt",
    "decoder_ckpt": "h-e1/checkpoints/decoder_seed0.pt",
    "seed": 42
  },
  "statistics": {
    "mean_delta": 0.0,
    "std_delta": 0.0,
    "n_pairs": 500,
    "t_stat": 0.0,
    "p_value": 1.0,
    "cohen_d": 0.0,
    "pct_pairs_positive": 0.0,
    "gate_pass": false,
    "per_task": {
      "mnist":   {"mean_delta": 0.0, "n": 0},
      "svhn":    {"mean_delta": 0.0, "n": 0},
      "cifar10": {"mean_delta": 0.0, "n": 0}
    }
  },
  "pairs": [
    {
      "pair_id": "mnist_0",
      "task": "mnist",
      "path_a": "...",
      "path_b": "...",
      "acc_a": 0.95,
      "acc_b": 0.94,
      "acc_latent": 0.0,
      "acc_ws": 0.0,
      "delta": 0.0
    }
  ]
}
```

#### _save_results

```python
def _save_results(results: list[dict], out_path: str) -> None:
    # results: list of per-pair dicts (from main loop)
    # Compute stats inline or accept pre-computed stats
    payload = {
        'metadata': {
            'experiment': 'H-M3',
            'date': datetime.date.today().isoformat(),
            'n_pairs': len(results),
            'encoder_ckpt': ENCODER_CKPT,
            'decoder_ckpt': DECODER_CKPT,
            'seed': PAIR_SEED,
        },
        'pairs': results,
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)
```

#### _write_validation_report

```python
def _write_validation_report(stats: dict, results: list[dict], out_path: str) -> None:
    """
    Writes 04_validation.md.
    Content structure:
    1. Summary: n_pairs, tasks, gate result (PASS / DOCUMENT)
    2. Table: mean±std accuracy for latent vs ws, per task + overall
    3. Statistical results: t_stat, p_value, cohen_d, pct_pairs_positive
    4. Gate evaluation: condition check + interpretation sentence
    5. Figure references (relative paths to h-m3/figures/)
    6. Conclusion sentence
    """
    gate_str = 'PASS' if stats['gate_pass'] else 'DOCUMENT'
    lines = [
        '# Validation: H-M3\n',
        f'**Gate**: {gate_str}  ',
        f'**Pairs evaluated**: {stats["n_pairs"]}  ',
        f'**Tasks**: MNIST, SVHN, CIFAR-10\n',
        '## Results\n',
        '| Method | MNIST | SVHN | CIFAR-10 | Overall |',
        '|--------|-------|------|----------|---------|',
        # populated from stats['per_task'] + overall means
        '...',
        '\n## Statistics\n',
        f'- t-statistic: {stats["t_stat"]:.4f}',
        f'- p-value: {stats["p_value"]:.4f}',
        f'- Cohen\'s d: {stats["cohen_d"]:.3f}',
        f'- % pairs positive: {stats["pct_pairs_positive"]:.1f}%',
        f'- mean(Δacc): {stats["mean_delta"]:.4f} ± {stats["std_delta"]:.4f}',
        '\n## Gate Evaluation\n',
        # PASS or DOCUMENT + interpretation
        '\n## Figures\n',
        '- figures/gate_comparison.png',
        '- figures/task_stratified.png',
        '- figures/delta_histogram.png',
        '- figures/pair_scatter.png',
    ]
    Path(out_path).write_text('\n'.join(lines))
```

---

## Subtask Summary

| ID | Module | Subtask | Budget |
|----|--------|---------|--------|
| L-4-1 | interpolator.py | encode_checkpoint | 1 |
| L-4-2 | interpolator.py | decode_latent_to_state_dict | 2 |
| L-4-3 | interpolator.py | latent_interpolate | 1 |
| L-4-4 | interpolator.py | weight_space_average | 0 |
| L-8-1 | run_hm3.py | main loop | 1 |
| L-8-2 | run_hm3.py | result serialization | 1 |

**Total**: 6 subtasks [6/6 budget used]

---

## Implementation Risk Notes

**L-4-2 is the highest risk.** `GraphDecoder` was trained to reconstruct *edge_attr statistics* (4D per-edge vectors), not raw weight tensors. The tiling approach to map `(512,)` → flattened weights is a PoC approximation. If `acc_latent` is near-random (< 10%), the decoder reconstruction is the likely cause. Verify with a single checkpoint round-trip (encode → decode → evaluate) before running 500 pairs.

**Verification check** (add to run_hm3.py `--verify` flag):
```python
# Encode and decode a single checkpoint; check acc vs original
sd_test = load_mlp_checkpoint(pairs[0]['path_a'], 'cpu')
sd_roundtrip = decode_latent_to_state_dict(
    decoder, encode_checkpoint(encoder, sd_test, device), sd_test, device)
acc_orig = evaluate_state_dict(sd_test, pairs[0]['task'], ...)
acc_rt   = evaluate_state_dict(sd_roundtrip, pairs[0]['task'], ...)
print(f"Round-trip: {acc_orig:.3f} -> {acc_rt:.3f}")
# If acc_rt << acc_orig, tiling reconstruction is failing; see ponytail note in L-4-2
```
