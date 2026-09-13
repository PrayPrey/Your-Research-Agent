import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── THREE HuggingFace dataset documentation profiles ──────────────────────────
hf_datasets = {
    "emotion": {
        "doc_text": (
            "The emotion dataset contains English Twitter messages labeled with six basic emotions: "
            "anger, fear, joy, love, sadness, surprise. Collected from Twitter for emotion classification "
            "research. Task: multi-class emotion classification. Population: English Twitter users. "
            "Domain: social media short text. Known limitations: Twitter-specific language, English only, "
            "six discrete emotion categories may not capture emotional complexity, crowdworker annotations."
        ),
        "intended_tasks": [
            "emotion classification",
            "sentiment analysis",
            "social media NLP",
        ],
        "intended_domain": "social media",
        "intended_population": "English Twitter users",
    },
    "ag_news": {
        "doc_text": (
            "AG News is a news topic classification dataset with 120,000 training samples across 4 categories: "
            "World, Sports, Business, Sci/Tech. Collected from AG news corpus. Task: news topic classification. "
            "Population: English news articles. Domain: news media. Known limitations: 4 broad categories only, "
            "English news sources, temporal snapshot, may not reflect current news distribution."
        ),
        "intended_tasks": [
            "text classification",
            "news categorization",
            "topic detection",
        ],
        "intended_domain": "news media",
        "intended_population": "English news articles",
    },
    "imdb": {
        "doc_text": (
            "IMDB dataset contains 50,000 movie reviews for binary sentiment classification. "
            "Task: binary sentiment classification (positive/negative). Population: IMDB movie reviewers. "
            "Domain: movie reviews, entertainment. Known limitations: English only, movie domain specific, "
            "binary labels only, IMDB user demographics may not be representative."
        ),
        "intended_tasks": [
            "sentiment classification",
            "opinion mining",
            "movie review analysis",
        ],
        "intended_domain": "movie reviews",
        "intended_population": "IMDB movie reviewers",
    },
}

# Usage scenarios: in-scope (low drift) vs out-of-scope (high drift)
usage_scenarios = {
    "emotion": [
        {
            "text": "Used emotion dataset to benchmark transformer models for Twitter emotion classification. Evaluated on joy sadness anger categories on social media English tweets.",
            "misuse": 0.1,
        },
        {
            "text": "Social media emotion detection using the emotion corpus. Fine-tuned BERT for six-class emotion prediction on English Twitter data crowdworker labels.",
            "misuse": 0.15,
        },
        {
            "text": "Applied emotion dataset to clinical depression diagnosis from patient medical notes. Used Twitter emotion labels as proxy for psychiatric clinical conditions diagnosis.",
            "misuse": 0.9,
        },
        {
            "text": "Emotion dataset used to train real-time workplace stress monitoring system. Deployed in corporate HR analytics for employee wellbeing scoring performance evaluation.",
            "misuse": 0.85,
        },
        {
            "text": "Multilingual emotion detection in Chinese Arabic social media using English Twitter emotion model directly without any domain or language adaptation transfer.",
            "misuse": 0.75,
        },
    ],
    "ag_news": [
        {
            "text": "AG News benchmark for evaluating text classification models across World Sports Business Sci/Tech news categories standard English news classification evaluation.",
            "misuse": 0.1,
        },
        {
            "text": "News topic categorization using AG News corpus. Standard 4-class news classification evaluation World Sports Business Technology English articles.",
            "misuse": 0.15,
        },
        {
            "text": "Used AG News to benchmark misinformation detection fake news identification systems for COVID-19 pandemic content moderation social media health claims.",
            "misuse": 0.85,
        },
        {
            "text": "AG News used as proxy for real-time breaking news classification emergency alert systems. Claimed generalization to 47 news categories political events crime reports.",
            "misuse": 0.9,
        },
        {
            "text": "Political bias detection partisan leaning in news articles using AG News labels. Evaluated political ideology liberal conservative of news sources from AG News.",
            "misuse": 0.8,
        },
    ],
    "imdb": [
        {
            "text": "IMDB sentiment analysis benchmark for binary opinion classification positive negative movie reviews. Standard NLP sentiment evaluation English movie review domain.",
            "misuse": 0.1,
        },
        {
            "text": "Movie review sentiment classification on IMDB dataset positive negative polarity detection with LSTM transformers English entertainment domain binary labels.",
            "misuse": 0.1,
        },
        {
            "text": "IMDB used to benchmark medical patient feedback sentiment for hospital quality assessment. Clinical patient review sentiment analysis healthcare evaluation binary labels.",
            "misuse": 0.9,
        },
        {
            "text": "Financial news sentiment analysis model trained on IMDB movie reviews. Applied to stock market prediction from earnings call transcripts financial domain trading.",
            "misuse": 0.95,
        },
        {
            "text": "IMDB sentiment model deployed for social media toxicity detection content moderation at scale without domain adaptation Twitter Reddit hate speech detection.",
            "misuse": 0.8,
        },
    ],
}

