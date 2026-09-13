"""Model inference + logprob extraction for MCQ benchmarks."""

import os
import gc
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm

from config import TORCH_DTYPE, DEVICE_MAP, CACHE_DIR
from data_loader import MCQDataLoader


class ModelRunner:
    """Load and run inference on AutoModelForCausalLM, extract MCQ log-probs."""

    def __init__(self, model_id: str, torch_dtype: str = "float16", device_map: str = "auto"):
        self.model_id = model_id
        self.torch_dtype = getattr(torch, torch_dtype)
        self.device_map = device_map
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        """Load model and tokenizer into GPU memory."""
        print(f"Loading model: {self.model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, padding_side="left")
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            device_map=self.device_map,
        )
        self.model.eval()
        print(f"  -> Loaded {self.model_id}")

    def extract_logprobs(
        self,
        dataset: list[dict],
        cache_path: str,
        batch_size: int = 1,
        dataset_cfg: dict = None,
    ) -> np.ndarray:
        """Extract log_softmax over 4 option tokens at last position.

        Returns:
            logprobs: (n, 4) log_softmax over [A, B, C, D] option tokens
        """
        if os.path.exists(cache_path):
            print(f"  -> Loading from cache: {cache_path}")
            return np.load(cache_path)

        assert self.model is not None, "Call load() before extract_logprobs()"

        # Get option token IDs for [" A", " B", " C", " D"]
        option_token_ids = []
        for label in [" A", " B", " C", " D"]:
            ids = self.tokenizer.encode(label, add_special_tokens=False)
            option_token_ids.append(ids[-1])

        # Determine dataset name for formatting
        ds_name = dataset_cfg["name"] if dataset_cfg else "mmlu"
        # We need the original dataset config to format prompts
        # Use the loader's format_prompt method via a temporary loader
        if dataset_cfg:
            loader = MCQDataLoader(dataset_cfg)
        else:
            loader = MCQDataLoader({"name": "mmlu", "hf_id": "cais/mmlu", "config": "all", "split": "test"})

        results = []
        for item in tqdm(dataset, desc=f"Extracting {self.model_id}"):
            prompt = loader.format_prompt(item)
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            input_ids = inputs["input_ids"].to(self.model.device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids)

            # outputs.logits: [1, seq_len, vocab_size]
            last_logits = outputs.logits[0, -1, option_token_ids]  # [4]
            log_probs = F.log_softmax(last_logits.float(), dim=0)   # [4]
            results.append(log_probs.cpu().numpy())

        arr = np.stack(results)  # [n, 4]
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        np.save(cache_path, arr)
        print(f"  -> Saved logprobs ({arr.shape}) to {cache_path}")
        return arr

    def unload(self) -> None:
        """Delete model from GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("  -> Model unloaded")


def run_pair_extraction(
    pair_cfg: dict,
    datasets: dict[str, list[dict]],
    cache_dir: str,
    dataset_cfgs: list[dict] = None,
) -> dict[str, dict]:
    """Run logprob extraction for one base+aligned model pair across all benchmarks.

    Returns:
        {"mmlu": {"base": ndarray (n,4), "aligned": ndarray (n,4)}, ...}
    """
    from config import DATASETS
    if dataset_cfgs is None:
        dataset_cfgs = DATASETS

    ds_cfg_map = {cfg["name"]: cfg for cfg in dataset_cfgs}
    pair_id = pair_cfg["pair_id"]
    result = {}

    for model_role, model_id in [("base", pair_cfg["base"]), ("aligned", pair_cfg["aligned"])]:
        runner = ModelRunner(model_id, torch_dtype=TORCH_DTYPE, device_map=DEVICE_MAP)
        runner.load()

        for ds_name, ds_items in datasets.items():
            cache_path = os.path.join(cache_dir, f"{pair_id}_{model_role}_{ds_name}.npy")
            ds_cfg = ds_cfg_map.get(ds_name)
            logprobs = runner.extract_logprobs(ds_items, cache_path, dataset_cfg=ds_cfg)

            if ds_name not in result:
                result[ds_name] = {}
            result[ds_name][model_role] = logprobs

        runner.unload()

    return result
