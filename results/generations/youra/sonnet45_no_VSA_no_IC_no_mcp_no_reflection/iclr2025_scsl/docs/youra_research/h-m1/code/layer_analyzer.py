"""Layer-wise neuron correlation analyzer."""
import torch
import numpy as np
from scipy.stats import pearsonr, ttest_ind
from typing import Dict, List, Tuple


class LayerNeuronAnalyzer:
    """Analyze layer-wise neuron correlations with spurious features."""

    def __init__(self, model: torch.nn.Module, layer_names: List[str]):
        self.model = model
        self.layer_names = layer_names
        self.activations: Dict[str, torch.Tensor] = {}
        self._register_hooks()

    def _register_hooks(self):
        """Register forward hooks for activation extraction."""
        def get_activation(name: str):
            def hook(module, input, output):
                self.activations[name] = output.detach()
            return hook

        for layer_name in self.layer_names:
            layer = getattr(self.model, layer_name)
            layer.register_forward_hook(get_activation(layer_name))

    def compute_layer_correlations(
        self,
        dataloader: torch.utils.data.DataLoader,
        spurious_labels: np.ndarray,
        device: str = 'cuda'
    ) -> Dict[str, np.ndarray]:
        """Compute per-neuron Pearson correlation with spurious feature."""
        layer_activations: Dict[str, List[torch.Tensor]] = {
            name: [] for name in self.layer_names
        }

        self.model.eval()
        with torch.no_grad():
            for batch_x, _, _ in dataloader:
                batch_x = batch_x.to(device)
                _ = self.model(batch_x)

                for layer_name in self.layer_names:
                    act = self.activations[layer_name]
                    # Spatial pooling: (B, C, H, W) → (B, C)
                    if act.dim() == 4:
                        pooled = act.mean(dim=(2, 3))
                    else:
                        pooled = act
                    layer_activations[layer_name].append(pooled.cpu())

        # Compute per-neuron correlations
        layer_rho_j: Dict[str, np.ndarray] = {}
        for layer_name, acts in layer_activations.items():
            acts_array = torch.cat(acts, dim=0).numpy()

            # Per-neuron correlation with spurious labels
            rho_j = np.array([
                pearsonr(acts_array[:, i], spurious_labels)[0]
                for i in range(acts_array.shape[1])
            ])
            layer_rho_j[layer_name] = rho_j

        return layer_rho_j

    def test_layer_consistency(
        self,
        layer_rho_j: Dict[str, np.ndarray],
        early_layers: List[str],
        late_layers: List[str]
    ) -> Tuple[float, float, Dict[str, float]]:
        """Test if early layers have higher spurious correlation than late."""
        # Group correlations
        early = np.concatenate([layer_rho_j[name] for name in early_layers])
        late = np.concatenate([layer_rho_j[name] for name in late_layers])

        # Statistical test
        t_stat, p_value = ttest_ind(early, late, alternative='greater')

        # Per-layer means
        layer_means = {name: np.mean(rho) for name, rho in layer_rho_j.items()}

        return t_stat, p_value, layer_means
