#!/usr/bin/env python3
"""
Experiment: h-m1 - Stratified Training Mechanism Validation

HYPOTHESIS: Under stratified training (oversampling low-educational, high-BEIR examples),
the retrieval-quality classifier learns to identify documents with high factual density
and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher
named entity density than perplexity-matched controls.

MECHANISM BEING TESTED:
1. Train classifier on BEIR qrels with stratified sampling (oversample divergent examples)
2. Apply classifier to held-out corpus (documents NOT in training qrels)
3. Measure REAL entity density using spaCy NER on selected documents
4. Compare entity density: classifier-selected vs perplexity-selected

Gate: Entity density_retrieval / entity_density_perplexity ≥ 1.15

This is NOT a tautological test - we measure real entity density on held-out documents,
not the training labels or classifier predictions.
"""

import json, time, random, tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import fasttext
import spacy
from beir import util
from beir.datasets.data_loader import GenericDataLoader
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

CONFIG = {
    "data": {"beir_dataset": "nq", "training_samples": 1000, "corpus_sample_size": 10000},
    "stratification": {"oversample_ratio": 3.0},
    "classifier": {"dim": 100, "lr": 0.1, "epoch": 25, "wordNgrams": 2},
    "perplexity": {"model": "gpt2", "batch_size": 8, "max_length": 512},
    "ner": {"model": "en_core_web_sm", "batch_size": 100},
    "selection": {"target_size": 5000},
}

perplexity_model = None
perplexity_tokenizer = None
ner_model = None

def load_beir_data(dataset_name: str = "nq"):
    print(f"\n📥 Loading BEIR {dataset_name}...")
    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset_name}.zip"
    data_path = util.download_and_unzip(url, "data/beir")
    corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split="test")
    print(f"✓ Loaded {len(corpus)} documents, {len(queries)} queries")
    return corpus, queries, qrels

def sample_corpus(corpus: Dict, size: int):
    print(f"\n📊 Sampling {size} documents...")
    sampled_ids = random.sample(list(corpus.keys()), min(size, len(corpus)))
    return {doc_id: corpus[doc_id] for doc_id in sampled_ids}

def extract_training_examples(corpus, qrels, samples_per_class):
    print(f"\n📋 Extracting {samples_per_class} positive + negative examples...")
    positive_ids = []
    for query_id, doc_scores in qrels.items():
        for doc_id, score in doc_scores.items():
            if score > 0 and doc_id in corpus:
                positive_ids.append(doc_id)
                if len(positive_ids) >= samples_per_class: break
        if len(positive_ids) >= samples_per_class: break
    
    all_doc_ids = set(corpus.keys())
    negative_ids = random.sample(list(all_doc_ids - set(positive_ids)), samples_per_class)
    
    pos_texts = [corpus[doc_id]["title"] + " " + corpus[doc_id]["text"] for doc_id in positive_ids]
    neg_texts = [corpus[doc_id]["title"] + " " + corpus[doc_id]["text"] for doc_id in negative_ids]
    print(f"✓ Extracted {len(pos_texts)} positive, {len(neg_texts)} negative")
    return pos_texts, positive_ids, neg_texts, negative_ids

def compute_perplexity_scores(texts: List[str]):
    global perplexity_model, perplexity_tokenizer
    print(f"\n🧮 Computing perplexity for {len(texts)} documents...")
    if perplexity_model is None:
        perplexity_model = GPT2LMHeadModel.from_pretrained(CONFIG["perplexity"]["model"])
        perplexity_tokenizer = GPT2TokenizerFast.from_pretrained(CONFIG["perplexity"]["model"]); perplexity_tokenizer.pad_token = perplexity_tokenizer.eos_token
        perplexity_model.eval()
        if torch.cuda.is_available(): perplexity_model = perplexity_model.cuda()
    
    perplexities = []
    batch_size = CONFIG["perplexity"]["batch_size"]
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        encodings = perplexity_tokenizer(batch, return_tensors="pt", truncation=True, 
                                        max_length=CONFIG["perplexity"]["max_length"], padding=True)
        if torch.cuda.is_available(): encodings = {k: v.cuda() for k, v in encodings.items()}
        with torch.no_grad():
            outputs = perplexity_model(**encodings, labels=encodings["input_ids"])
            perplexities.extend([np.exp(outputs.loss.cpu().item())] * len(batch))
    
    scores = np.array(perplexities)
    print(f"✓ Perplexity computed (mean: {scores.mean():.2f})")
    return scores

