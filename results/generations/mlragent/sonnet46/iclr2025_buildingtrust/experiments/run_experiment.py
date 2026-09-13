"""
Main experiment runner for CARE (Calibrated Adaptive Rejection with Explanations).
Tests the hypothesis that uncertainty-calibrated, explainable, domain-adaptive
guardrails improve safety classification performance over baselines.
"""

import os
import sys
import json
import time
import random
import logging
import numpy as np
import torch

# Set seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    RESULTS_DIR, ALPHA_VALUES, DEFAULT_ALPHA, ANTHROPIC_API_KEY,
    RISK_CATEGORIES, SEED, DATASET_SIZE, CALIBRATION_SIZE, TEST_SIZE
)
from data_processing import (
    load_toxigen_data, assign_risk_categories,
    split_data, create_domain_test_sets
)
from safety_classifier import (
    TfidfSafetyClassifier, RoBERTaSafetyClassifier,
    ConformaPredictor, evaluate_classifier, compute_ece
)
from baselines import (
    OpenAIModerationBaseline, BertBinaryClassifier,
    LlamaGuardBaseline, evaluate_baseline
)
from explanation_generator import (
    RiskCategoryClassifier, generate_explanation_llm,
    evaluate_explanation_faithfulness_batch, POLICY_TEXT
)
from domain_adaptation import DomainAdaptivePolicyLayer, evaluate_domain_adaptation
from visualization import (
    plot_coverage_vs_alpha, plot_precision_recall_comparison,
    plot_roc_comparison, plot_metrics_comparison,
    plot_ambiguity_distribution, plot_domain_adaptation_results,
    plot_ece_comparison, plot_explanation_faithfulness,
    plot_ablation_study
)

