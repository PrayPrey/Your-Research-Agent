import torch
from torch import Tensor
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from peft import PeftModel, LoraConfig, TaskType, get_peft_model
from typing import Optional
from config import ExperimentConfig


class LoRAExtractor:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model: Optional[object] = None
        self.tokenizer: Optional[object] = None

    def load_model(self):
        tokenizer = AutoTokenizer.from_pretrained(self.config.lora_base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        base_model = AutoModelForSequenceClassification.from_pretrained(
            self.config.lora_base_model,
            num_labels=self.config.num_labels,
            attn_implementation="eager",  # CRITICAL: enables output_attentions=True
            torch_dtype=torch.float16,
            device_map="auto",
        )

        try:
            model = PeftModel.from_pretrained(base_model, self.config.lora_checkpoint)
            print(f"✓ Loaded LoRA checkpoint: {self.config.lora_checkpoint}")
        except Exception as e:
            print(f"⚠ LoRA checkpoint failed ({e}), using fresh LoRA config")
            lora_config = LoraConfig(
                task_type=TaskType.SEQ_CLS,
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "k_proj", "v_proj"],
                lora_dropout=0.1,
            )
            model = get_peft_model(base_model, lora_config)

        model.eval()
        self.model = model
        self.tokenizer = tokenizer
        return model, tokenizer

    def extract_attention_scores(
        self,
        model,
        input_ids: Tensor,
        attention_mask: Tensor,
    ) -> list:
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
            )

        all_layer_scores = []
        for layer_idx in range(self.config.num_layers):
            attn = outputs.attentions[layer_idx]   # (1, 32, L, L)
            per_token = attn.sum(dim=2).squeeze(0)  # (32, L)
            all_layer_scores.append(per_token.cpu())
        return all_layer_scores  # list[32] of (32, L)

    def get_layer_scores(self, all_layer_scores: list, layer_idx: int) -> Tensor:
        return all_layer_scores[layer_idx]

    def unload(self) -> None:
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
        print("✓ LoRA model unloaded")
