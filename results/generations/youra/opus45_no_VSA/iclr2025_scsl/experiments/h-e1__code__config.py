from dataclasses import dataclass


@dataclass
class Config:
    data_root: str = "./data/waterbird_complete95_forest2water2"
    img_size: int = 224
    batch_size: int = 32
    imagenet_mean: tuple = (0.485, 0.456, 0.406)
    imagenet_std: tuple = (0.229, 0.224, 0.225)
    minority_groups: tuple = (1, 2)
    majority_groups: tuple = (0, 3)
    num_classes: int = 2
    pretrained: bool = False
    num_power_iter: int = 20
    seeds: tuple = (0, 1, 2, 3, 4)
    results_path: str = "results/sr_values.json"
    figure_path: str = "figures/sr_comparison.png"


CONFIG = Config()
