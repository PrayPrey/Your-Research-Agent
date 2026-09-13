"""Sample ResNet script for version stability testing."""

import torch
import torch.nn as nn


class SimpleResNet(nn.Module):
    """Simplified ResNet for testing."""

    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        return x


if __name__ == "__main__":
    model = SimpleResNet(num_classes=10)
    x = torch.randn(1, 3, 224, 224)
    output = model(x)
    print(f"Output shape: {output.shape}")
    print("Script executed successfully")
