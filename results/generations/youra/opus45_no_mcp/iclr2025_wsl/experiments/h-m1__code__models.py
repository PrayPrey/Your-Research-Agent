import torch
import torch.nn as nn
import torch.nn.functional as F

def flatten_weights(weights_dict):
    parts = [weights_dict[k].flatten() for k in sorted(weights_dict.keys())]
    return torch.cat(parts, dim=0)

def layer_wise_stats(weights_dict):
    all_stats = []
    for name in sorted(weights_dict.keys()):
        flat = weights_dict[name].flatten().float()
        all_stats.extend([flat.mean(), flat.std(), flat.min(), flat.max()])
    return torch.stack(all_stats)

class FlattenMLPEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim=256, embed_dim=128):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)

    def forward(self, weights_flat):
        h = F.relu(self.fc1(weights_flat))
        return self.fc2(h)

class LayerWiseEncoder(nn.Module):
    def __init__(self, num_layers, stats_per_layer=4, hidden_dim=256, embed_dim=128):
        super().__init__()
        input_dim = num_layers * stats_per_layer
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embed_dim)

    def compute_layer_stats(self, param):
        flat = param.flatten().float()
        return torch.stack([flat.mean(), flat.std(), flat.min(), flat.max()])

    def forward(self, weights_dict):
        layer_stats = [self.compute_layer_stats(weights_dict[name]) for name in sorted(weights_dict.keys())]
        x = torch.cat(layer_stats, dim=-1)
        h = F.relu(self.fc1(x))
        return self.fc2(h)

class AccuracyPredictor(nn.Module):
    def __init__(self, embed_dim=128, hidden_dim=64):
        super().__init__()
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)

    def forward(self, embedding):
        x = F.relu(self.fc1(embedding))
        return self.fc2(x).squeeze(-1)

class FullModel(nn.Module):
    def __init__(self, encoder, predictor, method):
        super().__init__()
        self.encoder = encoder
        self.predictor = predictor
        self.method = method

    def forward(self, weights_input, device="cuda"):
        if self.method == "flatten":
            emb = self.encoder(weights_input)
        else:
            emb = torch.stack([self.encoder({k: v.to(device) for k, v in wd.items()}) for wd in weights_input])
        return self.predictor(emb)
