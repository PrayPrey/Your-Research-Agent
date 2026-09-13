# Logic Specification: h-e1

**Date:** 2026-08-28  
**Author:** Phase 3 Logic Agent  
**Hypothesis:** Layer-wise weight tokenization for architecture family classification  
**Type:** EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - designing new APIs  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Task Allocation

| Task ID | Name | Complexity | Budget | Status |
|---------|------|------------|--------|--------|
| E1-1 | Data pipeline | 8 | 8 | ALLOCATED |
| E1-2 | Baseline model | 5 | 5 | ALLOCATED |
| E1-3 | Transformer model | 9 | 9 | ALLOCATED |
| E1-4 | Training loop | 7 | 7 | ALLOCATED |
| E1-5 | Evaluation | 6 | 6 | ALLOCATED |

**Total Budget:** 35 subtasks

---

## E1-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied:** Standard PyTorch DataLoader pattern

### API Signatures

```python
class TimmModelZooLoader:
    def __init__(self, families: list[str], num_models: int, cache_path: str, seed: int = 42):
        """Initialize loader with model filtering criteria."""
        
    def load_models(self) -> list[tuple[str, nn.Module, int]]:
        """Load models from timm. Returns: [(name, model, family_id), ...]"""
        
    def extract_weights(self, model: nn.Module) -> list[Tensor]:
        """Extract layer weights. Returns: [layer_tensor, ...] each [out, in]"""
        
    def split_data(
        self, 
        models_data: list,
        train_size: float = 0.7,
        val_size: float = 0.15,
        test_size: float = 0.15
    ) -> tuple[list, list, list]:
        """Stratified split by family. Returns: (train, val, test)"""

class WeightTokenizer:
    def __init__(self, max_layer_size: int = 4096, normalize: bool = True):
        """Initialize tokenizer with padding parameters."""
        
    def tokenize(self, layer_weights: list[Tensor]) -> Tensor:
        """Flatten + pad layers. layers: T × [variable] -> [T, max_size]"""
        
    def add_position_encoding(self, tokens: Tensor, d_model: int) -> Tensor:
        """Add sinusoidal position encoding. [T, F] -> [T, F]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_weights[i] | [out_i, in_i] | Variable per layer |
| flattened | [out_i * in_i] | 1D token |
| padded | [max_size] | Pad/truncate to fixed |
| tokens | [T, max_size] | T layers |
| pos_encoded | [T, max_size] | With layer position |

### Pseudo-code

```
tokenize(layer_weights):
    tokens = []
    for layer in layer_weights:
        flat = layer.flatten()  # [out*in]
        if len(flat) > max_size:
            flat = flat[:max_size]  # truncate
        else:
            flat = pad(flat, max_size)  # zero-pad
        if normalize:
            flat = (flat - mean(flat)) / std(flat)  # per-layer norm
        tokens.append(flat)
    return stack(tokens)  # [T, max_size]

