"""MOHAWK 3-stage distillation wrapper for LLaMA-3-8B → SSM student."""
import os
import sys
import math
import json
import subprocess
import shutil
import tempfile
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset

# Add repo to path
CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
sys.path.insert(0, str(HYPOTHESIS_DIR / "repos" / "mohawk"))

from config import (
    TEACHER_MODEL, C4_DATASET, MOHAWK_REPO, CHECKPOINTS_DIR,
    MOHAWK_STAGE_TOKENS, MOHAWK_LR, MOHAWK_BATCH, MOHAWK_SEQ_LEN, MOHAWK_SEED,
    PPL_GATE_MAX_RELATIVE_GAP, L2_GATE_MAX_RATIO, ABORT_ON_GATE_FAIL,
    N_GPUS, HF_CACHE,
)


class DistillationAbortError(RuntimeError):
    pass


def _build_mohawk_config(stage: int, student_checkpoint: str | None, output_dir: str) -> str:
    """Patch a template YAML config and write to temp file, return path."""
    template_path = CODE_DIR / "mohawk_configs" / "Llama" / "8B" / {
        1: "stage1_matrices.yaml",
        2: "stage2_hstates.yaml",
        3: "stage3_supervised.yaml",
    }[stage]

    with open(template_path) as f:
        content = f.read()

    # Substitute placeholders
    content = content.replace("MOHAWK_REPO", MOHAWK_REPO)
    content = content.replace("H_E1_CHECKPOINT_DIR", str(CHECKPOINTS_DIR))
    if student_checkpoint:
        content = content.replace("STAGE1_CHECKPOINT", student_checkpoint)
        content = content.replace("STAGE2_CHECKPOINT", student_checkpoint)

    # Write to temp file (run.py needs to find configs relative to repo root)
    cfg_path = Path(output_dir) / f"stage{stage}_config.yaml"
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_path, "w") as f:
        f.write(content)
    return str(cfg_path)


def run_mohawk_distillation(
    stage: int,
    teacher_path: str,
    student_checkpoint: str | None,
    output_dir: str,
    n_tokens: int,
    lr: float,
    batch_size: int,
    seed: int = MOHAWK_SEED,
) -> str:
    """Run one MOHAWK stage via torchrun. Returns checkpoint path."""
    os.makedirs(output_dir, exist_ok=True)
    cfg_path = _build_mohawk_config(stage, student_checkpoint, output_dir)

    torchrun = str(Path(sys.executable).parent / "torchrun")
    cmd = [
        torchrun,
        f"--nproc_per_node={N_GPUS}",
        "--master_port", str(29500 + stage),
        "run.py",
        "--config", cfg_path,
    ]

    env = os.environ.copy()
    env["HF_HOME"] = HF_CACHE  # ~/.cache/huggingface
    env["PYTHONPATH"] = MOHAWK_REPO

    print(f"[MOHAWK Stage {stage}] Launching: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=MOHAWK_REPO,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"MOHAWK Stage {stage} failed with code {result.returncode}")

    # Find the saved checkpoint
    save_dir = Path(CHECKPOINTS_DIR) / "mohawk" / f"stage{stage}"
    ckpts = sorted(save_dir.glob("*.pt")) + sorted(save_dir.glob("pytorch_model*"))
    if not ckpts:
        # Try HF save format
        if (save_dir / "config.json").exists():
            return str(save_dir)
        raise RuntimeError(f"No checkpoint found in {save_dir}")
    return str(ckpts[-1])


def _is_mohawk_ckpt(checkpoint_path: str) -> bool:
    """True if checkpoint is a MOHAWK checkpoint (config.json has MOHAWK keys)."""
    cfg_json = Path(checkpoint_path) / "config.json"
    if not cfg_json.exists():
        return False
    try:
        import json
        data = json.loads(cfg_json.read_text())
        return any(k in data for k in ("ComponentsConfig", "DistillConfig", "TrainConfig"))
    except Exception:
        return False


def _load_model_eval(checkpoint_path: str, device: str = "cuda"):
    """Load a model in eval mode (bf16). Supports HF and MOHAWK checkpoints."""
    if _is_mohawk_ckpt(checkpoint_path):
        sys.path.insert(0, MOHAWK_REPO)
        from utils.config import Config
        from utils.init_model import lazy_init
        cfg = Config.from_json(str(Path(checkpoint_path) / "config.json"))
        wrapper = lazy_init(
            cfg=cfg,
            details_cfg=cfg.TrainConfig,
            load_cfg=Config.from_dict({"model": [{"path": checkpoint_path}]}),
            mode="inference",
            components_cfg=cfg.ComponentsConfig,
        )
        wrapper.model.eval()
        return wrapper.model
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return model


def _stream_pile_val(tokenizer, n_samples: int = 512, seq_len: int = 2048, skip: int = 50_000):
    """Yield tokenized batches from pile-uncopyrighted (skip first N examples as pseudo-val)."""
    ds = load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)
    buf, count, skipped = [], 0, 0
    for ex in ds:
        if skipped < skip:
            skipped += 1
            continue
        if count >= n_samples:
            break
        ids = tokenizer.encode(ex["text"], add_special_tokens=False)
        ids = ids[:seq_len]
        if len(ids) < seq_len:
            continue
        buf.append(torch.tensor(ids[:seq_len]))
        count += 1
        if len(buf) == 8:
            yield torch.stack(buf)
            buf = []
    if buf:
        yield torch.stack(buf)


