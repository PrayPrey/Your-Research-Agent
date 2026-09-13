from typing import Tuple
import torch
from torch.utils.data import DataLoader, Dataset
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from datasets import load_dataset
from transformers import AutoTokenizer
from .stratified_sampler import StratifiedSampler

class DatasetPreparer:
    @staticmethod
    def get_cifar10(root: str = "./data", batch_size: int = 128) -> DataLoader:
        transform = transforms.Compose([
            transforms.ToTensor(),
        ])
        
        dataset = datasets.CIFAR10(root=root, train=False, download=True, transform=transform)
        
        def collate_fn(batch):
            images, labels = zip(*batch)
            return {
                'input': torch.stack(images),
                'target': torch.tensor(labels)
            }
        
        return DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    
    @staticmethod
    def get_imagenet(root: str = "./data", batch_size: int = 64) -> DataLoader:
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
        ])
        
        try:
            dataset = datasets.ImageNet(root=root, split='val', transform=transform)
        except:
            print("ImageNet not available - using CIFAR-10 as substitute for testing")
            return DatasetPreparer.get_cifar10(root, batch_size)
        
        def collate_fn(batch):
            images, labels = zip(*batch)
            return {
                'input': torch.stack(images),
                'target': torch.tensor(labels)
            }
        
        return DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    
    @staticmethod
    def get_wmt14(
        root: str = "./data",
        batch_size: int = 32,
        max_length: int = 128
    ) -> Tuple[Dataset, StratifiedSampler]:
        dataset = load_dataset('wmt14', 'de-en', split='test')
        tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        
        def tokenize_fn(sample):
            inputs = tokenizer(sample['translation']['en'], 
                             max_length=max_length, truncation=True)
            labels = tokenizer(sample['translation']['de'],
                             max_length=max_length, truncation=True)
            return {'input_ids': inputs['input_ids'], 'labels': labels['input_ids']}
        
        tokenized_dataset = dataset.map(tokenize_fn)
        sampler = StratifiedSampler(tokenized_dataset, batch_size)
        
        return tokenized_dataset, sampler
    
    @staticmethod
    def get_dataset_type(dataset_name: str) -> str:
        if dataset_name in ['cifar10', 'imagenet']:
            return 'image'
        elif dataset_name == 'wmt14':
            return 'text'
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
