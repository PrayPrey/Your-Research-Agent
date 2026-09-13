# h-m2 Logic Design

**Complexity**: All tasks Low. Budget: 0 subtasks (no decomposition).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1)
**Status**: `h-m1/code/` directory does not exist yet (code not generated for base hypothesis at design time). Serena `find_symbol`/`get_symbols_overview` returned no files. Falling back to `h-m1/03_logic.md` (spec) as the API reference — this is a fallback, not a violation, since no actual code exists to verify against.
**Analyzed Path**: `docs/youra_research/h-m1/code/` (empty/non-existent)
**Relevant Symbols**: None found (no code present)

**Note for Phase 4 Coder**: If h-m1 code exists by the time this hypothesis is implemented, verify signatures below against actual `h-m1/code/` before use — parameter names may drift from spec.

---

## A-1: Ablation Module [Complexity: Low, Budget: 0]

**Applied**: Standard PyTorch (module wrapping / flag-gated forward)

### API Signatures

```python
class AblationWrapper(nn.Module):
    def __init__(self, base_model: nn.Module, ablate: str = "none"):
        """ablate: 'none' | component name to disable, e.g. 'attention', 'graph_conv'."""
        ...

    def forward(self, x: Tensor, edge_index: Optional[Tensor] = None) -> Tensor:
        """x: [N, F] -> [N, C]. Routes through base_model with ablated component bypassed."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [N, F] | Input node features |
| edge_index | [2, E] | Graph connectivity (optional per base model) |
| out | [N, C] | Class logits |

### Subtasks [0/0 used]

None — Low complexity, single forward pass, no decomposition needed.

---

## External Dependencies (Base Hypothesis h-m1)

### API Signatures (From h-m1 Spec — code not yet generated)

```python
# From: h-m1/03_logic.md (SPEC — verify against h-m1/code/ when available)
class BaseModel(nn.Module):
    def forward(self, x: Tensor, edge_index: Optional[Tensor] = None) -> Tensor:
        """Forward pass. x: [N, F] -> [N, C]"""
        ...
```

**Verified from**: `h-m1/03_logic.md` (spec fallback — `h-m1/code/` not present). Re-verify with Serena once base code exists.
