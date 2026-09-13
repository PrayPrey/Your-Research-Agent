import sys, os, pickle, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import Config
from ngram_extractor import NgramExtractor
from corpus_indexer import CorpusIndexer
from datasketch import MinHashLSH

def make_indexer(tmpdir):
    cfg = Config()
    cfg.indices_dir = str(tmpdir)
    cfg.pile_index_path = os.path.join(str(tmpdir), "pile_index.pkl")
    cfg.c4_index_path = os.path.join(str(tmpdir), "c4_index.pkl")
    cfg.redpajama_index_path = os.path.join(str(tmpdir), "redpajama_index.pkl")
    ext = NgramExtractor(cfg)
    return CorpusIndexer(cfg, ext), cfg

def test_save_load_roundtrip(tmp_path):
    indexer, cfg = make_indexer(tmp_path)
    lsh = MinHashLSH(threshold=0.5, num_perm=128)
    path = str(tmp_path / "test.pkl")
    indexer.save(lsh, path)
    loaded = indexer.load(path)
    assert isinstance(loaded, MinHashLSH)

def test_checkpoint_creates_file(tmp_path):
    indexer, cfg = make_indexer(tmp_path)
    lsh = MinHashLSH(threshold=0.5, num_perm=128)
    indexer.checkpoint(lsh, "c4", 500000)
    assert (tmp_path / "c4_ckpt_500000.pkl").exists()

def test_load_or_build_uses_existing(tmp_path):
    indexer, cfg = make_indexer(tmp_path)
    lsh = MinHashLSH(threshold=0.5, num_perm=128)
    indexer.save(lsh, cfg.c4_index_path)
    loaded = indexer.load_or_build("c4")
    assert isinstance(loaded, MinHashLSH)
