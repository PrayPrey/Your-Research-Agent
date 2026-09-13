"""DynaMix: Adaptive Data Mixing with RL Controller and Scaling Laws.

Key components:
1. Proxy model scaling law estimation
2. Gradient SNR computation
3. RL controller (PPO-lite) for mixture policy
4. Stage-adaptive mixing
"""

import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.optimize import curve_fit
from config import (NUM_DOMAINS, DOMAINS, RL_UPDATE_INTERVAL, RL_LEARNING_RATE,
                    RL_GAMMA, RL_CLIP_EPS, SNR_WINDOW, DEVICE)

logger = logging.getLogger(__name__)


# ============================================================
# Scaling Law Estimation
# ============================================================

def scaling_law_fn(inputs, a, b, c):
    """Power-law scaling: L(N, C) = a * N^{-b} + c."""
    N, C = inputs
    return a * N**(-b) + c


class ScalingLawEstimator:
    """Estimates scaling law coefficients from proxy model runs."""

    def __init__(self, num_domains=NUM_DOMAINS):
        self.num_domains = num_domains
        # Domain-specific scaling coefficients
        self.coefficients = {
            domain: {"a": 1.0, "b": 0.1, "c": 0.5}
            for domain in DOMAINS
        }
        self.interaction_matrix = np.eye(num_domains) * 0.01
        self.is_fitted = False
        self.observations = []  # (n_params, compute, mixture, loss)

    def add_observation(self, n_params, compute, mixture, loss):
        """Add a proxy model observation."""
        self.observations.append({
            "n_params": n_params,
            "compute": compute,
            "mixture": np.array(mixture),
            "loss": float(loss)
        })

    def fit(self):
        """Fit scaling law from observations."""
        if len(self.observations) < 3:
            logger.debug("Not enough observations to fit scaling law")
            return False

        try:
            # Fit a simple scaling law: L = a * (N * C)^{-b} + c
            # where N*C is a proxy for total compute
            xs = []
            ys = []
            for obs in self.observations:
                total_compute = obs["n_params"] * obs["compute"]
                xs.append(total_compute)
                ys.append(obs["loss"])

            xs = np.array(xs)
            ys = np.array(ys)

            # Fit: L = a * x^{-b} + c
            def fn(x, a, b, c):
                return a * x**(-b) + c

            popt, _ = curve_fit(fn, xs, ys, p0=[1.0, 0.1, 0.5], maxfev=5000,
                               bounds=([0, 0, 0], [100, 1, 10]))
            self.global_coeffs = {"a": popt[0], "b": popt[1], "c": popt[2]}
            self.is_fitted = True
            return True
        except Exception as e:
            logger.debug(f"Scaling law fit failed: {e}")
            return False

    def predict_loss(self, n_params, compute, mixture=None):
        """Predict loss for given model size and compute."""
        if not self.is_fitted:
            # Use default scaling law estimates
            return 3.0 * (n_params * compute) ** (-0.1) + 1.0

        a, b, c = self.global_coeffs["a"], self.global_coeffs["b"], self.global_coeffs["c"]
        total_compute = n_params * compute
        base_loss = a * total_compute**(-b) + c

        # Add mixture interaction term
        if mixture is not None:
            m = np.array(mixture)
            interaction = float(m @ self.interaction_matrix @ m)
            base_loss += interaction

        return float(base_loss)

    def extrapolate_to_full_scale(self, target_n_params, target_compute, mixture):
        """Extrapolate scaling law to predict full-scale model loss."""
        return self.predict_loss(target_n_params, target_compute, mixture)


# ============================================================
# Gradient Signal-to-Noise Ratio
# ============================================================

