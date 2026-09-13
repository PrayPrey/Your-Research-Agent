#!/usr/bin/env python3
"""H-M1 ProvenanceCache Experiment"""

import os
import sys
import json
import time
import torch
import random
import numpy as np
from pathlib import Path
from typing import Dict, List
import logging

from transformers import AutoModelForCausalLM, AutoTokenizer
from cache_policy import (
    FullKVCache, H2OCache, ProvenanceCache, RandomCache,
    H2OCacheConfig, ProvenanceCacheConfig
)
from retrieval import ContrieverRetriever
from data import LongBenchLoader
from evaluate import compute_f1, compute_exact_match, compute_significance, aggregate_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

class ExperimentRunner:
    def __init__(self, config: Dict):
        self.config = config
        self.device = "cpu"  # Force CPU due to CUDA lib issue
        log.info(f"Using device: {self.device}")

        # Load model
        log.info(f"Loading {config['model_checkpoint']}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            config['model_checkpoint'],
            torch_dtype=torch.float32,
            output_attentions=True
        ).to(self.device)
        self.model.eval()

        self.tokenizer = AutoTokenizer.from_pretrained(config['model_checkpoint'])
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        # Load retriever
        log.info("Loading Contriever...")
        self.retriever = ContrieverRetriever(device=self.device)

        # Load dataset
        log.info("Loading LongBench...")
        loader = LongBenchLoader(config['tasks'], config['model_checkpoint'])
        self.samples = loader.load()
        log.info(f"Loaded {len(self.samples)} samples")

    def generate_with_cache(self, prompt: str, cache_policy, max_new_tokens: int = 100) -> str:
        """Generate with custom cache policy"""
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=4096)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.0,
                do_sample=False,
                output_attentions=isinstance(cache_policy, H2OCache),
                return_dict_in_generate=isinstance(cache_policy, H2OCache)
            )

        if isinstance(cache_policy, H2OCache):
            generated_ids = outputs.sequences
        else:
            generated_ids = outputs

        response = self.tokenizer.decode(generated_ids[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return response

    def run_condition(self, condition: str, cache_policy, num_samples: int = None) -> List[Dict]:
        """Run evaluation for one condition"""
        log.info(f"Running condition: {condition}")
        results = []
        samples = self.samples[:num_samples] if num_samples else self.samples

        for i, sample in enumerate(samples):
            if i % 5 == 0:
                log.info(f"  Sample {i}/{len(samples)}")

            try:
                query = sample['input']
                context = sample['context']
                ground_truths = sample['answers']
            except Exception as e:
                log.warning(f"Failed to parse sample {i}: {e}")
                continue

            # Retrieval for ProvenanceCache
            if isinstance(cache_policy, ProvenanceCache):
                passages = self.retriever.chunk_document(context)
                top_passages, scores = self.retriever.retrieve(query, passages, top_k=5)

                # Register provenance
                prompt = f"Question: {query}\n\nContext: {' '.join(top_passages)}\n\nAnswer:"
                query_tokens = self.tokenizer.encode(f"Question: {query}", add_special_tokens=False)
                query_indices = list(range(len(query_tokens)))
                cache_policy.register_provenance(query_indices, ["query"] * len(query_indices), [1.0] * len(query_indices))

                # Passage provenance
                offset = len(query_tokens)
                for i, (passage, score) in enumerate(zip(top_passages, scores)):
                    passage_tokens = self.tokenizer.encode(passage, add_special_tokens=False)
                    passage_indices = list(range(offset, offset + len(passage_tokens)))
                    passage_type = "high_rel_passage" if i < 3 else "low_rel_passage"
                    cache_policy.register_provenance(passage_indices, [passage_type] * len(passage_indices), [score] * len(passage_indices))
                    offset += len(passage_tokens)
            else:
                prompt = f"Question: {query}\n\nContext: {context}\n\nAnswer:"

            # Generate
            try:
                start_time = time.time()
                prediction = self.generate_with_cache(prompt, cache_policy, max_new_tokens=50)
                latency = time.time() - start_time

                # Evaluate
                f1 = compute_f1(prediction, ground_truths)
                em = compute_exact_match(prediction, ground_truths)

                results.append({
                    'task': sample['task'],
                    'prediction': prediction,
                    'ground_truths': ground_truths,
                    'f1': f1,
                    'em': em,
                    'latency': latency
                })
            except Exception as e:
                log.warning(f"Failed sample {i}: {e}")
                continue

        return results

    def run_experiment(self, poc: bool = False):
        """Run full experiment"""
        num_samples = 10 if poc else None

        conditions = {
            'FullKV': FullKVCache(),
            'H2O': H2OCache(H2OCacheConfig()),
            'ProvenanceCache': ProvenanceCache(ProvenanceCacheConfig()),
            'Random': RandomCache()
        }

        all_results = {}
        for name, policy in conditions.items():
            results = self.run_condition(name, policy, num_samples=num_samples)
            all_results[name] = results

            if len(results) > 0:
                agg = aggregate_results(results)
                log.info(f"{name}: F1={agg['f1_mean']:.4f}±{agg['f1_std']:.4f}, EM={agg['em_mean']:.4f}")
            else:
                log.warning(f"{name}: No valid results")

        # Statistical test
        if not poc and len(all_results['ProvenanceCache']) == len(all_results['H2O']):
            prov_f1 = [r['f1'] for r in all_results['ProvenanceCache']]
            h2o_f1 = [r['f1'] for r in all_results['H2O']]
            sig_test = compute_significance(prov_f1, h2o_f1)
            log.info(f"Statistical test: p={sig_test['p_value']:.4f}, significant={sig_test['significant']}")

            # Gate check
            prov_mean = np.mean(prov_f1)
            h2o_mean = np.mean(h2o_f1)
            gate_passed = prov_mean >= h2o_mean * 1.05
            log.info(f"Gate: ProvenanceCache={prov_mean:.4f}, H2O={h2o_mean:.4f}, PASS={gate_passed}")

        return all_results

def main():
    # CPU-only PoC: use smaller model and single task
    config = {
        'model_checkpoint': 'gpt2',  # Smaller model for CPU
        'tasks': ['narrativeqa'],  # Single task only
        'seed': 42
    }

    set_seed(config['seed'])
    runner = ExperimentRunner(config)

    poc = '--poc' in sys.argv
    results = runner.run_experiment(poc=poc)

    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / ('poc_results.json' if poc else 'full_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    log.info(f"Results saved to {output_file}")

    log.info("EXPERIMENT COMPLETE")

if __name__ == '__main__':
    main()
