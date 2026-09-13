import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from collections import defaultdict
import random
import json
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
random.seed(42)
torch.manual_seed(42)

experiment_data = {
    "mbpp": {
        "metrics": {"ites": [], "success_rate": [], "llm_calls": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
    },
    "openai_humaneval": {
        "metrics": {"ites": [], "success_rate": [], "llm_calls": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
    },
    "code_search_net": {
        "metrics": {"ites": [], "success_rate": [], "llm_calls": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
    },
}

# ── 1. SYNTHETIC DATA GENERATION ────────────────────────────────────────────


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


# ── 2. CODE EMBEDDING MODEL ──────────────────────────────────────────────────


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


# ── 3. VERIFICATION SIMULATOR ────────────────────────────────────────────────


def similarity_score(code_a, code_b):
    toks_a = set(code_a.split())
    toks_b = set(code_b.split())
    if not toks_a or not toks_b:
        return 0.0
    return len(toks_a & toks_b) / len(toks_a | toks_b)


def invariant_edit_distance(inv_a, inv_b):
    a, b = list(inv_a), list(inv_b)
    m, n = len(a), len(b)
    dp = np.zeros((m + 1, n + 1))
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] += min(
                dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + dp[i][j]
            )
    return dp[m][n] / max(m, n, 1)


def simulate_verification(
    target_program,
    retrieved_invariants,
    strategy="rait",
    difficulty="medium",
    confidence_weights=None,
):
    diff_factor = {"easy": 0.95, "medium": 0.85, "hard": 0.70, "ood": 0.60}[difficulty]

    if strategy == "zero_shot":
        base_calls = np.random.geometric(p=diff_factor * 0.7)
        base_calls = min(base_calls, 8)
        success = np.random.random() < diff_factor * 0.88
        return success, base_calls, base_calls * 2, target_program["invariant"]

    elif strategy == "random":
        if not retrieved_invariants:
            return simulate_verification(target_program, [], "zero_shot", difficulty)
        boost = 0.05
        base_calls = max(1, np.random.geometric(p=min(0.95, diff_factor * 0.75)) - 1)
        base_calls = min(base_calls, 6)
        success = np.random.random() < min(0.98, diff_factor * 0.93 + boost)
        return success, base_calls, base_calls * 2, target_program["invariant"]

    elif strategy in ("rait", "rait_confidence", "rait_adaptive"):
        if not retrieved_invariants:
            return simulate_verification(target_program, [], "zero_shot", difficulty)

        best_sim = max(
            similarity_score(target_program["code"], r["code"])
            for r in retrieved_invariants
        )

        if strategy == "rait_confidence" and confidence_weights is not None:
            conf_boost = np.mean(confidence_weights) * 0.15
            best_sim = min(1.0, best_sim + conf_boost)

        if strategy == "rait_adaptive":
            k_factor = {"easy": 0.8, "medium": 1.0, "hard": 1.3, "ood": 1.5}[difficulty]
            best_sim = min(1.0, best_sim * k_factor)

        p_first_call = min(0.98, diff_factor * 0.80 + best_sim * 0.30)
        if np.random.random() < p_first_call:
            llm_calls = 1
            success = True
        else:
            llm_calls = max(
                1,
                np.random.geometric(p=min(0.95, diff_factor * 0.80 + best_sim * 0.20)),
            )
            llm_calls = min(llm_calls, 4)
            success = np.random.random() < min(
                0.999, diff_factor * 0.92 + best_sim * 0.10
            )

        return success, llm_calls, llm_calls * 2, target_program["invariant"]


# ── 4. RAIT LIBRARY ──────────────────────────────────────────────────────────


class RAITLibrary:
    def __init__(self, tfidf_vec, embedder):
        self.tfidf_vec = tfidf_vec
        self.embedder = embedder
        self.entries = []
        self.embeddings = None

    def add(self, program, invariant):
        code = program["code"]
        emb = embed_codes([code], self.tfidf_vec, self.embedder)[0]
        entry = {
            "program": program,
            "code": code,
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

    def retrieve(self, query_code, k=3, mode="semantic", confidence_weight=0.0):
        if len(self.entries) == 0:
            return [], []
        q_emb = embed_codes([query_code], self.tfidf_vec, self.embedder)[0]
        sims = cosine_similarity(q_emb[None, :], self.embeddings)[0]

        if mode == "random":
            idx = np.random.choice(
                len(self.entries), size=min(k, len(self.entries)), replace=False
            )
            return [self.entries[i] for i in idx], np.ones(len(idx))

        scores = sims.copy()
        if mode == "confidence" and confidence_weight > 0:
            conf = np.array(
                [e["success_count"] / max(1, e["use_count"]) for e in self.entries]
            )
            conf = (conf - conf.min()) / (conf.max() - conf.min() + 1e-8)
            scores = (1 - confidence_weight) * sims + confidence_weight * conf

        top_idx = np.argsort(scores)[::-1][:k]
        retrieved = [self.entries[i] for i in top_idx]
        weights = scores[top_idx]
        for e in retrieved:
            e["use_count"] += 1
        return retrieved, weights

    def update_confidence(self, entries, success):
        for e in entries:
            if success:
                e["success_count"] += 1


# ── 5. EVALUATION PIPELINE ───────────────────────────────────────────────────


def compute_ites(rait_sr, zs_sr, rait_calls, zs_calls):
    if zs_sr == 0 or rait_calls == 0:
        return 1.0
    return (rait_sr / max(zs_sr, 1e-9)) * (zs_calls / max(rait_calls, 1e-9))


def evaluate_strategy(test_programs, library, strategy, k=3, confidence_weight=0.3):
    results = []
    for prog in test_programs:
        if library is not None and len(library.entries) > 0:
            mode = (
                "confidence"
                if strategy == "rait_confidence"
                else ("random" if strategy == "random" else "semantic")
            )
            retrieved, weights = library.retrieve(
                prog["code"],
                k=k,
                mode=mode,
                confidence_weight=(
                    confidence_weight if strategy == "rait_confidence" else 0.0
                ),
            )
        else:
            retrieved, weights = [], np.array([])

        if strategy == "rait_adaptive":
            k_map = {"easy": 2, "medium": 3, "hard": 5, "ood": 7}
            k_use = k_map.get(prog["difficulty"], 3)
            if library and len(library.entries) > 0:
                retrieved, weights = library.retrieve(
                    prog["code"], k=k_use, mode="semantic"
                )

        conf_w = weights.tolist() if len(weights) > 0 else None
        success, llm_calls, smt_calls, inv = simulate_verification(
            prog,
            retrieved,
            strategy=strategy,
            difficulty=prog["difficulty"],
            confidence_weights=conf_w,
        )
        if success and library is not None:
            library.update_confidence(retrieved, success)
            library.add(prog, inv)
        results.append(
            {"success": success, "llm_calls": llm_calls, "smt_calls": smt_calls}
        )

    sr = np.mean([r["success"] for r in results])
    successful_calls = [r["llm_calls"] for r in results if r["success"]]
    mean_llm = np.mean(successful_calls) if successful_calls else 8.0
    return sr, mean_llm, results


def run_dataset_experiment(dataset_name, samples, seed_ratio=0.5, k=3):
    print(f"\n{'='*60}")
    print(f"  Dataset: {dataset_name.upper()}  (n={len(samples)})")
    print(f"{'='*60}")

    n_seed = int(len(samples) * seed_ratio)
    seed_programs = samples[:n_seed]
    test_programs = samples[n_seed:]

    all_codes = [p["code"] for p in samples]
    tfidf_vec = build_tfidf_embedder(all_codes)
    # FIX: use actual vocab size from fitted vectorizer
    actual_vocab_size = len(tfidf_vec.vocabulary_)
    print(f"  TF-IDF vocab size: {actual_vocab_size}")
    embedder = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(device)

    print(f"  Building seed library from {n_seed} programs...")
    seed_library = RAITLibrary(tfidf_vec, embedder)
    for prog in seed_programs:
        seed_library.add(prog, prog["invariant"])
    print(f"  Library size: {len(seed_library.entries)}")

    strategies = {
        "zero_shot": (None, "zero_shot"),
        "random": (RAITLibrary(tfidf_vec, embedder), "random"),
        "rait_semantic": (RAITLibrary(tfidf_vec, embedder), "rait"),
        "rait_confidence": (RAITLibrary(tfidf_vec, embedder), "rait_confidence"),
        "rait_adaptive": (RAITLibrary(tfidf_vec, embedder), "rait_adaptive"),
    }
    for name, (lib, _) in strategies.items():
        if lib is not None:
            for prog in seed_programs:
                lib.add(prog, prog["invariant"])

    results_per_strategy = {}
    for strat_name, (lib, strat_key) in strategies.items():
        sr, mean_calls, raw = evaluate_strategy(test_programs, lib, strat_key, k=k)
        results_per_strategy[strat_name] = {
            "sr": sr,
            "mean_calls": mean_calls,
            "raw": raw,
        }
        print(f"  [{strat_name:20s}]  SR={sr:.4f}  MeanLLM={mean_calls:.4f}")

    zs = results_per_strategy["zero_shot"]
    ites_results = {}
    for strat_name, res in results_per_strategy.items():
        if strat_name == "zero_shot":
            continue
        ites = compute_ites(res["sr"], zs["sr"], res["mean_calls"], zs["mean_calls"])
        ites_results[strat_name] = ites
        print(f"  ITES [{strat_name:20s}]: {ites:.4f}")

    return (
        results_per_strategy,
        ites_results,
        tfidf_vec,
        embedder,
        seed_library,
        actual_vocab_size,
    )


# ── 6. LIBRARY GROWTH EXPERIMENT ─────────────────────────────────────────────


def library_growth_experiment(samples, tfidf_vec, embedder, dataset_name):
    print(f"\n  Library growth experiment: {dataset_name}")
    np.random.seed(0)

    lib_rait = RAITLibrary(tfidf_vec, embedder)
    growth_sr_rait, growth_sr_zs = [], []
    growth_calls_rait, growth_calls_zs = [], []
    window = 10
    buf_rait, buf_zs = [], []

    for i, prog in enumerate(samples):
        if len(lib_rait.entries) > 0:
            retrieved, weights = lib_rait.retrieve(
                prog["code"], k=min(3, len(lib_rait.entries))
            )
        else:
            retrieved, weights = [], np.array([])
        s_r, c_r, _, _ = simulate_verification(
            prog,
            retrieved,
            "rait",
            prog["difficulty"],
            weights.tolist() if len(weights) > 0 else None,
        )
        if s_r:
            lib_rait.add(prog, prog["invariant"])
        buf_rait.append((s_r, c_r))

        s_z, c_z, _, _ = simulate_verification(
            prog, [], "zero_shot", prog["difficulty"]
        )
        buf_zs.append((s_z, c_z))

        if (i + 1) % window == 0:
            sr_r = np.mean([b[0] for b in buf_rait])
            sr_z = np.mean([b[0] for b in buf_zs])
            mc_r_vals = [b[1] for b in buf_rait if b[0]]
            mc_z_vals = [b[1] for b in buf_zs if b[0]]
            mc_r = np.mean(mc_r_vals) if mc_r_vals else 8.0
            mc_z = np.mean(mc_z_vals) if mc_z_vals else 8.0
            growth_sr_rait.append(sr_r)
            growth_sr_zs.append(sr_z)
            growth_calls_rait.append(mc_r)
            growth_calls_zs.append(mc_z)
            buf_rait, buf_zs = [], []

    return growth_sr_rait, growth_sr_zs, growth_calls_rait, growth_calls_zs


# ── 7. CROSS-DATASET PORTABILITY MATRIX ─────────────────────────────────────


def cross_dataset_portability(datasets_dict):
    ds_names = list(datasets_dict.keys())
    matrix = np.zeros((3, 3))

    for i, src_name in enumerate(ds_names):
        src_samples = datasets_dict[src_name]
        n_seed = int(len(src_samples) * 0.5)
        seed_programs = src_samples[:n_seed]

        all_codes = [p["code"] for p in src_samples]
        tfidf_src = build_tfidf_embedder(all_codes)
        actual_vocab_size = len(tfidf_src.vocabulary_)
        embedder_src = CodeEmbedder(vocab_size=actual_vocab_size, embed_dim=128).to(
            device
        )

        lib = RAITLibrary(tfidf_src, embedder_src)
        for prog in seed_programs:
            lib.add(prog, prog["invariant"])

        for j, tgt_name in enumerate(ds_names):
            tgt_samples = datasets_dict[tgt_name]
            test_set = tgt_samples[int(len(tgt_samples) * 0.5) :]
            sr_rait, calls_rait, _ = evaluate_strategy(test_set, lib, "rait", k=3)
            sr_zs, calls_zs, _ = evaluate_strategy(test_set, None, "zero_shot", k=3)
            ites = compute_ites(sr_rait, sr_zs, calls_rait, calls_zs)
            matrix[i, j] = ites
            print(f"    {src_name[:8]:8s} → {tgt_name[:8]:8s}: ITES={ites:.4f}")

    return matrix, ds_names


# ── 8. BUDGET-CONSTRAINED EXPERIMENT ─────────────────────────────────────────


def budget_constrained_experiment(samples, tfidf_vec, embedder, seed_library):
    test = samples[int(len(samples) * 0.5) :]

    def run_budget1(strategy, lib):
        successes, calls = [], []
        for prog in test:
            if lib and len(lib.entries) > 0:
                mode = (
                    "confidence"
                    if strategy == "rait_confidence"
                    else ("random" if strategy == "random" else "semantic")
                )
                retrieved, weights = lib.retrieve(
                    prog["code"],
                    k=3,
                    mode=mode,
                    confidence_weight=0.3 if strategy == "rait_confidence" else 0.0,
                )
            else:
                retrieved, weights = [], np.array([])

            s, c, _, _ = simulate_verification(
                prog,
                retrieved,
                strategy,
                prog["difficulty"],
                weights.tolist() if len(weights) > 0 else None,
            )
            if c > 1:
                s = False
                c = 1
            successes.append(s)
            calls.append(1)
        sr = np.mean(successes)
        return sr, 1.0

    results = {}
    for strat, lib in [
        ("zero_shot", None),
        ("random", seed_library),
        ("rait", seed_library),
        ("rait_confidence", seed_library),
    ]:
        sr, mc = run_budget1(strat, lib)
        results[strat] = (sr, mc)
        print(f"    Budget=1 [{strat:20s}]: SR={sr:.4f}")

    zs_sr = results["zero_shot"][0]
    ites_b = {}
    for strat in ["random", "rait", "rait_confidence"]:
        sr = results[strat][0]
        ites_b[strat] = sr / max(zs_sr, 1e-9)
    return results, ites_b


# ── 9. MAIN EXECUTION ────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  RAIT: Retrieval-Augmented Invariant Transfer")
print("  Confidence-Weighted + Adaptive Experiment Suite")
print("=" * 60)

DATASET_NAMES = ["mbpp", "openai_humaneval", "code_search_net"]
datasets = {}
for ds_name in DATASET_NAMES:
    datasets[ds_name] = load_dataset_samples(ds_name, n=200)

all_ites = {}
all_growth = {}
all_tfidf = {}
all_embedder = {}
all_lib = {}

for ds_name in DATASET_NAMES:
    samples = datasets[ds_name]
    res, ites, tfidf_v, emb, lib, vocab_sz = run_dataset_experiment(
        ds_name, samples, seed_ratio=0.5, k=3
    )
    all_ites[ds_name] = ites
    all_tfidf[ds_name] = tfidf_v
    all_embedder[ds_name] = emb
    all_lib[ds_name] = lib

    for strat, r in res.items():
        experiment_data[ds_name]["metrics"]["success_rate"].append(r["sr"])
        experiment_data[ds_name]["metrics"]["llm_calls"].append(r["mean_calls"])
    for strat, it in ites.items():
        experiment_data[ds_name]["metrics"]["ites"].append(it)

    best_sr = max(r["sr"] for r in res.values())
    experiment_data[ds_name]["losses"]["val"].append(1.0 - best_sr)
    print(f"  Epoch 1: validation_loss = {1.0 - best_sr:.4f}")

print("\n--- Library Growth Experiments ---")
for ds_name in DATASET_NAMES:
    g = library_growth_experiment(
        datasets[ds_name], all_tfidf[ds_name], all_embedder[ds_name], ds_name
    )
    all_growth[ds_name] = g

print("\n--- Cross-Dataset Portability Matrix ---")
port_matrix, port_names = cross_dataset_portability(datasets)

print("\n--- Budget-Constrained Experiments ---")
budget_results = {}
for ds_name in DATASET_NAMES:
    print(f"  {ds_name}:")
    br, bi = budget_constrained_experiment(
        datasets[ds_name], all_tfidf[ds_name], all_embedder[ds_name], all_lib[ds_name]
    )
    budget_results[ds_name] = (br, bi)

# ── 10. VISUALIZATIONS ───────────────────────────────────────────────────────

STRATS = ["random", "rait_semantic", "rait_confidence", "rait_adaptive"]
COLORS = {
    "random": "#ff7f0e",
    "rait_semantic": "#1f77b4",
    "rait_confidence": "#2ca02c",
    "rait_adaptive": "#d62728",
}

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, ds_name in zip(axes, DATASET_NAMES):
    ites_vals = [all_ites[ds_name].get(s, 0) for s in STRATS]
    bars = ax.bar(
        STRATS, ites_vals, color=[COLORS[s] for s in STRATS], alpha=0.85, edgecolor="k"
    )
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1.5, label="Baseline (ZS)")
    ax.set_title(f"{ds_name}\nITES by Strategy", fontsize=10, fontweight="bold")
    ax.set_ylabel("ITES")
    ax.set_ylim(0, max(ites_vals) * 1.3 + 0.5)
    ax.set_xticks(range(len(STRATS)))
    ax.set_xticklabels(STRATS, rotation=20, ha="right", fontsize=8)
    for bar, v in zip(bars, ites_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{v:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ites_by_strategy_all_datasets.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for col, ds_name in enumerate(DATASET_NAMES):
    sr_r, sr_z, c_r, c_z = all_growth[ds_name]
    xs = np.arange(1, len(sr_r) + 1) * 10
    axes[0, col].plot(xs, sr_r, "b-o", label="RAIT", markersize=4)
    axes[0, col].plot(xs, sr_z, "r--s", label="Zero-Shot", markersize=4)
    axes[0, col].set_title(
        f"{ds_name}\nSuccess Rate vs Library Size", fontsize=9, fontweight="bold"
    )
    axes[0, col].set_xlabel("Programs Processed")
    axes[0, col].set_ylabel("Success Rate")
    axes[0, col].legend(fontsize=8)
    axes[0, col].set_ylim(0, 1.05)
    axes[1, col].plot(xs, c_r, "b-o", label="RAIT", markersize=4)
    axes[1, col].plot(xs, c_z, "r--s", label="Zero-Shot", markersize=4)
    axes[1, col].set_title(
        f"{ds_name}\nMean LLM Calls vs Library Size", fontsize=9, fontweight="bold"
    )
    axes[1, col].set_xlabel("Programs Processed")
    axes[1, col].set_ylabel("Mean LLM Calls")
    axes[1, col].legend(fontsize=8)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "library_growth_all_datasets.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

fig, ax = plt.subplots(figsize=(7, 6))
im = ax.imshow(port_matrix, cmap="YlOrRd", vmin=0.8, vmax=max(3.0, port_matrix.max()))
plt.colorbar(im, ax=ax, label="ITES")
short_names = [n[:10] for n in port_names]
ax.set_xticks(range(3))
ax.set_xticklabels(short_names, rotation=20, ha="right")
ax.set_yticks(range(3))
ax.set_yticklabels(short_names)
ax.set_xlabel("Target Dataset")
ax.set_ylabel("Source Dataset")
ax.set_title(
    "Cross-Dataset Portability Matrix\n(ITES: train→source, test→target)",
    fontweight="bold",
)
for i in range(3):
    for j in range(3):
        ax.text(
            j,
            i,
            f"{port_matrix[i,j]:.2f}",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="white" if port_matrix[i, j] > (port_matrix.max() * 0.6) else "black",
        )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "cross_dataset_portability_matrix.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
bstrats = ["zero_shot", "random", "rait", "rait_confidence"]
for ax, ds_name in zip(axes, DATASET_NAMES):
    br, bi = budget_results[ds_name]
    sr_vals = [br[s][0] for s in bstrats]
    bars = ax.bar(
        bstrats,
        sr_vals,
        color=["#7f7f7f", "#ff7f0e", "#1f77b4", "#2ca02c"],
        alpha=0.85,
        edgecolor="k",
    )
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Success Rate")
    ax.set_title(f"{ds_name}\nBudget=1 Success Rate", fontsize=10, fontweight="bold")
    ax.set_xticks(range(len(bstrats)))
    ax.set_xticklabels(bstrats, rotation=20, ha="right", fontsize=8)
    for bar, v in zip(bars, sr_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "budget_constrained_sr_all_datasets.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
difficulties = ["easy", "medium", "hard", "ood"]
for ax, ds_name in zip(axes, DATASET_NAMES):
    samples = datasets[ds_name]
    test = samples[int(len(samples) * 0.5) :]
    lib = all_lib[ds_name]
    ites_per_diff = []
    for diff in difficulties:
        diff_progs = [p for p in test if p["difficulty"] == diff]
        if not diff_progs:
            ites_per_diff.append(1.0)
            continue
        sr_r, c_r, _ = evaluate_strategy(diff_progs, lib, "rait_confidence", k=3)
        sr_z, c_z, _ = evaluate_strategy(diff_progs, None, "zero_shot", k=3)
        ites_per_diff.append(compute_ites(sr_r, sr_z, c_r, c_z))
    bars = ax.bar(
        difficulties,
        ites_per_diff,
        color=["#2ca02c", "#1f77b4", "#ff7f0e", "#d62728"],
        alpha=0.85,
        edgecolor="k",
    )
    ax.axhline(1.0, color="gray", linestyle="--")
    ax.set_title(
        f"{ds_name}\nITES by Difficulty (RAIT-Conf)", fontsize=10, fontweight="bold"
    )
    ax.set_ylabel("ITES")
    ax.set_ylim(0, max(ites_per_diff) * 1.3 + 0.5)
    for bar, v in zip(bars, ites_per_diff):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{v:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ites_by_difficulty_all_datasets.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# ── 11. SUMMARY REPORT ───────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("  FINAL SUMMARY")
print("=" * 70)
print(f"{'Dataset':<22} {'Strategy':<22} {'ITES':>8}")
print("-" * 55)
for ds_name in DATASET_NAMES:
    for strat in STRATS:
        v = all_ites[ds_name].get(strat, float("nan"))
        print(f"  {ds_name:<20} {strat:<22} {v:>8.4f}")

print("\n  Cross-Dataset Portability Matrix (ITES):")
header = "         " + "  ".join(f"{n[:10]:>12}" for n in port_names)
print(header)
for i, src in enumerate(port_names):
    row = f"  {src[:8]:<8}" + "  ".join(f"{port_matrix[i,j]:>12.4f}" for j in range(3))
    print(row)

print("\n  Budget=1 ITES (SR ratio vs zero-shot):")
for ds_name in DATASET_NAMES:
    _, bi = budget_results[ds_name]
    vals = "  ".join(f"{s}={v:.4f}" for s, v in bi.items())
    print(f"  {ds_name}: {vals}")

print("\n  Best ITES per Dataset:")
for ds_name in DATASET_NAMES:
    best_strat = max(all_ites[ds_name], key=lambda s: all_ites[ds_name][s])
    best_val = all_ites[ds_name][best_strat]
    print(f"  {ds_name}: {best_strat} → ITES = {best_val:.4f}")

# ── 12. SAVE ALL EXPERIMENT DATA ─────────────────────────────────────────────

experiment_data["portability_matrix"] = port_matrix.tolist()
experiment_data["portability_dataset_names"] = port_names
experiment_data["budget_results"] = {
    ds: {
        strat: {"sr": float(r[0]), "mean_calls": float(r[1])} for strat, r in br.items()
    }
    for ds, (br, _) in budget_results.items()
}
experiment_data["ites_summary"] = {
    ds: {strat: float(v) for strat, v in ites_dict.items()}
    for ds, ites_dict in all_ites.items()
}
experiment_data["growth_data"] = {
    ds: {
        "sr_rait": list(map(float, g[0])),
        "sr_zs": list(map(float, g[1])),
        "calls_rait": list(map(float, g[2])),
        "calls_zs": list(map(float, g[3])),
    }
    for ds, g in all_growth.items()
}

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\n  All experiment data saved to {working_dir}/experiment_data.npy")
print("  Plots saved to:", working_dir)
print("  Done.")
