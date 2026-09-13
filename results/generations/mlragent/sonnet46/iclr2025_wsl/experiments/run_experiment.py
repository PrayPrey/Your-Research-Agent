"""
Main experiment runner for SymAE weight space learning.
"""

import os
import sys
import json
import time
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Batch
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA as skPCA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
ZOO_DIR = "/tmp/model_zoo_wsl"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(ZOO_DIR, exist_ok=True)

log_path = os.path.join(BASE_DIR, "log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from model_zoo import build_model_zoo, HIDDEN_SIZE, compute_weight_dim
from symae import SymAE, FlatMLPAutoencoder, build_network_graph
from visualize import (
    plot_training_curves, plot_property_prediction_curves,
    plot_r2_comparison, plot_latent_space, plot_scatter_predictions,
    plot_accuracy_distribution, plot_reconstruction_quality
)

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def normalize_weights(weight_matrix):
    scaler = StandardScaler()
    return scaler.fit_transform(weight_matrix), scaler


def get_embeddings_symae(model, graphs, batch_size=32):
    model.eval()
    all_z = []
    with torch.no_grad():
        for start in range(0, len(graphs), batch_size):
            bg = Batch.from_data_list(graphs[start:start + batch_size]).to(DEVICE)
            z = model.encode(bg)
            all_z.append(z.cpu().numpy())
    return np.concatenate(all_z, axis=0)


def get_embeddings_flat(model, weight_tensor, batch_size=64):
    model.eval()
    all_z = []
    with torch.no_grad():
        for start in range(0, len(weight_tensor), batch_size):
            z = model.encode(weight_tensor[start:start + batch_size])
            all_z.append(z.cpu().numpy())
    return np.concatenate(all_z, axis=0)


def linear_probe(Z, labels, idx_train, idx_val):
    """Evaluate embedding quality via Ridge regression."""
    ridge = Ridge(alpha=0.1)
    ridge.fit(Z[idx_train], labels[idx_train])
    y_pred = ridge.predict(Z[idx_val])
    return y_pred, r2_score(labels[idx_val], y_pred), mean_absolute_error(labels[idx_val], y_pred)


def train_symae(graphs, weight_norm, labels_norm, labels_raw,
                latent_dim=32, num_epochs=100, batch_size=32,
                alpha=1.0, beta=0.05, lr=1e-3):
    """Train SymAE with GNN encoder."""
    N = len(graphs)
    model = SymAE(hidden_size=HIDDEN_SIZE, latent_dim=latent_dim, alpha=alpha, beta=beta).to(DEVICE)

    weight_tensor = torch.tensor(weight_norm, dtype=torch.float).to(DEVICE)
    label_tensor = torch.tensor(labels_norm, dtype=torch.float).to(DEVICE)

    idx_all = np.arange(N)
    idx_train, idx_val = train_test_split(idx_all, test_size=0.2, random_state=42)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    history = {
        "train_loss": [], "train_rec_loss": [], "train_prop_loss": [],
        "val_loss": [], "val_rec_loss": [], "val_prop_loss": []
    }

    for epoch in range(num_epochs):
        model.train()
        np.random.shuffle(idx_train)
        el = er = ep = nb = 0

        for start in range(0, len(idx_train), batch_size):
            batch_idx = idx_train[start:start + batch_size]
            if len(batch_idx) < 2:
                continue

            g_batch = Batch.from_data_list([graphs[i] for i in batch_idx]).to(DEVICE)
            w_batch = weight_tensor[batch_idx]
            y_batch = label_tensor[batch_idx]

            optimizer.zero_grad()

            z = model.encode(g_batch)
            w_rec = model.decode(z)
            y_pred = model.predict_property(z)

            rec_loss = F.mse_loss(w_rec, w_batch)
            prop_loss = F.mse_loss(y_pred, y_batch)

            # Contrastive loss with permutation augmentation
            cont_loss = torch.tensor(0.0, device=DEVICE)
            if beta > 0 and len(batch_idx) >= 4:
                perm_idx = batch_idx[:min(16, len(batch_idx))]
                aug_graphs = []
                for pi in perm_idx:
                    w_perm = model.permute_weights(weight_tensor[pi].cpu())
                    aug_graphs.append(build_network_graph(w_perm, hidden_size=HIDDEN_SIZE))

                g_orig_b = Batch.from_data_list([graphs[pi] for pi in perm_idx]).to(DEVICE)
                g_aug_b = Batch.from_data_list(aug_graphs).to(DEVICE)
                z_orig = model.encode(g_orig_b)
                z_aug = model.encode(g_aug_b)
                cont_loss = model.contrastive_loss(z_orig, z_aug)

            total_loss = rec_loss + alpha * prop_loss + beta * cont_loss
            total_loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            el += total_loss.item(); er += rec_loss.item(); ep += prop_loss.item(); nb += 1

        if nb > 0:
            history["train_loss"].append(el / nb)
            history["train_rec_loss"].append(er / nb)
            history["train_prop_loss"].append(ep / nb)

        # Validation
        model.eval()
        vl = vr = vp = nv = 0
        with torch.no_grad():
            for start in range(0, len(idx_val), batch_size):
                bi = idx_val[start:start + batch_size]
                g_b = Batch.from_data_list([graphs[i] for i in bi]).to(DEVICE)
                w_b = weight_tensor[bi]
                y_b = label_tensor[bi]
                z = model.encode(g_b)
                vr_i = F.mse_loss(model.decode(z), w_b).item()
                vp_i = F.mse_loss(model.predict_property(z), y_b).item()
                vr += vr_i; vp += vp_i
                vl += vr_i + alpha * vp_i; nv += 1

        if nv > 0:
            history["val_loss"].append(vl / nv)
            history["val_rec_loss"].append(vr / nv)
            history["val_prop_loss"].append(vp / nv)

        scheduler.step()

        if (epoch + 1) % 10 == 0:
            logger.info(f"  [SymAE] Epoch {epoch+1}/{num_epochs}: "
                        f"train={history['train_loss'][-1]:.4f}, "
                        f"val={history['val_loss'][-1]:.4f}")

    # Get all embeddings
    Z = get_embeddings_symae(model, graphs, batch_size=32)

    # Linear probing
    y_pred_val, r2, mae = linear_probe(Z, labels_raw, idx_train, idx_val)

    # Reconstruction errors on val set
    rec_errors = []
    model.eval()
    with torch.no_grad():
        for i in idx_val:
            g_b = Batch.from_data_list([graphs[i]]).to(DEVICE)
            z = model.encode(g_b)
            err = F.mse_loss(model.decode(z), weight_tensor[i:i+1]).item()
            rec_errors.append(err)

    return model, history, {"r2": float(r2), "mae": float(mae)}, Z, idx_train, idx_val, \
           np.array(rec_errors), labels_raw[idx_val], y_pred_val


def train_flat_mlp(weight_norm, labels_norm, labels_raw,
                   latent_dim=32, num_epochs=100, batch_size=32,
                   alpha=1.0, lr=1e-3):
    """Train flat MLP AE baseline."""
    N = len(weight_norm)
    weight_dim = weight_norm.shape[1]

    model = FlatMLPAutoencoder(
        weight_dim=weight_dim, latent_dim=latent_dim, hidden_dim=256, alpha=alpha
    ).to(DEVICE)

    weight_tensor = torch.tensor(weight_norm, dtype=torch.float).to(DEVICE)
    label_tensor = torch.tensor(labels_norm, dtype=torch.float).to(DEVICE)

    idx_all = np.arange(N)
    idx_train, idx_val = train_test_split(idx_all, test_size=0.2, random_state=42)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)

    history = {
        "train_loss": [], "train_rec_loss": [], "train_prop_loss": [],
        "val_loss": [], "val_rec_loss": [], "val_prop_loss": []
    }

    for epoch in range(num_epochs):
        model.train()
        np.random.shuffle(idx_train)
        el = er = ep = nb = 0

        for start in range(0, len(idx_train), batch_size):
            bi = idx_train[start:start + batch_size]
            w_b = weight_tensor[bi]; y_b = label_tensor[bi]
            optimizer.zero_grad()
            z = model.encode(w_b)
            rec_loss = F.mse_loss(model.decode(z), w_b)
            prop_loss = F.mse_loss(model.predict_property(z), y_b)
            total = rec_loss + alpha * prop_loss
            total.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            el += total.item(); er += rec_loss.item(); ep += prop_loss.item(); nb += 1

        history["train_loss"].append(el / max(nb, 1))
        history["train_rec_loss"].append(er / max(nb, 1))
        history["train_prop_loss"].append(ep / max(nb, 1))

        model.eval()
        vl = vr = vp = nv = 0
        with torch.no_grad():
            for start in range(0, len(idx_val), batch_size):
                bi = idx_val[start:start + batch_size]
                w_b = weight_tensor[bi]; y_b = label_tensor[bi]
                z = model.encode(w_b)
                vr_i = F.mse_loss(model.decode(z), w_b).item()
                vp_i = F.mse_loss(model.predict_property(z), y_b).item()
                vr += vr_i; vp += vp_i; vl += vr_i + alpha * vp_i; nv += 1

        history["val_loss"].append(vl / max(nv, 1))
        history["val_rec_loss"].append(vr / max(nv, 1))
        history["val_prop_loss"].append(vp / max(nv, 1))

        scheduler.step()

        if (epoch + 1) % 10 == 0:
            logger.info(f"  [FlatMLP-AE] Epoch {epoch+1}/{num_epochs}: "
                        f"train={history['train_loss'][-1]:.4f}, "
                        f"val={history['val_loss'][-1]:.4f}")

    Z = get_embeddings_flat(model, weight_tensor, batch_size=64)
    y_pred_val, r2, mae = linear_probe(Z, labels_raw, idx_train, idx_val)

    rec_errors = []
    model.eval()
    with torch.no_grad():
        for i in idx_val:
            z = model.encode(weight_tensor[i:i+1])
            err = F.mse_loss(model.decode(z), weight_tensor[i:i+1]).item()
            rec_errors.append(err)

    return model, history, {"r2": float(r2), "mae": float(mae)}, Z, idx_train, idx_val, \
           np.array(rec_errors), labels_raw[idx_val], y_pred_val


