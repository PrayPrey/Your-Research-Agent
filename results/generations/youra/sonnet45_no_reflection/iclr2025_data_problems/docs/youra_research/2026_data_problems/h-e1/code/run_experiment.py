"""
H-E1 Contamination Detection Experiment
Three-Tier Detection System Validation

Gate: MUST_WORK - Combined detection power ≥80% at <5% FPR
"""
import os
import sys
import random
import numpy as np
import json
from datetime import datetime
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.config import (
    TrainingConfig,
    ContaminationConfig,
    Tier1Config,
    Tier2Config,
    Tier3Config,
    EvaluationConfig
)
from data.loader import ContaminationDataset
from detectors.combined import CombinedDetector

def set_seed(seed):
    """Set random seeds for reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def prepare_dataset_for_training(samples, tokenizer, max_length=512):
    """Convert samples to tokenized format for training"""
    texts = []
    for sample in samples:
        question = sample.get('question', '')
        answer = sample.get('answer', '')
        text = f"Question: {question}\nAnswer: {answer}"
        texts.append(text)

    encodings = tokenizer(texts, truncation=True, padding='max_length', max_length=max_length, return_tensors='pt')

    class SimpleDataset(torch.utils.data.Dataset):
        def __init__(self, encodings):
            self.encodings = encodings

        def __len__(self):
            return len(self.encodings['input_ids'])

        def __getitem__(self, idx):
            return {key: val[idx] for key, val in self.encodings.items()}

    return SimpleDataset(encodings)

def extract_answer_number(answer_text):
    """Extract the final answer number from GSM8K format (#### <number>)"""
    import re
    # GSM8K format: answer ends with #### <number>
    match = re.search(r'####\s*(-?\d+\.?\d*)', answer_text)
    if match:
        return float(match.group(1))
    return None

def evaluate_gsm8k_accuracy(model, tokenizer, test_data, max_samples=100):
    """
    Evaluate model accuracy on GSM8K test set
    Returns accuracy as fraction of correct answers
    """
    model.eval()
    correct = 0
    total = 0

    # Sample subset for efficiency (full evaluation is expensive)
    import random
    samples = random.sample(list(test_data), min(max_samples, len(test_data)))

    with torch.no_grad():
        for sample in samples:
            question = sample.get('question', '')
            answer = sample.get('answer', '')

            # Get ground truth answer
            gt_number = extract_answer_number(answer)
            if gt_number is None:
                continue

            # Generate prediction
            prompt = f"Question: {question}\nAnswer:"
            inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=256)
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

            # Generate answer
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                num_beams=1,
                pad_token_id=tokenizer.eos_token_id
            )

            # Decode and extract predicted number
            generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            pred_number = extract_answer_number(generated)

            # Compare
            if pred_number is not None and abs(pred_number - gt_number) < 0.01:
                correct += 1
            total += 1

    accuracy = correct / total if total > 0 else 0.0
    model.train()
    return accuracy

