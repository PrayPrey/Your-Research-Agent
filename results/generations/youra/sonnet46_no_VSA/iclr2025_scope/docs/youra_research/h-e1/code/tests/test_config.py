"""Tests for config.py: verify all required constants exist and are valid."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_required_constants():
    from config import (
        TEACHER_MODEL, C4_DATASET, LONGBENCH_DATASET,
        CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY,
        MOHAWK_STAGE_TOKENS, MOHAWK_LR, MOHAWK_BATCH, MOHAWK_SEQ_LEN, MOHAWK_SEED,
        LAWCAT_PHASE1_TOKENS, LAWCAT_LORA_R, LAWCAT_LORA_ALPHA,
        HYBRID4_KEPT_LAYERS, PPL_GATE_MAX_RELATIVE_GAP, L2_GATE_MAX_RATIO,
    )
    assert TEACHER_MODEL == "meta-llama/Llama-3.1-8B"
    assert len(CATEGORIES) == 6
    assert RETRIEVAL_HEAVY == {"multi_doc_qa", "long_structured_data"}
    assert GENERATION_HEAVY == {"long_in_context_learning"}
    assert MOHAWK_STAGE_TOKENS["stage1"] == 26_000_000
    assert MOHAWK_STAGE_TOKENS["stage2"] == 52_000_000
    assert MOHAWK_STAGE_TOKENS["stage3"] == 920_000_000
    assert MOHAWK_LR["stage1"] == 1e-3
    assert MOHAWK_BATCH["stage3"] == 32
    assert MOHAWK_SEQ_LEN == 2048
    assert MOHAWK_SEED == 42
    assert LAWCAT_PHASE1_TOKENS == 50_000_000
    assert LAWCAT_LORA_R == 16
    assert LAWCAT_LORA_ALPHA == 32
    assert HYBRID4_KEPT_LAYERS == [14, 15, 16, 17]
    assert 0 < PPL_GATE_MAX_RELATIVE_GAP < 1
    assert 0 < L2_GATE_MAX_RATIO < 1


def test_category_coverage():
    from config import CATEGORIES, RETRIEVAL_HEAVY, GENERATION_HEAVY
    for cat in RETRIEVAL_HEAVY:
        assert cat in CATEGORIES
    for cat in GENERATION_HEAVY:
        assert cat in CATEGORIES
    neutral = set(CATEGORIES) - RETRIEVAL_HEAVY - GENERATION_HEAVY
    assert len(neutral) >= 2, "Should have at least 2 neutral categories"


def test_token_budget_sum():
    from config import MOHAWK_STAGE_TOKENS
    total = sum(MOHAWK_STAGE_TOKENS.values())
    assert total <= 1_000_000_000, f"Total MOHAWK tokens {total} exceeds 1B budget"
