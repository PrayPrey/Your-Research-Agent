from scipy.stats import binomtest, chi2

def mcnemar_test(static_newly_solved: set, exec_newly_solved: set, all_problems: set) -> dict:
    b = len(static_newly_solved - exec_newly_solved)
    c = len(exec_newly_solved - static_newly_solved)

    if b + c == 0:
        return {"p_value": 1.0, "static_only": b, "exec_only": c, "method": "no_discordant"}

    if b + c < 25:
        result = binomtest(min(b, c), b + c, p=0.5)
        p_value = result.pvalue
        method = "exact_binomial"
    else:
        chi2_stat = (abs(b - c) - 1) ** 2 / (b + c)
        p_value = 1 - chi2.cdf(chi2_stat, df=1)
        method = "chi2_approx"

    return {"p_value": p_value, "static_only": b, "exec_only": c, "method": method}
