"""NFN encoder (C3) — structured equivariance via AllanYangZhou/nfn.

Only conv layers fed to NFN (FC layers break NPLinear spatial ops).
FC layers handled via invariant sum-pool (DeepSets style) and concatenated.
"""
import torch
import torch.nn as nn

try:
    from nfn import layers
    from nfn.common import network_spec_from_wsfeat, WeightSpaceFeatures
    NFN_AVAILABLE = True
except ImportError:
    NFN_AVAILABLE = False

# Conv weight keys in order
CONV_KEYS_W = ["module_list.0.weight", "module_list.3.weight", "module_list.6.weight"]
CONV_KEYS_B = ["module_list.0.bias", "module_list.3.bias", "module_list.6.bias"]
FC_KEYS_W = ["module_list.9.weight", "module_list.11.weight"]
FC_KEYS_B = ["module_list.9.bias", "module_list.11.bias"]


def _conv_state_dict_to_wsfeat(state_dict: dict):
    """WeightSpaceFeatures from conv layers only.
    NFN requires (batch, nfn_in_channels, C_out, C_in, kH, kW) = 6D for conv,
    and (batch, nfn_in_channels, C_out) = 3D for bias.
    """
    # unsqueeze(0) adds batch dim, unsqueeze(1) adds nfn_channels=1 dim
    weights = [state_dict[k].unsqueeze(0).unsqueeze(1) for k in CONV_KEYS_W]
    biases = [state_dict[k].unsqueeze(0).unsqueeze(1) for k in CONV_KEYS_B]
    return WeightSpaceFeatures(weights, biases)


def state_dict_to_wsfeat(state_dict: dict):
    """Public API — returns wsfeat for ALL layers (conv + FC) for test compatibility.
    Note: this wsfeat is only used for shape checks; NFN forward only uses conv wsfeat."""
    if not NFN_AVAILABLE:
        raise ImportError("nfn not installed. Run: pip install nfn")
    all_keys_w = CONV_KEYS_W + FC_KEYS_W
    all_keys_b = CONV_KEYS_B + FC_KEYS_B
    weights = [state_dict[k].unsqueeze(0) for k in all_keys_w]
    biases = [state_dict[k].unsqueeze(0) for k in all_keys_b]
    return WeightSpaceFeatures(weights, biases)


def get_network_spec(sample_state_dict: dict):
    """Network spec from conv-only wsfeat (what NFN actually needs)."""
    if not NFN_AVAILABLE:
        raise ImportError("nfn not installed. Run: pip install nfn")
    conv_wsfeat = _conv_state_dict_to_wsfeat(sample_state_dict)
    return network_spec_from_wsfeat(conv_wsfeat)


class NFNEncoder(nn.Module):
    """NFN (conv layers) + invariant FC summary, concatenated into embed_dim."""
    def __init__(self, network_spec, sample_wsfeat, nfn_channels=32, embed_dim=128):
        super().__init__()
        nfn_embed = embed_dim * 3 // 4  # 96 dims from NFN
        fc_embed = embed_dim - nfn_embed   # 32 dims from FC

        nfn_pre = nn.Sequential(
            layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, nfn_channels, nfn_channels),
            layers.TupleOp(nn.ReLU()),
            layers.HNPPool(network_spec),
            nn.Flatten(),
        )
        # Compute actual output size with a forward pass
        with torch.no_grad():
            actual_num_outs = nfn_pre(sample_wsfeat).shape[-1]

        self.nfn_trunk = nn.Sequential(
            *list(nfn_pre.children()),
            nn.Linear(actual_num_outs, nfn_embed),
        )
        # FC summary: invariant summaries
        # FC1 weight (20, 36): col permutation from conv3 → must use sum(dim=1) (row-sum, col-invariant)
        # FC2 weight (10, 20): no permutation → use sum(dim=0) + sum(dim=1)
        # FC1: 20 (sum over cols); FC2: 20+10=30; biases: 20+10=30; total = 20+30+30=80
        self.fc_proj = nn.Linear(80, fc_embed)
        self.proj = nn.Linear(nfn_embed + fc_embed, embed_dim)

    def forward(self, state_dict: dict) -> torch.Tensor:
        conv_wsfeat = _conv_state_dict_to_wsfeat(state_dict)
        nfn_out = self.nfn_trunk(conv_wsfeat)  # (1, nfn_embed) or (nfn_embed,)
        if nfn_out.dim() > 1:
            nfn_out = nfn_out.squeeze(0)

        # FC summary — invariant to column permutations from conv3 output permutation
        fc1_w = state_dict[FC_KEYS_W[0]]  # (20, 36) — columns permuted by conv3 perm
        fc2_w = state_dict[FC_KEYS_W[1]]  # (10, 20) — not permuted by S_n³
        fc_cat = torch.cat([
            fc1_w.sum(dim=1),               # (20,) sum over cols → col-perm invariant
            fc2_w.sum(dim=0),               # (20,) sum over rows → row-perm invariant
            fc2_w.sum(dim=1),               # (10,) sum over cols → col-perm invariant
            state_dict[FC_KEYS_B[0]],       # (20,) FC1 bias — not permuted by S_n³ conv perms
            state_dict[FC_KEYS_B[1]],       # (10,) output bias — fixed
        ], dim=0)  # (80,)
        fc_out = self.fc_proj(fc_cat)

        combined = torch.cat([nfn_out, fc_out], dim=0)  # (nfn_embed + fc_embed,)
        return self.proj(combined)  # (embed_dim,)


def build_nfn_encoder(network_spec, sample_state_dict: dict = None, nfn_channels: int = 32, embed_dim: int = 128) -> NFNEncoder:
    if not NFN_AVAILABLE:
        raise ImportError("nfn not installed. Run: pip install nfn")
    if sample_state_dict is None:
        raise ValueError("sample_state_dict required to measure NFN output size")
    sample_wsfeat = _conv_state_dict_to_wsfeat(sample_state_dict)
    return NFNEncoder(network_spec, sample_wsfeat, nfn_channels=nfn_channels, embed_dim=embed_dim)


def encode_nfn(nfn_model: NFNEncoder, state_dict: dict) -> torch.Tensor:
    """state_dict -> (embed_dim,)."""
    with torch.no_grad():
        return nfn_model(state_dict)
