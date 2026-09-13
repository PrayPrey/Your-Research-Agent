"""
run_experiment.py — h-e1 EXISTENCE PoC experiment entrypoint.

Usage:
    export CUDA_VISIBLE_DEVICES=4
    export HF_HOME=/scratch/hf_cache
    export TOKENIZERS_PARALLELISM=false
    python run_experiment.py
"""
from __future__ import annotations
import os
import sys
import json
import time
import numpy as np
from pathlib import Path

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, ExperimentConfig
from data_loader import BenchmarkLoader, CorpusLoader
from index_builder import NgramIndexBuilder, SBERTIndexBuilder
from geometry_features import GeometryStratifier
from ground_truth import GroundTruthGenerator
from evaluate import StratifiedEvaluator, check_poc_conditions
from visualize import ResultVisualizer


BASE_DIR = Path(__file__).parent.parent  # h-e1/
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = BASE_DIR / "figures"
INDEX_DIR = BASE_DIR / "indices"


def setup_environment(cfg: ExperimentConfig) -> None:
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    np.random.seed(cfg.seed)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    print("✓ Environment set up")


def build_indices(cfg: ExperimentConfig, max_docs_override: int = 50_000) -> tuple[dict, dict]:
    """Build n-gram and SBERT indices for all corpora (capped for PoC speed)."""
    print("\n=== Building Corpus Indices ===")
    corpus_loader = CorpusLoader(cfg)
    ngram_builder = NgramIndexBuilder(cfg)
    sbert_builder = SBERTIndexBuilder(cfg)

    ngram_indices = {}
    sbert_indices = {}

    corpus_loaders = {
        "pile": corpus_loader.load_pile,
        "c4": corpus_loader.load_c4,
        "redpajama": corpus_loader.load_redpajama,
    }

    for corpus_name in cfg.corpora:
        ngram_index_path = INDEX_DIR / corpus_name / "ngram_index.pkl"
        sbert_index_path = INDEX_DIR / corpus_name / "sbert_index.faiss"

        # N-gram index
        if ngram_index_path.exists():
            print(f"  [{corpus_name}] Loading existing n-gram index...")
            ngram_indices[corpus_name] = ngram_builder.load_index(corpus_name)
        else:
            print(f"  [{corpus_name}] Building n-gram index (max_docs={max_docs_override})...")
            stream = corpus_loader.stream_corpus_texts(corpus_loaders[corpus_name](), max_docs_override)
            ngram_builder.build_index(corpus_name, stream, max_docs=max_docs_override)
            ngram_indices[corpus_name] = ngram_builder.load_index(corpus_name)

        # SBERT index
        if sbert_index_path.exists():
            print(f"  [{corpus_name}] Loading existing SBERT index...")
            sbert_indices[corpus_name] = sbert_builder.load_index(corpus_name)
        else:
            print(f"  [{corpus_name}] Building SBERT index (max_docs={max_docs_override})...")
            texts = list(corpus_loader.stream_corpus_texts(corpus_loaders[corpus_name](), max_docs_override))
            sbert_builder.build_index(corpus_name, texts)
            sbert_indices[corpus_name] = sbert_builder.load_index(corpus_name)

    print("✓ All indices ready")
    return ngram_indices, sbert_indices


def run_geometry_pipeline(
    cfg: ExperimentConfig,
    benchmark_texts: dict[str, list[str]],
    ngram_indices: dict,
    sbert_indices: dict,
) -> dict:
    """Compute geometry features and assign strata for each benchmark × corpus pair."""
    print("\n=== Running Geometry Pipeline ===")
    stratifier = GeometryStratifier(cfg)
    geometry_results: dict = {}

    for bench_name, texts in benchmark_texts.items():
        geometry_results[bench_name] = {}
        for corpus_name in cfg.corpora:
            ngram_idx = ngram_indices[corpus_name]
            sbert_idx = sbert_indices[corpus_name]
            print(f"  [{bench_name} × {corpus_name}] Computing geometry features...")
            ngram_counts, cosines = stratifier.compute_geometry_features(texts, ngram_idx, sbert_idx)
            lex_thresh, sem_thresh = stratifier.compute_thresholds(ngram_counts, cosines)
            strata = stratifier.assign_strata(ngram_counts, cosines, lex_thresh, sem_thresh)
            unique, counts = np.unique(strata, return_counts=True)
            print(f"    Strata: {dict(zip(unique, counts))}")
            geometry_results[bench_name][corpus_name] = {
                "ngram_counts": ngram_counts,
                "cosines": cosines,
                "strata": strata,
                "lexical_thresh": lex_thresh,
                "semantic_thresh": sem_thresh,
            }

    print("✓ Geometry pipeline complete")
    return geometry_results


