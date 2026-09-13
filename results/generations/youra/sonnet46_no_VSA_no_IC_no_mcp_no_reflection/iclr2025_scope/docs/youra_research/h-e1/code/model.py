import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from config import ExperimentConfig


class MambaForSequenceClassification(nn.Module):
    def __init__(self, cfg: ExperimentConfig, num_labels: int, backbone: nn.Module = None):
        super().__init__()
        self.backbone = backbone
        self.classifier = nn.Linear(768, num_labels)
        self.num_labels = num_labels
        nn.init.normal_(self.classifier.weight, std=0.02)
        nn.init.zeros_(self.classifier.bias)

    def forward(self, input_ids: torch.Tensor, labels: Optional[torch.Tensor] = None) -> dict:
        out = self.backbone(input_ids, output_hidden_states=True)
        hidden = out.hidden_states[-1]      # [B, L, 768]
        pooled = hidden[:, -1, :]          # [B, 768] last-token pooling
        logits = self.classifier(pooled)   # [B, num_labels]
        result = {"logits": logits}
        if labels is not None:
            result["loss"] = F.cross_entropy(logits, labels)
        return result


def build_lora_model(cfg: ExperimentConfig, num_labels: int) -> MambaForSequenceClassification:
    assert "conv1d" not in cfg.target_modules, "conv1d breaks PEFT — remove it"
    base = AutoModelForCausalLM.from_pretrained(cfg.model_name)
    lora_cfg = LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=list(cfg.target_modules),
        bias="none",
        task_type="FEATURE_EXTRACTION",
    )
    peft_model = get_peft_model(base, lora_cfg)
    peft_model.print_trainable_parameters()
    return MambaForSequenceClassification(cfg, num_labels, backbone=peft_model)


def build_zero_shot_model(cfg: ExperimentConfig, num_labels: int) -> MambaForSequenceClassification:
    base = AutoModelForCausalLM.from_pretrained(cfg.model_name)
    for p in base.parameters():
        p.requires_grad = False
    return MambaForSequenceClassification(cfg, num_labels, backbone=base)


def verify_lora_activated(model, results_lora: dict, results_zeroshot: dict) -> tuple:
    sd = model.backbone.state_dict()
    lora_keys = [k for k in sd if "lora_A" in k or "lora_B" in k]
    lora_keys_present = len(lora_keys) > 0
    lora_weights_nonzero = any(sd[k].abs().sum().item() > 0 for k in lora_keys) if lora_keys else False
    sst2_lora = results_lora.get("sst2", 0.0)
    sst2_zs = results_zeroshot.get("sst2", 0.0)
    sst2_delta_positive = (sst2_lora - sst2_zs) > 0
    indicators = {
        "lora_keys_present": lora_keys_present,
        "lora_weights_nonzero": lora_weights_nonzero,
        "sst2_delta_positive": sst2_delta_positive,
    }
    activated = lora_keys_present and lora_weights_nonzero
    return activated, indicators
