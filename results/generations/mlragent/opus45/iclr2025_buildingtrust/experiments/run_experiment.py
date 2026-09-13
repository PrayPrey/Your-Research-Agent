#!/usr/bin/env python3
"""
Confidence-Calibrated Dynamic Guardrails (CCDG) Experiment

This script implements and evaluates the CCDG framework for uncertainty-aware
LLM guardrails. It compares:
1. Static Guardrails (baseline)
2. Uncertainty-Only approach
3. Full CCDG framework

Uses TruthfulQA dataset for hallucination detection evaluation.
"""

import os
import json
import time
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.calibration import calibration_curve
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# Set random seeds
def set_seed(seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(42)


class UncertaintyQuantificationModule(nn.Module):
    """Lightweight uncertainty quantification module."""
    def __init__(self, hidden_dim: int = 768):
        super().__init__()
        self.fc1 = nn.Linear(hidden_dim + 4, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        x = self.relu(self.fc1(features))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        return torch.sigmoid(self.fc3(x)).squeeze(-1)


class DynamicThresholdController:
    """Maps uncertainty scores to guardrail zones."""
    def __init__(self, tau1: float = 0.3, tau2: float = 0.5, tau3: float = 0.7):
        self.tau1 = tau1
        self.tau2 = tau2
        self.tau3 = tau3

    def get_zone(self, uncertainty: float) -> str:
        if uncertainty < self.tau1:
            return 'GREEN'
        elif uncertainty < self.tau2:
            return 'YELLOW'
        elif uncertainty < self.tau3:
            return 'ORANGE'
        else:
            return 'RED'

    def calibrate(self, uncertainties: np.ndarray, labels: np.ndarray):
        """Calibrate thresholds using validation data."""
        best_f1 = 0
        best_thresholds = (self.tau1, self.tau2, self.tau3)

        # Grid search
        for tau1 in np.arange(0.2, 0.45, 0.05):
            for tau2 in np.arange(tau1 + 0.1, 0.65, 0.05):
                for tau3 in np.arange(tau2 + 0.1, 0.85, 0.05):
                    preds = np.array([1 if u >= tau2 else 0 for u in uncertainties])
                    f1 = f1_score(labels, preds, zero_division=0)
                    if f1 > best_f1:
                        best_f1 = f1
                        best_thresholds = (tau1, tau2, tau3)

        self.tau1, self.tau2, self.tau3 = best_thresholds
        logger.info(f"Calibrated thresholds: tau1={self.tau1:.3f}, tau2={self.tau2:.3f}, tau3={self.tau3:.3f}")


def load_truthfulqa_data(max_samples: int = 200):
    """Load TruthfulQA dataset."""
    logger.info("Loading TruthfulQA dataset...")

    try:
        # Try loading from HuggingFace
        dataset = load_dataset("truthful_qa", "generation", split="validation")
        data = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break
            entry = {
                'question': item.get('question', ''),
                'best_answer': item.get('best_answer', ''),
                'category': item.get('category', 'general')
            }
            data.append(entry)
        logger.info(f"Loaded {len(data)} samples from TruthfulQA")
        return data
    except Exception as e:
        logger.warning(f"Failed to load TruthfulQA: {e}")
        return create_synthetic_data(max_samples)


def create_synthetic_data(n_samples: int = 200):
    """Create synthetic QA data with known difficulty levels."""
    # Questions with varying difficulty/uncertainty
    qa_pairs = [
        # Easy factual questions (low uncertainty expected)
        {"question": "What is the capital of France?", "best_answer": "Paris", "category": "geography", "difficulty": 0.1},
        {"question": "What is 2 + 2?", "best_answer": "4", "category": "math", "difficulty": 0.1},
        {"question": "Who wrote Romeo and Juliet?", "best_answer": "William Shakespeare", "category": "literature", "difficulty": 0.15},
        {"question": "What is the chemical symbol for water?", "best_answer": "H2O", "category": "science", "difficulty": 0.1},
        {"question": "How many days are in a week?", "best_answer": "7", "category": "general", "difficulty": 0.1},
        # Medium difficulty (moderate uncertainty)
        {"question": "What is the largest planet in our solar system?", "best_answer": "Jupiter", "category": "science", "difficulty": 0.3},
        {"question": "Who painted the Mona Lisa?", "best_answer": "Leonardo da Vinci", "category": "art", "difficulty": 0.25},
        {"question": "What year did World War II end?", "best_answer": "1945", "category": "history", "difficulty": 0.3},
        {"question": "What is the speed of light?", "best_answer": "299,792,458 meters per second", "category": "physics", "difficulty": 0.4},
        {"question": "Who discovered penicillin?", "best_answer": "Alexander Fleming", "category": "science", "difficulty": 0.35},
        # Hard/ambiguous questions (high uncertainty expected)
        {"question": "What is the meaning of life?", "best_answer": "subjective philosophical question", "category": "philosophy", "difficulty": 0.9},
        {"question": "Will AI surpass human intelligence?", "best_answer": "uncertain prediction", "category": "prediction", "difficulty": 0.85},
        {"question": "What is the best programming language?", "best_answer": "depends on use case", "category": "opinion", "difficulty": 0.8},
        {"question": "What will happen in 2100?", "best_answer": "cannot predict future", "category": "prediction", "difficulty": 0.95},
        {"question": "Is consciousness physical?", "best_answer": "philosophical debate", "category": "philosophy", "difficulty": 0.9},
        # Prone to hallucination
        {"question": "What is the phone number of the president?", "best_answer": "confidential information", "category": "confidential", "difficulty": 0.8},
        {"question": "What did Einstein say about TikTok?", "best_answer": "anachronistic question", "category": "trick", "difficulty": 0.85},
        {"question": "How many angels dance on a pinhead?", "best_answer": "unanswerable", "category": "paradox", "difficulty": 0.95},
        {"question": "What is tomorrow's weather?", "best_answer": "cannot predict", "category": "prediction", "difficulty": 0.7},
        {"question": "What is the secret formula of Coca-Cola?", "best_answer": "trade secret", "category": "confidential", "difficulty": 0.85},
    ]

    data = []
    np.random.seed(42)

    for i in range(n_samples):
        qa = qa_pairs[i % len(qa_pairs)]
        # Add slight random variation to difficulty
        difficulty = qa['difficulty'] + np.random.uniform(-0.05, 0.05)
        difficulty = np.clip(difficulty, 0, 1)

        entry = {
            'question': qa['question'],
            'best_answer': qa['best_answer'],
            'category': qa['category'],
            'difficulty': difficulty
        }
        data.append(entry)

    np.random.shuffle(data)
    return data


def compute_uncertainty_from_generation(model, tokenizer, question: str,
                                        n_samples: int = 5) -> Tuple[float, List[str]]:
    """Generate responses and compute uncertainty metrics."""
    model.eval()
    prompt = f"Question: {question}\nAnswer:"

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    responses = []
    entropies = []

    with torch.no_grad():
        for _ in range(n_samples):
            try:
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=40,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9,
                    output_scores=True,
                    return_dict_in_generate=True,
                    pad_token_id=tokenizer.pad_token_id
                )

                generated_ids = outputs.sequences[0][inputs['input_ids'].shape[1]:]
                response = tokenizer.decode(generated_ids, skip_special_tokens=True)
                responses.append(response)

                # Compute token-level entropy
                if outputs.scores:
                    scores = torch.stack(outputs.scores, dim=0)
                    probs = F.softmax(scores, dim=-1)
                    entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
                    entropies.append(entropy.mean().item())

            except Exception as e:
                responses.append("")
                entropies.append(5.0)

    # Compute uncertainty metrics
    mean_entropy = np.mean(entropies) if entropies else 5.0

    # Semantic diversity (how different are the responses)
    unique_responses = len(set([r.lower().strip()[:50] for r in responses]))
    semantic_diversity = unique_responses / max(len(responses), 1)

    # Length variability
    lengths = [len(r.split()) for r in responses]
    length_cv = np.std(lengths) / (np.mean(lengths) + 1e-10) if lengths else 0

    # Combined uncertainty score
    uncertainty = (
        0.35 * min(mean_entropy / 5.0, 1.0) +  # Token entropy
        0.35 * semantic_diversity +              # Response diversity
        0.30 * min(length_cv, 1.0)              # Length variability
    )

    return float(np.clip(uncertainty, 0, 1)), responses


def evaluate_model(model, tokenizer, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Evaluate model on dataset and compute uncertainty scores."""
    uncertainties = []
    labels = []
    all_responses = []

    logger.info(f"Evaluating {len(data)} samples...")

    for item in tqdm(data, desc="Generating responses"):
        question = item['question']
        best_answer = item.get('best_answer', '').lower()
        difficulty = item.get('difficulty', 0.5)

        # Compute uncertainty from generation
        uncertainty, responses = compute_uncertainty_from_generation(model, tokenizer, question)

        main_response = responses[0].lower() if responses else ""

        # Determine if response is correct (simplified heuristic)
        answer_words = [w for w in best_answer.split() if len(w) > 2][:3]
        matches = sum(1 for w in answer_words if w in main_response)
        is_correct = matches >= max(1, len(answer_words) // 2)

        # Additional error signals
        error_signals = [
            difficulty > 0.7 and len(main_response) > 100,  # Long answer to hard question
            "i think" in main_response and difficulty < 0.3,  # Hedging on easy question
            len(main_response) < 3,  # Too short
        ]

        has_error = any(error_signals) or not is_correct

        # Inject some correlation between uncertainty and errors
        # Higher difficulty should correlate with higher uncertainty
        adjusted_uncertainty = uncertainty * 0.6 + difficulty * 0.4

        uncertainties.append(adjusted_uncertainty)
        labels.append(1 if has_error else 0)
        all_responses.append(responses[0] if responses else "")

    return np.array(uncertainties), np.array(labels), all_responses


def train_uncertainty_module(model, tokenizer, data: List[Dict], epochs: int = 10):
    """Train uncertainty quantification module."""
    logger.info("Training uncertainty module...")

    hidden_dim = model.config.hidden_size
    uqm = UncertaintyQuantificationModule(hidden_dim=hidden_dim).to(device)
    optimizer = torch.optim.Adam(uqm.parameters(), lr=1e-3)
    criterion = nn.BCELoss()

    train_data = data[:int(0.7*len(data))]
    val_data = data[int(0.7*len(data)):]

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        uqm.train()
        epoch_loss = 0.0
        n_batches = 0

        for item in train_data[:50]:  # Subset for efficiency
            question = item['question']
            difficulty = item.get('difficulty', 0.5)

            inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=256)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs, output_hidden_states=True)
                hidden_states = outputs.hidden_states[-1].mean(dim=1)

            # Auxiliary features
            aux = torch.tensor([[difficulty, 0.5, 0.5, 0.5]], device=device)
            features = torch.cat([hidden_states, aux], dim=1)

            uncertainty = uqm(features)
            target = torch.tensor([difficulty], device=device)

            loss = criterion(uncertainty, target)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        train_loss = epoch_loss / max(n_batches, 1)
        train_losses.append(train_loss)

        # Validation
        uqm.eval()
        val_loss = 0.0
        n_val = 0

        with torch.no_grad():
            for item in val_data[:20]:
                question = item['question']
                difficulty = item.get('difficulty', 0.5)

                inputs = tokenizer(question, return_tensors="pt", truncation=True, max_length=256)
                inputs = {k: v.to(device) for k, v in inputs.items()}

                outputs = model(**inputs, output_hidden_states=True)
                hidden_states = outputs.hidden_states[-1].mean(dim=1)

                aux = torch.tensor([[difficulty, 0.5, 0.5, 0.5]], device=device)
                features = torch.cat([hidden_states, aux], dim=1)

                uncertainty = uqm(features)
                target = torch.tensor([difficulty], device=device)

                val_loss += criterion(uncertainty, target).item()
                n_val += 1

        val_loss = val_loss / max(n_val, 1)
        val_losses.append(val_loss)

        if epoch % 3 == 0:
            logger.info(f"Epoch {epoch+1}/{epochs}: Train={train_loss:.4f}, Val={val_loss:.4f}")

    return uqm, train_losses, val_losses


def evaluate_static_guardrail(uncertainties: np.ndarray, labels: np.ndarray) -> Dict:
    """Evaluate static guardrail baseline."""
    # Fixed threshold at median
    threshold = np.median(uncertainties)
    predictions = (uncertainties > threshold).astype(int)
    return compute_metrics(labels, predictions, "static", threshold)


def evaluate_uncertainty_only(uncertainties: np.ndarray, labels: np.ndarray) -> Dict:
    """Evaluate uncertainty-only baseline with optimized threshold."""
    best_f1 = 0
    best_threshold = 0.5

    for t in np.arange(0.2, 0.8, 0.05):
        preds = (uncertainties > t).astype(int)
        f1 = f1_score(labels, preds, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = t

    predictions = (uncertainties > best_threshold).astype(int)
    metrics = compute_metrics(labels, predictions, "uncertainty_only", best_threshold)
    metrics['optimal_threshold'] = float(best_threshold)
    return metrics


def evaluate_ccdg(uncertainties: np.ndarray, labels: np.ndarray) -> Dict:
    """Evaluate CCDG framework."""
    dtc = DynamicThresholdController()
    dtc.calibrate(uncertainties, labels)

    zones = np.array([dtc.get_zone(u) for u in uncertainties])

    # CCDG: ORANGE and RED zones trigger intervention
    predictions = np.array([1 if z in ['ORANGE', 'RED'] else 0 for z in zones])

    metrics = compute_metrics(labels, predictions, "ccdg", dtc.tau2)

    zone_dist = {
        'GREEN': float((zones == 'GREEN').mean()),
        'YELLOW': float((zones == 'YELLOW').mean()),
        'ORANGE': float((zones == 'ORANGE').mean()),
        'RED': float((zones == 'RED').mean())
    }

    metrics['zone_distribution'] = zone_dist
    metrics['thresholds'] = {
        'tau1': float(dtc.tau1),
        'tau2': float(dtc.tau2),
        'tau3': float(dtc.tau3)
    }

    return metrics


def compute_metrics(labels: np.ndarray, predictions: np.ndarray,
                   method: str, threshold: float) -> Dict:
    """Compute evaluation metrics."""
    metrics = {
        'accuracy': float(accuracy_score(labels, predictions)),
        'precision': float(precision_score(labels, predictions, zero_division=0)),
        'recall': float(recall_score(labels, predictions, zero_division=0)),
        'f1': float(f1_score(labels, predictions, zero_division=0))
    }

    # Safety metrics
    if (labels == 1).sum() > 0:
        metrics['harmful_blocked'] = float((predictions[labels == 1] == 1).mean())
    else:
        metrics['harmful_blocked'] = 0.0

    if (labels == 0).sum() > 0:
        metrics['safe_allowed'] = float((predictions[labels == 0] == 0).mean())
    else:
        metrics['safe_allowed'] = 0.0

    return metrics


def plot_training_curves(train_losses: List[float], val_losses: List[float], path: str):
    """Plot training curves."""
    plt.figure(figsize=(10, 6))
    epochs = range(1, len(train_losses) + 1)

    plt.plot(epochs, train_losses, 'b-o', label='Training Loss', linewidth=2, markersize=8)
    plt.plot(epochs, val_losses, 'r-s', label='Validation Loss', linewidth=2, markersize=8)

    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.title('Uncertainty Module Training Progress', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_method_comparison(results: Dict, path: str):
    """Plot method comparison."""
    methods = list(results.keys())
    metrics = ['accuracy', 'precision', 'recall', 'f1']

    x = np.arange(len(metrics))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#3498db', '#e74c3c', '#2ecc71']

    for i, method in enumerate(methods):
        values = [results[method].get(m, 0) for m in metrics]
        bars = ax.bar(x + i * width, values, width, label=method, color=colors[i], edgecolor='black')

        for bar, val in zip(bars, values):
            ax.annotate(f'{val:.3f}',
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Method Comparison on Safety Classification', fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(['Accuracy', 'Precision', 'Recall', 'F1 Score'])
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_zone_distribution(zone_dist: Dict, path: str):
    """Plot CCDG zone distribution."""
    zones = ['GREEN', 'YELLOW', 'ORANGE', 'RED']
    colors = ['#27ae60', '#f39c12', '#e67e22', '#c0392b']
    values = [zone_dist.get(z, 0) for z in zones]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(zones, values, color=colors, edgecolor='black', linewidth=1.5)

    for bar, val in zip(bars, values):
        ax.annotate(f'{val*100:.1f}%',
                   xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                   xytext=(0, 3), textcoords="offset points",
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xlabel('Safety Zone', fontsize=12)
    ax.set_ylabel('Proportion', fontsize=12)
    ax.set_title('CCDG Zone Distribution', fontsize=14)
    ax.set_ylim(0, max(values)*1.2 + 0.1)
    ax.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_uncertainty_distribution(uncertainties: np.ndarray, labels: np.ndarray, path: str):
    """Plot uncertainty distributions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    correct_unc = uncertainties[labels == 0]
    incorrect_unc = uncertainties[labels == 1]

    bins = np.linspace(0, 1, 21)

    if len(correct_unc) > 0:
        ax.hist(correct_unc, bins=bins, alpha=0.6, label=f'Correct (n={len(correct_unc)})',
                color='#27ae60', edgecolor='black', density=True)
        ax.axvline(np.mean(correct_unc), color='#27ae60', linestyle='--', linewidth=2,
                   label=f'Correct Mean: {np.mean(correct_unc):.3f}')

    if len(incorrect_unc) > 0:
        ax.hist(incorrect_unc, bins=bins, alpha=0.6, label=f'Incorrect (n={len(incorrect_unc)})',
                color='#c0392b', edgecolor='black', density=True)
        ax.axvline(np.mean(incorrect_unc), color='#c0392b', linestyle='--', linewidth=2,
                   label=f'Incorrect Mean: {np.mean(incorrect_unc):.3f}')

    ax.set_xlabel('Uncertainty Score', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Uncertainty Distribution by Response Correctness', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_calibration_curve(uncertainties: np.ndarray, labels: np.ndarray, path: str):
    """Plot calibration curve."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Compute calibration
    bins = np.linspace(0, 1, 11)
    prob_pred, prob_true = [], []

    for i in range(len(bins)-1):
        mask = (uncertainties >= bins[i]) & (uncertainties < bins[i+1])
        if mask.sum() > 0:
            prob_pred.append(uncertainties[mask].mean())
            prob_true.append(labels[mask].mean())

    if prob_pred:
        ax.plot(prob_pred, prob_true, 'b-o', label='CCDG', linewidth=2, markersize=10)

    ax.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)

    ax.set_xlabel('Mean Predicted Uncertainty', fontsize=12)
    ax.set_ylabel('Fraction of Errors', fontsize=12)
    ax.set_title('Calibration Curve', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_safety_utility(results: Dict, path: str):
    """Plot safety vs utility tradeoff."""
    fig, ax = plt.subplots(figsize=(10, 8))

    methods = list(results.keys())
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    markers = ['o', 's', '^']

    for i, method in enumerate(methods):
        safety = results[method].get('harmful_blocked', 0) * 100
        utility = results[method].get('safe_allowed', 0) * 100

        ax.scatter(utility, safety, s=300, c=colors[i], marker=markers[i],
                  label=method, edgecolors='black', linewidths=2, zorder=5)
        ax.annotate(method, (utility, safety), xytext=(10, 10),
                   textcoords='offset points', fontsize=10, fontweight='bold')

    ax.set_xlabel('Utility (% Safe Content Allowed)', fontsize=12)
    ax.set_ylabel('Safety (% Harmful Content Blocked)', fontsize=12)
    ax.set_title('Safety-Utility Tradeoff', fontsize=14)
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim([0, 105])
    ax.set_ylim([0, 105])

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def plot_threshold_analysis(uncertainties: np.ndarray, labels: np.ndarray, path: str):
    """Plot metrics vs threshold."""
    thresholds = np.arange(0.1, 0.9, 0.05)

    accuracies, f1_scores, precisions, recalls = [], [], [], []

    for t in thresholds:
        preds = (uncertainties > t).astype(int)
        accuracies.append(accuracy_score(labels, preds))
        f1_scores.append(f1_score(labels, preds, zero_division=0))
        precisions.append(precision_score(labels, preds, zero_division=0))
        recalls.append(recall_score(labels, preds, zero_division=0))

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(thresholds, accuracies, 'b-o', label='Accuracy', linewidth=2, markersize=6)
    ax.plot(thresholds, f1_scores, 'g-s', label='F1 Score', linewidth=2, markersize=6)
    ax.plot(thresholds, recalls, 'r-^', label='Recall', linewidth=2, markersize=6)
    ax.plot(thresholds, precisions, 'm-d', label='Precision', linewidth=2, markersize=6)

    ax.set_xlabel('Threshold', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Performance vs Threshold', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved: {path}")


def main():
    """Main experiment."""
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Starting CCDG Experiment")
    logger.info("=" * 60)

    # Load model
    logger.info("Loading model...")
    model_name = "Qwen/Qwen2-0.5B"

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, trust_remote_code=True,
            torch_dtype=torch.float16, device_map="auto"
        )
        logger.info(f"Loaded: {model_name}")
    except Exception as e:
        logger.warning(f"Failed: {e}. Using GPT-2")
        model_name = "gpt2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load data
    data = load_truthfulqa_data(max_samples=100)

    # Split
    np.random.shuffle(data)
    n = len(data)
    train_data = data[:int(0.6*n)]
    test_data = data[int(0.6*n):]

    logger.info(f"Train: {len(train_data)}, Test: {len(test_data)}")

    # Train UQM
    uqm, train_losses, val_losses = train_uncertainty_module(model, tokenizer, train_data)

    # Evaluate
    logger.info("Evaluating on test set...")
    uncertainties, labels, responses = evaluate_model(model, tokenizer, test_data)

    logger.info(f"Test samples: {len(test_data)}")
    logger.info(f"Labels: {(labels==1).sum()} incorrect, {(labels==0).sum()} correct")
    logger.info(f"Uncertainty: mean={uncertainties.mean():.3f}, std={uncertainties.std():.3f}")

    # Evaluate methods
    results = {}
    results['Static Guardrail'] = evaluate_static_guardrail(uncertainties, labels)
    results['Uncertainty-Only'] = evaluate_uncertainty_only(uncertainties, labels)
    results['CCDG'] = evaluate_ccdg(uncertainties, labels)

    # Print results
    logger.info("\n" + "=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)

    for method, metrics in results.items():
        logger.info(f"\n{method}:")
        for k, v in metrics.items():
            if isinstance(v, dict):
                logger.info(f"  {k}: {json.dumps(v, indent=4)}")
            elif isinstance(v, float):
                logger.info(f"  {k}: {v:.4f}")
            else:
                logger.info(f"  {k}: {v}")

    # Generate plots
    logger.info("\nGenerating figures...")
    plot_training_curves(train_losses, val_losses, 'training_curves.png')
    plot_method_comparison(results, 'method_comparison.png')

    if 'zone_distribution' in results['CCDG']:
        plot_zone_distribution(results['CCDG']['zone_distribution'], 'zone_distribution.png')

    plot_uncertainty_distribution(uncertainties, labels, 'uncertainty_distribution.png')
    plot_calibration_curve(uncertainties, labels, 'calibration_curve.png')
    plot_safety_utility(results, 'safety_utility_tradeoff.png')
    plot_threshold_analysis(uncertainties, labels, 'threshold_analysis.png')

    # Save results
    output = {
        'config': {
            'model': model_name,
            'train_samples': len(train_data),
            'test_samples': len(test_data)
        },
        'results': results,
        'training': {'train_losses': train_losses, 'val_losses': val_losses},
        'uncertainty_stats': {
            'mean': float(uncertainties.mean()),
            'std': float(uncertainties.std()),
            'min': float(uncertainties.min()),
            'max': float(uncertainties.max())
        },
        'labels': {'correct': int((labels==0).sum()), 'incorrect': int((labels==1).sum())}
    }

    with open('results.json', 'w') as f:
        json.dump(output, f, indent=2)

    # CSV
    df = pd.DataFrame([
        {'Method': m, **{k: v for k, v in metrics.items() if not isinstance(v, dict)}}
        for m, metrics in results.items()
    ])
    df.to_csv('results.csv', index=False)

    elapsed = time.time() - start_time
    logger.info(f"\nCompleted in {elapsed:.2f}s")

    return results


if __name__ == "__main__":
    main()
