"""H-M1 Experiment: Orbit-PE Mechanism Verification
Entry point: python run_experiment.py

MUST_WORK gate:
  PASS if computability_rate==1.0 AND unified_codebase==True AND overhead_ratio_mean<=1.2
  FAIL otherwise → route to Phase 2A
"""
import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main(config_path: str = None) -> bool:
    """Run H-M1 benchmark experiment end-to-end.

    Returns: True if gate PASS, False if gate FAIL.
    """
    print("=" * 70)
    print("H-M1: Orbit-PE Architecture-Agnostic Computability Benchmark")
    print("=" * 70)

    # ── 1. Load config ────────────────────────────────────────────────────
    from config import load_config
    cfg = load_config(config_path)
    print(f"\nConfig: n_cnn={cfg.n_cnn_checkpoints}, n_transformer={cfg.n_transformer_checkpoints}")
    print(f"  token_dim={cfg.token_dim}, overhead_threshold={cfg.overhead_threshold}")
    print(f"  device={cfg.device}")

    # ── 2. Load checkpoints ───────────────────────────────────────────────
    from data_loader import CNNZooLoader, TransformerZooLoader

    print(f"\nLoading CNN Zoo checkpoints (n={cfg.n_cnn_checkpoints})...")
    cnn_loader = CNNZooLoader(
        zoo_dir=cfg.cnn_zoo_dir,
        n_checkpoints=cfg.n_cnn_checkpoints,
        seed=cfg.sample_seed,
    )
    try:
        cnn_checkpoints = cnn_loader.load_checkpoints()
    except Exception as e:
        logger.error("CNN Zoo loading failed: %s", e)
        cnn_checkpoints = []
    print(f"  Loaded {len(cnn_checkpoints)} CNN checkpoints")

    print(f"\nLoading Transformer Zoo checkpoints (n_mnist={cfg.n_transformer_checkpoints})...")
    # CRITICAL: use n_mnist kwarg (not n_checkpoints)
    tf_loader = TransformerZooLoader(
        mnist_dir=cfg.transformer_mnist_dir,
        n_mnist=cfg.n_transformer_checkpoints,
        seed=cfg.sample_seed,
    )
    try:
        transformer_checkpoints = tf_loader.load_checkpoints()
    except Exception as e:
        logger.error("Transformer Zoo loading failed: %s", e)
        transformer_checkpoints = []
    print(f"  Loaded {len(transformer_checkpoints)} Transformer checkpoints")

    total = len(cnn_checkpoints) + len(transformer_checkpoints)
    if total == 0:
        logger.error("No checkpoints loaded. Aborting.")
        return False
    print(f"\nTotal checkpoints: {total}")

    # ── 3. Init models ────────────────────────────────────────────────────
    from orbit_pe_computer import OrbitPEComputer, HAS_ARCH_BRANCHES
    from sequential_pe_baseline import SequentialPEBaseline

    orbit_computer = OrbitPEComputer(
        token_dim=cfg.token_dim,
        orbit_embed_dim=cfg.orbit_embed_dim,
    )
    orbit_computer.eval()

    baseline = SequentialPEBaseline(token_dim=cfg.token_dim)
    baseline.eval()

    print(f"\nOrbitPEComputer: HAS_ARCH_BRANCHES={HAS_ARCH_BRANCHES}")

    # ── 4. Run benchmark ──────────────────────────────────────────────────
    from benchmark import run_timing_benchmark

    print(f"\nRunning timing benchmark ({total} checkpoints)...")
    results = run_timing_benchmark(
        cnn_checkpoints=cnn_checkpoints,
        transformer_checkpoints=transformer_checkpoints,
        orbit_computer=orbit_computer,
        baseline=baseline,
        cfg=cfg,
    )
    print(f"Benchmark complete: {len(results)} results")

    # ── 5. Compute gate metrics ───────────────────────────────────────────
    from evaluate import compute_gate_metrics, save_metrics, generate_validation_report

    metrics = compute_gate_metrics(results, has_arch_branches=HAS_ARCH_BRANCHES)
    print(f"\nGate Metrics:")
    print(f"  computability_rate = {metrics.computability_rate:.4f}")
    print(f"  unified_codebase   = {metrics.unified_codebase}")
    print(f"  overhead_ratio_mean = {metrics.overhead_ratio_mean:.4f} ± {metrics.overhead_ratio_std:.4f}")
    print(f"  dim_consistent     = {metrics.dim_consistent}")
    print(f"  gate_pass          = {metrics.gate_pass}")

    # ── 6. Save metrics ───────────────────────────────────────────────────
    os.makedirs("outputs", exist_ok=True)
    save_metrics(metrics, cfg.results_path)

    # Determine validation report path (../04_validation.md relative to code/)
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "04_validation.md")
    generate_validation_report(metrics, report_path)

    # ── 7. Save figures ───────────────────────────────────────────────────
    from visualize import save_all_figures

    os.makedirs(cfg.figures_dir, exist_ok=True)
    try:
        save_all_figures(results, metrics, cfg.figures_dir)
    except Exception as e:
        logger.warning("Figure generation failed (non-fatal): %s", e)

    # ── 8. Final summary ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    verdict = "PASS" if metrics.gate_pass else "FAIL"
    print(f"EXPERIMENT COMPLETE — Gate: {verdict}")
    print(f"  computability_rate = {metrics.computability_rate:.4f}")
    print(f"  overhead_ratio_mean = {metrics.overhead_ratio_mean:.4f}")
    print(f"  unified_codebase = {metrics.unified_codebase}")
    print("=" * 70)

    return metrics.gate_pass


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    success = main(config_path)
    sys.exit(0 if success else 1)
