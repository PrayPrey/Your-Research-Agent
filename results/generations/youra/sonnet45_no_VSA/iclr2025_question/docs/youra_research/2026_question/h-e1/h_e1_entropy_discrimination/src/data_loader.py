"""HaluEval dataset loader and preprocessor for H-E1 experiment.

This module downloads, parses, and preprocesses the HaluEval QA dataset.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from tqdm import tqdm


class HaluEvalDataLoader:
    """Load and preprocess HaluEval QA dataset."""

    def __init__(self, cache_dir: str = "./data/halueval", seed: int = 42):
        """Initialize data loader.

        Parameters
        ----------
        cache_dir : str
            Directory to cache downloaded and processed data
        seed : int
            Random seed for reproducibility
        """
        self.cache_dir = Path(cache_dir)
        self.processed_dir = self.cache_dir / "processed"
        self.seed = seed
        random.seed(seed)

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_dataset(self) -> Path:
        """Download HaluEval QA dataset from GitHub.

        Returns
        -------
        Path
            Path to downloaded raw dataset file
        """
        raw_file = self.cache_dir / "qa_data.json"

        if raw_file.exists():
            print(f"Dataset already exists at {raw_file}")
            return raw_file

        # HaluEval QA dataset URL
        url = "https://raw.githubusercontent.com/RUCAIBox/HaluEval/main/data/qa_data.json"

        print(f"Downloading HaluEval QA dataset from {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"Downloaded dataset to {raw_file}")
        return raw_file

    def parse_dataset(self, raw_file: Path) -> List[Dict]:
        """Parse raw JSON dataset and validate schema.

        Parameters
        ----------
        raw_file : Path
            Path to raw dataset JSON file

        Returns
        -------
        List[Dict]
            List of validated samples
        """
        print(f"Parsing dataset from {raw_file}")

        with open(raw_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate and filter samples
        valid_samples = []
        skipped = 0

        for idx, sample in enumerate(tqdm(data, desc="Validating samples")):
            # Check required fields
            if not all(k in sample for k in ['question', 'answer', 'knowledge', 'hallucination_type']):
                skipped += 1
                continue

            # Create standardized sample
            processed = {
                'id': f"halueval_qa_{idx:05d}",
                'question': sample['question'],
                'gold_answer': sample.get('knowledge', ''),
                'model_answer': sample.get('answer', ''),
                'label': 1 if sample.get('hallucination_type', 'None') != 'None' else 0
            }

            valid_samples.append(processed)

        print(f"Parsed {len(valid_samples)} valid samples (skipped {skipped})")
        return valid_samples

    def split_dataset(
        self,
        samples: List[Dict],
        calibration_ratio: float = 0.1
    ) -> Tuple[List[Dict], List[Dict]]:
        """Split dataset into calibration and test sets.

        Parameters
        ----------
        samples : List[Dict]
            All dataset samples
        calibration_ratio : float
            Fraction of data for calibration set

        Returns
        -------
        Tuple[List[Dict], List[Dict]]
            (calibration_samples, test_samples)
        """
        # Shuffle with fixed seed
        shuffled = samples.copy()
        random.shuffle(shuffled)

        split_idx = int(len(shuffled) * calibration_ratio)
        calibration = shuffled[:split_idx]
        test = shuffled[split_idx:]

        print(f"Split: {len(calibration)} calibration, {len(test)} test samples")
        return calibration, test

    def compute_statistics(self, samples: List[Dict], split_name: str) -> Dict:
        """Compute dataset statistics.

        Parameters
        ----------
        samples : List[Dict]
            Dataset samples
        split_name : str
            Name of the split (e.g., 'calibration', 'test')

        Returns
        -------
        Dict
            Statistics dictionary
        """
        labels = [s['label'] for s in samples]
        n_total = len(labels)
        n_hallucinated = sum(labels)
        n_correct = n_total - n_hallucinated

        stats = {
            'split': split_name,
            'total_samples': n_total,
            'hallucinated': n_hallucinated,
            'correct': n_correct,
            'hallucination_rate': n_hallucinated / n_total if n_total > 0 else 0.0
        }

        print(f"{split_name} stats: {n_total} samples, "
              f"{n_hallucinated} hallucinated ({stats['hallucination_rate']:.2%})")

        return stats

    def save_split(self, samples: List[Dict], split_name: str) -> Path:
        """Save dataset split to JSONL file.

        Parameters
        ----------
        samples : List[Dict]
            Samples to save
        split_name : str
            Split name (used in filename)

        Returns
        -------
        Path
            Path to saved file
        """
        output_file = self.processed_dir / f"{split_name}.jsonl"

        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')

        print(f"Saved {len(samples)} samples to {output_file}")
        return output_file

    def prepare_dataset(self) -> Dict:
        """Execute full data preparation pipeline.

        Returns
        -------
        Dict
            Preparation summary with file paths and statistics
        """
        # Download
        raw_file = self.download_dataset()

        # Parse and validate
        samples = self.parse_dataset(raw_file)

        # Split
        calibration, test = self.split_dataset(samples)

        # Compute statistics
        cal_stats = self.compute_statistics(calibration, 'calibration')
        test_stats = self.compute_statistics(test, 'test')

        # Save splits
        cal_file = self.save_split(calibration, 'calibration')
        test_file = self.save_split(test, 'test')

        # Save combined statistics
        stats = {
            'calibration': cal_stats,
            'test': test_stats,
            'seed': self.seed,
            'calibration_ratio': 0.1
        }

        stats_file = self.processed_dir / 'dataset_stats.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"Saved statistics to {stats_file}")

        return {
            'calibration_file': str(cal_file),
            'test_file': str(test_file),
            'stats_file': str(stats_file),
            'statistics': stats
        }


def load_jsonl(file_path: str) -> List[Dict]:
    """Load samples from JSONL file.

    Parameters
    ----------
    file_path : str
        Path to JSONL file

    Returns
    -------
    List[Dict]
        Loaded samples
    """
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            samples.append(json.loads(line.strip()))
    return samples
