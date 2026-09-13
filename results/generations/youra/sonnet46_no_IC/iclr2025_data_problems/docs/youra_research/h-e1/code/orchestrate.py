"""Top-level pipeline runner for H-E1."""
import argparse
import json
import logging
import os

from config import CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_STAGE_FILE = os.path.join(os.path.dirname(CONFIG.results_csv), "pipeline_state.json")


def load_stage_state(state_file: str) -> dict:
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return {"stages_completed": [], "variant_metadata": []}


def save_stage_state(state: dict, state_file: str) -> None:
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    tmp = state_file + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, state_file)


def run_pipeline(stage: str = "all", resume: bool = True) -> None:
    """Entry point. Calls stages in order with resume support."""
    state = load_stage_state(_STAGE_FILE) if resume else {"stages_completed": [], "variant_metadata": []}
    completed = set(state.get("stages_completed", []))

    def _should_run(s):
        return stage == "all" or stage == s

    # Stage 1: Curate
    if _should_run("curate") and "curate" not in completed:
        logger.info("=== Stage: curate ===")
        from curate import curate_all_variants, get_corpus_stream, log_corpus_stats
        dolma_meta = curate_all_variants("dolma", get_corpus_stream("dolma"), CONFIG.corpus_root)
        fineweb_meta = curate_all_variants("fineweb", get_corpus_stream("fineweb"), CONFIG.corpus_root)
        all_variants = dolma_meta + fineweb_meta
        state["variant_metadata"] = all_variants
        state["stages_completed"].append("curate")
        save_stage_state(state, _STAGE_FILE)
        log_corpus_stats(all_variants)

    # Stage 2: Preprocess
    if _should_run("preprocess") and "preprocess" not in completed:
        logger.info("=== Stage: preprocess ===")
        from preprocess import preprocess_all_variants
        all_variants = state.get("variant_metadata", [])
        all_variants = preprocess_all_variants(all_variants, CONFIG.neox_repo)
        state["variant_metadata"] = all_variants
        state["stages_completed"].append("preprocess")
        save_stage_state(state, _STAGE_FILE)

    # Stage 3: Train
    if _should_run("train") and "train" not in completed:
        logger.info("=== Stage: train ===")
        from train import run_all_training
        all_variants = state.get("variant_metadata", [])
        run_records = run_all_training(all_variants)
        state["run_records"] = run_records
        state["stages_completed"].append("train")
        save_stage_state(state, _STAGE_FILE)

    # Stage 4: Evaluate
    if _should_run("evaluate") and "evaluate" not in completed:
        logger.info("=== Stage: evaluate ===")
        from evaluate import evaluate_all_checkpoints, save_results
        run_records = state.get("run_records", [])
        results = evaluate_all_checkpoints(run_records, CONFIG.eval_root)
        save_results(results, CONFIG.results_csv, CONFIG.results_parquet)
        state["stages_completed"].append("evaluate")
        save_stage_state(state, _STAGE_FILE)

    # Stage 5: Analyze
    if _should_run("analyze") and "analyze" not in completed:
        logger.info("=== Stage: analyze ===")
        from analyze import run_full_analysis
        analysis_results = run_full_analysis(CONFIG.results_csv)
        state["analysis_results"] = {
            k: v for k, v in analysis_results.items()
            if k != "anova_table"
        }
        state["stages_completed"].append("analyze")
        save_stage_state(state, _STAGE_FILE)

    # Stage 6: Visualize
    if _should_run("visualize") and "visualize" not in completed:
        logger.info("=== Stage: visualize ===")
        from visualize import generate_all_figures
        import pandas as pd
        df = pd.read_csv(CONFIG.results_csv)
        all_variants = state.get("variant_metadata", [])
        generate_all_figures(df, all_variants, CONFIG.figures_dir)
        state["stages_completed"].append("visualize")
        save_stage_state(state, _STAGE_FILE)

    logger.info(f"Pipeline complete. Stages: {state['stages_completed']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="all",
                        choices=["curate", "preprocess", "train", "evaluate", "analyze", "visualize", "all"])
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()
    run_pipeline(stage=args.stage, resume=not args.no_resume)