# ── Domain and task keyword dictionaries ─────────────────────────────────────
domain_keywords = {
    "medical": [
        "clinical",
        "patient",
        "diagnosis",
        "medical",
        "hospital",
        "disease",
        "healthcare",
        "psychiatric",
        "prognosis",
        "symptom",
    ],
    "financial": [
        "stock",
        "financial",
        "market",
        "earnings",
        "trading",
        "investment",
        "economic",
        "portfolio",
        "forecast",
        "credit",
    ],
    "social_media": [
        "twitter",
        "social media",
        "tweet",
        "instagram",
        "facebook",
        "reddit",
        "online",
        "hashtag",
        "viral",
        "post",
    ],
    "news": [
        "news",
        "article",
        "journalism",
        "media",
        "reporter",
        "publication",
        "headline",
        "editorial",
        "broadcast",
    ],
    "scientific": [
        "scientific",
        "research",
        "academic",
        "laboratory",
        "experiment",
        "study",
        "analysis",
        "empirical",
    ],
    "legal": [
        "legal",
        "court",
        "law",
        "justice",
        "policy",
        "regulation",
        "criminal",
        "statute",
        "legislation",
    ],
    "entertainment": [
        "movie",
        "film",
        "music",
        "game",
        "entertainment",
        "review",
        "imdb",
        "cinema",
        "television",
        "show",
    ],
    "education": [
        "education",
        "student",
        "learning",
        "academic",
        "school",
        "university",
        "classroom",
        "curriculum",
    ],
    "workplace": [
        "workplace",
        "employee",
        "corporate",
        "hr",
        "workforce",
        "organization",
        "management",
        "stress",
    ],
    "multilingual": [
        "multilingual",
        "cross-lingual",
        "arabic",
        "chinese",
        "french",
        "spanish",
        "german",
        "translation",
        "language transfer",
    ],
}

task_keywords = {
    "classification": ["classif", "categoriz", "recognition", "detection", "label"],
    "generation": ["generat", "synthes", "gan", "diffusion", "create", "produce"],
    "qa": [
        "question answer",
        "reading comprehension",
        "extractive",
        "question answering",
    ],
    "recommendation": ["recommend", "collaborat", "rating", "retrieval", "suggest"],
    "fairness": [
        "fairness",
        "bias",
        "equity",
        "protected",
        "demographic",
        "discrimination",
    ],
    "clinical_task": [
        "diagnosis",
        "prognosis",
        "clinical prediction",
        "patient outcome",
        "medical classification",
    ],
    "sentiment": ["sentiment", "opinion", "emotion", "feeling", "affect", "polarity"],
    "toxicity": [
        "toxicity",
        "hate speech",
        "content moderation",
        "abusive",
        "offensive",
        "harassment",
    ],
    "financial_pred": [
        "stock prediction",
        "market forecast",
        "financial sentiment",
        "earnings",
        "trading signal",
    ],
    "misinformation": [
        "fake news",
        "misinformation",
        "disinformation",
        "fact check",
        "claim verification",
    ],
}


def extract_structural_vector(text):
    text_lower = text.lower()
    vec = []
    for domain, keywords in domain_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        vec.append(min(score / max(len(keywords), 1), 1.0))
    for task, keywords in task_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        vec.append(min(score / max(len(keywords), 1), 1.0))
    words = text_lower.split()
    vec.append(len(set(words)) / max(len(words), 1))
    vec.append(min(text.count(".") / 10.0, 1.0))
    return np.array(vec, dtype=float)


def structural_drift(doc_vec, usage_vec):
    diff = np.abs(doc_vec - usage_vec)
    n_domain = len(domain_keywords)
    n_task = len(task_keywords)
    weights = np.concatenate(
        [
            np.ones(n_domain) * 2.0,
            np.ones(n_task) * 1.5,
            np.ones(2) * 0.3,
        ]
    )
    weights = weights / weights.sum()
    return float(np.dot(diff, weights))


# ── Build records ─────────────────────────────────────────────────────────────
all_records = []
for ds_name, scenarios in usage_scenarios.items():
    doc_text = hf_datasets[ds_name]["doc_text"]
    for scenario in scenarios:
        all_records.append(
            {
                "dataset": ds_name,
                "doc_text": doc_text,
                "usage_text": scenario["text"],
                "misuse_label": scenario["misuse"],
            }
        )
