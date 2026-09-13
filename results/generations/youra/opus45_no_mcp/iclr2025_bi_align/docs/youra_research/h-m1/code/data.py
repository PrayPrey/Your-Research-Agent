"""Dataset loading for H-E1 calibration inversion analysis."""

from typing import TypedDict, List, Optional
from datasets import load_dataset


class Task(TypedDict):
    task_id: str
    source_dataset: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]
    category: Optional[str]


def load_truthfulqa() -> List[Task]:
    """Load TruthfulQA multiple choice dataset."""
    ds = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
    tasks = []
    for i, row in enumerate(ds):
        mc1 = row.get("mc1_targets", {})
        choices = mc1.get("choices", [])
        labels = mc1.get("labels", [])

        if not choices or not labels:
            continue

        correct_idx = labels.index(1) if 1 in labels else 0
        correct = choices[correct_idx]
        incorrect = [c for j, c in enumerate(choices) if j != correct_idx]

        tasks.append(Task(
            task_id=f"tqa_{i}",
            source_dataset="truthfulqa",
            question=row["question"],
            correct_answer=correct,
            incorrect_answers=incorrect[:3],
            category=row.get("category")
        ))
    return tasks


def load_mmlu_moral() -> List[Task]:
    """Load MMLU moral_scenarios subset."""
    ds = load_dataset("cais/mmlu", "moral_scenarios", split="test")
    tasks = []
    for i, row in enumerate(ds):
        choices = row["choices"]
        answer_idx = row["answer"]

        correct = choices[answer_idx]
        incorrect = [c for j, c in enumerate(choices) if j != answer_idx]

        tasks.append(Task(
            task_id=f"mmlu_{i}",
            source_dataset="mmlu_moral",
            question=row["question"],
            correct_answer=correct,
            incorrect_answers=incorrect,
            category="moral_scenarios"
        ))
    return tasks


def load_anthropic_hh() -> List[Task]:
    """Load Anthropic HH-RLHF subset for preference analysis."""
    ds = load_dataset("Anthropic/hh-rlhf", split="test[:500]")
    tasks = []
    for i, row in enumerate(ds):
        chosen = row["chosen"]
        rejected = row["rejected"]

        human_prompt = chosen.split("\n\nHuman:")[1].split("\n\nAssistant:")[0].strip() if "\n\nHuman:" in chosen else chosen[:200]
        correct_response = chosen.split("\n\nAssistant:")[-1].strip()[:500] if "\n\nAssistant:" in chosen else chosen[-200:]
        incorrect_response = rejected.split("\n\nAssistant:")[-1].strip()[:500] if "\n\nAssistant:" in rejected else rejected[-200:]

        tasks.append(Task(
            task_id=f"hh_{i}",
            source_dataset="anthropic_hh",
            question=human_prompt[:500],
            correct_answer=correct_response,
            incorrect_answers=[incorrect_response],
            category="preference"
        ))
    return tasks


def load_all_tasks() -> List[Task]:
    """Load and combine all datasets into unified task list."""
    print("Loading TruthfulQA...")
    tqa = load_truthfulqa()
    print(f"  Loaded {len(tqa)} TruthfulQA tasks")

    print("Loading MMLU moral scenarios...")
    mmlu = load_mmlu_moral()
    print(f"  Loaded {len(mmlu)} MMLU tasks")

    print("Loading Anthropic HH-RLHF...")
    hh = load_anthropic_hh()
    print(f"  Loaded {len(hh)} HH-RLHF tasks")

    all_tasks = tqa + mmlu + hh
    print(f"Total: {len(all_tasks)} tasks")
    return all_tasks
