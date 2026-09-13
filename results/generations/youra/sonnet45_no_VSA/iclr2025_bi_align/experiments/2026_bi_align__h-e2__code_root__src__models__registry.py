import torch
import torch.nn as nn
import torchvision.models as models
from transformers import (
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    ViTForImageClassification
)

class ModelRegistry:
    CNN_MODELS = [
        "resnet18", "resnet34", "resnet50", "vgg16",
        "densenet121", "mobilenet_v2", "efficientnet_b0", "shufflenet_v2_x1_0"
    ]
    
    TRANSFORMER_MODELS = [
        "bert-base-uncased", "roberta-base", "gpt2", "t5-small",
        "distilbert-base-uncased", "albert-base-v2",
        "microsoft/deberta-base", "google/vit-base-patch16-224"
    ]
    
    @staticmethod
    def get_model(name: str, num_classes: int = 10, dataset_type: str = "image") -> nn.Module:
        if name in ModelRegistry.CNN_MODELS:
            return ModelRegistry._get_cnn_model(name, num_classes)
        elif name in ModelRegistry.TRANSFORMER_MODELS:
            return ModelRegistry._get_transformer_model(name, num_classes, dataset_type)
        else:
            raise ValueError(f"Unknown model: {name}")
    
    @staticmethod
    def _get_cnn_model(name: str, num_classes: int) -> nn.Module:
        if name == "resnet18":
            model = models.resnet18(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif name == "resnet34":
            model = models.resnet34(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif name == "resnet50":
            model = models.resnet50(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        elif name == "vgg16":
            model = models.vgg16(weights=None)
            model.classifier[6] = nn.Linear(model.classifier[6].in_features, num_classes)
        elif name == "densenet121":
            model = models.densenet121(weights=None)
            model.classifier = nn.Linear(model.classifier.in_features, num_classes)
        elif name == "mobilenet_v2":
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif name == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)
            model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        elif name == "shufflenet_v2_x1_0":
            model = models.shufflenet_v2_x1_0(weights=None)
            model.fc = nn.Linear(model.fc.in_features, num_classes)
        else:
            raise ValueError(f"Unknown CNN model: {name}")
        return model
    
    @staticmethod
    def _get_transformer_model(name: str, num_classes: int, dataset_type: str) -> nn.Module:
        if name == "google/vit-base-patch16-224":
            model = ViTForImageClassification.from_pretrained(name, num_labels=num_classes, ignore_mismatched_sizes=True)
        elif name == "gpt2":
            model = AutoModelForCausalLM.from_pretrained(name)
            model.config.num_labels = num_classes
        elif name == "t5-small":
            model = AutoModelForSeq2SeqLM.from_pretrained(name)
            model.config.num_labels = num_classes
        else:
            model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=num_classes, ignore_mismatched_sizes=True)
        return model
    
    @staticmethod
    def get_cnn_models() -> list[str]:
        return ModelRegistry.CNN_MODELS
    
    @staticmethod
    def get_transformer_models() -> list[str]:
        return ModelRegistry.TRANSFORMER_MODELS
    
    @staticmethod
    def list_all_models() -> dict[str, list[str]]:
        return {
            'cnn': ModelRegistry.CNN_MODELS,
            'transformer': ModelRegistry.TRANSFORMER_MODELS
        }
