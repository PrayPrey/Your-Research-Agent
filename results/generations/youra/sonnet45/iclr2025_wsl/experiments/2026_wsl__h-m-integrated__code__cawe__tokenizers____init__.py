"""Architecture-specific tokenizers for weight space"""
from .tokenizers_simple import CNNTokenizer, TransformerTokenizer, MLPTokenizer

__all__ = ['CNNTokenizer', 'TransformerTokenizer', 'MLPTokenizer']
