"""H-M1 IPCR Routing experiment source modules."""
from .data import (
    load_flan_families,
    split_train_heldout,
    get_task_type,
    FLAN_TASK_FAMILIES,
    generate_family_samples,
)
from .router import IPCRRouter
from .lora_manager import MultiAdapterModel
from .train_lora import LoRATrainer, train_lora_adapter
from .evaluate import EvaluationPipeline, evaluate_all_modes
from .visualize import create_all_figures, plot_gate_comparison

__all__ = [
    "load_flan_families",
    "split_train_heldout",
    "get_task_type",
    "FLAN_TASK_FAMILIES",
    "IPCRRouter",
    "MultiAdapterModel",
    "LoRATrainer",
    "train_lora_adapter",
    "EvaluationPipeline",
    "evaluate_all_modes",
    "create_all_figures",
    "plot_gate_comparison",
]
