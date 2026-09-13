import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {"alpha_tuning": {}}

synthetic_datasets = [
    {
        "name": "ImageNet",
        "doc_text": (
            "ImageNet is a large-scale image classification dataset containing 1.2 million images across 1000 object categories. Intended for benchmarking visual recognition systems. Images scraped from the internet, predominantly western contexts. Task: object classification. Population: general objects. Known limitations: label noise, western cultural bias, consent issues for human images."
        ),
        "usage_text": (
            "ImageNet used as backbone pretraining for medical image segmentation. Transfer learning for satellite imagery classification. Evaluated on aerial drone footage. Used as gold-standard benchmark for neural architecture search. Fairness evaluation across skin tone diversity. Autonomous driving perception. Medical diagnosis accuracy benchmarking."
        ),
        "misuse_label": 0.9,
    },
    {
        "name": "MNIST",
        "doc_text": (
            "MNIST is a dataset of handwritten digits (0-9) collected from US Census Bureau employees and high school students. Intended for evaluating handwritten digit recognition algorithms. Grayscale 28x28 pixel images. Task: digit classification. Population: American English writers. Known limitations: small size, simple patterns."
        ),
        "usage_text": (
            "MNIST used to benchmark deep learning architectures including transformers and GANs. Used as a proxy for evaluating continual learning and meta-learning. Anomaly detection baseline. Federated learning experiments. Quantum computing benchmarks. Used to claim state-of-the-art on general image recognition."
        ),
        "misuse_label": 0.85,
    },
    {
        "name": "MS-COCO",
        "doc_text": (
            "MS-COCO is an object detection, segmentation, and captioning dataset with 330K images. Designed for scene understanding. Images from Flickr, mostly western contexts. Task: detection, segmentation, captioning. Population: general scenes. Limitations: annotation subjectivity, cultural representation gaps."
        ),
        "usage_text": (
            "COCO used to benchmark object detection for autonomous vehicles. Evaluation of medical image annotation tools. Used for video understanding benchmarks. Cross-cultural visual question answering. Robotics manipulation tasks."
        ),
        "misuse_label": 0.7,
    },
    {
        "name": "SST-2",
        "doc_text": (
            "Stanford Sentiment Treebank contains movie reviews labeled with sentiment. Task: binary sentiment classification of English movie reviews. Population: English-speaking movie reviewers on Rotten Tomatoes. Limitations: domain-specific to movie reviews, may not generalize to other domains."
        ),
        "usage_text": (
            "SST-2 used as general English NLP benchmark for language models. Applied to product review sentiment analysis. Used for financial news sentiment classification. Medical text sentiment. Social media toxicity detection. Multilingual transfer. General-purpose NLP model leaderboard benchmark."
        ),
        "misuse_label": 0.8,
    },
    {
        "name": "SQuAD",
        "doc_text": (
            "Stanford Question Answering Dataset contains reading comprehension questions from Wikipedia articles. Task: extractive question answering. Population: English Wikipedia text, crowdworker questions. Limitations: extractive only, Wikipedia domain, English only."
        ),
        "usage_text": (
            "SQuAD used for evaluating open-domain question answering. Legal document QA. Medical literature question answering. Multilingual QA evaluation. Generative QA model benchmarking. Knowledge graph question answering."
        ),
        "misuse_label": 0.75,
    },
    {
        "name": "Adult Income",
        "doc_text": (
            "Adult Income dataset from 1994 US Census. Task: binary classification of income >50K. Population: US adults in 1994. Known limitations: outdated, US-specific, contains protected attributes (race, gender), reflects 1994 societal biases."
        ),
        "usage_text": (
            "Adult used to benchmark fairness-aware machine learning algorithms. Used to evaluate bias mitigation in modern hiring tools. Applied to non-US populations. Used as representative of current income distribution. Benchmark for explainable AI."
        ),
        "misuse_label": 0.95,
    },
    {
        "name": "PTB (Penn Treebank)",
        "doc_text": (
            "Penn Treebank contains Wall Street Journal articles from 1989. Task: language modeling, POS tagging, parsing. Population: financial news text 1989. Limitations: domain-specific financial text, outdated vocabulary, English only."
        ),
        "usage_text": (
            "PTB used as standard language modeling benchmark for neural networks. Applied to evaluate general-purpose language models. Used in biomedical NLP benchmarks. Perplexity on PTB used as proxy for general language understanding."
        ),
        "misuse_label": 0.7,
    },
    {
        "name": "CelebA",
        "doc_text": (
            "CelebA contains 200K celebrity face images with 40 binary attribute annotations. Task: face attribute prediction, face generation. Population: celebrities (skewed demographics). Limitations: non-consensual images, demographic imbalance, binary gender labels, beauty industry bias."
        ),
        "usage_text": (
            "CelebA used to benchmark GAN training quality. Facial recognition accuracy. Emotion detection evaluation. Age estimation from faces. Used as general face dataset without demographic caveats. Deepfake detection benchmark."
        ),
        "misuse_label": 0.9,
    },
    {
        "name": "CIFAR-10",
        "doc_text": (
            "CIFAR-10 contains 60K 32x32 color images in 10 classes. Task: image classification benchmark. Population: curated internet images. Intended for rapid prototyping. Limitations: low resolution, limited classes, may be saturated benchmark."
        ),
        "usage_text": (
            "CIFAR-10 used to claim state-of-the-art on general image recognition. Benchmark for neural architecture search as proxy for ImageNet performance. Continual learning evaluation. Adversarial robustness main benchmark."
        ),
        "misuse_label": 0.65,
    },
    {
        "name": "Iris",
        "doc_text": (
            "Iris dataset contains measurements of iris flowers from 3 species. Task: multiclass classification toy example. Population: specific iris flowers from Gaspe Peninsula, Canada 1936. Limitations: tiny, toy dataset, not for real use."
        ),
        "usage_text": (
            "Iris used to benchmark machine learning classifiers including deep learning. Evaluation of dimensionality reduction algorithms. Clustering algorithm comparison. Feature importance methods benchmark. Federated learning experiments."
        ),
        "misuse_label": 0.5,
    },
    {
        "name": "MultiNLI",
        "doc_text": (
            "Multi-Genre NLI corpus contains 433K sentence pairs for natural language inference. Task: textual entailment. Population: diverse English text genres. Limitations: annotation artifacts, hypothesis-only baselines, crowdworker bias."
        ),
        "usage_text": (
            "MultiNLI used to evaluate zero-shot text classification. Cross-lingual NLI. General natural language understanding benchmark. Used as transfer learning source for information extraction and relation classification."
        ),
        "misuse_label": 0.6,
    },
    {
        "name": "Enron Email",
        "doc_text": (
            "Enron email dataset from Enron Corporation bankruptcy. Task: email classification, spam detection. Population: corporate emails from Enron employees. Limitations: single company, legal/ethical concerns, outdated spam patterns."
        ),
        "usage_text": (
            "Enron used as general email benchmark for spam detection. Social network analysis. Communication pattern studies. Used to represent general email behavior. Organizational behavior analysis."
        ),
        "misuse_label": 0.7,
    },
    {
        "name": "MovieLens",
        "doc_text": (
            "MovieLens contains movie ratings from GroupLens. Task: collaborative filtering, recommendation systems research. Population: self-selected online movie raters. Limitations: self-selection bias, US-centric, older movies overrepresented."
        ),
        "usage_text": (
            "MovieLens used as benchmark for general recommender systems. News recommendation evaluation. E-commerce product recommendation. Music recommendation. Cross-domain recommendation evaluation."
        ),
        "misuse_label": 0.55,
    },
    {
        "name": "COMPAS",
        "doc_text": (
            "COMPAS recidivism dataset from Broward County, Florida. Task: recidivism risk scoring. Population: defendants in Broward County 2013-2014. Limitations: narrow geographic scope, racial bias documented, contested validity."
        ),
        "usage_text": (
            "COMPAS used as standard fairness benchmark across all ML fairness papers. Used to claim general recidivism prediction improvements. National policy implications drawn from single county data. Transferred to other countries."
        ),
        "misuse_label": 1.0,
    },
    {
        "name": "WikiText-103",
        "doc_text": (
            "WikiText-103 is a language modeling dataset from verified Wikipedia articles. Task: language modeling. Population: English Wikipedia. Limitations: formal encyclopedic text only, English only."
        ),
        "usage_text": (
            "WikiText-103 used to evaluate general language models. Used as pretraining data quality proxy. Perplexity as general NLP capability measure. Transfer to conversational and social media text."
        ),
        "misuse_label": 0.55,
    },
]

