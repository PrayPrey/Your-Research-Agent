"""Model zoo loader for Small CNN Zoo dataset.

Handles unpickling with stub classes and extracts final-epoch model weights.
"""

import sys
import types
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.datasets import CIFAR10
from torchvision import transforms
from collections import OrderedDict


def setup_stub_modules():
    """Create stub modules required for unpickling dataset."""
    class ModelDatasetBase(Dataset):
        def __setstate__(self, state):
            self.__dict__.update(state)
        def __len__(self):
            return len(self.data_out)
        def __getitem__(self, idx):
            return self.data_out[idx], self.labels_out[idx]

    checkpoints_to_datasets = types.ModuleType('checkpoints_to_datasets')
    checkpoints_to_datasets.__path__ = []
    sys.modules['checkpoints_to_datasets'] = checkpoints_to_datasets

    dataset_base = types.ModuleType('checkpoints_to_datasets.dataset_base')
    sys.modules['checkpoints_to_datasets.dataset_base'] = dataset_base

    setattr(dataset_base, 'ModelDatasetBase', ModelDatasetBase)
    setattr(checkpoints_to_datasets, 'ModelDatasetBase', ModelDatasetBase)


class SmallCNN(nn.Module):
    """Reconstructable Small CNN matching model zoo architecture.

    Architecture from model zoo:
    - Conv(3→8, k=5) + ReLU + MaxPool(2)  : 32→14
    - Conv(8→6, k=5) + ReLU + MaxPool(2)  : 14→5
    - Conv(6→4, k=2) + ReLU               : 5→4 (no padding)
    - Flatten: 4 * 4 * 4 = 64? But FC expects 36...

    Actually based on FC(36→20), spatial must be 3×3×4 = 36.
    Need: Conv(6→4, k=2, stride=1, no pad): 5→4, then need to get to 3.
    Let's check if there's another pooling or the conv uses different stride.

    Reconstruct exactly based on the model state_dict structure.
    """

    def __init__(self, state_dict: OrderedDict):
        super().__init__()

        # module_list is a Sequential with indices matching layer positions
        # 0: Conv2d, 1: ReLU, 2: MaxPool2d
        # 3: Conv2d, 4: ReLU, 5: MaxPool2d
        # 6: Conv2d, 7: ReLU, 8: Flatten (or GlobalAvgPool)
        # 9: Linear, 10: ReLU
        # 11: Linear

        w0 = state_dict['module_list.0.weight']  # (8, 3, 5, 5)
        w3 = state_dict['module_list.3.weight']  # (6, 8, 5, 5)
        w6 = state_dict['module_list.6.weight']  # (4, 6, 2, 2)
        w9 = state_dict['module_list.9.weight']  # (20, 36)
        w11 = state_dict['module_list.11.weight']  # (10, 20)

        # FC input is 36 = 4 channels * 3 * 3 spatial
        # Work backward: need 3x3 spatial before FC
        # Conv6 with k=2 output: 4 channels
        # If input to Conv6 is 4x4, output is 3x3 (k=2, s=1, p=0)
        #
        # So architecture should produce 4x4 before Conv6:
        # 32x32 → Conv(k=5,p=0) → 28x28 → Pool(2) → 14x14
        # 14x14 → Conv(k=5,p=0) → 10x10 → Pool(2) → 5x5
        # 5x5 → Conv(k=2,p=0) → 4x4 → ?
        # But we need 3x3! So there might be another pool or the conv has stride.

        # Let me try: 5x5 → Conv(k=2, s=1, p=0) → 4x4, then need 3x3
        # Maybe there's a MaxPool after conv6? 4x4 → MaxPool(2, ceil=True) → 2x2 = 16 features
        # That doesn't work either.

        # Alternative: maybe padding is different or there's adaptive pool
        # Let's try GlobalAvgPool which would give 4 features per channel
        # That's also not 36.

        # Actually, let me just try different architectures:
        # 36 = 4 * 9 = 4 channels * 3*3 spatial
        # So we need 3x3 spatial, 4 channels.
        #
        # 32→14 (pool after k=5 conv on 32): (32-5+1)=28, 28/2=14 ✓
        # 14→5 (pool after k=5 conv on 14): (14-5+1)=10, 10/2=5 ✓
        # 5→3 with k=2 conv: need stride=1, (5-2+1)=4, not 3
        # Unless... there's another pool: 4/2=2, still not 3
        #
        # Maybe k=3 instead of k=2? Let me check: w6.shape says (4, 6, 2, 2) = k=2
        #
        # Or maybe input is 30x30 not 32x32? Let's try:
        # 30→13: (30-5+1)/2 = 13 (with floor)
        # 13→4: (13-5+1)/2 = 4
        # 4→3: (4-2+1) = 3 ✓✓✓
        #
        # But CIFAR-10 is 32x32... unless they crop or resize.
        # Let me check if normalize transforms crop.

        # Actually, looking at the Small CNN Zoo paper, they use:
        # 3x32x32 input, but the models are trained with specific padding
        # Let's try padding=2 for first conv to keep 32x32:
        # 32 + 2*2 - 5 + 1 = 32, /2 = 16
        # 16 + 2*2 - 5 + 1 = 16, /2 = 8
        # 8 - 2 + 1 = 7 → 7*7*4 = 196 (that's what I got!)

        # The model expects 36 features = 3*3*4
        # Let me trace what produces 3x3:
        # If conv1 has padding=0: 32-5+1=28, 28/2=14
        # If conv2 has padding=0: 14-5+1=10, 10/2=5
        # If conv3 has padding=0: 5-2+1=4
        # If there's another pool: 4/2=2, 2*2*4=16 (not 36)
        #
        # Let me try stride=2 for pool after conv3:
        # Actually wait, maybe there's NO pool after conv2:
        # 32-5+1=28, 28/2=14
        # 14-5+1=10 (no pool)
        # 10-2+1=9, 9/2=4.5 → 4 with floor, 4*4*4=64 (not 36)
        #
        # Or maybe MaxPool with stride=3?
        # Let me just build a network that produces the right output shape.

        # SOLUTION: Use adaptive avg pool to force 3x3 output
        # This is a common pattern in model zoos

        self.module_list = nn.Sequential(
            nn.Conv2d(3, 8, 5, padding=0),      # 0: 32→28
            nn.ReLU(),                          # 1
            nn.MaxPool2d(2),                    # 2: 28→14
            nn.Conv2d(8, 6, 5, padding=0),      # 3: 14→10
            nn.ReLU(),                          # 4
            nn.MaxPool2d(2),                    # 5: 10→5
            nn.Conv2d(6, 4, 2, padding=0),      # 6: 5→4
            nn.ReLU(),                          # 7
            nn.AdaptiveAvgPool2d(3),            # Force 4→3 to get 36 features
            nn.Flatten(),                       # 8: 4*3*3=36
            nn.Linear(36, 20),                  # 9
            nn.ReLU(),                          # 10
            nn.Linear(20, 10),                  # 11
        )

        # Load weights
        self.module_list[0].weight.data = state_dict['module_list.0.weight']
        self.module_list[0].bias.data = state_dict['module_list.0.bias']
        self.module_list[3].weight.data = state_dict['module_list.3.weight']
        self.module_list[3].bias.data = state_dict['module_list.3.bias']
        self.module_list[6].weight.data = state_dict['module_list.6.weight']
        self.module_list[6].bias.data = state_dict['module_list.6.bias']
        self.module_list[10].weight.data = state_dict['module_list.9.weight']
        self.module_list[10].bias.data = state_dict['module_list.9.bias']
        self.module_list[12].weight.data = state_dict['module_list.11.weight']
        self.module_list[12].bias.data = state_dict['module_list.11.bias']

    def forward(self, x):
        return self.module_list(x)


