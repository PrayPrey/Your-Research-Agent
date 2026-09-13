"""H-M2 Perturbation Engine - Paraphrase and masking generators"""
import random
import re
from typing import List
import nltk
from nltk.corpus import wordnet


class PerturbationEngine:
    """Generate paraphrases (WordNet/embedding) and masking perturbations."""

    def __init__(self, m_cfg):
        self.m_cfg = m_cfg
        random.seed(m_cfg.random_state)
        # Ensure NLTK data available
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            nltk.download('omw-1.4', quiet=True)

    def _get_synonyms(self, word: str) -> List[str]:
        """Get WordNet synonyms for a word."""
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word and '_' not in lemma.name():
                    synonyms.add(lemma.name())
        return list(synonyms)

    def wordnet_paraphrases(self, text: str) -> List[str]:
        """Generate WordNet synonym-substituted variants using pure NLTK."""
        if not text or len(text.split()) < 3:
            return []

        words = text.split()
        results = []

        # Find words with synonyms
        replaceable = []
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) > 3:
                syns = self._get_synonyms(clean_word)
                if syns:
                    replaceable.append((i, word, syns))

        if not replaceable:
            return []

        # Generate paraphrases
        n_swap = max(1, int(len(words) * self.m_cfg.wordnet_pct_swap))
        for _ in range(self.m_cfg.wordnet_n):
            new_words = words[:]
            to_replace = random.sample(replaceable, min(n_swap, len(replaceable)))
            for idx, orig_word, syns in to_replace:
                new_word = random.choice(syns)
                # Preserve capitalization
                if orig_word[0].isupper():
                    new_word = new_word.capitalize()
                # Preserve punctuation
                if orig_word[-1] in '.,?!;:':
                    new_word += orig_word[-1]
                new_words[idx] = new_word
            para = ' '.join(new_words)
            if para != text and para not in results:
                results.append(para)

        return results[:self.m_cfg.wordnet_n]

    def embedding_paraphrases(self, text: str, encoder=None) -> List[str]:
        """Generate embedding-neighbor paraphrases using WordNet with cosine filter."""
        if not text or len(text.split()) < 3:
            return []

        # Use same wordnet method but with different random seeds
        old_state = random.getstate()
        candidates = []
        for i in range(self.m_cfg.embedding_n * 3):
            random.seed(self.m_cfg.random_state + i + 1000)
            paras = self.wordnet_paraphrases(text)
            candidates.extend(paras)

        random.setstate(old_state)
        candidates = list(set(candidates))

        if not candidates or encoder is None:
            return candidates[:self.m_cfg.embedding_n]

        # Filter by cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        orig_emb = encoder.encode([text])
        cand_emb = encoder.encode(candidates)
        sims = cosine_similarity(orig_emb, cand_emb)[0]
        return [c for c, s in zip(candidates, sims) if s >= self.m_cfg.embedding_min_cosine][:self.m_cfg.embedding_n]

    def mask_keywords(self, text: str, ratio: float, tfidf_words: set = None) -> str:
        """Mask TF-IDF important keywords at given ratio."""
        words = text.split()
        if not words:
            return text
        n_mask = max(1, int(len(words) * ratio))
        if tfidf_words:
            keyword_indices = [i for i, w in enumerate(words) if w.lower() in tfidf_words]
            if keyword_indices:
                to_mask = keyword_indices[:n_mask]
            else:
                to_mask = random.sample(range(len(words)), min(n_mask, len(words)))
        else:
            # Heuristic: longer words more likely to be keywords
            sorted_idx = sorted(range(len(words)), key=lambda i: len(words[i]), reverse=True)
            to_mask = sorted_idx[:n_mask]
        result = words[:]
        for i in to_mask:
            result[i] = "[MASK]"
        return " ".join(result)

    def mask_random(self, text: str, ratio: float) -> str:
        """Control baseline: mask random words at given ratio."""
        words = text.split()
        if not words:
            return text
        n_mask = max(1, int(len(words) * ratio))
        to_mask = random.sample(range(len(words)), min(n_mask, len(words)))
        result = words[:]
        for i in to_mask:
            result[i] = "[MASK]"
        return " ".join(result)
