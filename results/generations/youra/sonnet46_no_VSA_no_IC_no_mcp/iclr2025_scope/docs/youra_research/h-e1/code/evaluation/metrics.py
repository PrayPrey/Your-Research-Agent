from evaluation.longbench_eval import scorer as _scorer


def compute_f1(prediction: str, answers: list, task: str) -> float:
    return _scorer(prediction, answers, dataset=task)


def macro_f1(per_task_f1: dict) -> float:
    task_means = [sum(v) / len(v) for v in per_task_f1.values() if v]
    if not task_means:
        return 0.0
    return sum(task_means) / len(task_means)
