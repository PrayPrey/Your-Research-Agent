"""H-C1: Cross-Benchmark Four-Way AUROC Ranking on TruthfulQA."""
import os
import sys
import json
import torch

# Run from h-c1/code/
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from data import load_truthfulqa_yesno, compute_em_labels
from generate import load_base_model, generate_k_samples, generate_greedy_with_logits
from uncertainty import compute_te, compute_se, compute_scg, compute_vc
from evaluate import compute_all_aurocs, load_hm4_baselines
from visualize import generate_all_figures

_CACHE = os.path.join(os.path.dirname(__file__), "generation_cache.json")


def _save_cache(data):
    with open(_CACHE, "w") as f:
        json.dump(data, f)
    print(f"[cache] saved to {_CACHE}")


def _load_cache():
    if os.path.exists(_CACHE):
        with open(_CACHE) as f:
            data = json.load(f)
        print(f"[cache] loaded from {_CACHE} (n={len(data.get('questions', []))})")
        return data
    return None


def main():
    cfg = Config()
    os.makedirs(cfg.figures_dir, exist_ok=True)

    cache = _load_cache()

    if cache:
        questions = cache["questions"]
        gold_answers = cache["gold_answers"]
        samples = cache["samples"]
        greedy_answers = cache["greedy_answers"]
        logprobs = cache["logprobs"]
        em_labels = cache["em_labels"]
        n_correct = sum(em_labels)
        print(f"[cache] skipping generation. n={len(questions)}, em_correct={n_correct}")
    else:
        # 1. Load data
        print("=" * 60)
        print("Step 1: Loading TruthfulQA yes/no subset")
        questions, gold_answers = load_truthfulqa_yesno(seed=cfg.seed, max_n=cfg.n_questions)
        print(f"Loaded {len(questions)} questions")
        assert len(questions) >= 100, f"Too few questions: {len(questions)}"

        # 2. Load base model and generate
        print("=" * 60)
        print("Step 2: Loading Llama-2-7B-hf and generating samples")
        model_7b, tokenizer_7b = load_base_model(cfg)

        print("Step 2a: Generating K=10 stochastic samples (SE/SCG)")
        samples = generate_k_samples(
            questions, model_7b, tokenizer_7b,
            K=cfg.K, temperature=cfg.temperature_sample,
            max_new_tokens=cfg.max_new_tokens_gen,
            seed=cfg.seed, batch_size=cfg.batch_size
        )

        print("Step 2b: Generating greedy answers + logprobs (TE)")
        greedy_answers, logprobs = generate_greedy_with_logits(
            questions, model_7b, tokenizer_7b,
            max_new_tokens=cfg.max_new_tokens_gen,
            batch_size=cfg.batch_size
        )

        # 3. Compute EM labels
        print("=" * 60)
        print("Step 3: Computing EM labels")
        em_labels = compute_em_labels(greedy_answers, gold_answers)
        n_correct = sum(em_labels)
        print(f"EM labels: {n_correct}/{len(em_labels)} correct ({n_correct/len(em_labels)*100:.1f}%)")

        del model_7b, tokenizer_7b
        torch.cuda.empty_cache()

        _save_cache({
            "questions": questions,
            "gold_answers": gold_answers,
            "samples": samples,
            "greedy_answers": greedy_answers,
            "logprobs": logprobs,
            "em_labels": em_labels,
        })

    # 4. TE computation
    print("=" * 60)
    print("Step 4: Computing Token Entropy (TE)")
    te_scores = compute_te(logprobs)
    print(f"TE scores: min={min(te_scores):.4f}, max={max(te_scores):.4f}, "
          f"mean={sum(te_scores)/len(te_scores):.4f}")

    # 5. SE computation
    print("=" * 60)
    print("Step 5: Computing Semantic Entropy (SE) — NLI clustering")
    se_scores = compute_se(samples, cfg.nli_model_id)
    print(f"SE scores: min={min(se_scores):.4f}, max={max(se_scores):.4f}, "
          f"mean={sum(se_scores)/len(se_scores):.4f}")

    # 6. SCG computation
    print("=" * 60)
    print("Step 6: Computing SelfCheckGPT-BERTScore (SCG)")
    scg_scores = compute_scg(samples)
    print(f"SCG scores: min={min(scg_scores):.4f}, max={max(scg_scores):.4f}, "
          f"mean={sum(scg_scores)/len(scg_scores):.4f}")

    # 7. VC computation
    print("=" * 60)
    print("Step 7: Computing Verbalized Confidence (VC) with Llama-2-7B-Chat")
    vc_scores, fallback_count, raw_confidences = compute_vc(questions, cfg)
    parse_rate = 1.0 - (fallback_count / len(questions))
    print(f"VC parse rate: {parse_rate:.3f} (fallbacks: {fallback_count}/{len(questions)})")
    if parse_rate < cfg.parse_rate_gate:
        print(f"WARNING: VC parse rate {parse_rate:.3f} below gate {cfg.parse_rate_gate}")

    # 8. AUROC evaluation
    print("=" * 60)
    print("Step 8: Computing Bootstrap AUROC for all 4 methods")
    results = compute_all_aurocs(se_scores, scg_scores, te_scores, vc_scores, em_labels, cfg)

    # 9. Load H-M4 baselines for cross-benchmark comparison
    print("=" * 60)
    print("Step 9: Loading H-M4 TriviaQA baselines")
    hm4_baselines = load_hm4_baselines(cfg.hm4_results_path)
    print(f"H-M4 baselines: SE={hm4_baselines['auroc_se']:.4f}, "
          f"TE={hm4_baselines['auroc_te']:.4f}, VC={hm4_baselines['auroc_vc']:.4f}")

    # 10. Generate figures
    print("=" * 60)
    print("Step 10: Generating figures")
    generate_all_figures(results, hm4_baselines, raw_confidences, cfg, cfg.figures_dir)

    # 11. Save results
    print("=" * 60)
    print("Step 11: Saving results")
    output = {
        "hypothesis": "h-c1",
        "n_questions": len(questions),
        "benchmark": "truthfulqa_yesno",
        "auroc_se": results["auroc_se"],
        "auroc_se_ci": results["auroc_se_ci"],
        "auroc_scg": results["auroc_scg"],
        "auroc_scg_ci": results["auroc_scg_ci"],
        "auroc_te": results["auroc_te"],
        "auroc_te_ci": results["auroc_te_ci"],
        "auroc_vc": results["auroc_vc"],
        "auroc_vc_ci": results["auroc_vc_ci"],
        "gate_primary": results["gate_primary"],
        "gate_secondary": results["gate_secondary"],
        "gate_tertiary": results["gate_tertiary"],
        "gate_passed": results["gate_passed"],
        "ranking": results["ranking"],
        "parse_rate_vc": parse_rate,
        "seed": cfg.seed,
        "em_correct_rate": n_correct / len(em_labels),
        "hm4_baselines": hm4_baselines,
    }

    with open(cfg.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {cfg.results_path}")

    # 12. Final verdict
    print("=" * 60)
    print("FINAL VERDICT:")
    print(f"  Ranking: {results['ranking']}")
    print(f"  Gate primary (SE > TE): {results['gate_primary']}")
    print(f"  Gate secondary (VC < TE): {results['gate_secondary']}")
    print(f"  Gate tertiary (full ranking): {results['gate_tertiary']}")
    print(f"  Gate PASSED: {results['gate_passed']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