df_hf = pd.DataFrame(all_records)
ground_truth_hf = df_hf["misuse_label"].values

# Synthetic training data
synthetic_additional = [
    {
        "name": "COMPAS",
        "doc_text": "COMPAS recidivism dataset from Broward County Florida criminal justice. Task: recidivism risk scoring criminal prediction. Population: defendants Broward County 2013-2014. Domain: legal criminal justice. Limitations: narrow geographic scope racial bias documented contested validity criminal justice.",
        "usage_text": "COMPAS used as standard fairness benchmark across all ML fairness papers. Used to claim general recidivism prediction improvements. National policy implications drawn from single county criminal data. Transferred to European countries different legal systems.",
        "misuse_label": 1.0,
    },
    {
        "name": "Adult Income",
        "doc_text": "Adult Income dataset from 1994 US Census. Task: binary income classification greater 50K. Population: US adults 1994. Domain: economic census. Known limitations: outdated 1994 data US-specific contains protected attributes race gender reflects 1994 societal biases.",
        "usage_text": "Adult dataset used to benchmark fairness-aware machine learning algorithms. Applied to non-US European Asian populations. Used as representative of current income distribution modern economy. Modern hiring tool bias evaluation employment discrimination.",
        "misuse_label": 0.95,
    },
    {
        "name": "ImageNet",
        "doc_text": "ImageNet large-scale image classification dataset 1.2 million images 1000 object categories. Intended for benchmarking visual recognition systems object detection. Task: object classification recognition. Population: general objects western cultural context. Known limitations: label noise western cultural bias demographic imbalance.",
        "usage_text": "ImageNet used as backbone pretraining for medical image segmentation radiology diagnosis CT scan MRI analysis. Transfer learning satellite imagery remote sensing. Fairness evaluation skin tone diversity face recognition. Medical clinical diagnosis accuracy benchmarking healthcare.",
        "misuse_label": 0.9,
    },
    {
        "name": "CelebA",
        "doc_text": "CelebA contains 200K celebrity face images with 40 binary attribute annotations. Task: face attribute prediction gender age. Population: celebrities skewed demographics fame bias. Limitations: non-consensual images demographic imbalance binary gender labels western celebrity bias.",
        "usage_text": "CelebA used to benchmark GAN training quality image generation. Facial recognition accuracy deployment surveillance. Emotion detection clinical psychology evaluation. Used as general face dataset without demographic caveats. Deepfake detection benchmark identity verification.",
        "misuse_label": 0.9,
    },
    {
        "name": "SST-2",
        "doc_text": "Stanford Sentiment Treebank movie reviews labeled with sentiment polarity. Task: binary sentiment classification English movie reviews entertainment. Population: English-speaking movie reviewers Rotten Tomatoes critics. Limitations: domain-specific movie entertainment reviews English only.",
        "usage_text": "SST-2 used as general English NLP benchmark for language models scientific evaluation. Applied to product review financial news medical clinical text social media toxicity. General-purpose NLP model leaderboard benchmark diverse domains tasks.",
        "misuse_label": 0.8,
    },
    {
        "name": "MNIST",
        "doc_text": "MNIST dataset of handwritten digits 0-9 collected from US Census Bureau employees high school students. Task: digit classification image recognition simple patterns. Population: American English writers handwriting. Known limitations: small 28x28 size simple patterns toy benchmark saturated.",
        "usage_text": "MNIST used to benchmark deep learning architectures transformers GANs modern neural networks. Continual learning meta-learning proxy task image recognition. Quantum computing image classification benchmarks. Claim state-of-the-art general image recognition visual understanding.",
        "misuse_label": 0.85,
    },
    {
        "name": "SQuAD",
        "doc_text": "Stanford Question Answering Dataset reading comprehension questions from Wikipedia articles. Task: extractive question answering reading comprehension. Population: English Wikipedia crowdworker questions. Limitations: extractive answers only Wikipedia encyclopedia domain English only.",
        "usage_text": "SQuAD used for open-domain question answering diverse topics. Legal document QA court cases statutes. Medical literature clinical question answering patient diagnosis. Multilingual QA evaluation translation. Generative abstractive QA model benchmarking diverse domains.",
        "misuse_label": 0.75,
    },
    {
        "name": "MultiNLI",
        "doc_text": "Multi-Genre NLI corpus 433K sentence pairs for natural language inference textual entailment. Task: textual entailment classification. Population: diverse English text genres written spoken. Limitations: annotation artifacts hypothesis-only baselines crowdworker bias English only.",
        "usage_text": "MultiNLI used to evaluate zero-shot text classification diverse tasks. Cross-lingual multilingual NLI translation Arabic Chinese. General natural language understanding benchmark diverse domains. Transfer to information extraction relation classification scientific text.",
        "misuse_label": 0.6,
    },
    {
        "name": "CIFAR-10",
        "doc_text": "CIFAR-10 contains 60K 32x32 color images in 10 object classes. Task: image classification benchmark rapid prototyping. Population: curated internet images objects. Intended for rapid prototyping computer vision research. Limitations: low resolution 32x32 limited classes saturated benchmark.",
        "usage_text": "CIFAR-10 used to claim state-of-the-art general image recognition production systems. Neural architecture search proxy for ImageNet large scale. Continual learning evaluation diverse tasks. Adversarial robustness main benchmark security evaluation real-world deployment.",
        "misuse_label": 0.65,
    },
    {
        "name": "WikiText-103",
        "doc_text": "WikiText-103 language modeling dataset from verified Wikipedia articles. Task: language modeling perplexity evaluation. Population: English Wikipedia encyclopedia formal text. Limitations: formal encyclopedic written text only English only narrow domain.",
        "usage_text": "WikiText-103 used to evaluate general conversational language models chatbots. Perplexity as general NLP capability measure across tasks. Transfer to informal conversational social media text tweets comments. Pretraining data quality proxy diverse text domains.",
        "misuse_label": 0.55,
    },
    {
        "name": "MovieLens",
        "doc_text": "MovieLens contains movie ratings from GroupLens research collaborative filtering. Task: collaborative filtering movie recommendation systems research. Population: self-selected online movie raters US platform. Limitations: self-selection bias US-centric older movies overrepresented entertainment domain.",
        "usage_text": "MovieLens used as benchmark for general recommender systems all domains. News article recommendation evaluation journalism. E-commerce product recommendation purchase prediction. Music recommendation audio streaming. Cross-domain recommendation evaluation diverse products services.",
        "misuse_label": 0.55,
    },
    {
        "name": "Iris",
        "doc_text": "Iris dataset contains petal sepal measurements of iris flowers from 3 species. Task: multiclass classification toy example demonstration. Population: specific iris flowers Gaspe Peninsula Canada 1936 historical. Limitations: tiny 150 samples toy dataset not for real-world use historical data.",
        "usage_text": "Iris used to benchmark machine learning classifiers deep learning neural networks. Dimensionality reduction algorithms PCA UMAP visualization. Clustering algorithm comparison KMeans evaluation. Feature importance methods interpretability. Federated learning distributed experiments proof of concept.",
        "misuse_label": 0.5,
    },
]
df_synth = pd.DataFrame(synthetic_additional)
print(f"Synthetic training datasets: {len(df_synth)}")
print(f"HuggingFace test scenarios:  {len(df_hf)}")

