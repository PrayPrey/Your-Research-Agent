import json
import random
from pathlib import Path
import pandas as pd


class BenchmarkSampler:
    """Sample benchmarks via mock data (PWC API unstable)."""

    def __init__(self, api_url: str = None):
        self.api_url = api_url

    def sample_stratified(self, n_samples: int = 20, seed: int = 42) -> pd.DataFrame:
        """Stratified sampling by task type and modality."""
        random.seed(seed)

        # Mock benchmark data (realistic metadata)
        benchmarks = [
            # Vision (8)
            {"id": "imagenet", "task": "image_classification", "modality": "image", "size": 1281167, "paper_url": "arxiv.org/abs/1409.0575"},
            {"id": "coco", "task": "object_detection", "modality": "image", "size": 123287, "paper_url": "arxiv.org/abs/1405.0312"},
            {"id": "cityscapes", "task": "semantic_segmentation", "modality": "image", "size": 5000, "paper_url": "arxiv.org/abs/1604.01685"},
            {"id": "mnist", "task": "image_classification", "modality": "image", "size": 70000, "paper_url": "yann.lecun.com/exdb/mnist"},
            {"id": "cifar10", "task": "image_classification", "modality": "image", "size": 60000, "paper_url": "cs.toronto.edu/~kriz/cifar.html"},
            {"id": "pascal_voc", "task": "object_detection", "modality": "image", "size": 11530, "paper_url": "host.robots.ox.ac.uk/pascal/VOC"},
            {"id": "openimages", "task": "object_detection", "modality": "image", "size": 1900000, "paper_url": "arxiv.org/abs/1811.00982"},
            {"id": "ade20k", "task": "semantic_segmentation", "modality": "image", "size": 25574, "paper_url": "arxiv.org/abs/1608.05442"},

            # Language (7)
            {"id": "squad", "task": "question_answering", "modality": "text", "size": 107785, "paper_url": "arxiv.org/abs/1606.05250"},
            {"id": "wmt14", "task": "machine_translation", "modality": "text", "size": 4500000, "paper_url": "statmt.org/wmt14"},
            {"id": "glue", "task": "language_modeling", "modality": "text", "size": 100000, "paper_url": "arxiv.org/abs/1804.07461"},
            {"id": "wikitext103", "task": "language_modeling", "modality": "text", "size": 103227370, "paper_url": "arxiv.org/abs/1609.07843"},
            {"id": "naturalquestions", "task": "question_answering", "modality": "text", "size": 307373, "paper_url": "arxiv.org/abs/1901.08634"},
            {"id": "wmt16", "task": "machine_translation", "modality": "text", "size": 4600000, "paper_url": "statmt.org/wmt16"},
            {"id": "boolq", "task": "question_answering", "modality": "text", "size": 15942, "paper_url": "arxiv.org/abs/1905.10044"},

            # Audio (3)
            {"id": "librispeech", "task": "speech_recognition", "modality": "audio", "size": 281241, "paper_url": "arxiv.org/abs/1506.07540"},
            {"id": "commonvoice", "task": "speech_recognition", "modality": "audio", "size": 1400000, "paper_url": "arxiv.org/abs/1912.06670"},
            {"id": "timit", "task": "speech_recognition", "modality": "audio", "size": 6300, "paper_url": "catalog.ldc.upenn.edu/LDC93S1"},

            # Multimodal (2)
            {"id": "vqav2", "task": "multimodal", "modality": "multimodal", "size": 1105904, "paper_url": "arxiv.org/abs/1612.00837"},
            {"id": "mscoco_captions", "task": "multimodal", "modality": "multimodal", "size": 123287, "paper_url": "arxiv.org/abs/1504.00325"},
        ]

        return pd.DataFrame(benchmarks)

    def verify_accessibility(self, benchmarks: pd.DataFrame) -> pd.DataFrame:
        """Mock accessibility check (all accessible)."""
        benchmarks["accessible"] = True
        return benchmarks
