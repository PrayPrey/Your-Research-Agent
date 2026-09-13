"""Dataset preparation for SED experiments."""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import torch
from torch.utils.data import Dataset, DataLoader
from datasets import load_dataset


@dataclass
class UncertaintyDataPoint:
    """Single data point with uncertainty labels."""
    question: str
    answer: Optional[str]
    uncertainty_type: str  # 'epistemic', 'aleatoric', 'low'
    is_hallucination: bool = False
    ambiguity_score: float = 0.0


class HallucinationDataset(Dataset):
    """Dataset for hallucination detection with uncertainty types."""

    def __init__(self, data_points: List[UncertaintyDataPoint], tokenizer):
        self.data_points = data_points
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data_points)

    def __getitem__(self, idx):
        dp = self.data_points[idx]
        return {
            "question": dp.question,
            "answer": dp.answer if dp.answer is not None else "",  # Handle None answers
            "uncertainty_type": dp.uncertainty_type,
            "is_hallucination": dp.is_hallucination,
            "ambiguity_score": dp.ambiguity_score,
        }


def load_truthfulqa_subset(num_samples: int = 200, seed: int = 42) -> List[UncertaintyDataPoint]:
    """Load TruthfulQA for hallucination-prone queries (epistemic uncertainty)."""
    random.seed(seed)

    try:
        dataset = load_dataset("truthfulqa/truthful_qa", "generation", split="validation")
    except Exception:
        dataset = load_dataset("truthful_qa", "generation", split="validation")

    data_points = []
    indices = random.sample(range(len(dataset)), min(num_samples, len(dataset)))

    for idx in indices:
        item = dataset[idx]
        # TruthfulQA contains questions that often cause hallucinations
        data_points.append(UncertaintyDataPoint(
            question=item["question"],
            answer=item["best_answer"] if "best_answer" in item else item.get("correct_answers", [""])[0],
            uncertainty_type="epistemic",  # These test model knowledge gaps
            is_hallucination=True,  # Most TruthfulQA answers from models are hallucinated
            ambiguity_score=0.2,  # Generally factual questions, low ambiguity
        ))

    return data_points


def load_natural_questions_subset(num_samples: int = 200, seed: int = 42) -> List[UncertaintyDataPoint]:
    """Load Natural Questions for low uncertainty factual questions."""
    random.seed(seed)

    dataset = load_dataset("google-research-datasets/natural_questions", "default",
                           split="validation", streaming=True)

    data_points = []
    count = 0

    for item in dataset:
        if count >= num_samples:
            break

        # Get short answer if available
        annotations = item.get("annotations", {})
        if isinstance(annotations, dict):
            short_answers = annotations.get("short_answers", [])
        else:
            short_answers = []

        # Skip if no clear answer
        if not short_answers or not item.get("question", {}).get("text"):
            continue

        question_text = item["question"]["text"]
        answer_text = short_answers[0].get("text", "") if short_answers and isinstance(short_answers[0], dict) else str(short_answers[0]) if short_answers else ""

        if question_text and answer_text:
            data_points.append(UncertaintyDataPoint(
                question=question_text,
                answer=answer_text,
                uncertainty_type="low",  # Well-established facts
                is_hallucination=False,
                ambiguity_score=0.1,
            ))
            count += 1

    return data_points


