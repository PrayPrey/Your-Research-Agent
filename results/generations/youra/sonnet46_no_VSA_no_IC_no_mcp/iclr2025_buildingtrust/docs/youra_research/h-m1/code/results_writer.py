"""Write H-M1 analysis results using h-e1 storage utilities."""
import logging
import sys

logger = logging.getLogger(__name__)


def _get_storage():
    from config import H_E1_CODE_PATH
    if H_E1_CODE_PATH not in sys.path:
        sys.path.insert(0, H_E1_CODE_PATH)
    from results.storage import write_json, write_gate_result
    return write_json, write_gate_result


def write_main_results(stratum_results: dict, out_dir: str) -> None:
    """write_json(h_m1_results.json)"""
    import os
    os.makedirs(out_dir, exist_ok=True)
    write_json, _ = _get_storage()
    path = f"{out_dir}/h_m1_results.json"
    write_json(path, stratum_results)
    logger.info("Wrote main results: %s", path)


def write_gate_report(passed: bool, indicators: dict, out_dir: str) -> None:
    """write_gate_result(h_m1_gate_report.json, ...)"""
    import os
    os.makedirs(out_dir, exist_ok=True)
    _, write_gate_result = _get_storage()
    path = f"{out_dir}/h_m1_gate_report.json"
    # Map to h-e1 write_gate_result signature:
    # passed_cells: int, failed_cells: list, clean_sanity: bool
    passed_cells = int(passed)
    failed_cells = [] if passed else ["preservation_rate_ok or delta_ece_positive failed"]
    clean_sanity = indicators.get("delta_ece_positive", False)
    write_gate_result(
        path,
        passed_cells=passed_cells,
        failed_cells=failed_cells,
        clean_sanity=bool(clean_sanity),
        gate_passed=passed,
        summary=indicators,
    )
    logger.info("Wrote gate report: %s (gate_passed=%s)", path, passed)


def write_ablation_results(ablation_data: dict, out_dir: str) -> None:
    """write_json(ablation_results.json)"""
    import os
    os.makedirs(out_dir, exist_ok=True)
    write_json, _ = _get_storage()
    path = f"{out_dir}/ablation_results.json"
    write_json(path, ablation_data)
    logger.info("Wrote ablation results: %s", path)