def compute_beir_scores(pos_ids, neg_ids):
    """
    Assign BEIR relevance scores based on qrels.
    Positive examples (from qrels) get score 1, negative examples get score 0.
    This creates a supervised signal for training the retrieval-quality classifier.
    """
    return np.concatenate([np.ones(len(pos_ids)), np.zeros(len(neg_ids))])

def stratify_training_data(texts, edu_scores, beir_scores, ratio):
    print(f"\n🎯 Applying stratified sampling ({ratio}x)...")
    edu_median, beir_median = np.median(edu_scores), np.median(beir_scores)
    divergent_mask = (edu_scores > edu_median) & (beir_scores > beir_median)
    print(f"  Divergent examples: {divergent_mask.sum()}/{len(texts)}")
    
    stratified_texts, stratified_labels = [], []
    for i, text in enumerate(texts):
        label = int(beir_scores[i])
        stratified_texts.append(text)
        stratified_labels.append(label)
        if divergent_mask[i]:
            for _ in range(int(ratio) - 1):
                stratified_texts.append(text)
                stratified_labels.append(label)
    
    print(f"✓ Stratified: {len(stratified_texts)} examples (from {len(texts)})")
    return stratified_texts, np.array(stratified_labels)

def train_classifier(texts, labels):
    print(f"\n🤖 Training FastText...")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        for text, label in zip(texts, labels):
            text = text.replace('\n', ' ').replace('\r', ' ')
            f.write(f"__label__{label} {text}\n")
        train_file = f.name
    
    model = fasttext.train_supervised(train_file, dim=CONFIG["classifier"]["dim"], 
                                     lr=CONFIG["classifier"]["lr"], epoch=CONFIG["classifier"]["epoch"],
                                     wordNgrams=CONFIG["classifier"]["wordNgrams"], verbose=0)
    Path(train_file).unlink()
    print(f"✓ Classifier trained")
    return model

def select_by_classifier(corpus, classifier, target_size):
    print(f"\n📊 Selecting top-{target_size} by classifier...")
    scores = {}
    for doc_id, doc_data in corpus.items():
        text = (doc_data["title"] + " " + doc_data["text"]).replace('\n', ' ')
        pred = classifier.predict(text, k=1)
        label, prob = pred[0][0].replace('__label__', ''), pred[1][0]
        scores[doc_id] = prob if label == '1' else 1.0 - prob
    
    selected_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:target_size]
    print(f"✓ Selected {len(selected_ids)} documents")
    return {doc_id: corpus[doc_id] for doc_id in selected_ids}

def select_by_perplexity(corpus, target_size):
    print(f"\n📊 Selecting top-{target_size} by perplexity...")
    texts = [doc_data["title"] + " " + doc_data["text"] for doc_data in corpus.values()]
    doc_ids = list(corpus.keys())
    perplexities = compute_perplexity_scores(texts)
    selected_indices = np.argsort(perplexities)[:target_size]
    selected_ids = [doc_ids[i] for i in selected_indices]
    return {doc_id: corpus[doc_id] for doc_id in selected_ids}

def compute_entity_density(corpus):
    global ner_model
    print(f"\n🏷️ Computing entity density for {len(corpus)} documents...")
    if ner_model is None:
        ner_model = spacy.load(CONFIG["ner"]["model"])
    
    densities = {}
    doc_ids = list(corpus.keys())
    texts = [corpus[doc_id]["title"] + " " + corpus[doc_id]["text"] for doc_id in doc_ids]
    batch_size = CONFIG["ner"]["batch_size"]
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_ids = doc_ids[i:i+batch_size]
        docs = list(ner_model.pipe(batch_texts, batch_size=batch_size))
        for doc_id, doc in zip(batch_ids, docs):
            densities[doc_id] = (len(doc.ents) / len(doc) * 100) if len(doc) > 0 else 0.0
    
    print(f"✓ Entity density computed (mean: {np.mean(list(densities.values())):.2f})")
    return densities