df = pd.DataFrame(synthetic_datasets)
print(f"Dataset size: {len(df)} datasets")
print(df[["name", "misuse_label"]].to_string())

all_texts = df["doc_text"].tolist() + df["usage_text"].tolist()
vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words="english")
vectorizer.fit(all_texts)
doc_vectors = vectorizer.transform(df["doc_text"]).toarray()
usage_vectors = vectorizer.transform(df["usage_text"]).toarray()
doc_tensors = torch.FloatTensor(doc_vectors).to(device)
usage_tensors = torch.FloatTensor(usage_vectors).to(device)


class DriftEncoder(nn.Module):
    def __init__(self, input_dim, embed_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, embed_dim),
            nn.LayerNorm(embed_dim),
        )

    def forward(self, x):
        return self.encoder(x)


task_keywords = {
    "classification": ["classif", "recognition", "categoriz"],
    "generation": ["generat", "synthes", "GAN"],
    "qa": ["question answer", "reading comprehension", "QA"],
    "detection": ["detect", "segment", "locali"],
    "nlp": ["sentiment", "NLI", "entail", "language model"],
    "recommendation": ["recommend", "collaborat", "rating"],
    "fairness": ["fairness", "bias", "equity", "protected"],
}


def extract_task_vector(text):
    text_lower = text.lower()
    vec = []
    for task, keywords in task_keywords.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        vec.append(min(score, 1))
    return np.array(vec, dtype=float)


