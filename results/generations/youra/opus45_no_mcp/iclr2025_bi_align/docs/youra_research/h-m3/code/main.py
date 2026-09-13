"""H-M3: Representation Separation Analysis for Bidirectional Tasks.

Tests whether single scalar reward training causes models to miss bidirectional
adaptation nuance by analyzing hidden state representations.

Gate: SHOULD_WORK
Pass: separation_score < 0.1 OR probe_accuracy < 0.6
Fail: separation_score > 0.3 AND probe_accuracy > 0.8
"""

import sys
import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from tqdm import tqdm

# Add h-m1 code to path
H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))

from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.manifold import TSNE
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Import from H-M1
from data import load_all_tasks, Task

# Config
MODELS = [
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.2",
]
PRIMARY_MODEL_IDX = 0
BATCH_SIZE = 8
SEED = 42
SEP_PASS = 0.1
PROBE_PASS = 0.6
SEP_FAIL = 0.3
PROBE_FAIL = 0.8

OUTPUT_DIR = Path(__file__).parent / "outputs"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
H_M1_RESULTS = H_M1_CODE / "outputs" / "results.json"


def set_seed(seed: int = 42):
    torch.manual_seed(seed)
    np.random.seed(seed)


def load_task_classifications() -> Tuple[List[str], List[str], np.ndarray]:
    """Load H-M1 task type labels and raw task texts."""
    with open(H_M1_RESULTS) as f:
        hm1 = json.load(f)

    type_map = {t["task_id"]: t["task_type"] for t in hm1["per_task"]}

    tasks = load_all_tasks()
    task_ids = []
    prompts = []
    labels = []

    for task in tasks:
        tid = task["task_id"]
        if tid in type_map:
            task_ids.append(tid)
            prompts.append(task["question"])
            labels.append(0 if type_map[tid] == "A" else 1)

    print(f"Loaded {len(task_ids)} tasks with type labels")
    print(f"  Type A: {sum(1 for l in labels if l == 0)}")
    print(f"  Type B: {sum(1 for l in labels if l == 1)}")

    return task_ids, prompts, np.array(labels)


def load_model_with_hidden_states(model_id: str):
    """Load model with output_hidden_states=True."""
    print(f"Loading {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        output_hidden_states=True
    )
    model.eval()
    return model, tokenizer


def extract_hidden_states(
    model, tokenizer, prompts: List[str], batch_size: int = 8
) -> torch.Tensor:
    """Extract last-layer, last-token hidden states."""
    all_hidden = []

    for i in tqdm(range(0, len(prompts), batch_size), desc="Extracting"):
        batch = prompts[i:i+batch_size]
        enc = tokenizer(
            batch, return_tensors="pt", padding=True,
            truncation=True, max_length=512
        )
        enc = {k: v.to(model.device) for k, v in enc.items()}

        with torch.no_grad():
            out = model(**enc, output_hidden_states=True)

        last_layer = out.hidden_states[-1]  # [B, T, H]
        pooled = last_layer[:, -1, :]  # [B, H] last token
        all_hidden.append(pooled.float().cpu())

    return torch.cat(all_hidden, dim=0)


def compute_separation_score(
    type_a_hidden: torch.Tensor, type_b_hidden: torch.Tensor
) -> Dict[str, float]:
    """Compute intra/inter cosine similarity separation."""
    import torch.nn.functional as F

    # Normalize
    type_a_norm = F.normalize(type_a_hidden, dim=-1)
    type_b_norm = F.normalize(type_b_hidden, dim=-1)

    # Intra-type similarity (within A)
    sim_a = type_a_norm @ type_a_norm.T
    mask_a = ~torch.eye(len(type_a_norm), dtype=torch.bool)
    intra_a = sim_a[mask_a].mean().item()

    # Intra-type similarity (within B)
    sim_b = type_b_norm @ type_b_norm.T
    mask_b = ~torch.eye(len(type_b_norm), dtype=torch.bool)
    intra_b = sim_b[mask_b].mean().item()

    # Inter-type similarity (between A and B)
    inter = (type_a_norm @ type_b_norm.T).mean().item()

    # Weighted intra mean
    n_a, n_b = len(type_a_norm), len(type_b_norm)
    intra_mean = (intra_a * n_a + intra_b * n_b) / (n_a + n_b)

    separation = intra_mean - inter

    return {
        "intra_a": intra_a,
        "intra_b": intra_b,
        "intra_mean": intra_mean,
        "inter_mean": inter,
        "separation_score": separation
    }