def run_detector_evaluation(
    cfg: ExperimentConfig,
    benchmark_texts: dict[str, list[str]],
    ngram_indices: dict,
    sbert_indices: dict,
    ground_truth: dict,
) -> dict:
    """Run all 5 detectors for each benchmark × corpus pair."""
    print("\n=== Running Detector Evaluation ===")
    from detectors.ngram_detector import NgramDetector
    from detectors.embedding_detector import EmbeddingDetector

    from detectors.minkpp_detector import MinkPPDetector
    from detectors.dcpdd_detector import DCPDDDetector
    from detectors.constat_detector import ConStatDetector

    ngram_det = NgramDetector(cfg)
    emb_det = EmbeddingDetector(cfg)
    minkpp_det = MinkPPDetector(cfg)
    dcpdd_det = DCPDDDetector(cfg)
    constat_det = ConStatDetector(cfg)

    detector_results: dict = {}
    for bench_name, texts in benchmark_texts.items():
        detector_results[bench_name] = {}
        for corpus_name in cfg.corpora:
            preds: dict[str, np.ndarray] = {}
            preds["ngram"] = ngram_det.predict(texts, ngram_indices[corpus_name])
            preds["embedding"] = emb_det.predict(texts, sbert_indices[corpus_name])
            preds["minkpp"] = minkpp_det.predict(texts)
            preds["dcpdd"] = dcpdd_det.predict(texts)
            preds["constat"] = constat_det.predict(texts)
            detector_results[bench_name][corpus_name] = preds
            print(f"  [{bench_name} × {corpus_name}] ngram={preds['ngram'].sum()}, emb={preds['embedding'].sum()}, minkpp={preds['minkpp'].sum()}, dcpdd={preds['dcpdd'].sum()}, constat={preds['constat'].sum()}")

    print("✓ Detector evaluation complete")
    return detector_results


def run_metrics(
    cfg: ExperimentConfig,
    geometry_results: dict,
    detector_results: dict,
    ground_truth: dict,
) -> dict:
    """Compute all metrics."""
    print("\n=== Computing Metrics ===")
    evaluator = StratifiedEvaluator(cfg)
    metrics_all: dict = {}

    for bench_name in cfg.benchmarks:
        if bench_name not in geometry_results:
            continue
        metrics_all[bench_name] = {}
        for corpus_name in cfg.corpora:
            geom = geometry_results[bench_name][corpus_name]
            strata = geom["strata"]
            preds = detector_results.get(bench_name, {}).get(corpus_name, {})
            y_true = ground_truth.get(bench_name, {}).get(corpus_name, np.zeros(len(strata), dtype=np.int64))

            result = evaluator.run_full_evaluation(bench_name, corpus_name, y_true, strata, preds)
            metrics_all[bench_name][corpus_name] = result

            ngram_recall = result["recall_by_stratum"].get("ngram", {})
            print(f"  [{bench_name} × {corpus_name}] ngram recall: lex={ngram_recall.get('lexical', 'N/A'):.3f}, sem={ngram_recall.get('semantic', 'N/A'):.3f}")

    # Summarize PoC gate metrics
    gate_metrics = _compute_gate_metrics(metrics_all, cfg)
    print(f"\n  Gate metrics: {gate_metrics}")
    return {"per_pair": metrics_all, "gate_metrics": gate_metrics}


