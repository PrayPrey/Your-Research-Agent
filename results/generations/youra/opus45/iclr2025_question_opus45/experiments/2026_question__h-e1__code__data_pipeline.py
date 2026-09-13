"""Data pipeline for loading TruthfulQA and generating responses with hidden states."""

import json
import os
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from sklearn.model_selection import train_test_split
from transformers import AutoModelForCausalLM, AutoTokenizer
import warnings

# Suppress the max_new_tokens warning
warnings.filterwarnings("ignore", message=".*max_new_tokens.*max_length.*")

from config import ExperimentConfig


class DataPipeline:
    """Handles dataset loading, response generation, and hidden state extraction."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self):
        """Lazy load the LLM."""
        if self.model is None:
            print(f"Loading {self.config.llm_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.llm_name,
                trust_remote_code=True,
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.padding_side = "left"

            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.llm_name,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )
            self.model.eval()
            print("Model loaded successfully.")

    def load_dataset(self) -> tuple[list[str], list[str]]:
        """Load TruthfulQA and split into train/test."""
        print("Loading TruthfulQA dataset...")
        dataset = load_dataset(
            self.config.dataset_name,
            self.config.dataset_config,
            split="validation",  # TruthfulQA only has validation split
        )

        questions = [item["question"] for item in dataset]
        train_qs, test_qs = train_test_split(
            questions,
            test_size=self.config.test_size,
            random_state=self.config.seed,
        )
        print(f"Dataset loaded: {len(train_qs)} train, {len(test_qs)} test questions")
        return train_qs, test_qs

    def _format_prompt(self, question: str) -> str:
        """Format question as chat prompt for Llama-3."""
        messages = [
            {"role": "user", "content": question}
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        return prompt

    def _extract_hidden_state(self, input_ids: torch.Tensor) -> np.ndarray:
        """Extract TBG hidden state from layer 25 using forward pass only."""
        with torch.no_grad():
            outputs = self.model(
                input_ids,
                output_hidden_states=True,
                return_dict=True,
            )
            # Get layer 25 hidden state at last token position (TBG)
            layer_hidden = outputs.hidden_states[self.config.layer_idx]
            tbg_hidden = layer_hidden[0, -1, :].cpu().float().numpy()
        return tbg_hidden

    def generate_responses(
        self, questions: list[str]
    ) -> tuple[np.ndarray, list[list[str]]]:
        """Generate N responses per question and extract layer-25 TBG hidden states.

        Uses batched generation with num_return_sequences for efficiency.

        Returns:
            hidden_states: (N_questions, 4096) - TBG token hidden states
            responses: list of list[str] - generated responses per question
        """
        self._load_model()

        all_hidden_states = []
        all_responses = []

        # Use smaller batches for num_return_sequences to avoid OOM
        batch_size = 5  # Generate 5 responses at a time

        for q_idx, question in enumerate(questions):
            if (q_idx + 1) % 5 == 0 or q_idx == 0:
                print(f"Processing question {q_idx + 1}/{len(questions)}", flush=True)

            prompt = self._format_prompt(question)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            input_length = inputs["input_ids"].shape[1]

            # Extract TBG hidden state first (single forward pass)
            tbg_hidden = self._extract_hidden_state(inputs["input_ids"])

            # Generate responses in batches
            responses_q = []
            n_batches = (self.config.n_responses + batch_size - 1) // batch_size

            for batch_idx in range(n_batches):
                n_seqs = min(batch_size, self.config.n_responses - batch_idx * batch_size)

                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=self.config.max_new_tokens,
                        temperature=self.config.temperature,
                        do_sample=True,
                        num_return_sequences=n_seqs,
                        pad_token_id=self.tokenizer.pad_token_id,
                    )

                # Decode responses
                for seq in outputs:
                    generated_ids = seq[input_length:]
                    response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
                    responses_q.append(response.strip())

            all_hidden_states.append(tbg_hidden)
            all_responses.append(responses_q)

        hidden_states = np.stack(all_hidden_states, axis=0)
        return hidden_states, all_responses

    def load_or_generate(
        self, questions: list[str], split: str
    ) -> tuple[np.ndarray, list[list[str]]]:
        """Cache-aware wrapper: load from cache or generate."""
        cache_dir = Path(self.config.cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        hidden_path = cache_dir / f"hidden_states_{split}.npy"
        responses_path = cache_dir / f"responses_{split}.json"

        if hidden_path.exists() and responses_path.exists():
            print(f"Loading cached data for {split} split...")
            hidden_states = np.load(hidden_path)
            with open(responses_path, "r") as f:
                responses = json.load(f)
            print(f"Loaded {len(responses)} cached questions for {split}")
            return hidden_states, responses

        print(f"Generating responses for {split} split...")
        hidden_states, responses = self.generate_responses(questions)

        # Save to cache
        np.save(hidden_path, hidden_states)
        with open(responses_path, "w") as f:
            json.dump(responses, f)
        print(f"Saved cache for {split} split")

        return hidden_states, responses
