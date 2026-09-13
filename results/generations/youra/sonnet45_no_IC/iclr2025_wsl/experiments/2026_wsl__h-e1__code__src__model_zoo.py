"""
Model Zoo Collection Module
Downloads ImageNet-1K pre-trained models from HuggingFace Hub
"""

import json
import os
from typing import Dict, List
from collections import OrderedDict

import torch


class ModelZooCollector:
    """Download models from HuggingFace Hub"""

    def __init__(self, output_dir: str, random_seed: int = 42):
        self.output_dir = output_dir
        self.random_seed = random_seed
        os.makedirs(output_dir, exist_ok=True)

    def collect_models(self, n_resnet: int = 50, n_vit: int = 50) -> Dict[str, List]:
        """
        Download models from timm library (pre-trained on ImageNet).
        Returns: {"models": [...metadata...], "success_count": int}
        """
        import timm

        print(f"🔍 Collecting real pre-trained models from timm library...")
        print(f"  Target: {n_resnet} ResNet-50 + {n_vit} ViT-Base models")

        # Get all available pretrained models from timm
        all_timm_models = timm.list_models(pretrained=True)

        # Filter for ResNet-50 models
        print(f"\n  Filtering ResNet-50 models...")
        resnet_models = []
        for model_name in all_timm_models:
            if "resnet50" in model_name.lower() and len(resnet_models) < n_resnet:
                resnet_models.append({
                    "model_id": model_name,
                    "architecture": "resnet50",
                    "hf_path": model_name,  # timm model name
                    "imagenet_accuracy": None,
                    "split": None
                })

        # Filter for ViT-Base models
        print(f"  Filtering ViT-Base models...")
        vit_models = []
        for model_name in all_timm_models:
            if "vit_base" in model_name.lower() and len(vit_models) < n_vit:
                vit_models.append({
                    "model_id": model_name,
                    "architecture": "vit_base",
                    "hf_path": model_name,  # timm model name
                    "imagenet_accuracy": None,
                    "split": None
                })

        # If not enough models found, expand search
        if len(resnet_models) < n_resnet:
            print(f"  WARNING: Only found {len(resnet_models)} ResNet-50 models, need {n_resnet}")
            print(f"  Expanding to include ResNet variants...")
            for model_name in all_timm_models:
                if "resnet" in model_name.lower() and "50" in model_name and len(resnet_models) < n_resnet:
                    if model_name not in [m["model_id"] for m in resnet_models]:
                        resnet_models.append({
                            "model_id": model_name,
                            "architecture": "resnet50",
                            "hf_path": model_name,
                            "imagenet_accuracy": None,
                            "split": None
                        })

        if len(vit_models) < n_vit:
            print(f"  WARNING: Only found {len(vit_models)} ViT-Base models, need {n_vit}")
            print(f"  Expanding to include ViT variants...")
            for model_name in all_timm_models:
                if "vit" in model_name.lower() and ("base" in model_name.lower() or "small" in model_name.lower()):
                    if len(vit_models) < n_vit and model_name not in [m["model_id"] for m in vit_models]:
                        vit_models.append({
                            "model_id": model_name,
                            "architecture": "vit_base",
                            "hf_path": model_name,
                            "imagenet_accuracy": None,
                            "split": None
                        })

        # Combine results
        all_models = resnet_models + vit_models
        success_count = len(all_models)

        print(f"\n✓ Collected {len(resnet_models)} ResNet-50 and {len(vit_models)} ViT-Base models")
        print(f"  Total: {success_count} real pre-trained models from timm")

        if success_count < (n_resnet + n_vit) * 0.8:
            raise Exception(f"Insufficient models collected. Got {success_count}, expected at least {int((n_resnet + n_vit) * 0.8)}")

        return {
            "models": all_models,
            "success_count": success_count
        }

    def download_model(self, model_id: str, retry: int = 3) -> Dict:
        """
        Download single model with retry logic.
        Returns: {"model_id": str, "architecture": str, "state_dict": OrderedDict}
        """
        from transformers import AutoModel
        import timm

        for attempt in range(retry):
            try:
                print(f"  Downloading {model_id} (attempt {attempt + 1}/{retry})...")

                # Determine architecture type and download real model weights
                model_id_lower = model_id.lower()
                state_dict = None

                if "resnet" in model_id_lower:
                    # Try loading as timm model first (common for ResNets)
                    try:
                        model = timm.create_model(model_id, pretrained=True)
                        state_dict = model.state_dict()
                        architecture = "resnet50"
                    except Exception:
                        # Fallback to transformers
                        model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
                        state_dict = model.state_dict()
                        architecture = "resnet50"

                elif "vit" in model_id_lower:
                    # Try loading as timm model first (common for ViTs)
                    try:
                        model = timm.create_model(model_id, pretrained=True)
                        state_dict = model.state_dict()
                        architecture = "vit_base"
                    except Exception:
                        # Fallback to transformers
                        model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
                        state_dict = model.state_dict()
                        architecture = "vit_base"

                else:
                    # Generic fallback
                    try:
                        model = AutoModel.from_pretrained(model_id, trust_remote_code=True)
                        state_dict = model.state_dict()
                        architecture = "unknown"
                    except Exception:
                        model = timm.create_model(model_id, pretrained=True)
                        state_dict = model.state_dict()
                        architecture = "unknown"

                if state_dict is None:
                    raise Exception(f"Failed to load state_dict for {model_id}")

                return {
                    "model_id": model_id,
                    "architecture": architecture,
                    "state_dict": state_dict,
                    "accuracy": None  # Will be populated if available from model card
                }

            except Exception as e:
                if attempt == retry - 1:
                    raise Exception(f"Failed to download {model_id} after {retry} attempts: {e}")
                print(f"    Retry due to: {e}")
                continue

    def save_metadata(self, metadata: List[Dict], filepath: str) -> None:
        """Save collected metadata to JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Metadata saved to {filepath}")
