"""
Adaptive Token Pruning with Learnable Retention Policies
Main experiment runner with all baselines and evaluation metrics
"""

import os
import json
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM
from datasets import load_dataset
import argparse
from tqdm import tqdm
import logging
from typing import Dict, List, Tuple, Optional
import gc
import sys

# Add logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TokenRetentionPolicy(nn.Module):
    """Hierarchical token retention policy network"""

    def __init__(self, hidden_dim=768, chunk_size=128, num_layers=4):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.chunk_size = chunk_size

        # Chunk-level network
        self.chunk_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8, dim_feedforward=2048, batch_first=True),
            num_layers=2
        )

        # Query-aware attention
        self.query_proj = nn.Linear(hidden_dim, hidden_dim)
        self.chunk_proj = nn.Linear(hidden_dim, hidden_dim)

        # Chunk-level gating
        self.chunk_gate = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

        # Token-level pruning network
        self.token_scorer = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, hidden_states, query_embed, temperature=1.0, hard=False):
        """
        Args:
            hidden_states: [batch_size, seq_len, hidden_dim]
            query_embed: [batch_size, hidden_dim]
            temperature: temperature for gumbel softmax
            hard: whether to use hard sampling
        Returns:
            retention_mask: [batch_size, seq_len]
            retention_probs: [batch_size, seq_len]
        """
        batch_size, seq_len, hidden_dim = hidden_states.shape

        # Chunk-level processing
        num_chunks = (seq_len + self.chunk_size - 1) // self.chunk_size
        chunk_reps = []

        for i in range(num_chunks):
            start_idx = i * self.chunk_size
            end_idx = min((i + 1) * self.chunk_size, seq_len)
            chunk = hidden_states[:, start_idx:end_idx, :]
            chunk_rep = chunk.mean(dim=1)  # [batch_size, hidden_dim]
            chunk_reps.append(chunk_rep)

        chunk_reps = torch.stack(chunk_reps, dim=1)  # [batch_size, num_chunks, hidden_dim]

        # Query-chunk attention
        query_proj = self.query_proj(query_embed).unsqueeze(1)  # [batch_size, 1, hidden_dim]
        chunk_proj = self.chunk_proj(chunk_reps)  # [batch_size, num_chunks, hidden_dim]

        attention_scores = torch.matmul(query_proj, chunk_proj.transpose(1, 2)) / np.sqrt(hidden_dim)
        attention_weights = F.softmax(attention_scores, dim=-1)  # [batch_size, 1, num_chunks]

        # Chunk-level gating
        chunk_gates = []
        for i in range(num_chunks):
            gate_input = torch.cat([
                chunk_reps[:, i, :],
                query_embed,
                attention_weights[:, 0, i].unsqueeze(-1).expand(-1, hidden_dim)
            ], dim=-1)
            gate = self.chunk_gate(gate_input)  # [batch_size, 1]
            chunk_gates.append(gate)

        chunk_gates = torch.cat(chunk_gates, dim=1)  # [batch_size, num_chunks]

        # Token-level scoring for retained chunks
        token_probs = []
        for i in range(num_chunks):
            start_idx = i * self.chunk_size
            end_idx = min((i + 1) * self.chunk_size, seq_len)
            chunk_tokens = hidden_states[:, start_idx:end_idx, :]
            chunk_len = end_idx - start_idx

            # Expand query and chunk rep for all tokens in chunk
            query_expanded = query_embed.unsqueeze(1).expand(-1, chunk_len, -1)
            chunk_rep_expanded = chunk_reps[:, i, :].unsqueeze(1).expand(-1, chunk_len, -1)

            token_input = torch.cat([chunk_tokens, query_expanded, chunk_rep_expanded], dim=-1)
            token_scores = self.token_scorer(token_input).squeeze(-1)  # [batch_size, chunk_len]

            # Modulate by chunk gate
            token_scores = token_scores + chunk_gates[:, i].unsqueeze(-1).log()

            token_probs.append(torch.sigmoid(token_scores))

        retention_probs = torch.cat(token_probs, dim=1)  # [batch_size, seq_len]

        if hard:
            # Hard thresholding during inference
            retention_mask = (retention_probs > 0.5).float()
        else:
            # Soft mask during training
            retention_mask = retention_probs

        return retention_mask, retention_probs


class LongContextDataset(Dataset):
    """Dataset for long-context tasks"""

    def __init__(self, data, tokenizer, max_length=4096, task_type='qa'):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.task_type = task_type

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        if self.task_type == 'qa':
            context = item.get('context', '')
            question = item.get('input', item.get('question', ''))
            answer = item.get('answers', item.get('answer', ''))

            # Format as question-answering
            text = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"

            if isinstance(answer, list):
                answer = answer[0] if answer else ""

            return {
                'text': text,
                'answer': str(answer),
                'context': context,
                'question': question
            }

        return item


