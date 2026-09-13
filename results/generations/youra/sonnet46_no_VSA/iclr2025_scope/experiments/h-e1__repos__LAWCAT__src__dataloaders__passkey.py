from transformers import AutoTokenizer
from torch.utils.data import Dataset, DataLoader
import torch
import json
from typing import Dict, List
PROMPT_LOLCAT = "There is an important piece of info hidden inside a lot of irrelevant text. Find it and memorize it. I will quiz you about the important information there."
class PasskeyDataset(Dataset):
    def __init__(self, file_path, tokenizer_name="meta-llama/Meta-Llama-3-8B", max_length=8192):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load dataset
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.samples = data['samples']

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Format as instruction-response pair
        full_prompt = (
            f"{PROMPT_LOLCAT}\n{sample['prompt']}\nWhat is the pass key? The pass key is "
        )

        # Tokenize the full sequence
        encoding = self.tokenizer(
            full_prompt + sample['passkey'] + self.tokenizer.eos_token,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

        answer_encoding = self.tokenizer.encode(
            sample['passkey'],
            # f"What is the pass key? The pass key is {sample['passkey']}",
            add_special_tokens=False
        )
        # Create labels (-100 for all text before "The pass key is ")
        labels = encoding.input_ids.clone()
        
        # Mask labels: only calculate loss on the passkey response

        labels[:,:-1*len(answer_encoding)-1] = -100
        # labels[:,-1] = encoding.input_ids[:,-1] # last token is eos token
        labels[:,-1] = -100
        
        return {
            'input_ids': encoding.input_ids[0],
            'attention_mask': encoding.attention_mask[0],
            'labels': labels[0]
        }

def collate_fn(batch):
    pad_token_id = 128001  # Llama3 pad token
    
    max_len = max(len(item['input_ids']) for item in batch)
    
    padded_batch = {
        'input_ids': [],
        'attention_mask': [],
        'labels': []
    }
    
    for item in batch:
        pad_len = max_len - len(item['input_ids'])
        padded_batch['input_ids'].append(
            torch.cat([item['input_ids'], torch.full((pad_len,), pad_token_id)])
        )
        padded_batch['attention_mask'].append(
            torch.cat([item['attention_mask'], torch.zeros(pad_len)])
        )
        padded_batch['labels'].append(
            torch.cat([item['labels'], torch.full((pad_len,), -100)])
        )
    
    return {
        'input_ids': torch.stack(padded_batch['input_ids']),
        'attention_mask': torch.stack(padded_batch['attention_mask']),
        'labels': torch.stack(padded_batch['labels'])
    }

def load_data(name: str, dataset_config: Dict, pretrained_model_config: Dict,
              preprocess_config: dict, **loader_kwargs: any) -> Dict[str, DataLoader]:
    chunk_size = int(dataset_config['chunk_size'])
    file_path = "/data3/zeyu/LAWCAT/datasets/lolcat_passkey_dataset_870"
        
    train_dataset = PasskeyDataset(
        file_path=f"{file_path}_train.json",
        tokenizer_name=pretrained_model_config['pretrained_model_name_or_path'],
        max_length=dataset_config['chunk_size']
    )
    val_dataset = PasskeyDataset(
        file_path=f"{file_path}_validation.json",
        tokenizer_name=pretrained_model_config['pretrained_model_name_or_path'],
        max_length=dataset_config['chunk_size']
    )
    test_dataset = PasskeyDataset(
        file_path=f"{file_path}_test.json",
        tokenizer_name=pretrained_model_config['pretrained_model_name_or_path'],
        max_length=dataset_config['chunk_size']
    )
    dataloder = {}
    dataloder['train'] = DataLoader(
        train_dataset,
        batch_size=loader_kwargs.get('batch_size', 1),
        collate_fn=collate_fn,
        num_workers=loader_kwargs.get('num_workers', 4),
        shuffle=True
    )
    dataloder['validation'] = DataLoader(
        val_dataset,
        batch_size=loader_kwargs.get('batch_size', 1),
        collate_fn=collate_fn,
        num_workers=loader_kwargs.get('num_workers', 4),
        shuffle=False
    )
    dataloder['test'] = DataLoader(
        test_dataset,
        batch_size=loader_kwargs.get('batch_size', 1),
        collate_fn=collate_fn,
        num_workers=loader_kwargs.get('num_workers', 4),
        shuffle=False
    )
    return dataloder