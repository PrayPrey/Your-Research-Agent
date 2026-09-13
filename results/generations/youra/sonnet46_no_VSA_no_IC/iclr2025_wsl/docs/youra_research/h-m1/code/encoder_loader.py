import os
import sys
import torch
import torch.nn as nn
from pathlib import Path
import config

_H_M1_CODE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, config.DWSNETS_PATH)
sys.path.insert(0, config.H_E1_CODE_DIR)
sys.path.insert(0, _H_M1_CODE)  # h-m1/code must be first to shadow h-e1/code modules


def load_gnn_nfn(ckpt_path: str = config.GNN_CKPT,
                 hidden_dim: int = config.GNN_HIDDEN_DIM,
                 num_layers: int = config.GNN_NUM_LAYERS) -> nn.Module:
    from encoders import GNNNFNEncoder
    encoder = GNNNFNEncoder(hidden_dim=hidden_dim, num_layers=num_layers)
    p = Path(ckpt_path)
    if p.exists():
        state = torch.load(str(p), map_location="cpu")
        sd = state.get("model_state_dict", state.get("state_dict", state))
        encoder.load_state_dict(sd, strict=False)
        print(f"GNN-NFN loaded from {ckpt_path}")
    else:
        print(f"GNN-NFN checkpoint not found at {ckpt_path} — using random init")
    return encoder.eval()


def load_flat_mlp(input_dim: int, ckpt_path: str = config.FLAT_CKPT) -> nn.Module:
    from encoders import FlatMLP
    encoder = FlatMLP(input_dim=input_dim, hidden_dim=256, num_layers=3)
    p = Path(ckpt_path)
    if p.exists():
        state = torch.load(str(p), map_location="cpu")
        sd = state.get("model_state_dict", state.get("state_dict", state))
        encoder.load_state_dict(sd, strict=False)
        print(f"FlatMLP loaded from {ckpt_path}")
    else:
        print(f"FlatMLP checkpoint not found — using random init")
    return encoder.eval()


def get_fc_layer_specs(sample_state_dict: dict):
    """Extract FC layer (weight, bias) shapes from state_dict (linear layers only)."""
    weight_keys = sorted([k for k in sample_state_dict if k.endswith(".weight")])
    fc_specs = []
    for wk in weight_keys:
        w = sample_state_dict[wk]
        if w.dim() == 2:  # linear layer only
            fc_specs.append((wk, w.shape))
    return fc_specs


def build_dwsnet_input(state_dict: dict, fc_specs: list):
    """Convert state_dict to DWSNets input format: (weights_tuple, biases_tuple).

    DWSNets expects:
      weights: Tuple of Tensor(B, d_in, d_out, channels=1)
      biases:  Tuple of Tensor(B, d_out, channels=1)
    where B=1 for single model.
    """
    weights = []
    biases = []
    for wk, _ in fc_specs:
        w = state_dict[wk]  # (d_out, d_in)
        bk = wk.replace(".weight", ".bias")
        b = state_dict.get(bk, torch.zeros(w.shape[0]))
        # DWSNets shape: (B=1, d_in, d_out, 1)
        w_fmt = w.T.unsqueeze(0).unsqueeze(-1)  # (1, d_in, d_out, 1)
        b_fmt = b.unsqueeze(0).unsqueeze(-1)    # (1, d_out, 1)
        weights.append(w_fmt)
        biases.append(b_fmt)
    return tuple(weights), tuple(biases)