class AdaptiveTokenPruner:
    """Main class for adaptive token pruning experiments"""

    def __init__(self, model_name='facebook/opt-125m', device='cuda', chunk_size=128):
        self.device = device if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")

        self.model_name = model_name
        self.chunk_size = chunk_size

        # Load model and tokenizer
        logger.info(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float32).to(self.device)
        self.model.eval()

        # Initialize policy network
        hidden_dim = self.model.config.hidden_size
        self.policy_network = TokenRetentionPolicy(
            hidden_dim=hidden_dim,
            chunk_size=chunk_size
        ).to(self.device).to(torch.float32)

        logger.info(f"Model loaded with hidden_dim={hidden_dim}")

    def get_embeddings(self, text, max_length=2048):
        """Get embeddings from the model"""
        inputs = self.tokenizer(
            text,
            return_tensors='pt',
            max_length=max_length,
            truncation=True,
            padding='max_length'
        )

        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
            hidden_states = outputs.last_hidden_state  # [batch_size, seq_len, hidden_dim]

        return hidden_states, attention_mask

    def train_policy_network(self, train_loader, num_epochs=5, lr=5e-4):
        """Train the policy network with multi-objective loss"""
        logger.info("Training policy network...")

        optimizer = torch.optim.AdamW(self.policy_network.parameters(), lr=lr)
        self.policy_network.train()

        for epoch in range(num_epochs):
            total_loss = 0
            total_retention_rate = 0
            num_batches = 0

            pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
            for batch in pbar:
                try:
                    texts = batch['text']

                    # Get embeddings
                    hidden_states, attention_mask = self.get_embeddings(texts[0])

                    # Query embedding (use last token representation)
                    query_embed = hidden_states[:, -1, :]

                    # Forward pass
                    retention_mask, retention_probs = self.policy_network(
                        hidden_states, query_embed, temperature=1.0
                    )

                    # Multi-objective loss
                    # 1. Efficiency loss: encourage sparsity
                    valid_tokens = attention_mask.sum()
                    retention_rate = (retention_mask * attention_mask).sum() / (valid_tokens + 1e-8)
                    efficiency_loss = retention_rate ** 2

                    # 2. Coverage loss: ensure each chunk has at least one token
                    seq_len = hidden_states.size(1)
                    num_chunks = (seq_len + self.chunk_size - 1) // self.chunk_size
                    coverage_loss = 0
                    for i in range(num_chunks):
                        start_idx = i * self.chunk_size
                        end_idx = min((i + 1) * self.chunk_size, seq_len)
                        chunk_mask = retention_mask[:, start_idx:end_idx]
                        chunk_attention = attention_mask[:, start_idx:end_idx]

                        # Probability that at least one token is retained
                        no_retention_prob = torch.prod(1 - chunk_mask * chunk_attention + 1e-8, dim=1)
                        coverage_loss -= torch.log(1 - no_retention_prob + 1e-8).mean()

                    coverage_loss = coverage_loss / num_chunks

                    # Total loss
                    loss = 0.7 * efficiency_loss + 0.3 * coverage_loss

                    # Backward
                    optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.policy_network.parameters(), 1.0)
                    optimizer.step()

                    total_loss += loss.item()
                    total_retention_rate += retention_rate.item()
                    num_batches += 1

                    pbar.set_postfix({
                        'loss': f'{loss.item():.4f}',
                        'retention': f'{retention_rate.item():.3f}'
                    })

                except Exception as e:
                    logger.warning(f"Error in training batch: {e}")
                    continue

            avg_loss = total_loss / max(num_batches, 1)
            avg_retention = total_retention_rate / max(num_batches, 1)
            logger.info(f"Epoch {epoch+1}: Loss={avg_loss:.4f}, Retention Rate={avg_retention:.3f}")

        logger.info("Policy network training completed")

    def apply_pruning(self, text, method='adaptive', target_retention=0.5):
        """Apply different pruning methods"""
        hidden_states, attention_mask = self.get_embeddings(text)
        seq_len = hidden_states.size(1)
        valid_len = attention_mask.sum().item()

        if method == 'none':
            # No pruning
            mask = attention_mask.clone()

        elif method == 'static':
            # Static pruning: keep first and last tokens
            mask = torch.zeros_like(attention_mask)
            keep_count = int(valid_len * target_retention)
            keep_first = keep_count // 2
            keep_last = keep_count - keep_first
            mask[:, :keep_first] = 1
            mask[:, -keep_last:] = 1
            mask = mask * attention_mask

        elif method == 'attention':
            # Attention-based pruning: keep tokens with high attention
            try:
                with torch.no_grad():
                    outputs = self.model(
                        input_ids=self.tokenizer(text, return_tensors='pt', max_length=2048, truncation=True)['input_ids'].to(self.device),
                        output_attentions=True
                    )
                    if outputs.attentions and len(outputs.attentions) > 0:
                        # Average attention across all layers and heads
                        attentions = torch.stack([a.mean(dim=1) for a in outputs.attentions], dim=0).mean(dim=0)
                        # Sum attention received by each token
                        token_importance = attentions.sum(dim=1).squeeze(0)  # [seq_len]

                        # Keep top-k tokens
                        keep_count = max(1, int(valid_len * target_retention))
                        keep_count = min(keep_count, token_importance.size(0))
                        _, top_indices = torch.topk(token_importance, keep_count)
                        mask = torch.zeros_like(attention_mask)
                        mask[:, top_indices] = 1
                        mask = mask * attention_mask
                    else:
                        # Fallback to static pruning if attention not available
                        mask = torch.zeros_like(attention_mask)
                        keep_count = int(valid_len * target_retention)
                        keep_first = keep_count // 2
                        keep_last = keep_count - keep_first
                        mask[:, :keep_first] = 1
                        mask[:, -keep_last:] = 1
                        mask = mask * attention_mask
            except Exception as e:
                logger.warning(f"Attention pruning failed: {e}, using static fallback")
                # Fallback to static pruning
                mask = torch.zeros_like(attention_mask)
                keep_count = int(valid_len * target_retention)
                keep_first = keep_count // 2
                keep_last = keep_count - keep_first
                mask[:, :keep_first] = 1
                mask[:, -keep_last:] = 1
                mask = mask * attention_mask

        elif method == 'adaptive':
            # Adaptive pruning with learned policy
            query_embed = hidden_states[:, -1, :]
            with torch.no_grad():
                self.policy_network.eval()
                retention_mask, retention_probs = self.policy_network(
                    hidden_states, query_embed, hard=True
                )
            mask = retention_mask * attention_mask

        else:
            raise ValueError(f"Unknown pruning method: {method}")

        return mask, hidden_states

    def evaluate(self, test_data, method='adaptive', target_retention=0.5):
        """Evaluate pruning method"""
        logger.info(f"Evaluating method: {method}")

        results = {
            'method': method,
            'retention_rates': [],
            'latencies': [],
            'memory_usage': [],
        }

        self.model.eval()
        if hasattr(self, 'policy_network'):
            self.policy_network.eval()

        for idx, item in enumerate(tqdm(test_data[:50], desc=f"Evaluating {method}")):  # Limit to 50 samples
            try:
                text = item['text']

                # Measure latency
                torch.cuda.synchronize() if torch.cuda.is_available() else None
                start_time = time.time()

                # Apply pruning
                mask, hidden_states = self.apply_pruning(text, method=method, target_retention=target_retention)

                torch.cuda.synchronize() if torch.cuda.is_available() else None
                latency = time.time() - start_time

                # Calculate metrics
                valid_tokens = (hidden_states.abs().sum(dim=-1) > 0).sum().item()
                retained_tokens = mask.sum().item()
                retention_rate = retained_tokens / max(valid_tokens, 1)

                # Memory usage (approximate)
                memory_mb = hidden_states.element_size() * hidden_states.nelement() / (1024 ** 2)
                pruned_memory_mb = memory_mb * retention_rate

                results['retention_rates'].append(retention_rate)
                results['latencies'].append(latency)
                results['memory_usage'].append(pruned_memory_mb)

            except Exception as e:
                logger.warning(f"Error evaluating item {idx}: {e}")
                continue

        # Compute averages
        results['avg_retention_rate'] = np.mean(results['retention_rates'])
        results['avg_latency'] = np.mean(results['latencies'])
        results['avg_memory_mb'] = np.mean(results['memory_usage'])
        results['std_retention_rate'] = np.std(results['retention_rates'])
        results['std_latency'] = np.std(results['latencies'])

        # Cache reduction
        if method == 'none':
            results['cache_reduction'] = 0.0
        else:
            results['cache_reduction'] = 1.0 - results['avg_retention_rate']

        logger.info(f"{method} - Retention: {results['avg_retention_rate']:.3f}, "
                   f"Cache Reduction: {results['cache_reduction']:.3f}, "
                   f"Latency: {results['avg_latency']:.4f}s")

        return results


