import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_gate_comparison(gate_result, out_path):
    """Bar chart: VGG-11 vs ResNet-18 texture_bias_ratio."""
    fig, ax = plt.subplots(figsize=(8, 6))

    models = ['VGG-11', 'ResNet-18']
    ratios = [gate_result['vgg_ratio'], gate_result['resnet_ratio']]
    colors = ['#3498db', '#e74c3c']

    bars = ax.bar(models, ratios, color=colors, edgecolor='black', linewidth=1.5)
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label='Neutral (0.5)')

    ax.set_ylabel('Texture Bias Ratio', fontsize=12)
    ax.set_title(f'Texture Bias Comparison\n(Gate: {"PASS" if gate_result["pass_gate"] else "FAIL"}, Δ={gate_result["diff"]:.3f})', fontsize=14)
    ax.set_ylim(0, 1)
    ax.legend()

    for bar, ratio in zip(bars, ratios):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{ratio:.3f}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_curves(resnet_history, vgg_history, out_path):
    """Line plot: test_acc_curve for both models vs epoch."""
    fig, ax = plt.subplots(figsize=(10, 6))

    epochs = range(1, len(resnet_history['test_acc_curve']) + 1)

    ax.plot(epochs, vgg_history['test_acc_curve'], label='VGG-11', color='#3498db', linewidth=2)
    ax.plot(epochs, resnet_history['test_acc_curve'], label='ResNet-18', color='#e74c3c', linewidth=2)

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('Test Accuracy', fontsize=12)
    ax.set_title('Training Curves', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_confusion_shape_texture(resnet_bias, vgg_bias, out_path):
    """Bar chart of shape/texture accuracy comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x = [0, 1, 2.5, 3.5]
    labels = ['VGG Shape', 'VGG Texture', 'ResNet Shape', 'ResNet Texture']
    values = [
        vgg_bias['shape_accuracy'],
        vgg_bias['texture_accuracy'],
        resnet_bias['shape_accuracy'],
        resnet_bias['texture_accuracy'],
    ]
    colors = ['#3498db', '#85c1e9', '#e74c3c', '#f1948a']

    bars = ax.bar(x, values, color=colors, edgecolor='black', linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Shape vs Texture Accuracy', fontsize=14)
    ax.set_ylim(0, max(values) * 1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
