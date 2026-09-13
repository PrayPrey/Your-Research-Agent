"""CMNIST data loader with spurious feature labels."""
import torch
import numpy as np
from torchvision import datasets, transforms
from torch.utils.data import Dataset, DataLoader


class ColoredMNIST(Dataset):
    """MNIST with color spurious correlation."""

    def __init__(self, root, train=True, spurious_correlation=0.95, download=True):
        self.mnist = datasets.MNIST(root, train=train, download=download)
        self.spurious_correlation = spurious_correlation
        self.transform = transforms.ToTensor()

    def __len__(self):
        return len(self.mnist)

    def __getitem__(self, idx):
        img, label = self.mnist[idx]
        img = self.transform(img)

        # Color corruption: correlate with label
        if np.random.rand() < self.spurious_correlation:
            color = label
        else:
            color = np.random.randint(10)

        # Apply color (RGB channels)
        # Color mapping: 0-9 → different RGB biases
        color_map = torch.tensor([
            [1.0, 0.0, 0.0],  # 0: red
            [0.0, 1.0, 0.0],  # 1: green
            [0.0, 0.0, 1.0],  # 2: blue
            [1.0, 1.0, 0.0],  # 3: yellow
            [1.0, 0.0, 1.0],  # 4: magenta
            [0.0, 1.0, 1.0],  # 5: cyan
            [0.5, 0.5, 0.0],  # 6: olive
            [0.5, 0.0, 0.5],  # 7: purple
            [0.0, 0.5, 0.5],  # 8: teal
            [0.5, 0.5, 0.5],  # 9: gray
        ])

        color_rgb = color_map[color]
        colored_img = img * color_rgb.view(3, 1, 1)

        return colored_img, label, color


def get_dataloader(data_config, train=False):
    """Create CMNIST dataloader."""
    spurious_corr = data_config['spurious_train_correlation'] if train else data_config['spurious_test_correlation']

    dataset = ColoredMNIST(
        root=data_config['data_path'],
        train=train,
        spurious_correlation=spurious_corr,
        download=data_config['download']
    )

    loader = DataLoader(
        dataset,
        batch_size=data_config['batch_size'],
        shuffle=train,
        num_workers=data_config['num_workers'],
        pin_memory=True
    )

    return loader


def get_spurious_labels(dataset):
    """Extract spurious labels from dataset."""
    spurious_labels = []
    for i in range(len(dataset)):
        _, _, color = dataset[i]
        spurious_labels.append(color)
    return np.array(spurious_labels)
