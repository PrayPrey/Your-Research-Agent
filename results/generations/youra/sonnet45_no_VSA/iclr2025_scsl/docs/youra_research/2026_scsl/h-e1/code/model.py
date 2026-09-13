"""MNISTNet architecture (PyTorch official example)."""
import torch
import torch.nn as nn
import torch.nn.functional as F
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')
from config import MODEL_CONFIG


class MNISTNet(nn.Module):
    """Standard CNN from PyTorch official MNIST example."""

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, MODEL_CONFIG["conv1_out_channels"], 3, 1)
        self.conv2 = nn.Conv2d(MODEL_CONFIG["conv1_out_channels"],
                               MODEL_CONFIG["conv2_out_channels"], 3, 1)
        self.dropout1 = nn.Dropout(MODEL_CONFIG["dropout1"])
        self.dropout2 = nn.Dropout(MODEL_CONFIG["dropout2"])
        self.fc1 = nn.Linear(9216, MODEL_CONFIG["fc1_out_features"])
        self.fc2 = nn.Linear(MODEL_CONFIG["fc1_out_features"],
                            MODEL_CONFIG["num_classes"])

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)