class GradientSNRTracker:
    """Tracks per-domain gradient SNR over a sliding window."""

    def __init__(self, num_domains=NUM_DOMAINS, window=SNR_WINDOW):
        self.num_domains = num_domains
        self.window = window
        self.snr_history = [[] for _ in range(num_domains)]
        self.loss_history = [[] for _ in range(num_domains)]

    def update(self, domain_idx, loss_mean, loss_var):
        """Update SNR for a domain based on loss statistics."""
        snr = (loss_mean ** 2) / (loss_var + 1e-8)
        self.snr_history[domain_idx].append(snr)
        self.loss_history[domain_idx].append(loss_mean)

        # Keep only recent history
        if len(self.snr_history[domain_idx]) > self.window:
            self.snr_history[domain_idx].pop(0)
        if len(self.loss_history[domain_idx]) > self.window:
            self.loss_history[domain_idx].pop(0)

    def get_snr(self, domain_idx):
        """Get average SNR for a domain."""
        if not self.snr_history[domain_idx]:
            return 1.0
        return float(np.mean(self.snr_history[domain_idx]))

    def get_all_snrs(self):
        """Get SNRs for all domains."""
        return [self.get_snr(i) for i in range(self.num_domains)]

    def get_loss(self, domain_idx):
        """Get recent average loss for a domain."""
        if not self.loss_history[domain_idx]:
            return 1.0
        return float(np.mean(self.loss_history[domain_idx]))

    def get_all_losses(self):
        """Get recent losses for all domains."""
        return [self.get_loss(i) for i in range(self.num_domains)]


# ============================================================
# RL Policy Network (PPO-lite)
# ============================================================

class MixturePolicy(nn.Module):
    """Lightweight MLP policy for mixture control."""

    def __init__(self, state_dim, num_domains=NUM_DOMAINS, hidden_dim=64):
        super().__init__()
        self.num_domains = num_domains

        # Policy network
        self.policy_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, num_domains),
        )

        # Value network (critic)
        self.value_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )

        self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.orthogonal_(m.weight, gain=0.01)
            nn.init.zeros_(m.bias)

    def forward(self, state):
        """Returns mixture weights (action) and value estimate."""
        logits = self.policy_net(state)
        weights = F.softmax(logits, dim=-1)

        # Ensure minimum weight
        min_w = 0.05 / self.num_domains
        weights = weights * (1 - self.num_domains * min_w) + min_w

        value = self.value_net(state)
        return weights, value

    def get_action_and_log_prob(self, state):
        """Sample action (mixture weights) and compute log probability."""
        logits = self.policy_net(state)

        # Use Dirichlet distribution for simplex sampling
        concentration = F.softplus(logits) + 0.1
        dist = torch.distributions.Dirichlet(concentration)
        action = dist.sample()
        log_prob = dist.log_prob(action)

        value = self.value_net(state)
        return action, log_prob, value


class PPOBuffer:
    """Buffer for PPO training data."""

    def __init__(self, max_size=500):
        self.max_size = max_size
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.values = []
        self.dones = []

    def add(self, state, action, log_prob, reward, value, done):
        self.states.append(state.detach().cpu())
        self.actions.append(action.detach().cpu())
        self.log_probs.append(log_prob.detach().cpu())
        self.rewards.append(float(reward))
        self.values.append(value.detach().cpu())
        self.dones.append(float(done))

        if len(self.states) > self.max_size:
            self.states.pop(0)
            self.actions.pop(0)
            self.log_probs.pop(0)
            self.rewards.pop(0)
            self.values.pop(0)
            self.dones.pop(0)

    def compute_returns(self, gamma=RL_GAMMA):
        """Compute discounted returns."""
        returns = []
        advantages = []
        R = 0
        for reward, value, done in zip(reversed(self.rewards),
                                        reversed(self.values),
                                        reversed(self.dones)):
            R = reward + gamma * R * (1 - done)
            returns.insert(0, R)
            advantages.insert(0, R - value.item())

        returns = torch.tensor(returns, dtype=torch.float32)
        advantages = torch.tensor(advantages, dtype=torch.float32)
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        return returns, advantages

    def clear(self):
        self.states.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.values.clear()
        self.dones.clear()

    def __len__(self):
        return len(self.states)


# ============================================================
# DynaMix Controller
# ============================================================

