---
title: "Logic: H-M1 — NFT Orbit Invariance Probe"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-26
author: Anonymous
base_hypothesis: H-E1
budget: 14 subtasks (Logic Agent allocation)
---

Applied: Probe-first pattern (embedding extraction precedes similarity analysis; all torch.no_grad())
Applied: Incremental API extension (reuse H-E1 data/orbit APIs; add embedding-specific layer)
Applied: Decile-bucketing for cross-orbit sampling (avoids train/test contamination)

## Codebase Analysis (Serena)

**Project Type**: INCREMENTAL — extends H-E1
**Base Code**: `docs/youra_research/h-e1/code/`
**Verified API patterns from H-E1 architecture (03_architecture.md):**
- `construct_orbit_member(weights_flat: Tensor, transform_type: str, seed: int) -> Tensor` — takes flat (D,) tensor
- `load_zoo(hf_id, config, split) -> list[dict]` — list of per-model weight dicts
- H-E1 data_loader returns flat tensors from `sample_models()`; H-M1 needs dict format for NFT input — must convert after loading

**Critical difference from H-E1:** H-E1 used flat weight vectors for distance metrics. H-M1 needs **per-layer weight dicts** as NFT input. The conversion layer is in `nft_encoder.py`'s data prep.

---

## External Dependencies API

| Function | Source File | Signature | Return Type | Notes |
|----------|-------------|-----------|-------------|-------|
| `load_zoo` | `h-e1/code/data_loader.py` | `load_zoo(hf_id="schurholt/model_zoos_dataset", config="mnist", split="train+validation+test") -> list[dict]` | `list[dict]` | v2 corrected identifier; full 50k zoo required |
| `construct_orbit_member` | `h-e1/code/orbit_construction.py` | `construct_orbit_member(weights_flat: Tensor, transform_type: str, seed: int) -> Tensor` | `Tensor (D,)` | Input must be flat; H-M1 must flatten dict→tensor before calling |
| `aggregate` | `h-e1/code/statistics.py` | `aggregate(distances: list[float], threshold: float, n_boot: int, seed: int) -> dict` | `dict` | Keys: mean, std, p5, p95, frac_above, ci_lower, ci_upper |
| `bootstrap_ci` | via `aggregate()` in h-e1/code/statistics.py | see above | embedded in aggregate() | Use aggregate(); no separate bootstrap_ci export |

---

## A-5 Subtasks: Orbit Invariance Probe (5 subtasks)

### L-5-1: `probe_orbit_invariance()` — top-level probe orchestrator

**Parent Epic**: A-5 (Orbit Invariance Probe, complexity 18)

```python
def probe_orbit_invariance(
    nft_encoder: torch.nn.Module,
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,  # (N, 3): test_accuracy, gen_gap, lr
    orbit_type: str,               # "scaling" | "signflip"
    n_pairs: int = 1000,
    seed: int = 42,
    device: str = "cpu",
) -> dict:
    """
    Full probe pipeline for one orbit type.

    Returns:
        {
          "orbit_type": str,
          "within_sim": Tensor (n_pairs,),
          "cross_sim": Tensor (n_pairs,),
          "gap": Tensor (n_pairs,),
          "base_indices": list[int],
          "cross_indices": list[int],
        }

    Tensor shapes guaranteed:
        within_sim.shape == cross_sim.shape == gap.shape == (n_pairs,)
    """
    rng = torch.Generator().manual_seed(seed)
    base_idx = torch.randperm(len(zoo_weights), generator=rng)[:n_pairs].tolist()

    base_list, orbit_list = build_orbit_pairs(zoo_weights, base_idx, orbit_type, seed)
    cross_list, cross_idx = build_cross_orbit_pairs(zoo_weights, zoo_properties, base_idx, seed)

    emb_base  = extract_embeddings(nft_encoder, base_list,  device=device)  # (n, 256)
    emb_orbit = extract_embeddings(nft_encoder, orbit_list, device=device)  # (n, 256)
    emb_cross = extract_embeddings(nft_encoder, cross_list, device=device)  # (n, 256)

    sims = compute_similarity_vectors(emb_base, emb_orbit, emb_cross)
    return {
        "orbit_type": orbit_type,
        "within_sim": sims["within_sim"],
        "cross_sim":  sims["cross_sim"],
        "gap":        sims["gap"],
        "base_indices": base_idx,
        "cross_indices": cross_idx,
    }
```

**Tensor shapes**: emb_* all (n_pairs, 256); sims all (n_pairs,)

---

### L-5-2: `build_orbit_pairs()` — oracle orbit member construction

**Parent Epic**: A-5

