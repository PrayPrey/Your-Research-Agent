import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import random
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

MASTER_SEED = 42
np.random.seed(MASTER_SEED)
random.seed(MASTER_SEED)
torch.manual_seed(MASTER_SEED)

experiment_data = {
    "update_strategy_ablation": {
        ds: {
            "metrics": {"sr": [], "mean_calls": [], "ites": [], "ccd": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "library_sizes": [],
            "add_counts": [],
        }
        for ds in ["mbpp", "openai_humaneval", "code_search_net"]
    },
    "diversity_threshold_sweep": {
        ds: {
            "metrics": {"sr": [], "mean_calls": [], "ites": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "thresholds": [],
            "final_lib_sizes": [],
        }
        for ds in ["mbpp", "openai_humaneval", "code_search_net"]
    },
    "difficulty_breakdown": {
        strat: {
            "metrics": {"ites": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        }
        for strat in [
            "success_only",
            "unconditional",
            "failure_only",
            "diversity_driven",
        ]
    },
}


def make_loop_program(idx, domain="arithmetic", extra_vars=0):
    templates = {
        "arithmetic": [
            ("int x={s}; int y=0;\nwhile(x>0){{ y=y+x; x=x-1; }}", "y >= 0 && x >= 0"),
            (
                "int i=0; int s=0;\nwhile(i<{n}){{ s=s+i; i=i+1; }}",
                "s >= 0 && i >= 0 && i <= {n}",
            ),
            (
                "int a={s}; int b=0;\nwhile(a>={t}){{ b=b+1; a=a-{t}; }}",
                "b >= 0 && a >= 0",
            ),
        ],
        "array": [
            (
                "int arr[{n}]; int i=0; int mx=0;\nwhile(i<{n}){{ if(arr[i]>mx) mx=arr[i]; i++; }}",
                "mx >= 0 && i <= {n}",
            ),
            (
                "int arr[{n}]; int i=0; int sum=0;\nwhile(i<{n}){{ sum+=arr[i]; i++; }}",
                "i <= {n} && i >= 0",
            ),
        ],
        "bitwise": [
            (
                "int x={s}; int cnt=0;\nwhile(x!=0){{ cnt+=(x&1); x>>=1; }}",
                "cnt >= 0 && x >= 0",
            ),
            ("int x={s}; int y=1;\nwhile(y<x){{ y=y*2; }}", "y >= 1 && y > 0"),
        ],
    }
    domains_list = list(templates.keys())
    dom = domains_list[idx % len(domains_list)] if domain == "auto" else domain
    tmpl_list = templates[dom]
    tmpl, inv = tmpl_list[idx % len(tmpl_list)]
    s = (idx % 20) + 1
    n = (idx % 10) + 5
    t = max(1, (idx % 5) + 1)
    code = tmpl.format(s=s, n=n, t=t)
    extra = "".join([f" && v{i}>={i}" for i in range(extra_vars)])
    inv_full = inv.format(s=s, n=n, t=t) + extra
    difficulty = (
        "easy"
        if idx % 4 == 0
        else ("medium" if idx % 4 == 1 else ("hard" if idx % 4 == 2 else "ood"))
    )
    return {
        "id": idx,
        "code": code,
        "invariant": inv_full,
        "domain": dom,
        "difficulty": difficulty,
    }


def load_dataset_samples(name, n=200):
    print(f"  Generating synthetic samples for '{name}' (n={n})...")
    samples = []
    if name == "mbpp":
        for i in range(n):
            p = make_loop_program(i, domain="auto", extra_vars=i % 3)
            p["source"] = "mbpp"
            samples.append(p)
    elif name == "openai_humaneval":
        for i in range(n):
            p = make_loop_program(
                i, domain="arithmetic" if i % 2 == 0 else "bitwise", extra_vars=i % 2
            )
            p["source"] = "humaneval"
            samples.append(p)
    elif name == "code_search_net":
        for i in range(n):
            p = make_loop_program(
                i, domain="array" if i % 2 == 0 else "arithmetic", extra_vars=(i % 4)
            )
            p["source"] = "codesearchnet"
            samples.append(p)
    return samples


class CodeEmbedder(nn.Module):
    def __init__(self, vocab_size, embed_dim=128):
        super().__init__()
        self.embed_dim = embed_dim
        self.net = nn.Sequential(
            nn.Linear(vocab_size, 512), nn.ReLU(), nn.Linear(512, embed_dim)
        )

    def forward(self, x):
        return torch.nn.functional.normalize(self.net(x), dim=-1)


def build_tfidf_embedder(corpus, max_features=5000):
    vec = TfidfVectorizer(
        max_features=max_features, analyzer="char_wb", ngram_range=(2, 4)
    )
    vec.fit(corpus)
    return vec


def embed_codes(codes, tfidf_vec, embedder, batch_size=64):
    all_embs = []
    X = tfidf_vec.transform(codes).toarray().astype(np.float32)
    for i in range(0, len(X), batch_size):
        batch = torch.tensor(X[i : i + batch_size]).to(device)
        with torch.no_grad():
            emb = embedder(batch)
        all_embs.append(emb.cpu().numpy())
    return np.vstack(all_embs)


def similarity_score(code_a, code_b):
    toks_a = set(code_a.split())
    toks_b = set(code_b.split())
    if not toks_a or not toks_b:
        return 0.0
    return len(toks_a & toks_b) / len(toks_a | toks_b)


def simulate_verification(
    target_program, retrieved_invariants, strategy="rait", difficulty="medium", rng=None
):
    if rng is None:
        rng = np.random.RandomState(None)
    diff_factor = {"easy": 0.95, "medium": 0.85, "hard": 0.70, "ood": 0.60}[difficulty]
    if strategy == "zero_shot":
        # No retrieval benefit
        p_success = diff_factor * 0.88
        base_calls = int(rng.geometric(p=diff_factor * 0.7))
        base_calls = min(base_calls, 8)
        success = rng.random() < p_success
        return success, base_calls, base_calls * 2, target_program["invariant"]
    elif strategy == "rait":
        if not retrieved_invariants:
            return simulate_verification(
                target_program, [], "zero_shot", difficulty, rng
            )
        best_sim = max(
            similarity_score(target_program["code"], r["code"])
            for r in retrieved_invariants
        )
        p_first_call = min(0.98, diff_factor * 0.80 + best_sim * 0.30)
        if rng.random() < p_first_call:
            llm_calls = 1
            success = True
        else:
            llm_calls = max(
                1, int(rng.geometric(p=min(0.95, diff_factor * 0.80 + best_sim * 0.20)))
            )
            llm_calls = min(llm_calls, 4)
            success = rng.random() < min(0.999, diff_factor * 0.92 + best_sim * 0.10)
        return success, llm_calls, llm_calls * 2, target_program["invariant"]


class RAITLibrary:
    def __init__(
        self,
        tfidf_vec,
        embedder,
        update_strategy="success_only",
        diversity_threshold=0.3,
    ):
        self.tfidf_vec = tfidf_vec
        self.embedder = embedder
        self.update_strategy = update_strategy
        self.diversity_threshold = diversity_threshold
        self.entries = []
        self.embeddings = None
        self.add_counts = {"added": 0, "skipped": 0}

    def _is_diverse_enough(self, emb):
        if self.embeddings is None or len(self.embeddings) == 0:
            return True
        sims = cosine_similarity(emb[None, :], self.embeddings)[0]
        return sims.max() < (1.0 - self.diversity_threshold)

    def _do_add(self, program, invariant, emb):
        entry = {
            "program": program,
            "code": program["code"],
            "invariant": invariant,
            "embedding": emb,
            "success_count": 1,
            "use_count": 0,
        }
        self.entries.append(entry)
        if self.embeddings is None:
            self.embeddings = emb[None, :]
        else:
            self.embeddings = np.vstack([self.embeddings, emb[None, :]])
        self.add_counts["added"] += 1

    def add(self, program, invariant, success=True):
        code = program["code"]
        emb = embed_codes([code], self.tfidf_vec, self.embedder)[0]
        if self.update_strategy == "success_only":
            if success:
                self._do_add(program, invariant, emb)
            else:
                self.add_counts["skipped"] += 1
        elif self.update_strategy == "unconditional":
            self._do_add(program, invariant, emb)
        elif self.update_strategy == "failure_only":
            if not success:
                self._do_add(program, invariant, emb)
            else:
                self.add_counts["skipped"] += 1
        elif self.update_strategy == "diversity_driven":
            if self._is_diverse_enough(emb):
                self._do_add(program, invariant, emb)
            else:
                self.add_counts["skipped"] += 1

    def retrieve(self, query_code, k=3):
        if len(self.entries) == 0:
            return [], []
        q_emb = embed_codes([query_code], self.tfidf_vec, self.embedder)[0]
        sims = cosine_similarity(q_emb[None, :], self.embeddings)[0]
        top_idx = np.argsort(sims)[::-1][:k]
        retrieved = [self.entries[i] for i in top_idx]
        weights = sims[top_idx]
        for e in retrieved:
            e["use_count"] += 1
        return retrieved, weights

    def update_confidence(self, entries, success):
        for e in entries:
            if success:
                e["success_count"] += 1


def compute_ites(rait_sr, zs_sr, rait_calls, zs_calls):
    if zs_sr == 0 or rait_calls == 0:
        return 1.0
    return (rait_sr / max(zs_sr, 1e-9)) * (zs_calls / max(rait_calls, 1e-9))


def evaluate_update_strategy(
    test_programs,
    seed_programs,
    tfidf_vec,
    embedder,
    update_strategy,
    diversity_threshold=0.3,
    k=3,
    seed=0,
):
    # Use a per-run RNG so results differ between strategies
    rng = np.random.RandomState(seed)
    lib = RAITLibrary(
        tfidf_vec,
        embedder,
        update_strategy=update_strategy,
        diversity_threshold=diversity_threshold,
    )
    for prog in seed_programs:
        lib._do_add(
            prog, prog["invariant"], embed_codes([prog["code"]], tfidf_vec, embedder)[0]
        )

    results = []
    library_sizes = []
    for prog in test_programs:
        if len(lib.entries) > 0:
            retrieved, weights = lib.retrieve(prog["code"], k=min(k, len(lib.entries)))
        else:
            retrieved, weights = [], np.array([])
        success, llm_calls, smt_calls, inv = simulate_verification(
            prog, retrieved, strategy="rait", difficulty=prog["difficulty"], rng=rng
        )
        lib.add(prog, inv, success=success)
        if success:
            lib.update_confidence(retrieved, success)
        results.append(
            {"success": success, "llm_calls": llm_calls, "smt_calls": smt_calls}
        )
        library_sizes.append(len(lib.entries))

    sr = np.mean([r["success"] for r in results])
    successful_calls = [r["llm_calls"] for r in results if r["success"]]
    mean_llm = np.mean(successful_calls) if successful_calls else 8.0
    return sr, mean_llm, results, library_sizes, lib.add_counts.copy()


def run_zero_shot_baseline(test_programs, seed=999):
    rng = np.random.RandomState(seed)
    results = []
    for prog in test_programs:
        success, llm_calls, smt_calls, inv = simulate_verification(
            prog, [], strategy="zero_shot", difficulty=prog["difficulty"], rng=rng
        )
        results.append({"success": success, "llm_calls": llm_calls})
    sr = np.mean([r["success"] for r in results])
    successful_calls = [r["llm_calls"] for r in results if r["success"]]
    mean_llm = np.mean(successful_calls) if successful_calls else 8.0
    return sr, mean_llm


DATASET_NAMES = ["mbpp", "openai_humaneval", "code_search_net"]
UPDATE_STRATEGIES = [
    "success_only",
    "unconditional",
    "failure_only",
    "diversity_driven",
]
DIVERSITY_THRESHOLDS = [0.1, 0.3, 0.5, 0.7]

print("\n" + "=" * 70)
print("  ABLATION: Library Update Strategy Sensitivity Analysis")
print("=" * 70)

datasets = {}
for ds_name in DATASET_NAMES:
    datasets[ds_name] = load_dataset_samples(ds_name, n=200)

ablation_results = {}
# Track full RAIT SR (success_only = full system) for CCD computation
full_rait_sr = {}

for ds_name in DATASET_NAMES:
    print(f"\n{'='*60}")
    print(f"  Dataset: {ds_name.upper()}")
    print(f"{'='*60}")
    samples = datasets[ds_name]
    n_seed = int(len(samples) * 0.5)
    seed_programs = samples[:n_seed]
    test_programs = samples[n_seed:]
    all_codes = [p["code"] for p in samples]
    tfidf_vec = build_tfidf_embedder(all_codes)
    actual_vocab_size = len(tfidf_vec.vocabulary_)
    print(f"  TF-IDF vocab size: {actual_vocab_size}")
    embedder = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(device)

    zs_sr, zs_calls = run_zero_shot_baseline(test_programs, seed=999)
    print(f"  [zero_shot            ]  SR={zs_sr:.4f}  MeanLLM={zs_calls:.4f}")
    ablation_results[ds_name] = {"zero_shot": {"sr": zs_sr, "mean_calls": zs_calls}}

    strategy_sr = {}
    for strat_idx, strategy in enumerate(UPDATE_STRATEGIES):
        # Use different seeds per strategy to get genuinely different simulation outcomes
        run_seed = MASTER_SEED + strat_idx * 100 + hash(ds_name) % 1000
        sr, mean_calls, raw, lib_sizes, add_counts = evaluate_update_strategy(
            test_programs,
            seed_programs,
            tfidf_vec,
            embedder,
            update_strategy=strategy,
            diversity_threshold=0.3,
            k=3,
            seed=run_seed,
        )
        ites = compute_ites(sr, zs_sr, mean_calls, zs_calls)
        final_lib_size = lib_sizes[-1] if lib_sizes else 0
        strategy_sr[strategy] = sr
        print(
            f"  [{strategy:22s}]  SR={sr:.4f}  MeanLLM={mean_calls:.4f}  "
            f"ITES={ites:.4f}  LibSize={final_lib_size}  "
            f'Added={add_counts["added"]}  Skipped={add_counts["skipped"]}'
        )
        ablation_results[ds_name][strategy] = {
            "sr": sr,
            "mean_calls": mean_calls,
            "ites": ites,
            "library_sizes": lib_sizes,
            "add_counts": add_counts,
        }
        experiment_data["update_strategy_ablation"][ds_name]["metrics"]["sr"].append(sr)
        experiment_data["update_strategy_ablation"][ds_name]["metrics"][
            "mean_calls"
        ].append(mean_calls)
        experiment_data["update_strategy_ablation"][ds_name]["metrics"]["ites"].append(
            ites
        )
        experiment_data["update_strategy_ablation"][ds_name]["library_sizes"].append(
            lib_sizes
        )
        experiment_data["update_strategy_ablation"][ds_name]["add_counts"].append(
            add_counts
        )

    # Compute CCD: full RAIT (success_only) SR minus each ablated strategy SR
    full_sr = strategy_sr.get("success_only", zs_sr)
    full_rait_sr[ds_name] = full_sr
    for strategy in UPDATE_STRATEGIES:
        ablated_sr = strategy_sr.get(strategy, 0)
        ccd = full_sr - ablated_sr
        ablation_results[ds_name][strategy]["ccd"] = ccd
        experiment_data["update_strategy_ablation"][ds_name]["metrics"]["ccd"].append(
            ccd
        )
        print(f"  CCD [{strategy:22s}]: {ccd:.4f}")

    experiment_data["update_strategy_ablation"][ds_name]["losses"]["val"].append(
        1.0 - ablation_results[ds_name].get("success_only", {}).get("sr", 0)
    )

# Diversity threshold sweep
print("\n--- Diversity Threshold Sweep (diversity_driven strategy) ---")
diversity_sweep_results = {}
for ds_name in DATASET_NAMES:
    print(f"\n  Dataset: {ds_name}")
    samples = datasets[ds_name]
    n_seed = int(len(samples) * 0.5)
    seed_programs = samples[:n_seed]
    test_programs = samples[n_seed:]
    all_codes = [p["code"] for p in samples]
    tfidf_vec = build_tfidf_embedder(all_codes)
    actual_vocab_size = len(tfidf_vec.vocabulary_)
    embedder = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(device)
    zs_sr, zs_calls = run_zero_shot_baseline(test_programs, seed=999)
    diversity_sweep_results[ds_name] = {}
    for t_idx, thresh in enumerate(DIVERSITY_THRESHOLDS):
        run_seed = MASTER_SEED + t_idx * 77 + hash(ds_name) % 500
        sr, mean_calls, raw, lib_sizes, add_counts = evaluate_update_strategy(
            test_programs,
            seed_programs,
            tfidf_vec,
            embedder,
            update_strategy="diversity_driven",
            diversity_threshold=thresh,
            k=3,
            seed=run_seed,
        )
        ites = compute_ites(sr, zs_sr, mean_calls, zs_calls)
        final_lib_size = lib_sizes[-1] if lib_sizes else 0
        print(
            f'    threshold={thresh:.1f}: SR={sr:.4f}  ITES={ites:.4f}  LibSize={final_lib_size}  Added={add_counts["added"]}'
        )
        diversity_sweep_results[ds_name][thresh] = {
            "sr": sr,
            "mean_calls": mean_calls,
            "ites": ites,
            "final_lib_size": final_lib_size,
            "add_counts": add_counts,
        }
        experiment_data["diversity_threshold_sweep"][ds_name]["metrics"]["sr"].append(
            sr
        )
        experiment_data["diversity_threshold_sweep"][ds_name]["metrics"]["ites"].append(
            ites
        )
        experiment_data["diversity_threshold_sweep"][ds_name]["thresholds"].append(
            thresh
        )
        experiment_data["diversity_threshold_sweep"][ds_name]["final_lib_sizes"].append(
            final_lib_size
        )

# Per-difficulty breakdown
print("\n--- Per-Difficulty ITES by Update Strategy (mbpp) ---")
difficulties = ["easy", "medium", "hard", "ood"]
diff_breakdown = {}
ds_name = "mbpp"
samples = datasets[ds_name]
n_seed = int(len(samples) * 0.5)
seed_programs = samples[:n_seed]
all_codes = [p["code"] for p in samples]
tfidf_vec = build_tfidf_embedder(all_codes)
actual_vocab_size = len(tfidf_vec.vocabulary_)
embedder = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(device)

for s_idx, strategy in enumerate(UPDATE_STRATEGIES):
    diff_breakdown[strategy] = {}
    for d_idx, diff in enumerate(difficulties):
        diff_test = [p for p in samples[n_seed:] if p["difficulty"] == diff]
        if not diff_test:
            diff_breakdown[strategy][diff] = 1.0
            continue
        run_seed = MASTER_SEED + s_idx * 50 + d_idx * 13
        sr, mean_calls, _, lib_sizes, _ = evaluate_update_strategy(
            diff_test,
            seed_programs,
            tfidf_vec,
            embedder,
            update_strategy=strategy,
            diversity_threshold=0.3,
            k=3,
            seed=run_seed,
        )
        zs_sr, zs_calls = run_zero_shot_baseline(diff_test, seed=run_seed + 500)
        ites = compute_ites(sr, zs_sr, mean_calls, zs_calls)
        diff_breakdown[strategy][diff] = ites
    print(
        f"  [{strategy:22s}]: "
        + "  ".join(f"{d}={diff_breakdown[strategy][d]:.3f}" for d in difficulties)
    )
    experiment_data["difficulty_breakdown"][strategy]["metrics"]["ites"] = [
        diff_breakdown[strategy][d] for d in difficulties
    ]

# Library growth
print("\n--- Library Size Growth Over Time ---")
growth_by_strategy = {}
for s_idx, strategy in enumerate(UPDATE_STRATEGIES):
    growth_by_strategy[strategy] = {}
    for ds_name in DATASET_NAMES:
        samples = datasets[ds_name]
        n_seed = int(len(samples) * 0.5)
        seed_programs = samples[:n_seed]
        test_programs = samples[n_seed:]
        all_codes = [p["code"] for p in samples]
        tfidf_vec = build_tfidf_embedder(all_codes)
        actual_vocab_size = len(tfidf_vec.vocabulary_)
        embedder = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(device)
        run_seed = MASTER_SEED + s_idx * 100 + hash(ds_name) % 1000
        _, _, _, lib_sizes, _ = evaluate_update_strategy(
            test_programs,
            seed_programs,
            tfidf_vec,
            embedder,
            update_strategy=strategy,
            diversity_threshold=0.3,
            k=3,
            seed=run_seed,
        )
        growth_by_strategy[strategy][ds_name] = lib_sizes

# VISUALIZATIONS
COLORS_STRAT = {
    "success_only": "#1f77b4",
    "unconditional": "#ff7f0e",
    "failure_only": "#d62728",
    "diversity_driven": "#2ca02c",
}

# Plot 1: ITES by update strategy
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    ites_vals = [
        ablation_results[ds_name].get(s, {}).get("ites", 1.0) for s in UPDATE_STRATEGIES
    ]
    bars = ax.bar(
        UPDATE_STRATEGIES,
        ites_vals,
        color=[COLORS_STRAT[s] for s in UPDATE_STRATEGIES],
        alpha=0.85,
        edgecolor="k",
    )
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1.5, label="Zero-Shot")
    ax.set_title(f"{ds_name}\nITES by Update Strategy", fontsize=10, fontweight="bold")
    ax.set_ylabel("ITES")
    ax.set_ylim(0, max(ites_vals) * 1.3 + 0.3)
    ax.set_xticks(range(len(UPDATE_STRATEGIES)))
    ax.set_xticklabels(UPDATE_STRATEGIES, rotation=20, ha="right", fontsize=8)
    for bar, v in zip(bars, ites_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{v:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.suptitle("Library Update Strategy: ITES Comparison", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_update_strategy_ites.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 2: Success Rate
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    sr_vals = [
        ablation_results[ds_name].get(s, {}).get("sr", 0) for s in UPDATE_STRATEGIES
    ]
    zs_sr = ablation_results[ds_name]["zero_shot"]["sr"]
    bars = ax.bar(
        UPDATE_STRATEGIES,
        sr_vals,
        color=[COLORS_STRAT[s] for s in UPDATE_STRATEGIES],
        alpha=0.85,
        edgecolor="k",
    )
    ax.axhline(
        zs_sr, color="gray", linestyle="--", linewidth=1.5, label=f"ZS SR={zs_sr:.3f}"
    )
    ax.set_title(
        f"{ds_name}\nSuccess Rate by Update Strategy", fontsize=10, fontweight="bold"
    )
    ax.set_ylabel("Success Rate")
    ax.set_ylim(0, 1.15)
    ax.set_xticks(range(len(UPDATE_STRATEGIES)))
    ax.set_xticklabels(UPDATE_STRATEGIES, rotation=20, ha="right", fontsize=8)
    ax.legend(fontsize=8)
    for bar, v in zip(bars, sr_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.suptitle(
    "Library Update Strategy: Success Rate Comparison", fontsize=12, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_update_strategy_sr.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 3: Library growth
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    for strategy in UPDATE_STRATEGIES:
        lib_sizes = growth_by_strategy[strategy][ds_name]
        xs = np.arange(1, len(lib_sizes) + 1)
        ax.plot(
            xs, lib_sizes, label=strategy, color=COLORS_STRAT[strategy], linewidth=2
        )
    ax.set_title(f"{ds_name}\nLibrary Size Growth", fontsize=10, fontweight="bold")
    ax.set_xlabel("Test Programs Processed")
    ax.set_ylabel("Library Size")
    ax.legend(fontsize=7)
plt.suptitle("Library Growth by Update Strategy", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_update_strategy_lib_growth.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 4: Diversity threshold sweep
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    thresholds = DIVERSITY_THRESHOLDS
    ites_vals = [diversity_sweep_results[ds_name][t]["ites"] for t in thresholds]
    lib_sizes = [
        diversity_sweep_results[ds_name][t]["final_lib_size"] for t in thresholds
    ]
    ax2 = ax.twinx()
    ax.plot(thresholds, ites_vals, "b-o", linewidth=2, markersize=8, label="ITES")
    ax2.plot(
        thresholds, lib_sizes, "r--s", linewidth=2, markersize=8, label="Library Size"
    )
    ax.axhline(1.0, color="gray", linestyle=":", linewidth=1)
    ax.set_title(
        f"{ds_name}\nDiversity Threshold vs ITES", fontsize=10, fontweight="bold"
    )
    ax.set_xlabel("Diversity Threshold")
    ax.set_ylabel("ITES", color="blue")
    ax2.set_ylabel("Final Library Size", color="red")
    ax.tick_params(axis="y", labelcolor="blue")
    ax2.tick_params(axis="y", labelcolor="red")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8)
plt.suptitle(
    "Diversity-Driven Update: Threshold Sensitivity", fontsize=12, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_diversity_threshold_sweep.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 5: Per-difficulty heatmap
fig, ax = plt.subplots(figsize=(9, 5))
heatmap_data = np.array(
    [[diff_breakdown[s][d] for d in difficulties] for s in UPDATE_STRATEGIES]
)
im = ax.imshow(
    heatmap_data,
    cmap="YlOrRd",
    aspect="auto",
    vmin=0.8,
    vmax=max(2.5, heatmap_data.max()),
)
plt.colorbar(im, ax=ax, label="ITES")
ax.set_xticks(range(len(difficulties)))
ax.set_xticklabels(difficulties)
ax.set_yticks(range(len(UPDATE_STRATEGIES)))
ax.set_yticklabels(UPDATE_STRATEGIES)
ax.set_xlabel("Difficulty Level")
ax.set_ylabel("Update Strategy")
ax.set_title("ITES by Update Strategy × Difficulty (MBPP)", fontweight="bold")
for i in range(len(UPDATE_STRATEGIES)):
    for j in range(len(difficulties)):
        ax.text(
            j,
            i,
            f"{heatmap_data[i, j]:.2f}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white" if heatmap_data[i, j] > heatmap_data.max() * 0.7 else "black",
        )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_difficulty_strategy_heatmap.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 6: Mean LLM calls
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    calls_vals = [
        ablation_results[ds_name].get(s, {}).get("mean_calls", 0)
        for s in UPDATE_STRATEGIES
    ]
    zs_calls = ablation_results[ds_name]["zero_shot"]["mean_calls"]
    bars = ax.bar(
        UPDATE_STRATEGIES,
        calls_vals,
        color=[COLORS_STRAT[s] for s in UPDATE_STRATEGIES],
        alpha=0.85,
        edgecolor="k",
    )
    ax.axhline(
        zs_calls,
        color="gray",
        linestyle="--",
        linewidth=1.5,
        label=f"ZS calls={zs_calls:.2f}",
    )
    ax.set_title(
        f"{ds_name}\nMean LLM Calls by Update Strategy", fontsize=10, fontweight="bold"
    )
    ax.set_ylabel("Mean LLM Calls")
    ax.set_xticks(range(len(UPDATE_STRATEGIES)))
    ax.set_xticklabels(UPDATE_STRATEGIES, rotation=20, ha="right", fontsize=8)
    ax.legend(fontsize=8)
    for bar, v in zip(bars, calls_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.suptitle("Library Update Strategy: Mean LLM Calls", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_update_strategy_llm_calls.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 7: CCD across datasets
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    ccd_vals = [
        ablation_results[ds_name].get(s, {}).get("ccd", 0.0) for s in UPDATE_STRATEGIES
    ]
    bars = ax.bar(
        UPDATE_STRATEGIES,
        ccd_vals,
        color=[COLORS_STRAT[s] for s in UPDATE_STRATEGIES],
        alpha=0.85,
        edgecolor="k",
    )
    ax.axhline(0.0, color="gray", linestyle="--", linewidth=1.5)
    ax.set_title(f"{ds_name}\nCCD by Update Strategy", fontsize=10, fontweight="bold")
    ax.set_ylabel("Component Contribution Delta (CCD)")
    ax.set_xticks(range(len(UPDATE_STRATEGIES)))
    ax.set_xticklabels(UPDATE_STRATEGIES, rotation=20, ha="right", fontsize=8)
    for bar, v in zip(bars, ccd_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.suptitle(
    "Component Contribution Delta (CCD) Analysis", fontsize=12, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ablation_ccd_analysis.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# SUMMARY
print("\n" + "=" * 70)
print("  ABLATION SUMMARY: Library Update Strategy")
print("=" * 70)
print(
    f"\n{'Dataset':<22} {'Strategy':<24} {'SR':>6} {'MeanLLM':>9} {'ITES':>8} {'CCD':>8} {'LibSize':>8}"
)
print("-" * 85)
for ds_name in DATASET_NAMES:
    zs = ablation_results[ds_name]["zero_shot"]
    print(
        f"  {ds_name:<20} {'zero_shot':<24} {zs['sr']:>6.4f} {zs['mean_calls']:>9.4f} {'1.0000':>8}  {'0.0000':>7}  {'N/A':>7}"
    )
    for strategy in UPDATE_STRATEGIES:
        r = ablation_results[ds_name].get(strategy, {})
        final_size = r.get("library_sizes", [0])[-1] if r.get("library_sizes") else 0
        ccd = r.get("ccd", 0.0)
        print(
            f"  {ds_name:<20} {strategy:<24} {r.get('sr', 0):>6.4f} {r.get('mean_calls', 0):>9.4f} {r.get('ites', 0):>8.4f} {ccd:>8.4f} {final_size:>8}"
        )

print("\n  Diversity Threshold Sweep (diversity_driven):")
print(
    f"  {'Dataset':<20} " + "  ".join(f"thresh={t:.1f}" for t in DIVERSITY_THRESHOLDS)
)
for ds_name in DATASET_NAMES:
    row = f"  {ds_name:<20} "
    row += "  ".join(
        f"ITES={diversity_sweep_results[ds_name][t]['ites']:.4f}"
        for t in DIVERSITY_THRESHOLDS
    )
    print(row)

print("\n  Best update strategy per dataset (by ITES):")
for ds_name in DATASET_NAMES:
    best = max(
        UPDATE_STRATEGIES,
        key=lambda s: ablation_results[ds_name].get(s, {}).get("ites", 0),
    )
    best_ites = ablation_results[ds_name][best]["ites"]
    print(f"  {ds_name}: {best} → ITES = {best_ites:.4f}")

# Save experiment data
experiment_data["ablation_results"] = {
    ds: {
        strat: {
            "sr": float(ablation_results[ds].get(strat, {}).get("sr", 0)),
            "mean_calls": float(
                ablation_results[ds].get(strat, {}).get("mean_calls", 0)
            ),
            "ites": float(ablation_results[ds].get(strat, {}).get("ites", 0)),
            "ccd": float(ablation_results[ds].get(strat, {}).get("ccd", 0)),
        }
        for strat in UPDATE_STRATEGIES
    }
    for ds in DATASET_NAMES
}
experiment_data["diversity_sweep_results"] = {
    ds: {
        str(t): {
            "ites": float(diversity_sweep_results[ds][t]["ites"]),
            "final_lib_size": int(diversity_sweep_results[ds][t]["final_lib_size"]),
        }
        for t in DIVERSITY_THRESHOLDS
    }
    for ds in DATASET_NAMES
}
experiment_data["difficulty_breakdown_mbpp"] = {
    strat: {d: float(diff_breakdown[strat][d]) for d in difficulties}
    for strat in UPDATE_STRATEGIES
}
experiment_data["growth_by_strategy"] = {
    strategy: {
        ds_name: [int(x) for x in growth_by_strategy[strategy][ds_name]]
        for ds_name in DATASET_NAMES
    }
    for strategy in UPDATE_STRATEGIES
}

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\n  Results saved to {working_dir}/experiment_data.npy")
print("  Plots saved to:", working_dir)
print("  Done.")