class DWSNetsWrapper(nn.Module):
    """Wraps DWSModelForClassification for invariant embedding extraction."""

    def __init__(self, fc_specs: list, hidden_dim: int = 32, n_classes: int = 128):
        super().__init__()
        from nn.models import DWSModelForClassification
        weight_shapes = tuple((s[1], s[0]) for _, s in fc_specs)  # (d_in, d_out)
        bias_shapes = tuple(((s[0],),) for _, s in fc_specs)
        # flatten bias_shapes: DWSNets expects Tuple[Tuple[int]]
        bias_shapes_flat = tuple((s[0],) for _, s in fc_specs)
        self.model = DWSModelForClassification(
            weight_shapes=weight_shapes,
            bias_shapes=bias_shapes_flat,
            input_features=1,
            hidden_dim=hidden_dim,
            n_hidden=1,
            n_classes=n_classes,
            reduction="max",
        )
        self.fc_specs = fc_specs

    def forward(self, state_dict: dict) -> torch.Tensor:
        weights, biases = build_dwsnet_input(state_dict, self.fc_specs)
        out = self.model((weights, biases))  # (1, n_classes)
        return out.squeeze(0)  # (n_classes,)


def make_synthetic_fc_specs(layer_sizes=(64, 64, 64, 10)) -> list:
    """Create synthetic FC layer specs for DWSNets standalone test.

    CIFAR-10 CNN zoo has only 2 FC layers which is insufficient for DWSNets (requires M>2).
    We test DWSNets structural equivariance on synthetic 3-hidden-layer MLP weights instead.
    This is valid: equivariance is a structural property independent of the weight values.
    """
    specs = []
    for i in range(len(layer_sizes) - 1):
        in_dim = layer_sizes[i]
        out_dim = layer_sizes[i + 1]
        specs.append((f"fc{i}.weight", (out_dim, in_dim)))  # (out, in) as in state_dict
    return specs


def make_synthetic_state_dict(fc_specs: list) -> dict:
    """Create random weight tensors matching fc_specs."""
    from collections import OrderedDict
    sd = OrderedDict()
    for wk, shape in fc_specs:
        sd[wk] = torch.randn(*shape) * 0.1
        sd[wk.replace(".weight", ".bias")] = torch.randn(shape[0]) * 0.01
    return sd


def load_dwsnet(sample_state_dict: dict = None, hidden_dim: int = 32, n_classes: int = 128) -> tuple:
    """Build DWSNets wrapper. Uses synthetic MLP weights if zoo models have <3 FC layers.

    Returns (wrapper, synthetic_state_dicts_or_None).
    If synthetic, the second element is a list of state_dicts to use for verification.
    """
    fc_specs = get_fc_layer_specs(sample_state_dict) if sample_state_dict is not None else []
    use_synthetic = len(fc_specs) <= 2

    if use_synthetic:
        print(f"DWSNets: zoo has {len(fc_specs)} FC layers (need >2) — using synthetic 4-layer MLP for equivariance test")
        # 4-layer MLP: input(64) -> hidden(64) -> hidden(64) -> hidden(64) -> output(10)
        # This gives 4 weight matrices (M=4 > 2, satisfying DWSNets constraint)
        layer_sizes = (64, 64, 64, 64, 10)
        fc_specs = make_synthetic_fc_specs(layer_sizes)
        n_synthetic = 50  # test on 50 random synthetic networks, 20 perms each
        synthetic_sds = [make_synthetic_state_dict(fc_specs) for _ in range(n_synthetic)]
    else:
        synthetic_sds = None

    wrapper = DWSNetsWrapper(fc_specs=fc_specs, hidden_dim=hidden_dim, n_classes=n_classes)
    print(f"DWSNets loaded (random init, {len(fc_specs)} FC layers, structural equivariance)")
    return wrapper.eval(), synthetic_sds, fc_specs


def get_all_encoders(weight_dim: int, sample_state_dict: dict) -> dict:
    """Returns dict of encoders. 'dwsnet' entry is (model, synthetic_sds_or_None, fc_specs)."""
    encoders = {}
    encoders["gnn_nfn"] = load_gnn_nfn()
    encoders["flat_mlp"] = load_flat_mlp(weight_dim)
    try:
        dwsnet_model, synthetic_sds, fc_specs = load_dwsnet(sample_state_dict)
        encoders["dwsnet"] = (dwsnet_model, synthetic_sds, fc_specs)
    except Exception as e:
        print(f"DWSNets error: {e}")
        encoders["dwsnet"] = None
    return encoders