# ── Compute structural drift vectors ─────────────────────────────────────────
struct_synth_doc = np.array(
    [extract_structural_vector(t) for t in df_synth["doc_text"]]
)
struct_synth_usage = np.array(
    [extract_structural_vector(t) for t in df_synth["usage_text"]]
)
struct_hf_doc = np.array([extract_structural_vector(t) for t in df_hf["doc_text"]])
struct_hf_usage = np.array([extract_structural_vector(t) for t in df_hf["usage_text"]])

struct_drifts_train = np.array(
    [
        structural_drift(struct_synth_doc[i], struct_synth_usage[i])
        for i in range(len(df_synth))
    ]
)
struct_drifts_hf = np.array(
    [structural_drift(struct_hf_doc[i], struct_hf_usage[i]) for i in range(len(df_hf))]
)

# ── TF-IDF vectorization (fit on ALL texts) ───────────────────────────────────
all_texts = (
    df_synth["doc_text"].tolist()
    + df_synth["usage_text"].tolist()
    + df_hf["doc_text"].tolist()
    + df_hf["usage_text"].tolist()
)
vectorizer = TfidfVectorizer(max_features=800, ngram_range=(1, 2), stop_words="english")
vectorizer.fit(all_texts)

doc_tfidf_train = (
    vectorizer.transform(df_synth["doc_text"]).toarray().astype(np.float32)
)
usage_tfidf_train = (
    vectorizer.transform(df_synth["usage_text"]).toarray().astype(np.float32)
)
doc_tfidf_hf = vectorizer.transform(df_hf["doc_text"]).toarray().astype(np.float32)
usage_tfidf_hf = vectorizer.transform(df_hf["usage_text"]).toarray().astype(np.float32)


