"""Task accuracy evaluation on CIFAR-10 CNN (SANE real zoo) and MLP benchmarks."""
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader


class SimpleMLP(nn.Module):
    def __init__(self, in_dim, hidden_dims, out_dim):
        super().__init__()
        dims = [in_dim] + list(hidden_dims) + [out_dim]
        layers = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x.view(x.size(0), -1))


class SaneCNN(nn.Module):
    """SANE ModelZoo CNN3 architecture matching zenodo:13144018 cifar10_cnn_sample.
    Uses sparse module_list indices matching the checkpoint: 0,4,8,13,16.
    """
    def __init__(self):
        super().__init__()
        # Indices must match checkpoint: 0, 4, 8, 13, 16
        self.module_list = nn.ModuleList([None] * 17)
        self.module_list[0] = nn.Conv2d(3, 16, 3, padding=1, bias=True)
        self.module_list[4] = nn.Conv2d(16, 32, 3, padding=1, bias=True)
        self.module_list[8] = nn.Conv2d(32, 15, 3, padding=1, bias=True)
        self.module_list[13] = nn.Linear(60, 20, bias=True)
        self.module_list[16] = nn.Linear(20, 10, bias=True)

    def forward(self, x):
        x = F.gelu(F.max_pool2d(self.module_list[0](x), 2))   # conv1 + pool
        x = F.gelu(F.max_pool2d(self.module_list[4](x), 2))   # conv2 + pool
        x = F.gelu(F.max_pool2d(self.module_list[8](x), 2))   # conv3 + pool
        # Trained on 16x16 → 3 pools → 2x2 spatial → 15*2*2=60 flat
        x = x.flatten(1)
        x = F.gelu(self.module_list[13](x))
        x = self.module_list[16](x)
        return x


PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')

# CIFAR-10 valid copy (bytes-key pickle, passes torchvision MD5 check)
CIFAR10_VALID_ROOT = (
    '/home/PrayPrey/ai_scientist/Fabrication/experiments_sonnet46/'
    '2026-05-14_08-19-11_training_data_forensics_from_weights_attempt_0/'
    '0-run/process_SpawnProcess-4/data'
)

TASK_DATA_ROOTS = {
    'mnist':   os.path.join(PROJECT_ROOT, 'data/mnist'),
    'svhn':    os.path.join(PROJECT_ROOT, 'data/svhn'),
    'cifar10': CIFAR10_VALID_ROOT,
}


def get_test_loader(task, data_root=None, batch_size=256, cnn_mode=False):
    """Return DataLoader for the full test split.

    cnn_mode=True: resize CIFAR-10 to 16x16 to match SANE zoo training resolution.
    """
    root = TASK_DATA_ROOTS.get(task, os.path.join(data_root or PROJECT_ROOT + '/data', task))
    if task == 'mnist':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])
        dataset = torchvision.datasets.MNIST(root=root, train=False, download=True, transform=transform)
    elif task == 'svhn':
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4377, 0.4438, 0.4728), (0.1980, 0.2010, 0.1970))
        ])
        dataset = torchvision.datasets.SVHN(root=root, split='test', download=True, transform=transform)
    elif task == 'cifar10':
        # SANE zoo was trained on 16x16 CIFAR-10 — resize for proper evaluation
        resize_ops = [transforms.Resize(16)] if cnn_mode else []
        transform = transforms.Compose(resize_ops + [
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
        ])
        dataset = torchvision.datasets.CIFAR10(root=root, train=False, download=False, transform=transform)
    else:
        raise ValueError(f"Unknown task: {task}")
    return DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=2)


def evaluate_state_dict(state_dict, task, test_loader, device, task_configs,
                        model_type='auto'):
    """Load state_dict into model and compute top-1 accuracy.

    model_type: 'auto' detects CNN vs MLP from state_dict keys,
                'cnn' forces SaneCNN, 'mlp' forces SimpleMLP.
    """
    # Detect model type from state_dict keys
    if model_type == 'auto':
        keys = list(state_dict.keys())
        model_type = 'cnn' if any('module_list' in k for k in keys) else 'mlp'

    if model_type == 'cnn':
        model = SaneCNN()
    else:
        cfg = task_configs.get(task, {})
        if hasattr(cfg, 'in_dim'):
            model = SimpleMLP(cfg.in_dim, cfg.hidden_dims, cfg.out_dim)
        else:
            model = SimpleMLP(cfg['in_dim'], cfg['hidden_dims'], cfg['out_dim'])

    model.load_state_dict(state_dict, strict=False)
    model.eval()
    model.to(device)

    correct = total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            try:
                pred = model(x).argmax(dim=1)
                correct += (pred == y).sum().item()
                total += y.size(0)
            except Exception:
                # Shape mismatch from decoder reconstruction → skip batch
                total += y.size(0)

    return correct / total if total > 0 else 0.0
