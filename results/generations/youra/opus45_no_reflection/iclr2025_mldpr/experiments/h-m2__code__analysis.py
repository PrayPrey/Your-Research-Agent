"""Analysis pipeline for H-M2 hypothesis."""
from classifier import classify_benchmark
from date_extractor import extract_benchmark_date, resolve_missing_dates
from config import POST_2020_THRESHOLD


def build_benchmark_records(raw_datasets: list[dict]) -> list[dict]:
    """Build unified benchmark records with classification and dates."""
    records = []
    for raw in raw_datasets:
        name = raw.get("name") or raw.get("dataset") or ""
        description = raw.get("description") or ""
        tasks = raw.get("tasks") or raw.get("task") or []
        if isinstance(tasks, str):
            tasks = [tasks]

        category = classify_benchmark(name, description, tasks)
        year = extract_benchmark_date(raw)

        records.append({
            "name": name,
            "description": description[:200] if description else "",
            "tasks": tasks,
            "category": category,
            "year": year,
            "_raw": raw,
        })
    return records


def compute_post2020_ratio(benchmarks: list[dict]) -> dict:
    """Compute percentage of emergent benchmarks created post-2020."""
    emergent = [b for b in benchmarks if b["category"] == "emergent-capability" and b["year"] is not None]
    post_2020 = [b for b in emergent if b["year"] >= 2020]
    pre_2020 = [b for b in emergent if b["year"] < 2020]

    ratio = len(post_2020) / len(emergent) if emergent else 0.0

    return {
        "total_emergent": len(emergent),
        "post_2020_count": len(post_2020),
        "pre_2020_count": len(pre_2020),
        "post_2020_ratio": ratio,
        "passes_threshold": ratio > POST_2020_THRESHOLD,
    }


def compute_creation_rate_acceleration(benchmarks: list[dict]) -> dict:
    """Compare emergent-benchmark creation rate pre/post 2020."""
    emergent = [b for b in benchmarks if b["category"] == "emergent-capability" and b["year"] is not None]
    pre = [b for b in emergent if b["year"] < 2020]
    post = [b for b in emergent if b["year"] >= 2020]

    pre_years = 20  # 2000-2019
    post_years = 6  # 2020-2025

    pre_rate = len(pre) / pre_years if pre_years else 0
    post_rate = len(post) / post_years if post_years else 0

    return {
        "pre_2020_count": len(pre),
        "post_2020_count": len(post),
        "pre_2020_rate": pre_rate,
        "post_2020_rate": post_rate,
        "acceleration_ratio": post_rate / pre_rate if pre_rate > 0 else float("inf"),
    }


def evaluate_hypothesis(results: dict) -> dict:
    """Evaluate H-M2 success criteria."""
    passed = results["post_2020_ratio"] > POST_2020_THRESHOLD
    return {
        "gate": "SHOULD_WORK",
        "result": "PASS" if passed else "FAIL",
        "post_2020_ratio": results["post_2020_ratio"],
        "threshold": POST_2020_THRESHOLD,
        "margin": results["post_2020_ratio"] - POST_2020_THRESHOLD,
        "emergent_count": results["total_emergent"],
        "post_2020_count": results["post_2020_count"],
    }
