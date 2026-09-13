"""SQuAD v2.0 data loading and tokenization."""
from datasets import load_dataset, Dataset
from torch.utils.data import DataLoader
from transformers import PreTrainedTokenizer
from config import DataConfig


def load_squad_v2(cfg: DataConfig = None) -> tuple[Dataset, Dataset]:
    cfg = cfg or DataConfig()
    ds = load_dataset(cfg.dataset_name)
    train_ds = ds["train"].select(range(min(cfg.train_n, len(ds["train"]))))
    val_ds = ds["validation"].select(range(min(cfg.val_n, len(ds["validation"]))))
    return train_ds, val_ds


def tokenize_qa(dataset: Dataset, tokenizer: PreTrainedTokenizer, max_len: int = 512) -> Dataset:
    def preprocess(examples):
        questions = [q.strip() for q in examples["question"]]
        contexts = examples["context"]
        answers = examples["answers"]

        inputs = tokenizer(
            questions,
            contexts,
            max_length=max_len,
            truncation="only_second",
            padding="max_length",
            return_tensors=None,
        )

        start_positions = []
        end_positions = []
        for i, ans in enumerate(answers):
            if len(ans["answer_start"]) == 0:
                start_positions.append(0)
                end_positions.append(0)
            else:
                start_char = ans["answer_start"][0]
                end_char = start_char + len(ans["text"][0])

                token_start = inputs.char_to_token(i, start_char, sequence_index=1)
                token_end = inputs.char_to_token(i, end_char - 1, sequence_index=1)

                if token_start is None:
                    token_start = 0
                if token_end is None:
                    token_end = 0

                start_positions.append(token_start)
                end_positions.append(token_end)

        inputs["start_positions"] = start_positions
        inputs["end_positions"] = end_positions
        return inputs

    return dataset.map(preprocess, batched=True, remove_columns=dataset.column_names)


def make_dataloader(dataset: Dataset, batch_size: int, shuffle: bool = False) -> DataLoader:
    dataset.set_format("torch")
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
