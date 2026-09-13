def check_commitment(spurious_acc_history: list, core_acc_history: list,
                     noise_margin: float = 0.02, core_threshold: float = 0.85) -> dict:
    if len(spurious_acc_history) < 2:
        return {'committed': None, 'gate_pass': None, 'error': 'insufficient_data'}

    spurious_initial = spurious_acc_history[0]
    spurious_final = spurious_acc_history[-1]
    core_final = core_acc_history[-1]

    committed = (spurious_final >= spurious_initial - noise_margin)
    core_suppressed = (core_final < core_threshold)
    spurious_trend = compute_trend(spurious_acc_history, noise_margin)
    gate_pass = committed

    return {
        'committed': committed,
        'core_suppressed': core_suppressed,
        'spurious_trend': spurious_trend,
        'core_final': core_final,
        'spurious_final': spurious_final,
        'spurious_initial': spurious_initial,
        'gate_pass': gate_pass
    }

def compute_trend(history: list, noise_margin: float = 0.02) -> str:
    if len(history) < 2:
        return 'unknown'
    delta = history[-1] - history[0]
    if delta > noise_margin:
        return 'increasing'
    elif delta < -noise_margin:
        return 'decreasing'
    return 'stable'
