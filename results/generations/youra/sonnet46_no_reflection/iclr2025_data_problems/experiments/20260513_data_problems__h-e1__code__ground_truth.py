from __future__ import annotations
import numpy as np
from config import ExperimentConfig


class GroundTruthGenerator:
    """Generate binary contamination labels via Approach A (known inclusion) or B (simulated injection)."""

    def __init__(self, cfg: ExperimentConfig):
        self.contamination_rate: float = cfg.contamination_rate
        self.seed: int = cfg.seed

    def approach_a_pile_labels(
        self,
        benchmark_texts: list[str],
        ngram_index,
    ) -> np.ndarray:
        """Known-inclusion audit: items in The Pile index = contaminated.
        Returns shape (N,) int64 binary labels."""
        labels = np.array(
            [int(ngram_index.is_contaminated(t)) for t in benchmark_texts],
            dtype=np.int64,
        )
        return labels

    def approach_b_uniform(
        self,
        benchmark_texts: list[str],
        corpus_name: str,
    ) -> tuple[list[str], np.ndarray]:
        """Uniformly inject contamination_rate fraction into corpus.
        Returns (augmented_corpus, labels shape (N,) int64)."""
        rng = np.random.default_rng(self.seed)
        N = len(benchmark_texts)
        n_inject = max(1, int(N * self.contamination_rate))
        inject_idx = rng.choice(N, size=n_inject, replace=False)
        labels = np.zeros(N, dtype=np.int64)
        labels[inject_idx] = 1
        injected = [benchmark_texts[i] for i in inject_idx]
        # Build small synthetic corpus (real corpus not loaded here; injected items form augment)
        augmented = list(benchmark_texts) + injected
        return augmented, labels

    def approach_b_clustered(
        self,
        benchmark_texts: list[str],
        corpus_name: str,
    ) -> tuple[list[str], np.ndarray]:
        """Inject topic-clustered groups (grouped by first 50 chars).
        Returns (augmented_corpus, labels shape (N,) int64)."""
        rng = np.random.default_rng(self.seed + 1)
        N = len(benchmark_texts)
        # Group by topic proxy
        groups: dict[str, list[int]] = {}
        for i, t in enumerate(benchmark_texts):
            key = t[:50]
            groups.setdefault(key, []).append(i)
        n_inject = max(1, int(N * self.contamination_rate))
        labels = np.zeros(N, dtype=np.int64)
        injected: list[str] = []
        count = 0
        for idxs in groups.values():
            for i in idxs:
                if count >= n_inject:
                    break
                labels[i] = 1
                injected.append(benchmark_texts[i])
                count += 1
            if count >= n_inject:
                break
        augmented = list(benchmark_texts) + injected
        return augmented, labels

    def approach_b_paraphrased(
        self,
        benchmark_texts: list[str],
        corpus_name: str,
    ) -> tuple[list[str], np.ndarray]:
        """Paraphrase injected items before injection (simplified: reverse text as proxy).
        Returns (augmented_corpus, labels shape (N,) int64)."""
        rng = np.random.default_rng(self.seed + 2)
        N = len(benchmark_texts)
        n_inject = max(1, int(N * self.contamination_rate))
        inject_idx = rng.choice(N, size=n_inject, replace=False)
        labels = np.zeros(N, dtype=np.int64)
        labels[inject_idx] = 1
        # Simple paraphrase: word shuffle as proxy (llm-decontaminator not available offline)
        paraphrased = []
        for i in inject_idx:
            words = benchmark_texts[i].split()
            rng.shuffle(words)
            paraphrased.append(" ".join(words))
        augmented = list(benchmark_texts) + paraphrased
        return augmented, labels
