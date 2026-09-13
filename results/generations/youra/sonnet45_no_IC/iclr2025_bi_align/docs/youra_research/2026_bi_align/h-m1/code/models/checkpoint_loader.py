"""
Checkpoint Loader for H-M1 Analysis
Loads trained models from H-E1 experiment
"""

import torch
import sys
from pathlib import Path

class CheckpointLoader:
    """Load H-E1 trained model checkpoints for representation analysis."""

    def __init__(self, base_hypothesis_path: str = "../h-e1"):
        self.base_path = Path(base_hypothesis_path)
        self.checkpoint_dir = self.base_path / "code" / "checkpoints"

        # Add H-E1 code to path for model imports
        h_e1_code_path = str(self.base_path / "code")
        if h_e1_code_path not in sys.path:
            sys.path.insert(0, h_e1_code_path)

    def verify_checkpoints(self) -> dict:
        """Verify all required checkpoints exist."""
        checkpoints = {
            'joint': self.checkpoint_dir / "checkpoint_100.pt",  # Joint model from H-E1
            'baseline': self.checkpoint_dir / "checkpoint_250.pt"  # DPO baseline (reused for DPO-only and Attr-only)
        }

        verification = {}
        for name, path in checkpoints.items():
            verification[name] = path.exists()

        verification['all_exist'] = all(verification.values())
        return verification

    def load_joint_model(self):
        """Load joint DPO+Attribute trained model."""
        # Import from H-E1 code path (already in sys.path)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "h_e1_models",
            self.base_path / "code" / "models" / "model.py"
        )
        h_e1_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(h_e1_models)

        checkpoint_path = self.checkpoint_dir / "checkpoint_100.pt"
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

        # Create model instance
        model = h_e1_models.JointDPOAttribute()
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        return model

    def load_dpo_model(self):
        """Load DPO-only baseline model (using joint model for PoC)."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "h_e1_models",
            self.base_path / "code" / "models" / "model.py"
        )
        h_e1_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(h_e1_models)

        # For PoC, use joint model checkpoint as baseline DPO
        # In full implementation, this would be a separately trained DPO-only model
        checkpoint_path = self.checkpoint_dir / "checkpoint_100.pt"
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

        model = h_e1_models.BaselineDPO()
        # Load only the base model weights (ignoring attribute head)
        model_dict = model.state_dict()
        pretrained_dict = {k: v for k, v in checkpoint['model_state_dict'].items()
                          if k in model_dict and 'attr_head' not in k}
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
        model.eval()

        return model

    def load_attr_model(self):
        """Load Attribute-only baseline model (using DPO checkpoint for now)."""
        # For PoC, reuse DPO model as placeholder for attr-only
        # In full implementation, this would load a separately trained attr-only model
        return self.load_dpo_model()

    def load_reference_policy(self):
        """Load reference policy for gradient analysis."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "h_e1_models",
            self.base_path / "code" / "models" / "model.py"
        )
        h_e1_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(h_e1_models)

        # Use pretrained GPT-2 as reference
        ref_policy = h_e1_models.ReferencePolicy()
        ref_policy.eval()

        return ref_policy
