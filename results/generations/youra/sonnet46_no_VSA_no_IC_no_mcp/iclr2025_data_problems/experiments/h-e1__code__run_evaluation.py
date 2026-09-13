"""E2: Run lm-eval CLI for all 8 Pythia model variants; resume-safe."""
import json
import subprocess
import sys
from glob import glob
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CHECKPOINT_MAP_FILE = BASE_DIR / "checkpoint_map.json"
RESULTS_DIR = BASE_DIR / "results"

BENCHMARKS: list[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
FEWSHOT: dict[str, int] = {"mmlu": 5, "hellaswag": 0, "arc_challenge": 25, "winogrande": 5}
DTYPE: str = "float16"
BATCH_SIZE: str = "auto:4"


def build_lmeval_cmd(
    model_id: str,
    revision: str,
    output_path: str,
    benchmarks: list[str] = BENCHMARKS,
    fewshot: dict[str, int] = FEWSHOT,
    dtype: str = DTYPE,
    batch_size: str = BATCH_SIZE,
) -> list[str]:
    tasks_str = ",".join(benchmarks)
    # lm-eval 0.4.x: --num_fewshot takes a single int applied to all tasks,
    # or per-task via task configs. Use --apply_chat_template=False and pass
    # per-task fewshot via task name with :k suffix is not standard in 0.4.
    # Instead use separate evaluations per task to set num_fewshot correctly.
    # For simplicity: pass num_fewshot as the max across tasks (5 is harmless
    # for tasks that use fewer) — lm-eval respects task-level defaults unless
    # overridden, so this is fine for hellaswag (0-shot is its default).
    #
    # Correct approach for 0.4.x: pass --num_fewshot per task using task config.
    # We use the simple approach: separate calls per benchmark, each with correct shots.
    # This function is called per-benchmark (one benchmark per call).
    assert len(benchmarks) == 1, "Call build_lmeval_cmd with one benchmark at a time"
    task = benchmarks[0]
    num_shots = fewshot[task]

    model_args = f"pretrained={model_id},revision={revision},dtype={dtype},trust_remote_code=True"
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", model_args,
        "--tasks", task,
        "--num_fewshot", str(num_shots),
        "--batch_size", batch_size,
        "--output_path", output_path,
        "--log_samples",
    ]
    return cmd


def result_exists(output_path: str) -> bool:
    matches = glob(str(Path(output_path) / "**" / "*.json"), recursive=True)
    # Filter out samples files, keep results files
    result_files = [f for f in matches if "samples_" not in Path(f).name]
    return len(result_files) > 0


def evaluate_model(
    model_id: str,
    revision: str,
    output_dir: str,
    benchmarks: list[str] = BENCHMARKS,
    fewshot: dict[str, int] = FEWSHOT,
    skip_existing: bool = True,
) -> None:
    for task in benchmarks:
        task_output_dir = str(Path(output_dir) / task)
        if skip_existing and result_exists(task_output_dir):
            print(f"  [SKIP] {model_id} {revision} {task} — results exist")
            continue
        cmd = build_lmeval_cmd(
            model_id=model_id,
            revision=revision,
            output_path=task_output_dir,
            benchmarks=[task],
            fewshot=fewshot,
        )
        print(f"  [RUN] {model_id} {revision} {task}")
        print(f"    cmd: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                check=True,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            last_lines = "\n".join((e.stderr or "").splitlines()[-20:])
            print(f"  [FAIL] lm_eval exited non-zero:\n{last_lines}", file=sys.stderr)
            if "CUDA out of memory" in (e.stderr or ""):
                print("  [OOM] Reduce BATCH_SIZE (currently auto:4) and retry", file=sys.stderr)
            raise


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_map = json.loads(CHECKPOINT_MAP_FILE.read_text())
    sizes = list(checkpoint_map.keys())

    model_variants = (
        [(f"EleutherAI/pythia-{s}", f"step{checkpoint_map[s]['pile_step']}", "pile") for s in sizes]
        + [(f"EleutherAI/pythia-{s}-deduped", f"step{checkpoint_map[s]['dedup_step']}", "dedup") for s in sizes]
    )

    total = len(model_variants)
    for i, (hf_id, revision, corpus) in enumerate(model_variants, 1):
        slug = hf_id.replace("/", "-")
        output_dir = str(RESULTS_DIR / f"{slug}-{revision}")
        print(f"\n[{i}/{total}] {hf_id} ({corpus}) revision={revision}")
        evaluate_model(hf_id, revision, output_dir)

    print("\nAll 8 model variants evaluated.")


if __name__ == "__main__":
    main()
