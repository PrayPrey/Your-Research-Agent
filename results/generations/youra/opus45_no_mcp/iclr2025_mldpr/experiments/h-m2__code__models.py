import torch
import torch.nn as nn
import torchvision.models as models


def build_vgg11_cifar(num_classes=10):
    """VGG-11 adapted for CIFAR-10 (32x32 input)."""
    model = models.vgg11(weights=None)
    model.avgpool = nn.AdaptiveAvgPool2d((1, 1))
    model.classifier = nn.Sequential(
        nn.Linear(512, 256),
        nn.ReLU(True),
        nn.Dropout(0.5),
        nn.Linear(256, num_classes),
    )
    return model


def build_resnet18_cifar(num_classes=10):
    """ResNet-18 adapted for CIFAR-10 (32x32 input)."""
    model = models.resnet18(weights=None)
    model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
    model.maxpool = nn.Identity()
    model.fc = nn.Linear(512, num_classes)
    return model