```python
def build_orbit_pairs(
    zoo_weights: list[dict],
    base_indices: list[int],
    orbit_type: str,   # "scaling" | "signflip"
    seed: int = 42,
) -> tuple[list[dict], list[dict]]:
    """
    Construct oracle orbit pair for each base index.

    Algorithm:
        1. For each i in base_indices:
           a. flat_w = flatten_weight_dict(zoo_weights[i])  # (D,)
           b. orbit_flat = construct_orbit_member(flat_w, orbit_type, seed=seed + pair_idx)
              # imported from h-e1/code/orbit_construction.py
           c. orbit_dict = unflatten_to_weight_dict(orbit_flat)  # (D,) → dict
        2. Return (base_list, orbit_list) — parallel lists of weight dicts

    Key invariant: base_list[i] and orbit_list[i] are functionally identical
    (same network function, different weight representation).
    """
    ...

def flatten_weight_dict(w: dict) -> torch.Tensor:
    """Flatten per-layer dict to (D,) tensor. Order: layer0.weight, layer0.bias, layer1.weight, layer1.bias."""
    return torch.cat([
        w["layer0.weight"].flatten(),  # (784*64,) = (50176,)
        w["layer0.bias"].flatten(),    # (64,)
        w["layer1.weight"].flatten(),  # (10*64,) = (640,)
        w["layer1.bias"].flatten(),    # (10,)
    ])  # total: 51850

def unflatten_to_weight_dict(flat: torch.Tensor) -> dict:
    """Inverse of flatten_weight_dict. Splits (51850,) into per-layer tensors."""
    splits = [784*64, 64, 10*64, 10]
    parts = torch.split(flat, splits)
    return {
        "layer0.weight": parts[0].reshape(64, 784),
        "layer0.bias":   parts[1],
        "layer1.weight": parts[2].reshape(10, 64),
        "layer1.bias":   parts[3],
    }
```

**Shapes**: flat_w (51850,); orbit_flat (51850,); dict keys → (64,784), (64,), (10,64), (10,)

---

### L-5-3: `build_cross_orbit_pairs()` — same-property cross-orbit sampling

**Parent Epic**: A-5

```python
def build_cross_orbit_pairs(
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,  # (N, 3)
    base_indices: list[int],
    seed: int = 42,
) -> tuple[list[dict], list[int]]:
    """
    For each base model i, sample j ≠ i from same test_accuracy decile.

    Algorithm:
        acc = zoo_properties[:, 0]  # test_accuracy column
        quantiles = torch.quantile(acc, torch.linspace(0, 1, 11)[1:-1])  # 9 boundaries → 10 buckets
        decile_labels = torch.bucketize(acc, quantiles)  # (N,) ∈ {0,...,9}

        For each i in base_indices:
            same_decile_idx = (decile_labels == decile_labels[i]).nonzero().squeeze()  # (K,)
            candidates = same_decile_idx[same_decile_idx != i]  # exclude self
            j = candidates[rng.randint(0, len(candidates))]  # seed-controlled

    Returns: (cross_weight_list, cross_index_list)
    """
    ...
```

**Shapes**: acc (N,); decile_labels (N,); candidates variable-length 1D; cross_weight_list has n_pairs elements

---

### L-5-4: `compute_similarity_vectors()` — cosine similarity computation

**Parent Epic**: A-5

```python
def compute_similarity_vectors(
    emb_base:  torch.Tensor,   # (N, D) — base model embeddings
    emb_orbit: torch.Tensor,   # (N, D) — orbit member embeddings
    emb_cross: torch.Tensor,   # (N, D) — cross-orbit same-property embeddings
) -> dict[str, torch.Tensor]:
    """
    Compute pairwise cosine similarities.

    Algorithm:
        emb_base_n  = F.normalize(emb_base,  dim=-1, eps=1e-8)  # (N, D) L2-normalized
        emb_orbit_n = F.normalize(emb_orbit, dim=-1, eps=1e-8)
        emb_cross_n = F.normalize(emb_cross, dim=-1, eps=1e-8)

        within_sim = (emb_base_n * emb_orbit_n).sum(dim=-1)  # (N,) element-wise dot
        cross_sim  = (emb_base_n * emb_cross_n).sum(dim=-1)  # (N,)
        gap        = cross_sim - within_sim                    # (N,) positive = NFT NOT orbit-inv

    Returns:
        {
            "within_sim": Tensor (N,),   # cosine sim of base to orbit member
            "cross_sim":  Tensor (N,),   # cosine sim of base to cross-orbit pair
            "gap":        Tensor (N,),   # orbit_invariance_gap per pair
        }
    """
    import torch.nn.functional as F
    emb_base_n  = F.normalize(emb_base,  dim=-1, eps=1e-8)
    emb_orbit_n = F.normalize(emb_orbit, dim=-1, eps=1e-8)
    emb_cross_n = F.normalize(emb_cross, dim=-1, eps=1e-8)
    within_sim = (emb_base_n * emb_orbit_n).sum(dim=-1)
    cross_sim  = (emb_base_n * emb_cross_n).sum(dim=-1)
    gap        = cross_sim - within_sim
    return {"within_sim": within_sim, "cross_sim": cross_sim, "gap": gap}
```