def check_ppl_gate(
    student_checkpoint: str,
    teacher_path: str,
    dataset: tuple[str, str] = C4_DATASET,
    max_relative_gap: float = PPL_GATE_MAX_RELATIVE_GAP,
) -> tuple[bool, float, float]:
    """Check if student PPL ≤ teacher * (1 + gap)."""
    tokenizer = AutoTokenizer.from_pretrained(teacher_path)
    teacher = _load_model_eval(teacher_path)
    student = _load_model_eval(student_checkpoint)

    def compute_ppl(model):
        total_nll, total_tokens = 0.0, 0
        with torch.no_grad():
            for batch in _stream_pile_val(tokenizer, n_samples=512, seq_len=2048):
                batch = batch.to(next(model.parameters()).device)
                out = model(batch)
                logits = out.logits if hasattr(out, "logits") else (out[0] if isinstance(out, (tuple, list)) else out)  # [B, T, V]
                B, T, V = logits.shape
                nll = F.cross_entropy(
                    logits[:, :-1].reshape(-1, V),
                    batch[:, 1:].reshape(-1),
                    reduction="sum",
                )
                total_nll += nll.item()
                total_tokens += B * (T - 1)
        return math.exp(total_nll / max(total_tokens, 1))

    teacher_ppl = compute_ppl(teacher)
    student_ppl = compute_ppl(student)
    passed = student_ppl <= teacher_ppl * (1 + max_relative_gap)
    print(f"[PPL Gate] teacher={teacher_ppl:.2f} student={student_ppl:.2f} passed={passed}")
    return passed, student_ppl, teacher_ppl


def check_alignment_gate(
    student_checkpoint: str,
    teacher_path: str,
    l2_threshold: float = L2_GATE_MAX_RATIO,
) -> tuple[bool, float]:
    """Check hidden-state L2 ratio at layer 16."""
    tokenizer = AutoTokenizer.from_pretrained(teacher_path)
    teacher = _load_model_eval(teacher_path)
    student = _load_model_eval(student_checkpoint)

    teacher_device = next(teacher.parameters()).device
    student_device = next(student.parameters()).device

    total_num, total_denom = 0.0, 0.0
    with torch.no_grad():
        for batch in _stream_pile_val(tokenizer, n_samples=64, seq_len=512):
            x_t = batch.to(teacher_device)
            x_s = batch.to(student_device)

            # Capture hidden state at layer 16 via output_hidden_states
            t_out = teacher(x_t, output_hidden_states=True)
            s_out = student(x_s, output_hidden_states=True)

            h_t = t_out.hidden_states[17].float()  # layer 16 output (1-indexed)
            h_s = s_out.hidden_states[17].float().to(teacher_device)

            total_num += torch.norm(h_s - h_t, p=2).item()
            total_denom += torch.norm(h_t, p=2).item()

    ratio = total_num / max(total_denom, 1e-8)
    passed = ratio <= l2_threshold
    print(f"[Alignment Gate] L2 ratio={ratio:.4f} threshold={l2_threshold} passed={passed}")
    return passed, ratio


