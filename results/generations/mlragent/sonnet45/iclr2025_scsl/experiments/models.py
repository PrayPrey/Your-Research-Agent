"""
Model architectures for spurious correlation experiments
"""
import torch
import torch.nn as nn
import torchvision.models as models


class SimpleConvNet(nn.Module):
    """Simple CNN for small image datasets"""

    def __init__(self, num_classes=2, input_channels=3):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1)
        )

        self.classifier = nn.Linear(128, num_classes)

    def forward(self, x, return_features=False):
        features = self.features(x)
        features = features.view(features.size(0), -1)

        if return_features:
            return self.classifier(features), features

        return self.classifier(features)


class ResNetModel(nn.Module):
    """ResNet-based model"""

    def __init__(self, num_classes=2, arch='resnet18', pretrained=True):
        super().__init__()

        if arch == 'resnet18':
            self.backbone = models.resnet18(pretrained=pretrained)
        elif arch == 'resnet34':
            self.backbone = models.resnet34(pretrained=pretrained)
        elif arch == 'resnet50':
            self.backbone = models.resnet50(pretrained=pretrained)
        else:
            raise ValueError(f"Unknown architecture: {arch}")

        # Replace final layer
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_features, num_classes)

    def forward(self, x, return_features=False):
        if return_features:
            # Extract features before final layer
            features = self.backbone.avgpool(
                self.backbone.layer4(
                    self.backbone.layer3(
                        self.backbone.layer2(
                            self.backbone.layer1(
                                self.backbone.maxpool(
                                    self.backbone.relu(
                                        self.backbone.bn1(
                                            self.backbone.conv1(x)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
            features = torch.flatten(features, 1)
            return self.backbone.fc(features), features

        return self.backbone(x)


def get_model(config):
    """Get model based on configuration"""

    if config.model_arch.startswith('resnet'):
        model = ResNetModel(
            num_classes=2,
            arch=config.model_arch,
            pretrained=config.pretrained
        )
    else:
        model = SimpleConvNet(num_classes=2)

    return model.to(config.device)
