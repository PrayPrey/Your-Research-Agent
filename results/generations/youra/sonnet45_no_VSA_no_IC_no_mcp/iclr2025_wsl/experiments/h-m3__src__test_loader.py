"""Generate 30-hypothesis test set with ground truth labels."""

from typing import Dict, List


class TestLoader:
    """Generate labeled confound test set."""

    def __init__(self):
        pass

    def generate_test_set(self) -> List[Dict[str, str]]:
        """Generate 30 labeled hypotheses. Returns: [{text, label, domain}, ...]."""
        test_set = []

        # Confounded hypotheses (15 total: 5 NLP, 5 vision, 5 training)
        confounded_nlp = [
            "BPE tokenizer with 50k vocab vs 10k vocab on BLEU score",
            "Sequence length 128 vs 512 tokens affects accuracy",
            "Vocabulary size 30k vs 10k impacts perplexity",
            "Subword tokenization changes affect F1 score",
            "Max length 256 with truncation impacts score",
        ]

        confounded_vision = [
            "224px resolution ResNet18 vs 448px ResNet50",
            "Heavy augmentation with larger model capacity",
            "Image size 128 vs 256 with depth increase",
            "16-bit color depth with bigger network size",
            "Crop size variation coupled with model complexity",
        ]

        confounded_training = [
            "Batch size 256 with LR 0.1 vs batch 64 with LR 0.025",
            "Switch optimizer and adjust weight decay together",
            "Train 100 epochs on small dataset size vs 10 epochs on large dataset size",
            "Batch 128 with LR 0.05 vs batch 32 with LR 0.0125",
            "Momentum 0.9 with step learning rate schedule vs momentum 0.95 with cosine schedule",
        ]

        # Unconfounded hypotheses (15 total: 5 NLP, 5 vision, 5 training)
        unconfounded_nlp = [
            "Increase dropout from 0.1 to 0.5 holding architecture constant",
            "Replace ReLU with GELU activation (no other changes)",
            "Add layer normalization to existing architecture",
            "Test greedy vs beam search decoding (same model)",
            "Compare pre-training datasets (same architecture)",
        ]

        unconfounded_vision = [
            "Test random crop vs center crop (same model)",
            "Compare Adam vs SGD optimizer (fixed architecture)",
            "Add batch normalization layers only",
            "Test data augmentation strength (same resolution and model)",
            "Compare pooling strategies (same network)",
        ]

        unconfounded_training = [
            "Increase epochs from 10 to 50 (all else fixed)",
            "Test cosine vs step LR schedule (same optimizer and batch)",
            "Add gradient clipping (no other changes)",
            "Compare weight initialization schemes (same hyperparams)",
            "Test label smoothing strength (all else constant)",
        ]

        # Build test set
        for text in confounded_nlp:
            test_set.append({"text": text, "label": "confounded", "domain": "nlp"})

        for text in confounded_vision:
            test_set.append({"text": text, "label": "confounded", "domain": "vision"})

        for text in confounded_training:
            test_set.append(
                {"text": text, "label": "confounded", "domain": "training"}
            )

        for text in unconfounded_nlp:
            test_set.append({"text": text, "label": "unconfounded", "domain": "nlp"})

        for text in unconfounded_vision:
            test_set.append(
                {"text": text, "label": "unconfounded", "domain": "vision"}
            )

        for text in unconfounded_training:
            test_set.append(
                {"text": text, "label": "unconfounded", "domain": "training"}
            )

        return test_set
