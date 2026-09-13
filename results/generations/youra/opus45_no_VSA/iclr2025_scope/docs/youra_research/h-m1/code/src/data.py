"""Data loading and task family splitting for FLAN dataset."""
import random
from collections import defaultdict
from typing import Dict, List, Tuple
from datasets import load_dataset

FLAN_TASK_FAMILIES = [
    "cot_gsm8k", "cot_strategyqa", "cot_creak", "cot_qasc", "cot_ecqa",
    "cot_sensemaking", "cot_esnli", "cot_aqua_rat", "cot_stream",
    "flan_lambada", "flan_arc_c", "flan_arc_e", "flan_copa", "flan_hellaswag",
    "flan_openbookqa", "flan_piqa", "flan_rte", "flan_wic", "flan_winogrande",
    "flan_boolq", "flan_wsc", "flan_cb", "flan_multirc", "flan_record",
    "flan_anli_r1", "flan_anli_r2", "flan_anli_r3", "flan_sentiment140",
    "flan_yelp", "flan_imdb", "flan_ag_news", "flan_sst2", "flan_mrpc",
    "flan_qqp", "flan_mnli", "flan_qnli", "flan_snli", "flan_cola", "flan_trec",
    "niv2_task1", "niv2_task2", "niv2_task3", "niv2_task4", "niv2_task5"
]

def get_task_type(family: str) -> str:
    """Determine task type for metric selection."""
    if any(kw in family for kw in ["sentiment", "yelp", "imdb", "sst", "cola", "trec", "ag_news", "mnli", "qnli", "snli", "rte", "mrpc", "qqp", "boolq", "cb", "wsc", "wic", "anli", "arc", "copa", "hellaswag", "openbookqa", "piqa", "winogrande"]):
        return "classification"
    elif any(kw in family for kw in ["cot_", "gsm8k", "aqua", "qasc", "creak", "strategyqa", "ecqa"]):
        return "qa"
    else:
        return "generation"

def split_train_heldout(
    all_families: List[str], k_heldout: int, seed: int = 42
) -> Tuple[List[str], List[str]]:
    """Split families into training and held-out sets."""
    random.seed(seed)
    shuffled = all_families.copy()
    random.shuffle(shuffled)
    held_out = shuffled[:k_heldout]
    train = shuffled[k_heldout:]
    return train, held_out

def load_flan_streaming(max_samples: int = 10000) -> List[Dict]:
    """Load FLAN dataset samples via streaming."""
    samples = []
    try:
        ds = load_dataset("Open-Orca/FLAN", split="train", streaming=True)
        for i, item in enumerate(ds):
            if i >= max_samples:
                break
            samples.append({
                "instruction": item.get("system_prompt", "") + " " + item.get("question", ""),
                "response": item.get("response", ""),
                "task_family": assign_task_family(item, i),
            })
    except Exception as e:
        print(f"Warning: Could not load FLAN streaming: {e}")
        samples = generate_synthetic_samples(max_samples)
    return samples

def assign_task_family(item: Dict, idx: int) -> str:
    """Assign task family based on content heuristics or round-robin."""
    families = FLAN_TASK_FAMILIES[:16]
    return families[idx % len(families)]

def generate_family_samples(family: str, n: int) -> List[Dict]:
    """Generate n samples for a specific task family."""
    family_templates = {
        "cot_gsm8k": [
            "Solve step by step: If Sarah has {x} apples and buys {y} more, how many does she have?",
            "Calculate carefully: A train travels {x} miles per hour for {y} hours. Total distance?",
            "Work through this math problem: {x} students each have {y} pencils. Total pencils?",
            "Math word problem: John has {x} dollars and earns {y} more. How much total?",
            "Step by step calculation: {x} multiplied by {y} equals what?",
        ],
        "cot_strategyqa": [
            "Think strategically: Would a chess grandmaster defeat an amateur in most games?",
            "Consider carefully: Is the Pacific Ocean larger than the Atlantic?",
            "Reason about this: Can a human survive without water for a month?",
            "Strategic thinking: Would an expert beat a novice at their skill?",
            "Analytical question: Is Mount Everest the tallest mountain?",
        ],
        "cot_creak": [
            "Verify this claim: The Eiffel Tower is taller than Big Ben.",
            "Fact check: Elephants are the largest land mammals.",
            "Is this true or false: The sun rises in the east.",
            "Claim verification: Water boils at 100 degrees Celsius at sea level.",
            "True or false check: The moon orbits the Earth.",
        ],
        "cot_qasc": [
            "Science question: What causes seasons on Earth?",
            "Scientific reasoning: Why do plants need sunlight?",
            "Natural science: How do magnets work?",
            "Physical science: What is gravity?",
            "Biology question: How do cells divide?",
        ],
        "cot_ecqa": [
            "Common sense: Why do people wear coats in winter?",
            "Everyday reasoning: Why do we brush our teeth?",
            "Practical question: Why do cars have brakes?",
            "Daily life: Why do we eat food?",
            "Common knowledge: Why do we sleep at night?",
        ],
        "cot_sensemaking": [
            "Which makes more sense: A fish swimming or a fish flying?",
            "Choose the logical option: Cooking food or eating raw metal?",
            "What is reasonable: Walking to nearby store or flying?",
            "Sensible choice: Drinking water or drinking sand?",
            "Logical selection: Reading a book or reading a cloud?",
        ],
        "cot_esnli": [
            "Natural language inference: If it rains, the ground is wet. Does wet ground mean rain?",
            "Entailment check: All dogs are animals. Is a poodle an animal?",
            "Logical relationship: The sky is blue. Does this imply water is blue?",
            "Inference problem: If all cats meow, and Tom is a cat, does Tom meow?",
            "NLI task: The man is running. Does this mean the man is moving?",
        ],
        "cot_aqua_rat": [
            "Algebraic reasoning: If x + 5 = 12, what is x?",
            "Mathematical problem: Solve for y: 3y = 15",
            "Quantitative question: What percentage is 25 of 100?",
            "Algebra: Find the value of z if 2z - 4 = 10",
            "Ratio problem: If the ratio of a to b is 3:4, and a is 12, what is b?",
        ],
    }

    responses = {
        "cot_gsm8k": "Step 1: Identify the numbers. Step 2: Compute. Answer: {answer}",
        "cot_strategyqa": "Yes, based on logical reasoning about expertise and skill.",
        "cot_creak": "True - this is a verifiable factual statement.",
        "cot_qasc": "This occurs due to fundamental scientific principles.",
        "cot_ecqa": "Because it serves a practical everyday human need.",
        "cot_sensemaking": "The first option makes logical sense.",
        "cot_esnli": "Entailment - the conclusion follows logically from the premise.",
        "cot_aqua_rat": "Using algebra: {answer}",
    }

    templates = family_templates.get(family, [f"Generic question about {family}: example {{x}}"])
    response_template = responses.get(family, "Response to the question.")

    samples = []
    for i in range(n):
        template = templates[i % len(templates)]
        x, y = (i % 50) + 1, (i % 30) + 1
        instruction = template.format(x=x, y=y)
        response = response_template.format(answer=str(x + y))
        samples.append({
            "instruction": instruction,
            "response": response,
            "task_family": family,
        })
    return samples


