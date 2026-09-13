"""Benchmark classifier: emergent-capability vs traditional."""
from config import EMERGENT_KEYWORDS, EMERGENT_BENCHMARK_NAMES, EMERGENT_TASK_TYPES


def classify_benchmark(name: str, description: str = None, tasks: list[str] = None) -> str:
    """Classify benchmark as emergent-capability or traditional."""
    if not name:
        return "traditional"

    name_lower = name.lower().replace("-", "").replace("_", "")

    for eb in EMERGENT_BENCHMARK_NAMES:
        if eb.replace("-", "") in name_lower:
            return "emergent-capability"

    if description:
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in EMERGENT_KEYWORDS):
            return "emergent-capability"

    if tasks:
        task_names = []
        for t in tasks:
            if isinstance(t, dict):
                task_names.append(t.get("name", "") or t.get("task", ""))
            elif isinstance(t, str):
                task_names.append(t)
        task_set = {n.lower().replace("_", "-") for n in task_names if n}
        if task_set & EMERGENT_TASK_TYPES:
            return "emergent-capability"

    return "traditional"
