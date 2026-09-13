"""
Model Family Manager for H-M4
Handles loading and LoRA adaptation across 5 model families
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig, TaskType
from typing import Dict, Tuple, Optional
import gc


class ModelFamilyManager:
    """Manages multiple model families for cross-architecture experiments"""

    def __init__(self, model_families: Dict, lora_config: Dict, device: str = "cuda"):
        self.model_families = model_families
        self.lora_config = lora_config
        self.device = device
        self.current_model = None
        self.current_tokenizer = None
        self.current_family = None

    def load_model_family(self, family_name: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load a specific model family"""
        if family_name not in self.model_families:
            raise ValueError(f"Unknown model family: {family_name}")

        family_info = self.model_families[family_name]
        model_id = family_info["model_id"]

        print(f"Loading {family_name}: {model_id}")

        # Clear previous model if exists
        self.clear_current_model()

        # Load model with device mapping
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
        except Exception as e:
            print(f"Failed to load {model_id} with auto device_map, trying CPU: {e}")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                trust_remote_code=True
            )
            model = model.to(self.device)

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )

        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        self.current_model = model
        self.current_tokenizer = tokenizer
        self.current_family = family_name

        return model, tokenizer

    def apply_lora(self, model: AutoModelForCausalLM, family_name: str) -> AutoModelForCausalLM:
        """Apply LoRA to a model with family-specific target modules"""
        family_info = self.model_families[family_name]
        target_modules = family_info["lora_target_modules"]

        print(f"Applying LoRA to {family_name} (targets: {target_modules})")

        # Create LoRA config with family-specific targets
        lora_config = LoraConfig(
            r=self.lora_config["r"],
            lora_alpha=self.lora_config["lora_alpha"],
            target_modules=target_modules,
            lora_dropout=self.lora_config["lora_dropout"],
            bias=self.lora_config["bias"],
            task_type=TaskType.CAUSAL_LM
        )

        # Apply LoRA
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        return model

    def clear_current_model(self):
        """Clear current model from memory"""
        if self.current_model is not None:
            del self.current_model
            self.current_model = None
        if self.current_tokenizer is not None:
            del self.current_tokenizer
            self.current_tokenizer = None

        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def get_model_info(self, family_name: str) -> Dict:
        """Get information about a model family"""
        return self.model_families.get(family_name, {})

    def list_families(self):
        """List all available model families"""
        return list(self.model_families.keys())
