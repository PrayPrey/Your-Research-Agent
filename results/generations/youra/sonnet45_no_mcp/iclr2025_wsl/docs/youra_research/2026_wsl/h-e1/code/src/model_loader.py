"""ModelLoader: Load pretrained ImageNet models from torchvision"""

import torch
import torchvision.models as models
from typing import Dict
import torch.nn as nn


class ModelLoader:
    """Load pretrained ImageNet models from torchvision."""

    def __init__(self, shallow_names=None, deep_names=None):
        """Initialize model loader with model name lists."""
        self.shallow_names = shallow_names or [
            "resnet18", "resnet34", "vgg11", "vgg13", "vgg16",
            "vgg19", "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
        ]
        self.deep_names = deep_names or [
            "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
            "densenet201", "wide_resnet50_2", "wide_resnet101_2",
            "resnext50_32x4d", "resnext101_32x8d"
        ]

    def load_shallow_models(self) -> Dict[str, nn.Module]:
        """Load shallow models (≤34 layers). Returns: {name: model}"""
        models_dict = {}
        for i, name in enumerate(self.shallow_names, 1):
            print(f"Loading shallow model {i}/{len(self.shallow_names)}: {name}")
            try:
                model = getattr(models, name)(pretrained=True)
                model.eval()  # Set to evaluation mode
                models_dict[name] = model
            except Exception as e:
                print(f"Warning: Failed to load {name}: {e}")
        return models_dict

    def load_deep_models(self) -> Dict[str, nn.Module]:
        """Load deep models (≥50 layers). Returns: {name: model}"""
        models_dict = {}
        for i, name in enumerate(self.deep_names, 1):
            print(f"Loading deep model {i}/{len(self.deep_names)}: {name}")
            try:
                model = getattr(models, name)(pretrained=True)
                model.eval()  # Set to evaluation mode
                models_dict[name] = model
            except Exception as e:
                print(f"Warning: Failed to load {name}: {e}")
        return models_dict

    def load_all_models(self) -> tuple:
        """Load all 20 models. Returns: (shallow_dict, deep_dict)"""
        print(f"\n{'='*60}")
        print("Loading Pretrained Models")
        print(f"{'='*60}")

        shallow_models = self.load_shallow_models()
        deep_models = self.load_deep_models()

        print(f"\n✓ Loaded {len(shallow_models)} shallow models")
        print(f"✓ Loaded {len(deep_models)} deep models")
        print(f"✓ Total: {len(shallow_models) + len(deep_models)} models")

        return shallow_models, deep_models
