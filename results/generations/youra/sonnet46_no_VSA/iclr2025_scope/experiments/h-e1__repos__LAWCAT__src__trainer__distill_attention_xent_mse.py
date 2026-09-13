"""
Custom trainer class for distilling attentions ("attention transfer"). Can substitute for Hugging Face trainer.

In this implementation we support using either just the softmax attention outputs, or the softmax attention weights.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange
from .default_lm import OurTrainer as DefaultTrainer
from .utils import decode_samples

def chain_order_loss(A: torch.Tensor) -> torch.Tensor:
    """
    A has shape (N, L), and we want:
        A[:,0] > A[:,1] > A[:,2] > ... > A[:,L-1].
    That is, each column is strictly larger than the next one.

    This function returns a scalar loss penalizing any violation,
    i.e. whenever A[:,k+1] >= A[:,k].
    """
    # diff will be (N, L-1), where diff[:,k] = A[:,k+1] - A[:,k]
    diff = torch.diff(A, dim=1)  # shape: (N, L-1)
    
    # We want each diff < 0, so we penalize max(0, diff)
    # Summation => a single scalar
    penalty = F.relu(diff)  # same as clamp(diff, min=0)
    return penalty.sum()

class OurTrainer(DefaultTrainer):
    """
    Custom trainer class for distilling attentions. 
    - We compute and store the attention outputs and/or weights for each head and layer,
      for both the "teacher" softmax attentions and "student" learnable subquadratic attentions
    - We then train the student layers to minimize either MSE(outputs) or CrossEntropy(weights)
    """
    def __init__(self,
                 model: nn.Module,
                 metric_for_best_model: str = 'distill/eval/loss',
                 mse_factor: float = 1e3,
                 xent_factor: float = 0,
                 reg_factor: float = 0,
                 **kwargs: any):
        super().__init__(model=model, 
                         metric_for_best_model=metric_for_best_model,
                         **kwargs)
        # self.criterion_xent = nn.CrossEntropyLoss(reduction='mean')
        self.criterion_xent = nn.KLDivLoss(reduction='batchmean')
        self.criterion_mse = nn.MSELoss(reduction='mean')
        self.mse_factor = mse_factor
        self.xent_factor = xent_factor
        self.reg_factor = reg_factor
        self.compute_loss_backprop = False  # Whether we backprop in self.compute_loss
        self.distill_loss_coef = kwargs.get('distill_loss_coef', 1.0)
        self.ans_factor = kwargs.get('ans_factor', 0.0)

    def compute_loss(self, model: nn.Module, data: dict[torch.Tensor],
                     sample_idx: int = None, cur_steps: int = None, **kwargs: any,) -> tuple[torch.Tensor, dict[any]]:
        """
        Attention distillation ("attention transfer")
        - For each layer and head, get attentions and train to 
          minimize some combo of MSE and cross-entropy loss
        """
        inputs = {k: v.to(model.device) for k, v in data.items() if k == 'input_ids' or k == 'attention_mask'}
        outputs = model(**inputs, output_attentions=True, use_cache=False)
        # outputs = model(**inputs, output_attentions=True, use_cache=False, cur_steps=cur_steps)
        outputs = outputs.get('attentions')

        # Attentions are tuple[tuple[torch.Tensor, torch.Tensor]]
        # n_layers x (predicted_attns, true_attns)
        # predicted_attns and true_attns are shape (batch, n_heads, q_len, k_len)
        loss_mse = 0
        loss_xent = 0
        n_layers = 0  # Number of layers to distill
        softmax_layers = []
        for layer_idx, attns in enumerate(outputs):
            if attns is not None:
                if len(attns) != 2:
                    attns = attns.cpu()
                else:
                    # if self.xent_factor > 0:
                    #     # Cross-entropy loss
                    #     a_pred, a_true = attns[0]
                    #     a_pred = a_pred.clamp(min=1e-12).log()  # nn.CrossEntropy assumes unnormalized logits
                    #     k_len = a_true.shape[-1]  # batch, n_heads, q_len, k_len
                    #     # Compute mean cross-entropy over all queries
                    #     a_pred = a_pred.contiguous().view(-1, k_len)
                    #     a_true = a_true.contiguous().view(-1, k_len)
                    #     loss_xent += self.criterion_xent(a_pred, a_true)
                    if self.mse_factor > 0:
                        # breakpoint()
                        label_mask = torch.where(data['input_ids'] == 128009, 
                                                torch.tensor(0), 
                                                torch.tensor(1)).float().to(attns[1][0].device)
                        # breakpoint()
                        y_pred, y_true = (x.float() * label_mask[...,None] for x in attns[1])
                        # y_pred = attns[1][0].float()
                        # y_true = attns[1][1].float()
                        if self.distill_loss_coef == 'layer_wise':
                            distill_loss_coef = layer_idx
                        else:
                            distill_loss_coef = 1.0
                        if self.ans_factor > 0:
                            label_mask = data['labels'] != -100
                            ans_factor = (label_mask * (self.ans_factor - 1) + 1).float().to(y_pred.device)
                            # loss_mse += ((y_pred - y_true).pow(2).mean(dim=-1) * ans_factor).mean() * distill_loss_coef
                            per_token_error = F.mse_loss(y_pred, y_true, reduction='none').mean(dim=-1)  # [B, N]
                            loss_mse = (per_token_error * ans_factor).sum() / ans_factor.sum()
                        else:
                            loss_mse += self.criterion_mse(y_pred, y_true) * distill_loss_coef
                        # loss_mse += self.criterion_mse(*attns[1])
                        if self.xent_factor > 0:
                            y_dist_log = F.log_softmax(y_pred, dim=-1)
                            y_dist = F.softmax(y_true, dim=-1)
                            loss_xent += self.criterion_xent(y_dist_log, y_dist) * distill_loss_coef
                    n_layers += distill_loss_coef
            else:
                softmax_layers.append(layer_idx)
        if n_layers > 0:
            loss_xent = loss_xent / n_layers * self.xent_factor
            loss_mse = loss_mse / n_layers * self.mse_factor
        loss_mask_reg = torch.tensor(0.0, device=model.device)
        if self.reg_factor > 0:
            for n, p in model.named_parameters():
                if 'window_diff_mask' in n:
                    loss_mask_reg += chain_order_loss(p)
            loss_mask_reg *= self.reg_factor
        # print(f"Losses: xent={loss_xent.item() if self.xent_factor > 0 else 0}, mse={loss_mse.item() if self.mse_factor > 0 else 0}, mask_reg={loss_mask_reg.item()}")
        loss = loss_xent + loss_mse + loss_mask_reg
        if 'position_ids' in data:
            outputs = {'loss_xent': loss_xent.item() if self.xent_factor > 0 else 0,
                       'loss_mse': loss_mse.item() if self.mse_factor > 0 else 0,
                       'input_len': data['position_ids'].shape[1],
                       'position_ids': data['position_ids'][0].detach().cpu().numpy(),
                       'mse_factor': self.mse_factor,
                       'xent_factor': self.xent_factor,}
        else:
            outputs = {'loss_xent': loss_xent.item() if self.xent_factor > 0 else 0,
                       'loss_mse': loss_mse.item() if self.mse_factor > 0 else 0, 
                       'mse_factor': self.mse_factor, 
                       'xent_factor': self.xent_factor}
        if self.reg_factor > 0:
            outputs['loss_mask_reg'] = loss_mask_reg.item()
        return loss, outputs
