import torch
from typing import Tuple, List


class Validator:
    """Validation protocol for distillation."""

    def __init__(self, teacher, student, loss_fn, val_loader, device):
        self.teacher = teacher
        self.student = student
        self.loss_fn = loss_fn
        self.val_loader = val_loader
        self.device = device

    @torch.no_grad()
    def evaluate(self) -> Tuple[float, List[float]]:
        """
        Evaluate on validation set.

        Returns:
            mean_loss: Scalar
            per_layer_losses: List[Scalar] (12)
        """
        self.student.eval()
        total_loss = 0.0
        layer_loss_accum = [0.0] * 12

        for batch in self.val_loader:
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)

            teacher_hiddens = self.teacher(input_ids, attention_mask)
            student_hiddens = self.student(input_ids)

            loss, layer_losses = self.loss_fn(teacher_hiddens, student_hiddens)

            total_loss += loss.item()
            for i, ll in enumerate(layer_losses):
                layer_loss_accum[i] += ll.item()

        mean_loss = total_loss / len(self.val_loader)
        per_layer = [l / len(self.val_loader) for l in layer_loss_accum]

        self.student.train()
        return mean_loss, per_layer
