"""Main experiment runner for H-E1: SMC-NLI existence proof."""
import os
import sys

# Run from code/ directory
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(CODE_DIR)
sys.path.insert(0, CODE_DIR)

from config import CFG
from data_pipeline import download_halueval
from evaluate import compute_metrics, plot_figures, save_results
from llm_sampler import LLMSampler
from scorer import SMCEmbedScorer, SMCNLIScorer


def verify_mechanism(sampler: LLMSampler, scorer: SMCNLIScorer, sample_questions: list, n: int = 10) -> None:
    """Sanity check on 5 questions before full experiment."""
    scores = []
    for q_data in sample_questions[:5]:
        samps = sampler.sample(q_data["question"], n=n)
        smc = scorer.score_question(q_data["question"], samps)
        scores.append(smc)
        print(f"Q: {q_data['question'][:50]} | SMC-NLI: {smc:.4f} | Label: {q_data['label']}")

    assert max(scores) - min(scores) > 0.01, "FAIL: SMC-NLI scores degenerate (no variation)"
    assert 0.0 <= min(scores) <= max(scores) <= 1.0, "FAIL: SMC-NLI scores out of [0,1]"
    print("✅ Mechanism verification PASSED")


def main() -> None:
    print("=" * 60)
    print("H-E1: SMC-NLI Existence Proof Experiment")
    print("=" * 60)

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 1. Download / load HaluEval
    os.makedirs("data", exist_ok=True)
    questions_data = download_halueval(
        save_path=CFG["data_path"],
        raw_cache="data/HaluEval_QA/qa_data.json",
        n_questions=CFG["n_questions"],
        seed=CFG["seed"],
    )
    questions = [d["question"] for d in questions_data]
    labels = [d["label"] for d in questions_data]
    print(f"Questions loaded: {len(questions)} (correct={labels.count(0)}, hallucinated={labels.count(1)})")

    # 2. Load models
    sampler = LLMSampler(
        model_id=CFG["llm_model_id"],
        torch_dtype=torch.float16,
        device_map="auto",
    )
    nli_scorer = SMCNLIScorer(
        model_id=CFG["nli_model_id"],
        device=device,
        batch_size=CFG["nli_batch_size"],
    )
    embed_scorer = SMCEmbedScorer(model_id=CFG["embed_model_id"])

    # 3. Mechanism verification (5 questions)
    print("\n--- Mechanism Verification ---")
    verify_mechanism(sampler, nli_scorer, questions_data[:5], n=CFG["n_samples"])

    # 4. Sample all questions (resume if exists)
    print("\n--- LLM Sampling (1000 questions × 10 samples) ---")
    all_samples = sampler.sample_all(
        questions=questions,
        save_path=CFG["samples_path"],
        resume=True,
        n=CFG["n_samples"],
        temperature=CFG["temperature"],
        top_p=CFG["top_p"],
        max_new_tokens=CFG["max_new_tokens"],
    )

    # 5. SMC-NLI scoring
    print("\n--- SMC-NLI Scoring ---")
    nli_scores = nli_scorer.score_all(
        questions=questions,
        all_samples=all_samples,
        labels=labels,
        save_path=CFG["nli_scores_path"],
        resume=True,
    )

    # 6. SMC-Embed scoring
    print("\n--- SMC-Embed Scoring (robustness check) ---")
    embed_scores = embed_scorer.score_all(
        all_samples=all_samples,
        save_path=CFG["embed_scores_path"],
        resume=True,
    )

    # 7. Compute metrics
    results = [
        {"idx": i, "question": questions[i], "label": labels[i],
         "smc_nli": nli_scores[i], "smc_embed": embed_scores[i]}
        for i in range(len(questions))
    ]
    metrics = compute_metrics(results)

    # 8. Save results and figures
    os.makedirs("outputs", exist_ok=True)
    save_results(results, metrics, path=CFG["results_path"])
    fig_dir = os.path.join(os.path.dirname(CODE_DIR), "figures") if "figures" not in CFG["figures_dir"] else CFG["figures_dir"]
    # Use absolute path relative to hypothesis folder
    hyp_dir = os.path.dirname(CODE_DIR)
    fig_dir = os.path.join(hyp_dir, "figures")
    plot_figures(results, metrics, fig_dir=fig_dir)

    # 9. Gate verdict
    print("\n" + "=" * 60)
    print("GATE RESULT")
    print("=" * 60)
    print(f"SMC-NLI AUROC:  {metrics['smc_nli_auroc']:.4f}")
    print(f"SMC-Embed AUROC: {metrics['smc_embed_auroc']:.4f}")
    print(f"SMC-NLI std:    {metrics['smc_nli_std']:.4f}")
    print(f"Random baseline: 0.5000")
    print(f"Gate threshold:  0.60")

    gate_pass = metrics["smc_nli_auroc"] > 0.60
    embed_pass = metrics["smc_embed_auroc"] > 0.60

    if gate_pass:
        print("\n✅ GATE PASSED: SMC-NLI AUROC > 0.60")
        gate_result = "PASSED"
    elif embed_pass:
        print("\n⚠️  SMC-NLI AUROC < 0.60, but SMC-Embed AUROC > 0.60")
        print("    NLI OOD confirmed. Switch primary metric to SMC-Embed.")
        gate_result = "CONDITIONAL_PASS_EMBED"
    else:
        print("\n❌ GATE FAILED: Both SMC-NLI and SMC-Embed AUROC < 0.60")
        gate_result = "FAILED"

    print(f"\nGATE_RESULT: {gate_result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