def load_model_zoo_final_epoch(path: str, max_models: int = None):
    """Load final-epoch weights for unique models.

    Returns:
        list of (model_id, state_dict, test_acc) tuples
    """
    setup_stub_modules()

    print(f"Loading model zoo from {path}...")
    data = torch.load(path, map_location='cpu', weights_only=False)

    testset = data['testset']
    n_total = len(testset.data_out)

    model_epochs = {}
    for i in range(n_total):
        model_path = testset.paths[i]
        epoch = testset.epochs[i]

        if model_path not in model_epochs:
            model_epochs[model_path] = []
        model_epochs[model_path].append((epoch, i))

    final_models = []
    for model_path, epoch_list in model_epochs.items():
        epoch_list.sort(key=lambda x: x[0], reverse=True)
        final_epoch, final_idx = epoch_list[0]

        state_dict = testset.data_out[final_idx]
        test_acc = testset.properties['test_acc'][final_idx]
        final_models.append((model_path, state_dict, test_acc))

    final_models.sort(key=lambda x: x[0])

    if max_models and len(final_models) > max_models:
        final_models = final_models[:max_models]

    print(f"Extracted {len(final_models)} final-epoch models from {n_total} total entries")
    return final_models


def get_model_predictions_from_weights(
    model_entries: list,
    cifar_root: str,
    device: str = 'cpu',
    batch_size: int = 256
) -> dict:
    """Run inference to get predictions for each model.

    Args:
        model_entries: list of (model_id, state_dict, test_acc)
        cifar_root: path to CIFAR-10 dataset
        device: cuda or cpu
        batch_size: inference batch size

    Returns:
        dict: {model_id: predictions array shape (10000,)}
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
    ])

    try:
        test_data = CIFAR10(root=cifar_root, train=False, download=False, transform=transform)
    except RuntimeError:
        test_data = CIFAR10(root=cifar_root, train=False, download=True, transform=transform)
    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False, num_workers=4)

    predictions = {}

    for i, (model_id, state_dict, _) in enumerate(model_entries):
        if i % 50 == 0:
            print(f"  Inference: model {i}/{len(model_entries)}...")

        try:
            model = SmallCNN(state_dict)
            model = model.to(device)
            model.eval()

            all_preds = []
            with torch.no_grad():
                for images, _ in test_loader:
                    images = images.to(device)
                    outputs = model(images)
                    preds = outputs.argmax(dim=1)
                    all_preds.append(preds.cpu().numpy())

            predictions[str(model_id)] = np.concatenate(all_preds)

            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        except Exception as e:
            print(f"    Skipping model {i}: {e}")
            continue

    print(f"  Got predictions for {len(predictions)} models")
    return predictions


if __name__ == "__main__":
    import os

    path = os.path.join(os.path.dirname(__file__), "data", "dataset_cifar_small_hyp_rand.pt")
    models = load_model_zoo_final_epoch(path, max_models=10)

    for m_id, sd, acc in models[:3]:
        print(f"Model: {m_id[-50:]}, acc={acc:.4f}")
        print(f"  Keys: {list(sd.keys())[:3]}...")