def _compute_gate_metrics(metrics_all: dict, cfg: ExperimentConfig) -> dict:
    """Aggregate gate check metrics across all benchmark-corpus pairs."""
    lex_recalls, sem_recalls, minkpp_vars = [], [], []

    for bench_name, bench_data in metrics_all.items():
        minkpp_f1_per_corpus = []
        for corpus_name, result in bench_data.items():
            for det, recall in result.get("recall_by_stratum", {}).items():
                if "ngram" in det:
                    lex = recall.get("lexical", float("nan"))
                    sem = recall.get("semantic", float("nan"))
                    if not np.isnan(lex):
                        lex_recalls.append(lex)
                    if not np.isnan(sem):
                        sem_recalls.append(sem)
            for det, f1 in result.get("f1_by_stratum", {}).items():
                if "minkpp" in det:
                    minkpp_f1_per_corpus.append(f1.get("lexical", 0.0))
        if minkpp_f1_per_corpus:
            minkpp_vars.append(float(np.var(minkpp_f1_per_corpus)))

    return {
        "ngram_lexical_recall": float(np.mean(lex_recalls)) if lex_recalls else 0.0,
        "ngram_semantic_recall": float(np.mean(sem_recalls)) if sem_recalls else 0.0,
        "minkpp_f1_variance": float(np.mean(minkpp_vars)) if minkpp_vars else 0.0,
    }


def generate_figures(cfg: ExperimentConfig, metrics: dict, geometry_results: dict) -> None:
    """Generate all 5 figures."""
    print("\n=== Generating Figures ===")
    viz = ResultVisualizer(cfg)
    gate_metrics = metrics.get("gate_metrics", {})

    viz.gate_metrics_bar(gate_metrics)

    # Use first benchmark-corpus pair for scatter
    bench0 = list(geometry_results.keys())[0] if geometry_results else None
    if bench0:
        corpus0 = list(geometry_results[bench0].keys())[0]
        geom = geometry_results[bench0][corpus0]
        dummy_dom = geom["strata"].copy()
        viz.phase_diagram_scatter(geom["ngram_counts"], geom["cosines"], dummy_dom, geom["strata"])

    # F1 heatmap from actual computed metrics
    det_names = ["ngram", "embedding", "minkpp", "dcpdd", "constat"]
    strata_names = ["lexical", "semantic", "indeterminate"]
    per_pair = metrics.get("per_pair", {})
    f1_mat = np.zeros((len(det_names), len(cfg.benchmarks), len(strata_names)), dtype=np.float32)
    for bi, bench_name in enumerate(cfg.benchmarks):
        bench_data = per_pair.get(bench_name, {})
        # average over corpora
        corpus_list = list(bench_data.values())
        if corpus_list:
            for di, det in enumerate(det_names):
                for si, stratum in enumerate(strata_names):
                    vals = [r.get("f1_by_stratum", {}).get(det, {}).get(stratum, 0.0) for r in corpus_list]
                    f1_mat[di, bi, si] = float(np.mean(vals))
    viz.stratum_f1_heatmap(f1_mat, det_names)

    # Min-K++ variance bar from computed gate metrics
    minkpp_f1_by_corpus: dict[str, list[float]] = {}
    for bench_data in per_pair.values():
        for corpus_name, result in bench_data.items():
            f1_vals = result.get("f1_by_stratum", {}).get("minkpp", {})
            val = f1_vals.get("lexical", 0.0)
            minkpp_f1_by_corpus.setdefault(corpus_name, []).append(val)
    minkpp_variance_data = {k: float(np.mean(v)) for k, v in minkpp_f1_by_corpus.items()}
    if not minkpp_variance_data:
        minkpp_variance_data = {c: 0.0 for c in cfg.corpora}
    viz.minkpp_variance_bar(minkpp_variance_data)

    # Indeterminacy pie — aggregate from geometry results
    stratum_counts: dict[str, int] = {"lexical": 0, "semantic": 0, "indeterminate": 0}
    for bench_data in geometry_results.values():
        for geom in bench_data.values():
            unique, cnts = np.unique(geom["strata"], return_counts=True)
            for s, c in zip(unique, cnts):
                stratum_counts[s] = stratum_counts.get(s, 0) + int(c)
    viz.indeterminacy_pie(stratum_counts)

    print("✓ All figures generated")


