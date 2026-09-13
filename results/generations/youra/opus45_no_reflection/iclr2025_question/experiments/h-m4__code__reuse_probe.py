"""H-M4 Probe Reuse: Retrain H-M3 probe identically."""
import sys
from pathlib import Path


def get_probe_scores(h_m1_cache_folder: str, h_m3_code_path: str, seed: int = 42) -> dict:
    """Retrain H-M3 probe identically; return val scores + labels."""
    # Resolve paths relative to this file's location
    code_dir = Path(__file__).parent.resolve()
    h_m3_abs = (code_dir / h_m3_code_path).resolve()
    h_m1_abs = (code_dir / h_m1_cache_folder).resolve()

    # Add H-M3 code to path
    sys.path.insert(0, str(h_m3_abs))
    from probe import LinearCorrectnessProbe
    from data import load_hidden_states, scale_features

    # Load cached hidden states from H-M1
    X_train, y_train, X_val, y_val = load_hidden_states(str(h_m1_abs))

    # Scale features
    X_train_s, X_val_s, scaler = scale_features(X_train, X_val)

    # Retrain probe with same hyperparameters
    probe = LinearCorrectnessProbe(C=1e-3, max_iter=2000)
    probe.fit(X_train_s, y_train)

    # Get val scores
    probe_scores = probe.predict_proba(X_val_s)

    # Sanity check
    auroc = probe.evaluate(X_val_s, y_val)
    print(f"Probe AUROC sanity check: {auroc:.4f} (expected ~0.8851)")

    return {
        "probe_scores": probe_scores,
        "y_val": y_val,
        "probe": probe,
        "scaler": scaler,
        "probe_auroc": auroc
    }
