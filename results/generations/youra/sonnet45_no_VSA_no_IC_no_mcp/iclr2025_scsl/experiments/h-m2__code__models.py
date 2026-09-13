import torch
import torch.nn as nn
import torchvision.models as models
import timm
from cbam import CBAM


def create_resnet_bn(num_classes=2):
    """ResNet-18 with Batch Normalization (control)."""
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)
    return model


def create_resnet_cbam(num_classes=2, reduction=16):
    """ResNet-18 with CBAM modules after each layer."""
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1)
            nn.init.constant_(m.bias, 0)

    model.layer1_cbam = CBAM(64, reduction)
    model.layer2_cbam = CBAM(128, reduction)
    model.layer3_cbam = CBAM(256, reduction)
    model.layer4_cbam = CBAM(512, reduction)

    for cbam in [model.layer1_cbam, model.layer2_cbam, model.layer3_cbam, model.layer4_cbam]:
        for m in cbam.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)

    original_forward = model.forward

    def cbam_forward(x):
        x = model.conv1(x)
        x = model.bn1(x)
        x = model.relu(x)
        x = model.maxpool(x)

        x = model.layer1(x)
        x = model.layer1_cbam(x)

        x = model.layer2(x)
        x = model.layer2_cbam(x)

        x = model.layer3(x)
        x = model.layer3_cbam(x)

        x = model.layer4(x)
        x = model.layer4_cbam(x)

        x = model.avgpool(x)
        x = torch.flatten(x, 1)
        x = model.fc(x)
        return x

    model.forward = cbam_forward
    return model


def create_vit_small(num_classes=2):
    """ViT-Small from timm."""
    model = timm.create_model('vit_small_patch16_224', pretrained=False, num_classes=num_classes)
    return model
