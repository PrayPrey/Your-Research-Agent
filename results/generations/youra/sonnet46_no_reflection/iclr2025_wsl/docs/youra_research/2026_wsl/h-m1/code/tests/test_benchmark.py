"""Tests for benchmark.py: timing benchmark and CheckpointResult."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import pytest
from benchmark import CheckpointResult, _time_vanilla, _time_orbit, run_timing_benchmark
from orbit_pe_computer import OrbitPEComputer
from sequential_pe_baseline import SequentialPEBaseline
from config import BenchmarkConfig


def make_state_dict(n_layers=2):
    return {f"layer{i}.weight": torch.randn(32, 16) for i in range(n_layers)}


def test_checkpoint_result_fields():
    r = CheckpointResult(
        checkpoint_id="test",
        arch_family="cnn",
        t_vanilla=0.01,
        t_orbit=0.012,
        overhead_ratio=1.2,
        success=True,
        layer_types_seen=["Linear"],
    )
    assert r.overhead_ratio == 1.2
    assert r.success is True
    assert r.error is None


def test_time_vanilla_returns_float():
    baseline = SequentialPEBaseline(token_dim=64)
    sd = make_state_dict()
    t = _time_vanilla(sd, baseline)
    assert isinstance(t, float)
    assert t >= 0.0


def test_time_orbit_returns_tuple():
    model = OrbitPEComputer(token_dim=64)
    sd = make_state_dict()
    elapsed, success, layer_types = _time_orbit(sd, model)
    assert isinstance(elapsed, float)
    assert isinstance(success, bool)
    assert isinstance(layer_types, list)


def test_run_timing_benchmark_count():
    """run_timing_benchmark should return n_cnn + n_transformer results."""
    orbit = OrbitPEComputer(token_dim=64)
    baseline = SequentialPEBaseline(token_dim=64)
    cfg = BenchmarkConfig()

    cnn_ckpts = [{"checkpoint_id": f"cnn_{i}", "state_dict": make_state_dict()} for i in range(5)]
    tf_ckpts = [{"checkpoint_id": f"tf_{i}", "state_dict": make_state_dict()} for i in range(3)]

    results = run_timing_benchmark(cnn_ckpts, tf_ckpts, orbit, baseline, cfg)
    assert len(results) == 8


def test_overhead_ratio_computed():
    orbit = OrbitPEComputer(token_dim=64)
    baseline = SequentialPEBaseline(token_dim=64)
    cfg = BenchmarkConfig()

    cnn_ckpts = [{"checkpoint_id": "c0", "state_dict": make_state_dict()}]
    results = run_timing_benchmark(cnn_ckpts, [], orbit, baseline, cfg)
    assert len(results) == 1
    assert results[0].overhead_ratio >= 0.0
    assert results[0].arch_family == "cnn"
