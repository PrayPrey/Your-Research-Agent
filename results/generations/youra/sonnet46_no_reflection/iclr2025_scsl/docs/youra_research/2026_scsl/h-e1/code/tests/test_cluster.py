"""Tests for clustering probe."""
import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_cluster_import():
    import cluster
    assert cluster is not None


def test_run_kmeans():
    from cluster import run_kmeans
    embeddings = np.random.randn(100, 2048).astype(np.float32)
    assignments = run_kmeans(embeddings, k=2, n_init=3, seed=42)
    assert assignments.shape == (100,)
    assert set(np.unique(assignments)).issubset({0, 1})


def test_worst_cluster_purity():
    from cluster import worst_cluster_purity
    group_ids = np.array([0, 0, 0, 1, 1, 1])
    assignments = np.array([0, 0, 0, 1, 1, 1])
    purity = worst_cluster_purity(group_ids, assignments, k=2)
    assert purity == pytest.approx(1.0)


def test_run_kmeans_probe():
    from cluster import run_kmeans_probe
    # Separable data
    emb = np.vstack([np.random.randn(200, 10) + 5,
                     np.random.randn(200, 10) - 5])
    emb = np.pad(emb, ((0,0),(0,2038)))  # pad to 2048
    group_ids = np.array([0]*200 + [1]*200)
    ami, wp, assignments = run_kmeans_probe(emb, group_ids, k=2)
    assert 0.0 <= ami <= 1.0
    assert 0.0 <= wp <= 1.0


def test_compute_random_baseline():
    from cluster import compute_random_baseline
    group_ids = np.array([0]*100 + [1]*100 + [2]*100 + [3]*100)
    ami_r, pur_r = compute_random_baseline(group_ids, k=2, seed=0)
    assert abs(ami_r) < 0.2  # random should be near 0


def test_verify_mechanism_activated():
    from cluster import verify_mechanism_activated
    # Perfectly separable
    emb = np.vstack([np.random.randn(200, 2048) + 10,
                     np.random.randn(200, 2048) - 10]).astype(np.float32)
    assignments = np.array([0]*200 + [1]*200, dtype=np.int32)
    group_ids = np.array([0]*200 + [1]*200)
    ok, indicators = verify_mechanism_activated(emb, assignments, group_ids, k=2)
    assert indicators['embedding_shape_correct'] is True
    assert indicators['clusters_non_trivial'] is True


def test_probe(tmp_path):
    from cluster import probe
    emb = np.random.randn(100, 2048).astype(np.float32)
    grp = np.random.randint(0, 4, 100)
    emb_path = str(tmp_path / 'emb.npy')
    grp_path = str(tmp_path / 'grp.npy')
    np.save(emb_path, emb)
    np.save(grp_path, grp)
    result = probe(emb_path, grp_path, k=2)
    assert 'ami' in result
    assert 'worst_purity' in result
    assert 'mechanism_ok' in result
