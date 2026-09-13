"""SQuAD-v2 and HotpotQA data loading and tokenization."""
from datasets import load_dataset, DatasetDict
from transformers import PreTrainedTokenizer


def load_squad_v2(cache_dir: str | None = None) -> DatasetDict:
    """Load SQuAD-v2 dataset from HuggingFace."""
    return load_dataset("squad_v2", cache_dir=cache_dir)


def tokenize_squad(
    dataset: DatasetDict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 384,
) -> DatasetDict:
    """Tokenize SQuAD-v2 for extractive QA with answer span positions."""

    def preprocess(examples):
        questions = [q.strip() for q in examples["question"]]
        contexts = examples["context"]

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

        for i, offsets in enumerate(offset_mapping):
            sample_idx = sample_mapping[i]
            answers = examples["answers"][sample_idx]

            if len(answers["answer_start"]) == 0:
                start_positions.append(0)
                end_positions.append(0)
                continue

            start_char = answers["answer_start"][0]
            end_char = start_char + len(answers["text"][0])

            sequence_ids = tokenized.sequence_ids(i)
            context_start = 0
            while sequence_ids[context_start] != 1:
                context_start += 1
            context_end = len(sequence_ids) - 1
            while sequence_ids[context_end] != 1:
                context_end -= 1

            if offsets[context_start][0] > end_char or offsets[context_end][1] < start_char:
                start_positions.append(0)
                end_positions.append(0)
            else:
                token_start = context_start
                while token_start <= context_end and offsets[token_start][0] <= start_char:
                    token_start += 1
                start_positions.append(token_start - 1)

                token_end = context_end
                while token_end >= context_start and offsets[token_end][1] >= end_char:
                    token_end -= 1
                end_positions.append(token_end + 1)

        tokenized["start_positions"] = start_positions
        tokenized["end_positions"] = end_positions
        tokenized["example_id"] = [examples["id"][sample_mapping[i]] for i in range(len(sample_mapping))]

        return tokenized

    tokenized_dataset = dataset.map(
        preprocess,
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    return tokenized_dataset


def load_hotpotqa(cache_dir: str | None = None) -> DatasetDict:
    """Load HotpotQA distractor-setting dataset from HuggingFace."""
    return load_dataset("hotpotqa/hotpot_qa", "distractor", cache_dir=cache_dir)


def tokenize_hotpotqa(
    dataset: DatasetDict,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 384,
) -> DatasetDict:
    """Tokenize HotpotQA for extractive QA with answer span positions.

    Context is the concatenation of all supporting and distractor paragraphs.
    """

    def preprocess(examples):
        questions = [q.strip() for q in examples["question"]]
        contexts = []
        for ctx_titles, ctx_sents in zip(examples["context"]["title"], examples["context"]["sentences"]):
            full_context = " ".join(" ".join(sents) for sents in ctx_sents)
            contexts.append(full_context)

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

        for i, offsets in enumerate(offset_mapping):
            sample_idx = sample_mapping[i]
            answer_text = examples["answer"][sample_idx]
            context = contexts[sample_idx]

            start_char = context.find(answer_text)
            if start_char == -1:
                start_positions.append(0)
                end_positions.append(0)
                continue

            end_char = start_char + len(answer_text)

            sequence_ids = tokenized.sequence_ids(i)
            context_start = 0
            while context_start < len(sequence_ids) and sequence_ids[context_start] != 1:
                context_start += 1
            context_end = len(sequence_ids) - 1
            while context_end >= 0 and sequence_ids[context_end] != 1:
                context_end -= 1

            if context_start > context_end:
                start_positions.append(0)
                end_positions.append(0)
                continue

            if offsets[context_start][0] > end_char or offsets[context_end][1] < start_char:
                start_positions.append(0)
                end_positions.append(0)
            else:
                token_start = context_start
                while token_start <= context_end and offsets[token_start][0] <= start_char:
                    token_start += 1
                start_positions.append(token_start - 1)

                token_end = context_end
                while token_end >= context_start and offsets[token_end][1] >= end_char:
                    token_end -= 1
                end_positions.append(token_end + 1)

        tokenized["start_positions"] = start_positions
        tokenized["end_positions"] = end_positions
        tokenized["example_id"] = [examples["id"][sample_mapping[i]] for i in range(len(sample_mapping))]

        return tokenized

    tokenized_dataset = dataset.map(
        preprocess,
        batched=True,
        remove_columns=dataset["train"].column_names,
    )

    return tokenized_dataset