add_position_encoding(tokens, d_model):
    T = tokens.shape[0]
    pos = arange(T)
    pe = zeros([T, d_model])
    for i in range(d_model // 2):
        pe[:, 2*i] = sin(pos / 10000^(2*i/d_model))
        pe[:, 2*i+1] = cos(pos / 10000^(2*i/d_model))
    return tokens + pe[:, :tokens.shape[1]]  # broadcast
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Model loading | Filter timm models by family |
| L-1-2 | Weight extraction | Extract layer weights from state_dict |
| L-1-3 | Flatten layers | Convert 2D weights to 1D tokens |
| L-1-4 | Pad/truncate | Handle variable layer sizes |
| L-1-5 | Normalization | Per-layer zero mean, unit variance |
| L-1-6 | Position encoding | Sinusoidal encoding for layer index |
| L-1-7 | Stratified split | Train/val/test by architecture family |
| L-1-8 | Caching | Save extracted weights to disk |

---

## E1-2: Baseline Model [Complexity: 5, Budget: 5]

**Applied:** Standard MLP classifier

### API Signatures

```python
def extract_layer_statistics(weights: list[Tensor]) -> Tensor:
    """Compute mean/std/norm per layer. Returns: [3*T]"""

class BaselineMLP(nn.Module):
    def __init__(self, num_features: int, hidden_dim: int = 256, num_classes: int = 4):
        """Initialize MLP. num_features = 3 * num_layers (mean/std/norm)"""
        
    def forward(self, stats: Tensor) -> Tensor:
        """Forward pass. stats: [B, 3*T] -> [B, C]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights[i] | [out_i, in_i] | Layer weight tensor |
| stats | [B, 3*T] | 3 stats × T layers |
| hidden | [B, 256] | First layer output |
| logits | [B, C] | Class predictions |

### Pseudo-code

```
extract_layer_statistics(weights):
    stats = []
    for layer in weights:
        stats.extend([
            layer.mean(),
            layer.std(),
            layer.norm()
        ])
    return tensor(stats)  # [3*T]

BaselineMLP.forward(stats):
    x = linear1(stats)  # [B, 256]
    x = relu(x)
    x = linear2(x)  # [B, 128]
    x = relu(x)
    x = linear3(x)  # [B, C]
    return x
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Statistics extraction | Mean/std/norm per layer |
| L-2-2 | MLP architecture | 3-layer MLP (256 → 128 → C) |
| L-2-3 | Forward pass | Linear → ReLU sequence |
| L-2-4 | Loss computation | CrossEntropyLoss |
| L-2-5 | Training integration | Plug into Trainer class |

---

## E1-3: Transformer Model [Complexity: 9, Budget: 9]

**Applied:** Standard PyTorch TransformerEncoder

### API Signatures

```python
class WeightTransformer(nn.Module):
    def __init__(
        self,
        max_layer_size: int = 4096,
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 6,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        num_classes: int = 4
    ):
        """Initialize weight transformer."""
        
    def forward(self, layer_tokens: Tensor) -> Tensor:
        """Forward pass. tokens: [B, T, max_size] -> [B, C]"""
        
    def get_attention_weights(self, layer_tokens: Tensor) -> Tensor:
        """Extract attention for visualization. Returns: [B, nhead, T, T]"""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_tokens | [B, T, max_size] | Input weight tokens |
| projected | [B, T, d_model] | After token projection |
| pos_encoded | [B, T, d_model] | With position encoding |
| transposed | [T, B, d_model] | For TransformerEncoder |
| encoded | [T, B, d_model] | After transformer |
| pooled | [B, d_model] | After mean pooling |
| logits | [B, C] | Class predictions |

### Pseudo-code

```
forward(layer_tokens):
    # Token projection
    x = token_projection(layer_tokens)  # [B, T, max_size] -> [B, T, d_model]
    
    # Position encoding
    x = pos_encoder(x)  # [B, T, d_model]
    
    # Transpose for transformer
    x = x.transpose(0, 1)  # [T, B, d_model]
    
    # Transformer encoder
    x = transformer(x)  # [T, B, d_model]
    
    # Global pooling
    x = x.mean(dim=0)  # [B, d_model]
    
    # Classifier
    x = dropout(linear1(x))  # [B, 128]
    x = relu(x)
    x = dropout(x)
    logits = linear2(x)  # [B, C]
    
    return logits

get_attention_weights(layer_tokens):
    # Hook into transformer encoder layer
    # Return first layer attention: [B, nhead, T, T]
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Token projection | Linear layer: max_size → d_model |
| L-3-2 | Position encoding | Sinusoidal encoding module |
| L-3-3 | Transformer setup | TransformerEncoderLayer config |
| L-3-4 | Encoder stack | TransformerEncoder(6 layers) |
| L-3-5 | Pooling layer | Mean pooling over sequence |
| L-3-6 | Classifier head | MLP(d_model → 128 → C) |
| L-3-7 | Forward pass | Full pipeline integration |
| L-3-8 | Attention extraction | Hook for visualization |
| L-3-9 | Gradient handling | Ensure all layers trainable |

---

## E1-4: Training Loop [Complexity: 7, Budget: 7]

**Applied:** Standard PyTorch training pattern

### API Signatures

```python
class Trainer:
    def __init__(
        self,
        model: nn.Module,
        optimizer: Optimizer,
        scheduler: LRScheduler,
        criterion: nn.Module,
        device: str = "cuda",
        gradient_clip_max_norm: float = 1.0
    ):
        """Initialize trainer."""
        
    def train_epoch(self, dataloader: DataLoader) -> dict[str, float]:
        """Single training epoch. Returns: {loss, accuracy}"""
        
    def validate(self, dataloader: DataLoader) -> dict[str, float]:
        """Validation pass. Returns: {loss, accuracy}"""
        
    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        patience: int = 10,
        checkpoint_path: str = "best_model.pt"
    ) -> dict:
        """Full training loop. Returns: {train_history, val_history, best_epoch}"""

class EarlyStopping:
    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        """Initialize early stopping."""
        
    def __call__(self, val_loss: float) -> bool:
        """Check if should stop. Returns: True if no improvement for patience epochs"""
```

### Pseudo-code

```
train_epoch(dataloader):
    model.train()
    total_loss = 0
    correct = 0
    
    for batch in dataloader:
        inputs, labels = batch  # [B, T, F], [B]
        
        # Forward
        logits = model(inputs)  # [B, C]
        loss = criterion(logits, labels)
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm)
        optimizer.step()
        
        # Metrics
        preds = logits.argmax(dim=1)
        correct += (preds == labels).sum()
        total_loss += loss.item()
    
    return {
        'loss': total_loss / len(dataloader),
        'accuracy': correct / len(dataloader.dataset)
    }

validate(dataloader):
    model.eval()
    total_loss = 0
    correct = 0
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            logits = model(inputs)
            loss = criterion(logits, labels)
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum()
            total_loss += loss.item()
    
    return {
        'loss': total_loss / len(dataloader),
        'accuracy': correct / len(dataloader.dataset)
    }

fit(train_loader, val_loader, epochs, patience):
    early_stop = EarlyStopping(patience)
    best_val_loss = inf
    history = {'train': [], 'val': []}
    
    for epoch in range(epochs):
        # Train
        train_metrics = train_epoch(train_loader)
        history['train'].append(train_metrics)
        
        # Validate
        val_metrics = validate(val_loader)
        history['val'].append(val_metrics)
        
        # Scheduler
        scheduler.step()
        
        # Checkpoint
        if val_metrics['loss'] < best_val_loss:
            best_val_loss = val_metrics['loss']
            save_checkpoint(model, checkpoint_path)
        
        # Early stopping
        if early_stop(val_metrics['loss']):
            break
    
    return history
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Optimizer setup | AdamW with weight decay |
| L-4-2 | Scheduler setup | CosineAnnealingLR |
| L-4-3 | Training step | Forward + backward + clip |
| L-4-4 | Validation step | No-grad evaluation |
| L-4-5 | Early stopping | Patience-based stopping |
| L-4-6 | Checkpointing | Save best model by val loss |
| L-4-7 | Metrics logging | Loss and accuracy tracking |

---

## E1-5: Evaluation [Complexity: 6, Budget: 6]

**Applied:** sklearn metrics + matplotlib

### API Signatures

```python
def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    device: str = "cuda"
) -> dict[str, float]:
    """Evaluate on test set. Returns: {accuracy, precision, recall, f1}"""

