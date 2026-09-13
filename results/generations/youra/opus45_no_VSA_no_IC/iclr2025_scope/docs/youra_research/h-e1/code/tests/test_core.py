"""Core tests for LoRA scaling law experiment modules."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd


class TestConfig:
    def test_models_defined(self):
        from config import MODELS, MODEL_HF_IDS
        assert len(MODELS) == 4
        assert "pythia-1b" in MODELS
        assert "pythia-12b" in MODELS
        assert MODELS["pythia-1b"] == 1.0e9
        assert all(m in MODEL_HF_IDS for m in MODELS)

    def test_ranks_seeds(self):
        from config import RANKS, SEEDS
        assert RANKS == [4, 8, 16, 32, 64, 128]
        assert len(SEEDS) == 3

    def test_train_config(self):
        from config import TrainConfig
        cfg = TrainConfig()
        assert cfg.epochs == 3
        assert cfg.lr == 1e-4
        assert cfg.batch_size == 8
        assert cfg.grad_accum == 4
        assert cfg.gradient_checkpointing is True


class TestData:
    def test_load_squad_v2(self):
        from data import load_squad_v2
        ds = load_squad_v2()
        assert "train" in ds
        assert "validation" in ds
        assert len(ds["train"]) > 100000
        assert len(ds["validation"]) > 10000

    def test_tokenize_squad(self):
        from data import load_squad_v2, tokenize_squad
        from datasets import DatasetDict
        from transformers import AutoTokenizer

        ds = load_squad_v2()
        small_ds = DatasetDict({"train": ds["train"].select(range(10))})
        tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")
        tokenizer.pad_token = tokenizer.eos_token

        tokenized = tokenize_squad(small_ds, tokenizer, max_length=384)
        assert "input_ids" in tokenized["train"].features
        assert "start_positions" in tokenized["train"].features


class TestModel:
    def test_load_tokenizer(self):
        from model import load_tokenizer
        tokenizer = load_tokenizer("pythia-1b")
        assert tokenizer.pad_token is not None

    @pytest.mark.skipif(not os.environ.get("RUN_GPU_TESTS"), reason="Skip GPU tests")
    def test_load_base_model(self):
        from model import load_base_model
        model = load_base_model("pythia-1b")
        assert model is not None

    @pytest.mark.skipif(not os.environ.get("RUN_GPU_TESTS"), reason="Skip GPU tests")
    def test_apply_lora(self):
        from model import load_base_model, apply_lora
        model = load_base_model("pythia-1b")
        lora_model = apply_lora(model, rank=8)
        trainable = sum(p.numel() for p in lora_model.parameters() if p.requires_grad)
        assert trainable > 0
        assert trainable < sum(p.numel() for p in lora_model.parameters())


class TestAnalyze:
    def test_compute_r_opt(self, tmp_path):
        from analyze import compute_r_opt

        sweep_csv = tmp_path / "sweep.csv"
        df = pd.DataFrame([
            {"model": "pythia-1b", "rank": 4, "seed": 42, "f1_score": 0.5},
            {"model": "pythia-1b", "rank": 8, "seed": 42, "f1_score": 0.6},
            {"model": "pythia-1b", "rank": 16, "seed": 42, "f1_score": 0.55},
            {"model": "pythia-2.8b", "rank": 8, "seed": 42, "f1_score": 0.7},
            {"model": "pythia-2.8b", "rank": 16, "seed": 42, "f1_score": 0.75},
        ])
        df.to_csv(sweep_csv, index=False)

        result = compute_r_opt(str(sweep_csv), str(tmp_path / "optimal.csv"))
        assert len(result) == 2
        assert result[result["model"] == "pythia-1b"]["r_opt"].values[0] == 8
        assert result[result["model"] == "pythia-2.8b"]["r_opt"].values[0] == 16

    def test_fit_scaling_law(self, tmp_path):
        from analyze import fit_scaling_law

        optimal_df = pd.DataFrame([
            {"model": "pythia-1b", "N": 1e9, "r_opt": 8, "seed": 42},
            {"model": "pythia-2.8b", "N": 2.8e9, "r_opt": 12, "seed": 42},
            {"model": "pythia-6.9b", "N": 6.9e9, "r_opt": 18, "seed": 42},
            {"model": "pythia-12b", "N": 1.2e10, "r_opt": 24, "seed": 42},
        ])

        result = fit_scaling_law(optimal_df, n_bootstrap=100, output_json=str(tmp_path / "fit.json"))
        assert "alpha" in result
        assert "alpha_ci_low" in result
        assert "alpha_ci_high" in result
        assert "r2" in result
        assert 0 < result["alpha"] < 1

    def test_check_pass_fail(self):
        from analyze import check_pass_fail

        good_result = {"alpha": 0.5, "alpha_ci_low": 0.35, "alpha_ci_high": 0.65, "r2": 0.85}
        checks = check_pass_fail(good_result)
        assert checks["alpha_in_range"] is True
        assert checks["ci_excludes_zero"] is True
        assert checks["ci_excludes_one"] is True
        assert checks["overall_pass"] is True

        bad_result = {"alpha": 0.9, "alpha_ci_low": 0.8, "alpha_ci_high": 1.1, "r2": 0.5}
        checks = check_pass_fail(bad_result)
        assert checks["overall_pass"] is False