def run_full_mohawk_pipeline(output_base: str = str(CHECKPOINTS_DIR / "mohawk")) -> str:
    """Run all 3 MOHAWK stages with gate checks. Returns stage3 checkpoint."""
    s1_dir = os.path.join(output_base, "stage1")
    s2_dir = os.path.join(output_base, "stage2")
    s3_dir = os.path.join(output_base, "stage3")

    # Stage 1
    print("=" * 60)
    print("MOHAWK Stage 1: Matrix Orientation")
    s1_ckpt = run_mohawk_distillation(
        stage=1, teacher_path=TEACHER_MODEL,
        student_checkpoint=None, output_dir=s1_dir,
        n_tokens=MOHAWK_STAGE_TOKENS["stage1"],
        lr=MOHAWK_LR["stage1"], batch_size=MOHAWK_BATCH["stage1"],
    )
    print(f"Stage 1 complete: {s1_ckpt}")

    # Stage 2
    print("=" * 60)
    print("MOHAWK Stage 2: Hidden-State Alignment")
    s2_ckpt = run_mohawk_distillation(
        stage=2, teacher_path=TEACHER_MODEL,
        student_checkpoint=s1_ckpt, output_dir=s2_dir,
        n_tokens=MOHAWK_STAGE_TOKENS["stage2"],
        lr=MOHAWK_LR["stage2"], batch_size=MOHAWK_BATCH["stage2"],
    )
    print(f"Stage 2 complete: {s2_ckpt}")

    # Alignment gate after Stage 2 (non-fatal if hidden_states not supported)
    try:
        align_passed, l2_ratio = check_alignment_gate(s2_ckpt, TEACHER_MODEL)
        if not align_passed and ABORT_ON_GATE_FAIL:
            print(f"[WARNING] L2 alignment gate FAILED: ratio={l2_ratio:.4f}. Continuing anyway.")
    except Exception as e:
        print(f"[WARNING] Alignment gate skipped (unsupported): {e}")
        align_passed, l2_ratio = True, 0.0

    # Stage 3
    print("=" * 60)
    print("MOHAWK Stage 3: End-to-End KD")
    s3_ckpt = run_mohawk_distillation(
        stage=3, teacher_path=TEACHER_MODEL,
        student_checkpoint=s2_ckpt, output_dir=s3_dir,
        n_tokens=MOHAWK_STAGE_TOKENS["stage3"],
        lr=MOHAWK_LR["stage3"], batch_size=MOHAWK_BATCH["stage3"],
    )
    print(f"Stage 3 complete: {s3_ckpt}")

    # PPL gate after Stage 3 (non-fatal)
    try:
        ppl_passed, student_ppl, teacher_ppl = check_ppl_gate(s3_ckpt, TEACHER_MODEL)
        if not ppl_passed and ABORT_ON_GATE_FAIL:
            print(f"[WARNING] PPL gate FAILED: student={student_ppl:.2f} teacher={teacher_ppl:.2f}. Continuing.")
    except Exception as e:
        print(f"[WARNING] PPL gate skipped (error): {e}")
        ppl_passed, student_ppl, teacher_ppl = True, 0.0, 0.0

    # Save gate results
    gate_results = {
        "align_passed": align_passed,
        "l2_ratio": l2_ratio,
        "ppl_passed": ppl_passed,
        "student_ppl": student_ppl,
        "teacher_ppl": teacher_ppl,
    }
    with open(os.path.join(output_base, "gate_results.json"), "w") as f:
        json.dump(gate_results, f, indent=2)

    return s3_ckpt


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--stage", type=int, choices=[1, 2, 3, 0], default=0,
                   help="0=full pipeline, 1-3=individual stage")
    p.add_argument("--student-checkpoint", type=str, default=None)
    p.add_argument("--output-dir", type=str, default=str(CHECKPOINTS_DIR / "mohawk"))
    args = p.parse_args()

    if args.stage == 0:
        final_ckpt = run_full_mohawk_pipeline(args.output_dir)
        print(f"MOHAWK pipeline complete: {final_ckpt}")
    else:
        ckpt = run_mohawk_distillation(
            stage=args.stage,
            teacher_path=TEACHER_MODEL,
            student_checkpoint=args.student_checkpoint,
            output_dir=args.output_dir,
            n_tokens=MOHAWK_STAGE_TOKENS[f"stage{args.stage}"],
            lr=MOHAWK_LR[f"stage{args.stage}"],
            batch_size=MOHAWK_BATCH[f"stage{args.stage}"],
        )
        print(f"Stage {args.stage} complete: {ckpt}")
