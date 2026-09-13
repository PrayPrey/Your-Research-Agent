"""
Data processing utilities for loading and preparing datasets
"""
import json
import random
from typing import List, Dict, Tuple
from datasets import load_dataset
import numpy as np


class DataProcessor:
    """Process and prepare datasets for confidence calibration experiments"""

    def __init__(self, config: Dict):
        self.config = config
        self.random_seed = config.get('random_seed', 42)
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)

    def load_trivia_qa(self, max_samples: int = 100) -> List[Dict]:
        """Load TriviaQA dataset"""
        print("Loading TriviaQA dataset...")
        try:
            dataset = load_dataset('trivia_qa', 'rc.nocontext', split='validation', trust_remote_code=True)

            samples = []
            for idx, item in enumerate(dataset):
                if len(samples) >= max_samples:
                    break

                # Extract question and answer
                question = item['question']
                # Get the first answer as ground truth
                answer = item['answer']['value'] if isinstance(item['answer'], dict) else item['answer']['aliases'][0]

                samples.append({
                    'id': f'trivia_qa_{idx}',
                    'question': question,
                    'answer': answer,
                    'dataset': 'trivia_qa',
                    'aliases': item['answer'].get('aliases', [answer]) if isinstance(item['answer'], dict) else [answer]
                })

            print(f"Loaded {len(samples)} samples from TriviaQA")
            return samples
        except Exception as e:
            print(f"Error loading TriviaQA: {e}")
            # Create synthetic fallback data
            return self._create_synthetic_trivia_qa(max_samples)

    def load_commonsense_qa(self, max_samples: int = 100) -> List[Dict]:
        """Load CommonsenseQA dataset"""
        print("Loading CommonsenseQA dataset...")
        try:
            dataset = load_dataset('commonsense_qa', split='validation', trust_remote_code=True)

            samples = []
            for idx, item in enumerate(dataset):
                if len(samples) >= max_samples:
                    break

                # Format question with choices
                question = item['question']
                choices = item['choices']['text']
                labels = item['choices']['label']
                answer_key = item['answerKey']

                # Find the correct answer
                answer_idx = labels.index(answer_key)
                answer = choices[answer_idx]

                # Format question with choices
                formatted_question = f"{question}\n"
                for label, choice in zip(labels, choices):
                    formatted_question += f"{label}. {choice}\n"

                samples.append({
                    'id': f'commonsense_qa_{idx}',
                    'question': formatted_question,
                    'answer': answer,
                    'answer_key': answer_key,
                    'dataset': 'commonsense_qa',
                    'choices': choices,
                })

            print(f"Loaded {len(samples)} samples from CommonsenseQA")
            return samples
        except Exception as e:
            print(f"Error loading CommonsenseQA: {e}")
            return self._create_synthetic_commonsense_qa(max_samples)

    def _create_synthetic_trivia_qa(self, n_samples: int = 100) -> List[Dict]:
        """Create synthetic TriviaQA-like data as fallback"""
        print("Creating synthetic TriviaQA data...")
        synthetic_data = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "Who wrote Romeo and Juliet?", "answer": "William Shakespeare"},
            {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
            {"question": "In which year did World War II end?", "answer": "1945"},
            {"question": "What is the speed of light?", "answer": "299,792,458 meters per second"},
            {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
            {"question": "What is the chemical symbol for gold?", "answer": "Au"},
            {"question": "How many continents are there?", "answer": "Seven"},
            {"question": "What is the smallest prime number?", "answer": "2"},
            {"question": "Who invented the telephone?", "answer": "Alexander Graham Bell"},
        ]

        samples = []
        for idx in range(min(n_samples, len(synthetic_data) * 10)):
            base_item = synthetic_data[idx % len(synthetic_data)]
            samples.append({
                'id': f'synthetic_trivia_{idx}',
                'question': base_item['question'],
                'answer': base_item['answer'],
                'dataset': 'trivia_qa',
                'aliases': [base_item['answer']]
            })

        return samples[:n_samples]

    def _create_synthetic_commonsense_qa(self, n_samples: int = 100) -> List[Dict]:
        """Create synthetic CommonsenseQA-like data as fallback"""
        print("Creating synthetic CommonsenseQA data...")
        synthetic_data = [
            {
                "question": "Where would you find a jellyfish?",
                "choices": ["desert", "ocean", "mountain", "forest", "city"],
                "answer": "ocean",
                "answer_key": "B"
            },
            {
                "question": "What do you use to write?",
                "choices": ["hammer", "pen", "saw", "screwdriver", "wrench"],
                "answer": "pen",
                "answer_key": "B"
            },
            {
                "question": "Where do you sleep?",
                "choices": ["kitchen", "bed", "office", "street", "store"],
                "answer": "bed",
                "answer_key": "B"
            },
        ]

        samples = []
        for idx in range(min(n_samples, len(synthetic_data) * 35)):
            base_item = synthetic_data[idx % len(synthetic_data)]

            formatted_question = f"{base_item['question']}\n"
            labels = ['A', 'B', 'C', 'D', 'E']
            for label, choice in zip(labels, base_item['choices']):
                formatted_question += f"{label}. {choice}\n"

            samples.append({
                'id': f'synthetic_commonsense_{idx}',
                'question': formatted_question,
                'answer': base_item['answer'],
                'answer_key': base_item['answer_key'],
                'dataset': 'commonsense_qa',
                'choices': base_item['choices'],
            })

        return samples[:n_samples]

    def load_all_datasets(self) -> List[Dict]:
        """Load all configured datasets"""
        all_samples = []
        max_samples = self.config.get('max_samples_per_dataset', 100)

        # Load TriviaQA
        trivia_samples = self.load_trivia_qa(max_samples)
        all_samples.extend(trivia_samples)

        # Load CommonsenseQA
        commonsense_samples = self.load_commonsense_qa(max_samples)
        all_samples.extend(commonsense_samples)

        # Shuffle all samples
        random.shuffle(all_samples)

        print(f"\nTotal samples loaded: {len(all_samples)}")
        return all_samples

    def split_data(self, samples: List[Dict],
                   train_ratio: float = 0.7,
                   val_ratio: float = 0.15,
                   test_ratio: float = 0.15) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Split data into train/val/test sets"""
        n_samples = len(samples)
        n_train = int(n_samples * train_ratio)
        n_val = int(n_samples * val_ratio)

        train_samples = samples[:n_train]
        val_samples = samples[n_train:n_train + n_val]
        test_samples = samples[n_train + n_val:]

        print(f"\nData split:")
        print(f"  Train: {len(train_samples)} samples")
        print(f"  Val: {len(val_samples)} samples")
        print(f"  Test: {len(test_samples)} samples")

        return train_samples, val_samples, test_samples

    def save_data(self, samples: List[Dict], filename: str):
        """Save samples to JSON file"""
        with open(filename, 'w') as f:
            json.dump(samples, f, indent=2)
        print(f"Saved data to {filename}")

    def load_data(self, filename: str) -> List[Dict]:
        """Load samples from JSON file"""
        with open(filename, 'r') as f:
            samples = json.load(f)
        print(f"Loaded {len(samples)} samples from {filename}")
        return samples
