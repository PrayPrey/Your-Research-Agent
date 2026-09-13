"""SSM state monitoring via forward hooks."""

import torch
import logging
from typing import Dict, Any


class SSMStateHook:
    """Hook for capturing SSM intermediate states."""

    def __init__(self, name: str):
        self.name = name
        self.outputs = []

    def hook_fn(self, module, input, output):
        """Forward hook function."""
        if isinstance(output, torch.Tensor):
            has_nan = torch.isnan(output).any().item()
            has_inf = torch.isinf(output).any().item()

            self.outputs.append({
                'has_nan': has_nan,
                'has_inf': has_inf,
                'shape': list(output.shape),
                'mean': output.mean().item() if not (has_nan or has_inf) else None,
                'std': output.std().item() if not (has_nan or has_inf) else None
            })

    def reset(self):
        """Reset captured outputs."""
        self.outputs = []


class SSMStateMonitor:
    """Monitor SSM internal states during forward pass."""

    def __init__(self):
        self.hooks = []
        self.hook_handles = []
        self.logger = logging.getLogger(__name__)

    def register_hooks(self, model) -> int:
        """Register forward hooks on Mamba blocks."""
        hook_count = 0

        for name, module in model.named_modules():
            if 'mamba' in name.lower() or 'mixer' in name.lower():
                hook = SSMStateHook(name)
                handle = module.register_forward_hook(hook.hook_fn)

                self.hooks.append(hook)
                self.hook_handles.append(handle)
                hook_count += 1

        self.logger.info(f"Registered {hook_count} SSM state hooks")
        return hook_count

    def validate_states(self) -> Dict[str, Any]:
        """Validate captured SSM states."""
        all_valid = True
        issues = []

        for hook in self.hooks:
            for idx, output in enumerate(hook.outputs):
                if output['has_nan']:
                    all_valid = False
                    issues.append(f"{hook.name} (call {idx}): NaN detected")
                if output['has_inf']:
                    all_valid = False
                    issues.append(f"{hook.name} (call {idx}): Inf detected")

        return {
            'passed': all_valid,
            'num_hooks': len(self.hooks),
            'total_captures': sum(len(hook.outputs) for hook in self.hooks),
            'issues': issues[:10]
        }

    def remove_hooks(self):
        """Remove all registered hooks."""
        for handle in self.hook_handles:
            handle.remove()

        self.hooks = []
        self.hook_handles = []
        self.logger.info("Removed all SSM state hooks")

    def reset(self):
        """Reset all captured outputs."""
        for hook in self.hooks:
            hook.reset()