def run_pca_baseline(weight_norm, labels_raw, latent_dim=32):
    """PCA baseline."""
    pca = skPCA(n_components=latent_dim, random_state=42)
    Z = pca.fit_transform(weight_norm)
    W_rec = pca.inverse_transform(Z)

    idx_all = np.arange(len(labels_raw))
    idx_train, idx_val = train_test_split(idx_all, test_size=0.2, random_state=42)

    y_pred_val, r2, mae = linear_probe(Z, labels_raw, idx_train, idx_val)

    rec_errors = np.mean((weight_norm[idx_val] - W_rec[idx_val]) ** 2, axis=1)
    exp_var = float(pca.explained_variance_ratio_.sum())

    return Z, {"r2": float(r2), "mae": float(mae), "explained_variance": exp_var}, \
           idx_train, idx_val, rec_errors, labels_raw[idx_val], y_pred_val


def run_statistics_baseline(weight_matrix, labels_raw):
    """Hand-crafted weight statistics baseline."""
    features = []
    for w in weight_matrix:
        feat = [
            w.mean(), w.std(), np.abs(w).mean(),
            np.percentile(w, 10), np.percentile(w, 25),
            np.percentile(w, 75), np.percentile(w, 90),
            w.min(), w.max(), (w > 0).mean()
        ]
        features.append(feat)

    Z = np.array(features)
    idx_all = np.arange(len(labels_raw))
    idx_train, idx_val = train_test_split(idx_all, test_size=0.2, random_state=42)
    y_pred_val, r2, mae = linear_probe(Z, labels_raw, idx_train, idx_val)
    return Z, {"r2": float(r2), "mae": float(mae)}, idx_train, idx_val, labels_raw[idx_val], y_pred_val


