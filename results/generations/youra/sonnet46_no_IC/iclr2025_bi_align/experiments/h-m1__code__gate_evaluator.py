def evaluate_gate(ols_result: dict, vif: dict, perm_result: dict = None) -> dict:
    if not vif['any_high_vif']:
        abs_win = abs(ols_result['beta_win'])
        abs_len = abs(ols_result['beta_len'])
        passes = (abs_win > abs_len) and (ols_result['p_win'] < 0.05)
        return {
            'passes_gate': passes,
            'path': 'OLS_beta',
            'beta_win': ols_result['beta_win'],
            'beta_len': ols_result['beta_len'],
            'p_win': ols_result['p_win'],
            'dominant': 'win_rate' if abs_win > abs_len else 'avg_length'
        }
    else:
        passes = perm_result['imp_win'] > perm_result['imp_len']
        return {
            'passes_gate': passes,
            'path': 'permutation_importance',
            'beta_win': ols_result['beta_win'],
            'beta_len': ols_result['beta_len'],
            'p_win': ols_result['p_win'],
            'dominant': 'win_rate' if passes else 'avg_length'
        }