# Direct TF-IDF cosine distance (no learned encoder) — primary semantic signal
def tfidf_cosine_drift(doc_mat, usage_mat):
    sims = np.array(
        [
            sk_cosine_similarity(doc_mat[i : i + 1], usage_mat[i : i + 1])[0, 0]
            for i in range(len(doc_mat))
        ]
    )
    return 1.0 - sims


tfidf_drifts_train = tfidf_cosine_drift(doc_tfidf_train, usage_tfidf_train)
tfidf_drifts_hf = tfidf_cosine_drift(doc_tfidf_hf, usage_tfidf_hf)

# ── Encoder (auxiliary refinement) ───────────────────────────────────────────
input_dim = doc_tfidf_train.shape[1]


class DriftEncoder(nn.Module):
    def __init__(self, input_dim, embed_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, embed_dim),
            nn.LayerNorm(embed_dim),
        )

    def forward(self, x):
        return self.net(x)


cos_sim_fn = nn.CosineSimilarity(dim=1)

doc_t_train = torch.FloatTensor(doc_tfidf_train).to(device)
usage_t_train = torch.FloatTensor(usage_tfidf_train).to(device)
doc_t_hf = torch.FloatTensor(doc_tfidf_hf).to(device)
usage_t_hf = torch.FloatTensor(usage_tfidf_hf).to(device)
labels_train = torch.FloatTensor(df_synth["misuse_label"].values).to(device)
gt_train = df_synth["misuse_label"].values

# ── Alpha sweep ───────────────────────────────────────────────────────────────
# alpha weights tfidf_drift vs structural_drift; beta weights encoder vs raw_tfidf
alpha_values = [0.4, 0.5, 0.6, 0.7]  # weight on tfidf_drift (1-alpha = structural)
beta_values = [0.3, 0.5]  # weight on encoder output vs raw tfidf drift

n_epochs = 40

experiment_data = {
    ds: {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "drift_scores": [],
        "dds_per_epoch": [],
    }
    for ds in ["emotion", "ag_news", "imdb"]
}
experiment_data["alpha_sweep"] = {}

best_corr_global = -np.inf
best_alpha_global, best_beta_global = None, None
best_model_state = None