def generate_confusion_matrix(
    y_true: ndarray,
    y_pred: ndarray,
    class_names: list[str],
    save_path: str
) -> None:
    """Plot confusion matrix heatmap."""

def plot_training_curves(
    train_history: list[dict],
    val_history: list[dict],
    save_path: str
) -> None:
    """Plot train/val loss and accuracy."""

def plot_gate_metrics(
    random_acc: float,
    baseline_acc: float,
    proposed_acc: float,
    threshold: float = 0.6,
    save_path: str
) -> None:
    """Bar chart: Random vs Baseline vs Proposed with threshold line."""

def visualize_attention(
    model: WeightTransformer,
    sample_input: Tensor,
    save_path: str
) -> None:
    """Heatmap of transformer attention over layers."""
```

### Pseudo-code

```
evaluate_model(model, test_loader):
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            logits = model(inputs)
            preds = logits.argmax(dim=1)
            all_preds.extend(preds.cpu())
            all_labels.extend(labels.cpu())
    
    return {
        'accuracy': accuracy_score(all_labels, all_preds),
        'precision': precision_score(all_labels, all_preds, average='macro'),
        'recall': recall_score(all_labels, all_preds, average='macro'),
        'f1': f1_score(all_labels, all_preds, average='macro')
    }

plot_gate_metrics(random_acc, baseline_acc, proposed_acc, threshold):
    fig, ax = plt.subplots()
    bars = ax.bar(['Random', 'Baseline', 'Proposed'], 
                  [random_acc, baseline_acc, proposed_acc])
    ax.axhline(threshold, color='red', linestyle='--', label='Gate Threshold')
    ax.set_ylabel('Test Accuracy')
    ax.set_ylim([0, 1])
    ax.legend()
    plt.savefig(save_path)

