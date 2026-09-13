"""HotpotQA data loading and tokenization for extractive QA."""
from datasets import load_dataset, DatasetDict
from transformers import PreTrainedTokenizer


def load_hotpot_qa(cache_dir: str | None = None) -> DatasetDict:
    """Load HotpotQA distractor split from HuggingFace."""
    return load_dataset("hotpot_qa", "distractor", cache_dir=cache_dir)


def _concat_context(example: dict) -> str:
    """Concatenate all context paragraphs into single string.

    HotpotQA context: list of [title, [sentence1, sentence2, ...]]
    """
    parts = []
    for title, sentences in zip(example["context"]["title"], example["context"]["sentences"]):
        parts.append(f"{title}: {' '.join(sentences)}")
    return " ".join(parts)


def tokenize_hotpot(
    dataset: DatasetDict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 512,
) -> DatasetDict:
    """Tokenize HotpotQA for extractive QA with answer span positions."""

    def preprocess(examples):
        questions = [q.strip() for q in examples["question"]]
        contexts = [_concat_context(ex) for ex in
                    [{"context": {"title": t, "sentences": s}}
                     for t, s in zip(examples["context"]["title"], examples["context"]["sentences"])]]

        tokenized = tokenizer(
            questions,
            contexts,
            max_length=max_length,
            truncation="only_second",
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length",
        )

        sample_mapping = tokenized.pop("overflow_to_sample_mapping")
        offset_mapping = tokenized.pop("offset_mapping")

        start_positions = []
        end_positions = []
        example_ids = []

        for i, offsets in enumerate(offset_mapping):
            sample_idx = sample_mapping[i]
            answer = examples["answer"][sample_idx]
            context = contexts[sample_idx]

            example_ids.append(examples["id"][sample_idx])

            answer_start = context.find(answer)
            if answer_start == -1 or answer.lower() in ["yes", "no"]:
                start_positions.append(0)
                end_positions.append(0)
                continue

            answer_end = answer_start + len(answer)

            sequence_ids = tokenized.sequence_ids(i)
            context_start = 0
            while context_start < len(sequence_ids) and sequence_ids[context_start] != 1:
                context_start += 1
            context_end = len(sequence_ids) - 1
            while context_end >= 0 and sequence_ids[context_end] != 1:
                context_end -= 1

            if context_start >= len(offsets) or context_end < 0:
                start_positions.append(0)
                end_positions.append(0)
                continue

            if offsets[context_start][0] > answer_end or offsets[context_end][1] < answer_start:
                start_positions.append(0)
                end_positions.append(0)
            else:
                token_start = context_start
                while token_start <= context_end and offsets[token_start][0] <= answer_start:
                    token_start += 1
                start_positions.append(token_start - 1)

                token_end = context_end
                while token_end >= context_start and offsets[token_end][1] >= answer_end:
                    token_end -= 1
                end_positions.append(token_end + 1)

        tokenized["start_positions"] = start_positions
        tokenized["end_positions"] = end_positions
        tokenized["example_id"] = example_ids

        return tokenized

    cols_to_remove = dataset["train"].column_names
    tokenized_dataset = dataset.map(
        preprocess,
        batched=True,
        remove_columns=cols_to_remove,
    )

    return tokenized_dataset
