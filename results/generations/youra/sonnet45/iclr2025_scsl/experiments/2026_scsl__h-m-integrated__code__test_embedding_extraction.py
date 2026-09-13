"""Test embedding extraction to debug shape issue."""

import sys
from pathlib import Path
import torch
import numpy as np
from torch.utils.data import DataLoader

current_dir = Path(__file__).parent.absolute()
h_e1_path = (current_dir.parent.parent / 'h-e1' / 'code').absolute()
sys.path.insert(0, str(h_e1_path))

from models.simclr import SimCLR
from data.dataset import WaterbirdsDataset, get_eval_transforms

# Load config
import importlib.util
config_spec = importlib.util.spec_from_file_location("config", current_dir / "config.py")
config_module = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_module)
DATA_CONFIG = config_module.DATA_CONFIG

# Load model
model = SimCLR(
    encoder_name='resnet50',
    projection_dim=128,
    pretrained=False
).to('cuda')

checkpoint = torch.load('checkpoints/simclr/seed_0/final.pt', map_location='cuda')
model.load_state_dict(checkpoint['model_state_dict'])

# Load dataset
eval_transform = get_eval_transforms()
test_dataset = WaterbirdsDataset(
    root_dir=DATA_CONFIG['root_dir'],
    split='test',
    transform=eval_transform
)

test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

# Test extraction
model.eval()
with torch.no_grad():
    for batch_data in test_loader:
        images, labels, groups = batch_data
        print(f'Batch data type: {type(batch_data)}')
        print(f'Images shape: {images.shape}')
        print(f'Labels shape: {labels.shape}')
        print(f'Groups shape: {groups.shape}')

        # Get embeddings
        images_gpu = images.to('cuda')
        print(f'Images GPU shape: {images_gpu.shape}')

        features = model.encoder(images_gpu)
        print(f'Features shape: {features.shape}')
        print(f'Features dtype: {features.dtype}')
        print(f'Features device: {features.device}')
        break

print('\\nExtraction test successful!')