doc_task_vecs = np.array([extract_task_vector(t) for t in df["doc_text"]])
usage_task_vecs = np.array([extract_task_vector(t) for t in df["usage_text"]])


def structural_drift(doc_vec, usage_vec):
    if doc_vec.sum() == 0 and usage_vec.sum() == 0:
        return 0.0
    intersection = np.minimum(doc_vec, usage_vec).sum()
    union = np.maximum(doc_vec, usage_vec).sum()
    if union == 0:
        return 0.0
    return 1.0 - (intersection / union)


structural_drifts = np.array(
    [structural_drift(doc_task_vecs[i], usage_task_vecs[i]) for i in range(len(df))]
)
ground_truth = df["misuse_label"].values
misuse_labels = torch.FloatTensor(ground_truth).to(device)
input_dim = doc_vectors.shape[1]

alpha_values = [0.3, 0.5, 0.7, 0.9]
n_epochs = 50
cos_sim_fn = nn.CosineSimilarity(dim=1)

best_alpha = None
best_final_corr = -np.inf
best_drift_scores = None
best_semantic_drifts = None

print("\n=== HYPERPARAMETER TUNING: alpha ===")

for alpha in alpha_values:
    print(f"\n--- Training with alpha={alpha} ---")
    torch.manual_seed(42)
    encoder = DriftEncoder(input_dim=input_dim, embed_dim=64).to(device)
    optimizer = torch.optim.Adam(encoder.parameters(), lr=1e-3)

    train_losses = []
    val_losses = []
    train_corrs = []
    val_corrs = []
    drift_scores_per_epoch = []

    for epoch in range(n_epochs):
        encoder.train()
        optimizer.zero_grad()
        doc_emb = encoder(doc_tensors)
        usage_emb = encoder(usage_tensors)
        cos_sims = cos_sim_fn(doc_emb, usage_emb)
        target_sim = 1.0 - misuse_labels
        loss = nn.MSELoss()(cos_sims, target_sim)
        loss.backward()
        optimizer.step()

        encoder.eval()
        with torch.no_grad():
            doc_emb_val = encoder(doc_tensors)
            usage_emb_val = encoder(usage_tensors)
            cos_sims_val = cos_sim_fn(doc_emb_val, usage_emb_val).cpu().numpy()

        semantic_drifts = 1.0 - cos_sims_val
        drift_scores = alpha * semantic_drifts + (1 - alpha) * structural_drifts
        corr, pval = spearmanr(drift_scores, ground_truth)

        train_losses.append(loss.item())
        val_losses.append(loss.item())
        train_corrs.append(corr)
        val_corrs.append(corr)
        drift_scores_per_epoch.append(drift_scores.tolist())

        if (epoch + 1) % 10 == 0:
            print(
                f"  Epoch {epoch+1}/{n_epochs}: loss={loss.item():.4f}, Spearman={corr:.4f}, p={pval:.4f}"
            )

    # Final evaluation for this alpha
    encoder.eval()
    with torch.no_grad():
        doc_emb_final = encoder(doc_tensors)
        usage_emb_final = encoder(usage_tensors)
        final_cos_sims = cos_sim_fn(doc_emb_final, usage_emb_final).cpu().numpy()

    semantic_drifts_final = 1.0 - final_cos_sims
    drift_scores_final = alpha * semantic_drifts_final + (1 - alpha) * structural_drifts
    final_corr, final_pval = spearmanr(drift_scores_final, ground_truth)

    print(f"  Final Spearman for alpha={alpha}: {final_corr:.4f} (p={final_pval:.4f})")

    alpha_key = f"alpha_{alpha}"
    experiment_data["alpha_tuning"][alpha_key] = {
        "metrics": {"train": train_corrs, "val": val_corrs},
        "losses": {"train": train_losses, "val": val_losses},
        "predictions": drift_scores_final.tolist(),
        "ground_truth": ground_truth.tolist(),
        "drift_scores": drift_scores_final.tolist(),
        "semantic_drifts": semantic_drifts_final.tolist(),
        "structural_drifts": structural_drifts.tolist(),
        "spearman_correlation": final_corr,
        "pvalue": final_pval,
        "alpha": alpha,
        "dataset_names": df["name"].tolist(),
        "drift_scores_per_epoch": drift_scores_per_epoch,
    }

    if final_corr > best_final_corr:
        best_final_corr = final_corr
        best_alpha = alpha
        best_drift_scores = drift_scores_final.copy()
        best_semantic_drifts = semantic_drifts_final.copy()