def train_linear_probe(
    hidden_states: np.ndarray, labels: np.ndarray, cv: int = 5
) -> Dict[str, float]:
    """Train LinearSVC with stratified k-fold CV."""
    scaler = StandardScaler()
    X = scaler.fit_transform(hidden_states)

    clf = LinearSVC(max_iter=5000, random_state=SEED)
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=SEED)

    scores = cross_val_score(clf, X, labels, cv=skf, scoring="accuracy")

    return {
        "probe_accuracy": scores.mean(),
        "probe_std": scores.std(),
        "fold_scores": scores.tolist()
    }


def evaluate_gate(sep: float, probe: float) -> Tuple[bool, bool, str]:
    """Evaluate SHOULD_WORK gate condition."""
    gate_pass = (sep < SEP_PASS) or (probe < PROBE_PASS)
    gate_fail = (sep > SEP_FAIL) and (probe > PROBE_FAIL)

    if gate_pass:
        reason = f"PASS: sep={sep:.4f}<{SEP_PASS} OR probe={probe:.4f}<{PROBE_PASS}"
    elif gate_fail:
        reason = f"FAIL: sep={sep:.4f}>{SEP_FAIL} AND probe={probe:.4f}>{PROBE_FAIL}"
    else:
        reason = f"INCONCLUSIVE: sep={sep:.4f}, probe={probe:.4f}"

    return gate_pass, gate_fail, reason


def generate_tsne_plot(
    hidden_states: np.ndarray, labels: np.ndarray, model_name: str
):
    """Generate t-SNE visualization."""
    print(f"Generating t-SNE for {model_name}...")

    tsne = TSNE(n_components=2, random_state=SEED, perplexity=30)
    embed = tsne.fit_transform(hidden_states)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        embed[:, 0], embed[:, 1],
        c=labels, cmap='coolwarm', alpha=0.6, s=10
    )
    plt.colorbar(scatter, label='Task Type (0=A, 1=B)')
    plt.title(f"Hidden State t-SNE: {model_name.split('/')[-1]}")
    plt.xlabel("t-SNE 1")
    plt.ylabel("t-SNE 2")

    safe_name = model_name.replace("/", "_")
    plt.savefig(FIGURES_DIR / f"tsne_{safe_name}.png", dpi=150, bbox_inches='tight')
    plt.close()


def generate_gate_metrics_plot(results: Dict):
    """Generate gate metrics bar chart."""
    models = list(results["per_model"].keys())
    seps = [results["per_model"][m]["separation_score"] for m in models]
    probes = [results["per_model"][m]["probe_accuracy"] for m in models]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    bars1 = ax.bar(x - width/2, seps, width, label='Separation Score', color='steelblue')
    bars2 = ax.bar(x + width/2, probes, width, label='Probe Accuracy', color='coral')

    ax.axhline(y=SEP_PASS, color='steelblue', linestyle='--', alpha=0.7, label=f'Sep Pass ({SEP_PASS})')
    ax.axhline(y=PROBE_PASS, color='coral', linestyle='--', alpha=0.7, label=f'Probe Pass ({PROBE_PASS})')

    ax.set_xlabel('Model')
    ax.set_ylabel('Score')
    ax.set_title('H-M3 Gate Metrics: Representation Separation Analysis')
    ax.set_xticks(x)
    ax.set_xticklabels([m.split('/')[-1] for m in models], rotation=15, ha='right')
    ax.legend()
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "gate_metrics.png", dpi=150, bbox_inches='tight')
    plt.close()


