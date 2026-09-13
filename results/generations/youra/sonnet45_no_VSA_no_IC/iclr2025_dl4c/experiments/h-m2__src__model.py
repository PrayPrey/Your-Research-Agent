"""Model loading and configuration for RLVR training."""

import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType
from typing import Tuple

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, config: dict):
        self.config = config
        self.model_name = config["model"]["name"]
        self.precision = config["model"]["precision"]
        self.cache_dir = config["model"]["cache_dir"]
        self.lora_config = config["lora"]
        self.device = torch.device(config["hardware"]["device"] if torch.cuda.is_available() else "cpu")

    def load_pretrained(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load CodeGen-350M or StarCoder-1B with specified precision."""
        logger.info(f"Loading pretrained model: {self.model_name}")

        dtype = torch.float16 if self.precision == "fp16" else torch.bfloat16

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            torch_dtype=dtype,
            device_map="auto"
        )

        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        logger.info(f"Model loaded successfully on {self.device}")
        return model, tokenizer

    def configure_lora(self, model: AutoModelForCausalLM) -> AutoModelForCausalLM:
        """Add LoRA adapters to q_proj, v_proj."""
        if not self.lora_config["enabled"]:
            logger.info("LoRA disabled, returning original model")
            return model

        logger.info("Configuring LoRA adapters...")
        lora_config = LoraConfig(
            r=self.lora_config["r"],
            lora_alpha=self.lora_config["alpha"],
            target_modules=self.lora_config["target_modules"],
            lora_dropout=self.lora_config["dropout"],
            bias=self.lora_config["bias"],
            task_type=TaskType.CAUSAL_LM
        )

        model = get_peft_model(model, lora_config)
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in model.parameters())

        logger.info(f"LoRA configured: {trainable_params:,} trainable params ({100 * trainable_params / total_params:.2f}%)")
        return model

    def freeze_reference(self, model: AutoModelForCausalLM) -> AutoModelForCausalLM:
        """Create frozen copy for KL penalty computation."""
        logger.info("Creating frozen reference model...")
        ref_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if self.precision == "fp16" else torch.bfloat16,
            device_map="auto"
        )

        for param in ref_model.parameters():
            param.requires_grad = False

        ref_model.eval()
        logger.info("Reference model frozen successfully")
        return ref_model

    def setup_sft_model(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Set up model for SFT training."""
        model, tokenizer = self.load_pretrained()
        model = self.configure_lora(model)
        return model, tokenizer

    def setup_rlvr_models(self, sft_checkpoint_path: str) -> Tuple[AutoModelForCausalLM, AutoModelForCausalLM, AutoTokenizer]:
        """Set up policy and reference models for RLVR training."""
        logger.info(f"Loading SFT checkpoint from {sft_checkpoint_path}")

        policy_model, tokenizer = self.load_pretrained()
        policy_model = self.configure_lora(policy_model)

        checkpoint = torch.load(sft_checkpoint_path, map_location=self.device)
        policy_model.load_state_dict(checkpoint["model_state_dict"])

        ref_model = self.freeze_reference(policy_model)

        logger.info("RLVR models setup complete")
        return policy_model, ref_model, tokenizer
