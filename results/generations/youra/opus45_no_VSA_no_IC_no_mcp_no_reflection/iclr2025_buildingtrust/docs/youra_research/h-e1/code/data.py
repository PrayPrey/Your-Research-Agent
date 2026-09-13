from datasets import load_dataset

def load_truthfulqa() -> list[dict]:
    ds = load_dataset("truthful_qa", "generation", split="validation")
    out = []
    for row in ds:
        out.append({
            "question": row["question"],
            "correct_answers": row["correct_answers"],
            "incorrect_answers": row["incorrect_answers"],
        })
    return out

def load_halueval_qa(max_samples: int = 5000) -> list[dict]:
    ds = load_dataset("pminervini/HaluEval", "qa_samples", split="data")
    out = []
    for i, row in enumerate(ds):
        if i >= max_samples:
            break
        out.append({
            "question": row["question"],
            "answer": row["answer"],
            "hallucination": row["hallucination"],  # "yes" or "no"
        })
    return out
