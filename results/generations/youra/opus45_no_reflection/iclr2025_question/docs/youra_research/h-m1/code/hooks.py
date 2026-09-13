"""HiddenStateExtractor: Context-managed hook attach/detach for non-intrusive extraction."""

import torch


class HiddenStateExtractor:
    """
    Extract hidden states from transformer layers without affecting generation.
    Context-managed: hooks registered on __enter__, removed on __exit__.
    Non-intrusive: hook returns None, only stores detached copy.
    """

    def __init__(self, model, layer_indices: list = None):
        self.model = model
        if layer_indices is None:
            layer_indices = [19]
        self.layer_indices = layer_indices
        self.hidden_states = {}
        self.handles = []

    def _create_hook(self, layer_idx: int):
        def hook(module, input, output):
            hidden = output[0] if isinstance(output, tuple) else output
            self.hidden_states[layer_idx] = hidden.detach().cpu()
            return None
        return hook

    def __enter__(self):
        self.hidden_states.clear()
        for idx in self.layer_indices:
            layer = self.model.model.layers[idx]
            handle = layer.register_forward_hook(self._create_hook(idx))
            self.handles.append(handle)
        return self

    def __exit__(self, *exc):
        for handle in self.handles:
            handle.remove()
        self.handles.clear()
