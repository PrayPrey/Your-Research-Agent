"""Model loader with quantization and LoRA support."""

import torch
from transformers import MambaForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from typing import List, Tuple
import logging
import os


class ModelLoader:
    """Load Mamba model with quantization and LoRA adapters."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def create_quantization_config(self) -> BitsAndBytesConfig:
        """Create BitsAndBytesConfig for 4-bit quantization."""
        dtype_map = {
            'bfloat16': torch.bfloat16,
            'float16': torch.float16,
            'float32': torch.float32
        }

        compute_dtype = dtype_map[self.config.quantization.bnb_4bit_compute_dtype]

        return BitsAndBytesConfig(
            load_in_4bit=self.config.quantization.load_in_4bit,
            bnb_4bit_quant_type=self.config.quantization.bnb_4bit_quant_type,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=self.config.quantization.bnb_4bit_use_double_quant
        )

    def inspect_target_modules(self, model) -> List[str]:
        """Inspect model architecture to find target modules."""
        found_modules = set()

        for name, module in model.named_modules():
            if any(target in name for target in ['x_proj', 'dt_proj', 'in_proj', 'out_proj']):
                module_type = name.split('.')[-1]
                found_modules.add(module_type)

        self.logger.info(f"Found target modules: {found_modules}")

        configured_targets = self.config.lora.target_modules
        verified_targets = [t for t in configured_targets if t in found_modules]

        if not verified_targets:
            self.logger.warning(f"Configured targets {configured_targets} not found. "
                              f"Using all linear layers.")
            return "all-linear"

        return verified_targets

    def load_quantized_mamba(self, apply_lora: bool = True) -> Tuple:
        """
        Load Mamba model with quantization and optional LoRA adapters.

        Returns:
            (model, trainable_params_count, target_modules)
        """
        dtype_map = {
            'bfloat16': torch.bfloat16,
            'float16': torch.float16,
            'float32': torch.float32
        }
        torch_dtype = dtype_map[self.config.model.torch_dtype]

        quantization_config = self.create_quantization_config()

        self.logger.info(f"Loading model: {self.config.model.name}")

        # Use PR#1 which has safetensors format (bypasses torch 2.6 requirement)
        model = MambaForCausalLM.from_pretrained(
            self.config.model.name,
            revision="refs/pr/1",  # Use PR with safetensors
            quantization_config=quantization_config,
            device_map=self.config.model.device_map,
            torch_dtype=torch_dtype
        )

        target_modules = None
        trainable_params = 0

        if apply_lora:
            # Only prepare for kbit training if quantization is enabled
            if self.config.quantization.load_in_4bit:
                model = prepare_model_for_kbit_training(model)
            model.enable_input_require_grads()

            target_modules = self.inspect_target_modules(model)

            lora_config = LoraConfig(
                r=self.config.lora.r,
                lora_alpha=self.config.lora.lora_alpha,
                target_modules=target_modules,
                lora_dropout=self.config.lora.lora_dropout,
                bias=self.config.lora.bias,
                task_type=self.config.lora.task_type
            )

            self.logger.info(f"Applying LoRA with config: r={self.config.lora.r}, "
                           f"alpha={self.config.lora.lora_alpha}, "
                           f"targets={target_modules}")

            model = get_peft_model(model, lora_config)

            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            total_params = sum(p.numel() for p in model.parameters())

            self.logger.info(f"Trainable parameters: {trainable_params:,} "
                           f"({100 * trainable_params / total_params:.4f}%)")

        return model, trainable_params, target_modules

    def load_baseline(self, use_quantization: bool = False, use_lora: bool = False):
        """Load baseline configurations for comparison."""
        dtype_map = {
            'bfloat16': torch.bfloat16,
            'float16': torch.float16,
            'float32': torch.float32
        }
        torch_dtype = dtype_map[self.config.model.torch_dtype]

        kwargs = {
            'pretrained_model_name_or_path': self.config.model.name,
            'revision': "refs/pr/1",  # Use PR with safetensors
            'device_map': self.config.model.device_map,
            'torch_dtype': torch_dtype
        }

        if use_quantization:
            kwargs['quantization_config'] = self.create_quantization_config()

        model = MambaForCausalLM.from_pretrained(**kwargs)

        if use_lora:
            if use_quantization:
                model = prepare_model_for_kbit_training(model)
            model.enable_input_require_grads()

            target_modules = self.inspect_target_modules(model)

            lora_config = LoraConfig(
                r=self.config.lora.r,
                lora_alpha=self.config.lora.lora_alpha,
                target_modules=target_modules,
                lora_dropout=self.config.lora.lora_dropout,
                bias=self.config.lora.bias,
                task_type=self.config.lora.task_type
            )

            model = get_peft_model(model, lora_config)

        return model