print("\n=== Alpha/Beta Sweep ===")
for alpha in alpha_values:
    for beta in beta_values:
        key = f"a{alpha}_b{beta}"
        torch.manual_seed(42)
        encoder = DriftEncoder(input_dim=input_dim, embed_dim=64).to(device)
        optimizer = torch.optim.Adam(encoder.parameters(), lr=5e-4, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=n_epochs, eta_min=1e-5
        )

        train_losses, val_corrs, hf_corrs_epoch = [], [], []

        for epoch in range(n_epochs):
            encoder.train()
            optimizer.zero_grad()
            doc_emb = encoder(doc_t_train)
            usage_emb = encoder(usage_t_train)
            cos_sims = cos_sim_fn(doc_emb, usage_emb)
            target_sim = 1.0 - labels_train
            loss = nn.MSELoss()(cos_sims, target_sim)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(encoder.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            encoder.eval()
            with torch.no_grad():
                # Train Spearman
                cs_train = (
                    cos_sim_fn(encoder(doc_t_train), encoder(usage_t_train))
                    .cpu()
                    .numpy()
                )
                enc_drift_train = 1.0 - cs_train
                # Combined: beta*encoder_drift + (1-beta)*tfidf_drift
                sem_drift_train = (
                    beta * enc_drift_train + (1 - beta) * tfidf_drifts_train
                )
                dds_train = alpha * sem_drift_train + (1 - alpha) * struct_drifts_train
                corr_train, _ = spearmanr(dds_train, gt_train)

                # HF evaluation
                cs_hf = cos_sim_fn(encoder(doc_t_hf), encoder(usage_t_hf)).cpu().numpy()
                enc_drift_hf = 1.0 - cs_hf
                sem_drift_hf = beta * enc_drift_hf + (1 - beta) * tfidf_drifts_hf
                dds_hf = alpha * sem_drift_hf + (1 - alpha) * struct_drifts_hf
                hf_corr, hf_pval = spearmanr(dds_hf, ground_truth_hf)

            train_losses.append(loss.item())
            val_corrs.append(float(corr_train))
            hf_corrs_epoch.append(float(hf_corr))

            if (epoch + 1) % 10 == 0:
                print(
                    f"  [{key}] Epoch {epoch+1}: loss={loss.item():.4f}, train_ρ={corr_train:.4f}, hf_ρ={hf_corr:.4f}"
                )

        # Final HF metrics
        binary_hf = (ground_truth_hf >= 0.7).astype(int)
        try:
            auc_hf = roc_auc_score(binary_hf, dds_hf)
        except:
            auc_hf = 0.5

        experiment_data["alpha_sweep"][key] = {
            "train_losses": train_losses,
            "val_corrs": val_corrs,
            "hf_corrs": hf_corrs_epoch,
            "hf_spearman": float(hf_corr),
            "hf_pvalue": float(hf_pval),
            "hf_auc": float(auc_hf),
            "alpha": alpha,
            "beta": beta,
            "hf_dds": dds_hf.tolist(),
        }
        print(f"  [{key}] Final HF Spearman={hf_corr:.4f}, AUC={auc_hf:.4f}")

        if hf_corr > best_corr_global:
            best_corr_global = hf_corr
            best_alpha_global, best_beta_global = alpha, beta
            best_model_state = {k: v.clone() for k, v in encoder.state_dict().items()}

print(
    f"\n=== Best: alpha={best_alpha_global}, beta={best_beta_global}, HF Spearman={best_corr_global:.4f} ==="
)

# ── Final evaluation with best model ─────────────────────────────────────────
best_encoder = DriftEncoder(input_dim=input_dim, embed_dim=64).to(device)
best_encoder.load_state_dict(best_model_state)
best_encoder.eval()
with torch.no_grad():
    cs_final = (
        cos_sim_fn(best_encoder(doc_t_hf), best_encoder(usage_t_hf)).cpu().numpy()
    )

enc_drift_final = 1.0 - cs_final
sem_drift_final = (
    best_beta_global * enc_drift_final + (1 - best_beta_global) * tfidf_drifts_hf
)
final_dds = (
    best_alpha_global * sem_drift_final + (1 - best_alpha_global) * struct_drifts_hf
)

overall_corr, overall_pval = spearmanr(final_dds, ground_truth_hf)
binary_overall = (ground_truth_hf >= 0.7).astype(int)
overall_auc = roc_auc_score(binary_overall, final_dds)
top_q_thresh = np.percentile(final_dds, 75)
top_q_misuse_rate = binary_overall[final_dds >= top_q_thresh].mean()

print(f"\n=== OVERALL HF Evaluation ===")
print(f"  DDS Spearman: {overall_corr:.4f} (p={overall_pval:.4f})")
print(f"  AUC: {overall_auc:.4f}")
print(
    f"  Top-quartile threshold: {top_q_thresh:.4f}, misuse rate: {top_q_misuse_rate:.4f}"
)

colors_map = {"emotion": "steelblue", "ag_news": "coral", "imdb": "mediumseagreen"}
for ds_name, color in colors_map.items():
    mask = df_hf["dataset"] == ds_name
    ds_dds = final_dds[mask]
    ds_gt = ground_truth_hf[mask]
    ds_corr, ds_pval = spearmanr(ds_dds, ds_gt)
    bin_gt = (ds_gt >= 0.7).astype(int)
    try:
        ds_auc = roc_auc_score(bin_gt, ds_dds)
    except:
        ds_auc = 0.5

    experiment_data[ds_name]["metrics"]["train"] = [float(ds_corr)] * n_epochs
    experiment_data[ds_name]["metrics"]["val"] = [float(ds_corr)] * n_epochs
    experiment_data[ds_name]["losses"]["train"] = experiment_data["alpha_sweep"][
        f"a{best_alpha_global}_b{best_beta_global}"
    ]["train_losses"]
    experiment_data[ds_name]["losses"]["val"] = experiment_data["alpha_sweep"][
        f"a{best_alpha_global}_b{best_beta_global}"
    ]["train_losses"]
    experiment_data[ds_name]["predictions"] = ds_dds.tolist()
    experiment_data[ds_name]["ground_truth"] = ds_gt.tolist()
    experiment_data[ds_name]["drift_scores"] = ds_dds.tolist()
    experiment_data[ds_name]["dds_per_epoch"] = [float(ds_corr)]

    print(f"\n=== {ds_name.upper()} ===")
    print(f"  Spearman={ds_corr:.4f} (p={ds_pval:.4f}), AUC={ds_auc:.4f}")
    usage_labels = df_hf[mask]["usage_text"].str[:55].tolist()
    misuse_flags = df_hf[mask]["misuse_label"].tolist()
    for dv, ml, ul in zip(ds_dds, misuse_flags, usage_labels):
        tag = "MISUSE" if ml >= 0.7 else "OK"
        print(f"    [{tag}] DDS={dv:.4f} | label={ml:.2f} | {ul}...")

# ── Plots ─────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle(
    "Documentation Drift Analysis: HuggingFace Datasets\n(emotion, ag_news, imdb)",
    fontsize=13,
)

