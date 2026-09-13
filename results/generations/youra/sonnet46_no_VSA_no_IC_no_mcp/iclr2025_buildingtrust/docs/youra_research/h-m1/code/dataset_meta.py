"""HuggingFace dataset metadata loading for H-M1."""
import logging
from datasets import load_dataset

logger = logging.getLogger(__name__)


def load_adv_mnli_meta():
    """load_dataset('adv_glue', 'adv_mnli', split='validation')"""
    ds = load_dataset("adv_glue", "adv_mnli", split="validation", trust_remote_code=True)
    logger.info("Loaded adv_glue/adv_mnli: n=%d", len(ds))
    return ds


def load_anli_meta(round_id: int):
    """load_dataset('anli', split=f'test_r{round_id}')"""
    if round_id not in (1, 2, 3):
        raise ValueError(f"round_id must be 1, 2, or 3; got {round_id}")
    ds = load_dataset("anli", split=f"test_r{round_id}", trust_remote_code=True)
    logger.info("Loaded anli test_r%d: n=%d", round_id, len(ds))
    return ds


def load_glue_mnli_meta(seed: int = 1, n: int = 2000):
    """load_dataset('glue', 'mnli', split='validation_matched'), subsample n."""
    ds = load_dataset("glue", "mnli", split="validation_matched", trust_remote_code=True)
    if len(ds) > n:
        ds = ds.shuffle(seed=seed).select(range(n))
    logger.info("Loaded glue/mnli validation_matched (subsampled): n=%d", len(ds))
    return ds
