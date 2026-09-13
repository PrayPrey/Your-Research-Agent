"""LLaMA answer generation module with caching."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
import json
import os
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class GeneratedAnswer:
    """Container for generated answer with metadata."""
    text: str
    logits: Optional[torch.Tensor] = None
    generation_config: Optional[dict] = None


class LLaMAGenerator:
    """Generate multiple answers per question using LLaMA-2-7B."""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-chat-hf",
        device: str = "cuda",
        dtype: str = "float16"
    ):
        self.model_name = model_name
        self.device = device
        self.dtype = getattr(torch, dtype)
        self.model = None
        self.tokenizer = None
    
    def load_model(self):
        """Load LLaMA model with FP16 precision."""
        logger.info(f"Loading {self.model_name} with {self.dtype}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=self.dtype,
        )
        self.model.eval()
        logger.info("Model loaded successfully")
    
    def generate_answers(
        self,
        question: str,
        num_samples: int = 10,
        temperature: float = 1.0,
        top_p: float = 0.95,
        max_new_tokens: int = 50
    ) -> List[GeneratedAnswer]:
        """Generate multiple answers via nucleus sampling."""
        prompt = f"Answer the following question concisely: {question}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        answers = []
        config = {
            'temperature': temperature,
            'top_p': top_p,
            'max_new_tokens': max_new_tokens,
            'num_samples': num_samples
        }
        
        for _ in range(num_samples):
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    return_dict_in_generate=True,
                    output_scores=True
                )
            
            answer_text = self.tokenizer.decode(
                output.sequences[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Extract final token logits for baselines
            final_logits = output.scores[-1][0] if output.scores else None
            
            answers.append(GeneratedAnswer(
                text=answer_text,
                logits=final_logits,
                generation_config=config
            ))
        
        return answers
    
    def batch_generate(
        self,
        samples: List[Dict],
        cache_manager: 'CacheManager',
        checkpoint_interval: int = 100
    ) -> Dict[int, List[GeneratedAnswer]]:
        """Generate answers for all samples with checkpointing."""
        logger.info(f"Generating answers for {len(samples)} questions")
        
        if self.model is None:
            self.load_model()
        
        all_generations = {}
        
        for idx, sample in enumerate(tqdm(samples, desc="Generating answers")):
            example_id = sample['example_id']
            
            # Check cache first
            if cache_manager.exists(example_id):
                all_generations[example_id] = cache_manager.load(example_id)
                continue
            
            # Generate answers
            answers = self.generate_answers(sample['question'])
            all_generations[example_id] = answers
            
            # Save to cache
            cache_manager.save(example_id, answers, sample['question'])
            
            # Checkpoint
            if (idx + 1) % checkpoint_interval == 0:
                logger.info(f"Checkpoint: {idx + 1}/{len(samples)} completed")
        
        logger.info("Answer generation complete")
        return all_generations


class CacheManager:
    """Manage caching of generated answers."""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_path(self, example_id: int) -> str:
        """Get cache file path for example."""
        return os.path.join(self.cache_dir, f"gen_{example_id}.json")
    
    def exists(self, example_id: int) -> bool:
        """Check if cached answers exist."""
        return os.path.exists(self._get_path(example_id))
    
    def save(self, example_id: int, answers: List[GeneratedAnswer], question: str):
        """Save generated answers to cache."""
        data = {
            'example_id': example_id,
            'question': question,
            'answers': [
                {
                    'text': ans.text,
                    'logits': ans.logits.cpu().tolist() if ans.logits is not None else None,
                    'config': ans.generation_config
                }
                for ans in answers
            ]
        }
        with open(self._get_path(example_id), 'w') as f:
            json.dump(data, f)
    
    def load(self, example_id: int) -> List[GeneratedAnswer]:
        """Load cached answers."""
        with open(self._get_path(example_id), 'r') as f:
            data = json.load(f)
        
        answers = []
        for ans_data in data['answers']:
            logits = torch.tensor(ans_data['logits']) if ans_data['logits'] else None
            answers.append(GeneratedAnswer(
                text=ans_data['text'],
                logits=logits,
                generation_config=ans_data['config']
            ))
        return answers
