"""Gradient Reversal Layer for adversarial training."""
import torch
import torch.nn as nn
from torch.autograd import Function
import math


class RevGradFn(Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.alpha * grad_output, None


class GradientReversalLayer(nn.Module):
    def __init__(self, alpha: float = 0.0):
        super().__init__()
        self.alpha = alpha

    def forward(self, x):
        return RevGradFn.apply(x, self.alpha)

    def set_alpha(self, alpha: float):
        self.alpha = alpha


def grl_alpha_schedule(step: int, total_steps_epoch1: int) -> float:
    """DANN sigmoid schedule: 0 -> 1 over first epoch."""
    if total_steps_epoch1 <= 0:
        return 1.0
    if step >= total_steps_epoch1:
        return 1.0
    p = step / total_steps_epoch1
    return float(2.0 / (1.0 + math.exp(-10 * p)) - 1.0)
