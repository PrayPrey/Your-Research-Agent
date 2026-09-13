import importlib.util
from pathlib import Path

h_m1_code = Path(__file__).parent.parent.parent / "h-m1" / "code"

spec = importlib.util.spec_from_file_location("h_m1_data", h_m1_code / "data.py")
h_m1_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_m1_data)

load_corpus = h_m1_data.load_corpus
load_mmlu = h_m1_data.load_mmlu
verbalize = h_m1_data.verbalize
filter_by_strategy = h_m1_data.filter_by_strategy

spec2 = importlib.util.spec_from_file_location("h_m1_train", h_m1_code / "train.py")
h_m1_train = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(h_m1_train)

TextDataset = h_m1_train.TextDataset

__all__ = ["load_corpus", "load_mmlu", "verbalize", "filter_by_strategy", "TextDataset"]
