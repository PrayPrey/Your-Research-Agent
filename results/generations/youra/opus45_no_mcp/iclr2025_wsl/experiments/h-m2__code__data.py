import os
import torch
from torch.utils.data import Dataset, DataLoader

def download_model_zoo(data_dir="data/"):
    import subprocess
    os.makedirs(data_dir, exist_ok=True)
    target = os.path.join(data_dir, "dataset_cifar_small_hyp_fix.pt")
    if os.path.exists(target):
        return
    subprocess.run(["zenodo_get", "-d", "10.5281/zenodo.6620869", "-o", data_dir], check=True)

def _setup_model_zoo_stubs():
    import sys
    import types
    stub_modules = [
        'checkpoints_to_datasets',
        'checkpoints_to_datasets.dataset_auxiliaries',
        'checkpoints_to_datasets.dataset_base',
    ]
    for name in stub_modules:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)
    for mod_name in stub_modules:
        mod = sys.modules[mod_name]
        for cls_name in ['DatasetElement', 'DatasetBase', 'ModelDatasetBase', 'Dataset']:
            setattr(mod, cls_name, type(cls_name, (), {}))
    sys.modules['checkpoints_to_datasets'].dataset_auxiliaries = sys.modules['checkpoints_to_datasets.dataset_auxiliaries']
    sys.modules['checkpoints_to_datasets'].dataset_base = sys.modules['checkpoints_to_datasets.dataset_base']

def _extract_samples(ds):
    """Extract (weights, accuracy) samples from ModelDatasetBase."""
    samples = []
    accuracies = ds.properties['test_acc']
    for i, weights in enumerate(ds.data_in):
        samples.append({'weights': weights, 'accuracy': accuracies[i]})
    return samples

def load_model_zoo(data_path="data/dataset_cifar_small_hyp_fix.pt"):
    _setup_model_zoo_stubs()
    data = torch.load(data_path, weights_only=False)
    train_ds = data['trainset']
    val_ds = data['valset']
    test_ds = data['testset']
    return _extract_samples(train_ds), _extract_samples(val_ds), _extract_samples(test_ds)

def extract_weights_and_accuracy(sample):
    return sample['weights'], sample['accuracy']

class ModelZooDataset(Dataset):
    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        w, a = extract_weights_and_accuracy(self.samples[idx])
        return w, a

def collate_weights(batch):
    weights_list = [b[0] for b in batch]
    accuracies = torch.tensor([b[1] for b in batch], dtype=torch.float32)
    return weights_list, accuracies

def make_dataloaders(train, val, test, batch_size=256):
    train_ds = ModelZooDataset(train)
    val_ds = ModelZooDataset(val)
    test_ds = ModelZooDataset(test)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_weights)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_weights)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_weights)
    return train_loader, val_loader, test_loader
