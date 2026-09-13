import random
from datasets import load_dataset


def load_truthfulqa_yesno(seed=42, max_n=200):
    """
    Load TruthfulQA yes/no-anchored subset.
    Selects questions where best_answer starts with 'yes' or 'no'.
    Returns (questions, gold_labels) where gold_labels are 'yes' or 'no'.
    """
    dataset = load_dataset("truthful_qa", "generation")["validation"]

    yesno_examples = []
    for ex in dataset:
        first_word = ex.get("best_answer", "").strip().lower().split()
        if first_word and first_word[0].rstrip(",.") in {"yes", "no"}:
            yesno_examples.append({
                "question": ex["question"],
                "gold_label": first_word[0].rstrip(",."),  # 'yes' or 'no'
                "best_answer": ex["best_answer"],
                "correct_answers": ex.get("correct_answers", []),
            })

    print(f"TruthfulQA yes/no-anchored subset: {len(yesno_examples)} examples found")

    rng = random.Random(seed)
    if len(yesno_examples) > max_n:
        yesno_examples = rng.sample(yesno_examples, max_n)

    questions = [ex["question"] for ex in yesno_examples]
    gold_labels = [ex["gold_label"] for ex in yesno_examples]
    return questions, gold_labels


def compute_em_labels(generated_answers, gold_labels):
    """
    Binary EM for yes/no-anchored questions.
    1 if the model's generated first word matches the gold yes/no label.
    Falls back to checking if gold label appears anywhere in short answer.
    """
    labels = []
    for gen, gold in zip(generated_answers, gold_labels):
        gen_norm = gen.strip().lower()
        gen_first = gen_norm.split()[0].rstrip(",.") if gen_norm.split() else ""
        if gen_first == gold:
            labels.append(1)
        elif gold in gen_norm[:20]:  # gold label anywhere in first 20 chars
            labels.append(1)
        else:
            labels.append(0)
    return labels
