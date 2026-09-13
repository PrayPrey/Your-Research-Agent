"""
Joint DPO + Attribute Training Models
Implements: BaselineDPO, JointDPOAttribute, ReferencePolicy, AttributeHead
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM


class AttributeHead(nn.Module):
    """Multi-attribute classifier for 3 attributes × 5 levels"""

    def __init__(self, hidden_dim=1600, num_attributes=3, num_levels=5):
        super().__init__()
        self.num_attributes = num_attributes
        self.num_levels = num_levels

        # Separate classifier for each attribute
        self.classifiers = nn.ModuleList([
            nn.Linear(hidden_dim, num_levels) for _ in range(num_attributes)
        ])

    def forward(self, hidden_states):
        """
        Args:
            hidden_states: (B, seq_len, hidden_dim)
        Returns:
            logits: list of (B, num_levels) for each attribute
        """
        # Use last token's hidden state
        last_hidden = hidden_states[:, -1, :]  # (B, hidden_dim)

        # Predict each attribute
        logits = [classifier(last_hidden) for classifier in self.classifiers]

        return logits


class ReferencePolicy(nn.Module):
    """Frozen reference policy for DPO loss computation"""

    def __init__(self, model_name="gpt2-xl"):
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()

        # Freeze all parameters
        for param in self.model.parameters():
            param.requires_grad = False

    @torch.no_grad()
    def forward(self, input_ids, attention_mask=None):
        """
        Returns:
            logits: (B, seq_len, vocab_size)
        """
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits


class BaselineDPO(nn.Module):
    """DPO-only baseline model"""

    def __init__(self, model_name="gpt2-xl", beta=0.1):
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.beta = beta
        self.hidden_dim = 1600  # GPT-2 XL hidden size

    def compute_dpo_loss(self, chosen_logits, rejected_logits, ref_chosen_logits, ref_rejected_logits):
        """
        DPO Loss: -log σ(β·log(π_θ(y_w|x)/π_ref(y_w|x)) - β·log(π_θ(y_l|x)/π_ref(y_l|x)))
        """
        # Compute log probabilities
        chosen_logprobs = F.log_softmax(chosen_logits, dim=-1)
        rejected_logprobs = F.log_softmax(rejected_logits, dim=-1)
        ref_chosen_logprobs = F.log_softmax(ref_chosen_logits, dim=-1)
        ref_rejected_logprobs = F.log_softmax(ref_rejected_logits, dim=-1)

        # Sum over sequence (simplified: mean pooling)
        chosen_logp = chosen_logprobs.mean(dim=1)
        rejected_logp = rejected_logprobs.mean(dim=1)
        ref_chosen_logp = ref_chosen_logprobs.mean(dim=1)
        ref_rejected_logp = ref_rejected_logprobs.mean(dim=1)

        # Compute log ratios
        chosen_ratio = chosen_logp - ref_chosen_logp
        rejected_ratio = rejected_logp - ref_rejected_logp

        # DPO loss
        loss_dpo = -F.logsigmoid(self.beta * (chosen_ratio - rejected_ratio)).mean()

        return loss_dpo

    def forward(self, chosen_ids, rejected_ids, ref_chosen_logits, ref_rejected_logits):
        """
        Returns:
            loss_dpo: scalar
        """
        # Forward pass
        chosen_outputs = self.model(input_ids=chosen_ids)
        rejected_outputs = self.model(input_ids=rejected_ids)

        chosen_logits = chosen_outputs.logits
        rejected_logits = rejected_outputs.logits

        # Compute DPO loss
        loss_dpo = self.compute_dpo_loss(chosen_logits, rejected_logits,
                                          ref_chosen_logits, ref_rejected_logits)

        return loss_dpo


class JointDPOAttribute(nn.Module):
    """Joint DPO + Attribute training model"""

    def __init__(self, model_name="gpt2-xl", beta=0.1, alpha=0.7):
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.beta = beta
        self.alpha = alpha  # Loss weight: L_total = alpha*L_DPO + (1-alpha)*L_attr
        self.hidden_dim = 1600  # GPT-2 XL hidden size

        # Attribute head
        self.attr_head = AttributeHead(hidden_dim=self.hidden_dim,
                                        num_attributes=3,
                                        num_levels=5)

    def compute_dpo_loss(self, chosen_logits, rejected_logits, ref_chosen_logits, ref_rejected_logits):
        """Same as BaselineDPO"""
        # Compute log probabilities
        chosen_logprobs = F.log_softmax(chosen_logits, dim=-1)
        rejected_logprobs = F.log_softmax(rejected_logits, dim=-1)
        ref_chosen_logprobs = F.log_softmax(ref_chosen_logits, dim=-1)
        ref_rejected_logprobs = F.log_softmax(ref_rejected_logits, dim=-1)

        # Sum over sequence (simplified: mean pooling)
        chosen_logp = chosen_logprobs.mean(dim=1)
        rejected_logp = rejected_logprobs.mean(dim=1)
        ref_chosen_logp = ref_chosen_logprobs.mean(dim=1)
        ref_rejected_logp = ref_rejected_logprobs.mean(dim=1)

        # Compute log ratios
        chosen_ratio = chosen_logp - ref_chosen_logp
        rejected_ratio = rejected_logp - ref_rejected_logp

        # DPO loss
        loss_dpo = -F.logsigmoid(self.beta * (chosen_ratio - rejected_ratio)).mean()

        return loss_dpo

    def compute_attr_loss(self, hidden_states, target_attrs):
        """
        Attribute conditioning loss: Cross-entropy on attribute prediction

        Args:
            hidden_states: (B, seq_len, hidden_dim)
            target_attrs: (B, 3) - attribute levels for [helpfulness, verbosity, creativity]
        Returns:
            loss_attr: scalar
        """
        # Get predictions for each attribute
        attr_logits = self.attr_head(hidden_states)  # List of 3 × (B, num_levels)

        # Compute cross-entropy for each attribute
        loss_attr = 0.0
        for i in range(3):
            loss_attr += F.cross_entropy(attr_logits[i], target_attrs[:, i] - 1)  # -1 for 0-indexing

        loss_attr /= 3  # Average over attributes

        return loss_attr

    def forward(self, chosen_ids, rejected_ids, ref_chosen_logits, ref_rejected_logits, target_attrs):
        """
        Joint training forward pass
        Returns:
            loss_total: L_total = alpha·L_DPO + (1-alpha)·L_attr
            loss_dpo: DPO loss component
            loss_attr: Attribute loss component
        """
        # Forward pass for DPO
        chosen_outputs = self.model(input_ids=chosen_ids, output_hidden_states=True)
        rejected_outputs = self.model(input_ids=rejected_ids, output_hidden_states=True)

        chosen_logits = chosen_outputs.logits
        rejected_logits = rejected_outputs.logits
        chosen_hidden = chosen_outputs.hidden_states[-1]  # Last layer

        # DPO loss
        loss_dpo = self.compute_dpo_loss(chosen_logits, rejected_logits,
                                          ref_chosen_logits, ref_rejected_logits)

        # Attribute loss (on chosen responses)
        loss_attr = self.compute_attr_loss(chosen_hidden, target_attrs)

        # Joint loss
        loss_total = self.alpha * loss_dpo + (1 - self.alpha) * loss_attr

        return loss_total, loss_dpo, loss_attr


if __name__ == "__main__":
    # Test models
    print("Testing models...")

    # Create dummy inputs
    batch_size = 2
    seq_len = 512
    vocab_size = 50257

    chosen_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    rejected_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    target_attrs = torch.randint(1, 6, (batch_size, 3))

    # Test ReferencePolicy
    ref_policy = ReferencePolicy()
    ref_chosen_logits = ref_policy(chosen_ids)
    ref_rejected_logits = ref_policy(rejected_ids)
    print(f"✓ ReferencePolicy: {ref_chosen_logits.shape}")

    # Test BaselineDPO
    baseline = BaselineDPO()
    loss_dpo = baseline(chosen_ids, rejected_ids, ref_chosen_logits, ref_rejected_logits)
    print(f"✓ BaselineDPO loss: {loss_dpo.item():.4f}")

    # Test JointDPOAttribute
    joint_model = JointDPOAttribute()
    loss_total, loss_dpo, loss_attr = joint_model(chosen_ids, rejected_ids,
                                                   ref_chosen_logits, ref_rejected_logits,
                                                   target_attrs)
    print(f"✓ JointDPOAttribute: total={loss_total.item():.4f}, dpo={loss_dpo.item():.4f}, attr={loss_attr.item():.4f}")
