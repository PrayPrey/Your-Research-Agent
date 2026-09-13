"""Data pipeline: TriviaQA loading, answer sampling, and embedding extraction."""

import os
import json
import hashlib
import numpy as np
import torch
from typing import List, Dict, Tuple
from datasets import load_dataset
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm


class TriviaQALoader:
    """Load and preprocess TriviaQA dataset."""
    
    def __init__(self, cache_dir: str, seed: int = 42):
        self.cache_dir = cache_dir
        self.seed = seed
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_validation(self, n: int) -> List[Dict]:
        """Load TriviaQA validation set."""
        print(f"Loading TriviaQA validation set (n={n})...")
        dataset = load_dataset(
            "trivia_qa",
            "rc.wikipedia",
            split="validation",
            trust_remote_code=True,
            cache_dir=self.cache_dir
        )
        
        # Select first n questions
        dataset = dataset.select(range(min(n, len(dataset))))
        
        # Convert to list of dicts
        data = []
        for item in dataset:
            data.append({
                'question_id': item.get('question_id', str(len(data))),
                'question': item['question'],
                'answer': item['answer'],
            })
        
        return self.preprocess(data)
    
    def preprocess(self, data: List[Dict]) -> List[Dict]:
        """Filter and normalize answers."""
        filtered = []
        for item in data:
            answer_value = item['answer'].get('value', '')
            answer_aliases = item['answer'].get('aliases', [])
            
            if not answer_value or not answer_aliases:
                continue
            
            # Normalize
            item['answer']['value'] = answer_value.lower().strip()
            item['answer']['aliases'] = [a.lower().strip() for a in answer_aliases]
            filtered.append(item)
        
        print(f"Preprocessed: {len(filtered)}/{len(data)} questions kept")
        return filtered
    
    def check_correctness(self, answer: str, ground_truth: Dict) -> bool:
        """Check if answer matches any ground truth alias."""
        answer_clean = answer.lower().strip()
        return answer_clean in ground_truth['aliases'] or answer_clean == ground_truth['value']


class AnswerSampler:
    """Generate answer samples using Llama-2."""
    
    def __init__(self, model_name: str, device: str, cache_dir: str):
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Loading QA model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float16,
            device_map=device
        )
        self.model.eval()
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def sample(self, questions: List[str], n: int, temp: float, batch: int) -> List[List[str]]:
        """Generate N answers per question."""
        all_answers = []
        
        for question in tqdm(questions, desc="Sampling answers"):
            # Check cache
            cache_key = self._cache_key(question, n, temp)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    answers = json.load(f)
                all_answers.append(answers)
                continue
            
            # Generate answers
            prompt = f"Answer the following question in a few words.\n\nQuestion: {question}\nAnswer:"
            
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=temp,
                    top_p=0.95,
                    do_sample=True,
                    num_return_sequences=n,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode answers
            answers = []
            for output in outputs:
                answer = self.tokenizer.decode(output, skip_special_tokens=True)
                # Extract answer part (after "Answer:")
                if "Answer:" in answer:
                    answer = answer.split("Answer:")[-1].strip()
                answers.append(answer)
            
            # Cache
            with open(cache_path, 'w') as f:
                json.dump(answers, f)
            
            all_answers.append(answers)
        
        return all_answers
    
    def _cache_key(self, question: str, n: int, temp: float) -> str:
        """Generate cache key."""
        key = f"{question}_{self.model_name}_{n}_{temp}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]


class Embedder:
    """Extract DeBERTa embeddings."""
    
    def __init__(self, model_name: str, device: str, batch_size: int):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        
        print(f"Loading embedding model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Extract embeddings for texts."""
        embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Mean pooling
                hidden = outputs.last_hidden_state
                attention_mask = inputs['attention_mask'].unsqueeze(-1)
                masked_hidden = hidden * attention_mask
                summed = masked_hidden.sum(dim=1)
                counts = attention_mask.sum(dim=1).clamp(min=1)
                pooled = summed / counts
                
                # L2 normalize
                pooled = pooled / pooled.norm(dim=-1, keepdim=True)
                embeddings.append(pooled.cpu().numpy())
        
        embeddings = np.concatenate(embeddings, axis=0)
        
        # Validate
        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-4), "Embeddings not L2 normalized"
        
        return embeddings
    
    def similarity_matrix(self, emb: np.ndarray) -> np.ndarray:
        """Compute cosine similarity matrix."""
        S = emb @ emb.T
        
        # Validate
        assert np.allclose(S, S.T), "Similarity matrix not symmetric"
        assert np.allclose(np.diag(S), 1.0, atol=1e-6), "Diagonal not 1.0"
        assert np.all((S >= -0.01) & (S <= 1.01)), "Similarity out of range"
        
        return S