class DynaMixController:
    """Main DynaMix controller for adaptive data mixing.

    State: [snr_1...snr_K, loss_1...loss_K, prev_weights_1...prev_weights_K, stage]
    Action: mixture weights over K domains
    Reward: negative proxy-predicted evaluation loss improvement
    """

    def __init__(self, num_domains=NUM_DOMAINS, update_interval=RL_UPDATE_INTERVAL):
        self.num_domains = num_domains
        self.update_interval = update_interval
        self.name = "DynaMix"

        # State dimension: SNRs + losses + prev_weights + stage
        state_dim = num_domains * 3 + 1  # SNRs + losses + prev_weights + stage
        self.policy = MixturePolicy(state_dim, num_domains).to(DEVICE)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=RL_LEARNING_RATE)

        self.buffer = PPOBuffer()
        self.snr_tracker = GradientSNRTracker(num_domains)
        self.scaling_law = ScalingLawEstimator(num_domains)

        # Current state
        self.current_weights = np.ones(num_domains) / num_domains
        self.current_stage = 0  # 0=pretraining, 1=instruction, 2=alignment
        self.step = 0
        self.prev_eval_loss = None
        self.mixture_history = []

        # Training metrics
        self.ppo_losses = []
        self.value_losses = []

    def get_state_tensor(self):
        """Build state tensor for policy network."""
        snrs = self.snr_tracker.get_all_snrs()
        losses = self.snr_tracker.get_all_losses()
        weights = self.current_weights.tolist()
        stage = [self.current_stage / 2.0]  # Normalize to [0, 1]

        # Normalize SNRs and losses
        snrs_norm = np.array(snrs) / (max(snrs) + 1e-8)
        losses_norm = np.array(losses) / (max(losses) + 1e-8)

        state = snrs_norm.tolist() + losses_norm.tolist() + weights + stage
        return torch.tensor(state, dtype=torch.float32).to(DEVICE)

    def update_snr(self, domain_idx, loss_batch):
        """Update SNR tracker from a batch of per-sample losses."""
        if len(loss_batch) > 1:
            loss_mean = float(np.mean(loss_batch))
            loss_var = float(np.var(loss_batch))
        else:
            loss_mean = float(loss_batch[0]) if loss_batch else 1.0
            loss_var = 0.1
        self.snr_tracker.update(domain_idx, loss_mean, loss_var)

    def get_weights(self, eval_loss=None, **kwargs):
        """Get current mixture weights from policy."""
        state = self.get_state_tensor()

        with torch.no_grad():
            action, log_prob, value = self.policy.get_action_and_log_prob(state.unsqueeze(0))

        weights = action.squeeze(0).cpu().numpy()

        # Compute reward if we have previous eval loss
        if eval_loss is not None and self.prev_eval_loss is not None:
            reward = self.prev_eval_loss - eval_loss  # Positive reward for improvement
        else:
            reward = 0.0

        self.prev_eval_loss = eval_loss

        # Store transition
        self.buffer.add(state.unsqueeze(0), action, log_prob, reward, value, done=0.0)

        self.current_weights = weights
        self.mixture_history.append(weights.copy())
        self.step += 1

        # Update policy periodically
        if self.step % self.update_interval == 0 and len(self.buffer) >= 10:
            self._update_policy()

        return weights.copy()

    def _update_policy(self, n_epochs=3, clip_eps=RL_CLIP_EPS):
        """PPO policy update."""
        if len(self.buffer) < 5:
            return

        returns, advantages = self.buffer.compute_returns()

        # Collect tensors
        states = torch.cat(self.buffer.states, dim=0).to(DEVICE)
        actions = torch.cat(self.buffer.actions, dim=0).to(DEVICE)
        old_log_probs = torch.cat(self.buffer.log_probs, dim=0).to(DEVICE)
        returns = returns.to(DEVICE)
        advantages = advantages.to(DEVICE)

        total_ppo_loss = 0
        total_value_loss = 0

        for _ in range(n_epochs):
            # Compute new log probs
            logits = self.policy.policy_net(states)
            concentration = F.softplus(logits) + 0.1
            dist = torch.distributions.Dirichlet(concentration)
            new_log_probs = dist.log_prob(actions)
            values = self.policy.value_net(states).squeeze(-1)

            # PPO clipped objective
            ratio = torch.exp(new_log_probs - old_log_probs.detach())
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages
            policy_loss = -torch.min(surr1, surr2).mean()

            # Value loss
            value_loss = F.mse_loss(values, returns)

            # Entropy bonus for exploration
            entropy = dist.entropy().mean()

            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()

            total_ppo_loss += policy_loss.item()
            total_value_loss += value_loss.item()

        self.ppo_losses.append(total_ppo_loss / n_epochs)
        self.value_losses.append(total_value_loss / n_epochs)
        self.buffer.clear()

    def update(self, domain_losses, domain_snrs=None, **kwargs):
        """Update internal state from training signals."""
        for i, loss in enumerate(domain_losses):
            if loss is not None:
                self.snr_tracker.update(i, loss, 0.1)

    def set_stage(self, stage):
        """Update training stage (0=pretrain, 1=instruction, 2=alignment)."""
        self.current_stage = stage
        logger.info(f"DynaMix: transitioning to stage {stage}")
