import re
import string
from typing import Dict, List, Optional, Tuple

from datasets import load_dataset, Dataset


TRIVIA_QA_FEW_SHOT = [
    {"question": "What is the capital of France?", "answer": "Paris"},
    {"question": "Who wrote Hamlet?", "answer": "Shakespeare"},
    {"question": "What element has symbol Au?", "answer": "Gold"},
    {"question": "In what year did World War II end?", "answer": "1945"},
    {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
]

NQ_FEW_SHOT = [
    {"question": "Who is the CEO of Tesla?", "answer": "Elon Musk"},
    {"question": "When was the Eiffel Tower built?", "answer": "1889"},
    {"question": "What is the chemical formula for water?", "answer": "H2O"},
    {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
    {"question": "What is the speed of light?", "answer": "299792458 meters per second"},
]


def normalize_answer(answer: str) -> str:
    """Lowercase, remove punctuation, articles, and extra whitespace."""
    answer = answer.lower()
    answer = re.sub(r"\b(a|an|the)\b", " ", answer)
    answer = "".join(ch for ch in answer if ch not in string.punctuation)
    answer = " ".join(answer.split())
    return answer


def extract_first_answer(text: str) -> str:
    """Extract the first answer from generated text (before any continuation)."""
    # Model output often continues with more Q&A; take only first line
    first_line = text.split("\n")[0].strip()
    return first_line if first_line else text.strip()


def compute_exact_match(prediction: str, gold_answers: List[str]) -> int:
    """Return 1 if normalized prediction matches any normalized gold answer."""
    # Extract just the first line to avoid matching against model continuations
    first_answer = extract_first_answer(prediction)
    norm_pred = normalize_answer(first_answer)
    for gold in gold_answers:
        if normalize_answer(gold) == norm_pred:
            return 1
    return 0


def format_few_shot_prompt(question: str, examples: List[Dict], n_shot: int = 5) -> str:
    """Format few-shot prompt for QA generation."""
    shots = examples[:n_shot]
    prompt = ""
    for ex in shots:
        prompt += f"Q: {ex['question']}\nA: {ex['answer']}\n\n"
    prompt += f"Q: {question}\nA:"
    return prompt


def load_trivia_qa(n_few_shot: int = 5) -> Tuple[List[Dict], List[str]]:
    """Load TriviaQA rc.nocontext validation split with gold answers."""
    ds = load_dataset("trivia_qa", "rc.nocontext", split="validation",
                      storage_options={"client_kwargs": {"timeout": 60}})
    items = []
    for row in ds:
        question = row["question"]
        answer = row["answer"]
        gold_answers = answer.get("aliases") or answer.get("normalized_aliases") or []
        if not gold_answers and answer.get("value") and answer["value"] != "<unk>":
            gold_answers = [answer["value"]]
        if not gold_answers:
            continue
        prompt = format_few_shot_prompt(question, TRIVIA_QA_FEW_SHOT, n_shot=n_few_shot)
        items.append({
            "question_id": row["question_id"],
            "question": question,
            "prompt": prompt,
            "gold_answers": gold_answers,
        })
    return items


def load_natural_questions(n_few_shot: int = 5) -> List[Dict]:
    """Load NaturalQuestions open-domain validation split."""
    ds = load_dataset("google-research-datasets/natural_questions", split="validation",
                      storage_options={"client_kwargs": {"timeout": 60}})
    items = []
    for i, row in enumerate(ds):
        question = row["question"]["text"] if isinstance(row["question"], dict) else row["question"]
        # Extract short answers
        gold_answers = []
        ann = row.get("annotations", {})
        if isinstance(ann, dict):
            # Batched dict format: annotations["short_answers"] is a list of dicts per annotator
            for sa in ann.get("short_answers", []):
                if isinstance(sa, dict):
                    texts = sa.get("text", [])
                    gold_answers.extend(texts if isinstance(texts, list) else [texts])
        else:
            for a in ann:
                for sa in a.get("short_answers", []):
                    if sa.get("text"):
                        gold_answers.extend(sa["text"] if isinstance(sa["text"], list) else [sa["text"]])
        if not gold_answers:
            continue
        prompt = format_few_shot_prompt(question, NQ_FEW_SHOT, n_shot=n_few_shot)
        items.append({
            "question_id": str(row.get("id", i)),
            "question": question,
            "prompt": prompt,
            "gold_answers": list(set(gold_answers)),
        })
    return items[:500]


def load_truthful_qa(n_few_shot: int = 0) -> List[Dict]:
    """Load TruthfulQA mc1_targets validation split (scope boundary test)."""
    ds = load_dataset("truthful_qa", "mc1_targets", split="validation",
                      storage_options={"client_kwargs": {"timeout": 60}})
    items = []
    for i, row in enumerate(ds):
        question = row["question"]
        # mc1: correct answer is first in choices
        choices = row.get("mc1_targets", {})
        labels = choices.get("labels", [])
        choice_list = choices.get("choices", [])
        gold_answers = [c for c, l in zip(choice_list, labels) if l == 1]
        prompt = format_few_shot_prompt(question, [], n_shot=0)
        items.append({
            "question_id": str(i),
            "question": question,
            "prompt": prompt,
            "gold_answers": gold_answers,
        })
    return items


def get_dataset(name: str, n_few_shot: int = 5) -> List[Dict]:
    """Load dataset by name. Returns list of items with question_id, prompt, gold_answers."""
    if name == "trivia_qa":
        return load_trivia_qa(n_few_shot=n_few_shot)
    elif name == "natural_questions":
        return load_natural_questions(n_few_shot=n_few_shot)
    elif name == "truthful_qa":
        return load_truthful_qa(n_few_shot=n_few_shot)
    else:
        raise ValueError(f"Unknown dataset: {name}")
