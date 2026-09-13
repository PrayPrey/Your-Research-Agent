import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_delta_comparison(compare_result: dict, out_path: str) -> None:
    static = compare_result["static_first"]
    exec_ = compare_result["exec_first"]

    conditions = ["Static-First (A)", "Exec-First (B)"]
    deltas = [static["delta_pass_12"], exec_["delta_pass_12"]]

    # Bootstrap SE approximation: sqrt(p*(1-p)/n)
    def se(delta, n):
        p = delta if delta > 0 else 0.01
        return np.sqrt(p * (1 - p) / n)

    errors = [se(d, compare_result["static_first"]["n_problems"]) for d in deltas]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(conditions, deltas, yerr=errors, capsize=5, color=['#4C72B0', '#DD8452'])
    ax.set_ylabel('ΔPass₁₂ (Iteration 2 - Iteration 1)')
    ax.set_title('Early Iteration Gains by Feedback Order')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

    for bar, d in zip(bars, deltas):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{d:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_iteration_trajectory(traj_static: dict[int, float], traj_exec: dict[int, float], out_path: str) -> None:
    iters = [1, 2, 3]
    static_vals = [traj_static[i] for i in iters]
    exec_vals = [traj_exec[i] for i in iters]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(iters, static_vals, 'o-', label='Static-First (A)', color='#4C72B0', markersize=8)
    ax.plot(iters, exec_vals, 's-', label='Exec-First (B)', color='#DD8452', markersize=8)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Cumulative Pass@1')
    ax.set_title('Pass Rate Trajectory by Iteration')
    ax.legend()
    ax.set_xticks(iters)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
