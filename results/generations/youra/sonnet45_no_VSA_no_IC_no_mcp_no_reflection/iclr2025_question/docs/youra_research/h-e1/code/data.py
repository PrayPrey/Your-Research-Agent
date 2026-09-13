from datasets import load_dataset

def load_triviaqa_subset(split: str = "validation[:1000]"):
    dataset = load_dataset("trivia_qa", "unfiltered", split=split)
    if len(dataset) == 0:
        raise ValueError(f"Dataset empty for split: {split}")
    return dataset

def prepare_example(example: dict) -> tuple:
    question = example["question"]
    answer = example["answer"]["value"]
    return question, answer
