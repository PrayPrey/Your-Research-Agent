"""Data loading for H-E1: load all corpora and construct Equal-mix."""
import random
import logging
from datasets import load_dataset

logger = logging.getLogger(__name__)

SOURCES = {
    "humaneval_train": ("openai/openai_humaneval", None, "test"),
    "mbpp_train": ("google-research-datasets/mbpp", "sanitized", "train"),
    "leetcode": ("newfacade/LeetCodeDataset", None, "train"),
    "humaneval_plus": ("evalplus/humanevalplus", None, "test"),
    "mbpp_plus": ("evalplus/mbppplus", None, "test"),
}

EQUAL_MIX_PER_SOURCE = 164


def extract_text(example: dict, source_name: str) -> str:
    """Concatenate prompt+solution string for one example."""
    if source_name in ("humaneval_train", "humaneval_plus"):
        prompt = example.get("prompt", "") or ""
        canonical = example.get("canonical_solution", "") or ""
        return (prompt + "\n" + canonical).strip()
    elif source_name in ("mbpp_train", "mbpp_plus"):
        text = example.get("text", "") or example.get("prompt", "") or ""
        code = example.get("code", "") or ""
        return (text + "\n" + code).strip()
    elif source_name == "leetcode":
        desc = example.get("question_title", "") or example.get("description", "") or ""
        solution = example.get("python_solution", "") or example.get("solution", "") or ""
        if not solution:
            for k, v in example.items():
                if "solution" in k.lower() or "code" in k.lower():
                    solution = str(v) or ""
                    break
        return (desc + "\n" + solution).strip()
    else:
        # Generic fallback
        parts = []
        for k in ("prompt", "text", "description", "question", "canonical_solution", "code", "solution"):
            if example.get(k):
                parts.append(str(example[k]))
        return "\n".join(parts).strip()


def load_all_corpora(seed: int = 42) -> dict:
    """Returns dict mapping corpus name -> list of raw text strings.
    Equal-mix: 164 from each of humaneval_train, mbpp_train (seed), leetcode (seed).
    """
    rng = random.Random(seed)
    corpora = {}

    for name, (dataset_id, config_name, split) in SOURCES.items():
        logger.info(f"Loading {name} from {dataset_id}...")
        try:
            ds = load_dataset(dataset_id, config_name, split=split, trust_remote_code=True)
        except Exception as e:
            logger.warning(f"Failed to load {name}: {e}")
            # Try without config
            try:
                ds = load_dataset(dataset_id, split=split, trust_remote_code=True)
            except Exception as e2:
                logger.error(f"Could not load {name}: {e2}")
                corpora[name] = []
                continue

        texts = [extract_text(ex, name) for ex in ds]
        texts = [t for t in texts if t.strip()]
        logger.info(f"Loaded {len(texts)} texts for {name}")
        corpora[name] = texts

    # Build Equal-mix: 164 from humaneval_train, mbpp_train, leetcode
    equal_mix = []
    for src in ("humaneval_train", "mbpp_train", "leetcode"):
        pool = corpora.get(src, [])
        n = min(EQUAL_MIX_PER_SOURCE, len(pool))
        sampled = rng.sample(pool, n)
        equal_mix.extend(sampled)

    corpora["equal_mix"] = equal_mix
    logger.info(f"Equal-mix constructed: {len(equal_mix)} texts total")
    return corpora
