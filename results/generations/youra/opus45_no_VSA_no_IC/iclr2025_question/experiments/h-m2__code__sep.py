"""Semantic Entropy Probe (SEP) implementation."""

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression


class SemanticEntropyProbe:
    def __init__(self, layer_idx: int, token_position: str = "last"):
        self.layer_idx = layer_idx
        self.token_position = token_position
        self.clf = LogisticRegression(max_iter=1000, solver="lbfgs")

    def extract_hidden_state(self, model, input_ids, attention_mask) -> np.ndarray:
        """Extract hidden state at specified layer and token position."""
        hidden_states = model.get_hidden_states(input_ids, attention_mask)
        layer_hidden = hidden_states[self.layer_idx]  # [batch, seq, hidden]
        if self.token_position == "last":
            seq_lens = attention_mask.sum(dim=1)
            batch_size = layer_hidden.shape[0]
            last_hidden = []
            for i in range(batch_size):
                last_idx = seq_lens[i].item() - 1
                last_hidden.append(layer_hidden[i, last_idx, :])
            hidden = torch.stack(last_hidden, dim=0)
        else:
            hidden = layer_hidden[:, -1, :]
        return hidden.cpu().numpy()

    def fit(self, hidden_states: np.ndarray, se_labels: list) -> None:
        """Fit logistic regression probe."""
        self.clf.fit(hidden_states, se_labels)

    def predict_proba(self, hidden_states: np.ndarray) -> np.ndarray:
        """Predict probability of high semantic entropy."""
        return self.clf.predict_proba(hidden_states)