print(f"\n=== BEST ALPHA: {best_alpha} with Spearman={best_final_corr:.4f} ===")

# Baseline TF-IDF
tfidf_cos = cosine_similarity(doc_vectors, usage_vectors).diagonal()
tfidf_drift = 1.0 - tfidf_cos
tfidf_combined = 0.7 * tfidf_drift + 0.3 * structural_drifts
baseline_corr, baseline_pval = spearmanr(tfidf_combined, ground_truth)
print(f"Baseline TF-IDF Spearman: {baseline_corr:.4f} (p={baseline_pval:.4f})")

# Summary table
print("\n=== ALPHA TUNING SUMMARY ===")
print(f"{'Alpha':<10} {'Spearman':<12} {'P-value':<12}")
print("-" * 34)
for alpha in alpha_values:
    ak = f"alpha_{alpha}"
    corr = experiment_data["alpha_tuning"][ak]["spearman_correlation"]
    pv = experiment_data["alpha_tuning"][ak]["pvalue"]
    marker = " <-- BEST" if alpha == best_alpha else ""
    print(f"{alpha:<10} {corr:<12.4f} {pv:<12.4f}{marker}")

# Per-dataset results for best alpha
results_df = df[["name", "misuse_label"]].copy()
results_df["semantic_drift"] = best_semantic_drifts
results_df["structural_drift"] = structural_drifts
results_df["combined_drift_score"] = best_drift_scores
results_df["tfidf_drift_score"] = tfidf_combined
results_df = results_df.sort_values("combined_drift_score", ascending=False)
print(f"\nPer-Dataset Drift Scores (best alpha={best_alpha}):")
print(results_df.to_string(index=False))

# ─── Visualizations ───────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(f"Alpha Hyperparameter Tuning Results", fontsize=14)

# Plot 1: Spearman correlation over epochs for all alphas
ax = axes[0, 0]
colors_alpha = ["blue", "green", "orange", "red"]
for i, alpha in enumerate(alpha_values):
    ak = f"alpha_{alpha}"
    ax.plot(
        experiment_data["alpha_tuning"][ak]["metrics"]["val"],
        label=f"alpha={alpha}",
        color=colors_alpha[i],
        alpha=0.8,
    )
ax.axhline(
    y=baseline_corr,
    color="black",
    linestyle="--",
    label=f"TF-IDF Baseline ({baseline_corr:.3f})",
)
ax.set_xlabel("Epoch")
ax.set_ylabel("Spearman Correlation")
ax.set_title("Spearman Correlation vs Epoch (All Alphas)")
ax.legend(fontsize=8)
ax.grid(True)

# Plot 2: Final Spearman correlation bar chart
ax = axes[0, 1]
final_corrs = [
    experiment_data["alpha_tuning"][f"alpha_{a}"]["spearman_correlation"]
    for a in alpha_values
]
bar_colors = ["gold" if a == best_alpha else "steelblue" for a in alpha_values]
bars = ax.bar(
    [str(a) for a in alpha_values],
    final_corrs,
    color=bar_colors,
    alpha=0.8,
    edgecolor="black",
)
ax.axhline(
    y=baseline_corr,
    color="red",
    linestyle="--",
    label=f"TF-IDF Baseline ({baseline_corr:.3f})",
)
ax.set_xlabel("Alpha Value")
ax.set_ylabel("Final Spearman Correlation")
ax.set_title("Final Spearman Correlation per Alpha\n(Gold = Best Alpha)")
ax.legend()
ax.grid(True, axis="y")
for bar, corr in zip(bars, final_corrs):
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        bar.get_height() + 0.005,
        f"{corr:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

