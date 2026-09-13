"""
Simulated value evolution module for testing adaptive alignment
"""

import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple

class ValueEvolutionSimulator:
    """Simulates human preference evolution over time"""

    def __init__(self, feature_dim: int, action_dim: int, num_contexts: int,
                 drift_rate: float = 0.02, seed: int = 42):
        self.feature_dim = feature_dim
        self.action_dim = action_dim
        self.num_contexts = num_contexts
        self.drift_rate = drift_rate

        np.random.seed(seed)

        # Initialize core preferences (stable across time)
        self.core_preferences = np.random.randn(feature_dim, action_dim)
        self.core_preferences /= np.linalg.norm(self.core_preferences, axis=0)

        # Context-dependent variations
        self.context_preferences = {
            c: np.random.randn(feature_dim, action_dim) * 0.3
            for c in range(num_contexts)
        }

        # Evolved preferences (changes over time)
        self.evolved_preferences = np.zeros((feature_dim, action_dim))

    def get_preference_score(self, state: np.ndarray, action: int,
                            context: int, timestep: int) -> float:
        """
        Compute preference score for a state-action pair
        P(x,a,c,t) = P_core(x,a) + P_context(x,a,c) + P_evolved(x,a,t)
        """
        # Core component
        core_score = np.dot(state, self.core_preferences[:, action])

        # Context component
        context_score = np.dot(state, self.context_preferences[context][:, action])

        # Evolved component
        evolved_score = np.dot(state, self.evolved_preferences[:, action])

        return core_score + context_score + evolved_score

    def get_preferred_action(self, state: np.ndarray, context: int,
                            timestep: int) -> int:
        """Get the most preferred action for current state and context"""
        scores = [self.get_preference_score(state, a, context, timestep)
                 for a in range(self.action_dim)]
        return np.argmax(scores)

    def apply_gradual_drift(self, timestep: int):
        """Apply gradual preference drift"""
        drift = np.random.randn(self.feature_dim, self.action_dim) * self.drift_rate
        self.evolved_preferences += drift

    def apply_rapid_shift(self, magnitude: float = 0.5):
        """Apply rapid preference shift"""
        shift = np.random.randn(self.feature_dim, self.action_dim) * magnitude
        self.evolved_preferences = shift

    def apply_value_conflict(self, affected_actions: List[int], magnitude: float = 0.7):
        """Apply conflicting preference changes to specific actions"""
        for action in affected_actions:
            conflict = np.random.randn(self.feature_dim) * magnitude
            self.evolved_preferences[:, action] += conflict


class InteractionEnvironment:
    """Environment for simulating human-AI interactions"""

    def __init__(self, num_users: int, feature_dim: int, action_dim: int,
                 num_contexts: int, num_timesteps: int, scenario: str = 'gradual_drift',
                 seed: int = 42):
        self.num_users = num_users
        self.feature_dim = feature_dim
        self.action_dim = action_dim
        self.num_contexts = num_contexts
        self.num_timesteps = num_timesteps
        self.scenario = scenario

        np.random.seed(seed)

        # Create value evolution simulator for each user
        self.user_values = [
            ValueEvolutionSimulator(feature_dim, action_dim, num_contexts, seed=seed+i)
            for i in range(num_users)
        ]

    def generate_state(self) -> np.ndarray:
        """Generate a random state"""
        state = np.random.randn(self.feature_dim)
        return state / np.linalg.norm(state)

    def generate_interaction_trajectory(self, user_id: int) -> Dict:
        """Generate a full interaction trajectory for a user"""
        trajectory = {
            'states': [],
            'contexts': [],
            'human_actions': [],
            'timesteps': [],
            'preference_type': []  # 'core', 'context', 'evolved'
        }

        current_context = 0
        value_sim = self.user_values[user_id]

        for t in range(self.num_timesteps):
            # Sample context change
            if np.random.random() < 0.2:
                current_context = np.random.randint(0, self.num_contexts)

            # Generate state
            state = self.generate_state()

            # Apply scenario-specific preference evolution
            if self.scenario == 'gradual_drift':
                value_sim.apply_gradual_drift(t)
            elif self.scenario == 'rapid_shift' and t == self.num_timesteps // 2:
                value_sim.apply_rapid_shift()
            elif self.scenario == 'value_conflict' and t % 20 == 10:
                affected_actions = np.random.choice(self.action_dim, 2, replace=False).tolist()
                value_sim.apply_value_conflict(affected_actions)

            # Get human's preferred action
            human_action = value_sim.get_preferred_action(state, current_context, t)

            # Determine preference type
            pref_type = self._determine_preference_type(t)

            trajectory['states'].append(state)
            trajectory['contexts'].append(current_context)
            trajectory['human_actions'].append(human_action)
            trajectory['timesteps'].append(t)
            trajectory['preference_type'].append(pref_type)

        return trajectory

    def _determine_preference_type(self, timestep: int) -> str:
        """Determine the type of preference at a given timestep"""
        if self.scenario == 'gradual_drift' and timestep > 30:
            return 'evolved'
        elif self.scenario == 'rapid_shift' and timestep >= self.num_timesteps // 2:
            return 'evolved'
        elif self.scenario == 'value_conflict':
            return 'evolved' if timestep % 20 > 10 else 'core'
        return 'core'

    def generate_batch_data(self, batch_size: int) -> Tuple[torch.Tensor, ...]:
        """Generate a batch of training data"""
        states = []
        contexts = []
        actions = []
        timesteps = []

        for _ in range(batch_size):
            user_id = np.random.randint(0, self.num_users)
            t = np.random.randint(0, self.num_timesteps)
            context = np.random.randint(0, self.num_contexts)

            state = self.generate_state()
            value_sim = self.user_values[user_id]

            # Apply evolution up to timestep t
            temp_sim = ValueEvolutionSimulator(
                self.feature_dim, self.action_dim, self.num_contexts
            )
            temp_sim.core_preferences = value_sim.core_preferences.copy()
            temp_sim.context_preferences = {k: v.copy() for k, v in value_sim.context_preferences.items()}
            temp_sim.evolved_preferences = value_sim.evolved_preferences.copy()

            if self.scenario == 'gradual_drift':
                for i in range(t):
                    temp_sim.apply_gradual_drift(i)
            elif self.scenario == 'rapid_shift' and t >= self.num_timesteps // 2:
                temp_sim.apply_rapid_shift()

            action = temp_sim.get_preferred_action(state, context, t)

            states.append(state)
            contexts.append(context)
            actions.append(action)
            timesteps.append(t / self.num_timesteps)  # Normalized timestep

        return (torch.FloatTensor(np.array(states)),
                torch.LongTensor(contexts),
                torch.LongTensor(actions),
                torch.FloatTensor(timesteps).unsqueeze(1))
