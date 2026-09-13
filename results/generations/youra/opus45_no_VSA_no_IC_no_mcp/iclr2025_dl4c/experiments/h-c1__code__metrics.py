"""Metrics computation for hypothesis validation."""
from statistics import mean
from scipy import stats


def compute_complexity_effect(
    humaneval_results: list[dict], mbpp_results: list[dict]
) -> dict:
    """Compute execution advantage difference between complex (MBPP) and simple (HumanEval) tasks."""
    he_advantages = [r["execution_advantage"] for r in humaneval_results]
    mbpp_advantages = [r["execution_advantage"] for r in mbpp_results]

    he_adv = mean(he_advantages) if he_advantages else 0.0
    mbpp_adv = mean(mbpp_advantages) if mbpp_advantages else 0.0
    complexity_effect = mbpp_adv - he_adv

    t_stat, p_value = None, None
    if len(he_advantages) > 1 and len(mbpp_advantages) > 1:
        t_stat, p_value = stats.ttest_ind(mbpp_advantages, he_advantages)

    return {
        "humaneval_exec_advantage": he_adv,
        "mbpp_exec_advantage": mbpp_adv,
        "complexity_effect": complexity_effect,
        "hypothesis_supported": complexity_effect > 0,
        "humaneval_pass_at_1_exec": mean([r["execution_pass"] for r in humaneval_results]) if humaneval_results else 0,
        "humaneval_pass_at_1_critic": mean([r["critic_pass"] for r in humaneval_results]) if humaneval_results else 0,
        "mbpp_pass_at_1_exec": mean([r["execution_pass"] for r in mbpp_results]) if mbpp_results else 0,
        "mbpp_pass_at_1_critic": mean([r["critic_pass"] for r in mbpp_results]) if mbpp_results else 0,
        "humaneval_n": len(humaneval_results),
        "mbpp_n": len(mbpp_results),
        "t_statistic": float(t_stat) if t_stat is not None else None,
        "p_value": float(p_value) if p_value is not None else None,
    }


if __name__ == "__main__":
    he = [{"execution_advantage": 0.1, "execution_pass": 0.8, "critic_pass": 0.7}]
    mbpp = [{"execution_advantage": 0.2, "execution_pass": 0.7, "critic_pass": 0.5}]
    print(compute_complexity_effect(he, mbpp))
