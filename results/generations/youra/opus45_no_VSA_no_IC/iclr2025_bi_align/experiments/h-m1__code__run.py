"""H-M1: Semantic Similarity Analysis Pipeline."""

import json
import pandas as pd
from config import CONFIG
from data import load_mode_data
from embeddings import get_model, compute_embeddings, compute_pairwise_similarity, save_embeddings, load_embeddings
from stats import run_statistical_analysis


def main() -> dict:
    """Full pipeline: load -> embed -> similarity -> stats -> save outputs."""
    CONFIG["output_dir"].mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-M1: Semantic Similarity Analysis")
    print("=" * 60)

    df = load_mode_data()
    print(f"\nTotal samples for analysis: {len(df)}")

    embeddings_path = CONFIG["output_dir"] / "embeddings.npz"
    cached = load_embeddings(embeddings_path)

    if cached is not None:
        emb_a, emb_b, battle_ids = cached
        print(f"Loaded cached embeddings from {embeddings_path}")
    else:
        print("\nComputing embeddings...")
        try:
            model = get_model()
        except Exception as e:
            print(f"GPU loading failed ({e}), falling back to CPU...")
            model = get_model(device="cpu")

        emb_a = compute_embeddings(df["resp_a"].tolist(), model)
        emb_b = compute_embeddings(df["resp_b"].tolist(), model)
        save_embeddings(embeddings_path, emb_a, emb_b, df["battle_id"].values)

    print("\nComputing pairwise similarities...")
    similarities = compute_pairwise_similarity(emb_a, emb_b)
    df["similarity"] = similarities

    similarity_path = CONFIG["output_dir"] / "similarity_scores.parquet"
    df[["battle_id", "mode", "similarity"]].to_parquet(similarity_path)
    print(f"Saved similarity scores to {similarity_path}")

    print("\nRunning statistical analysis...")
    sim_mode1 = df.loc[df["mode"] == 1, "similarity"].values
    sim_mode3 = df.loc[df["mode"] == 3, "similarity"].values

    stats_result = run_statistical_analysis(sim_mode1, sim_mode3)

    stats_path = CONFIG["output_dir"] / "statistical_results.json"
    with open(stats_path, "w") as f:
        json.dump(stats_result, f, indent=2)
    print(f"Saved statistical results to {stats_path}")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Mode 1 (Aligned-Confident): n={stats_result['mode_1_n']}, "
          f"mean={stats_result['mode_1_mean_similarity']:.4f}, std={stats_result['mode_1_std']:.4f}")
    print(f"Mode 3 (Misaligned-Confident): n={stats_result['mode_3_n']}, "
          f"mean={stats_result['mode_3_mean_similarity']:.4f}, std={stats_result['mode_3_std']:.4f}")
    print(f"\nCohen's d = {stats_result['cohens_d']:.4f} (95% CI: [{stats_result['ci_95_d'][0]:.4f}, {stats_result['ci_95_d'][1]:.4f}])")
    print(f"Effect size interpretation: {stats_result['effect_interpretation']}")
    print(f"Welch's t-test: t={stats_result['t_statistic']:.4f}, p={stats_result['p_value']:.2e}")
    print(f"\nHypothesis result: {stats_result['result']}")
    print("=" * 60)

    return stats_result


if __name__ == "__main__":
    main()
    print("\nEXPERIMENT COMPLETE")
