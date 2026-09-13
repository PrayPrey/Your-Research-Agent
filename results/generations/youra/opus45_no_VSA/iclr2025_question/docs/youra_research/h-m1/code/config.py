# config.py - h-m1 MECHANISM: Combined model vs H_L baseline
import os

CONFIG = {
    # Inherited from h-e1
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",
    "target_layers": (24, 31),
    "n_folds": 5,
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",
    "batch_size": 4,
    # h-m1 specific: LRT parameters
    "lrt_df": 2,  # degrees of freedom: NTI + CMI added
    "auroc_gain_threshold": 0.03,
    "lrt_pvalue_threshold": 0.05,
    "falsify_gain": 0.02,
    "falsify_pvalue": 0.10,
    "logreg_C": 1.0,
    "logreg_max_iter": 1000,
    # Paths
    "figures_dir": os.path.join(os.path.dirname(__file__), "figures"),
    "outputs_dir": os.path.join(os.path.dirname(__file__), "outputs"),
}
