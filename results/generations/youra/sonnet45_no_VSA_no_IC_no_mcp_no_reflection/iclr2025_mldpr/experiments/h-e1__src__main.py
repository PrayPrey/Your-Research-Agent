"""Pipeline orchestration for h-e1 data availability verification."""
import asyncio
import json
from pathlib import Path
from pwc_scraper import PWCLeaderboardScraper
from data_validator import DataValidator


async def run_pipeline():
    """Execute h-e1 verification pipeline."""
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    output_dir = data_dir / "pwc_leaderboards"

    print("=" * 60)
    print("H-E1: Data Availability Verification Pipeline")
    print("=" * 60)

    # Step 1: PWC API data collection
    print("\n[Step 1/3] Collecting PWC leaderboard data...")
    benchmarks = {
        "imagenet": "imagenet",
        "glue": "glue",
        "squad": "squad"
    }

    async with PWCLeaderboardScraper(output_dir) as scraper:
        for bench_name, bench_slug in benchmarks.items():
            try:
                submissions = await scraper.fetch_benchmark_sota(bench_slug)
                scraper.save_jsonl(submissions, f"{bench_name}_raw.jsonl")
            except Exception as e:
                print(f"ERROR collecting {bench_name}: {e}")

    # Step 2: Validation
    print("\n[Step 2/3] Validating data completeness...")
    validator = DataValidator(data_dir)
    report = validator.generate_report()

    # Save report
    report_path = data_dir / "validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Validation report saved to {report_path}")

    # Step 3: Success criteria check
    print("\n[Step 3/3] Evaluating success criteria...")
    print(f"\nPWC Data Pass: {report['success_criteria']['pwc_pass']}")
    print(f"Survey Pass: {report['success_criteria']['survey_pass']} (skipped in PoC)")
    print(f"Overall Pass: {report['success_criteria']['overall_pass']}")

    # Print detailed results
    print("\nPWC Data Details:")
    for benchmark, results in report["pwc_data"].items():
        print(f"  {benchmark}:")
        print(f"    Timestamped: {results['timestamped_submissions']}/{results['total_submissions']}")
        print(f"    Coverage: {results['timestamp_coverage']:.1%}")
        print(f"    Range: {results['temporal_range']}")
        print(f"    Pass: {results['pass']}")

    # Final verdict
    print("\n" + "=" * 60)
    if report["success_criteria"]["overall_pass"]:
        print("H-E1 EXISTENCE: PASS")
        print("Data infrastructure verified - ready for h-m1")
    else:
        print("H-E1 EXISTENCE: FAIL")
        print(f"Failure response: {report['failure_response']}")
    print("=" * 60)

    return report


if __name__ == "__main__":
    asyncio.run(run_pipeline())