# Setup logging
os.makedirs(RESULTS_DIR, exist_ok=True)
log_path = os.path.join(RESULTS_DIR, "log.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="w"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


def log_section(title):
    log.info("=" * 60)
    log.info(f"  {title}")
    log.info("=" * 60)


def main():
    start_time = time.time()
    log_section("CARE Experiment: Starting")
    log.info(f"Results directory: {RESULTS_DIR}")
    log.info(f"GPU available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # =========================================================
    # STEP 1: Load Data
    # =========================================================
    log_section("Step 1: Loading Data")
    texts, labels = load_toxigen_data(max_samples=DATASET_SIZE, seed=SEED)
    log.info(f"Total samples: {len(texts)}")
    log.info(f"Positive (unsafe): {sum(labels)}, Negative (safe): {len(labels) - sum(labels)}")

    (train_texts, train_labels), (cal_texts, cal_labels), (test_texts, test_labels) = \
        split_data(texts, labels, cal_size=CALIBRATION_SIZE, test_size=TEST_SIZE, seed=SEED)

    log.info(f"Train: {len(train_texts)}, Cal: {len(cal_texts)}, Test: {len(test_texts)}")

    # Assign multi-label risk categories
    log.info("Assigning risk categories...")
    train_risk = assign_risk_categories(train_texts, train_labels, seed=SEED)
    cal_risk = assign_risk_categories(cal_texts, cal_labels, seed=SEED)
    test_risk = assign_risk_categories(test_texts, test_labels, seed=SEED)

    # Create domain test sets
    domain_test_sets = create_domain_test_sets(test_texts, test_labels, seed=SEED)
    log.info(f"Domain test sets created: {list(domain_test_sets.keys())}")

    # =========================================================
    # STEP 2: Train CARE Base Classifier (TF-IDF + LR)
    # =========================================================
    log_section("Step 2: Train CARE Base Classifier")
    log.info("Training TF-IDF + Logistic Regression base classifier...")
    tfidf_clf = TfidfSafetyClassifier(seed=SEED)
    tfidf_clf.fit(train_texts, train_labels)
    log.info("  TF-IDF classifier trained.")

    # Evaluate base classifier
    base_metrics, base_probs = evaluate_classifier(
        tfidf_clf, test_texts, test_labels, name="CARE-Base (TF-IDF+LR)"
    )
    log.info(f"  CARE-Base metrics: {base_metrics}")

    # =========================================================
    # STEP 3: Load RoBERTa Safety Classifier (main CARE model)
    # =========================================================
    log_section("Step 3: Load RoBERTa Safety Classifier")
    device = 0 if torch.cuda.is_available() else -1
    roberta_clf = RoBERTaSafetyClassifier(device=device)
    roberta_clf.load()

    log.info("Computing RoBERTa predictions on all splits...")
    roberta_train_probs = roberta_clf.predict_proba(train_texts)
    roberta_cal_probs = roberta_clf.predict_proba(cal_texts)
    roberta_test_probs = roberta_clf.predict_proba(test_texts)

    roberta_metrics, roberta_probs = evaluate_classifier(
        roberta_clf, test_texts, test_labels, name="CARE (RoBERTa)"
    )
    log.info(f"  CARE (RoBERTa) metrics: {roberta_metrics}")

    # =========================================================
    # STEP 4: Conformal Prediction (UQM)
    # =========================================================
    log_section("Step 4: Conformal Prediction Calibration (UQM)")
    conformal_pred = ConformaPredictor(roberta_clf)
    nonconf_scores = conformal_pred.calibrate(cal_texts, cal_labels, alpha_values=ALPHA_VALUES)
    log.info(f"  Conformal calibration complete. Thresholds: {conformal_pred.quantile_thresholds}")

    # Evaluate coverage
    coverage_rates = conformal_pred.evaluate_coverage(test_texts, test_labels)
    log.info(f"  Coverage rates: {coverage_rates}")
    max_deviation = max(abs(coverage_rates[a] - (1 - a)) for a in ALPHA_VALUES)
    log.info(f"  Max coverage deviation: {max_deviation:.4f}")

    # Get decisions at different alpha levels
    decisions_by_alpha = {}
    for alpha in ALPHA_VALUES:
        decisions, _, _ = conformal_pred.predict_set(test_texts, alpha=alpha)
        decisions_by_alpha[alpha] = decisions
        ambig_rate = sum(1 for d in decisions if d == "ambiguous") / len(decisions)
        log.info(f"  α={alpha}: {sum(1 for d in decisions if d=='safe')} safe, "
                 f"{sum(1 for d in decisions if d=='unsafe')} unsafe, "
                 f"{sum(1 for d in decisions if d=='ambiguous')} ambiguous "
                 f"(ambig rate={ambig_rate:.3f})")

    # CARE decisions at default alpha
    care_decisions, care_probs_conformal, care_pred_sets = conformal_pred.predict_set(
        test_texts, alpha=DEFAULT_ALPHA
    )
    care_preds = np.array([1 if d == "unsafe" else 0 for d in care_decisions])
    # Ambiguous -> treat as positive (flag for review) for evaluation
    care_preds_conservative = np.array(
        [1 if d in ("unsafe", "ambiguous") else 0 for d in care_decisions]
    )

    # =========================================================
    # STEP 5: Load and Evaluate Baselines
    # =========================================================
    log_section("Step 5: Load and Evaluate Baselines")

    # Baseline 1: OpenAI Moderation (simulated)
    log.info("Evaluating OpenAI Moderation baseline (simulated)...")
    openai_baseline = OpenAIModerationBaseline()
    openai_metrics, openai_probs = evaluate_baseline(
        openai_baseline, test_texts, test_labels, name="OpenAI Moderation (sim.)"
    )
    log.info(f"  OpenAI Moderation: {openai_metrics}")

    # Baseline 2: BERT-based classifier
    log.info("Loading BERT-based classifier...")
    bert_clf = BertBinaryClassifier(device=device)
    bert_clf.load()
    bert_metrics, bert_probs = evaluate_baseline(
        bert_clf, test_texts, test_labels, name="BERT Safety Classifier"
    )
    log.info(f"  BERT: {bert_metrics}")

    # Baseline 3: Llama Guard proxy
    log.info("Loading Llama Guard proxy...")
    llama_guard = LlamaGuardBaseline(device=device)
    llama_guard.load()
    llama_metrics, llama_probs = evaluate_baseline(
        llama_guard, test_texts, test_labels, name="Llama Guard (proxy)"
    )
    log.info(f"  Llama Guard: {llama_metrics}")

    # CARE ablations
    # CARE-NoUQ: RoBERTa without conformal prediction
    care_nouq_metrics = dict(roberta_metrics)
    care_nouq_metrics["name"] = "CARE-NoUQ (No Conformal)"
    log.info(f"  CARE-NoUQ: {care_nouq_metrics}")

    # CARE Full (with UQM, using conservative preds)
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    care_full_metrics = {
        "name": "CARE Full (UQM+DAPL)",
        "accuracy": float(accuracy_score(test_labels, care_preds_conservative)),
        "precision": float(precision_score(test_labels, care_preds_conservative, zero_division=0)),
        "recall": float(recall_score(test_labels, care_preds_conservative, zero_division=0)),
        "f1": float(f1_score(test_labels, care_preds_conservative, zero_division=0)),
        "auroc": float(roc_auc_score(test_labels, care_probs_conformal)),
    }
    log.info(f"  CARE Full: {care_full_metrics}")

    # =========================================================
    # STEP 6: ECE (Calibration Quality)
    # =========================================================
    log_section("Step 6: Calibration Quality (ECE)")
    ece_results = {}
    for name, prbs in [
        ("CARE Full (UQM)", care_probs_conformal),
        ("CARE-NoUQ", roberta_probs),
        ("BERT Safety", bert_probs),
        ("Llama Guard (proxy)", llama_probs),
        ("OpenAI Mod. (sim.)", openai_probs),
    ]:
        ece = compute_ece(prbs, test_labels)
        ece_results[name] = ece
        log.info(f"  ECE {name}: {ece:.4f}")

    # =========================================================
    # STEP 7: Train Risk Category Classifier (EGM)
    # =========================================================
    log_section("Step 7: Train Risk Category Classifier (EGM)")
    risk_clf = RiskCategoryClassifier()
    # Use first 80% of train for fitting, rest for threshold tuning
    n_train = len(train_texts)
    split_pt = int(n_train * 0.8)
    risk_clf.fit(
        train_texts[:split_pt], train_risk[:split_pt],
        val_texts=train_texts[split_pt:],
        val_risk_matrix=train_risk[split_pt:]
    )
    log.info("  Risk category classifier trained.")

    # Evaluate risk categories on test set
    test_triggered = risk_clf.predict_categories(test_texts)
    log.info(f"  Sample triggered categories: {test_triggered[:3]}")

    # Compute per-category faithfulness using a subset
    import anthropic as anthropic_module
    client = anthropic_module.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Generate explanations for a sample (first 20 unsafe samples)
    log_section("Step 7b: Generate and Evaluate Explanations (EGM)")
    unsafe_idx = [i for i, l in enumerate(test_labels) if l == 1][:20]
    explanations = []
    triggered_cats_sample = []
    for i in unsafe_idx:
        cats = test_triggered[i] if test_triggered[i] else ["general_safety_violation"]
        triggered_cats_sample.append(cats)
        expl = generate_explanation_llm(test_texts[i], cats, "unsafe", client=client)
        explanations.append(expl)
        log.info(f"  Sample {i}: cats={cats}, explanation='{expl[:80]}...'")

    # Evaluate faithfulness per category
    overall_faithfulness = evaluate_explanation_faithfulness_batch(
        explanations, triggered_cats_sample
    )
    log.info(f"  Overall faithfulness: {overall_faithfulness:.3f}")

    # Per-category faithfulness
    cat_faithfulness = {}
    for cat in RISK_CATEGORIES:
        relevant_idx = [
            i for i, cats in enumerate(triggered_cats_sample) if cat in cats
        ]
        if relevant_idx:
            cat_expls = [explanations[i] for i in relevant_idx]
            cat_cats = [triggered_cats_sample[i] for i in relevant_idx]
            score = evaluate_explanation_faithfulness_batch(cat_expls, cat_cats)
        else:
            score = overall_faithfulness  # use global as estimate
        cat_faithfulness[cat] = float(score)
        log.info(f"  Faithfulness [{cat}]: {score:.3f}")

    # =========================================================
    # STEP 8: Domain Adaptation (DAPL)
    # =========================================================
    log_section("Step 8: Domain Adaptation (DAPL)")
    dapl = DomainAdaptivePolicyLayer(base_alpha=DEFAULT_ALPHA)

    # We need to add a method to conformal predictor for DAPL
    # Patch it to accept probs directly
    def predict_set_from_probs(probs, alpha):
        if not conformal_pred.calibrated:
            raise RuntimeError("Not calibrated")
        q_hat = conformal_pred.quantile_thresholds[alpha]
        decisions = []
        pred_sets = []
        for prob in probs:
            s_unsafe = 1 - prob
            s_safe = prob
            in_unsafe = s_unsafe <= q_hat
            in_safe = s_safe <= q_hat
            if in_unsafe and in_safe:
                decisions.append("ambiguous")
                pred_sets.append({0, 1})
            elif in_unsafe:
                decisions.append("unsafe")
                pred_sets.append({1})
            elif in_safe:
                decisions.append("safe")
                pred_sets.append({0})
            else:
                decisions.append("ambiguous")
                pred_sets.append(set())
        return decisions, probs, pred_sets

    # Pre-compute probs for domain test sets
    domain_probs = {}
    for domain, (dtexts, dlabels) in domain_test_sets.items():
        domain_probs[domain] = roberta_clf.predict_proba(dtexts)

    # Evaluate DAPL
    domain_results = {}
    for domain, (dtexts, dlabels) in domain_test_sets.items():
        dprobs = domain_probs[domain]
        dlabels_arr = np.array(dlabels)

        # Without DAPL
        decisions_base, _, _ = predict_set_from_probs(dprobs, DEFAULT_ALPHA)
        preds_base = np.array([1 if d in ("unsafe", "ambiguous") else 0 for d in decisions_base])

        # With DAPL: adjust alpha
        eff_alpha = dapl.get_effective_alpha(domain)
        available_alphas = list(conformal_pred.quantile_thresholds.keys())
        closest_alpha = min(available_alphas, key=lambda a: abs(a - eff_alpha))
        decisions_dapl, _, _ = predict_set_from_probs(dprobs, closest_alpha)
        preds_dapl = np.array([1 if d in ("unsafe", "ambiguous") else 0 for d in decisions_dapl])

        from sklearn.metrics import f1_score, precision_score, recall_score
        f1_b = f1_score(dlabels_arr, preds_base, zero_division=0)
        f1_d = f1_score(dlabels_arr, preds_dapl, zero_division=0)
        p_b = precision_score(dlabels_arr, preds_base, zero_division=0)
        p_d = precision_score(dlabels_arr, preds_dapl, zero_division=0)
        r_b = recall_score(dlabels_arr, preds_base, zero_division=0)
        r_d = recall_score(dlabels_arr, preds_dapl, zero_division=0)

        from domain_adaptation import REGULATORY_KNOWLEDGE_BASE
        domain_results[domain] = {
            "f1_base": float(f1_b),
            "f1_dapl": float(f1_d),
            "f1_delta": float(f1_d - f1_b),
            "precision_base": float(p_b),
            "precision_dapl": float(p_d),
            "recall_base": float(r_b),
            "recall_dapl": float(r_d),
            "effective_alpha": float(eff_alpha),
            "base_alpha": float(DEFAULT_ALPHA),
            "regulation": REGULATORY_KNOWLEDGE_BASE.get(domain, {}).get("regulation", "N/A"),
        }
        log.info(f"  Domain {domain}: F1 {f1_b:.3f} -> {f1_d:.3f} (delta={f1_d - f1_b:+.3f})")

    # =========================================================
    # STEP 9: Compile All Results
    # =========================================================
    log_section("Step 9: Compile Results")

    all_metrics = [
        care_full_metrics,
        care_nouq_metrics,
        base_metrics,
        bert_metrics,
        llama_metrics,
        openai_metrics,
    ]

    # For ablation study (subset)
    ablation_metrics = [
        care_full_metrics,
        care_nouq_metrics,
        base_metrics,
        bert_metrics,
        llama_metrics,
    ]

    all_probs_list = [
        care_probs_conformal,
        roberta_probs,
        base_probs,
        bert_probs,
        llama_probs,
        openai_probs,
    ]
    all_names = [m["name"] for m in all_metrics]

    results = {
        "experiment": "CARE: Calibrated Adaptive Rejection with Explanations",
        "dataset": "ToxiGen (balanced, annotated)",
        "dataset_size": len(texts),
        "train_size": len(train_texts),
        "calibration_size": len(cal_texts),
        "test_size": len(test_texts),
        "seed": SEED,
        "alpha_values": ALPHA_VALUES,
        "default_alpha": DEFAULT_ALPHA,
        "coverage_rates": {str(k): v for k, v in coverage_rates.items()},
        "max_coverage_deviation": float(max_deviation),
        "ece_results": ece_results,
        "classifier_metrics": all_metrics,
        "explanation_faithfulness": {
            "overall": float(overall_faithfulness),
            "per_category": cat_faithfulness,
            "n_samples_evaluated": len(explanations),
        },
        "domain_adaptation_results": domain_results,
        "ambiguity_rates": {
            str(alpha): float(
                sum(1 for d in decisions_by_alpha[alpha] if d == "ambiguous") / len(decisions_by_alpha[alpha])
            )
            for alpha in ALPHA_VALUES
        },
    }

    results_path = os.path.join(RESULTS_DIR, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"Results saved to {results_path}")

    # =========================================================
    # STEP 10: Generate Figures
    # =========================================================
    log_section("Step 10: Generating Figures")

    # Figure 1: Coverage calibration
    plot_coverage_vs_alpha(
        coverage_rates,
        os.path.join(RESULTS_DIR, "coverage_calibration.png")
    )

    # Figure 2: Precision-Recall curves
    plot_precision_recall_comparison(
        all_probs_list, test_labels, all_names,
        os.path.join(RESULTS_DIR, "precision_recall_curves.png")
    )

    # Figure 3: ROC curves
    plot_roc_comparison(
        all_probs_list, test_labels, all_names,
        os.path.join(RESULTS_DIR, "roc_curves.png")
    )

    # Figure 4: Metrics bar chart
    plot_metrics_comparison(
        all_metrics,
        os.path.join(RESULTS_DIR, "metrics_comparison.png")
    )

    # Figure 5: Ambiguity distribution by alpha
    plot_ambiguity_distribution(
        decisions_by_alpha,
        os.path.join(RESULTS_DIR, "ambiguity_distribution.png")
    )

    # Figure 6: Domain adaptation results
    plot_domain_adaptation_results(
        domain_results,
        os.path.join(RESULTS_DIR, "domain_adaptation.png")
    )

    # Figure 7: ECE comparison
    plot_ece_comparison(
        ece_results,
        os.path.join(RESULTS_DIR, "ece_comparison.png")
    )

    # Figure 8: Explanation faithfulness
    plot_explanation_faithfulness(
        cat_faithfulness,
        os.path.join(RESULTS_DIR, "explanation_faithfulness.png")
    )

    # Figure 9: Ablation study
    plot_ablation_study(
        ablation_metrics,
        os.path.join(RESULTS_DIR, "ablation_study.png")
    )

    elapsed = time.time() - start_time
    log.info(f"\nTotal experiment time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    log_section("Experiment Complete")

    return results


if __name__ == "__main__":
    results = main()
    print("\n=== CARE Experiment Completed Successfully ===")
    print(f"Results saved to: {RESULTS_DIR}")
