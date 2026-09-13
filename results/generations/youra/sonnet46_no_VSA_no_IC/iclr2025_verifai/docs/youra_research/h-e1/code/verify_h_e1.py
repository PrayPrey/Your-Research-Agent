import logging
import sys
import os

# Run from project root so relative paths resolve correctly
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Add code dir to path for sibling imports
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import load_failures, verify_counts, verify_fields, ARCHIVE
from api_verifier import verify_api_accessible, verify_task_ids
from figure_generator import generate_all, FIGURES_DIR
from report_writer import write_report, RESULTS_DIR


def run_verification(archive: str = ARCHIVE,
                     figures_dir: str = FIGURES_DIR,
                     results_dir: str = RESULTS_DIR) -> dict:
    checks = {}

    # Step 1: Load failures from stored JSON
    logger.info("Loading h-e1 Run 2 eval results...")
    try:
        he_failures, mbpp_failures = load_failures(archive)
        checks["load_json"] = "PASS"
        logger.info(f"  HE+ failures: {len(he_failures)}, MBPP+ failures: {len(mbpp_failures)}")
    except Exception as e:
        logger.error(f"load_failures failed: {e}")
        checks["load_json"] = "FAIL"
        return write_report(checks, 0, 0, results_dir)

    # Step 2: Verify counts
    try:
        verify_counts(he_failures, mbpp_failures)
        checks["count_verification"] = "PASS"
        logger.info("  Count check: 34 HE+ + 100 MBPP+ = 134 ✓")
    except AssertionError as e:
        logger.error(f"Count mismatch: {e}")
        checks["count_verification"] = "FAIL"

    # Step 3: Verify fields present — collect all empty-pft tasks before failing
    empty_pft_tasks = []
    for failures_dict, label in [(he_failures, "HE+"), (mbpp_failures, "MBPP+")]:
        for tid, rec in failures_dict.items():
            if not rec.get("plus_fail_tests"):
                empty_pft_tasks.append(tid)
    if empty_pft_tasks:
        logger.warning(f"  {len(empty_pft_tasks)} tasks have empty plus_fail_tests: {empty_pft_tasks}")
        checks["field_verification"] = "FAIL"
    else:
        checks["field_verification"] = "PASS"
        logger.info("  Field check: solution + plus_fail_tests present for all 134 ✓")
    # solution check separately
    missing_solution = [tid for d in [he_failures, mbpp_failures]
                        for tid, rec in d.items() if not rec.get("solution")]
    if missing_solution:
        logger.error(f"  Missing solution for: {missing_solution}")
        checks["field_verification"] = "FAIL"

    # Step 4: Verify EvalPlus API accessible
    try:
        he_problems, mbpp_problems = verify_api_accessible()
        checks["api_accessible"] = "PASS"
        logger.info(f"  EvalPlus API: HE+={len(he_problems)} tasks, MBPP+={len(mbpp_problems)} tasks ✓")
    except Exception as e:
        logger.error(f"EvalPlus API inaccessible: {e}")
        checks["api_accessible"] = "FAIL"
        he_problems, mbpp_problems = {}, {}

    # Step 5: Verify task IDs in EvalPlus
    if he_problems and mbpp_problems:
        try:
            verify_task_ids(he_failures, mbpp_failures, he_problems, mbpp_problems)
            checks["task_id_verification"] = "PASS"
            logger.info("  Task ID check: all 134 task IDs in EvalPlus datasets ✓")
        except AssertionError as e:
            logger.error(f"Task ID mismatch: {e}")
            checks["task_id_verification"] = "FAIL"
    else:
        checks["task_id_verification"] = "FAIL"

    # Step 6: Generate figures
    try:
        generate_all(he_failures, mbpp_failures, he_problems, mbpp_problems, figures_dir)
        checks["figure_generation"] = "PASS"
        logger.info(f"  Figures saved to {figures_dir} ✓")
    except Exception as e:
        logger.error(f"Figure generation failed: {e}")
        checks["figure_generation"] = "FAIL"

    # Step 7: Write report
    extra = {}
    if empty_pft_tasks:
        extra["empty_plus_fail_tests_tasks"] = empty_pft_tasks
        extra["recoverable_count"] = len(he_failures) + len(mbpp_failures) - len(empty_pft_tasks)
        extra["note"] = (f"{len(empty_pft_tasks)}/134 tasks have empty plus_fail_tests "
                         f"(plus_status=fail but test list not stored). "
                         f"{extra['recoverable_count']}/134 fully recoverable for Conditions B/C.")
    report = write_report(checks, len(he_failures), len(mbpp_failures), results_dir, extra=extra or None)

    if report["gate"] == "PASS":
        logger.info(f"✅ H-E1 gate PASS: {report['total']} failures loaded "
                    f"({report['he_failures']} HE+ + {report['mbpp_failures']} MBPP+)")
    else:
        failed = [k for k, v in checks.items() if v == "FAIL"]
        logger.error(f"❌ H-E1 gate FAIL. Failed checks: {failed}")

    return report


if __name__ == "__main__":
    report = run_verification()
    sys.exit(0 if report["gate"] == "PASS" else 1)
