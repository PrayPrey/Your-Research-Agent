import random
import re


def load_paraphraser():
    return None, None


def rule_based_paraphrase(text: str, seed: int = 42, variation: int = 0) -> str:
    random.seed(seed + variation)

    synonyms_sets = [
        {"which": ["what"], "of the following": ["among these", "from the options", "listed below"]},
        {"is": ["represents", "refers to", "indicates"], "are": ["represent", "indicate"]},
        {"the": ["a", "this"], "best": ["most accurate", "correct", "appropriate"]},
        {"following": ["listed", "given", "shown"], "most": ["primarily", "mainly"]},
        {"determine": ["find", "identify"], "calculate": ["compute", "find"]},
        {"what": ["which"], "how": ["in what way"]},
    ]

    transforms = [
        lambda t: t,
        lambda t: " ".join(t.split()[::-1][:len(t.split())//2]) + " " + " ".join(t.split()[len(t.split())//2:]),
        lambda t: re.sub(r'\b(is|are)\b', lambda m: 'was' if m.group() == 'is' else 'were', t) if random.random() < 0.3 else t,
    ]

    synonym_set = synonyms_sets[variation % len(synonyms_sets)]

    words = text.split()
    result = []
    for word in words:
        lower = word.lower().strip(".,?!")
        if lower in synonym_set and random.random() < 0.4:
            replacement = random.choice(synonym_set[lower])
            if word[0].isupper():
                replacement = replacement.capitalize()
            punct = ""
            for c in word[::-1]:
                if c in ".,?!":
                    punct = c + punct
                else:
                    break
            result.append(replacement + punct)
        else:
            result.append(word)

    paraphrased = " ".join(result)

    if variation > 0 and random.random() < 0.3:
        paraphrased = transforms[variation % len(transforms)](paraphrased)

    return paraphrased


def generate_paraphrases(text: str, para_model, para_tokenizer, k: int = 5, seed: int = 42) -> list:
    paraphrases = []
    seen = {text.lower().strip()}

    for i in range(k * 3):
        para = rule_based_paraphrase(text, seed=seed + i, variation=i)
        normalized = para.lower().strip()
        if normalized not in seen and para != text:
            paraphrases.append(para)
            seen.add(normalized)
        if len(paraphrases) >= k:
            break

    while len(paraphrases) < k:
        base_para = rule_based_paraphrase(text, seed=seed + len(paraphrases) + 100, variation=len(paraphrases))
        if base_para.lower().strip() not in seen:
            paraphrases.append(base_para)
            seen.add(base_para.lower().strip())
        else:
            paraphrases.append(text + " ")

    return paraphrases[:k]


def build_paraphrase_bank(test_set, contaminated_ids: set, para_model, para_tokenizer,
                          k: int = 5, seed: int = 42) -> dict:
    from data import format_mmlu_prompt
    bank = {}

    print(f"Building paraphrase bank for {len(contaminated_ids)} items, K={k}...")
    for i, idx in enumerate(sorted(contaminated_ids)):
        item = test_set[idx]
        question_text = item["question"]
        paras = generate_paraphrases(question_text, para_model, para_tokenizer, k=k, seed=seed + idx)

        formatted_paras = []
        for para in paras:
            choices = item["choices"]
            formatted = f"Question: {para}\n\n"
            for j, choice in enumerate(choices):
                letter = chr(ord('A') + j)
                formatted += f"{letter}. {choice}\n"
            formatted += "\nAnswer:"
            formatted_paras.append(formatted)

        bank[idx] = formatted_paras
        if (i + 1) % 200 == 0:
            print(f"  Processed {i+1}/{len(contaminated_ids)} items")

    return bank