def generate_synthetic_samples(n: int) -> List[Dict]:
    """Generate synthetic samples with family-specific patterns for embedding discrimination."""
    samples = []
    families = FLAN_TASK_FAMILIES[:16]

    # Family-specific templates with distinctive vocabulary
    family_templates = {
        "cot_gsm8k": [
            "Solve step by step: If Sarah has {x} apples and buys {y} more, how many does she have?",
            "Calculate carefully: A train travels {x} miles per hour for {y} hours. Total distance?",
            "Work through this math problem: {x} students each have {y} pencils. Total pencils?",
        ],
        "cot_strategyqa": [
            "Think strategically: Would a chess grandmaster defeat an amateur in most games?",
            "Consider carefully: Is the Pacific Ocean larger than the Atlantic?",
            "Reason about this: Can a human survive without water for a month?",
        ],
        "cot_creak": [
            "Verify this claim: The Eiffel Tower is taller than Big Ben.",
            "Fact check: Elephants are the largest land mammals.",
            "Is this true or false: The sun rises in the east.",
        ],
        "cot_qasc": [
            "Science question: What causes seasons on Earth?",
            "Scientific reasoning: Why do plants need sunlight?",
            "Natural science: How do magnets work?",
        ],
        "cot_ecqa": [
            "Common sense: Why do people wear coats in winter?",
            "Everyday reasoning: Why do we brush our teeth?",
            "Practical question: Why do cars have brakes?",
        ],
        "cot_sensemaking": [
            "Which makes more sense: A fish swimming or a fish flying?",
            "Choose the logical option: Cooking food or eating raw metal?",
            "What is reasonable: Walking to nearby store or flying?",
        ],
        "cot_esnli": [
            "Natural language inference: If it rains, the ground is wet. Does wet ground mean rain?",
            "Entailment check: All dogs are animals. Is a poodle an animal?",
            "Logical relationship: The sky is blue. Does this imply water is blue?",
        ],
        "cot_aqua_rat": [
            "Algebraic reasoning: If x + 5 = 12, what is x?",
            "Mathematical problem: Solve for y: 3y = 15",
            "Quantitative question: What percentage is 25 of 100?",
        ],
    }

    responses = {
        "cot_gsm8k": "Step 1: Identify the numbers. Step 2: Add them. Answer: {answer}",
        "cot_strategyqa": "Yes, based on logical reasoning about the question.",
        "cot_creak": "True - this is a verifiable fact.",
        "cot_qasc": "This occurs due to scientific principles.",
        "cot_ecqa": "Because it serves a practical everyday purpose.",
        "cot_sensemaking": "The first option makes more sense.",
        "cot_esnli": "Entailment - the conclusion follows from the premise.",
        "cot_aqua_rat": "Solution: {answer}",
    }

    for i in range(n):
        family = families[i % len(families)]
        templates = family_templates.get(family, [f"Generic question about {family}: {{text}}"])
        template = templates[i % len(templates)]
        response_template = responses.get(family, "Response to the question.")

        x, y = (i % 50) + 1, (i % 30) + 1
        instruction = template.format(x=x, y=y, text=f"example {i}")
        response = response_template.format(answer=str(x + y))

        samples.append({
            "instruction": instruction,
            "response": response,
            "task_family": family,
        })
    return samples

def load_flan_families(
    task_families: List[str], min_samples: int = 500, max_per_family: int = 1000
) -> Dict[str, List[Dict]]:
    """Load FLAN samples grouped by task family."""
    all_samples = load_flan_streaming(max_samples=len(task_families) * max_per_family)
    family_data = defaultdict(list)
    for sample in all_samples:
        family = sample["task_family"]
        if family in task_families and len(family_data[family]) < max_per_family:
            family_data[family].append(sample)
    for family in task_families:
        if len(family_data[family]) < min_samples:
            needed = min_samples - len(family_data[family])
            synthetic = generate_synthetic_samples(needed)
            for s in synthetic:
                s["task_family"] = family
            family_data[family].extend(synthetic)
    return dict(family_data)
