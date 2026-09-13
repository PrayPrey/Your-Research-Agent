"""Dual-encoder embedder: CodeBERT mean-pool + all-MiniLM-L6-v2."""
import logging
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logger = logging.getLogger(__name__)

CODEBERT_MODEL_ID = "microsoft/codebert-base"
MINILM_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"


def encode_codebert(
    texts: list,
    tokenizer,
    model,
    batch_size: int = 32,
    device: str = "cuda",
    max_length: int = 512,
) -> torch.Tensor:
    """Returns L2-normalized (N, 768) float32 tensor. Mean-pools last hidden states."""
    model.eval()
    model.to(device)
    all_embs = []
    effective_batch = batch_size

    for i in tqdm(range(0, len(texts), effective_batch), desc="CodeBERT"):
        chunk = texts[i:i + effective_batch]
        try:
            enc = tokenizer(
                chunk,
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            ).to(device)
            with torch.no_grad():
                out = model(**enc)
            mask = enc["attention_mask"].unsqueeze(-1).float()  # [B, L, 1]
            pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            all_embs.append(F.normalize(pooled, dim=-1).cpu())
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                effective_batch = max(1, effective_batch // 4)
                torch.cuda.empty_cache()
                logger.warning(f"OOM, reducing batch to {effective_batch}")
                # Re-encode this chunk with smaller batch
                for j in range(0, len(chunk), effective_batch):
                    sub = chunk[j:j + effective_batch]
                    enc = tokenizer(
                        sub,
                        padding=True,
                        truncation=True,
                        max_length=max_length,
                        return_tensors="pt",
                    ).to(device)
                    with torch.no_grad():
                        out = model(**enc)
                    mask = enc["attention_mask"].unsqueeze(-1).float()
                    pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                    all_embs.append(F.normalize(pooled, dim=-1).cpu())
            else:
                raise

    return torch.cat(all_embs, dim=0)


def encode_minilm(
    texts: list,
    batch_size: int = 32,
) -> torch.Tensor:
    """Returns L2-normalized (N, 384) float32 tensor via SentenceTransformer."""
    model = SentenceTransformer(MINILM_MODEL_ID)
    embs = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
        convert_to_tensor=True,
    )
    return embs.cpu().float()


def encode_all_corpora(
    corpora: dict,
    batch_size: int = 32,
    device: str = "cuda",
) -> dict:
    """Returns {corpus_name: {"codebert": Tensor(N,768), "minilm": Tensor(N,384)}}."""
    tokenizer = AutoTokenizer.from_pretrained(CODEBERT_MODEL_ID)
    cb_model = AutoModel.from_pretrained(CODEBERT_MODEL_ID)
    cb_model.to(device).eval()

    results = {}
    for name, texts in corpora.items():
        N = len(texts)
        logger.info(f"Encoding {N} texts for {name}...")
        cb_emb = encode_codebert(texts, tokenizer, cb_model, batch_size, device)
        logger.info(f"Encoded {N} problems for {name} with codebert")
        ml_emb = encode_minilm(texts, batch_size)
        logger.info(f"Encoded {N} problems for {name} with minilm")
        results[name] = {"codebert": cb_emb, "minilm": ml_emb}

    return results
