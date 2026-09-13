"""
Synthetic data generator for CAVE experiments.

Simulates users with latent value profiles that evolve over time,
with contextual interactions and feedback signals.
"""

import numpy as np
import torch
from config import (
    NUM_USERS, NUM_TIMESTEPS, NUM_VALUE_DIMS, NUM_CONTEXT_DIMS,
    NUM_ACTIONS, NUM_DEMOGRAPHIC_GROUPS, SEED
)


def set_seed(seed=SEED):
    np.random.seed(seed)
    torch.manual_seed(seed)


class SyntheticValueEnvironment:
    """
    Simulates a population of users with heterogeneous, evolving value profiles.
    Each user belongs to a demographic group with a group-level prior.
    Value drift is simulated for a subset of users.
    """

    def __init__(self, seed=SEED):
        set_seed(seed)
        self.n_users = NUM_USERS
        self.n_timesteps = NUM_TIMESTEPS
        self.n_value_dims = NUM_VALUE_DIMS
        self.n_context_dims = NUM_CONTEXT_DIMS
        self.n_actions = NUM_ACTIONS
        self.n_groups = NUM_DEMOGRAPHIC_GROUPS

        self._generate_user_profiles()
        self._generate_action_embeddings()

    def _generate_user_profiles(self):
        # Group-level value means (population prior)
        self.group_means = np.random.randn(self.n_groups, self.n_value_dims) * 0.5
        self.group_stds = np.abs(np.random.randn(self.n_groups, self.n_value_dims)) * 0.3 + 0.1

        # Assign users to groups
        self.user_groups = np.random.randint(0, self.n_groups, size=self.n_users)

        # Initial per-user value vectors (drawn from group prior)
        self.true_user_values = np.zeros((self.n_users, self.n_value_dims))
        for u in range(self.n_users):
            g = self.user_groups[u]
            self.true_user_values[u] = (
                self.group_means[g] + np.random.randn(self.n_value_dims) * self.group_stds[g]
            )

        # Simulate value drift for 30% of users
        self.drift_users = np.random.choice(
            self.n_users, size=int(0.3 * self.n_users), replace=False
        )
        self.drift_timesteps = np.random.randint(50, 150, size=len(self.drift_users))

        # Context-to-value mapping: which value dims are active in each context
        self.context_weights = np.random.randn(self.n_context_dims, self.n_value_dims) * 0.3

        # Action value profiles: each action has a value profile
        self.action_profiles = np.random.randn(self.n_actions, self.n_value_dims)

    def _generate_action_embeddings(self):
        """Actions have embeddings in context space."""
        self.action_embeddings = np.random.randn(self.n_actions, self.n_context_dims) * 0.5

    def get_context(self):
        """Sample a random context vector."""
        return np.random.randn(self.n_context_dims)

    def get_true_value(self, user_id, timestep):
        """Get true value vector at given timestep (may have drifted)."""
        val = self.true_user_values[user_id].copy()
        if user_id in self.drift_users:
            drift_idx = np.where(self.drift_users == user_id)[0][0]
            drift_t = self.drift_timesteps[drift_idx]
            if timestep >= drift_t:
                # Gradual drift toward AI-convenient (zero) values
                alpha = min(1.0, (timestep - drift_t) / 50.0) * 0.5
                val = val * (1 - alpha)
        return val

    def get_reward(self, user_id, action_id, context, timestep, noise_std=0.2):
        """Compute feedback reward for a user-action-context tuple."""
        true_val = self.get_true_value(user_id, timestep)
        # Reward = alignment between user values and action profile, modulated by context
        context_effect = context @ self.context_weights
        effective_values = true_val + 0.2 * context_effect
        alignment = np.dot(effective_values, self.action_profiles[action_id])
        # Normalize to [0,1]
        reward = 1 / (1 + np.exp(-alignment)) + np.random.randn() * noise_std
        return float(np.clip(reward, 0, 1))

    def get_preference(self, user_id, action_a, action_b, context, timestep):
        """Binary preference: 1 if action_a preferred over action_b."""
        r_a = self.get_reward(user_id, action_a, context, timestep, noise_std=0.05)
        r_b = self.get_reward(user_id, action_b, context, timestep, noise_std=0.05)
        # Bradley-Terry model
        prob_a = 1 / (1 + np.exp(-(r_a - r_b) * 5))
        return int(np.random.rand() < prob_a)

    def generate_interaction_data(self, n_users=None, n_timesteps=None):
        """Generate full interaction dataset."""
        n_users = n_users or self.n_users
        n_timesteps = n_timesteps or self.n_timesteps

        data = {
            'user_ids': [],
            'timesteps': [],
            'contexts': [],
            'action_a': [],
            'action_b': [],
            'preferences': [],
            'rewards': [],
            'user_groups': [],
            'true_values': [],
        }

        for u in range(n_users):
            for t in range(n_timesteps):
                ctx = self.get_context()
                a = np.random.randint(0, self.n_actions)
                b = np.random.randint(0, self.n_actions)
                while b == a:
                    b = np.random.randint(0, self.n_actions)

                pref = self.get_preference(u, a, b, ctx, t)
                reward = self.get_reward(u, a, ctx, t)

                data['user_ids'].append(u)
                data['timesteps'].append(t)
                data['contexts'].append(ctx)
                data['action_a'].append(a)
                data['action_b'].append(b)
                data['preferences'].append(pref)
                data['rewards'].append(reward)
                data['user_groups'].append(self.user_groups[u])
                data['true_values'].append(self.get_true_value(u, t))

        for key in data:
            data[key] = np.array(data[key])

        return data
