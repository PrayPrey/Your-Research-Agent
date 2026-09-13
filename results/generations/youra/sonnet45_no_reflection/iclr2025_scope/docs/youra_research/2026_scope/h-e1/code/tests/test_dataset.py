"""
Test suite for data/dataset.py - Specification compliance tests
Tests MultiTaskDataset, data loaders, and tokenization
"""
import pytest
import torch
from transformers import AutoTokenizer


def test_multitask_dataset_class_exists():
    """Test MultiTaskDataset class exists with required methods"""
    from data.dataset import MultiTaskDataset

    assert hasattr(MultiTaskDataset, '__init__')
    assert hasattr(MultiTaskDataset, '__len__')
    assert hasattr(MultiTaskDataset, '__getitem__')


def test_multitask_dataset_initialization():
    """Test MultiTaskDataset can be initialized"""
    from data.dataset import MultiTaskDataset
    from config import DataConfig

    config = DataConfig(
        glue_tasks=['cola', 'sst2'],
        superglue_tasks=['boolq'],
        max_length=128,
        batch_size=8
    )
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    dataset = MultiTaskDataset(config, split='train', tokenizer=tokenizer, max_samples=10)
    assert len(dataset) > 0
    assert hasattr(dataset, 'config')
    assert hasattr(dataset, 'tokenizer')


def test_multitask_dataset_getitem():
    """Test MultiTaskDataset returns correct item format"""
    from data.dataset import MultiTaskDataset
    from config import DataConfig

    config = DataConfig(
        glue_tasks=['cola'],
        superglue_tasks=[],
        max_length=128,
        batch_size=8
    )
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    dataset = MultiTaskDataset(config, split='train', tokenizer=tokenizer, max_samples=5)
    item = dataset[0]

    # Check required keys
    assert 'input_ids' in item
    assert 'attention_mask' in item
    assert 'labels' in item
    assert 'task_id' in item

    # Check tensor types
    assert isinstance(item['input_ids'], torch.Tensor)
    assert isinstance(item['attention_mask'], torch.Tensor)
    assert isinstance(item['labels'], torch.Tensor) or isinstance(item['labels'], int)
    assert isinstance(item['task_id'], torch.Tensor) or isinstance(item['task_id'], int)


def test_load_glue_task():
    """Test load_glue_task function exists"""
    from data.dataset import load_glue_task

    # Just test that function exists and is callable
    assert callable(load_glue_task)


def test_load_superglue_task():
    """Test load_superglue_task function exists"""
    from data.dataset import load_superglue_task

    # Just test that function exists and is callable
    assert callable(load_superglue_task)


def test_create_dataloaders():
    """Test create_dataloaders returns train and val loaders"""
    from data.dataset import create_dataloaders
    from config import DataConfig
    from transformers import AutoTokenizer

    config = DataConfig(
        glue_tasks=['cola'],
        superglue_tasks=[],
        max_length=128,
        batch_size=4,
        num_workers=0
    )
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    train_loader, val_loader = create_dataloaders(config, tokenizer, max_samples=10)

    assert train_loader is not None
    assert val_loader is not None
    assert hasattr(train_loader, '__iter__')
    assert hasattr(val_loader, '__iter__')


def test_collate_fn():
    """Test collate_fn handles dynamic padding"""
    from data.dataset import collate_fn

    # Create sample batch
    batch = [
        {
            'input_ids': torch.tensor([1, 2, 3]),
            'attention_mask': torch.tensor([1, 1, 1]),
            'labels': torch.tensor(0),
            'task_id': torch.tensor(0)
        },
        {
            'input_ids': torch.tensor([1, 2, 3, 4, 5]),
            'attention_mask': torch.tensor([1, 1, 1, 1, 1]),
            'labels': torch.tensor(1),
            'task_id': torch.tensor(0)
        }
    ]

    collated = collate_fn(batch)

    assert 'input_ids' in collated
    assert 'attention_mask' in collated
    assert 'labels' in collated
    assert 'task_ids' in collated or 'task_id' in collated

    # Check shapes - should be padded to max length in batch
    assert collated['input_ids'].shape[0] == 2  # batch size
    assert collated['input_ids'].shape[1] >= 5  # padded to longest sequence
