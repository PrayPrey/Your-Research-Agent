"""Generate synthetic PWC data for h-e1 PoC validation."""
import json
from pathlib import Path
from datetime import datetime, timedelta
import random


def generate_benchmark_data(benchmark: str, output_dir: Path):
    """Generate synthetic leaderboard data with realistic patterns."""
    # ImageNet: 2015-2020, scores 70-90%
    # GLUE: 2018-2022, scores 60-90%
    # SQuAD: 2016-2020, scores 75-95%

    config = {
        "imagenet": {
            "start_year": 2015,
            "end_year": 2020,
            "score_range": (0.70, 0.90),
            "submissions_per_year": 50
        },
        "glue": {
            "start_year": 2018,
            "end_year": 2022,
            "score_range": (0.60, 0.90),
            "submissions_per_year": 40
        },
        "squad": {
            "start_year": 2016,
            "end_year": 2020,
            "score_range": (0.75, 0.95),
            "submissions_per_year": 45
        }
    }

    if benchmark not in config:
        return

    cfg = config[benchmark]
    submissions = []

    # Generate submissions with upward trend
    start_date = datetime(cfg["start_year"], 1, 1)
    end_date = datetime(cfg["end_year"], 12, 31)
    total_days = (end_date - start_date).days

    total_submissions = cfg["submissions_per_year"] * (cfg["end_year"] - cfg["start_year"])

    for i in range(total_submissions):
        # Distribute submissions across time range
        days_offset = int((i / total_submissions) * total_days)
        date = start_date + timedelta(days=days_offset)

        # Scores improve over time
        progress = i / total_submissions
        min_score, max_score = cfg["score_range"]
        base_score = min_score + (max_score - min_score) * progress

        # Add noise
        score = base_score + random.gauss(0, 0.02)
        score = max(min_score, min(max_score, score))

        submission = {
            "benchmark": benchmark,
            "model_name": f"Model-{i:04d}",
            "score": round(score, 4),
            "submission_date": date.strftime("%Y-%m-%d"),
            "paper_title": f"Paper {i}",
            "paper_url": f"https://arxiv.org/abs/placeholder.{i}"
        }
        submissions.append(submission)

    # Save to JSONL
    output_file = output_dir / f"{benchmark}_raw.jsonl"
    with open(output_file, "w") as f:
        for sub in submissions:
            f.write(json.dumps(sub) + "\n")

    print(f"Generated {len(submissions)} submissions for {benchmark}")


if __name__ == "__main__":
    output_dir = Path("../data/pwc_leaderboards")
    output_dir.mkdir(parents=True, exist_ok=True)

    for benchmark in ["imagenet", "glue", "squad"]:
        generate_benchmark_data(benchmark, output_dir)

    print("\nSynthetic data generation complete")
