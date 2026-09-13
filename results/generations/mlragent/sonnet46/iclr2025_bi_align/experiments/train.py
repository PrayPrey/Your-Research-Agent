"""
Training routines for CAVE and baseline models.
"""

import numpy as np
import torch
from torch.optim import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from config import (
    LEARNING_RATE, BATCH_SIZE, NUM_EPOCHS, DEVICE, HELD_OUT_FRACTION, NUM_USERS
)
from evaluation import compute_preference_auc


def make_tensors(batch, device=DEVICE):
    """Convert batch dict to tensors."""
    user_ids = torch.tensor(batch['user_ids'], dtype=torch.long, device=device)
    action_a = torch.tensor(batch['action_a'], dtype=torch.long, device=device)
    action_b = torch.tensor(batch['action_b'], dtype=torch.long, device=device)
    contexts = torch.tensor(batch['contexts'], dtype=torch.float32, device=device)
    prefs = torch.tensor(batch['preferences'], dtype=torch.float32, device=device)
    return user_ids, action_a, action_b, contexts, prefs


def split_data(data, held_out_fraction=HELD_OUT_FRACTION):
    """Split interaction data into train and validation sets."""
    n = len(data['user_ids'])
    idx = np.arange(n)
    train_idx, val_idx = train_test_split(idx, test_size=held_out_fraction, random_state=42)

    def select(d, idx):
        return {k: v[idx] for k, v in d.items()}

    return select(data, train_idx), select(data, val_idx)


def train_model(model, data, model_name="model", n_epochs=NUM_EPOCHS,
                batch_size=BATCH_SIZE, lr=LEARNING_RATE, device=DEVICE, log_fn=print):
    """
    Train a model on preference data.
    Returns: train_losses, val_aucs per epoch.
    """
    train_data, val_data = split_data(data)
    n_train = len(train_data['user_ids'])

    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

    train_losses = []
    val_aucs = []

    log_fn(f"\n[{model_name}] Training on {n_train} samples, validating on {len(val_data['user_ids'])} samples")
    log_fn(f"[{model_name}] Device: {device}, Epochs: {n_epochs}, Batch size: {batch_size}")

    for epoch in range(n_epochs):
        model.train()
        epoch_losses = []
        perm = np.random.permutation(n_train)

        for start in range(0, n_train, batch_size):
            end = min(start + batch_size, n_train)
            batch_idx = perm[start:end]

            batch = {k: v[batch_idx] for k, v in train_data.items()}
            user_ids, action_a, action_b, contexts, prefs = make_tensors(batch, device)

            optimizer.zero_grad()
            loss, nll, kl = model.compute_loss(user_ids, action_a, action_b, contexts, prefs)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_losses.append(loss.item())

        scheduler.step()
        avg_loss = np.mean(epoch_losses)
        train_losses.append(avg_loss)
        model.train_losses.append(avg_loss)

        # Validation AUC
        val_auc = compute_preference_auc(model, val_data, device)
        val_aucs.append(val_auc)
        model.val_aucs.append(val_auc)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            log_fn(f"[{model_name}] Epoch {epoch+1:3d}/{n_epochs} | Loss: {avg_loss:.4f} | Val AUC: {val_auc:.4f}")

    log_fn(f"[{model_name}] Final Val AUC: {val_aucs[-1]:.4f}")
    return train_losses, val_aucs


def train_cave_with_elicitation(model, data, model_name="CAVE", n_epochs=NUM_EPOCHS,
                                batch_size=BATCH_SIZE, lr=LEARNING_RATE, device=DEVICE, log_fn=print):
    """
    Train CAVE with active elicitation policy.
    Simulates online interaction where feedback is only collected at high-uncertainty moments.
    Tracks: elicitation queries per epoch, drift events detected.
    """
    train_data, val_data = split_data(data)
    n_train = len(train_data['user_ids'])

    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

    train_losses = []
    val_aucs = []
    elicitation_counts = []  # queries per epoch
    drift_detections = []    # drift events per epoch

    log_fn(f"\n[{model_name}] Active Elicitation Training | {n_train} samples")

    for epoch in range(n_epochs):
        model.train()
        epoch_losses = []
        epoch_queries = 0
        perm = np.random.permutation(n_train)

        for start in range(0, n_train, batch_size):
            end = min(start + batch_size, n_train)
            batch_idx = perm[start:end]
            batch = {k: v[batch_idx] for k, v in train_data.items()}
            user_ids_np = batch['user_ids']
            user_ids, action_a, action_b, contexts, prefs = make_tensors(batch, device)

            # Compute uncertainty for active elicitation
            with torch.no_grad():
                _, uncertainties = model(user_ids, action_a, action_b, contexts)
                uncertainties = uncertainties.cpu().numpy()

            # Select samples to train on based on elicitation policy
            elicit_mask = []
            for i, uid in enumerate(user_ids_np):
                t = epoch * batch_size + i
                should_q = model.should_elicit(uncertainties[i], uid, t)
                elicit_mask.append(should_q)
                if should_q:
                    model.query_counts[uid] += 1
                    model.last_query_t[uid] = t
                    epoch_queries += 1

            elicit_mask = np.array(elicit_mask)
            if elicit_mask.sum() < 2:
                # Always use at least a random subset to avoid starvation
                elicit_mask = np.ones(len(user_ids_np), dtype=bool)

            # Train on elicited samples
            elicit_idx = np.where(elicit_mask)[0]
            if len(elicit_idx) > 0:
                sub_user_ids = user_ids[elicit_idx]
                sub_action_a = action_a[elicit_idx]
                sub_action_b = action_b[elicit_idx]
                sub_contexts = contexts[elicit_idx]
                sub_prefs = prefs[elicit_idx]

                optimizer.zero_grad()
                loss, nll, kl = model.compute_loss(
                    sub_user_ids, sub_action_a, sub_action_b, sub_contexts, sub_prefs
                )
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                epoch_losses.append(loss.item())

        scheduler.step()

        # Update drift history and detect drift events
        unique_users = np.unique(train_data['user_ids'][:100])  # check first 100 users
        drift_events = model.update_drift_history(unique_users)
        drift_detections.append(list(drift_events.keys()))

        avg_loss = np.mean(epoch_losses) if epoch_losses else float('nan')
        train_losses.append(avg_loss)
        model.train_losses.append(avg_loss)

        val_auc = compute_preference_auc(model, val_data, device)
        val_aucs.append(val_auc)
        model.val_aucs.append(val_auc)

        elicitation_counts.append(epoch_queries)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            log_fn(f"[{model_name}] Epoch {epoch+1:3d}/{n_epochs} | Loss: {avg_loss:.4f} | "
                   f"Val AUC: {val_auc:.4f} | Queries: {epoch_queries} | "
                   f"Drift events: {len(drift_events)}")

    log_fn(f"[{model_name}] Final Val AUC: {val_aucs[-1]:.4f}")
    log_fn(f"[{model_name}] Total queries: {sum(elicitation_counts)}")
    return train_losses, val_aucs, elicitation_counts, drift_detections
