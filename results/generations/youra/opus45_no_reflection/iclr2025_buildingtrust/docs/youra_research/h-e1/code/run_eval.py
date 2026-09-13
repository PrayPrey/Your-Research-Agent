"""H-E1: TruthfulQA MC1 + TextFooler ASR Evaluation Pipeline (Simplified PoC)"""

import json
import os
import numpy as np
import torch
from typing import Dict, List, Optional
from pathlib import Path

from config import (
    MODEL_IDS, MODEL_PARAMS, MODEL_FAMILY, LARGE_MODELS, BATCH_SIZE, SEED,
    TRUTHFULQA_TASK, TEXTFOOLER_NUM_EXAMPLES, RESULTS_PATH
)

SMALL_MODELS = [m for m in MODEL_IDS if m not in LARGE_MODELS]


def eval_truthfulqa_mc1(model_id: str, batch_size: int = BATCH_SIZE) -> float:
    """Run lm-eval-harness TruthfulQA MC1 task. Returns accuracy in [0,1]."""
    try:
        from lm_eval import evaluator
        from lm_eval.models.huggingface import HFLM
    except ImportError:
        print(f"  lm-eval import error, skipping {model_id}")
        return None

    print(f"  Evaluating TruthfulQA MC1 for {model_id}...")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        lm = HFLM(
            pretrained=model_id,
            batch_size=batch_size,
            device=device,
        )

        results = evaluator.simple_evaluate(
            model=lm,
            tasks=[TRUTHFULQA_TASK],
            batch_size=batch_size
        )

        acc = results["results"][TRUTHFULQA_TASK]["acc,none"]
        print(f"  MC1 Accuracy: {acc:.4f}")

        del lm
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return float(acc)

    except Exception as e:
        print(f"  Error evaluating {model_id}: {e}")
        return None
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class LLMSentimentWrapper:
    """TextAttack-compatible wrapper that uses LLM prompting for sentiment classification."""

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.prompt_template = "Classify the sentiment as positive or negative. Text: {text}\nSentiment:"

    def __call__(self, text_list):
        import torch.nn.functional as F
        probs = []
        for text in text_list:
            prompt = self.prompt_template.format(text=text)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits[0, -1]

            pos_tokens = self.tokenizer.encode(" positive", add_special_tokens=False)
            neg_tokens = self.tokenizer.encode(" negative", add_special_tokens=False)

            pos_logit = logits[pos_tokens[0]] if pos_tokens else logits.max()
            neg_logit = logits[neg_tokens[0]] if neg_tokens else logits.min()

            pair_logits = torch.tensor([neg_logit, pos_logit])
            pair_probs = F.softmax(pair_logits, dim=0).cpu().numpy()
            probs.append(pair_probs)

        return np.array(probs)