def main():
    logger.info("=" * 60)
    logger.info("SymAE: Symmetry-Aware Weight Space Learning Experiment")
    logger.info("=" * 60)
    logger.info(f"Device: {DEVICE}")

    # ========================
    # Step 1: Build Model Zoo
    # ========================
    logger.info("\n[Step 1] Building Model Zoo...")
    t0 = time.time()

    zoo_weights_path = os.path.join(ZOO_DIR, "weights.npy")
    zoo_meta_path = os.path.join(ZOO_DIR, "metadata.json")

    if os.path.exists(zoo_weights_path) and os.path.exists(zoo_meta_path):
        logger.info("  Loading cached model zoo...")
        weight_matrix = np.load(zoo_weights_path)
        with open(zoo_meta_path) as f:
            metadata = json.load(f)
    else:
        weight_matrix, metadata = build_model_zoo(num_models=200, save_dir=ZOO_DIR)

    labels_raw = np.array([m["test_accuracy"] for m in metadata])
    N = len(labels_raw)
    weight_dim = weight_matrix.shape[1]

    logger.info(f"  Zoo: {N} models, weight_dim={weight_dim}")
    logger.info(f"  Accuracy: mean={labels_raw.mean():.3f}, std={labels_raw.std():.3f}, "
                f"range=[{labels_raw.min():.3f}, {labels_raw.max():.3f}]")
    logger.info(f"  Zoo build time: {time.time()-t0:.1f}s")

    plot_accuracy_distribution(
        labels_raw.tolist(),
        os.path.join(RESULTS_DIR, "accuracy_distribution.png")
    )

    # Normalize weights and labels
    weight_norm, scaler = normalize_weights(weight_matrix)
    label_mean, label_std = labels_raw.mean(), labels_raw.std() + 1e-8
    labels_norm = (labels_raw - label_mean) / label_std

    # ========================
    # Step 2: Build Graphs
    # ========================
    logger.info("\n[Step 2] Building graph representations for SymAE...")
    t0 = time.time()
    graphs = [build_network_graph(
        torch.tensor(weight_matrix[i], dtype=torch.float),
        hidden_size=HIDDEN_SIZE
    ) for i in range(N)]
    logger.info(f"  Built {N} graphs. Example: {graphs[0].x.shape[0]} nodes, "
                f"{graphs[0].edge_index.shape[1]} edges. Time: {time.time()-t0:.1f}s")

    # ========================
    # Step 3: Train SymAE
    # ========================
    logger.info("\n[Step 3] Training SymAE (GNN encoder, equivariant to permutation symmetries)...")
    t0 = time.time()
    (symae_model, symae_hist, symae_metrics, symae_Z,
     s_idx_train, s_idx_val, symae_rec_err,
     symae_y_true, symae_y_pred) = train_symae(
        graphs, weight_norm, labels_norm, labels_raw,
        latent_dim=32, num_epochs=100, batch_size=32, alpha=1.0, beta=0.05, lr=1e-3
    )
    logger.info(f"  SymAE: R²={symae_metrics['r2']:.4f}, MAE={symae_metrics['mae']:.4f}. "
                f"Time: {time.time()-t0:.1f}s")

    # ========================
    # Step 4: Train Flat MLP AE
    # ========================
    logger.info("\n[Step 4] Training Flat MLP Autoencoder baseline...")
    t0 = time.time()
    (flat_model, flat_hist, flat_metrics, flat_Z,
     f_idx_train, f_idx_val, flat_rec_err,
     flat_y_true, flat_y_pred) = train_flat_mlp(
        weight_norm, labels_norm, labels_raw,
        latent_dim=32, num_epochs=100, batch_size=32, alpha=1.0, lr=1e-3
    )
    logger.info(f"  FlatMLP-AE: R²={flat_metrics['r2']:.4f}, MAE={flat_metrics['mae']:.4f}. "
                f"Time: {time.time()-t0:.1f}s")

    # ========================
    # Step 5: PCA Baseline
    # ========================
    logger.info("\n[Step 5] Running PCA baseline...")
    (pca_Z, pca_metrics, pca_train, pca_val,
     pca_rec_err, pca_y_true, pca_y_pred) = run_pca_baseline(
        weight_norm, labels_raw, latent_dim=32
    )
    logger.info(f"  PCA: R²={pca_metrics['r2']:.4f}, MAE={pca_metrics['mae']:.4f}, "
                f"ExplVar={pca_metrics['explained_variance']:.3f}")

    # ========================
    # Step 6: Statistics Baseline
    # ========================
    logger.info("\n[Step 6] Running Statistics baseline...")
    (stats_Z, stats_metrics, st_train, st_val,
     stats_y_true, stats_y_pred) = run_statistics_baseline(weight_matrix, labels_raw)
    logger.info(f"  Statistics: R²={stats_metrics['r2']:.4f}, MAE={stats_metrics['mae']:.4f}")

    # ========================
    # Step 7: Generate Figures
    # ========================
    logger.info("\n[Step 7] Generating visualization figures...")

    plot_training_curves(
        [symae_hist, flat_hist],
        ["SymAE (GNN)", "Flat MLP AE"],
        os.path.join(RESULTS_DIR, "training_curves.png")
    )

    plot_property_prediction_curves(
        [symae_hist, flat_hist],
        ["SymAE (GNN)", "Flat MLP AE"],
        os.path.join(RESULTS_DIR, "property_loss_curves.png")
    )

    all_methods = ["SymAE (GNN)", "Flat MLP AE", "PCA", "Statistics"]
    all_r2 = [symae_metrics["r2"], flat_metrics["r2"], pca_metrics["r2"], stats_metrics["r2"]]
    all_mae = [symae_metrics["mae"], flat_metrics["mae"], pca_metrics["mae"], stats_metrics["mae"]]

    plot_r2_comparison(
        all_methods, all_r2, all_mae,
        os.path.join(RESULTS_DIR, "r2_comparison.png")
    )

    plot_latent_space(
        {"SymAE (GNN)": symae_Z, "Flat MLP AE": flat_Z, "PCA": pca_Z},
        labels_raw.tolist(),
        os.path.join(RESULTS_DIR, "latent_space.png")
    )

    plot_scatter_predictions(
        {"SymAE (GNN)": symae_y_true, "Flat MLP AE": flat_y_true, "PCA": pca_y_true},
        {"SymAE (GNN)": symae_y_pred, "Flat MLP AE": flat_y_pred, "PCA": pca_y_pred},
        os.path.join(RESULTS_DIR, "scatter_predictions.png")
    )

    plot_reconstruction_quality(
        [symae_rec_err, flat_rec_err, pca_rec_err],
        ["SymAE (GNN)", "Flat MLP AE", "PCA"],
        os.path.join(RESULTS_DIR, "reconstruction_quality.png")
    )

    # ========================
    # Step 8: Save Results
    # ========================
    logger.info("\n[Step 8] Saving results...")

    results = {
        "experiment": "SymAE Weight Space Learning",
        "device": str(DEVICE),
        "zoo_size": int(N),
        "weight_dim": int(weight_dim),
        "latent_dim": 32,
        "num_epochs": 100,
        "batch_size": 32,
        "hidden_size": int(HIDDEN_SIZE),
        "methods": {
            "SymAE (GNN)": {
                "description": "GNN encoder with permutation symmetry handling + contrastive loss",
                "r2": symae_metrics["r2"],
                "mae": symae_metrics["mae"],
                "final_train_loss": float(symae_hist["train_loss"][-1]),
                "final_val_loss": float(symae_hist["val_loss"][-1]),
                "mean_rec_error": float(symae_rec_err.mean()),
            },
            "Flat MLP AE": {
                "description": "Flat MLP autoencoder on raw/normalized weight vectors",
                "r2": flat_metrics["r2"],
                "mae": flat_metrics["mae"],
                "final_train_loss": float(flat_hist["train_loss"][-1]),
                "final_val_loss": float(flat_hist["val_loss"][-1]),
                "mean_rec_error": float(flat_rec_err.mean()),
            },
            "PCA": {
                "description": "PCA on normalized weight vectors (32 components)",
                "r2": pca_metrics["r2"],
                "mae": pca_metrics["mae"],
                "explained_variance": pca_metrics["explained_variance"],
                "mean_rec_error": float(pca_rec_err.mean()),
            },
            "Statistics": {
                "description": "Hand-crafted weight statistics features",
                "r2": stats_metrics["r2"],
                "mae": stats_metrics["mae"],
            }
        },
        "model_zoo_stats": {
            "mean_accuracy": float(labels_raw.mean()),
            "std_accuracy": float(labels_raw.std()),
            "min_accuracy": float(labels_raw.min()),
            "max_accuracy": float(labels_raw.max()),
        }
    }

    with open(os.path.join(RESULTS_DIR, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(RESULTS_DIR, "symae_history.json"), "w") as f:
        json.dump(symae_hist, f)
    with open(os.path.join(RESULTS_DIR, "flat_mlp_history.json"), "w") as f:
        json.dump(flat_hist, f)

    # ========================
    # Summary
    # ========================
    logger.info("\n" + "=" * 60)
    logger.info("FINAL RESULTS SUMMARY")
    logger.info("=" * 60)
    logger.info(f"{'Method':<20} {'R²':>8} {'MAE':>10}")
    logger.info("-" * 40)
    for method, r2, mae in zip(all_methods, all_r2, all_mae):
        logger.info(f"{method:<20} {r2:>8.4f} {mae:>10.4f}")

    best_idx = int(np.argmax(all_r2))
    logger.info(f"\nBest method: {all_methods[best_idx]} (R²={all_r2[best_idx]:.4f})")
    logger.info(f"SymAE vs PCA R² delta: {symae_metrics['r2'] - pca_metrics['r2']:+.4f}")
    logger.info(f"SymAE vs FlatMLP R² delta: {symae_metrics['r2'] - flat_metrics['r2']:+.4f}")
    logger.info(f"\nAll results saved to: {RESULTS_DIR}")
    logger.info("Experiment complete.")


if __name__ == "__main__":
    main()
