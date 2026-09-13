"""H-M2 Robustness Evaluation - Cosine similarity, routing consistency, accuracy drop"""
from typing import Dict, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


def eval_paraphrase_robustness(ctx, engine, variant: str) -> Dict:
    """Evaluate robustness to paraphrases (wordnet or embedding)."""
    print(f"Evaluating {variant} paraphrase robustness...")

    # Encode all originals once
    orig_emb = ctx.probe.encode(ctx.X_test)
    orig_preds = ctx.probe.classifier.predict(orig_emb)

    all_cosines = []
    consistent_count = 0
    total_paras = 0
    per_sample = []

    for i, (text, orig_pred) in enumerate(tqdm(zip(ctx.X_test, orig_preds), total=len(ctx.X_test))):
        if variant == "wordnet":
            paras = engine.wordnet_paraphrases(text)
        else:
            paras = engine.embedding_paraphrases(text, ctx.probe.encoder)

        if not paras:
            per_sample.append({"idx": i, "text": text, "paras": 0, "cosines": [], "consistent": []})
            continue

        para_emb = ctx.probe.encode(paras)
        sims = cosine_similarity(orig_emb[i:i+1], para_emb)[0]
        para_preds = ctx.probe.classifier.predict(para_emb)
        consistent = (para_preds == orig_pred).astype(int).tolist()

        all_cosines.extend(sims.tolist())
        consistent_count += sum(consistent)
        total_paras += len(paras)

        per_sample.append({
            "idx": i,
            "text": text[:100],
            "paras": len(paras),
            "cosines": sims.tolist(),
            "consistent": consistent,
            "y_true": int(ctx.y_test[i]),
        })

    cosine_mean = float(np.mean(all_cosines)) if all_cosines else 0.0
    cosine_min = float(np.min(all_cosines)) if all_cosines else 0.0
    routing_consistency = consistent_count / total_paras if total_paras > 0 else 0.0

    return {
        "variant": variant,
        "cosine_mean": cosine_mean,
        "cosine_min": cosine_min,
        "routing_consistency": routing_consistency,
        "total_paraphrases": total_paras,
        "per_sample": per_sample,
    }


def eval_masking_robustness(ctx, engine, ratio: float, mode: str) -> Dict:
    """Evaluate robustness to keyword or random masking."""
    print(f"Evaluating {mode} masking (ratio={ratio})...")

    # Original accuracy
    orig_metrics = ctx.probe.evaluate(ctx.X_test, ctx.y_test, k=3)

    # Build TF-IDF keyword set from corpus
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=200)
    vectorizer.fit(ctx.X_test)
    tfidf_words = set(vectorizer.get_feature_names_out())

    # Mask texts
    if mode == "keyword":
        masked_texts = [engine.mask_keywords(x, ratio, tfidf_words) for x in ctx.X_test]
    else:
        masked_texts = [engine.mask_random(x, ratio) for x in ctx.X_test]

    masked_metrics = ctx.probe.evaluate(masked_texts, ctx.y_test, k=3)
    accuracy_drop = orig_metrics["top1_accuracy"] - masked_metrics["top1_accuracy"]

    return {
        "mode": mode,
        "ratio": ratio,
        "original_acc": orig_metrics["top1_accuracy"],
        "masked_acc": masked_metrics["top1_accuracy"],
        "accuracy_drop": accuracy_drop,
        "original_top3": orig_metrics["top3_accuracy"],
        "masked_top3": masked_metrics["top3_accuracy"],
    }


def per_class_consistency(ctx, per_sample_records: List[Dict]) -> Dict[str, float]:
    """Aggregate routing consistency per task family for heatmap."""
    class_stats = {}

    for rec in per_sample_records:
        if not rec.get("consistent"):
            continue
        class_idx = rec.get("y_true")
        if class_idx is None:
            continue
        class_name = ctx.task_families[class_idx] if class_idx < len(ctx.task_families) else f"class_{class_idx}"

        if class_name not in class_stats:
            class_stats[class_name] = {"consistent": 0, "total": 0}
        class_stats[class_name]["consistent"] += sum(rec["consistent"])
        class_stats[class_name]["total"] += len(rec["consistent"])

    return {
        name: stats["consistent"] / stats["total"] if stats["total"] > 0 else 0.0
        for name, stats in class_stats.items()
    }
