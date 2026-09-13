import os
import matplotlib.pyplot as plt
import numpy as np
from config import CONFIG

def ensure_figures_dir():
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)

def plot_gate_comparison(results: dict, out_path: str = None) -> None:
    ensure_figures_dir()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "gate_comparison.png")

    models = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
    model_labels = ["CodeLlama-7B", "CodeLlama-34B", "GPT-4"]
    benchmarks = CONFIG["benchmarks"]

    fig, axes = plt.subplots(1, len(benchmarks), figsize=(12, 5))
    if len(benchmarks) == 1:
        axes = [axes]

    for ax, benchmark in zip(axes, benchmarks):
        structured_scores = []
        raw_scores = []
        for model in models:
            s_key = f"{model}|{benchmark}|structured"
            r_key = f"{model}|{benchmark}|raw"
            structured_scores.append(results.get(s_key, {}).get("pass_at_1", 0))
            raw_scores.append(results.get(r_key, {}).get("pass_at_1", 0))

        x = np.arange(len(models))
        width = 0.35
        ax.bar(x - width/2, structured_scores, width, label="Structured", color="#2196F3")
        ax.bar(x + width/2, raw_scores, width, label="Raw", color="#FF9800")
        ax.set_ylabel("Pass@1")
        ax.set_title(f"{benchmark.upper()}")
        ax.set_xticks(x)
        ax.set_xticklabels(model_labels, rotation=15, ha="right")
        ax.legend()
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_repair_success(results: dict, out_path: str = None) -> None:
    ensure_figures_dir()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "repair_success.png")

    models = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
    model_labels = ["CodeLlama-7B", "CodeLlama-34B", "GPT-4"]

    structured_rates = []
    raw_rates = []
    for model in models:
        s_vals = [results.get(f"{model}|{b}|structured", {}).get("repair_success_rate", 0) for b in CONFIG["benchmarks"]]
        r_vals = [results.get(f"{model}|{b}|raw", {}).get("repair_success_rate", 0) for b in CONFIG["benchmarks"]]
        structured_rates.append(np.mean(s_vals))
        raw_rates.append(np.mean(r_vals))

    x = np.arange(len(models))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, structured_rates, width, label="Structured", color="#4CAF50")
    ax.bar(x + width/2, raw_rates, width, label="Raw", color="#F44336")
    ax.set_ylabel("Repair Success Rate")
    ax.set_title("Repair Success Rate by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(model_labels)
    ax.legend()
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_repair_iterations(results: dict, out_path: str = None) -> None:
    ensure_figures_dir()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "repair_iterations.png")

    models = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
    model_labels = ["CodeLlama-7B", "CodeLlama-34B", "GPT-4"]

    structured_attempts = []
    raw_attempts = []
    for model in models:
        s_vals = [results.get(f"{model}|{b}|structured", {}).get("avg_attempts", 0) for b in CONFIG["benchmarks"]]
        r_vals = [results.get(f"{model}|{b}|raw", {}).get("avg_attempts", 0) for b in CONFIG["benchmarks"]]
        structured_attempts.append(np.mean(s_vals))
        raw_attempts.append(np.mean(r_vals))

    x = np.arange(len(models))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, structured_attempts, width, label="Structured", color="#9C27B0")
    ax.bar(x + width/2, raw_attempts, width, label="Raw", color="#795548")
    ax.set_ylabel("Avg Repair Attempts")
    ax.set_title("Average Repair Iterations by Model")
    ax.set_xticks(x)
    ax.set_xticklabels(model_labels)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_error_type_heatmap(results: dict, out_path: str = None) -> None:
    ensure_figures_dir()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "error_heatmap.png")

    all_error_types = set()
    for key, val in results.items():
        if isinstance(val, dict) and "error_breakdown" in val:
            all_error_types.update(val["error_breakdown"].keys())

    error_types = sorted(all_error_types)[:10]
    if not error_types:
        error_types = ["SyntaxError", "TypeError", "NameError"]

    models = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]
    formats = ["structured", "raw"]
    col_labels = [f"{m.split('/')[-1].replace('-Instruct-hf', '')}|{f}" for m in models for f in formats]

    data = np.zeros((len(error_types), len(col_labels)))
    for i, err_type in enumerate(error_types):
        for j, (model, fmt) in enumerate([(m, f) for m in models for f in formats]):
            for benchmark in CONFIG["benchmarks"]:
                key = f"{model}|{benchmark}|{fmt}"
                data[i, j] += results.get(key, {}).get("error_breakdown", {}).get(err_type, 0)

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(error_types)))
    ax.set_xticklabels(col_labels, rotation=45, ha="right")
    ax.set_yticklabels(error_types)
    ax.set_title("Error Type Distribution")
    plt.colorbar(im, ax=ax, label="Count")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def plot_benchmark_comparison(results: dict, out_path: str = None) -> None:
    ensure_figures_dir()
    out_path = out_path or os.path.join(CONFIG["figures_dir"], "benchmark_comparison.png")

    benchmarks = CONFIG["benchmarks"]
    models = ["codellama/CodeLlama-7b-Instruct-hf", "codellama/CodeLlama-34b-Instruct-hf", "gpt-4"]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, fmt, color in zip(axes, ["structured", "raw"], ["#2196F3", "#FF9800"]):
        data = []
        for benchmark in benchmarks:
            row = [results.get(f"{m}|{benchmark}|{fmt}", {}).get("pass_at_1", 0) for m in models]
            data.append(row)

        x = np.arange(len(models))
        width = 0.35
        for i, benchmark in enumerate(benchmarks):
            offset = (i - 0.5) * width
            ax.bar(x + offset, data[i], width, label=benchmark.upper())

        ax.set_ylabel("Pass@1")
        ax.set_title(f"{fmt.capitalize()} Format")
        ax.set_xticks(x)
        ax.set_xticklabels(["7B", "34B", "GPT-4"])
        ax.legend()
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
