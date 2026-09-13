import torch.optim as optim
from typing import Dict

class OptimizerFactory:
    @staticmethod
    def get_optimizer(name: str, model_params, lr: float = None) -> optim.Optimizer:
        config = OptimizerFactory.get_default_config(name)
        
        if lr is not None:
            config['lr'] = lr
        
        if name == "adam":
            return optim.Adam(model_params, lr=config['lr'], betas=config['betas'])
        elif name == "adamw":
            return optim.AdamW(model_params, lr=config['lr'], betas=config['betas'], 
                             weight_decay=config['weight_decay'])
        elif name == "sgd":
            return optim.SGD(model_params, lr=config['lr'], momentum=config['momentum'])
        else:
            raise ValueError(f"Unknown optimizer: {name}")
    
    @staticmethod
    def get_default_config(name: str) -> Dict:
        if name == "adam":
            return {'lr': 0.0001, 'betas': (0.9, 0.999)}
        elif name == "adamw":
            return {'lr': 0.0001, 'betas': (0.9, 0.999), 'weight_decay': 0.01}
        elif name == "sgd":
            return {'lr': 0.1, 'momentum': 0.9}
        else:
            raise ValueError(f"Unknown optimizer: {name}")
    
    @staticmethod
    def list_supported_optimizers() -> list[str]:
        return ["adam", "adamw", "sgd"]
