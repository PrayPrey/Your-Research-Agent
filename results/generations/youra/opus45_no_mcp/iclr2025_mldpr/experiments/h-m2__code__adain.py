import torch


def adain_style_transfer(content, style, alpha=1.0):
    """AdaIN: transfer style's channel-wise mean/std onto content."""
    eps = 1e-8
    c_mean = content.mean(dim=[2, 3], keepdim=True)
    c_std = content.std(dim=[2, 3], keepdim=True) + eps
    s_mean = style.mean(dim=[2, 3], keepdim=True)
    s_std = style.std(dim=[2, 3], keepdim=True) + eps

    normalized = (content - c_mean) / c_std
    stylized = normalized * s_std + s_mean
    out = alpha * stylized + (1 - alpha) * content
    return out.clamp(0, 1)
