import os
import math

# from dotenv import load_dotenv
import torch
import numpy as np
from torch.utils.data import DataLoader, ConcatDataset
import datasets

from torch.nn.utils.rnn import pad_sequence
# import transformers  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402
from typing import Dict

try:
    from .babilong.babilong_utils import TaskDataset, SentenceSampler, NoiseInjectionDataset
except ImportError:
    from babilong.babilong_utils import TaskDataset, SentenceSampler, NoiseInjectionDataset



TASK_NAME_DICT = {
    'qa1': 'qa1_single-supporting-fact',
    'qa2': 'qa2_two-supporting-facts',
    'qa3': 'qa3_three-supporting-facts',
}

def load_data(name: str, dataset_config: Dict, pretrained_model_config: Dict,
              preprocess_config: dict, **loader_kwargs: any) -> Dict[str, DataLoader]:
    # Prepare datasets
    try:
        noise_dataset = datasets.load_dataset('fla-hub/pg19')
        noise_dataset_train = noise_dataset['train']
        noise_dataset_test = noise_dataset['test']
    except ConnectionError:
        raise ConnectionError("Failed to load noise dataset")
    
    # task dataset 
    if dataset_config['name'] == 'qa23':
        task_name = 'qa3_three-supporting-facts'
    else:
        task_name = TASK_NAME_DICT[dataset_config['name']]
    vary_n_segments = dataset_config.get('vary_n_segments', False)
    segment_size = dataset_config.get('segment_size', dataset_config['chunk_size'])
    max_n_segments = dataset_config.get('max_n_segments', 1)
    mixed_length_ratio = dataset_config.get('mixed_length_ratio', 0.0)
    data_n_workers = loader_kwargs.get("num_workers", 4)
    per_worker_batch_size = loader_kwargs.get("batch_size", 1)
    sample_size = segment_size * max_n_segments
    max_n_facts = sample_size // 8
    train_path = os.path.join("/home/liuzeyu/babilong/data/tasks_1-20_v1-2/en-10k", f"{task_name}_train.txt")
    test_path = os.path.join("/home/liuzeyu/babilong/data/tasks_1-20_v1-2/en-10k", f"{task_name}_test.txt")

    task_dataset_train = TaskDataset(train_path, max_n_facts=max_n_facts)
    task_dataset_test = TaskDataset(test_path, max_n_facts=max_n_facts)

    if dataset_config['name'] == 'qa23':
        task_dataset_train2 = TaskDataset(os.path.join("/home/liuzeyu/babilong/data/tasks_1-20_v1-2/en-10k", f"qa2_two-supporting-facts_train.txt"), max_n_facts=max_n_facts)
        task_dataset_test2 = TaskDataset(os.path.join("/home/liuzeyu/babilong/data/tasks_1-20_v1-2/en-10k", f"qa2_two-supporting-facts_test.txt"), max_n_facts=max_n_facts)
        task_dataset_train = ConcatDataset([task_dataset_train, task_dataset_train2])
        task_dataset_test = ConcatDataset([task_dataset_test, task_dataset_test2])

    # background text
    qa_margin = 20          # leave space for questions and answers
    if vary_n_segments:  # choose sample sizes according to each number of segments up to args.max_n_segments
        train_sample_size = [int(segment_size * i) for i in range(1, max_n_segments)] + [sample_size]
        train_sample_size = [s - qa_margin for s in train_sample_size]
    else:
        sample_size = sample_size - qa_margin
        train_sample_size = sample_size - qa_margin
    test_sample_size = sample_size - qa_margin
    max_sentence_len = None

    tokenizer = AutoTokenizer.from_pretrained(pretrained_model_config['pretrained_model_name_or_path'], use_fast=True)
    noise_sampler_train = SentenceSampler(noise_dataset_train, tokenizer=tokenizer, max_sentence_len=max_sentence_len, shuffle=True, random_seed=None)
    noise_sampler_test = SentenceSampler(noise_dataset_test, tokenizer=tokenizer, max_sentence_len=max_sentence_len, shuffle=True, random_seed=42)

    train_dataset = NoiseInjectionDataset(task_dataset=task_dataset_train,
                                            noise_sampler=noise_sampler_train,
                                            tokenizer=tokenizer,
                                            sample_size=train_sample_size,
                                            mixed_length_ratio=mixed_length_ratio,
                                            task_start_pct=None,
                                            task_end_pct=None
                                            )

    test_dataset = NoiseInjectionDataset(task_dataset=task_dataset_test,
                                            noise_sampler=noise_sampler_test,
                                            tokenizer=tokenizer,
                                            sample_size=test_sample_size,
                                            mixed_length_ratio=mixed_length_ratio,
                                            task_start_pct=None,
                                            task_end_pct=None
                                            )
    
    id_pad_value = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    gen_token = tokenizer.encode('GEN')[0]
    eos_token = tokenizer.eos_token_id

    def collate_fn(batch):
        targets = [torch.tensor(b['target_tokens']) for b in batch]
        input_ids = [torch.tensor(b['input_tokens'] + b['question_tokens'] + [gen_token] + b['target_tokens'] + [eos_token]) for b in batch]
        gen_inputs = [torch.tensor(b['input_tokens'] + b['question_tokens'] + [gen_token]) for b in batch]

        attention_mask = [torch.ones_like(b, dtype=int) for b in input_ids]
        labels_mask = [torch.zeros_like(b, dtype=bool) for b in input_ids]
        for m, t in zip(labels_mask, targets):
            m[-len(t) - 2:] = True

        input_ids = pad_sequence(input_ids, padding_value=id_pad_value, batch_first=True)
        gen_inputs = pad_sequence(gen_inputs, padding_value=id_pad_value, batch_first=True)
        attention_mask = pad_sequence(attention_mask, padding_value=0, batch_first=True)
        labels_mask = pad_sequence(labels_mask, padding_value=0, batch_first=True)

        collated = {}
        collated['input_ids'] = collated['labels'] = input_ids
        collated['input_ids_generate'] = gen_inputs
        collated['labels_mask'] = labels_mask
        collated['attention_mask'] = attention_mask.bool()
        collated['attention_mask_generate'] = (gen_inputs != id_pad_value).bool()
        collated['target_text'] = [b['answer'] for b in batch]
        return collated

    kwargs = {'pin_memory': True, 'num_workers': data_n_workers, 'collate_fn': collate_fn}
    
    train_loader = DataLoader(train_dataset, batch_size=per_worker_batch_size, shuffle=True, **kwargs)
    test_loader = DataLoader(test_dataset, batch_size=per_worker_batch_size, shuffle=False, **kwargs)

    return {
        "train":  train_loader,
        "validation":    test_loader,
        "test":   test_loader,  # same split
    }