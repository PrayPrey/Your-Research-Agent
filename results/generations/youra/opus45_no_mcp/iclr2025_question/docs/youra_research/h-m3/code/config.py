"""H-M3 Configuration: Linear Fusion of Entropy + Consistency"""

H_M2_RESULTS_PATH = "../../h-m2/code/results/h-m2_results.json"

VAL_FRACTION = 0.1  # 10% val / 90% test
ALPHA_RANGE = [round(i * 0.1, 1) for i in range(11)]  # 0.0..1.0 step 0.1
BETA_RANGE = [round(i * 0.1, 1) for i in range(11)]   # 0.0..1.0 step 0.1

N_BOOTSTRAP = 1000
CI_LEVEL = 0.95

SEED = 42

OUTPUT_PATH = "results/h-m3_results.json"
FIGURES_DIR = "figures/"
