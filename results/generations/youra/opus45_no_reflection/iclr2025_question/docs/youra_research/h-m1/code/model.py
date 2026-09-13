import torch
import torch.nn as nn


class HiddenStateExtractor:
    def __init__(self, model, target_layer: int = 19):
        self.hidden_states = None
        self.target_layer = target_layer

        if target_layer >= len(model.model.layers):
            raise IndexError(f"target_layer {target_layer} >= num_layers {len(model.model.layers)}")

        self.hook = model.model.layers[target_layer].register_forward_hook(self._capture_hook)

    def _capture_hook(self, module, input, output):
        self.hidden_states = output[0][:, -1, :].detach().cpu()

    def get_last_hidden(self) -> torch.Tensor:
        if self.hidden_states is None:
            raise RuntimeError("No forward pass captured")
        return self.hidden_states

    def remove(self):
        self.hook.remove()


class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096):
        super().__init__()
        self.classifier = nn.Linear(hidden_dim, 1)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        logits = self.classifier(hidden_states)
        return torch.sigmoid(logits)


def extract_hidden_states(model, tokenizer, extractor, examples: list, batch_size: int = 32) -> tuple:
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    all_hidden = []
    all_labels = []

    try:
        for i in range(0, len(examples), batch_size):
            batch = examples[i:i+batch_size]
            prompts = [e["prompt"] for e in batch]

            enc = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(model.device)

            with torch.no_grad():
                model(**enc)

            h = extractor.get_last_hidden()
            all_hidden.append(h.float())
            all_labels.extend(e["label"] for e in batch)
    finally:
        extractor.remove()

    return torch.cat(all_hidden, dim=0), torch.tensor(all_labels, dtype=torch.long)


def train_probe(hidden_states: torch.Tensor, labels: torch.Tensor, cfg) -> tuple:
    probe = LinearProbe(hidden_dim=hidden_states.shape[1])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    probe = probe.to(device)
    hidden_states = hidden_states.to(device)
    labels = labels.float().to(device)

    optimizer = torch.optim.Adam(probe.parameters(), lr=cfg.lr)
    criterion = nn.BCELoss()

    loss_per_epoch = []
    n_samples = hidden_states.shape[0]

    for epoch in range(cfg.epochs):
        indices = torch.randperm(n_samples)
        epoch_loss = 0.0
        n_batches = 0

        for i in range(0, n_samples, cfg.batch_size):
            batch_idx = indices[i:i+cfg.batch_size]
            batch_h = hidden_states[batch_idx]
            batch_y = labels[batch_idx]

            optimizer.zero_grad()
            preds = probe(batch_h).squeeze()
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        avg_loss = epoch_loss / n_batches
        loss_per_epoch.append(avg_loss)
        print(f"Epoch {epoch+1}/{cfg.epochs}, Loss: {avg_loss:.4f}")

    return probe.cpu(), loss_per_epoch
