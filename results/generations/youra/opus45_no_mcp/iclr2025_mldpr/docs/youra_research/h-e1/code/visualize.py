import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


def plot_gap_comparison(gap_high: float, gap_low: float, out_path: str):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['High-Use (CIFAR-10)', 'Low-Use (SVHN)'], [gap_high, gap_low], color=['#d62728', '#1f77b4'])
    ax.set_ylabel('Generalization Gap (%)')
    ax.set_title('Generalization Gap Comparison')
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_accuracy_comparison(results: dict, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = [0, 1]
    width = 0.35
    in_domain = [results['cifar10']['in_domain_acc'], results['svhn']['in_domain_acc']]
    held_out = [results['cifar10']['held_out_acc'], results['svhn']['held_out_acc']]
    ax.bar([i - width/2 for i in x], in_domain, width, label='In-Domain', color='#2ca02c')
    ax.bar([i + width/2 for i in x], held_out, width, label='Held-Out', color='#ff7f0e')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('In-Domain vs Held-Out Accuracy')
    ax.set_xticks(x)
    ax.set_xticklabels(['CIFAR-10', 'SVHN'])
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_curves(history: dict, out_path: str):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    for cond, data in history.items():
        epochs = [e['epoch'] for e in data]
        losses = [e['loss'] for e in data]
        accs = [e['acc'] for e in data]
        ax1.plot(epochs, losses, label=cond)
        ax2.plot(epochs, accs, label=cond)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Loss')
    ax1.legend()
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training Accuracy')
    ax2.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
