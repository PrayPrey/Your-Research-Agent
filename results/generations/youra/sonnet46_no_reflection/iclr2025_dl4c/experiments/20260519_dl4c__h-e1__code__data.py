import random
from datasets import Dataset, load_dataset
from evalplus.data import get_human_eval_plus, get_mbpp_plus
from config import ExperimentConfig


_DEEPSEEK_CHAT_TEMPLATE = (
    "You are an AI programming assistant, utilizing the DeepSeek Coder model, "
    "developed by DeepSeek Company, and you only answer questions related to computer science. "
    "For politically sensitive questions, security and privacy issues, and other non-computer "
    "science questions, you will refuse to answer.\n"
    "### Instruction:\n{instruction}\n### Response:\n"
)


def _format_grpo_prompt(instruction: str) -> str:
    return _DEEPSEEK_CHAT_TEMPLATE.format(instruction=instruction)


def load_grpo_dataset(cfg: ExperimentConfig) -> Dataset:
    """Load CodeAlpaca-20K, format with DeepSeek-Coder chat template.
    Returns Dataset with columns: [prompt, task_id]
    """
    ds = load_dataset(cfg.training_dataset, split="train")
    prompts = []
    task_ids = []
    for i, example in enumerate(ds):
        instruction = example.get("instruction", "") or example.get("prompt", "")
        if instruction:
            prompts.append(_format_grpo_prompt(instruction))
            task_ids.append(f"codealpha-{i}")
    return Dataset.from_dict({"prompt": prompts, "task_id": task_ids})


def load_kl_prompts(cfg: ExperimentConfig) -> list:
    """Fixed 100-prompt held-out set, sampled with seed=42."""
    ds = load_dataset(cfg.training_dataset, split="train")
    all_instructions = []
    for example in ds:
        instruction = example.get("instruction", "") or example.get("prompt", "")
        if instruction:
            all_instructions.append(_format_grpo_prompt(instruction))
    rng = random.Random(42)
    sampled = rng.sample(all_instructions, min(cfg.kl_prompt_count, len(all_instructions)))
    return sampled[:cfg.kl_prompt_count]


def generate_dpo_pairs(cfg: ExperimentConfig, model_id: str) -> Dataset:
    """Generate execution-oracle preference pairs using real model-generated completions.

    For each HumanEval+ problem:
    - Generate multiple completions from the model
    - Label each completion via execution oracle (evalplus check_correctness)
    - Build chosen/rejected pairs: chosen = passing completion, rejected = failing completion
    Only problems where at least one passing AND one failing completion exist are used.

    Returns Dataset with columns: [prompt, chosen, rejected]
    """
    import gc
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from rewards import run_evalplus_tests

    print(f"[DPO data] Loading model {model_id} for completion generation...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    # Load onto a single GPU (CUDA_VISIBLE_DEVICES already set to one GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map={"": device},
        trust_remote_code=True,
    )
    model.eval()

    he_problems = get_human_eval_plus()
    prompts = []
    chosen_list = []
    rejected_list = []

    n_generations = 8  # completions per problem to find both passing and failing

    for task_id, problem in he_problems.items():
        if len(prompts) >= cfg.dpo_min_pairs:
            break

        prompt_text = _format_grpo_prompt(problem["prompt"])
        inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                num_return_sequences=n_generations,
                pad_token_id=tokenizer.eos_token_id,
            )

        completions = []
        for seq in output_ids:
            gen_tokens = seq[inputs["input_ids"].shape[1]:]
            completion = tokenizer.decode(gen_tokens, skip_special_tokens=True)
            completions.append(completion)

        # Label via execution oracle
        passing = []
        failing = []
        for completion in completions:
            result = run_evalplus_tests(task_id, completion)
            if result["passed"]:
                passing.append(completion)
            else:
                failing.append(completion)

        # Need at least one of each to form a valid preference pair
        if passing and failing:
            prompts.append(prompt_text)
            chosen_list.append(passing[0])
            rejected_list.append(failing[0])

    # Free model memory before returning so callers can load training models
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    if not prompts:
        raise RuntimeError(
            "No valid DPO pairs generated: no HumanEval+ problem produced "
            "both a passing and a failing model completion. Check model and generation settings."
        )

    print(f"[DPO data] Generated {len(prompts)} execution-oracle preference pairs.")
    return Dataset.from_dict({
        "prompt": prompts,
        "chosen": chosen_list,
        "rejected": rejected_list,
    })


def load_humaneval_plus() -> dict:
    """Return HumanEval+ problem dict via evalplus API."""
    return get_human_eval_plus()


def load_mbpp_plus() -> dict:
    """Return MBPP+ problem dict via evalplus API."""
    return get_mbpp_plus()
