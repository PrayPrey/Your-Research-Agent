def normalize(s: str) -> str:
    return s.lower().strip()

def label_truthfulqa(sample: dict, responses: list[str]) -> int:
    correct = {normalize(a) for a in sample["correct_answers"]}
    incorrect = {normalize(a) for a in sample["incorrect_answers"]}
    for r in responses:
        r_norm = normalize(r)
        for inc in incorrect:
            if inc in r_norm:
                return 1  # hallucinated
        for cor in correct:
            if cor in r_norm:
                return 0  # truthful
    return 1  # default hallucinated if no match

def label_halueval(sample: dict, use_right: bool) -> int:
    return 0 if use_right else 1
