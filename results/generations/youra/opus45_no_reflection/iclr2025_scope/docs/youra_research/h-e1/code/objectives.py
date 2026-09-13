"""H-E1 Distillation Objectives - MOHAWK and CAB"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any
from model import Teacher, PhiMambaStudent, Bridge, TeacherOutput


def mohawk_loss(teacher_out: TeacherOutput, student_out: Dict[str, Any],
                layer_idx: int, stage: int) -> torch.Tensor:
    """MOHAWK loss for different stages.
    Stage 1: Frobenius norm between attention and transfer matrices
    Stage 2: + L2 norm between hidden states
    Stage 3: KL divergence between logits
    """
    loss = torch.tensor(0.0, device=teacher_out.logits.device, dtype=torch.float32)

    if stage == 1:
        teacher_attn = teacher_out.attentions[layer_idx]
        student_transfer = student_out["layer_out"]["transfer_matrix"]
        # Sample teacher attention to match student transfer matrix shape
        student_L = student_transfer.shape[-1]
        teacher_L = teacher_attn.shape[-1]
        sample_stride = max(1, teacher_L // student_L)
        teacher_attn_sampled = teacher_attn[:, :, ::sample_stride, ::sample_stride]
        # Ensure shapes match
        min_L = min(student_transfer.shape[-1], teacher_attn_sampled.shape[-1])
        loss = torch.linalg.matrix_norm(
            student_transfer[:, :, :min_L, :min_L].float() - teacher_attn_sampled[:, :, :min_L, :min_L].float(), ord="fro"
        ).mean()

    elif stage == 2:
        teacher_attn = teacher_out.attentions[layer_idx]
        student_transfer = student_out["layer_out"]["transfer_matrix"]
        student_L = student_transfer.shape[-1]
        teacher_L = teacher_attn.shape[-1]
        sample_stride = max(1, teacher_L // student_L)
        teacher_attn_sampled = teacher_attn[:, :, ::sample_stride, ::sample_stride]
        min_L = min(student_transfer.shape[-1], teacher_attn_sampled.shape[-1])
        matrix_loss = torch.linalg.matrix_norm(
            student_transfer[:, :, :min_L, :min_L].float() - teacher_attn_sampled[:, :, :min_L, :min_L].float(), ord="fro"
        ).mean()

        teacher_hidden = teacher_out.hidden_states[layer_idx + 1]
        student_hidden = student_out["hidden_states"][layer_idx + 1]
        hidden_loss = F.mse_loss(student_hidden.float(), teacher_hidden.float())

        loss = matrix_loss + hidden_loss

    elif stage == 3:
        teacher_logits = teacher_out.logits
        student_logits = student_out["logits"]

        teacher_probs = F.softmax(teacher_logits.float(), dim=-1)
        student_log_probs = F.log_softmax(student_logits.float(), dim=-1)
        loss = F.kl_div(student_log_probs, teacher_probs, reduction="batchmean")

    return loss


def cab_loss(teacher_out: TeacherOutput, student_out: Dict[str, Any],
             phi_B: Bridge, phi_C: Bridge, layer_idx: int, stage: int) -> torch.Tensor:
    """CAB loss for different stages.
    Stage 1: MSE between bridge outputs and K/Q projections
    Stage 2: KL divergence between logits
    """
    device = teacher_out.logits.device

    if stage == 1:
        teacher_hidden = teacher_out.hidden_states[layer_idx]
        K = teacher_hidden @ teacher_out.k_projs[layer_idx].T
        Q = teacher_hidden @ teacher_out.q_projs[layer_idx].T

        B = student_out["layer_out"]["B"]
        C = student_out["layer_out"]["C"]

        B_flat = B.view(B.shape[0], B.shape[1], -1)
        C_flat = C.view(C.shape[0], C.shape[1], -1)

        phi_B_out = phi_B(B_flat)
        phi_C_out = phi_C(C_flat)

        loss_B = F.mse_loss(phi_B_out.float(), K.float())
        loss_C = F.mse_loss(phi_C_out.float(), Q.float())
        loss = loss_B + loss_C

    elif stage == 2:
        teacher_logits = teacher_out.logits
        student_logits = student_out["logits"]

        teacher_probs = F.softmax(teacher_logits.float(), dim=-1)
        student_log_probs = F.log_softmax(student_logits.float(), dim=-1)
        loss = F.kl_div(student_log_probs, teacher_probs, reduction="batchmean")

    else:
        loss = torch.tensor(0.0, device=device)

    return loss


class UnifiedDistillationFramework:
    def __init__(self, teacher: Teacher, student: PhiMambaStudent,
                 objective_type: str, config):
        self.teacher = teacher
        self.student = student
        self.objective_type = objective_type
        self.config = config

        if objective_type == "token":
            d_state_flat = config.num_heads * config.d_state
            d_head_flat = config.hidden_size
            self.phi_B = Bridge(d_state_flat, d_head_flat).to(next(student.parameters()).device)
            self.phi_C = Bridge(d_state_flat, d_head_flat).to(next(student.parameters()).device)
        else:
            self.phi_B = None
            self.phi_C = None

    def compute_loss(self, input_ids: torch.Tensor, layer_idx: int, stage: int) -> torch.Tensor:
        teacher_out = self.teacher(input_ids)

        if self.objective_type == "matrix":
            student_out = self.student(
                input_ids, layer_idx=layer_idx,
                return_mixer_matrix=(stage in [1, 2])
            )
            return mohawk_loss(teacher_out, student_out, layer_idx, stage)

        elif self.objective_type == "token":
            student_out = self.student(
                input_ids, layer_idx=layer_idx,
                return_bc=(stage == 1)
            )
            return cab_loss(teacher_out, student_out, self.phi_B, self.phi_C, layer_idx, stage)

        return torch.tensor(0.0)

    def get_trainable_params(self, stage: int):
        """Get trainable parameters based on stage and objective type."""
        params = []

        if self.objective_type == "matrix":
            if stage == 1:
                for layer in self.student.layers:
                    params.extend(layer.mixer.parameters())
            elif stage == 2:
                for layer in self.student.layers:
                    params.extend(layer.parameters())
            elif stage == 3:
                params = list(self.student.parameters())

        elif self.objective_type == "token":
            if stage == 1:
                params = list(self.phi_B.parameters()) + list(self.phi_C.parameters())
            elif stage == 2:
                params = list(self.student.parameters())

        return params

    def freeze_for_stage(self, stage: int):
        """Freeze/unfreeze parameters based on stage."""
        for p in self.student.parameters():
            p.requires_grad = False

        if self.phi_B is not None:
            for p in self.phi_B.parameters():
                p.requires_grad = False
            for p in self.phi_C.parameters():
                p.requires_grad = False

        if self.objective_type == "matrix":
            if stage == 1:
                for layer in self.student.layers:
                    for p in layer.mixer.parameters():
                        p.requires_grad = True
            elif stage == 2:
                for layer in self.student.layers:
                    for p in layer.parameters():
                        p.requires_grad = True
            elif stage == 3:
                for p in self.student.parameters():
                    p.requires_grad = True

        elif self.objective_type == "token":
            if stage == 1:
                for p in self.phi_B.parameters():
                    p.requires_grad = True
                for p in self.phi_C.parameters():
                    p.requires_grad = True
            elif stage == 2:
                for p in self.student.parameters():
                    p.requires_grad = True
