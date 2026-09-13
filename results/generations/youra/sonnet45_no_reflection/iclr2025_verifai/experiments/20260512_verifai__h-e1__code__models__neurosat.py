"""NeuroSAT architecture for constraint-graph message passing."""
import torch
import torch.nn as nn
from torch import Tensor
from typing import Tuple
from torch_geometric.data import Batch
from torch_geometric.utils import scatter
from .mlp import MLP


class NeuroSAT(nn.Module):
    """NeuroSAT message-passing GNN for SAT solving."""

    def __init__(self, hidden_size: int = 128, num_rounds: int = 32, max_vars: int = 500):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_rounds = num_rounds

        # Learnable embedding initialization layers
        # Instead of random embeddings, we use a small learned initialization
        self.literal_init = nn.Parameter(torch.randn(1, hidden_size) * 0.1)
        self.clause_init = nn.Parameter(torch.randn(1, hidden_size) * 0.1)

        # Message MLPs
        self.l_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)
        self.c_msg_mlp = MLP(hidden_size, hidden_size, hidden_size, num_layers=3)

        # LSTM state updates
        self.l_update = nn.LSTM(hidden_size * 2, hidden_size, batch_first=True)
        self.c_update = nn.LSTM(hidden_size, hidden_size, batch_first=True)

        # Satisfiability decoder
        self.sat_decoder = nn.Sequential(
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )

    def forward(self, batch: Batch) -> Tuple[Tensor, Tensor]:
        """
        Message-passing forward pass.
        Args:
            batch: Batch with edge_index=[2, E], n_literals, n_clauses (or computed from edge_index)
        Returns:
            l_final=[L, H], c_final=[C, H]
        """
        # Initialize embeddings from learned parameters (not random)
        # Handle both single instances and batched data
        if not hasattr(batch, 'x_literal') or batch.x_literal is None:
            # Use stored n_literals/n_clauses if available, otherwise compute from edge_index
            if hasattr(batch, 'n_literals'):
                # For batched data, n_literals might be a tensor - sum it
                n_literals = int(batch.n_literals.sum().item() if torch.is_tensor(batch.n_literals) else batch.n_literals)
            else:
                n_literals = int(batch.edge_index[1].max().item() + 1)

            if hasattr(batch, 'n_clauses'):
                n_clauses = int(batch.n_clauses.sum().item() if torch.is_tensor(batch.n_clauses) else batch.n_clauses)
            else:
                n_clauses = int(batch.edge_index[0].max().item() + 1)

            # Use learnable initialization, broadcast to all literals/clauses
            l_state = self.literal_init.expand(n_literals, -1).contiguous()  # [L, 128]
            c_state = self.clause_init.expand(n_clauses, -1).contiguous()    # [C, 128]
        else:
            l_state = batch.x_literal  # [L, 128]
            c_state = batch.x_clause   # [C, 128]

        edge_index = batch.edge_index  # [2, E] - (clause_idx, lit_idx)

        # Initialize LSTM hidden states
        batch_size = 1
        l_hidden = (torch.zeros(1, l_state.size(0), self.hidden_size, device=l_state.device),
                    torch.zeros(1, l_state.size(0), self.hidden_size, device=l_state.device))
        c_hidden = (torch.zeros(1, c_state.size(0), self.hidden_size, device=c_state.device),
                    torch.zeros(1, c_state.size(0), self.hidden_size, device=c_state.device))

        for _ in range(self.num_rounds):
            # Literal -> Clause message passing
            l_msg = self.l_msg_mlp(l_state)  # [L, 128]

            # Aggregate messages to clauses
            clause_indices = edge_index[0]  # Clause indices
            lit_indices = edge_index[1]     # Literal indices
            c_agg = scatter(l_msg[lit_indices], clause_indices, dim=0,
                           dim_size=c_state.size(0), reduce='mean')  # [C, 128]

            # Update clause states with LSTM
            c_input = c_agg.unsqueeze(1)  # [C, 1, 128]
            c_output, c_hidden = self.c_update(c_input, c_hidden)
            c_state = c_output.squeeze(1)  # [C, 128]

            # Clause -> Literal message passing
            c_msg = self.c_msg_mlp(c_state)  # [C, 128]

            # Aggregate messages to literals (send from clauses to literals)
            # clause_indices tells us which clause, we send its message to lit_indices
            l_agg = scatter(c_msg[clause_indices], lit_indices, dim=0,
                           dim_size=l_state.size(0), reduce='mean')  # [L, 128]

            # Flip literal pairs (connect positive and negative literals)
            l_flip = self._flip_literal_pairs(l_state)  # [L, 128]

            # Concatenate aggregated messages and flipped states
            l_input = torch.cat([l_agg, l_flip], dim=-1).unsqueeze(1)  # [L, 1, 256]

            # Update literal states with LSTM
            l_output, l_hidden = self.l_update(l_input, l_hidden)
            l_state = l_output.squeeze(1)  # [L, 128]

        return l_state, c_state

    def _flip_literal_pairs(self, l_state: Tensor) -> Tensor:
        """
        Swap positive and negative literal embeddings.
        l_state: [L, 128] where L = 2n (pairs: [pos1, neg1, pos2, neg2, ...])
        Returns: [L, 128] with pairs swapped
        """
        L, H = l_state.shape
        l_reshaped = l_state.view(-1, 2, H)  # [n, 2, 128]
        l_flipped = torch.flip(l_reshaped, dims=[1])  # Swap pos/neg
        return l_flipped.view(L, H)

    def decode_assignment(self, l_embeddings: Tensor, num_vars: int) -> Tensor:
        """
        Decode variable assignment from literal embeddings.
        Args:
            l_embeddings: [L, H] where L=2n
            num_vars: Number of variables n
        Returns:
            assignment: [n] boolean values
        """
        l_reshaped = l_embeddings.view(num_vars, 2, -1)  # [n, 2, 128]
        pos_scores = l_reshaped[:, 0, :].mean(dim=1)  # [n]
        neg_scores = l_reshaped[:, 1, :].mean(dim=1)  # [n]
        assignment = pos_scores > neg_scores  # True if positive
        return assignment

    def predict_sat(self, l_embeddings: Tensor, batch_literal: Tensor) -> Tensor:
        """
        Predict satisfiability from literal embeddings.
        Args:
            l_embeddings: [L, H]
            batch_literal: [L] batch indices
        Returns:
            p_sat: [B] probability per instance
        """
        # Global pooling over literals per instance
        batch_size = batch_literal.max().item() + 1
        pooled = scatter(l_embeddings, batch_literal, dim=0,
                        dim_size=batch_size, reduce='mean')  # [B, 128]
        p_sat = self.sat_decoder(pooled).squeeze(-1)  # [B]
        return p_sat