**Shapes**: all inputs (N, 256); all outputs (N,)

---

### L-5-5: `evaluate_gate()` — gate evaluation across orbit types

**Parent Epic**: A-5

```python
def evaluate_gate(
    results_scaling: dict,   # from probe_orbit_invariance(orbit_type="scaling")
    results_signflip: dict,  # from probe_orbit_invariance(orbit_type="signflip")
    n_boot: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Aggregate per-type bootstrap CI; determine PASS/FAIL.

    Algorithm:
        For each orbit_type in [scaling, signflip]:
            gap = results[orbit_type]["gap"].numpy()
            ci = scipy.stats.bootstrap(
                (gap,), np.mean,
                confidence_level=0.95,
                n_resamples=n_boot,
                random_state=seed
            ).confidence_interval
            gate_pass[orbit_type] = ci.low > 0

        overall_pass = all(gate_pass.values())

    Returns:
        {
            "overall_pass": bool,
            "scaling": {"ci_low": float, "ci_high": float, "mean_gap": float, "gate_pass": bool,
                        "mean_within_sim": float, "mean_cross_sim": float},
            "signflip": {...},
        }
    """
    ...
```

---

## A-2 Subtasks: NFT Encoder Module (4 subtasks)

### L-2-1: `load_nft_encoder()` — checkpoint load with fallback

**Parent Epic**: A-2

```python
CHECKPOINT_PATH_DEFAULT = "../../h-e1/code/checkpoints/nft_condition_a.pt"
MNIST_MLP_ARCH = {
    "d_in": 784, "h": 64, "d_out": 10,
    "n_layers": 1,  # number of hidden layers (M=2 total including output)
}
NFT_CONFIG = {
    "d_model": 256,
    "n_heads": 8,
    "n_layers": 4,
    "dropout": 0.0,
}

def load_nft_encoder(
    checkpoint_path: str = CHECKPOINT_PATH_DEFAULT,
    device: str = "cpu",
) -> torch.nn.Module:
    """
    Load NFT Condition A encoder from checkpoint.

    Algorithm:
        1. Check os.path.exists(checkpoint_path)
        2. If exists:
            model = build_nft(MNIST_MLP_ARCH, NFT_CONFIG)
            state = torch.load(checkpoint_path, map_location=device)
            model.load_state_dict(state)
            model.eval()
            return model
        3. If missing:
            raise FileNotFoundError with path + instruction to run FR-0.3 training
            # Caller (main.py) handles fallback to train_nft_fallback()

    Returns: NFT module in eval mode on device
    """
    ...
```

---

### L-2-2: `build_nft()` — NFT architecture constructor

**Parent Epic**: A-2

```python
def build_nft(arch_spec: dict, nft_config: dict) -> torch.nn.Module:
    """
    Construct NFT for MNIST MLP zoo.

    Follows Zhou et al. 2023 weight tokenization scheme:
    - W1 (64×784): 64 row tokens of dim 784 → project to d_model via linear
    - b1 (64,): 64 scalar tokens
    - W2 (10×64): 10 row tokens of dim 64 → project to d_model
    - b2 (10,): 10 scalar tokens
    Total tokens per model: 64+64+10+10 = 148

    Transformer: TransformerEncoder(n_layers=4, d_model=256, n_heads=8)
    Pooling: mean over all tokens → (256,) embedding
    Property head: Linear(256, 3)

    Note: If using DeepMind NFT repo, use their NFT class directly:
        from nft import NFT
        return NFT(arch_spec=arch_spec, **nft_config)
    """
    ...
```

---

### L-2-3: `extract_embeddings()` — batched inference

**Parent Epic**: A-2

