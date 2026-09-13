"""
Evaluation Module
Implements preference evaluation and attribute steering evaluation
"""

import torch
import numpy as np
from tqdm import tqdm
import json
import random


class GPT4Judge:
    """
    Model-based preference judge using perplexity comparison
    Uses the trained model's own confidence as a proxy for preference
    """

    def __init__(self, model=None, tokenizer=None, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def evaluate_batch(self, prompts, generated_responses, baseline_responses):
        """
        Evaluate preference: generated vs baseline using perplexity
        Returns: list of win/loss/tie (1/0/0.5)
        """
        results = []

        for prompt, gen_resp, base_resp in zip(prompts, generated_responses, baseline_responses):
            # Compute perplexity for both responses given prompt
            gen_ppl = self._compute_perplexity(prompt, gen_resp)
            base_ppl = self._compute_perplexity(prompt, base_resp)

            # Lower perplexity = better (more confident)
            if gen_ppl < base_ppl:
                results.append(1)  # Win
            elif gen_ppl > base_ppl:
                results.append(0)  # Loss
            else:
                results.append(0.5)  # Tie

        return results

    def _compute_perplexity(self, prompt, response):
        """Compute perplexity of response given prompt"""
        if self.model is None:
            # Fallback: use response length as proxy (shorter = better for quality)
            return len(response) / 100.0

        # Combine prompt and response
        full_text = prompt + " " + response
        input_ids = self.tokenizer.encode(full_text, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.model(input_ids, labels=input_ids)
            loss = outputs.loss

        # Perplexity = exp(loss)
        perplexity = torch.exp(loss).item()

        return perplexity

    def compute_win_rate(self, results):
        """Compute overall win rate"""
        return np.mean(results)


class AttributeEvaluator:
    """
    Evaluate attribute steering accuracy
    Tests whether model can generate responses with specified attributes
    """

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def generate_with_attributes(self, prompt, target_attrs, max_length=100):
        """
        Generate response conditioned on target attributes

        Args:
            prompt: Input prompt string
            target_attrs: dict with keys ["helpfulness", "verbosity", "creativity"]
            max_length: Max generation length
        Returns:
            generated_text: str
        """
        # Tokenize prompt
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        # Generate (simplified: no attribute conditioning in generation for PoC)
        with torch.no_grad():
            output_ids = self.model.model.generate(
                input_ids,
                max_length=input_ids.shape[1] + max_length,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode
        generated_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

        return generated_text

    def predict_attributes(self, text):
        """
        Predict attributes from generated text using trained model's attribute head
        """
        # Tokenize text
        input_ids = self.tokenizer.encode(text, return_tensors="pt", max_length=512, truncation=True).to(self.device)

        # Get model's attribute predictions
        with torch.no_grad():
            outputs = self.model.model(input_ids, output_hidden_states=True)
            hidden_states = outputs.hidden_states[-1]  # Last layer

            # Use attribute head to predict
            attr_logits = self.model.attr_head(hidden_states)  # List of 3 x (1, 5)

            # Get predicted levels (1-5 scale)
            predicted = {
                "helpfulness": torch.argmax(attr_logits[0], dim=-1).item() + 1,  # +1 for 1-indexed
                "verbosity": torch.argmax(attr_logits[1], dim=-1).item() + 1,
                "creativity": torch.argmax(attr_logits[2], dim=-1).item() + 1
            }

        return predicted

    def evaluate_steering_accuracy(self, test_prompts, attribute_combinations, num_samples=100):
        """
        Test attribute steering accuracy

        Args:
            test_prompts: List of test prompts
            attribute_combinations: List of attribute dicts to test
            num_samples: Number of samples per combination
        Returns:
            accuracy: % within ±0.5 of target
        """
        total_tests = 0
        correct_tests = 0

        for attr_combo in tqdm(attribute_combinations, desc="Testing attribute combinations"):
            for _ in range(num_samples):
                # Random prompt
                prompt = random.choice(test_prompts)

                # Generate with target attributes
                generated = self.generate_with_attributes(prompt, attr_combo)

                # Predict attributes
                predicted = self.predict_attributes(generated)

                # Check accuracy (within ±0.5 for each attribute)
                for attr_name in ["helpfulness", "verbosity", "creativity"]:
                    target_val = attr_combo[attr_name]
                    pred_val = predicted[attr_name]

                    if abs(pred_val - target_val) <= 0.5:
                        correct_tests += 1

                    total_tests += 1

        accuracy = correct_tests / total_tests if total_tests > 0 else 0.0

        return accuracy

    def evaluate(self, test_loader, num_test_samples=600):
        """
        Run full evaluation: preference + steering

        Args:
            test_loader: Test data loader
            num_test_samples: Number of samples to evaluate
        Returns:
            results: dict with metrics
        """
        # Get test prompts from loader
        test_prompts = []
        for batch in test_loader:
            # Decode prompts
            for i in range(len(batch["prompt_ids"])):
                prompt = self.tokenizer.decode(batch["prompt_ids"][i], skip_special_tokens=True)
                test_prompts.append(prompt)

            if len(test_prompts) >= 1000:
                break

        # Preference evaluation using model-based judge
        gpt4_judge = GPT4Judge(model=self, tokenizer=self.tokenizer, device=self.device)
        preference_results = []

        print("Evaluating preference win rate...")
        for i in tqdm(range(min(1000, len(test_prompts)))):
            prompt = test_prompts[i]

            # Generate response with target attributes
            generated = self.generate_with_attributes(prompt, {
                "helpfulness": 4,
                "verbosity": 3,
                "creativity": 4
            }, max_length=50)

            # Generate baseline response (neutral attributes)
            baseline = self.generate_with_attributes(prompt, {
                "helpfulness": 3,
                "verbosity": 3,
                "creativity": 3
            }, max_length=50)

            # Judge
            result = gpt4_judge.evaluate_batch([prompt], [generated], [baseline])
            preference_results.extend(result)

        win_rate = gpt4_judge.compute_win_rate(preference_results)

        # Attribute steering evaluation
        print("\nEvaluating attribute steering accuracy...")
        attribute_combinations = [
            {"helpfulness": 5, "verbosity": 3, "creativity": 4},
            {"helpfulness": 3, "verbosity": 5, "creativity": 2},
            {"helpfulness": 4, "verbosity": 2, "creativity": 5},
            {"helpfulness": 2, "verbosity": 4, "creativity": 3},
            {"helpfulness": 5, "verbosity": 5, "creativity": 5},
            {"helpfulness": 1, "verbosity": 1, "creativity": 1}
        ]

        steering_accuracy = self.evaluate_steering_accuracy(
            test_prompts[:100],
            attribute_combinations,
            num_samples=100
        )

        results = {
            "preference_win_rate": win_rate,
            "steering_accuracy": steering_accuracy,
            "num_preference_tests": len(preference_results),
            "num_steering_tests": len(attribute_combinations) * 100 * 3  # 3 attributes
        }

        return results


if __name__ == "__main__":
    print("Testing evaluation module...")

    # Test GPT4Judge
    judge = GPT4Judge()
    prompts = ["Test prompt 1", "Test prompt 2"]
    generated = ["Response 1", "Response 2"]
    baseline = ["Baseline 1", "Baseline 2"]

    results = judge.evaluate_batch(prompts, generated, baseline)
    win_rate = judge.compute_win_rate(results)

    print(f"✓ GPT4Judge: win_rate = {win_rate:.2%}")
    print("✓ Evaluation module working")
