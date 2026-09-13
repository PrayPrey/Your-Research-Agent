CHAT_MODELS = {
    "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama/Llama-2-13b-chat-hf",
    "mistralai/Mistral-7B-Instruct-v0.1",
}

# Answer choices per task
TASK_CHOICES = {
    "qqp": ["No", "Yes"],       # label 0=not-duplicate, 1=duplicate
    "sst2": ["negative", "positive"],  # label 0=neg, 1=pos
    "nli": ["entailment", "neutral", "contradiction"],  # 0,1,2
}


def _format_qqp(example, model_id):
    q1, q2 = example["question1"], example["question2"]
    prompt = (
        f"Are these two questions asking the same thing?\n"
        f"Question 1: {q1}\nQuestion 2: {q2}\n"
        f"Answer (No/Yes):"
    )
    if model_id in CHAT_MODELS:
        prompt = f"[INST] {prompt} [/INST]"
    return prompt, TASK_CHOICES["qqp"]


def _format_sst2(example, model_id):
    sentence = example["sentence"]
    prompt = (
        f"Sentiment of this review (negative/positive):\n{sentence}\nAnswer:"
    )
    if model_id in CHAT_MODELS:
        prompt = f"[INST] {prompt} [/INST]"
    return prompt, TASK_CHOICES["sst2"]


def _format_nli(example, model_id):
    # Handle different field names across datasets
    premise = example.get("premise", example.get("sentence1", ""))
    hypothesis = example.get("hypothesis", example.get("sentence2", ""))
    prompt = (
        f"Premise: {premise}\nHypothesis: {hypothesis}\n"
        f"Relationship (entailment/neutral/contradiction):"
    )
    if model_id in CHAT_MODELS:
        prompt = f"[INST] {prompt} [/INST]"
    return prompt, TASK_CHOICES["nli"]


def format_mc_prompt(example, task, model_id):
    if task == "qqp":
        return _format_qqp(example, model_id)
    elif task == "sst2":
        return _format_sst2(example, model_id)
    elif task == "nli":
        return _format_nli(example, model_id)
    else:
        raise ValueError(f"Unknown task: {task}")
