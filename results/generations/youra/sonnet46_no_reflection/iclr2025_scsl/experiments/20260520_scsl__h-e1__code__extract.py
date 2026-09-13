"""Penultimate-layer embedding extraction."""
import os
import sys
import argparse
import numpy as np
import torch
import yaml
from typing import Tuple, Dict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.datasets import WaterBirdsDataset, CelebADataset, get_dataloader
from models.resnet import ERMModel, load_checkpoint


def extract_embeddings(model: ERMModel, dataloader, device: torch.device
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    feature_extractor = model.get_feature_extractor()
    feature_extractor.eval()
    embs, labs, grps = [], [], []
    with torch.no_grad():
        for x, y, g in dataloader:
            feat = feature_extractor(x.to(device))   # (B, 2048, 1, 1)
            feat = feat.squeeze(-1).squeeze(-1)        # (B, 2048)
            embs.append(feat.cpu().numpy())
            labs.append(y.numpy())
            grps.append(g.numpy())
    embeddings = np.concatenate(embs).astype(np.float32)  # (N, 2048)
    assert embeddings.shape[1] == 2048, f'Wrong embedding dim: {embeddings.shape[1]}'
    print(f'Embeddings extracted: shape {embeddings.shape}')
    return embeddings, np.concatenate(labs), np.concatenate(grps)


def run_extraction(ckpt_path: str, dataset_name: str, data_dir: str,
                   output_dir: str, batch_size: int = 256) -> Dict[str, str]:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ERMModel(num_classes=2, pretrained=True)
    load_checkpoint(model, ckpt_path, device)
    model = model.to(device)

    if dataset_name == 'waterbirds':
        dataset = WaterBirdsDataset(data_dir, 'train', augment=False)
    elif dataset_name == 'celeba':
        dataset = CelebADataset(data_dir, 'train', augment=False)
    else:
        raise ValueError(f'Unknown dataset: {dataset_name}')

    loader = get_dataloader(dataset, batch_size, shuffle=False, num_workers=4)
    embeddings, labels, group_ids = extract_embeddings(model, loader, device)

    os.makedirs(output_dir, exist_ok=True)
    emb_path = os.path.join(output_dir, f'{dataset_name}_epoch5.npy')
    lab_path = os.path.join(output_dir, f'{dataset_name}_labels.npy')
    grp_path = os.path.join(output_dir, f'{dataset_name}_group_ids.npy')

    np.save(emb_path, embeddings)
    np.save(lab_path, labels)
    np.save(grp_path, group_ids)
    print(f'Saved: {emb_path}, {lab_path}, {grp_path}')
    return {'embeddings': emb_path, 'labels': lab_path, 'group_ids': grp_path}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', required=True)
    parser.add_argument('--dataset', required=True, choices=['waterbirds', 'celeba'])
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--batch_size', type=int, default=256)
    args = parser.parse_args()
    run_extraction(args.ckpt, args.dataset, args.data_dir, args.output_dir, args.batch_size)


if __name__ == '__main__':
    main()