visualize_attention(model, sample_input):
    # Forward pass with attention hooks
    attn_weights = model.get_attention_weights(sample_input)  # [B, nhead, T, T]
    
    # Average over batch and heads
    attn_map = attn_weights.mean(dim=[0, 1])  # [T, T]
    
    # Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(attn_map.cpu().numpy(), cmap='viridis')
    plt.xlabel('Layer Index (Key)')
    plt.ylabel('Layer Index (Query)')
    plt.title('Transformer Attention Over Layers')
    plt.savefig(save_path)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Test evaluation | Accuracy/precision/recall/F1 |
| L-5-2 | Confusion matrix | sklearn + seaborn heatmap |
| L-5-3 | Training curves | Loss and accuracy plots |
| L-5-4 | Gate metrics | Bar chart with threshold |
| L-5-5 | Attention visualization | Transformer attention heatmap |
| L-5-6 | Figure saving | All plots to figures/ directory |

---

## Critical Design Decisions

### 1. Padding Strategy

**Decision:** Zero-pad to max_layer_size (4096)

**Rationale:**
- Fixed-size tokens required for batch processing
- Zero-padding preserves original values without bias
- Truncation for outlier large layers (e.g., final classifier)

**Edge Case:** Empty layers → skip during extraction

### 2. Normalization

**Decision:** Per-layer zero mean, unit variance

**Rationale:**
- Layer weights have different scales (conv vs linear)
- Per-layer normalization preserves within-layer structure
- Prevents large layers from dominating attention

**Alternative:** Global normalization → rejected (loses layer-specific scale)

### 3. Pooling Method

**Decision:** Mean pooling over layers

**Rationale:**
- Simple and effective for classification
- Captures global information from all layers
- Alternative: CLS token → adds complexity without clear benefit for PoC

### 4. Position Encoding

**Decision:** Sinusoidal encoding on layer index

**Rationale:**
- Standard transformer practice
- Captures layer depth information
- Generalizes to unseen layer counts

### 5. Gradient Clipping

**Decision:** max_norm = 1.0

**Rationale:**
- Prevents exploding gradients in transformer
- Weight-space learning can have unstable gradients
- Standard practice for transformers

---

## Edge Case Handling

### OOM Prevention

```python
# Limit max layer size
if layer.numel() > max_layer_size:
    layer = layer.flatten()[:max_layer_size]

# Batch size reduction if OOM
try:
    loss.backward()
except RuntimeError as e:
    if "out of memory" in str(e):
        torch.cuda.empty_cache()
        # Retry with smaller batch
```

### Empty Layers

```python
# Skip non-weight parameters
def extract_weights(model):
    weights = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() >= 2:
            weights.append(param.data)
    return weights
```

### Variable Layer Counts

```python
# Pad sequence to max layers if needed
def collate_fn(batch):
    max_layers = max(len(x) for x, _ in batch)
    padded = []
    for x, y in batch:
        if len(x) < max_layers:
            pad = torch.zeros(max_layers - len(x), x.shape[1])
            x = torch.cat([x, pad], dim=0)
        padded.append((x, y))
    return torch.stack([x for x, _ in padded]), torch.tensor([y for _, y in padded])
```

### Imbalanced Classes

```python
# Stratified split by architecture family
from sklearn.model_selection import StratifiedShuffleSplit

splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.3, random_state=42)
train_idx, temp_idx = next(splitter.split(X, families))
# Further split temp into val/test
```

---

## API Contract Summary

### Data Pipeline
- Input: timm model names (list[str])
- Output: Tokenized weights [B, T, max_size], labels [B]

### Models
- Baseline: `forward([B, 3*T]) -> [B, C]`
- Transformer: `forward([B, T, max_size]) -> [B, C]`

### Training
- Input: DataLoader, epochs, patience
- Output: {train_history, val_history, best_checkpoint}

### Evaluation
- Input: model, test_loader
- Output: {accuracy, precision, recall, f1} + figures

---

## Validation Checklist

- [x] All API signatures copy-paste ready
- [x] Tensor shapes annotated at each step
- [x] Pseudo-code for complex algorithms (tokenization, training loop)
- [x] Edge case handling (OOM, empty layers, variable sizes)
- [x] Critical decisions documented (padding, normalization, pooling)
- [x] Total subtasks within budget (35/35 used)
- [x] Codebase Analysis section included
- [x] No ASCII diagrams
- [x] Docstrings ≤ 2 lines
- [x] Total length < 600 lines

---

*Logic Status: FINAL*  
*Next Phase: Phase 4 - Implementation (Coder-Validator loop)*
