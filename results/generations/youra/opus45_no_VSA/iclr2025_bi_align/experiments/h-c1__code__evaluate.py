import os
import numpy as np
import matplotlib.pyplot as plt
from umap import UMAP
from wordcloud import WordCloud

import hc1_config as config


def plot_gate_bar(agency_pattern_rate, out_path):
    """Plot bar chart comparing agency_pattern_rate vs thresholds."""
    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(
        ["Agency Pattern Rate"],
        [agency_pattern_rate],
        color="steelblue",
        width=0.5,
    )

    ax.axhline(y=config.AGENCY_RATE_PASS_THRESHOLD, color="green", linestyle="--",
               label=f"PASS threshold ({config.AGENCY_RATE_PASS_THRESHOLD:.0%})")
    ax.axhline(y=config.AGENCY_RATE_PARTIAL_THRESHOLD, color="orange", linestyle="--",
               label=f"PARTIAL threshold ({config.AGENCY_RATE_PARTIAL_THRESHOLD:.0%})")

    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Rate")
    ax.set_title("H-C1 Gate: Agency Pattern Rate")

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
                f'{height:.1%}', ha='center', va='bottom', fontsize=12)

    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_umap_projection(embeddings, topics, out_path):
    """Plot 2D UMAP projection colored by cluster."""
    reducer = UMAP(n_components=2, random_state=config.RANDOM_STATE)
    embedding_2d = reducer.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(10, 8))

    unique_topics = sorted(set(topics))
    colors = plt.cm.tab20(np.linspace(0, 1, len(unique_topics)))

    for i, topic in enumerate(unique_topics):
        mask = np.array(topics) == topic
        label = "Noise" if topic == -1 else f"Topic {topic}"
        alpha = 0.3 if topic == -1 else 0.7
        ax.scatter(
            embedding_2d[mask, 0],
            embedding_2d[mask, 1],
            c=[colors[i]],
            label=label,
            alpha=alpha,
            s=10,
        )

    ax.set_title("UMAP Projection of Disagreement Slice")
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")

    if len(unique_topics) <= 15:
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_topic_wordclouds(topic_model, top_k, out_path):
    """Generate word clouds for top-k topics."""
    topic_info = topic_model.get_topic_info()
    topics_to_plot = [t for t in topic_info["Topic"].tolist() if t != -1][:top_k]

    n_cols = min(3, len(topics_to_plot))
    n_rows = (len(topics_to_plot) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    axes = np.array(axes).flatten() if len(topics_to_plot) > 1 else [axes]

    for idx, topic_id in enumerate(topics_to_plot):
        keywords = topic_model.get_topic_keywords(topic_id)
        if not keywords:
            continue

        word_freq = {word: score for word, score in keywords}

        wc = WordCloud(
            width=400, height=300,
            background_color="white",
            max_words=50,
        ).generate_from_frequencies(word_freq)

        axes[idx].imshow(wc, interpolation="bilinear")
        axes[idx].set_title(f"Topic {topic_id}")
        axes[idx].axis("off")

    for idx in range(len(topics_to_plot), len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_cluster_size_histogram(topics, out_path):
    """Plot histogram of cluster sizes."""
    topics_arr = np.array(topics)
    unique_topics, counts = np.unique(topics_arr, return_counts=True)

    non_noise_mask = unique_topics != -1
    cluster_ids = unique_topics[non_noise_mask]
    cluster_sizes = counts[non_noise_mask]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(cluster_ids)), cluster_sizes, color="steelblue")
    ax.set_xticks(range(len(cluster_ids)))
    ax.set_xticklabels([f"T{t}" for t in cluster_ids], rotation=45)
    ax.set_xlabel("Topic")
    ax.set_ylabel("Count")
    ax.set_title("Cluster Size Distribution")

    noise_count = counts[unique_topics == -1][0] if -1 in unique_topics else 0
    ax.text(0.95, 0.95, f"Noise: {noise_count}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=10, bbox=dict(boxstyle="round", facecolor="wheat"))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def save_representative_docs_table(topic_model, agency_topic_ids, out_path):
    """Save representative documents for agency clusters to markdown."""
    lines = ["# Representative Documents (Agency Clusters)\n"]

    for topic_id in agency_topic_ids[:5]:
        keywords = topic_model.get_topic_keywords(topic_id)
        keywords_str = ", ".join(w for w, _ in keywords[:5])
        lines.append(f"\n## Topic {topic_id}: {keywords_str}\n")

        docs = topic_model.get_representative_docs(topic_id, n=3)
        for i, doc in enumerate(docs, 1):
            truncated = doc[:300] + "..." if len(doc) > 300 else doc
            lines.append(f"\n**Example {i}:**\n> {truncated}\n")

    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Saved: {out_path}")
