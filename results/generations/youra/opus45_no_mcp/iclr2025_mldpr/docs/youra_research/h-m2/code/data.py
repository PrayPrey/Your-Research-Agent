import os
import random
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision
import torchvision.transforms as T
from PIL import Image
from tqdm import tqdm

from adain import adain_style_transfer
import config


def get_cifar10_loaders(batch_size):
    train_transform = T.Compose([
        T.RandomCrop(config.CROP_SIZE, padding=config.CROP_PADDING),
        T.RandomHorizontalFlip(),
        T.ToTensor(),
    ])
    test_transform = T.Compose([T.ToTensor()])

    train_set = torchvision.datasets.CIFAR10(
        root=config.DATA_DIR, train=True, download=True, transform=train_transform
    )
    test_set = torchvision.datasets.CIFAR10(
        root=config.DATA_DIR, train=False, download=True, transform=test_transform
    )

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
    return train_loader, test_loader


def load_dtd_images(dtd_dir):
    """Load all DTD images with category labels. Returns list of (tensor, category_idx)."""
    transform = T.Compose([
        T.Resize(32),
        T.CenterCrop(32),
        T.ToTensor(),
    ])

    images_with_labels = []
    categories = sorted([d for d in os.listdir(dtd_dir) if os.path.isdir(os.path.join(dtd_dir, d))])

    for cat_idx, cat_name in enumerate(categories):
        cat_path = os.path.join(dtd_dir, cat_name)
        for fname in os.listdir(cat_path):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(cat_path, fname)
                try:
                    img = Image.open(img_path).convert('RGB')
                    tensor = transform(img)
                    images_with_labels.append((tensor, cat_idx))
                except Exception:
                    continue

    return images_with_labels, len(categories)


class StylizedCIFAR10(Dataset):
    def __init__(self, cifar_test, dtd_images_with_labels, seed):
        self.stylized_images = []
        self.shape_labels = []
        self.texture_labels = []

        rng = random.Random(seed)
        dtd_images, dtd_labels = zip(*dtd_images_with_labels)
        dtd_images = list(dtd_images)
        dtd_labels = list(dtd_labels)

        print("Generating Stylized-CIFAR-10 conflict stimuli...")
        for i in tqdm(range(len(cifar_test)), desc="Stylizing"):
            content_img, shape_label = cifar_test[i]
            dtd_idx = rng.randint(0, len(dtd_images) - 1)
            style_img = dtd_images[dtd_idx]
            texture_label = dtd_labels[dtd_idx]

            stylized = adain_style_transfer(
                content_img.unsqueeze(0), style_img.unsqueeze(0), alpha=1.0
            ).squeeze(0)

            self.stylized_images.append(stylized)
            self.shape_labels.append(shape_label)
            self.texture_labels.append(texture_label)

    def __getitem__(self, idx):
        return self.stylized_images[idx], self.shape_labels[idx], self.texture_labels[idx]

    def __len__(self):
        return len(self.stylized_images)


def build_stylized_cifar10(cifar_test, dtd_images_with_labels, seed):
    return StylizedCIFAR10(cifar_test, dtd_images_with_labels, seed)


def get_conflict_loader(stylized_dataset, batch_size):
    return DataLoader(stylized_dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
