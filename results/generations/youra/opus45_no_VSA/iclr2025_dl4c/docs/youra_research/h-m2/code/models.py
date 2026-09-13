"""Model loading for H-M2 DiD experiment."""
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase
from peft import PeftModel

from config import Config


def load_eval_model(checkpoint_dir, cfg: Config) -> tuple[PeftModel, PreTrainedTokenizerBase]:
    """Load base model + PEFT adapter for evaluation."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, cache_dir=cfg.cache_dir)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        cfg.model_id,
        cache_dir=cfg.cache_dir,
        torch_dtype=torch.float16,
    )
    model = PeftModel.from_pretrained(base_model, checkpoint_dir)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model, tokenizer


def load_rl_ce_models(cfg: Config) -> dict[str, tuple[PeftModel, PreTrainedTokenizerBase]]:
    """Load both RL and CE models."""
    return {
        "RL": load_eval_model(cfg.rl_checkpoint, cfg),
        "CE": load_eval_model(cfg.ce_checkpoint, cfg),
    }