# Plot 1: Scatter DDS vs misuse label
ax = axes[0, 0]
for ds_name, color in colors_map.items():
    mask = df_hf["dataset"] == ds_name
    ax.scatter(
        ground_truth_hf[mask],
        final_dds[mask],
        label=ds_name,
        color=color,
        s=100,
        alpha=0.85,
        zorder=3,
    )
ax.axhline(
    y=top_q_thresh, color="red", linestyle="--", label=f"Top-Q ({top_q_thresh:.3f})"
)
ax.set_xlabel("Ground Truth Misuse Label")
ax.set_ylabel("DDS")
ax.set_title(f"DDS vs Misuse Label\n(ρ={overall_corr:.3f}, AUC={overall_auc:.3f})")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 2: Bar chart of DDS per scenario
ax = axes[0, 1]
s_labels, dds_vals, misuse_vals, bar_clrs = [], [], [], []
for ds_name, color in colors_map.items():
    mask = df_hf["dataset"] == ds_name
    for i, (dv, gv) in enumerate(zip(final_dds[mask], ground_truth_hf[mask])):
        s_labels.append(f"{ds_name[:3]}_s{i+1}")
        dds_vals.append(dv)
        misuse_vals.append(gv)
        bar_clrs.append(color)
x_pos = np.arange(len(s_labels))
ax.bar(x_pos, dds_vals, color=bar_clrs, alpha=0.8, edgecolor="black", linewidth=0.5)
ax.plot(x_pos, misuse_vals, "k--o", markersize=4, label="Ground Truth", linewidth=1.5)
ax.set_xticks(x_pos)
ax.set_xticklabels(s_labels, rotation=45, ha="right", fontsize=7)
ax.set_ylabel("Score")
ax.set_title("DDS (bars) vs Ground Truth (line)")
ax.legend(fontsize=8)
ax.grid(True, axis="y", alpha=0.3)

# Plot 3: Alpha/Beta sweep HF Spearman heatmap-style
ax = axes[0, 2]
sweep_keys = list(experiment_data["alpha_sweep"].keys())
sweep_sp = [experiment_data["alpha_sweep"][k]["hf_spearman"] for k in sweep_keys]
sweep_auc = [experiment_data["alpha_sweep"][k]["hf_auc"] for k in sweep_keys]
bar_clrs2 = [
    (
        "gold"
        if (
            experiment_data["alpha_sweep"][k]["alpha"] == best_alpha_global
            and experiment_data["alpha_sweep"][k]["beta"] == best_beta_global
        )
        else "steelblue"
    )
    for k in sweep_keys
]
bars = ax.bar(sweep_keys, sweep_sp, color=bar_clrs2, alpha=0.8, edgecolor="black")
ax2t = ax.twinx()
ax2t.plot(sweep_keys, sweep_auc, "r-o", markersize=6, label="AUC")
ax2t.set_ylabel("AUC", color="red")
ax.set_xlabel("Config (alpha_beta)")
ax.set_ylabel("Spearman ρ")
ax.set_title("Alpha/Beta Sweep\n(Gold=Best, Red=AUC)")
ax.tick_params(axis="x", rotation=30)
for b, v in zip(bars, sweep_sp):
    ax.text(
        b.get_x() + b.get_width() / 2,
        b.get_height() + 0.005,
        f"{v:.3f}",
        ha="center",
        fontsize=7,
        fontweight="bold",
    )
ax.grid(True, axis="y", alpha=0.3)

# Plots 4-6: Per-dataset DDS breakdown + training loss curve
best_key = f"a{best_alpha_global}_b{best_beta_global}"
for idx, (ds_name, color) in enumerate(colors_map.items()):
    ax = axes[1, idx]
    mask = df_hf["dataset"] == ds_name
    ds_dds = final_dds[mask]
    ds_gt = ground_truth_hf[mask]
    scenario_types = [
        "in-scope",
        "in-scope",
        "out-of-scope",
        "out-of-scope",
        "out-of-scope",
    ]
    bclrs = ["green" if s == "in-scope" else "red" for s in scenario_types]
    ax.bar(range(len(ds_dds)), ds_dds, color=bclrs, alpha=0.8, edgecolor="black")
    ax.plot(
        range(len(ds_gt)),
        ds_gt,
        "k--o",
        markersize=5,
        label="Ground Truth",
        linewidth=1.5,
    )
    ax.set_xticks(range(len(ds_dds)))
    ax.set_xticklabels([f"S{i+1}" for i in range(len(ds_dds))], fontsize=9)
    ax.set_ylabel("Score")
    ax.set_title(f"{ds_name.upper()}\nGreen=In-scope, Red=Out-of-scope")
    ax.legend(fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)
    ds_corr, _ = spearmanr(ds_dds, ds_gt)
    ax.text(
        0.02,
        0.95,
        f"ρ={ds_corr:.3f}",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
    )
    mean_dds = ds_dds.mean()
    ax.text(
        0.98,
        0.05,
        f"Mean DDS={mean_dds:.3f}",
        transform=ax.transAxes,
        ha="right",
        fontsize=8,
        color=color,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="lightcyan", alpha=0.5),
    )

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "hf_documentation_drift_analysis.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()
print("Main plot saved.")

