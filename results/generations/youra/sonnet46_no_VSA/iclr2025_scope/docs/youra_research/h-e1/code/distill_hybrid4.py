"""Build and fine-tune Hybrid-4 model via MOHAWK with full attention at layers 14-17."""
import os
import sys
import subprocess
from pathlib import Path

CODE_DIR = Path(__file__).parent
HYPOTHESIS_DIR = CODE_DIR.parent
MOHAWK_REPO = str(HYPOTHESIS_DIR / "repos" / "mohawk")
sys.path.insert(0, MOHAWK_REPO)

from config import (
    TEACHER_MODEL, CHECKPOINTS_DIR, HYBRID4_KEPT_LAYERS, HYBRID4_STAGE3_TOKENS,
    MOHAWK_LR, MOHAWK_BATCH, MOHAWK_SEED, HF_CACHE, N_GPUS,
)

HYBRID4_KEPT_LAYERS = list(HYBRID4_KEPT_LAYERS)  # e.g. [14, 15, 16, 17]


def _write_hybrid4_config(
    output_path: str,
    mohawk_ssm_checkpoint: str,
    teacher_path: str,
    n_tokens: float,
    lr: float,
    batch_size: int,
    seed: int,
) -> str:
    """Write MOHAWK Stage 3 hybrid config with attention at layers 14-17."""
    # Build Blocks spec: groups of contiguous layer types
    # Layers 0-13: pure SSM (32 heads → 0 attention heads)
    # Layers 14-17: full attention (32 heads)
    # Layers 18-31: pure SSM (0 attention heads)
    attn_layers = set(HYBRID4_KEPT_LAYERS)
    n_layers = 32

    block_input = "{resid_dropout: 0.0, mlp_intermediate_size: 14336, mlp_act_fn: 'silu', norm_epsilon: !!float 1e-5}"
    ssm_input = ("{d_state: 64, n_qk_heads: 32, n_v_heads: 32, expand: 1, chunk_size: 128, "
                 "headdim: 128, activation: identity, use_ref_impl: false, bias: false, "
                 "norm_cls: none, initializer: {a_log: default, x: default, B: default, "
                 "C: default, D: default, z: default, out: default, convolution: identity}}")
    rope_input = ("{factor: 8.0, low_freq_factor: 1.0, high_freq_factor: 4.0, "
                  "original_max_position_embeddings: 8192, rope_type: llama3}")

    # Build groups of (start, end, n_attn_heads)
    groups = []
    i = 0
    while i < n_layers:
        is_attn = (i in attn_layers)
        j = i
        while j < n_layers and (j in attn_layers) == is_attn:
            j += 1
        n_heads = 32 if is_attn else 0
        groups.append((i, j, n_heads))
        i = j

    blocks_yaml = ""
    for start, end, n_heads in groups:
        count = end - start
        blocks_yaml += f"""
    - name: SSDBlock
      n_layers: {count}
      input: {block_input}
      ssm_layer:
        name: DiscreteMamba2
        input: {ssm_input}
      attn_layer:
        name: LlamaAttention
        input:
          num_attention_heads: {n_heads}
          attention_bias: false
          head_dim: 128
          _attn_implementation: flash_attention_2
          rope_theta: 500000
          max_position_embeddings: 131072
          rope_scaling: {rope_input}
"""

    # Compute training steps
    accumulation_steps = max(1, batch_size // (8 * N_GPUS))
    effective_batch = 8 * N_GPUS * accumulation_steps

    mohawk_repo_path = str(HYPOTHESIS_DIR / "repos" / "mohawk")
    save_dir = str(CHECKPOINTS_DIR / "hybrid4" / "stage3")
    tmp_dir = str(CHECKPOINTS_DIR / "hybrid4" / "tmp_stage3")

    config = f"""# Hybrid-4: MOHAWK-SSM + LLaMA attention at layers {HYBRID4_KEPT_LAYERS}
LOAD:
- {mohawk_repo_path}/configs/Llama/8B/bases/teacher.yaml
- {mohawk_repo_path}/configs/Llama/8B/bases/optimizer.yaml
- {mohawk_repo_path}/configs/Llama/8B/bases/train.yaml
- {mohawk_repo_path}/configs/management.yaml

DistillConfig:
  name: h-e1-hybrid4
  type: supervised

ComponentsConfig:
  name: LayeredMambaLM
  input: {{vocab_size: 128256, tie_embeddings: true, pad_vocab_size_multiple: 8, lm_head_bias: false}}
  MixerModel:
    name: LlamaModel
    input: {{d_model: 4096, n_layer: {n_layers}, lm_head_prenorm: rms, norm_epsilon: !!float 1e-5}}
    Blocks:{blocks_yaml}

TeacherConfig:
  dir: {teacher_path}
  model_dtype: bfloat16
  mixed_precision: true

TrainConfig:
  seed: {seed}
  n_tokens: !!float {n_tokens:.2e}
  effective_batch_size: {effective_batch}
  mixed_precision: true
  model_dtype: bfloat16
  activation_checkpointing: true
  tokenizer: {teacher_path}

TrainDataConfig:
  loaders: [HFDataset, Tokenize, PackingDataLoader, TorchDataLoader]
  HFDataset:
    path: monology/pile-uncopyrighted
    streaming: true
    split: train
  Tokenize:
    tokenizer: {teacher_path}
    collate_type: text
  PackingDataLoader:
    max_seq_len: 2048
  TorchDataLoader:
    num_workers: 4
    batch_size: 8

OptimizerConfig:
  optimizer: AdamW
  lr: {lr}
  betas: [0.9, 0.999]
  weight_decay: 0.1
  scheduler:
    name: wsd
    warmup_steps: 500
    decay_steps: 0.1
    min_lr: !!float 1.0e-8

ManagementConfig:
  wandb:
    project: "youra-h-e1"
    entity: "anonymous"
  paths:
    base_dir: {str(CHECKPOINTS_DIR / "hybrid4")}
    save_dir: {save_dir}
    tmp_dir: {tmp_dir}
  env_vars:
    WANDB_MODE: "disabled"
    HF_TOKEN: ""
    LOGURU_LEVEL: "INFO"
    NCCL_DEBUG: "WARN"

LoadConfig:
  model:
    - null
    - path: {mohawk_ssm_checkpoint}
      strict: false
      allow_missing_keys: true
      allow_unexpected_keys: true
    - path: {teacher_path}
      strict: false
      allow_missing_keys: true
      allow_unexpected_keys: true
      rename:
        'model.': 'backbone.'
        'self_attn.': 'mixer.self_attn.'
        'module.': ''
        'embed_tokens.': 'embedding.'
        '.norm.': '.final_layernorm.'
      white_list:
        - self_attn
"""
    with open(output_path, "w") as f:
        f.write(config)
    return output_path


def run_hybrid4_pipeline(
    mohawk_ssm_checkpoint: str,
    teacher_path: str = TEACHER_MODEL,
    output_dir: str | None = None,
    n_tokens: float = HYBRID4_STAGE3_TOKENS,
    lr: float | None = None,
    batch_size: int | None = None,
    seed: int = MOHAWK_SEED,
) -> str:
    """Build Hybrid-4 by fine-tuning MOHAWK-SSM with attention at layers 14-17."""
    if output_dir is None:
        output_dir = str(CHECKPOINTS_DIR / "hybrid4" / "stage3")
    if lr is None:
        lr = MOHAWK_LR["stage3"]
    if batch_size is None:
        batch_size = MOHAWK_BATCH["stage3"]

    os.makedirs(output_dir, exist_ok=True)
    config_path = str(CHECKPOINTS_DIR / "hybrid4" / "hybrid4_config.yaml")
    os.makedirs(str(CHECKPOINTS_DIR / "hybrid4"), exist_ok=True)

    _write_hybrid4_config(
        output_path=config_path,
        mohawk_ssm_checkpoint=mohawk_ssm_checkpoint,
        teacher_path=teacher_path,
        n_tokens=n_tokens,
        lr=lr,
        batch_size=batch_size,
        seed=seed,
    )

    torchrun = str(Path(sys.executable).parent / "torchrun")
    cmd = [
        torchrun,
        f"--nproc_per_node={N_GPUS}",
        "--master_port", "29503",
        "run.py",
        "--config", config_path,
    ]

    env = os.environ.copy()
    env["HF_HOME"] = HF_CACHE
    env["HF_DATASETS_CACHE"] = str(Path(HF_CACHE) / "datasets")

    print(f"[Hybrid-4] Launching: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=MOHAWK_REPO, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Hybrid-4 training failed with code {result.returncode}")

    # Find final checkpoint
    save_dir = str(CHECKPOINTS_DIR / "hybrid4" / "stage3")
    ckpts = sorted(Path(save_dir).glob("step_*"), key=lambda p: int(p.name.split("_")[1]))
    if ckpts:
        return str(ckpts[-1])
    if (Path(save_dir) / "model.safetensors").exists():
        return save_dir
    raise RuntimeError(f"No checkpoint found in {save_dir}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--mohawk-checkpoint", type=str, required=True)
    p.add_argument("--output-dir", type=str, default=str(CHECKPOINTS_DIR / "hybrid4"))
    args = p.parse_args()

    final_ckpt = run_hybrid4_pipeline(
        mohawk_ssm_checkpoint=args.mohawk_checkpoint,
        output_dir=args.output_dir,
    )
    print(f"Hybrid-4 complete: {final_ckpt}")
