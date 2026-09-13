"""
CAVE model implementation: Hierarchical Bayesian Value Representation
with Active Elicitation Policy and Value Drift Detection.

Also includes baseline models:
1. Standard RLHF (population-level reward model)
2. LoCo-RLHF (low-rank contextual)
3. Contextual Bandit with Entropy-based feedback
4. Static Personalization (collaborative filtering style)
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam
from config import (
    NUM_VALUE_DIMS, NUM_CONTEXT_DIMS, NUM_ACTIONS, LATENT_DIM,
    LEARNING_RATE, ELICITATION_LAMBDA, ELICITATION_THRESHOLD,
    DRIFT_THRESHOLD_PERCENTILE, VALUE_DRIFT_WINDOW, DEVICE
)


# ========================== CAVE Components ==========================

class ContextEncoder(nn.Module):
    """Lightweight transformer-style context encoder."""
    def __init__(self, in_dim=NUM_CONTEXT_DIMS, out_dim=LATENT_DIM):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Linear(64, out_dim),
            nn.Tanh()
        )

    def forward(self, x):
        return self.net(x)


class RewardScorer(nn.Module):
    """Scores (value_vector, context, action_embedding) -> reward."""
    def __init__(self, value_dim=NUM_VALUE_DIMS, ctx_dim=LATENT_DIM, action_dim=NUM_CONTEXT_DIMS):
        super().__init__()
        in_dim = value_dim + ctx_dim + action_dim
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, theta, ctx_enc, action_emb):
        inp = torch.cat([theta, ctx_enc, action_emb], dim=-1)
        return self.net(inp).squeeze(-1)


class CAVEModel(nn.Module):
    """
    CAVE: Contextual Adaptive Value Elicitation.
    Per-user variational Bayesian value representation with:
    - Hierarchical Bayesian prior (population-level hyperparams)
    - Active elicitation policy
    - Value drift detection via KL divergence change-point detection
    """

    def __init__(self, n_users, action_embeddings, device=DEVICE):
        super().__init__()
        self.n_users = n_users
        self.device = device
        self.value_dim = NUM_VALUE_DIMS
        self.latent_dim = LATENT_DIM

        # Per-user variational parameters: mean and log-variance
        self.user_mu = nn.Parameter(
            torch.zeros(n_users, self.value_dim, device=device)
        )
        self.user_log_sigma = nn.Parameter(
            torch.ones(n_users, self.value_dim, device=device) * -1.0
        )

        # Population-level prior hyperparameters (learned)
        self.prior_mu = nn.Parameter(torch.zeros(self.value_dim, device=device))
        self.prior_log_sigma = nn.Parameter(torch.zeros(self.value_dim, device=device))

        # Context encoder and reward scorer
        self.context_encoder = ContextEncoder().to(device)
        self.reward_scorer = RewardScorer().to(device)

        # Action embeddings (fixed from environment)
        self.action_embeddings = torch.tensor(
            action_embeddings, dtype=torch.float32, device=device
        )

        # Drift tracking: history of posterior KL divergences per user
        self.kl_history = {u: [] for u in range(n_users)}
        self.prev_mu = None
        self.prev_log_sigma = None

        # Elicitation: query count per user
        self.query_counts = np.zeros(n_users)
        self.last_query_t = np.zeros(n_users)

        # Training metrics
        self.train_losses = []
        self.val_aucs = []

    def get_user_sigma(self, user_ids=None):
        """Get per-user standard deviation."""
        if user_ids is None:
            return torch.exp(self.user_log_sigma)
        return torch.exp(self.user_log_sigma[user_ids])

    def get_prior_sigma(self):
        return torch.exp(self.prior_log_sigma)

    def sample_theta(self, user_ids, n_samples=5):
        """Sample theta from variational posterior."""
        mu = self.user_mu[user_ids]
        sigma = self.get_user_sigma(user_ids)
        eps = torch.randn(n_samples, len(user_ids), self.value_dim, device=self.device)
        return mu.unsqueeze(0) + sigma.unsqueeze(0) * eps  # (n_samples, B, value_dim)

    def predict_reward(self, user_ids, action_ids, contexts, n_samples=5):
        """Predict reward mean and std via MC sampling."""
        ctx_enc = self.context_encoder(contexts)  # (B, latent_dim)
        action_emb = self.action_embeddings[action_ids]  # (B, action_dim)

        thetas = self.sample_theta(user_ids, n_samples)  # (n_samples, B, value_dim)
        rewards = []
        for i in range(n_samples):
            r = self.reward_scorer(thetas[i], ctx_enc, action_emb)
            rewards.append(r)
        rewards = torch.stack(rewards, dim=0)  # (n_samples, B)
        return rewards.mean(0), rewards.std(0)

    def compute_kl_divergence(self, user_ids):
        """KL(q(theta_u) || prior)."""
        mu = self.user_mu[user_ids]
        log_sigma = self.user_log_sigma[user_ids]
        sigma = torch.exp(log_sigma)

        prior_mu = self.prior_mu
        prior_sigma = self.get_prior_sigma()

        kl = (
            torch.log(prior_sigma / sigma)
            + (sigma**2 + (mu - prior_mu)**2) / (2 * prior_sigma**2)
            - 0.5
        ).sum(-1)
        return kl

    def elicitation_utility(self, uncertainty, user_id, t):
        """Active elicitation utility: uncertainty minus burden."""
        recent_queries = self.query_counts[user_id]
        time_since_last = t - self.last_query_t[user_id] + 1
        burden = ELICITATION_LAMBDA * np.exp(-time_since_last / 10.0)
        return float(uncertainty) - burden

    def should_elicit(self, uncertainty, user_id, t):
        """Decide whether to elicit feedback."""
        utility = self.elicitation_utility(uncertainty, user_id, t)
        return utility > ELICITATION_THRESHOLD

    def update_drift_history(self, user_ids):
        """Track KL divergence between consecutive posteriors for drift detection."""
        if self.prev_mu is None:
            self.prev_mu = self.user_mu.detach().clone()
            self.prev_log_sigma = self.user_log_sigma.detach().clone()
            return {}

        drift_events = {}
        for uid in user_ids:
            mu_curr = self.user_mu[uid].detach()
            sigma_curr = torch.exp(self.user_log_sigma[uid]).detach()
            mu_prev = self.prev_mu[uid]
            sigma_prev = torch.exp(self.prev_log_sigma[uid])

            # KL(q_curr || q_prev)
            kl = (
                torch.log(sigma_prev / sigma_curr)
                + (sigma_curr**2 + (mu_curr - mu_prev)**2) / (2 * sigma_prev**2)
                - 0.5
            ).sum().item()
            kl = max(0, kl)
            self.kl_history[uid].append(kl)

            # Detect drift using percentile threshold
            if len(self.kl_history[uid]) >= VALUE_DRIFT_WINDOW:
                recent = self.kl_history[uid][-VALUE_DRIFT_WINDOW:]
                threshold = np.percentile(
                    self.kl_history[uid][:-VALUE_DRIFT_WINDOW] or [0.1],
                    DRIFT_THRESHOLD_PERCENTILE
                )
                if recent[-1] > threshold and recent[-1] > 0.5:
                    drift_events[uid] = kl

        self.prev_mu = self.user_mu.detach().clone()
        self.prev_log_sigma = self.user_log_sigma.detach().clone()
        return drift_events

    def forward(self, user_ids, action_ids_a, action_ids_b, contexts):
        """Compute preference prediction logits."""
        r_a, unc_a = self.predict_reward(user_ids, action_ids_a, contexts)
        r_b, unc_b = self.predict_reward(user_ids, action_ids_b, contexts)
        logit = r_a - r_b
        uncertainty = (unc_a + unc_b) / 2
        return logit, uncertainty

    def compute_loss(self, user_ids, action_ids_a, action_ids_b, contexts, preferences, beta=0.01):
        """ELBO loss: preference likelihood + KL regularization."""
        logits, _ = self.forward(user_ids, action_ids_a, action_ids_b, contexts)
        targets = preferences.float()
        nll = F.binary_cross_entropy_with_logits(logits, targets)
        kl = self.compute_kl_divergence(user_ids).mean()
        loss = nll + beta * kl
        return loss, nll.item(), kl.item()


# ========================== Baselines ==========================

class PopulationRLHF(nn.Module):
    """
    Standard RLHF: single population-level reward model (no personalization).
    """
    def __init__(self, action_embeddings, device=DEVICE):
        super().__init__()
        self.device = device
        self.action_embeddings = torch.tensor(
            action_embeddings, dtype=torch.float32, device=device
        )
        self.net = nn.Sequential(
            nn.Linear(NUM_CONTEXT_DIMS + NUM_CONTEXT_DIMS, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        ).to(device)
        self.train_losses = []
        self.val_aucs = []

    def score(self, action_ids, contexts):
        action_emb = self.action_embeddings[action_ids]
        inp = torch.cat([contexts, action_emb], dim=-1)
        return self.net(inp).squeeze(-1)

    def forward(self, user_ids, action_ids_a, action_ids_b, contexts):
        r_a = self.score(action_ids_a, contexts)
        r_b = self.score(action_ids_b, contexts)
        return r_a - r_b

    def compute_loss(self, user_ids, action_ids_a, action_ids_b, contexts, preferences):
        logits = self.forward(user_ids, action_ids_a, action_ids_b, contexts)
        return F.binary_cross_entropy_with_logits(logits, preferences.float()), 0, 0


class LoCoRLHF(nn.Module):
    """
    LoCo-RLHF: Low-rank contextual RLHF with user embeddings.
    Models reward as a low-rank interaction between user context and action.
    """
    def __init__(self, n_users, action_embeddings, rank=8, device=DEVICE):
        super().__init__()
        self.device = device
        self.rank = rank
        self.action_embeddings = torch.tensor(
            action_embeddings, dtype=torch.float32, device=device
        )
        # User embeddings in low-rank space
        self.user_emb = nn.Embedding(n_users, rank).to(device)
        # Context and action projection to low-rank space
        self.ctx_proj = nn.Linear(NUM_CONTEXT_DIMS, rank, bias=False).to(device)
        self.action_proj = nn.Linear(NUM_CONTEXT_DIMS, rank, bias=False).to(device)
        self.bias = nn.Parameter(torch.zeros(1, device=device))
        self.train_losses = []
        self.val_aucs = []

    def score(self, user_ids, action_ids, contexts):
        u_emb = self.user_emb(user_ids)  # (B, rank)
        ctx_proj = self.ctx_proj(contexts)  # (B, rank)
        action_emb = self.action_embeddings[action_ids]
        act_proj = self.action_proj(action_emb)  # (B, rank)
        # Low-rank interaction: sum over rank dimension
        r = (u_emb * ctx_proj * act_proj).sum(-1) + self.bias
        return r

    def forward(self, user_ids, action_ids_a, action_ids_b, contexts):
        r_a = self.score(user_ids, action_ids_a, contexts)
        r_b = self.score(user_ids, action_ids_b, contexts)
        return r_a - r_b

    def compute_loss(self, user_ids, action_ids_a, action_ids_b, contexts, preferences):
        logits = self.forward(user_ids, action_ids_a, action_ids_b, contexts)
        return F.binary_cross_entropy_with_logits(logits, preferences.float()), 0, 0


class ContextualBanditEntropy(nn.Module):
    """
    Contextual Bandit with Entropy-based Human Feedback.
    Solicits feedback when model uncertainty (entropy) is high.
    Uses MC dropout for uncertainty estimation.
    """
    def __init__(self, n_users, action_embeddings, device=DEVICE):
        super().__init__()
        self.device = device
        self.action_embeddings = torch.tensor(
            action_embeddings, dtype=torch.float32, device=device
        )
        self.user_emb = nn.Embedding(n_users, LATENT_DIM).to(device)
        self.net = nn.Sequential(
            nn.Linear(NUM_CONTEXT_DIMS + NUM_CONTEXT_DIMS + LATENT_DIM, 64),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.Dropout(0.2),
            nn.ReLU(),
            nn.Linear(32, 1)
        ).to(device)
        self.train_losses = []
        self.val_aucs = []

    def score(self, user_ids, action_ids, contexts, n_samples=5):
        u_emb = self.user_emb(user_ids)
        action_emb = self.action_embeddings[action_ids]
        inp = torch.cat([contexts, action_emb, u_emb], dim=-1)
        # MC dropout
        self.train()  # enable dropout
        scores = torch.stack([self.net(inp).squeeze(-1) for _ in range(n_samples)], dim=0)
        return scores.mean(0), scores.std(0)

    def forward(self, user_ids, action_ids_a, action_ids_b, contexts):
        r_a, std_a = self.score(user_ids, action_ids_a, contexts)
        r_b, std_b = self.score(user_ids, action_ids_b, contexts)
        uncertainty = (std_a + std_b) / 2
        return r_a - r_b, uncertainty

    def compute_loss(self, user_ids, action_ids_a, action_ids_b, contexts, preferences):
        logits, _ = self.forward(user_ids, action_ids_a, action_ids_b, contexts)
        return F.binary_cross_entropy_with_logits(logits, preferences.float()), 0, 0


class StaticPersonalization(nn.Module):
    """
    Static Personalization: user-specific bias added to population reward model.
    Similar to collaborative filtering with content features.
    """
    def __init__(self, n_users, action_embeddings, device=DEVICE):
        super().__init__()
        self.device = device
        self.action_embeddings = torch.tensor(
            action_embeddings, dtype=torch.float32, device=device
        )
        # Shared context-action scorer
        self.shared_net = nn.Sequential(
            nn.Linear(NUM_CONTEXT_DIMS * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        ).to(device)
        # Per-user bias
        self.user_bias = nn.Embedding(n_users, 1).to(device)
        nn.init.zeros_(self.user_bias.weight)
        self.train_losses = []
        self.val_aucs = []

    def score(self, user_ids, action_ids, contexts):
        action_emb = self.action_embeddings[action_ids]
        inp = torch.cat([contexts, action_emb], dim=-1)
        shared = self.shared_net(inp).squeeze(-1)
        bias = self.user_bias(user_ids).squeeze(-1)
        return shared + bias

    def forward(self, user_ids, action_ids_a, action_ids_b, contexts):
        r_a = self.score(user_ids, action_ids_a, contexts)
        r_b = self.score(user_ids, action_ids_b, contexts)
        return r_a - r_b

    def compute_loss(self, user_ids, action_ids_a, action_ids_b, contexts, preferences):
        logits = self.forward(user_ids, action_ids_a, action_ids_b, contexts)
        return F.binary_cross_entropy_with_logits(logits, preferences.float()), 0, 0