def run_experiment():
    """Run full H-M3 experiment."""
    set_seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-M3: Representation Separation Analysis")
    print("=" * 60)

    # Load task classifications
    task_ids, prompts, labels = load_task_classifications()

    results = {
        "hypothesis": "H-M3",
        "title": "Models Learn Single Reward Signal Missing Bidirectional Nuance",
        "gate_type": "SHOULD_WORK",
        "timestamp": datetime.now().isoformat(),
        "per_model": {},
        "aggregate": {}
    }

    primary_hidden = None

    for i, model_id in enumerate(MODELS):
        print(f"\n{'='*60}")
        print(f"Processing {model_id} ({i+1}/{len(MODELS)})")
        print("=" * 60)

        model, tokenizer = load_model_with_hidden_states(model_id)
        hidden = extract_hidden_states(model, tokenizer, prompts, BATCH_SIZE)

        # Split by type
        type_a_hidden = hidden[labels == 0]
        type_b_hidden = hidden[labels == 1]

        print(f"Hidden states: {hidden.shape}")
        print(f"  Type A: {type_a_hidden.shape}")
        print(f"  Type B: {type_b_hidden.shape}")

        # Separation analysis
        sep_result = compute_separation_score(type_a_hidden, type_b_hidden)
        print(f"Separation score: {sep_result['separation_score']:.4f}")

        # Linear probe
        probe_result = train_linear_probe(hidden.numpy(), labels)
        print(f"Probe accuracy: {probe_result['probe_accuracy']:.4f}")

        # Gate evaluation
        gate_pass, gate_fail, reason = evaluate_gate(
            sep_result["separation_score"], probe_result["probe_accuracy"]
        )
        print(f"Gate: {reason}")

        results["per_model"][model_id] = {
            **sep_result,
            **probe_result,
            "gate_pass": gate_pass,
            "gate_fail": gate_fail,
            "gate_reason": reason,
            "n_type_a": int(type_a_hidden.shape[0]),
            "n_type_b": int(type_b_hidden.shape[0])
        }

        # Store primary model hidden states for t-SNE
        if i == PRIMARY_MODEL_IDX:
            primary_hidden = hidden.numpy()
            generate_tsne_plot(primary_hidden, labels, model_id)

        # Free memory
        del model, tokenizer, hidden
        torch.cuda.empty_cache()

    # Aggregate results (primary model decision)
    primary = MODELS[PRIMARY_MODEL_IDX]
    pm = results["per_model"][primary]

    results["aggregate"] = {
        "primary_model": primary,
        "separation_score": pm["separation_score"],
        "probe_accuracy": pm["probe_accuracy"],
        "gate_pass": pm["gate_pass"],
        "gate_fail": pm["gate_fail"],
        "gate_result": "PASS" if pm["gate_pass"] else ("FAIL" if pm["gate_fail"] else "INCONCLUSIVE"),
        "gate_reason": pm["gate_reason"],
        "total_tasks": len(task_ids),
        "type_a_count": int(sum(labels == 0)),
        "type_b_count": int(sum(labels == 1)),
        "cross_model_separation": {
            m: results["per_model"][m]["separation_score"] for m in MODELS
        },
        "cross_model_probe": {
            m: results["per_model"][m]["probe_accuracy"] for m in MODELS
        }
    }

    # Generate gate metrics plot
    generate_gate_metrics_plot(results)

    # Save results
    with open(OUTPUT_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Primary Model: {primary}")
    print(f"Separation Score: {pm['separation_score']:.4f}")
    print(f"Probe Accuracy: {pm['probe_accuracy']:.4f}")
    print(f"Gate Result: {results['aggregate']['gate_result']}")
    print(f"Reason: {pm['gate_reason']}")
    print(f"\nSaved to: {OUTPUT_DIR / 'results.json'}")
    print(f"Figures: {FIGURES_DIR}")

    return results


if __name__ == "__main__":
    results = run_experiment()
    print("\n[EXPERIMENT COMPLETE]")
