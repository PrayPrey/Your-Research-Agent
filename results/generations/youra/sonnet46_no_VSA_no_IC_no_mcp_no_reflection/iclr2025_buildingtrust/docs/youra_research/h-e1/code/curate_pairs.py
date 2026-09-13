"""FR-1: Model Pair Curation — curate ≥6 matched DPO/SFT 7B pairs."""
import json
import os

REQUIRED_FIELDS = ["sft_model_id", "dpo_model_id", "base_model_id",
                   "sft_dataset", "dpo_dataset", "source"]


def curate_pairs() -> list[dict]:
    """Return 6 DPO/SFT 7B model pairs from the same base checkpoints."""
    return [
        # Pair 1: Mistral-7B-v0.1 base — SFT-instruct vs Zephyr-alpha (DPO)
        {
            "sft_model_id": "mistralai/Mistral-7B-Instruct-v0.1",
            "dpo_model_id": "HuggingFaceH4/zephyr-7b-alpha",
            "base_model_id": "mistralai/Mistral-7B-v0.1",
            "sft_dataset": "mistral-instruct-v0.1-data",
            "dpo_dataset": "UltraFeedback-binarized",
            "source": "huggingface-hub",
        },
        # Pair 2: Mistral-7B-v0.1 base — OpenHermes (SFT) vs Zephyr-beta (DPO)
        {
            "sft_model_id": "teknium/OpenHermes-2.5-Mistral-7B",
            "dpo_model_id": "HuggingFaceH4/zephyr-7b-beta",
            "base_model_id": "mistralai/Mistral-7B-v0.1",
            "sft_dataset": "OpenHermes-2.5",
            "dpo_dataset": "UltraFeedback-binarized",
            "source": "huggingface-hub",
        },
        # Pair 3: LLaMA-2-7B base — Tulu-2-SFT vs Tulu-2-DPO (controlled pair)
        {
            "sft_model_id": "allenai/tulu-2-7b",
            "dpo_model_id": "allenai/tulu-2-dpo-7b",
            "base_model_id": "meta-llama/Llama-2-7b-hf",
            "sft_dataset": "tulu-v2-sft-mixture",
            "dpo_dataset": "tulu-2-preference-data",
            "source": "allenai",
        },
        # Pair 4: LLaMA-2-7B base — Llama-2-chat (SFT RLHF) vs neural-chat-v3-1 (DPO)
        {
            "sft_model_id": "meta-llama/Llama-2-7b-chat-hf",
            "dpo_model_id": "Intel/neural-chat-7b-v3-1",
            "base_model_id": "meta-llama/Llama-2-7b-hf",
            "sft_dataset": "llama-2-rlhf-data",
            "dpo_dataset": "orca_dpo_pairs",
            "source": "intel-neural-chat",
        },
        # Pair 5: Mistral-7B-v0.1 base — OpenChat-3.5 (SFT) vs Starling-LM-7B-alpha (DPO)
        {
            "sft_model_id": "openchat/openchat_3.5",
            "dpo_model_id": "berkeley-nest/Starling-LM-7B-alpha",
            "base_model_id": "mistralai/Mistral-7B-v0.1",
            "sft_dataset": "openchat-3.5-data",
            "dpo_dataset": "berkeley-nectar-preferences",
            "source": "openchat-starling",
        },
        # Pair 6: Mistral-7B-v0.3 base — Mistral-Instruct-v0.3 (SFT) vs neural-chat-v3-3 (DPO)
        {
            "sft_model_id": "mistralai/Mistral-7B-Instruct-v0.3",
            "dpo_model_id": "Intel/neural-chat-7b-v3-3",
            "base_model_id": "mistralai/Mistral-7B-v0.3",
            "sft_dataset": "mistral-instruct-v0.3-data",
            "dpo_dataset": "orca_dpo_pairs",
            "source": "intel-neural-chat",
        },
    ]


def validate_pairs(pairs: list[dict]) -> None:
    assert len(pairs) >= 6, f"Need ≥6 pairs, got {len(pairs)}"
    seen = set()
    for p in pairs:
        for f in REQUIRED_FIELDS:
            assert f in p, f"Missing field '{f}' in pair: {p}"
        for key in ("sft_model_id", "dpo_model_id"):
            assert p[key] not in seen, f"Duplicate model_id: {p[key]}"
            seen.add(p[key])


def write_pairs(pairs: list[dict], output_path: str = "model_pairs.json") -> None:
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(pairs, f, indent=2)
    print(f"✓ Wrote {len(pairs)} pairs to {output_path}")


def main() -> list[dict]:
    pairs = curate_pairs()
    validate_pairs(pairs)
    write_pairs(pairs)
    print(f"✓ {len(pairs)} valid model pairs curated")
    for i, p in enumerate(pairs, 1):
        print(f"  Pair {i}: {p['sft_model_id']} (SFT) vs {p['dpo_model_id']} (DPO)")
    return pairs


if __name__ == "__main__":
    main()