```python
def extract_embeddings(
    nft_encoder: torch.nn.Module,
    weights_list: list[dict],
    batch_size: int = 64,
    device: str = "cpu",
) -> torch.Tensor:
    """
    Extract fixed-dim embeddings from NFT for a list of model weight dicts.

    Algorithm:
        nft_encoder.eval()
        embeddings = []
        with torch.no_grad():
            for batch in batches(weights_list, batch_size):
                # Convert list of dicts to batched tensor format expected by NFT
                tokens = prepare_nft_tokens(batch)  # see L-2-4
                emb = nft_encoder.encode(tokens)    # (B, d_model) — mean-pooled
                embeddings.append(emb.cpu())
        return torch.cat(embeddings, dim=0)  # (N, d_model)

    Returns: Tensor (N, 256), float32, on CPU
    """
    ...
```

**Shape**: inputs — list of N weight dicts; output — (N, 256)

---

### L-2-4: `prepare_nft_tokens()` — weight dict → NFT token format

**Parent Epic**: A-2

```python
def prepare_nft_tokens(weights_batch: list[dict]) -> dict[str, torch.Tensor]:
    """
    Convert batch of per-layer weight dicts to NFT token format.

    For each model in batch:
        W1: (64, 784) → row-tokenize → (64, 784) tokens
        b1: (64,)     → (64, 1) tokens
        W2: (10, 64)  → row-tokenize → (10, 64) tokens
        b2: (10,)     → (10, 1) tokens

    Batch and project to d_model via learned embeddings (inside NFT).

    Returns dict with keys expected by NFT forward():
        {"W1": Tensor(B, 64, 784), "b1": Tensor(B, 64),
         "W2": Tensor(B, 10, 64),  "b2": Tensor(B, 10)}

    Note: exact key names depend on NFT implementation.
    If using DeepMind NFT: pass list[dict] directly (NFT handles tokenization internally).
    """
    B = len(weights_batch)
    W1 = torch.stack([w["layer0.weight"] for w in weights_batch])  # (B, 64, 784)
    b1 = torch.stack([w["layer0.bias"]   for w in weights_batch])  # (B, 64)
    W2 = torch.stack([w["layer1.weight"] for w in weights_batch])  # (B, 10, 64)
    b2 = torch.stack([w["layer1.bias"]   for w in weights_batch])  # (B, 10)
    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2}
```

**Shapes**: W1 (B,64,784); b1 (B,64); W2 (B,10,64); b2 (B,10)

---

## A-3 Subtasks: Oracle Orbit Pair Construction (2 subtasks)

### L-3-1: `verify_orbit_functional_equivalence()` — orbit correctness check

**Parent Epic**: A-3

```python
def verify_orbit_functional_equivalence(
    original: dict,
    orbit_member: dict,
    test_input: torch.Tensor = None,  # (batch_size, 784)
    tol: float = 1e-4,
) -> bool:
    """
    Verify that original and orbit_member produce same output on test_input.

    Algorithm:
        If test_input is None: generate random (64, 784) input, seed=0
        out_orig  = forward_mlp(original, test_input)      # (B, 10)
        out_orbit = forward_mlp(orbit_member, test_input)  # (B, 10)
        max_delta = (out_orig - out_orbit).abs().max()
        return max_delta < tol

    Used during orbit pair construction for sanity check (not in hot path).
    """
    ...

def forward_mlp(weights: dict, x: torch.Tensor) -> torch.Tensor:
    """2-layer MLP forward pass: ReLU(x @ W1.T + b1) @ W2.T + b2."""
    h = torch.relu(x @ weights["layer0.weight"].T + weights["layer0.bias"])
    return h @ weights["layer1.weight"].T + weights["layer1.bias"]
```

---

### L-3-2: `sample_base_models()` — seed-controlled base model sampling

**Parent Epic**: A-3

```python
def sample_base_models(
    zoo_weights: list[dict],
    n: int = 1000,
    seed: int = 42,
) -> tuple[list[int], list[dict]]:
    """
    Sample n models from zoo without replacement.

    Returns: (base_indices, base_weight_list)
    base_indices: list[int] — indices into zoo_weights, used for cross-orbit sampling
    base_weight_list: list[dict] — corresponding weight dicts
    """
    rng = torch.Generator().manual_seed(seed)
    idx = torch.randperm(len(zoo_weights), generator=rng)[:n].tolist()
    return idx, [zoo_weights[i] for i in idx]
```

---

## A-4 Subtasks: Cross-Orbit Pair Sampling (2 subtasks)

### L-4-1: `compute_accuracy_deciles()` — decile bucketing

**Parent Epic**: A-4

