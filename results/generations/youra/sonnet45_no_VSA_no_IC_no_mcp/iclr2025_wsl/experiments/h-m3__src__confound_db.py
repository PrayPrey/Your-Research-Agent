"""Confound pattern database from literature sources."""

from typing import Dict, List


class ConfoundDatabase:
    """Literature-sourced confound patterns across DL domains."""

    def __init__(self):
        self.patterns = self._init_patterns()

    def _init_patterns(self) -> Dict[str, List[Dict]]:
        """Load 15 confound patterns (3 domains × 5 patterns)."""
        return {
            "nlp": [
                {
                    "keywords": ["tokenizer", "vocab", "BLEU"],
                    "description": "tokenizer-BLEU confound",
                },
                {
                    "keywords": ["sequence length", "accuracy"],
                    "description": "length-metric confound",
                },
                {
                    "keywords": ["vocabulary size", "perplexity"],
                    "description": "vocab-perplexity confound",
                },
                {
                    "keywords": ["subword", "tokenization", "F1"],
                    "description": "tokenization-F1 confound",
                },
                {
                    "keywords": ["max length", "truncation", "score"],
                    "description": "truncation-score confound",
                },
            ],
            "vision": [
                {
                    "keywords": ["resolution", "architecture"],
                    "description": "resolution-architecture confound",
                },
                {
                    "keywords": ["augmentation", "model capacity"],
                    "description": "augmentation-capacity confound",
                },
                {
                    "keywords": ["image size", "depth"],
                    "description": "size-depth confound",
                },
                {
                    "keywords": ["color depth", "network size"],
                    "description": "color-network confound",
                },
                {
                    "keywords": ["crop size", "model complexity"],
                    "description": "crop-complexity confound",
                },
            ],
            "training": [
                {
                    "keywords": ["batch size", "learning rate"],
                    "description": "batch-LR confound",
                },
                {
                    "keywords": ["optimizer", "weight decay"],
                    "description": "optimizer-regularization confound",
                },
                {
                    "keywords": ["epochs", "dataset size"],
                    "description": "epochs-data confound",
                },
                {
                    "keywords": ["batch", "LR"],
                    "description": "batch-LR confound (abbrev)",
                },
                {
                    "keywords": ["momentum", "learning rate schedule"],
                    "description": "momentum-schedule confound",
                },
            ],
        }

    def load_patterns(self) -> Dict[str, List[Dict]]:
        """Returns: {domain: [patterns]}."""
        return self.patterns

    def get_all_patterns(self) -> List[Dict]:
        """Flatten all patterns. Returns: [{domain, keywords, description}, ...]."""
        all_patterns = []
        for domain, patterns in self.patterns.items():
            for pattern in patterns:
                all_patterns.append(
                    {
                        "domain": domain,
                        "keywords": pattern["keywords"],
                        "description": pattern["description"],
                    }
                )
        return all_patterns
