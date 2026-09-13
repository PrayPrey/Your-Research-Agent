"""Model loading utilities for CNN and Transformer models."""

from typing import Union, Callable
import torch
from torch import nn
from torch.optim import Optimizer, SGD, Adam, AdamW
from transformers import (
    AutoModel,
    AutoModelForMaskedLM,
    AutoModelForCausalLM,
    get_linear_schedule_with_warmup
)
import torchvision.models as models

from config import CNNConfig, TransformerConfig


def load_cnn_model(config: CNNConfig, device: str = "cpu") -> nn.Module:
    """
    Load CNN model from torchvision.

    Args:
        config: CNN configuration
        device: Device to load model on

    Returns:
        PyTorch model
    """
    # Map model names to torchvision functions
    model_map = {
        "resnet18": models.resnet18,
        "resnet50": models.resnet50,
        "vgg16": models.vgg16,
        "efficientnet_b0": models.efficientnet_b0,
        "densenet121": models.densenet121,
        "mobilenet_v2": models.mobilenet_v2,
        "shufflenet_v2_x1_0": models.shufflenet_v2_x1_0,
        "squeezenet1_0": models.squeezenet1_0,
    }

    if config.model_name not in model_map:
        raise ValueError(f"Unknown CNN model: {config.model_name}")

    # Load pretrained model
    model = model_map[config.model_name](pretrained=True)

    # Modify final layer for CIFAR-10 (10 classes)
    if config.dataset == "cifar10":
        num_classes = 10

        if "resnet" in config.model_name or "densenet" in config.model_name:
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)
        elif "vgg" in config.model_name:
            in_features = model.classifier[6].in_features
            model.classifier[6] = nn.Linear(in_features, num_classes)
        elif "efficientnet" in config.model_name:
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)
        elif "mobilenet" in config.model_name:
            in_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(in_features, num_classes)
        elif "shufflenet" in config.model_name:
            in_features = model.fc.in_features
            model.fc = nn.Linear(in_features, num_classes)
        elif "squeezenet" in config.model_name:
            model.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=1)
            model.num_classes = num_classes

    model = model.to(device)
    return model


def load_transformer_model(config: TransformerConfig, device: str = "cpu") -> nn.Module:
    """
    Load Transformer model from HuggingFace.

    Args:
        config: Transformer configuration
        device: Device to load model on

    Returns:
        PyTorch model
    """
    # Determine model type and load appropriate class
    if "gpt" in config.model_name.lower():
        model = AutoModelForCausalLM.from_pretrained(config.model_name)
    elif "bert" in config.model_name.lower() or "albert" in config.model_name.lower() or \
         "roberta" in config.model_name.lower() or "electra" in config.model_name.lower() or \
         "deberta" in config.model_name.lower():
        model = AutoModelForMaskedLM.from_pretrained(config.model_name)
    elif "t5" in config.model_name.lower():
        from transformers import AutoModelForSeq2SeqLM
        model = AutoModelForSeq2SeqLM.from_pretrained(config.model_name)
    else:
        # Fallback to AutoModel
        model = AutoModel.from_pretrained(config.model_name)

    model = model.to(device)
    return model


def get_optimizer(model: nn.Module, config: Union[CNNConfig, TransformerConfig]) -> Optimizer:
    """
    Create optimizer based on configuration.

    Args:
        model: PyTorch model
        config: CNN or Transformer configuration

    Returns:
        PyTorch optimizer
    """
    optimizer_name = config.optimizer.lower()

    if optimizer_name == "sgd":
        if isinstance(config, CNNConfig):
            optimizer = SGD(
                model.parameters(),
                lr=config.lr,
                momentum=config.momentum,
                weight_decay=config.weight_decay
            )
        else:
            # For transformers with SGD (rare)
            optimizer = SGD(
                model.parameters(),
                lr=config.lr,
                weight_decay=config.weight_decay
            )

    elif optimizer_name == "adam":
        optimizer = Adam(
            model.parameters(),
            lr=config.lr,
            weight_decay=config.weight_decay
        )

    elif optimizer_name == "adamw":
        optimizer = AdamW(
            model.parameters(),
            lr=config.lr,
            weight_decay=config.weight_decay
        )

    elif optimizer_name == "adafactor":
        from transformers import Adafactor
        optimizer = Adafactor(
            model.parameters(),
            lr=config.lr,
            scale_parameter=True,
            relative_step=False
        )

    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")

    return optimizer


def get_criterion(config: Union[CNNConfig, TransformerConfig]) -> Callable:
    """
    Get loss function (CrossEntropyLoss for all tasks).

    Args:
        config: CNN or Transformer configuration

    Returns:
        Loss function
    """
    return nn.CrossEntropyLoss()
