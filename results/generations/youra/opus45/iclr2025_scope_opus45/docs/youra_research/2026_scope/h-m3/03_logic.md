# Logic: H-M3 — Eigenmode Energy Redistribution via Projection-Only LoRA

Applied: PyTorch forward hook hidden state capture pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual code (direct file read; Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/20260327_scope/h-m2/code/model.py`
**Relevant Symbols**:
- `MambaProbe.__init__(self, config: ExperimentConfig)` — loads model via `AutoModelForCausalLM.from_pretrained`
- `MambaProbe.load_model(self)` — sets `self.model`, `self.tokenizer`; exposes `backbone.layers`
- `MambaProbe.get_model(self)` — returns raw model for LoRA wrapping
- `MambaProbe.get_tokenizer(self)` — returns tokenizer
- `MambaProbe.extract_layer_A_log(self)` — `layer.mixer.A_log.detach().float()` per layer → List[Tensor[d_inner, d_state]]
- `LoRAAdapter.__init__(self, model, config: ExperimentConfig)`
- `LoRAAdapter.apply(self)` — returns PEFT-wrapped model
- `LoRAAdapter.verify_mechanism(self)` — asserts A_log frozen, proj LoRA trainable
- A_log access path: `model.backbone.layers[i].mixer.A_log`
- Eigenvalue formula: `torch.exp(-torch.exp(a_log.float()))` → [d_inner, d_state]

---

## External Dependencies API

### API Signatures (From Actual Code: h-m2/code/model.py)

```python
class MambaProbe:
    def __init__(self, config: ExperimentConfig) -> None: ...
    def load_model(self) -> None: ...
    def get_model(self): ...          # returns raw AutoModelForCausalLM
    def get_tokenizer(self): ...      # returns tokenizer
    def extract_layer_A_log(self) -> List[Tensor]: ...
    # Each tensor: [d_inner, d_state] = [4096, 16]

class LoRAAdapter:
    def __init__(self, model, config: ExperimentConfig) -> None: ...
    def apply(self):  ...             # returns PEFT-wrapped model
    def verify_mechanism(self) -> bool: ...
```

**Verified from**: `h-m2/code/model.py` (actual implementation)

### API Signatures (From Actual Code: h-m2/code/train.py)

```python
def load_wikitext103_train(config: ExperimentConfig, tokenizer) -> Dataset: ...
def build_dataloader(tokenized_dataset, config: ExperimentConfig) -> DataLoader: ...
def build_optimizer_and_scheduler(
    model, config: ExperimentConfig, num_training_steps: int
) -> Tuple[torch.optim.Optimizer, Any]: ...
def train(
    model, dataloader: DataLoader, optimizer, scheduler,
    config: ExperimentConfig
) -> List[float]: ...
```

---

## A-4: EigenmodeEnergyAnalyzer [Complexity: 17, Budget: 4 subtasks]

Applied: PyTorch forward hook hidden state capture pattern

### API Signatures

```python
class EigenmodeEnergyAnalyzer:
    def __init__(self, model, config: "ExperimentConfig") -> None:
        """Store model/config; init hooks=[], hidden_states=[]."""
        # self.model = model  (PEFT-wrapped or raw)
        # self.config = config
        # self.hooks: List[RemovableHook] = []
        # self.hidden_states: List[Tensor] = []  # appended per layer per forward
        ...

    def register_hooks(self) -> None:
        """Register forward hook on each layer.mixer; appends to self.hooks."""
        # for layer in self.model.backbone.layers:
        #     h = layer.mixer.register_forward_hook(self._capture_state)
        #     self.hooks.append(h)
        ...

    def clear_hooks(self) -> None:
        """Remove all hooks; clear self.hidden_states."""
        # for h in self.hooks: h.remove()
        # self.hooks.clear(); self.hidden_states.clear()
        ...

    def _capture_state(self, module, input, output) -> None:
        """Hook callback; appends output tensor detached to self.hidden_states."""
        # self.hidden_states.append(output.detach().float())
        # output shape from layer.mixer: [B, L, d_model] = [B, L, 2048]
        ...

    def measure_energy(self, model, input_ids: Tensor) -> dict:
        """Run forward pass (no_grad); compute energy; clear hidden_states after.

        Args:
            model: same as self.model (passed for interface clarity)
            input_ids: [B, L] token ids

        Returns:
            {
              'per_layer': List[float],            # slow_fraction per layer, len=48
              'slow_fraction': float,              # global mean of per_layer
              'per_layer_total_energy': List[float],  # total ||h||^2 per layer
            }
        """
        ...

    def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> dict:
        """Compute ΔE metrics from two measure_energy() result dicts.

        Returns:
            {
              'delta_slow_fraction': float,     # post - pre global slow_fraction
              'delta_e_nats': float,            # -log(1 - min(|delta|, 0.99))
              'gate_pass': bool,                # delta_e_nats > config.delta_e_gate_threshold
              'per_layer_delta': List[float],   # per-layer post - pre slow_fraction
            }
        """
        ...

    def get_eigenvalues_per_layer(self) -> List[Tensor]:
        """Compute λ = exp(-exp(A_log)) per layer from frozen A_log.

        Returns: List[Tensor[d_inner, d_state]], len=48
        """
        # for layer in self.model.backbone.layers:
        #     a_log = layer.mixer.A_log.detach().float()  # [d_inner, d_state]
        #     lam = torch.exp(-torch.exp(a_log))          # [d_inner, d_state]
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | B=batch, L=seq_len (256) |
| output (hook) | [B, L, d_model] | d_model=2048 for Mamba-1.4B |
| A_log | [d_inner, d_state] | [4096, 16] per layer |
| eigenvalues | [d_inner, d_state] | [4096, 16]; λ = exp(-exp(A_log)) |
| slow_mask | [d_inner, d_state] | bool; |λ| > 0.99 |
| mode_energy | [d_model] | ||h||^2 summed over B and L |
| per_layer slow_fraction | scalar | slow_energy / total_energy |

### Pseudo-code: measure_energy

```
register_hooks() if not already done
with torch.no_grad():
    model(input_ids)           # triggers _capture_state for 48 layers
# self.hidden_states now has 48 tensors [B, L, d_model]

per_layer = []
per_layer_total = []
for i, layer in enumerate(model.backbone.layers):
    a_log = layer.mixer.A_log.detach().float()      # [d_inner, d_state]
    eigs  = exp(-exp(a_log))                        # [d_inner, d_state]
    slow_mask = eigs.abs() > config.slow_mode_threshold  # [d_inner, d_state]

    h = self.hidden_states[i]                       # [B, L, d_model]
    # project hidden to d_inner dim (first d_inner channels)
    h_inner = h[..., :d_inner]                      # [B, L, d_inner]
    # energy per d_inner channel: sum over B and L
    ch_energy = (h_inner ** 2).sum(dim=(0, 1))      # [d_inner]

    # slow_mask per channel: any slow mode in that channel
    slow_ch = slow_mask.any(dim=1)                  # [d_inner] bool
    slow_energy = ch_energy[slow_ch].sum().item()
    total_energy = ch_energy.sum().item()
    per_layer.append(slow_energy / (total_energy + 1e-8))
    per_layer_total.append(total_energy)

self.hidden_states.clear()   # free GPU memory immediately
return {
    'per_layer': per_layer,
    'slow_fraction': mean(per_layer),
    'per_layer_total_energy': per_layer_total,
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | hook_registration | `register_hooks`, `clear_hooks`, `_capture_state` |
| L-4-2 | eigenvalue_computation | `get_eigenvalues_per_layer`, slow_mask construction |
| L-4-3 | energy_measurement | `measure_energy` full implementation with channel projection |
| L-4-4 | delta_e_computation | `compute_delta_e` nats formula + gate evaluation |

---

## A-5: compute_delta_e [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch

### API Signatures

```python
# Part of EigenmodeEnergyAnalyzer.compute_delta_e (detailed spec)

def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> dict:
    """
    pre_energy, post_energy: output of measure_energy()
    Returns delta metrics dict.
    """
    # per_layer_delta[i] = post['per_layer'][i] - pre['per_layer'][i]
    # delta_slow_fraction = post['slow_fraction'] - pre['slow_fraction']
    # delta_e_nats = -log(1 - min(|delta_slow_fraction|, 0.99))
    # gate_pass = delta_e_nats > self.config.delta_e_gate_threshold (0.1)
    ...
```

### Pseudo-code

```
per_layer_delta = [post[i] - pre[i] for i in range(48)]
delta = post_slow_fraction - pre_slow_fraction
delta_e_nats = -math.log(1 - min(abs(delta), 0.99))
gate_pass = delta_e_nats > config.delta_e_gate_threshold
return {
    'delta_slow_fraction': delta,
    'delta_e_nats': delta_e_nats,
    'gate_pass': gate_pass,
    'per_layer_delta': per_layer_delta,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | nats_formula | implement -log(1 - min(|ΔE|, 0.99)) with edge case guard |
| L-5-2 | gate_evaluation | threshold comparison + per_layer_delta assembly |

---

## A-10: Orchestrator (run_experiment.py) [Complexity: 14, Budget: 3 subtasks]

Applied: Standard PyTorch pipeline pattern

### API Signatures

```python
def main() -> None:
    """Full pipeline: load → LoRA → pre-energy → train → post-energy → ΔE → PPL → save."""
    ...

def _load_model_and_lora(config: "ExperimentConfig") -> Tuple[Any, Any, Any]:
    """Load MambaProbe, apply LoRAAdapter, verify mechanism.

    Returns:
        (probe, lora_adapter, model)  # model is PEFT-wrapped
    """
    ...

def _measure_energy_pass(
    analyzer: "EigenmodeEnergyAnalyzer",
    model,
    eval_dataloader: "DataLoader",
    config: "ExperimentConfig",
    label: str,
) -> dict:
    """Run analyzer over eval_dataloader batches; average energy dicts.

    Args:
        analyzer: EigenmodeEnergyAnalyzer (hooks registered inside)
        model: PEFT-wrapped Mamba model
        eval_dataloader: batches of input_ids
        config: for device
        label: "pre" or "post" for logging

    Returns:
        averaged measure_energy dict over all batches
    """
    ...
```

### Pseudo-code: main()

```
1. config = ExperimentConfig()
2. probe, lora_adapter, model = _load_model_and_lora(config)
3. tokenizer = probe.get_tokenizer()
4. analyzer = EigenmodeEnergyAnalyzer(model, config)

5. eval_ds = load_wikitext103_eval(config, tokenizer)
   eval_dl = build_dataloader(eval_ds, config)

6. # Pre-training energy
   pre_energy = _measure_energy_pass(analyzer, model, eval_dl, config, "pre")

7. # Training
   train_ds = load_wikitext103_train(config, tokenizer)
   train_dl = build_dataloader(train_ds, config)
   num_steps = len(train_dl) * config.num_epochs
   optimizer, scheduler = build_optimizer_and_scheduler(model, config, num_steps)
   losses = train(model, train_dl, optimizer, scheduler, config)

8. # Post-training energy
   post_energy = _measure_energy_pass(analyzer, model, eval_dl, config, "post")

9. delta_e_result = analyzer.compute_delta_e(pre_energy, post_energy)
   eigenvalues = analyzer.get_eigenvalues_per_layer()

10. ppl = compute_perplexity(model, eval_ds, config)

11. # Figures
    plot_gate_metrics(delta_e_result['delta_e_nats'], config.delta_e_gate_threshold, config.figures_dir)
    plot_energy_distribution(pre_energy, post_energy, config.figures_dir)
    plot_per_layer_slow_fraction(pre_energy, post_energy, config.figures_dir)
    plot_eigenvalue_energy_scatter(eigenvalues, pre_energy, post_energy, config.figures_dir)
    plot_training_loss(losses, config.figures_dir)

12. results = {
        'delta_e_nats': delta_e_result['delta_e_nats'],
        'gate_pass': delta_e_result['gate_pass'],
        'pre_slow_fraction': pre_energy['slow_fraction'],
        'post_slow_fraction': post_energy['slow_fraction'],
        'perplexity': ppl,
    }
    save_results(results, config.results_path)
    print(f"Gate: {'PASS' if delta_e_result['gate_pass'] else 'FAIL'} "
          f"(ΔE={delta_e_result['delta_e_nats']:.4f} nats)")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | model_load_lora | `_load_model_and_lora`: MambaProbe + LoRAAdapter + verify |
| L-10-2 | energy_measurement_loop | `_measure_energy_pass`: batch loop + average dict |
| L-10-3 | pipeline_wiring | `main()`: wire all steps, figures, results.yaml |

---

## Implementation Notes (Critical)

1. **Hook output vs SSM state**: `layer.mixer` forward returns `[B, L, d_model]` (processed sequence), not raw d_state. Energy is computed by projecting to d_inner channels (first 4096 of d_model=2048 for Mamba-1.4B; actually d_inner = 2 * d_model = 4096). Use `h[..., :d_inner]` as proxy for inner state channelwise energy.

2. **slow_mask channel mapping**: `slow_mask` is `[d_inner, d_state]`; collapse to per-channel with `slow_mask.any(dim=1)` → `[d_inner]` for indexing channel energies.

3. **float32 for energy**: cast all tensors to float32 before energy computation even if model runs in float16.

4. **clear_hooks after each pass**: call `analyzer.clear_hooks()` immediately after each `measure_energy` call to avoid GPU OOM from 48-layer accumulated tensors.

5. **A_log access in PEFT model**: both raw and PEFT-wrapped model expose `model.backbone.layers[i].mixer.A_log` directly (verified from H-M2 `extract_layer_A_log`).
