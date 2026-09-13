import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from copy import deepcopy
import random
import numpy as np
from models import flatten_weights

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True

def prepare_flatten_batch(weights_list, input_dim, device):
    batch = []
    for wd in weights_list:
        flat = flatten_weights(wd)
        if flat.numel() < input_dim:
            flat = F.pad(flat, (0, input_dim - flat.numel()))
        else:
            flat = flat[:input_dim]
        batch.append(flat)
    return torch.stack(batch).to(device)

def train_one_epoch(model, loader, optimizer, device, method, input_dim=None):
    model.train()
    total_loss = 0
    total_samples = 0
    for weights_list, targets in loader:
        targets = targets.to(device)
        if method == "flatten":
            weights_input = prepare_flatten_batch(weights_list, input_dim, device)
        else:
            weights_input = weights_list
        preds = model(weights_input, device)
        loss = F.mse_loss(preds, targets)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(targets)
        total_samples += len(targets)
    return total_loss / total_samples

def validate(model, loader, device, method, input_dim=None):
    model.eval()
    total_loss = 0
    total_samples = 0
    with torch.no_grad():
        for weights_list, targets in loader:
            targets = targets.to(device)
            if method == "flatten":
                weights_input = prepare_flatten_batch(weights_list, input_dim, device)
            else:
                weights_input = weights_list
            preds = model(weights_input, device)
            loss = F.mse_loss(preds, targets)
            total_loss += loss.item() * len(targets)
            total_samples += len(targets)
    return total_loss / total_samples

def train_model(model, train_loader, val_loader, lr=1e-3, weight_decay=1e-4, max_epochs=50,
                early_stop_patience=10, device="cuda", method="flatten", input_dim=None):
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    best_val_loss = float('inf')
    patience_ctr = 0
    best_state = None
    history = {'train_loss': [], 'val_loss': []}

    for epoch in range(max_epochs):
        train_loss = train_one_epoch(model, train_loader, optimizer, device, method, input_dim)
        val_loss = validate(model, val_loader, device, method, input_dim)
        scheduler.step(val_loss)
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = deepcopy(model.state_dict())
            patience_ctr = 0
        else:
            patience_ctr += 1
            if patience_ctr >= early_stop_patience:
                break

    model.load_state_dict(best_state)
    return model, history

def save_checkpoint(model, path):
    torch.save(model.state_dict(), path)
