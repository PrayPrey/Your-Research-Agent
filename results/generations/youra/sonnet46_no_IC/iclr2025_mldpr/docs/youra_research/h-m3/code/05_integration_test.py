"""H-M3: Integration test — run scripts 01→04 and verify outputs."""
import os
import sys
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')


def run_script(script):
    path = os.path.join(CODE_DIR, script)
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAIL: {script}")
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        sys.exit(1)
    print(f"OK: {script}")


def verify():
    # Verify preprocessed parquet
    parquet = os.path.join(RESULTS_DIR, 'preprocessed_m3.parquet')
    assert os.path.exists(parquet), f"Missing: {parquet}"
    import pandas as pd
    df = pd.read_parquet(parquet)
    assert len(df) >= 5000, f"N={len(df)} < 5000"
    assert 'tag_count_cat' in df.columns, "Missing tag_count_cat"
    cats = df['tag_count_cat'].value_counts()
    assert len(cats) == 4, f"Expected 4 bins, got {len(cats)}"
    assert (cats > 0).all(), "Some bins empty"
    print(f"  Parquet OK: N={len(df)}, bins={dict(cats)}")

    # Verify model_results.json
    model_path = os.path.join(RESULTS_DIR, 'model_results.json')
    assert os.path.exists(model_path), f"Missing: {model_path}"
    with open(model_path) as f:
        m = json.load(f)
    assert 'cat_irr' in m, "Missing cat_irr"
    assert 'ct_lr_test' in m, "Missing ct_lr_test"
    print(f"  model_results OK: is_monotonic={m['is_monotonic']}, n_passing={m['n_adjacent_contrasts_passing']}")

    # Verify primary_results.json
    pr_path = os.path.join(RESULTS_DIR, 'primary_results.json')
    assert os.path.exists(pr_path), f"Missing: {pr_path}"
    with open(pr_path) as f:
        pr = json.load(f)
    assert pr['result'] in ('PASS', 'INFORMATIVE_NEGATIVE'), f"Unexpected result: {pr['result']}"
    assert 'is_monotonic' in pr, "Missing is_monotonic"
    print(f"  primary_results OK: result={pr['result']}")

    # Verify 5 figures
    fig_names = ['fig1_irr_bar_chart.png', 'fig2_dose_response.png',
                 'fig3_category_distribution.png', 'fig4_contrast_forest.png', 'fig5_attenuation.png']
    for fig in fig_names:
        fp = os.path.join(FIGURES_DIR, fig)
        assert os.path.exists(fp), f"Missing figure: {fp}"
        assert os.path.getsize(fp) > 1000, f"Figure too small: {fp}"
    print(f"  All 5 figures OK")


if __name__ == '__main__':
    run_script('01_preprocess.py')
    run_script('02_fit_models.py')
    run_script('04_evaluate_gate.py')  # must run before 03 (needs primary_results.json)
    run_script('03_generate_figures.py')
    verify()
    print("INTEGRATION TEST PASSED")
