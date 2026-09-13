import os
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.datasets import CelebA as TorchCelebA


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# CelebA attribute indices (40 attributes total, 0-indexed)
# Blond_Hair = index 9, Male = index 20
CELEBA_ATTR_NAMES = [
    '5_o_Clock_Shadow', 'Arched_Eyebrows', 'Attractive', 'Bags_Under_Eyes',
    'Bald', 'Bangs', 'Big_Lips', 'Big_Nose', 'Black_Hair', 'Blond_Hair',
    'Blurry', 'Brown_Hair', 'Bushy_Eyebrows', 'Chubby', 'Double_Chin',
    'Eyeglasses', 'Goatee', 'Gray_Hair', 'Heavy_Makeup', 'High_Cheekbones',
    'Male', 'Mouth_Slightly_Open', 'Mustache', 'Narrow_Eyes', 'No_Beard',
    'Oval_Face', 'Pale_Skin', 'Pointy_Nose', 'Receding_Hairline', 'Rosy_Cheeks',
    'Sideburns', 'Smiling', 'Straight_Hair', 'Wavy_Hair', 'Wearing_Earrings',
    'Wearing_Hat', 'Wearing_Lipstick', 'Wearing_Necklace', 'Wearing_Necktie', 'Young'
]
SPURIOUS_ATTR = "Blond_Hair"   # index 9
CORE_ATTR = "Male"             # index 20
SPURIOUS_IDX = CELEBA_ATTR_NAMES.index(SPURIOUS_ATTR)
CORE_IDX = CELEBA_ATTR_NAMES.index(CORE_ATTR)

SPLIT_MAP = {"train": "train", "val": "valid", "test": "test"}


class CelebADataset(Dataset):
    def __init__(self, root: str, split: str, transform=None):
        torchvision_split = SPLIT_MAP.get(split, split)
        self._celeba = TorchCelebA(
            root=root,
            split=torchvision_split,
            target_type="attr",
            transform=transform,
            download=True,
        )

    def __len__(self) -> int:
        return len(self._celeba)

    def __getitem__(self, idx: int) -> dict:
        image, attrs = self._celeba[idx]
        return {
            "image": image,
            "core_label": int(attrs[CORE_IDX].item()),
            "spurious_label": int(attrs[SPURIOUS_IDX].item()),
        }


def get_celeba_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int,
    augment: bool = False,
) -> DataLoader:
    if augment:
        tf = transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    else:
        tf = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    dataset = CelebADataset(root=root, split=split, transform=tf)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=num_workers,
        pin_memory=True,
    )
