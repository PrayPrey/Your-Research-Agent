"""
Training script for GNN fingerprinting model.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch_geometric.data import Data, Batch
from torch_geometric.loader import DataLoader
import numpy as np
from tqdm import tqdm
import os
import json
from typing import Dict, List, Tuple

import config
from models.gnn_fingerprinter import GNNFingerprinter, model_to_graph
from data_generator import SimpleMLPModel, SimpleCNNModel
from utils.evaluation import MetricsTracker


class TripletLoss(nn.Module):
    """Triplet loss for contrastive learning."""
    def __init__(self, margin=0.5):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        pos_dist = torch.sum((anchor - positive) ** 2, dim=-1)
        neg_dist = torch.sum((anchor - negative) ** 2, dim=-1)
        loss = torch.relu(pos_dist - neg_dist + self.margin)
        return loss.mean()


class SupervisedContrastiveLoss(nn.Module):
    """Supervised contrastive loss."""
    def __init__(self, temperature=0.1):
        super().__init__()
        self.temperature = temperature

    def forward(self, features, labels):
        device = features.device
        batch_size = features.shape[0]

        # Normalize features
        features = F.normalize(features, p=2, dim=1)

        # Compute similarity matrix
        similarity_matrix = torch.matmul(features, features.T) / self.temperature

        # Create mask for positive pairs
        labels = labels.contiguous().view(-1, 1)
        mask = torch.eq(labels, labels.T).float().to(device)

        # Mask out self-similarity
        logits_mask = torch.scatter(
            torch.ones_like(mask),
            1,
            torch.arange(batch_size).view(-1, 1).to(device),
            0
        )
        mask = mask * logits_mask

        # Compute log probabilities
        exp_logits = torch.exp(similarity_matrix) * logits_mask
        log_prob = similarity_matrix - torch.log(exp_logits.sum(1, keepdim=True))

        # Compute mean of log-likelihood over positive pairs
        mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + 1e-8)

        loss = -mean_log_prob_pos.mean()

        return loss


def load_models_as_graphs(dataset_info: Dict, split: str = 'train') -> List[Tuple[Data, str, str]]:
    """Load models and convert to graph representations."""
    graphs = []

    # Determine which models to load based on split
    if split == 'train':
        # Use base models and some variants for training
        model_infos = dataset_info['base_models'][:40]  # 80% for training
        variant_infos = []
        for v in dataset_info['symmetry_variants']:
            base_id = v['base_id']
            if any(base_id == m['id'] for m in model_infos):
                variant_infos.append(v)
        model_infos.extend(variant_infos[:len(variant_infos)*4//5])

    elif split == 'val':
        model_infos = dataset_info['base_models'][40:]  # 20% for validation
        variant_infos = []
        for v in dataset_info['symmetry_variants']:
            base_id = v['base_id']
            if any(base_id == m['id'] for m in model_infos):
                variant_infos.append(v)
        model_infos.extend(variant_infos[len(variant_infos)*4//5:])

    else:  # test
        model_infos = dataset_info['base_models'] + dataset_info['symmetry_variants']
        model_infos.extend(dataset_info['backdoored_models'])

    print(f"Loading {len(model_infos)} models for {split} split...")

    for model_info in tqdm(model_infos, desc=f"Converting {split} models to graphs"):
        filepath = model_info['filepath']
        model_id = model_info['id']
        arch = model_info['architecture']

        # Load model weights
        state_dict = torch.load(filepath, map_location='cpu')

        # Convert to graph
        graph = model_to_graph(state_dict, arch)
        graphs.append((graph, model_id, arch))

    return graphs


def create_triplet_batches(
    graphs: List[Tuple[Data, str, str]],
    dataset_info: Dict,
    batch_size: int = 16
) -> List[Tuple[Batch, Batch, Batch]]:
    """Create triplet batches for training."""
    # Build mapping from base_id to variants
    base_to_variants = {}
    for variant in dataset_info['symmetry_variants']:
        base_id = variant['base_id']
        if base_id not in base_to_variants:
            base_to_variants[base_id] = []
        base_to_variants[base_id].append(variant['id'])

    # Build id to graph mapping
    id_to_graph = {model_id: graph for graph, model_id, arch in graphs}

    triplets = []

    # For each base model, create triplets with its variants
    base_models = [g for g in graphs if any(g[1] == m['id'] for m in dataset_info['base_models'])]

    for anchor_graph, anchor_id, anchor_arch in base_models:
        # Get positive samples (variants of the same base)
        if anchor_id in base_to_variants:
            variant_ids = base_to_variants[anchor_id]
            for variant_id in variant_ids[:3]:  # Limit positives per base
                if variant_id in id_to_graph:
                    positive_graph = id_to_graph[variant_id]

                    # Get negative sample (different base model)
                    negative_candidates = [g for g in base_models if g[1] != anchor_id and g[2] == anchor_arch]
                    if negative_candidates:
                        negative_graph, _, _ = negative_candidates[np.random.randint(len(negative_candidates))]
                        triplets.append((anchor_graph, positive_graph, negative_graph))

    # Shuffle triplets
    np.random.shuffle(triplets)

    # Create batches
    batches = []
    for i in range(0, len(triplets), batch_size):
        batch_triplets = triplets[i:i+batch_size]
        if len(batch_triplets) < batch_size // 2:
            continue

        anchors = Batch.from_data_list([t[0] for t in batch_triplets])
        positives = Batch.from_data_list([t[1] for t in batch_triplets])
        negatives = Batch.from_data_list([t[2] for t in batch_triplets])

        batches.append((anchors, positives, negatives))

    return batches


def train_epoch(
    model: GNNFingerprinter,
    triplet_batches: List[Tuple[Batch, Batch, Batch]],
    optimizer: optim.Optimizer,
    triplet_loss_fn: TripletLoss,
    device: torch.device
) -> float:
    """Train for one epoch."""
    model.train()
    total_loss = 0.0

    for anchors, positives, negatives in tqdm(triplet_batches, desc="Training"):
        anchors = anchors.to(device)
        positives = positives.to(device)
        negatives = negatives.to(device)

        optimizer.zero_grad()

        # Forward pass
        anchor_emb = model(anchors)
        positive_emb = model(positives)
        negative_emb = model(negatives)

        # Compute loss
        loss = triplet_loss_fn(anchor_emb, positive_emb, negative_emb)

        # Backward pass
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(triplet_batches)


def train_gnn_fingerprinter(dataset_info: Dict) -> GNNFingerprinter:
    """Train the GNN fingerprinting model."""
    device = config.DEVICE
    print(f"Using device: {device}")

    # Load data
    train_graphs = load_models_as_graphs(dataset_info, 'train')
    val_graphs = load_models_as_graphs(dataset_info, 'val')

    # Create model
    node_feature_dim = 4
    edge_feature_dim = 3

    model = GNNFingerprinter(
        node_feature_dim=node_feature_dim,
        edge_feature_dim=edge_feature_dim,
        hidden_dim=config.GNN_HIDDEN_DIM,
        num_layers=config.GNN_NUM_LAYERS,
        embedding_dim=config.GNN_EMBEDDING_DIM,
        pooling=config.GNN_POOLING
    ).to(device)

    # Optimizer and loss
    optimizer = optim.AdamW(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY)
    triplet_loss_fn = TripletLoss(margin=config.TRIPLET_MARGIN)

    # Training history
    history = {
        'train_loss': [],
        'val_loss': []
    }

    # Training loop
    best_val_loss = float('inf')

    for epoch in range(config.NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{config.NUM_EPOCHS}")

        # Create triplet batches
        train_batches = create_triplet_batches(train_graphs, dataset_info, config.BATCH_SIZE)

        # Train
        train_loss = train_epoch(model, train_batches, optimizer, triplet_loss_fn, device)
        history['train_loss'].append(train_loss)

        print(f"Train Loss: {train_loss:.4f}")

        # Validation
        if (epoch + 1) % 5 == 0:
            val_batches = create_triplet_batches(val_graphs, dataset_info, config.BATCH_SIZE)
            model.eval()
            val_loss = 0.0

            with torch.no_grad():
                for anchors, positives, negatives in val_batches:
                    anchors = anchors.to(device)
                    positives = positives.to(device)
                    negatives = negatives.to(device)

                    anchor_emb = model(anchors)
                    positive_emb = model(positives)
                    negative_emb = model(negatives)

                    loss = triplet_loss_fn(anchor_emb, positive_emb, negative_emb)
                    val_loss += loss.item()

            val_loss = val_loss / len(val_batches) if val_batches else 0.0
            history['val_loss'].append(val_loss)
            print(f"Val Loss: {val_loss:.4f}")

            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                os.makedirs(config.CHECKPOINTS_DIR, exist_ok=True)
                torch.save(model.state_dict(), os.path.join(config.CHECKPOINTS_DIR, 'best_gnn_model.pt'))

    # Save training history
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    with open(os.path.join(config.RESULTS_DIR, 'gnn_training_history.json'), 'w') as f:
        json.dump(history, f, indent=2)

    return model, history


if __name__ == "__main__":
    torch.manual_seed(config.SEED)
    np.random.seed(config.SEED)

    # Load dataset info
    with open(os.path.join(config.DATA_DIR, 'dataset_info.json'), 'r') as f:
        dataset_info = json.load(f)

    # Train model
    model, history = train_gnn_fingerprinter(dataset_info)
    print("Training complete!")
