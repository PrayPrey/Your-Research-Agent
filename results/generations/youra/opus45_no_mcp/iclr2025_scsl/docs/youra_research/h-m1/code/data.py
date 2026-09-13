import torch
from torch.utils.data import DataLoader
from torchvision import transforms

try:
    from wilds import get_dataset
    from wilds.common.data_loaders import get_train_loader, get_eval_loader
    WILDS_AVAILABLE = True
except ImportError:
    WILDS_AVAILABLE = False

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_transforms(eval_mode: bool) -> transforms.Compose:
    if eval_mode:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    return transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

def load_dataset(name: str, root_dir: str = "./data"):
    if not WILDS_AVAILABLE:
        raise ImportError("wilds package required: pip install wilds")
    return get_dataset(dataset=name, download=True, root_dir=root_dir)

def get_loaders(name: str, batch_size: int = 128, root_dir: str = "./data") -> dict:
    dataset = load_dataset(name, root_dir)
    train_data = dataset.get_subset("train", transform=get_transforms(False))
    val_data = dataset.get_subset("val", transform=get_transforms(True))
    test_data = dataset.get_subset("test", transform=get_transforms(True))

    train_loader = get_train_loader("standard", train_data, batch_size=batch_size)
    val_loader = get_eval_loader("standard", val_data, batch_size=batch_size)
    test_loader = get_eval_loader("standard", test_data, batch_size=batch_size)

    return {"train": train_loader, "val": val_loader, "test": test_loader}
