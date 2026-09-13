import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms


class SyntheticWaterbirds(Dataset):
    """Synthetic Waterbirds for POC when download fails."""
    def __init__(self, split='train'):
        if split == 'train':
            self.n = 800
        elif split == 'val':
            self.n = 100
        else:
            self.n = 600

        self.transform = transforms.Compose([
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def __len__(self):
        return self.n

    def __getitem__(self, idx):
        torch.manual_seed(idx)
        image = torch.randn(3, 224, 224)
        image = self.transform(image)

        label = idx % 2
        group = idx % 4

        metadata = torch.tensor([group, label], dtype=torch.long)
        return image, label, metadata


def get_waterbirds_dataloader(split='train', batch_size=64, num_workers=4):
    """
    Load synthetic Waterbirds (POC fallback).

    Returns:
        DataLoader yielding (images, labels, metadata) where:
        - images: [B, 3, 224, 224] normalized
        - labels: [B] binary (0=landbird, 1=waterbird)
        - metadata: [B, 2] with [group_id, label]
    """
    dataset = SyntheticWaterbirds(split)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=(split=='train'), num_workers=num_workers)
    return loader


if __name__ == '__main__':
    loader = get_waterbirds_dataloader('train')
    batch = next(iter(loader))
    images, labels, metadata = batch
    print(f"Images: {images.shape}")
    print(f"Labels: {labels.shape}")
    print(f"Group IDs: {metadata[:, 0].shape}, range: {metadata[:, 0].min()}-{metadata[:, 0].max()}")
