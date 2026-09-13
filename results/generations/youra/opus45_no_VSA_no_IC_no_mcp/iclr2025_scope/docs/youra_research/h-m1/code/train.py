import torch
from torch import Tensor
from models.task_embedding import TaskEmbeddingEncoder
from losses.infonce import InfoNCELoss


def train_embedding(
    model: TaskEmbeddingEncoder,
    hidden_states: Tensor,
    cluster_labels: Tensor,
    lr: float = 1e-4,
    batch_size: int = 32,
    epochs: int = 10,
    device: str = None,
) -> TaskEmbeddingEncoder:
    """Train task embedding encoder with InfoNCE loss."""
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    hidden_states = hidden_states.to(device)
    cluster_labels = cluster_labels.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    criterion = InfoNCELoss(temperature=0.1)

    n = hidden_states.shape[0]
    model.train()

    for epoch in range(epochs):
        perm = torch.randperm(n)
        total_loss = 0.0
        num_batches = 0

        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            if len(idx) < 2:
                continue

            batch_h = hidden_states[idx]
            batch_labels = cluster_labels[idx]

            embeddings = model(batch_h)
            loss = criterion(embeddings, batch_labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / max(num_batches, 1)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    model.eval()
    return model
