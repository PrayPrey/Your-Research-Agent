import json
from dataclasses import dataclass

@dataclass
class Completion:
    task_id: str
    completion: str

def load_completions_jsonl(path: str) -> list[Completion]:
    completions = []
    with open(path) as f:
        for line in f:
            data = json.loads(line)
            completions.append(Completion(task_id=data["task_id"], completion=data["completion"]))
    return completions

def generate_canonical_completions(problems) -> list[Completion]:
    return [Completion(task_id=p.task_id, completion=p.canonical_solution) for p in problems]
