import torch
import torch.nn as nn
import torchvision.models as models
from transformers import AutoModel
from typing import Literal
from tqdm import tqdm


class FeatureExtractor:
    def __init__(self, model_type: Literal["resnet50", "bert-base"] = "resnet50", device: str = "cuda"):
        """Initialize with frozen model. model_type: 'resnet50' or 'bert-base'."""
        self.device = device
        self.model_type = model_type
        self.model = load_pretrained_model(model_type).to(device)
        self.model.eval()

    def extract_features(self, data: torch.Tensor, batch_size: int = 256) -> torch.Tensor:
        """Extract features in batches. data: [N, ...] -> [N, F]"""
        features_list = []

        with torch.no_grad():
            for i in tqdm(range(0, len(data), batch_size), desc="Extracting features"):
                batch = data[i:i + batch_size].to(self.device)

                if self.model_type == "resnet50":
                    batch_features = self.model(batch)
                elif self.model_type == "bert-base":
                    # BERT expects input_ids
                    outputs = self.model(input_ids=batch.long())
                    batch_features = outputs.last_hidden_state[:, 0, :]  # [CLS] token

                features_list.append(batch_features.cpu())

        return torch.cat(features_list, dim=0)

    def get_feature_dim(self) -> int:
        """Return feature dimension F."""
        if self.model_type == "resnet50":
            return 2048
        elif self.model_type == "bert-base":
            return 768
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")


def load_pretrained_model(model_type: str) -> nn.Module:
    """Load frozen model without classification head."""
    if model_type == "resnet50":
        # Load ResNet-50 and remove classification head
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        model = nn.Sequential(*list(model.children())[:-1])  # Remove FC layer
        model = nn.Sequential(model, nn.Flatten())

        # Freeze all parameters
        for param in model.parameters():
            param.requires_grad = False

        return model

    elif model_type == "bert-base":
        # Load BERT-base
        model = AutoModel.from_pretrained("bert-base-uncased")

        # Freeze all parameters
        for param in model.parameters():
            param.requires_grad = False

        return model

    else:
        raise ValueError(f"Unknown model type: {model_type}")