def eval_textfooler_asr(model_id: str, num_examples: int = TEXTFOOLER_NUM_EXAMPLES) -> float:
    """Run TextFooler attack on SST-2. Returns Attack Success Rate in [0,1]."""
    try:
        from textattack.models.wrappers import ModelWrapper
        from textattack.datasets import HuggingFaceDataset
        from textattack.attack_recipes import TextFoolerJin2019
        from textattack import Attacker, AttackArgs
        from transformers import AutoModelForCausalLM, AutoTokenizer, T5ForConditionalGeneration
    except ImportError as e:
        print(f"  TextAttack import error: {e}")
        return None

    print(f"  Running TextFooler attack for {model_id}...")

    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        if "t5" in model_id.lower():
            model = T5ForConditionalGeneration.from_pretrained(model_id, torch_dtype=torch.float16)
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_id, torch_dtype=torch.float16, trust_remote_code=True
            )

        model = model.to(device).eval()

        class LLMWrapper(ModelWrapper):
            def __init__(self, llm_model, llm_tokenizer, llm_device):
                self.model = llm_model
                self.tokenizer = llm_tokenizer
                self.device = llm_device

            def __call__(self, text_list):
                import torch.nn.functional as F
                probs = []
                for text in text_list:
                    if "t5" in model_id.lower():
                        prompt = f"sst2 sentence: {text}"
                        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = self.model.generate(**inputs, max_new_tokens=5, return_dict_in_generate=True, output_scores=True)
                            first_token_logits = outputs.scores[0][0]

                        pos_id = self.tokenizer.encode("positive", add_special_tokens=False)[0]
                        neg_id = self.tokenizer.encode("negative", add_special_tokens=False)[0]
                    else:
                        prompt = f"Sentiment (positive/negative): {text}\nAnswer:"
                        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
                        inputs = {k: v.to(self.device) for k, v in inputs.items()}
                        with torch.no_grad():
                            outputs = self.model(**inputs)
                            first_token_logits = outputs.logits[0, -1]

                        pos_id = self.tokenizer.encode(" positive", add_special_tokens=False)[0]
                        neg_id = self.tokenizer.encode(" negative", add_special_tokens=False)[0]

                    pair = torch.tensor([first_token_logits[neg_id], first_token_logits[pos_id]])
                    pair_probs = F.softmax(pair.float(), dim=0).cpu().numpy()
                    probs.append(pair_probs)
                return np.array(probs)

        wrapper = LLMWrapper(model, tokenizer, device)
        dataset = HuggingFaceDataset("glue", "sst2", split="validation")
        attack = TextFoolerJin2019.build(wrapper)

        attack_args = AttackArgs(
            num_examples=num_examples,
            random_seed=SEED,
            disable_stdout=True,
            parallel=False
        )

        attacker = Attacker(attack, dataset, attack_args)
        results = attacker.attack_dataset()

        n_success = sum(1 for r in results if r.__class__.__name__ == "SuccessfulAttackResult")
        n_total = sum(1 for r in results if r.__class__.__name__ != "SkippedAttackResult")

        if n_total == 0:
            print(f"  No valid attack samples")
            return None

        asr = n_success / n_total
        print(f"  ASR: {asr:.4f} ({n_success}/{n_total} attacks succeeded)")

        del model, tokenizer, wrapper
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return float(asr)

    except Exception as e:
        print(f"  Error in TextFooler attack for {model_id}: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def run_all(model_ids: Optional[List[str]] = None) -> Dict:
    """Run evaluation pipeline on all models. Returns results dict."""
    if model_ids is None:
        model_ids = SMALL_MODELS

    results = {
        "model": [],
        "mc1_acc": [],
        "asr": [],
        "robustness": [],
        "log_params": []
    }

    print(f"Starting evaluation pipeline for {len(model_ids)} models...")
    print(f"(Skipping 70B models: {LARGE_MODELS})")
    print("=" * 60)

    for i, model_id in enumerate(model_ids):
        print(f"\n[{i+1}/{len(model_ids)}] {model_id}")
        print("-" * 40)

        mc1_acc = eval_truthfulqa_mc1(model_id)

        asr = eval_textfooler_asr(model_id)

        if mc1_acc is not None:
            results["model"].append(model_id)
            results["mc1_acc"].append(mc1_acc)
            results["asr"].append(asr if asr is not None else np.nan)
            results["robustness"].append(1.0 - asr if asr is not None else np.nan)
            results["log_params"].append(np.log10(MODEL_PARAMS[model_id]))

    print("\n" + "=" * 60)
    print(f"Evaluation complete: {len(results['model'])}/{len(model_ids)} models successful")

    return results


def save_results(results: Dict, path: str = RESULTS_PATH) -> None:
    """Save results to JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    results_serializable = {
        k: [float(v) if isinstance(v, (np.floating, float)) else v for v in vals]
        for k, vals in results.items()
    }

    with open(path, 'w') as f:
        json.dump(results_serializable, f, indent=2)

    print(f"Results saved to {path}")


if __name__ == "__main__":
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    results = run_all()
    save_results(results)