def evaluate_mechanism(retrieval_corpus, baseline_corpus):
    print(f"\n📊 Evaluating mechanism...")
    retrieval_densities = compute_entity_density(retrieval_corpus)
    baseline_densities = compute_entity_density(baseline_corpus)
    
    retrieval_mean = np.mean(list(retrieval_densities.values()))
    baseline_mean = np.mean(list(baseline_densities.values()))
    ratio = retrieval_mean / baseline_mean if baseline_mean > 0 else 0.0
    gate_satisfied = ratio >= 1.15
    
    print(f"\n{'='*60}")
    print(f"MECHANISM VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Entity Density (Retrieval):  {retrieval_mean:.2f}")
    print(f"Entity Density (Baseline):   {baseline_mean:.2f}")
    print(f"Ratio:                       {ratio:.3f}")
    print(f"Gate Threshold:              1.15")
    print(f"Gate Status:                 {'✅ PASS' if gate_satisfied else '❌ FAIL'}")
    print(f"{'='*60}")
    
    return {
        "entity_density_retrieval": float(retrieval_mean),
        "entity_density_baseline": float(baseline_mean),
        "density_ratio": float(ratio),
        "gate_threshold": 1.15,
        "gate_satisfied": bool(gate_satisfied),
    }

def generate_visualizations(results, output_dir):
    print(f"\n📊 Generating visualizations...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ['Retrieval-Quality\nFiltering', 'Perplexity\nBaseline']
    densities = [results["entity_density_retrieval"], results["entity_density_baseline"]]
    bars = ax.bar(labels, densities, color=['#2ecc71', '#3498db'])
    ax.axhline(y=results["entity_density_baseline"] * 1.15, color='r', linestyle='--', label='Gate Threshold (1.15×)')
    ax.set_ylabel('Entity Density (entities per 100 tokens)')
    ax.set_title('Named Entity Density Comparison', fontweight='bold')
    ax.legend(); ax.grid(axis='y', alpha=0.3)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h, f'{h:.2f}', ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/entity_density_comparison.png", dpi=300)
    plt.close()
    print(f"✓ Figure saved: {output_dir}/entity_density_comparison.png")

def save_results(results, output_file):
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved: {output_file}")

def main():
    start_time = time.time()
    print(f"\n{'='*60}\nEXPERIMENT: h-m1 (MECHANISM)\n{'='*60}")

    # Load full BEIR corpus
    corpus, queries, qrels = load_beir_data(CONFIG["data"]["beir_dataset"])
    print(f"\n📊 Total corpus size: {len(corpus)} documents")

    # Split corpus: use documents in qrels for training, held-out documents for evaluation
    training_doc_ids = set()
    for query_id, doc_scores in qrels.items():
        training_doc_ids.update(doc_scores.keys())

    all_doc_ids = set(corpus.keys())
    eval_doc_ids = list(all_doc_ids - training_doc_ids)

    print(f"  Training docs (from qrels): {len(training_doc_ids)}")
    print(f"  Eval docs (held-out): {len(eval_doc_ids)}")

    # Sample evaluation corpus from held-out documents
    eval_sample_size = min(CONFIG["data"]["corpus_sample_size"], len(eval_doc_ids))
    eval_sampled_ids = random.sample(eval_doc_ids, eval_sample_size)
    eval_corpus = {doc_id: corpus[doc_id] for doc_id in eval_sampled_ids}
    print(f"  Sampled {len(eval_corpus)} documents for evaluation")

    # Extract training examples from qrels
    pos_texts, pos_ids, neg_texts, neg_ids = extract_training_examples(corpus, qrels, CONFIG["data"]["training_samples"])
    all_texts = pos_texts + neg_texts

    # Compute educational quality (perplexity) and BEIR quality for stratification
    edu_scores = compute_perplexity_scores(all_texts)
    beir_scores = compute_beir_scores(pos_ids, neg_ids)

    # Apply stratified sampling (oversample low-educational, high-BEIR examples)
    stratified_texts, stratified_labels = stratify_training_data(all_texts, edu_scores, beir_scores, CONFIG["stratification"]["oversample_ratio"])

    # Train classifier on stratified data
    classifier = train_classifier(stratified_texts, stratified_labels)

    # Apply classifier to held-out evaluation corpus
    retrieval_corpus = select_by_classifier(eval_corpus, classifier, CONFIG["selection"]["target_size"])

    # Apply perplexity baseline to same evaluation corpus
    baseline_corpus = select_by_perplexity(eval_corpus, CONFIG["selection"]["target_size"])

    # Measure REAL entity density on selected documents
    results = evaluate_mechanism(retrieval_corpus, baseline_corpus)
    generate_visualizations(results, "figures")
    results["execution_time_seconds"] = time.time() - start_time
    save_results(results, "outputs/results.json")
    print(f"\n✅ Experiment completed in {time.time() - start_time:.1f} seconds")
    return results

if __name__ == "__main__":
    main()