```python
def compute_accuracy_deciles(
    zoo_properties: torch.Tensor,  # (N, 3)
) -> torch.Tensor:
    """
    Bucket test_accuracy into 10 deciles.

    Returns: decile_labels (N,) ∈ {0, ..., 9}

    Algorithm:
        acc = zoo_properties[:, 0]
        boundaries = torch.quantile(acc, torch.linspace(0, 1, 11)[1:-1])  # 9 boundaries
        return torch.bucketize(acc, boundaries)
    """
    acc = zoo_properties[:, 0]
    boundaries = torch.quantile(acc, torch.linspace(0, 1, 11, device=acc.device)[1:-1])
    return torch.bucketize(acc, boundaries)
```

**Shapes**: zoo_properties (N,3); acc (N,); boundaries (9,); return (N,)

---

### L-4-2: `sample_cross_pair()` — single cross-pair index selection

**Parent Epic**: A-4

```python
def sample_cross_pair(
    base_idx: int,
    decile_labels: torch.Tensor,  # (N,)
    rng: torch.Generator,
) -> int:
    """
    Find j ≠ base_idx in same decile as base_idx. Seed-controlled.

    Algorithm:
        target_decile = decile_labels[base_idx]
        same_decile = (decile_labels == target_decile).nonzero(as_tuple=True)[0]
        candidates = same_decile[same_decile != base_idx]
        if len(candidates) == 0:
            raise ValueError(f"No cross-pair candidates for model {base_idx} in decile {target_decile}")
        k = torch.randint(len(candidates), (1,), generator=rng).item()
        return candidates[k].item()
    """
    ...
```

---

## A-10 Subtask: Main Runner (1 subtask)

### L-10-1: `verify_probe_activated()` — mechanism activation check

**Parent Epic**: A-10

```python
def verify_probe_activated(
    within_sim: torch.Tensor,
    cross_sim: torch.Tensor,
    n_orbit_pairs_constructed: int,
) -> tuple[bool, dict]:
    """
    Validate that the probing mechanism is working correctly.

    Algorithm:
        indicators = {
            "pairs_constructed": n_orbit_pairs_constructed == 1000,
            "shapes_match": within_sim.shape == cross_sim.shape,
            "gap_measurable": (cross_sim - within_sim).abs().mean() > 0.001,
            "no_degenerate_sims": within_sim.mean() < 0.99,  # not collapsed to 1.0
        }
        success = all(indicators.values())
        gap = (cross_sim - within_sim).mean().item()
        print(f"[VERIFY] Orbit invariance gap: {gap:.4f} (positive = NFT NOT orbit-inv)")
        return success, indicators

    Raise RuntimeError if success is False (mechanism not activated).
    """
    ...
```

---

## Pseudo-code: Full Main Flow

```python
# main.py high-level flow
def run(n_orbit_pairs=1000, seed=42, checkpoint_path=CHECKPOINT_PATH_DEFAULT,
        results_path="results.json", device="cpu"):

    # 1. Load zoo
    zoo_weights = load_zoo("schurholt/model_zoos_dataset", "mnist", "train+validation+test")
    assert len(zoo_weights) >= 10000, "v2 requires full 50k zoo"  # pre-flight check
    zoo_properties = extract_properties(zoo_weights)  # (N, 3) tensor

    # 2. Load NFT
    try:
        nft = load_nft_encoder(checkpoint_path, device)
    except FileNotFoundError:
        nft = train_nft_fallback(zoo_weights, zoo_properties)
    print("✓ NFT loaded. Embedding dim: 256")

    # 3. Probe scaling orbits
    results_scaling  = probe_orbit_invariance(nft, zoo_weights, zoo_properties,
                                              orbit_type="scaling",  n_pairs=n_orbit_pairs, seed=seed)
    # 4. Probe sign-flip orbits
    results_signflip = probe_orbit_invariance(nft, zoo_weights, zoo_properties,
                                              orbit_type="signflip", n_pairs=n_orbit_pairs, seed=seed)

    # 5. Mechanism verification
    ok, indicators = verify_probe_activated(results_scaling["within_sim"],
                                            results_scaling["cross_sim"], n_orbit_pairs)
    if not ok: raise RuntimeError(f"Probe failed activation: {indicators}")

    # 6. Gate evaluation
    gate = evaluate_gate(results_scaling, results_signflip, n_boot=1000, seed=seed)

    # 7. Figures
    generate_all_figures(results_scaling, results_signflip, zoo_properties, gate)

    # 8. Results
    results = build_results_dict(gate, results_scaling, results_signflip)
    write_json(results_path, results)

    print(f"\n{'PASS' if gate['overall_pass'] else 'FAIL'}: orbit_invariance_gap CI includes 0: "
          f"scaling CI=[{gate['scaling']['ci_low']:.4f}, {gate['scaling']['ci_high']:.4f}]")
    return results
```