def create_ambiguous_questions(num_samples: int = 200, seed: int = 42) -> List[UncertaintyDataPoint]:
    """Create ambiguous questions for aleatoric uncertainty testing."""
    random.seed(seed)

    ambiguous_templates = [
        ("What is the best {topic}?", 0.9),
        ("Which is better, {opt1} or {opt2}?", 0.8),
        ("What should I {action}?", 0.85),
        ("How should I {action}?", 0.7),
        ("What do you think about {topic}?", 0.95),
        ("Is {topic} good or bad?", 0.75),
        ("What is the meaning of {concept}?", 0.6),
    ]

    topics = ["programming language", "framework", "database", "operating system", "editor",
              "cloud provider", "machine learning model", "approach", "methodology", "strategy"]
    options_pairs = [("Python", "JavaScript"), ("React", "Vue"), ("MySQL", "PostgreSQL"),
                     ("Linux", "Windows"), ("REST", "GraphQL"), ("Docker", "Kubernetes")]
    actions = ["learn first", "prioritize", "focus on", "start with", "choose", "approach this problem"]
    concepts = ["success", "happiness", "life", "intelligence", "creativity", "meaning"]

    data_points = []
    for _ in range(num_samples):
        template, ambiguity = random.choice(ambiguous_templates)
        if "{topic}" in template:
            question = template.format(topic=random.choice(topics))
        elif "{opt1}" in template:
            opt1, opt2 = random.choice(options_pairs)
            question = template.format(opt1=opt1, opt2=opt2)
        elif "{action}" in template:
            question = template.format(action=random.choice(actions))
        elif "{concept}" in template:
            question = template.format(concept=random.choice(concepts))
        else:
            question = template

        data_points.append(UncertaintyDataPoint(
            question=question,
            answer=None,  # Multiple valid answers possible
            uncertainty_type="aleatoric",
            is_hallucination=False,  # Not about factual accuracy
            ambiguity_score=ambiguity + random.uniform(-0.1, 0.1),
        ))

    return data_points


def create_factual_questions(num_samples: int = 200, seed: int = 42) -> List[UncertaintyDataPoint]:
    """Create factual questions with known answers (low uncertainty)."""
    random.seed(seed)

    # Simple factual questions
    factual_qa = [
        ("What is the capital of France?", "Paris"),
        ("What is 2 + 2?", "4"),
        ("What planet is closest to the Sun?", "Mercury"),
        ("What is the chemical symbol for water?", "H2O"),
        ("Who wrote Romeo and Juliet?", "William Shakespeare"),
        ("What is the largest ocean on Earth?", "Pacific Ocean"),
        ("How many continents are there?", "7"),
        ("What is the square root of 144?", "12"),
        ("What year did World War II end?", "1945"),
        ("What is the currency of Japan?", "Yen"),
        ("What is the boiling point of water in Celsius?", "100"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("What is the largest mammal?", "Blue whale"),
        ("What is the speed of light in vacuum?", "299,792,458 m/s"),
        ("What element has atomic number 1?", "Hydrogen"),
    ]

    data_points = []
    for _ in range(num_samples):
        q, a = random.choice(factual_qa)
        # Add some variation
        variations = ["", "Please tell me: ", "Can you answer: ", "Quick question: "]
        prefix = random.choice(variations)
        data_points.append(UncertaintyDataPoint(
            question=prefix + q,
            answer=a,
            uncertainty_type="low",
            is_hallucination=False,
            ambiguity_score=0.05,
        ))

    return data_points


def prepare_datasets(config, tokenizer) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Prepare train, validation, and test dataloaders."""

    # Load different types of data
    epistemic_data = load_truthfulqa_subset(config.train_samples // 3, config.seed)
    aleatoric_data = create_ambiguous_questions(config.train_samples // 3, config.seed)
    low_uncertainty_data = create_factual_questions(config.train_samples // 3, config.seed)

    # Combine and shuffle
    all_data = epistemic_data + aleatoric_data + low_uncertainty_data
    random.seed(config.seed)
    random.shuffle(all_data)

    # Split into train/val/test
    train_size = int(0.7 * len(all_data))
    val_size = int(0.15 * len(all_data))

    train_data = all_data[:train_size]
    val_data = all_data[train_size:train_size + val_size]
    test_data = all_data[train_size + val_size:]

    # Create datasets
    train_dataset = HallucinationDataset(train_data, tokenizer)
    val_dataset = HallucinationDataset(val_data, tokenizer)
    test_dataset = HallucinationDataset(test_data, tokenizer)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)

    return train_loader, val_loader, test_loader


def get_test_dataset_for_evaluation(config) -> List[UncertaintyDataPoint]:
    """Get a dedicated test dataset for final evaluation."""

    # Mix of different uncertainty types
    epistemic_data = load_truthfulqa_subset(config.test_samples // 2, config.seed + 100)
    factual_data = create_factual_questions(config.test_samples // 4, config.seed + 100)
    ambiguous_data = create_ambiguous_questions(config.test_samples // 4, config.seed + 100)

    all_data = epistemic_data + factual_data + ambiguous_data
    random.seed(config.seed + 100)
    random.shuffle(all_data)

    return all_data
