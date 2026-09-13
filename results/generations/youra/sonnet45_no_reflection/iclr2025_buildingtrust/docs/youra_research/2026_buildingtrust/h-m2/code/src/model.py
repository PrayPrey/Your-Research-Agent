"""Model loading and LoRA intervention for H-E1"""
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel
import torch
from typing import Dict, List, Optional

class BaselineModel:
    """Baseline model loader"""

    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B"):
        """Initialize baseline model.

        Args:
            model_id: HuggingFace model identifier
        """
        self.model_id = model_id
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def load_model(self) -> AutoModelForCausalLM:
        """Load pretrained model with bfloat16."""
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        return self.model

    def load_tokenizer(self) -> AutoTokenizer:
        """Load tokenizer with padding setup."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        return self.tokenizer


class LoRAInterventionModel:
    """LoRA intervention wrapper"""

    def __init__(
        self,
        base_model: AutoModelForCausalLM,
        lora_rank: int = 8,
        lora_alpha: int = 8,
        lora_dropout: float = 0.05,
        target_modules: Optional[List[str]] = None
    ):
        """Initialize LoRA intervention wrapper.

        Args:
            base_model: Base model to apply LoRA
            lora_rank: LoRA rank
            lora_alpha: LoRA alpha scaling
            lora_dropout: LoRA dropout rate
            target_modules: Modules to apply LoRA (default: q_proj, v_proj)
        """
        self.base_model = base_model
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.target_modules = target_modules or ["q_proj", "v_proj"]
        self.peft_model: Optional[PeftModel] = None

    def apply_lora(self) -> PeftModel:
        """Apply LoRA adapter to base model.

        Returns:
            PeftModel with trainable adapters
        """
        lora_config = LoraConfig(
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            lora_dropout=self.lora_dropout,
            target_modules=self.target_modules,
            bias="none",
            task_type="CAUSAL_LM"
        )

        self.peft_model = get_peft_model(self.base_model, lora_config)
        return self.peft_model

    def get_trainable_params(self) -> Dict[str, int]:
        """Get trainable parameter statistics.

        Returns:
            Dictionary with trainable, total, and percentage
        """
        if self.peft_model is None:
            raise ValueError("LoRA not applied yet. Call apply_lora() first.")

        trainable_params = 0
        all_params = 0

        for _, param in self.peft_model.named_parameters():
            all_params += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()

        percentage = 100 * trainable_params / all_params if all_params > 0 else 0

        return {
            "trainable": trainable_params,
            "total": all_params,
            "percentage": percentage
        }