def load_long_context_data(max_samples=200):
    """Load long-context dataset for experiments"""
    logger.info("Loading dataset...")

    try:
        # Try to load a long-context QA dataset
        # Using narrativeqa as it has longer contexts
        dataset = load_dataset("narrativeqa", split='test', trust_remote_code=True)

        processed_data = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break

            # NarrativeQA format
            context = item.get('document', {}).get('text', '')[:10000]  # Limit context length
            question = item.get('question', {}).get('text', '')
            answers = item.get('answers', [{}])[0].get('text', '') if item.get('answers') else ''

            if context and question:
                processed_data.append({
                    'text': f"Context: {context}\n\nQuestion: {question}\n\nAnswer:",
                    'answer': answers,
                    'context': context,
                    'question': question
                })

        logger.info(f"Loaded {len(processed_data)} samples from NarrativeQA")

    except Exception as e:
        logger.warning(f"Could not load NarrativeQA: {e}")
        logger.info("Using SQuAD as fallback...")

        # Fallback to SQuAD
        dataset = load_dataset("squad", split='validation')

        processed_data = []
        for i, item in enumerate(dataset):
            if i >= max_samples:
                break

            context = item['context']
            question = item['question']
            answers = item['answers']['text'][0] if item['answers']['text'] else ''

            processed_data.append({
                'text': f"Context: {context}\n\nQuestion: {question}\n\nAnswer:",
                'answer': answers,
                'context': context,
                'question': question
            })

        logger.info(f"Loaded {len(processed_data)} samples from SQuAD")

    return processed_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='facebook/opt-125m',
                       help='Model name or path')
    parser.add_argument('--chunk_size', type=int, default=128,
                       help='Chunk size for hierarchical processing')
    parser.add_argument('--train_epochs', type=int, default=3,
                       help='Number of training epochs')
    parser.add_argument('--max_samples', type=int, default=200,
                       help='Maximum number of samples to use')
    parser.add_argument('--target_retention', type=float, default=0.5,
                       help='Target retention rate for baselines')
    parser.add_argument('--output_dir', type=str, default='.',
                       help='Output directory')
    args = parser.parse_args()

    logger.info("="*80)
    logger.info("Adaptive Token Pruning Experiments")
    logger.info("="*80)
    logger.info(f"Model: {args.model}")
    logger.info(f"Chunk size: {args.chunk_size}")
    logger.info(f"Training epochs: {args.train_epochs}")
    logger.info(f"Max samples: {args.max_samples}")
    logger.info(f"Target retention: {args.target_retention}")

    # Load data
    data = load_long_context_data(max_samples=args.max_samples)
    train_size = int(0.7 * len(data))
    train_data = data[:train_size]
    test_data = data[train_size:]

    logger.info(f"Train samples: {len(train_data)}")
    logger.info(f"Test samples: {len(test_data)}")

    # Initialize pruner
    pruner = AdaptiveTokenPruner(
        model_name=args.model,
        chunk_size=args.chunk_size
    )

    # Create dataset and dataloader for training
    train_dataset = LongContextDataset(train_data, pruner.tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True)

    # Train policy network
    pruner.train_policy_network(train_loader, num_epochs=args.train_epochs)

    # Save trained policy network
    policy_path = os.path.join(args.output_dir, 'policy_network.pt')
    torch.save(pruner.policy_network.state_dict(), policy_path)
    logger.info(f"Saved policy network to {policy_path}")

    # Evaluate all methods
    methods = ['none', 'static', 'attention', 'adaptive']
    all_results = {}

    for method in methods:
        results = pruner.evaluate(test_data, method=method, target_retention=args.target_retention)
        all_results[method] = results

        # Clean up memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

    # Save results
    results_path = os.path.join(args.output_dir, 'experiment_results.json')
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=float)

    logger.info(f"Results saved to {results_path}")

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("RESULTS SUMMARY")
    logger.info("="*80)
    logger.info(f"{'Method':<15} {'Retention':<12} {'Cache Red.':<12} {'Latency (s)':<12} {'Memory (MB)':<12}")
    logger.info("-"*80)
    for method, results in all_results.items():
        logger.info(f"{method:<15} "
                   f"{results['avg_retention_rate']:<12.3f} "
                   f"{results['cache_reduction']:<12.3f} "
                   f"{results['avg_latency']:<12.4f} "
                   f"{results['avg_memory_mb']:<12.2f}")
    logger.info("="*80)

    logger.info("\nExperiment completed successfully!")


if __name__ == '__main__':
    main()