def run_single_experiment(
    contamination_rate: float,
    seed: int,
    configs: dict,
    model_name: str = "EleutherAI/pythia-1.4b"
) -> dict:
    """Run a single experiment run with real model training"""
    set_seed(seed)

    # Load data
    dataset = ContaminationDataset(contamination_rate=contamination_rate, seed=seed)
    gsm8k_train = dataset.load_gsm8k("train")
    gsm8k_test = dataset.load_gsm8k("test")

    # Create contaminated dataset
    training_data, contaminated_indices = dataset.create_contaminated_mix(
        contamination_rate=contamination_rate,
        background_size=5000
    )

    # Load real model and tokenizer
    print(f"  Loading model {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        cache_dir="./models/pretrained"
    )

    # Prepare tokenized dataset
    train_dataset = prepare_dataset_for_training(training_data, tokenizer)

    # Training arguments - lightweight for PoC
    train_config = configs['train']
    training_args = TrainingArguments(
        output_dir=f"./checkpoints/run_{seed}_{contamination_rate}",
        num_train_epochs=1,  # Reduced for PoC
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_steps=50,
        save_strategy="epoch",
        fp16=False,  # Disabled to avoid FP16 gradient issues
        seed=seed,
        remove_unused_columns=False,
        report_to="none"
    )

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Train model
    print(f"  Training model (contamination={contamination_rate*100:.1f}%)...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    # Evaluate initial accuracy (before training)
    print(f"  Evaluating initial accuracy...")
    initial_accuracy = evaluate_gsm8k_accuracy(model, tokenizer, gsm8k_test, max_samples=50)
    print(f"  Initial accuracy: {initial_accuracy:.4f}")

    # Train
    trainer.train()

    # Evaluate final accuracy (after training)
    print(f"  Evaluating final accuracy...")
    final_accuracy = evaluate_gsm8k_accuracy(model, tokenizer, gsm8k_test, max_samples=50)
    print(f"  Final accuracy: {final_accuracy:.4f}")

    tokens_processed = len(training_data) * 256  # Approximate tokens

    # Initialize combined detector
    detector = CombinedDetector(
        tier1_config=vars(configs['tier1']),
        tier2_config=vars(configs['tier2']),
        tier3_config=vars(configs['tier3'])
    )

    # Index benchmark
    detector.index_benchmark(list(gsm8k_test))

    # Training metrics for detection
    training_metrics = {
        'initial_accuracy': initial_accuracy,
        'final_accuracy': final_accuracy,
        'tokens_processed': tokens_processed
    }

    # Run detection
    detected, detection_results = detector.detect_contamination(
        model=model,
        training_data=training_data,
        benchmark_data=list(gsm8k_test),
        training_metrics=training_metrics
    )

    # Ground truth
    ground_truth_contaminated = (contamination_rate > 0.0)

    # Clean up model to save memory
    del model
    del trainer
    torch.cuda.empty_cache()

    return {
        'seed': seed,
        'contamination_rate': contamination_rate,
        'ground_truth': ground_truth_contaminated,
        'detected': detected,
        'correct': detected == ground_truth_contaminated,
        'detection_results': detection_results,
        'training_metrics': training_metrics
    }

def evaluate_detection_power(results: list, eval_config: EvaluationConfig) -> dict:
    """Evaluate detection performance across runs"""

    # Separate by contamination rate
    results_by_rate = {}
    for r in results:
        rate = r['contamination_rate']
        if rate not in results_by_rate:
            results_by_rate[rate] = []
        results_by_rate[rate].append(r)

    # Compute metrics
    metrics = {}

    # Clean baseline (0% contamination) - measure FPR
    clean_results = results_by_rate.get(0.0, [])
    false_positives = sum(1 for r in clean_results if r['detected'])
    fpr = false_positives / len(clean_results) if clean_results else 0.0

    # Contaminated runs (1%, 5%) - measure detection power
    detection_powers = {}
    for rate in [0.01, 0.05]:
        contam_results = results_by_rate.get(rate, [])
        true_positives = sum(1 for r in contam_results if r['detected'])
        detection_powers[rate] = true_positives / len(contam_results) if contam_results else 0.0

    # Combined detection power (average across contamination rates)
    combined_power = np.mean(list(detection_powers.values())) if detection_powers else 0.0

    # Gate check
    gate_satisfied = (
        combined_power >= eval_config.target_detection_power and
        fpr < eval_config.max_false_positive_rate
    )

    metrics = {
        'false_positive_rate': fpr,
        'detection_power_1pct': detection_powers.get(0.01, 0.0),
        'detection_power_5pct': detection_powers.get(0.05, 0.0),
        'combined_detection_power': combined_power,
        'gate_satisfied': gate_satisfied,
        'target_power': eval_config.target_detection_power,
        'max_fpr': eval_config.max_false_positive_rate
    }

    return metrics

def main():
    """Main experiment execution"""
    print("="*80)
    print("H-E1: Three-Tier Contamination Detection Experiment")
    print("="*80)

    # Load configs
    train_config = TrainingConfig()
    contam_config = ContaminationConfig()
    tier1_config = Tier1Config()
    tier2_config = Tier2Config()
    tier3_config = Tier3Config()
    eval_config = EvaluationConfig()

    configs = {
        'train': train_config,
        'contamination': contam_config,
        'tier1': tier1_config,
        'tier2': tier2_config,
        'tier3': tier3_config,
        'eval': eval_config
    }

    # Run experiments
    all_results = []
    contamination_rates = contam_config.rates  # [0.0, 0.01, 0.05]
    num_runs_per_rate = 20

    for rate in contamination_rates:
        print(f"\nRunning experiments with {rate*100:.1f}% contamination...")
        for run_idx in range(num_runs_per_rate):
            seed = train_config.seed_base + run_idx
            result = run_single_experiment(rate, seed, configs)
            all_results.append(result)
            print(f"  Run {run_idx+1}/{num_runs_per_rate}: Detected={result['detected']}, Correct={result['correct']}")

    # Evaluate
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)

    metrics = evaluate_detection_power(all_results, eval_config)

    print(f"\nFalse Positive Rate: {metrics['false_positive_rate']:.2%} (target: <{metrics['max_fpr']:.0%})")
    print(f"Detection Power (1%): {metrics['detection_power_1pct']:.2%}")
    print(f"Detection Power (5%): {metrics['detection_power_5pct']:.2%}")
    print(f"Combined Detection Power: {metrics['combined_detection_power']:.2%} (target: ≥{metrics['target_power']:.0%})")

    print(f"\n{'='*80}")
    if metrics['gate_satisfied']:
        print("✅ GATE SATISFIED: MUST_WORK condition met")
        print(f"   Detection power {metrics['combined_detection_power']:.1%} ≥ {metrics['target_power']:.0%}")
        print(f"   False positive rate {metrics['false_positive_rate']:.1%} < {metrics['max_fpr']:.0%}")
    else:
        print("❌ GATE FAILED: MUST_WORK condition not met")
        if metrics['combined_detection_power'] < metrics['target_power']:
            print(f"   Detection power {metrics['combined_detection_power']:.1%} < {metrics['target_power']:.0%}")
        if metrics['false_positive_rate'] >= metrics['max_fpr']:
            print(f"   False positive rate {metrics['false_positive_rate']:.1%} ≥ {metrics['max_fpr']:.0%}")
    print("="*80)

    # Save results
    output = {
        'experiment': 'H-E1_contamination_detection',
        'timestamp': datetime.now().isoformat(),
        'configs': {k: vars(v) for k, v in configs.items()},
        'metrics': metrics,
        'all_results': all_results
    }

    with open('experiment_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Results saved to experiment_results.json")
    print("\nEXPERIMENT COMPLETE")

if __name__ == '__main__':
    main()
