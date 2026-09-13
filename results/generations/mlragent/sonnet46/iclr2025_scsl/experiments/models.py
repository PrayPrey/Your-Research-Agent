"""
Model architectures for spurious correlation experiments.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class LinearClassifier(nn.Module):
    """Simple linear classifier for synthetic linear datasets."""
    def __init__(self, input_dim, num_classes=2, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_classes)
        )

    def forward(self, x):
        return self.net(x)

    def get_features(self, x):
        """Return penultimate layer features."""
        for i, layer in enumerate(self.net):
            x = layer(x)
            if i == len(self.net) - 2:
                return x
        return x


class SimpleCNN(nn.Module):
    """Simple CNN for image datasets."""
    def __init__(self, in_channels=1, num_classes=2, img_size=28):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        feat_size = (img_size // 4) * (img_size // 4) * 64
        self.classifier = nn.Sequential(
            nn.Linear(feat_size, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.flatten(1)
        return self.classifier(x)

    def get_features(self, x):
        x = self.features(x)
        x = x.flatten(1)
        # Return after first FC layer
        return F.relu(self.classifier[0](x))
