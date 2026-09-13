"""Dataset loading and hidden state extraction."""

import torch
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import os


class DatasetLoader:
    def __init__(self, tokenizer, max_length=512, random_seed=42):
        """Initialize dataset loader."""
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def load_triviaqa(self, n_samples=60000):
        """Load TriviaQA dataset."""
        print(f"Loading TriviaQA (n={n_samples})...")
        dataset = load_dataset("trivia_qa", "rc.wikipedia", split="train")

        samples = []
        for i, item in enumerate(tqdm(dataset, desc="Processing TriviaQA")):
            if len(samples) >= n_samples:
                break

            question = item['question']
            answer = item['answer']['value'] if isinstance(item['answer'], dict) else item['answer']

            # Tokenize
            encoded = self.tokenizer(
                question,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='np'
            )

            samples.append({
                'input_ids': encoded['input_ids'][0],
                'attention_mask': encoded['attention_mask'][0],
                'question': question,
                'answer': answer
            })

        return samples

    def load_truthfulqa(self, n_samples=60000):
        """Load TruthfulQA dataset."""
        print(f"Loading TruthfulQA (n={n_samples})...")
        dataset = load_dataset("truthful_qa", "generation", split="validation")

        samples = []
        for i, item in enumerate(tqdm(dataset, desc="Processing TruthfulQA")):
            if len(samples) >= n_samples:
                break

            question = item['question']
            best_answer = item['best_answer']

            # Tokenize
            encoded = self.tokenizer(
                question,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='np'
            )

            samples.append({
                'input_ids': encoded['input_ids'][0],
                'attention_mask': encoded['attention_mask'][0],
                'question': question,
                'answer': best_answer
            })

        return samples

    def load_nli(self, n_samples=80000):
        """Load SNLI dataset."""
        print(f"Loading NLI (n={n_samples})...")
        dataset = load_dataset("snli", split="train")

        samples = []
        for i, item in enumerate(tqdm(dataset, desc="Processing NLI")):
            if len(samples) >= n_samples:
                break

            if item['label'] == -1:  # Skip invalid samples
                continue

            premise = item['premise']
            hypothesis = item['hypothesis']
            question = f"Premise: {premise} Hypothesis: {hypothesis}"

            # Label: 0=entailment, 1=neutral, 2=contradiction
            label = item['label']

            # Tokenize
            encoded = self.tokenizer(
                question,
                max_length=self.max_length,
                padding='max_length',
                truncation=True,
                return_tensors='np'
            )

            samples.append({
                'input_ids': encoded['input_ids'][0],
                'attention_mask': encoded['attention_mask'][0],
                'question': question,
                'nli_label': label
            })

        return samples

    def merge_datasets(self, datasets):
        """Merge multiple datasets."""
        all_samples = []
        for ds in datasets:
            all_samples.extend(ds)
        return all_samples

    def create_splits(self, samples, train_ratio=0.8, val_ratio=0.1):
        """Split dataset into train/val/test."""
        np.random.shuffle(samples)

        n = len(samples)
        train_idx = int(n * train_ratio)
        val_idx = int(n * (train_ratio + val_ratio))

        train_samples = samples[:train_idx]
        val_samples = samples[train_idx:val_idx]
        test_samples = samples[val_idx:]

        return train_samples, val_samples, test_samples


class HiddenStateExtractor:
    def __init__(self, model_name, target_layers, cache_dir, device="cuda"):
        """Initialize frozen LLaMA model."""
        print(f"Loading model {model_name}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto" if device == "cuda" else None
        )
        self.model.eval()
        self.target_layers = target_layers
        self.cache_dir = cache_dir
        self.device = device

    def extract_batch(self, input_ids, attention_mask):
        """Extract hidden states from a batch."""
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                output_hidden_states=True
            )

            # Extract last token hidden states for target layers
            hidden_states = {}
            for layer_idx in self.target_layers:
                # outputs.hidden_states is a tuple of (num_layers + 1) tensors
                # Layer 0 is embedding, Layer 1-32 are transformer layers
                layer_hidden = outputs.hidden_states[layer_idx]  # [B, L, 4096]

                # Get last token position (account for padding)
                last_token_idx = attention_mask.sum(dim=1) - 1  # [B]
                batch_size = layer_hidden.shape[0]

                # Extract last token for each sample in batch
                last_token_hidden = layer_hidden[
                    torch.arange(batch_size),
                    last_token_idx,
                    :
                ]  # [B, 4096]

                hidden_states[layer_idx] = last_token_hidden.cpu().numpy()

            return hidden_states

    def extract_dataset(self, samples, batch_size, split_name):
        """Extract and cache hidden states for dataset."""
        cache_path = os.path.join(self.cache_dir, f"hidden_states_{split_name}.npz")

        if os.path.exists(cache_path):
            print(f"Loading cached hidden states from {cache_path}")
            return self.load_cached_states(cache_path)

        print(f"Extracting hidden states for {split_name} split...")

        all_hidden_states = {layer: [] for layer in self.target_layers}
        all_labels = []

        # Process in batches
        for i in tqdm(range(0, len(samples), batch_size), desc="Extracting"):
            batch_samples = samples[i:i+batch_size]

            # Stack inputs
            input_ids = torch.tensor(
                np.stack([s['input_ids'] for s in batch_samples])
            ).to(self.device)
            attention_mask = torch.tensor(
                np.stack([s['attention_mask'] for s in batch_samples])
            ).to(self.device)

            # Extract hidden states
            batch_hidden = self.extract_batch(input_ids, attention_mask)

            # Accumulate
            for layer_idx in self.target_layers:
                all_hidden_states[layer_idx].append(batch_hidden[layer_idx])

            # Generate binary labels (simplified: use random for PoC)
            batch_labels = np.random.randint(0, 2, len(batch_samples))
            all_labels.append(batch_labels)

        # Concatenate all batches
        for layer_idx in self.target_layers:
            all_hidden_states[layer_idx] = np.concatenate(
                all_hidden_states[layer_idx], axis=0
            )
        all_labels = np.concatenate(all_labels, axis=0)

        # Save to cache
        print(f"Saving hidden states to {cache_path}")
        np.savez_compressed(
            cache_path,
            labels=all_labels,
            **{f'layer_{layer}': all_hidden_states[layer] for layer in self.target_layers}
        )

        return all_hidden_states, all_labels

    def load_cached_states(self, cache_path):
        """Load cached hidden states."""
        data = np.load(cache_path)
        hidden_states = {}
        for layer in self.target_layers:
            hidden_states[layer] = data[f'layer_{layer}']
        labels = data['labels']
        return hidden_states, labels