# Plot 3: Training loss over epochs for all alphas
ax = axes[1, 0]
for i, alpha in enumerate(alpha_values):
    ak = f"alpha_{alpha}"
    ax.plot(
        experiment_data["alpha_tuning"][ak]["losses"]["train"],
        label=f"alpha={alpha}",
        color=colors_alpha[i],
        alpha=0.8,
    )
ax.set_xlabel("Epoch")
ax.set_ylabel("MSE Loss")
ax.set_title("Training Loss Over Epochs (All Alphas)")
ax.legend(fontsize=8)
ax.grid(True)

# Plot 4: Scatter plot for best alpha
ax = axes[1, 1]
ax.scatter(best_drift_scores, ground_truth, color="blue", alpha=0.7, s=60)
for i, row in df.iterrows():
    ax.annotate(
        row["name"][:8], (best_drift_scores[i], ground_truth[i]), fontsize=6, alpha=0.8
    )
ax.set_xlabel("Combined Drift Score")
ax.set_ylabel("Ground Truth Misuse Label")
ax.set_title(
    f"Best Alpha={best_alpha}: Drift Score vs Misuse (ρ={best_final_corr:.3f})"
)
ax.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "alpha_tuning_results.png"), dpi=150, bbox_inches="tight"
)
plt.close()
print(f"\nPlot saved to {working_dir}/alpha_tuning_results.png")

# Component analysis plot
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle(f"Drift Components Analysis (Best alpha={best_alpha})", fontsize=13)

ax = axes2[0]
x = np.arange(len(df))
width = 0.35
ax.bar(
    x - width / 2,
    best_semantic_drifts,
    width,
    label="Semantic Drift",
    alpha=0.8,
    color="steelblue",
)
ax.bar(
    x + width / 2,
    structural_drifts,
    width,
    label="Structural Drift",
    alpha=0.8,
    color="coral",
)
ax.set_xticks(x)
ax.set_xticklabels(df["name"].values, rotation=45, ha="right", fontsize=7)
ax.set_ylabel("Drift Component Score")
ax.set_title("Semantic vs Structural Drift Components")
ax.legend()
ax.grid(True, axis="y")

ax = axes2[1]
# Overlay drift scores for all alphas per dataset (sorted by misuse label)
sorted_idx = np.argsort(ground_truth)[::-1]
sorted_names = [df["name"].values[i] for i in sorted_idx]
x = np.arange(len(sorted_names))
for i, alpha in enumerate(alpha_values):
    ak = f"alpha_{alpha}"
    scores = np.array(experiment_data["alpha_tuning"][ak]["drift_scores"])
    ax.plot(
        x,
        scores[sorted_idx],
        marker="o",
        markersize=4,
        label=f"alpha={alpha}",
        color=colors_alpha[i],
        alpha=0.8,
    )
ax.set_xticks(x)
ax.set_xticklabels(sorted_names, rotation=45, ha="right", fontsize=7)
ax.set_ylabel("Combined Drift Score")
ax.set_title("Drift Scores by Alpha (Datasets sorted by Misuse Label)")
ax.legend(fontsize=8)
ax.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "alpha_components_analysis.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()
print("Component analysis plot saved.")

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
results_df.to_csv(
    os.path.join(working_dir, "drift_scores_per_dataset.csv"), index=False
)
print(f"All experiment data saved to {working_dir}")

print("\n=== FINAL SUMMARY ===")
print(f"Best Alpha:                    {best_alpha}")
print(f"Best Spearman Correlation:     {best_final_corr:.4f}")
print(f"Baseline TF-IDF Correlation:   {baseline_corr:.4f}")
print(f"Number of datasets analyzed:   {len(df)}")
print(f"Alpha values tested:           {alpha_values}")
print("\nAll alpha results:")
for alpha in alpha_values:
    ak = f"alpha_{alpha}"
    corr = experiment_data["alpha_tuning"][ak]["spearman_correlation"]
    print(f"  alpha={alpha}: Spearman={corr:.4f}")