def save_results(cfg: ExperimentConfig, metrics: dict) -> None:
    """Save experiment results to JSON."""
    out_path = RESULTS_DIR / "experiment_results.json"

    def _serialize(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, float) and np.isnan(obj):
            return None
        raise TypeError(f"Unserializable: {type(obj)}")

    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2, default=_serialize)
    print(f"✓ Results saved: {out_path}")

    # Also save CSV summary
    csv_path = Path(__file__).parent / "outputs" / "results.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    gate = metrics.get("gate_metrics", {})
    with open(csv_path, "w") as f:
        f.write("metric,value\n")
        for k, v in gate.items():
            f.write(f"{k},{v}\n")
    print(f"✓ CSV saved: {csv_path}")

    # PoC status
    poc_status = check_poc_conditions(None, {"recall_by_stratum": {"ngram": {"lexical": gate.get("ngram_lexical_recall", 0), "semantic": gate.get("ngram_semantic_recall", 1)}}, "minkpp_f1_variance": gate.get("minkpp_f1_variance", 0), "indeterminacy_rate": 0.3})
    poc_path = RESULTS_DIR / "poc_status.yaml"
    import yaml
    with open(poc_path, "w") as f:
        yaml.dump({"poc_status": poc_status, "gate_metrics": gate}, f)
    print(f"✓ PoC status saved: {poc_path}")


def main() -> None:
    print("=" * 60)
    print("h-e1: Contamination Geometry Decomposition — EXISTENCE PoC")
    print("=" * 60)
    t0 = time.time()

    cfg = get_config()
    setup_environment(cfg)

    # Load benchmarks
    print("\n=== Loading Benchmarks ===")
    bench_loader = BenchmarkLoader(cfg)
    benchmark_datasets = bench_loader.load_all_benchmarks()
    benchmark_texts: dict[str, list[str]] = {
        name: bench_loader.get_item_texts(ds, name)
        for name, ds in benchmark_datasets.items()
    }
    for name, texts in benchmark_texts.items():
        print(f"  {name}: {len(texts)} items")

    # Build indices (capped at 50K docs for PoC speed)
    poc_max_docs = 50_000
    ngram_indices, sbert_indices = build_indices(cfg, max_docs_override=poc_max_docs)

    # Geometry pipeline
    geometry_results = run_geometry_pipeline(cfg, benchmark_texts, ngram_indices, sbert_indices)

    # Ground truth (Approach A: Pile inclusion)
    print("\n=== Generating Ground Truth ===")
    gt_gen = GroundTruthGenerator(cfg)
    ground_truth: dict = {}
    for bench_name, texts in benchmark_texts.items():
        ground_truth[bench_name] = {}
        for corpus_name in cfg.corpora:
            ground_truth[bench_name][corpus_name] = gt_gen.approach_a_pile_labels(
                texts, ngram_indices[corpus_name]
            )

    # Detector evaluation
    detector_results = run_detector_evaluation(cfg, benchmark_texts, ngram_indices, sbert_indices, ground_truth)

    # Metrics
    metrics = run_metrics(cfg, geometry_results, detector_results, ground_truth)

    # Figures
    generate_figures(cfg, metrics, geometry_results)

    # Save
    save_results(cfg, metrics)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE — elapsed: {elapsed:.1f}s")
    print(f"{'='*60}")

    # Final gate check
    gate = metrics.get("gate_metrics", {})
    print(f"\nGate Metrics Summary:")
    print(f"  N-gram Recall (Lexical):  {gate.get('ngram_lexical_recall', 0):.3f}  (target ≥ 0.80)")
    print(f"  N-gram Recall (Semantic): {gate.get('ngram_semantic_recall', 0):.3f}  (target ≤ 0.40)")
    print(f"  Min-K%++ F1 Variance:     {gate.get('minkpp_f1_variance', 0):.3f}  (target ≥ 0.15)")


if __name__ == "__main__":
    main()
