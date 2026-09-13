"""Run only stochastic inference (greedy already complete)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config
from data import load_halueval_qa
from inference import load_llm, run_stochastic_inference

cfg = get_config()
print(f"Loading data...")
examples = load_halueval_qa(cfg)
print(f"Loaded {len(examples)} examples")

print(f"Loading model {cfg.llm_model_id} with dtype={cfg.llm_dtype}...")
model, tokenizer = load_llm(cfg)
print("Model loaded.")

print("Running stochastic inference (resume-enabled)...")
run_stochastic_inference(examples, model, tokenizer, cfg, resume=True)
print("Stochastic inference complete.")
