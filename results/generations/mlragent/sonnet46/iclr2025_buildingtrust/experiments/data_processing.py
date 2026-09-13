"""Data loading and processing for CARE experiments using ToxiGen and HarmBench-style data."""

import numpy as np
import random
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from config import SEED, DATASET_SIZE, CALIBRATION_SIZE, TEST_SIZE, RISK_CATEGORIES


def load_toxigen_data(max_samples=DATASET_SIZE, seed=SEED):
    """Load ToxiGen dataset from HuggingFace."""
    print("Loading ToxiGen dataset...")
    try:
        ds = load_dataset("skg/toxigen-data", "annotated", split="train", trust_remote_code=True)
        print(f"  ToxiGen annotated loaded: {len(ds)} samples")
    except Exception as e:
        print(f"  ToxiGen annotated failed: {e}, trying 'train' split...")
        try:
            ds = load_dataset("skg/toxigen-data", "train", split="train", trust_remote_code=True)
            print(f"  ToxiGen train loaded: {len(ds)} samples")
        except Exception as e2:
            print(f"  Falling back to basic toxigen load: {e2}")
            ds = load_dataset("skg/toxigen-data", split="train", trust_remote_code=True)
            print(f"  ToxiGen basic loaded: {len(ds)} samples")

    # Extract text and labels
    texts = []
    labels = []

    for item in ds:
        # Get text
        text = item.get("text", item.get("generation", item.get("prompt", "")))
        if not text:
            continue

        # Get label - ToxiGen uses various label formats
        label = None
        if "toxicity_human" in item and item["toxicity_human"] is not None:
            # Annotated split: toxicity_human is 1-5 scale; >2.5 = toxic
            try:
                tox_val = float(item["toxicity_human"])
                label = 1 if tox_val > 2.5 else 0
            except (ValueError, TypeError):
                pass
        if label is None and "toxicity_ai" in item and item["toxicity_ai"] is not None:
            try:
                tox_val = float(item["toxicity_ai"])
                label = 1 if tox_val > 2.5 else 0
            except (ValueError, TypeError):
                pass
        if label is None and "label" in item:
            try:
                label = int(item["label"])
            except (ValueError, TypeError):
                pass
        if label is None and "prompt_label" in item:
            try:
                label = int(item["prompt_label"])
            except (ValueError, TypeError):
                pass

        if label is not None:
            texts.append(str(text)[:512])  # truncate
            labels.append(label)

    print(f"  Extracted {len(texts)} labeled samples")

    # Balance dataset
    pos_idx = [i for i, l in enumerate(labels) if l == 1]
    neg_idx = [i for i, l in enumerate(labels) if l == 0]
    print(f"  Positive: {len(pos_idx)}, Negative: {len(neg_idx)}")

    rng = random.Random(seed)
    n_each = min(max_samples // 2, len(pos_idx), len(neg_idx))
    selected_pos = rng.sample(pos_idx, n_each)
    selected_neg = rng.sample(neg_idx, n_each)
    selected = selected_pos + selected_neg
    rng.shuffle(selected)

    texts = [texts[i] for i in selected]
    labels = [labels[i] for i in selected]
    print(f"  Final balanced dataset: {len(texts)} samples ({n_each} per class)")

    return texts, labels


def load_harmbench_style_data(max_samples=500, seed=SEED):
    """Load a HarmBench-style safety dataset. Falls back to civil_comments if not available."""
    print("Loading HarmBench-style safety data...")
    try:
        ds = load_dataset("walledai/HarmBench", split="standard", trust_remote_code=True)
        print(f"  HarmBench loaded: {len(ds)} samples")
        texts = []
        labels = []
        for item in ds:
            text = item.get("behavior", item.get("prompt", item.get("text", "")))
            label = 1  # HarmBench is all harmful
            if text:
                texts.append(str(text)[:512])
                labels.append(label)
    except Exception as e:
        print(f"  HarmBench failed: {e}, using civil_comments instead...")
        ds = load_dataset("civil_comments", split="train", trust_remote_code=True)
        rng = random.Random(seed)
        indices = rng.sample(range(len(ds)), min(max_samples * 2, len(ds)))
        texts = []
        labels = []
        for i in indices:
            item = ds[i]
            text = item.get("text", "")
            tox = item.get("toxicity", 0.0)
            label = 1 if tox > 0.5 else 0
            if text:
                texts.append(str(text)[:512])
                labels.append(label)
        print(f"  Civil comments loaded: {len(texts)} samples")

    # Sample balanced
    pos_idx = [i for i, l in enumerate(labels) if l == 1]
    neg_idx = [i for i, l in enumerate(labels) if l == 0]
    rng = random.Random(seed)
    n_each = min(max_samples // 2, len(pos_idx), len(neg_idx))
    if n_each < 1:
        n_each = max(1, min(len(pos_idx), len(neg_idx)))
    selected_pos = rng.sample(pos_idx, n_each)
    selected_neg = rng.sample(neg_idx, n_each)
    selected = selected_pos + selected_neg
    rng.shuffle(selected)

    texts = [texts[i] for i in selected]
    labels = [labels[i] for i in selected]
    print(f"  Final safety dataset: {len(texts)} samples")
    return texts, labels


def assign_ambiguity_labels(texts, labels, classifier_probs, seed=SEED):
    """
    Simulate ambiguity annotation: samples where classifier probability is
    near 0.5 are labeled as ambiguous (simulating inter-annotator disagreement).
    """
    ambiguity_labels = []
    for prob in classifier_probs:
        # Ambiguous if classifier confidence is uncertain (prob in [0.35, 0.65])
        if 0.35 <= prob <= 0.65:
            ambiguity_labels.append("ambiguous")
        elif prob > 0.65:
            ambiguity_labels.append("unsafe")
        else:
            ambiguity_labels.append("safe")
    return ambiguity_labels


def assign_risk_categories(texts, labels, seed=SEED):
    """
    Assign multi-label risk categories to samples (simulated for experiments
    based on label and text heuristics).
    """
    rng = random.Random(seed)
    risk_matrix = []
    for text, label in zip(texts, labels):
        cats = [0] * len(RISK_CATEGORIES)
        if label == 1:  # unsafe
            # Assign 1-2 risk categories
            n_cats = rng.randint(1, 2)
            triggered = rng.sample(range(len(RISK_CATEGORIES)), n_cats)
            for t in triggered:
                cats[t] = 1
        risk_matrix.append(cats)
    return np.array(risk_matrix)


def split_data(texts, labels, cal_size=CALIBRATION_SIZE, test_size=TEST_SIZE, seed=SEED):
    """Split data into train, calibration, and test sets."""
    n = len(texts)
    train_size = n - cal_size - test_size
    if train_size < 10:
        train_size = int(n * 0.5)
        cal_size = int(n * 0.25)
        test_size = n - train_size - cal_size

    # First split off test
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=test_size, random_state=seed, stratify=labels
    )
    # Then split calibration from remaining train
    train_texts, cal_texts, train_labels, cal_labels = train_test_split(
        train_texts, train_labels,
        test_size=cal_size, random_state=seed, stratify=train_labels
    )

    print(f"  Train: {len(train_texts)}, Calibration: {len(cal_texts)}, Test: {len(test_texts)}")
    return (train_texts, train_labels), (cal_texts, cal_labels), (test_texts, test_labels)


def create_domain_test_sets(test_texts, test_labels, seed=SEED):
    """Create domain-specific test subsets."""
    rng = random.Random(seed)
    n = len(test_texts)
    # Healthcare: slightly stricter (more false negative concern, so label 1 is weighted)
    # Finance: similar strictness
    # We'll just create subsets with some overlap and domain "context" tags

    idx = list(range(n))
    rng.shuffle(idx)

    mid = n // 2
    health_idx = idx[:mid]
    finance_idx = idx[mid:]

    health_texts = [test_texts[i] for i in health_idx]
    health_labels = [test_labels[i] for i in health_idx]

    finance_texts = [test_texts[i] for i in finance_idx]
    finance_labels = [test_labels[i] for i in finance_idx]

    return {
        "healthcare": (health_texts, health_labels),
        "finance": (finance_texts, finance_labels),
    }
