"""Tests for config.py — A-1."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    BENCHMARKS, NGRAM_SIZE, SAMPLE_SIZE, RANDOM_SEED,
    CORRECTED_ALPHA, N_WORKERS, PILE_HF_ID, PILE_DEDUP_HF_ID,
    BASE_DIR, FIGURES_DIR, CHECKPOINT_DIR,
    FigureConfig, StyleConfig, PipelineConfig, ResourceConfig, PIPELINE_STAGES
)


def test_benchmarks():
    assert BENCHMARKS == ["mmlu", "hellaswag", "arc_challenge", "winogrande"]


def test_ngram_size():
    assert NGRAM_SIZE == 13


def test_corrected_alpha():
    assert abs(CORRECTED_ALPHA - 0.0125) < 1e-9


def test_sample_size():
    assert SAMPLE_SIZE == 10_000


def test_corpus_ids():
    # Pile source may be monology/pile-uncopyrighted (parquet mirror) or EleutherAI/pile
    assert "pile" in PILE_HF_ID.lower()
    assert "EleutherAI" in PILE_DEDUP_HF_ID
    assert PILE_HF_ID != PILE_DEDUP_HF_ID


def test_paths():
    assert isinstance(BASE_DIR, Path)
    assert isinstance(FIGURES_DIR, Path)
    assert isinstance(CHECKPOINT_DIR, Path)


def test_pipeline_stages():
    expected = ["hash_diff", "sample", "ngrams", "overlaps", "stats", "ablations", "figures"]
    assert PIPELINE_STAGES == expected


def test_figure_config():
    fc = FigureConfig()
    assert fc.dpi == 150
    assert fc.color_removed == "#d62728"
    assert fc.color_retained == "#1f77b4"


def test_style_config():
    sc = StyleConfig()
    assert sc.seaborn_theme == "whitegrid"
    assert sc.mpl_backend == "Agg"
    assert "mmlu" in sc.axis_labels


def test_pipeline_config():
    pc = PipelineConfig()
    assert pc.resume is True
    assert "hash_diff" in pc.checkpoint_files


def test_resource_config():
    rc = ResourceConfig()
    assert rc.random_seed == RANDOM_SEED
    assert rc.n_workers >= 1
