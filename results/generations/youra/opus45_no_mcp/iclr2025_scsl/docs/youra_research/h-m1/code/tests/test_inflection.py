import sys
sys.path.insert(0, '..')
from inflection import compute_inflection_epoch, correlate_with_wga

def test_compute_inflection_epoch():
    ratio_history = [1.0, 0.9, 0.7, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
    inflection, d1 = compute_inflection_epoch(ratio_history, smoothing_window=3)
    assert 0 <= inflection < len(ratio_history) // 2

def test_correlate_with_wga():
    gradient = [1.0, 0.8, 0.6, 0.4, 0.2]
    wga = [0.9, 0.85, 0.75, 0.65, 0.55]
    result = correlate_with_wga(2, 3, gradient, wga, 10)
    assert 'r' in result
    assert 'p_value' in result
    assert 'gate_pass' in result

def test_short_history():
    result = correlate_with_wga(0, 0, [0.5], [0.5], 10)
    assert result['r'] == 0.0
    assert result['gate_pass'] == False

if __name__ == "__main__":
    test_compute_inflection_epoch()
    test_correlate_with_wga()
    test_short_history()
    print("All tests passed")