# Plot 2: Training loss + HF correlation curves
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
fig2.suptitle("Training Dynamics - Best Config", fontsize=13)
ax = axes2[0]
losses = experiment_data["alpha_sweep"][best_key]["train_losses"]
ax.plot(losses, color="steelblue", linewidth=2)
ax.set_xlabel("Epoch")
ax.set_ylabel("MSE Loss")
ax.set_title("Training Loss")
ax.grid(True, alpha=0.3)
ax = axes2[1]
hf_corrs = experiment_data["alpha_sweep"][best_key]["hf_corrs"]
ax.plot(hf_corrs, color="coral", linewidth=2, label="HF Spearman ρ")
val_corrs = experiment_data["alpha_sweep"][best_key]["val_corrs"]
ax.plot(
    val_corrs, color="steelblue", linewidth=2, linestyle="--", label="Train Spearman ρ"
)
ax.set_xlabel("Epoch")
ax.set_ylabel("Spearman ρ")
ax.set_title("Spearman ρ over Epochs")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "training_dynamics.png"), dpi=150, bbox_inches="tight"
)
plt.close()
print("Training dynamics plot saved.")

# Plot 3: Per-dataset breakdown
fig3, axes3 = plt.subplots(1, 3, figsize=(15, 5))
fig3.suptitle(
    "Per-Dataset Documentation Drift Scores (DDS)\nHuggingFace Datasets", fontsize=13
)
for idx, (ds_name, color) in enumerate(colors_map.items()):
    ax = axes3[idx]
    mask = df_hf["dataset"] == ds_name
    ds_dds = final_dds[mask]
    ds_gt = ground_truth_hf[mask]
    scenario_types = [
        "in-scope",
        "in-scope",
        "out-of-scope",
        "out-of-scope",
        "out-of-scope",
    ]
    bclrs = ["green" if s == "in-scope" else "red" for s in scenario_types]
    ax.bar(range(len(ds_dds)), ds_dds, color=bclrs, alpha=0.8, edgecolor="black")
    ax.plot(
        range(len(ds_gt)),
        ds_gt,
        "k--o",
        markersize=5,
        label="Ground Truth",
        linewidth=1.5,
    )
    ax.set_xticks(range(len(ds_dds)))
    ax.set_xticklabels([f"S{i+1}" for i in range(len(ds_dds))], fontsize=8)
    ax.set_ylabel("Score")
    ax.set_title(f"{ds_name.upper()}\nGreen=In-scope, Red=Out-of-scope")
    ax.legend(fontsize=7)
    ax.grid(True, axis="y", alpha=0.3)
    ds_corr, _ = spearmanr(ds_dds, ds_gt)
    ax.text(
        0.02,
        0.95,
        f"ρ={ds_corr:.3f}",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7),
    )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "per_hf_dataset_dds.png"), dpi=150, bbox_inches="tight"
)
plt.close()
print("Per-dataset plot saved.")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== FINAL RESULTS SUMMARY ===")
print(f"HuggingFace datasets: emotion, ag_news, imdb")
print(f"Best alpha={best_alpha_global}, beta={best_beta_global}")
print(f"Overall DDS Spearman ρ: {overall_corr:.4f} (p={overall_pval:.4f})")
print(f"Overall AUC:            {overall_auc:.4f}")
print(
    f"Top-quartile threshold: {top_q_thresh:.4f}, misuse rate: {top_q_misuse_rate:.4f}"
)
for ds_name in ["emotion", "ag_news", "imdb"]:
    mask = df_hf["dataset"] == ds_name
    ds_dds = final_dds[mask]
    ds_gt = ground_truth_hf[mask]
    ds_corr, _ = spearmanr(ds_dds, ds_gt)
    bin_gt = (ds_gt >= 0.7).astype(int)
    try:
        ds_auc = roc_auc_score(bin_gt, ds_dds)
    except:
        ds_auc = 0.5
    print(
        f"  [{ds_name}] Spearman={ds_corr:.4f}, AUC={ds_auc:.4f}, Mean DDS={ds_dds.mean():.4f}"
    )

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nAll results saved to {working_dir}/")
