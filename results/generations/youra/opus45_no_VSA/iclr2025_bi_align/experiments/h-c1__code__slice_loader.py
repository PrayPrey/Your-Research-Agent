import sys
import os
import subprocess
import pickle
import tempfile


def load_disagreement_slice():
    """
    Run H-M2 pipeline in subprocess to avoid sys.path conflicts.
    Returns (hl_texts, lh_texts): high-BAI/low-reward, low-BAI/high-reward.
    """
    _here = os.path.dirname(os.path.abspath(__file__))
    _h_m2_path = os.path.abspath(os.path.join(_here, "..", "..", "h-m2", "code"))
    _h_e1_path = os.path.abspath(os.path.join(_here, "..", "..", "h-e1", "code"))

    script = f'''
import sys
import os
import pickle
import numpy as np

sys.path.insert(0, "{_h_m2_path}")
sys.path.insert(0, "{_h_e1_path}")

from data import load_hh_rlhf, load_reward_bench_safety
from bai import train_proxy_detectors, compute_bai_scores
from reward import load_reward_model, compute_reward_scores
from analysis import compute_disagreement_rate

print("Loading HH-RLHF responses...")
hh_texts = load_hh_rlhf()
print(f"Loaded {{len(hh_texts)}} HH-RLHF responses")

print("Loading RewardBench Safety responses...")
rb_texts = load_reward_bench_safety()
print(f"Loaded {{len(rb_texts)}} RewardBench Safety responses")

responses = hh_texts + rb_texts
print(f"Total responses: {{len(responses)}}")

print("Training proxy detectors...")
detectors = train_proxy_detectors()

print("Computing BAI scores...")
bai_scores = compute_bai_scores(responses, detectors)

print("Loading reward model...")
model, tokenizer = load_reward_model()

print("Computing reward scores...")
prompts = [""] * len(responses)
reward_scores = compute_reward_scores(prompts, responses, model, tokenizer)

print("Computing disagreement rate...")
result = compute_disagreement_rate(np.array(bai_scores), np.array(reward_scores))

bai_z = result["bai_z"]
reward_z = result["reward_z"]
q_bounds = result["q_bounds"]

hl_mask = (bai_z >= q_bounds["q75_bai"]) & (reward_z <= q_bounds["q25_rw"])
lh_mask = (bai_z <= q_bounds["q25_bai"]) & (reward_z >= q_bounds["q75_rw"])

hl_texts = [responses[i] for i in np.where(hl_mask)[0]]
lh_texts = [responses[i] for i in np.where(lh_mask)[0]]

print(f"Disagreement rate: {{result['disagreement_rate']:.2%}}")
print(f"High-BAI/Low-Reward (HL): {{len(hl_texts)}}")
print(f"Low-BAI/High-Reward (LH): {{len(lh_texts)}}")

output = sys.argv[1]
with open(output, "wb") as f:
    pickle.dump((hl_texts, lh_texts), f)
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        output_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path, output_path],
            capture_output=False,
            check=True,
        )

        with open(output_path, "rb") as f:
            hl_texts, lh_texts = pickle.load(f)

        return hl_texts, lh_texts

    finally:
        os.unlink(script_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


if __name__ == "__main__":
    hl, lh = load_disagreement_slice()
    print(f"\nSample HL text: {hl[0][:100]}...")
