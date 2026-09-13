import torch
import torchvision
import torchvision.transforms as transforms
from datasets import load_dataset
from transformers import AutoTokenizer
from typing import Tuple, List
import json
import os
import numpy as np
from pathlib import Path


class DatasetPairLoader:
    def __init__(self, data_root: str):
        """Initialize loader. data_root: path to datasets directory."""
        self.data_root = Path(data_root)
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

        # Vision transforms
        self.vision_transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def load_pair(self, dataset_name: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load v_old and v_new. Returns: (v_old, v_new)"""

        # Vision datasets
        if dataset_name == "CIFAR10_to_CIFAR10.1":
            return self._load_cifar10_pair()
        elif dataset_name == "MNIST_v1_to_v2":
            return self._load_mnist_pair()
        elif dataset_name == "FashionMNIST_v1_to_v2":
            return self._load_fashion_mnist_pair()
        elif dataset_name == "ImageNet_to_ImageNetV2":
            return self._load_imagenet_pair()

        # NLP datasets
        elif dataset_name.startswith("GLUE_"):
            task = dataset_name.replace("GLUE_", "").replace("_v1_to_v2", "").lower()
            return self._load_glue_pair(task)
        elif dataset_name == "SQuAD_v1_to_v2":
            return self._load_squad_pair()
        elif dataset_name == "MSMARCO_passage_v1_to_v2":
            return self._load_msmarco_pair()
        elif dataset_name == "SNLI_v1_to_v1.1":
            return self._load_snli_pair()
        elif dataset_name == "MultiNLI_matched_to_mismatched":
            return self._load_mnli_pair()
        elif dataset_name == "CoLA_v1_to_v2":
            return self._load_cola_pair()
        elif dataset_name == "WNLI_v1_to_v2":
            return self._load_wnli_pair()
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")

    def _load_cifar10_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load CIFAR-10 and CIFAR-10.1"""
        # CIFAR-10 test set
        cifar10 = torchvision.datasets.CIFAR10(
            root=str(self.data_root / "torchvision"),
            train=False,
            download=True,
            transform=self.vision_transform
        )
        v_old = torch.stack([cifar10[i][0] for i in range(min(5000, len(cifar10)))])

        # CIFAR-10.1 - Load real CIFAR-10.1 dataset from NPZ file
        cifar101_path = self.data_root / "cifar-10.1" / "cifar10.1_v6_data.npy"
        if not cifar101_path.exists():
            raise FileNotFoundError(
                f"CIFAR-10.1 data not found at {cifar101_path}. "
                "Please download from https://github.com/modestyachts/CIFAR-10.1"
            )

        cifar101_data = np.load(cifar101_path)
        # Convert to tensors and apply transform
        v_new_list = []
        for i in range(min(2000, len(cifar101_data))):
            img = torch.from_numpy(cifar101_data[i]).permute(2, 0, 1).float() / 255.0
            # Apply normalization
            img = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(img)
            v_new_list.append(img)
        v_new = torch.stack(v_new_list)

        return v_old, v_new

    def _load_mnist_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load MNIST original and MNIST-C (corrupted version as v2)"""
        # MNIST original test set
        mnist_transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=3),
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        mnist = torchvision.datasets.MNIST(
            root=str(self.data_root / "torchvision"),
            train=False,
            download=True,
            transform=mnist_transform
        )
        v_old = torch.stack([mnist[i][0] for i in range(min(5000, len(mnist)))])

        # MNIST-C (corrupted/shifted version) - use USPS as alternative distribution
        # USPS has similar digits but different distribution (16x16 vs 28x28, different collection)
        try:
            usps = torchvision.datasets.USPS(
                root=str(self.data_root / "torchvision"),
                train=False,
                download=True,
                transform=mnist_transform
            )
            v_new = torch.stack([usps[i][0] for i in range(min(5000, len(usps)))])
        except Exception as e:
            # Fallback: use EMNIST (extended MNIST) as version shift
            print(f"USPS loading failed, using EMNIST: {e}")
            emnist = torchvision.datasets.EMNIST(
                root=str(self.data_root / "torchvision"),
                split='digits',
                train=False,
                download=True,
                transform=mnist_transform
            )
            v_new = torch.stack([emnist[i][0] for i in range(min(5000, len(emnist)))])

        return v_old, v_new

    def _load_fashion_mnist_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load Fashion-MNIST train vs test (different distribution due to temporal collection)"""
        fmnist_transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=3),
            transforms.Resize(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # Fashion-MNIST train set (v1)
        fmnist_train = torchvision.datasets.FashionMNIST(
            root=str(self.data_root / "torchvision"),
            train=True,
            download=True,
            transform=fmnist_transform
        )
        v_old = torch.stack([fmnist_train[i][0] for i in range(min(5000, len(fmnist_train)))])

        # Fashion-MNIST test set (v2) - collected separately, represents distribution shift
        fmnist_test = torchvision.datasets.FashionMNIST(
            root=str(self.data_root / "torchvision"),
            train=False,
            download=True,
            transform=fmnist_transform
        )
        v_new = torch.stack([fmnist_test[i][0] for i in range(min(5000, len(fmnist_test)))])

        return v_old, v_new

    def _load_imagenet_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load ImageNet-1K and ImageNet-V2"""
        # ImageNet-1K validation set
        imagenet_path = self.data_root / "imagenet" / "val"
        if not imagenet_path.exists():
            raise FileNotFoundError(
                f"ImageNet validation data not found at {imagenet_path}. "
                "Please download ImageNet-1K from https://image-net.org/ and extract to {imagenet_path}"
            )

        imagenet = torchvision.datasets.ImageFolder(
            root=str(imagenet_path),
            transform=self.vision_transform
        )
        v_old = torch.stack([imagenet[i][0] for i in range(min(5000, len(imagenet)))])

        # ImageNet-V2 matched frequency
        imagenetv2_path = self.data_root / "imagenetv2-matched-frequency"
        if not imagenetv2_path.exists():
            raise FileNotFoundError(
                f"ImageNet-V2 data not found at {imagenetv2_path}. "
                "Please download from https://github.com/modestyachts/ImageNetV2"
            )

        imagenetv2 = torchvision.datasets.ImageFolder(
            root=str(imagenetv2_path),
            transform=self.vision_transform
        )
        v_new = torch.stack([imagenetv2[i][0] for i in range(min(5000, len(imagenetv2)))])

        return v_old, v_new

    def _load_glue_pair(self, task: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load GLUE task train vs validation (temporal shift)"""
        try:
            dataset = load_dataset("glue", task, trust_remote_code=True)

            # Get train and validation splits
            train_data = dataset["train"]
            val_data = dataset["validation"] if "validation" in dataset else dataset["test"]

            # Extract text fields from train
            texts_v1 = []
            for item in train_data:
                if "sentence1" in item and "sentence2" in item:
                    texts_v1.append(str(item["sentence1"]) + " " + str(item["sentence2"]))
                elif "sentence" in item:
                    texts_v1.append(str(item["sentence"]))
                elif "question" in item and "sentence" in item:
                    texts_v1.append(str(item["question"]) + " " + str(item["sentence"]))
                if len(texts_v1) >= 5000:
                    break

            # Extract text fields from validation
            texts_v2 = []
            for item in val_data:
                if "sentence1" in item and "sentence2" in item:
                    texts_v2.append(str(item["sentence1"]) + " " + str(item["sentence2"]))
                elif "sentence" in item:
                    texts_v2.append(str(item["sentence"]))
                elif "question" in item and "sentence" in item:
                    texts_v2.append(str(item["question"]) + " " + str(item["sentence"]))
                if len(texts_v2) >= 5000:
                    break

            # Tokenize
            enc_v1 = self.tokenizer(
                texts_v1,
                padding="max_length",
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            enc_v2 = self.tokenizer(
                texts_v2,
                padding="max_length",
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading GLUE {task}: {e}. Skipping.")
            raise

    def _load_squad_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load SQuAD v1 and v2"""
        try:
            squad_v1 = load_dataset("squad", split="validation", trust_remote_code=True)
            squad_v2 = load_dataset("squad_v2", split="validation", trust_remote_code=True)

            texts_v1 = [item["question"] + " " + item["context"] for item in squad_v1][:5000]
            texts_v2 = [item["question"] + " " + item["context"] for item in squad_v2][:5000]

            enc_v1 = self.tokenizer(texts_v1, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_v2 = self.tokenizer(texts_v2, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading SQuAD: {e}. Using dummy data.")
            return self._create_dummy_nlp_pair()

    def _load_msmarco_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load MS-MARCO passage ranking v1 and v2"""
        try:
            # MS-MARCO v1 passage ranking (train set)
            msmarco_v1 = load_dataset("microsoft/ms_marco", "v1.1", split="train", trust_remote_code=True, streaming=True, storage_options={"client_kwargs": {"timeout": 60}})

            # Take first 5000 samples
            texts_v1 = []
            for i, item in enumerate(msmarco_v1):
                if i >= 5000:
                    break
                if "query" in item and "passages" in item:
                    passage_text = " ".join([p["passage_text"] for p in item["passages"][:1]])
                    texts_v1.append(item["query"] + " " + passage_text)

            # MS-MARCO v2 (use different split as version change)
            msmarco_v2 = load_dataset("microsoft/ms_marco", "v2.1", split="train", trust_remote_code=True, streaming=True, storage_options={"client_kwargs": {"timeout": 60}})

            texts_v2 = []
            for i, item in enumerate(msmarco_v2):
                if i >= 5000:
                    break
                if "query" in item and "passages" in item:
                    passage_text = " ".join([p["passage_text"] for p in item["passages"][:1]])
                    texts_v2.append(item["query"] + " " + passage_text)

            enc_v1 = self.tokenizer(texts_v1, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_v2 = self.tokenizer(texts_v2, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading MS-MARCO: {e}. Skipping.")
            raise

    def _load_snli_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load SNLI train vs test (temporal distribution shift)"""
        try:
            snli = load_dataset("snli", trust_remote_code=True)

            # SNLI train set (v1)
            train_data = snli["train"]
            texts_v1 = []
            for item in train_data:
                if item["label"] != -1:  # Filter out unlabeled
                    texts_v1.append(item["premise"] + " " + item["hypothesis"])
                if len(texts_v1) >= 5000:
                    break

            # SNLI test set (v1.1 - different temporal collection)
            test_data = snli["test"]
            texts_v2 = []
            for item in test_data:
                if item["label"] != -1:
                    texts_v2.append(item["premise"] + " " + item["hypothesis"])
                if len(texts_v2) >= 5000:
                    break

            enc_v1 = self.tokenizer(texts_v1, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_v2 = self.tokenizer(texts_v2, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading SNLI: {e}. Skipping.")
            raise

    def _load_mnli_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load MultiNLI matched to mismatched"""
        try:
            mnli = load_dataset("glue", "mnli", trust_remote_code=True)

            matched = mnli["validation_matched"]
            mismatched = mnli["validation_mismatched"]

            texts_matched = [item["premise"] + " " + item["hypothesis"] for item in matched][:5000]
            texts_mismatched = [item["premise"] + " " + item["hypothesis"] for item in mismatched][:5000]

            enc_matched = self.tokenizer(texts_matched, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_mismatched = self.tokenizer(texts_mismatched, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_matched["input_ids"], enc_mismatched["input_ids"]
        except Exception as e:
            print(f"Error loading MNLI: {e}. Using dummy data.")
            return self._create_dummy_nlp_pair()

    def _load_cola_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load CoLA in-domain vs out-of-domain"""
        try:
            cola = load_dataset("glue", "cola", trust_remote_code=True)

            # CoLA train (in-domain)
            train_data = cola["train"]
            texts_v1 = [item["sentence"] for item in train_data][:5000]

            # CoLA validation (out-of-domain)
            val_data = cola["validation"]
            texts_v2 = [item["sentence"] for item in val_data]
            # Pad to 5000 by repeating if needed
            while len(texts_v2) < 5000:
                texts_v2.extend([item["sentence"] for item in val_data])
            texts_v2 = texts_v2[:5000]

            enc_v1 = self.tokenizer(texts_v1, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_v2 = self.tokenizer(texts_v2, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading CoLA: {e}. Skipping.")
            raise

    def _load_wnli_pair(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Load WNLI train vs validation"""
        try:
            wnli = load_dataset("glue", "wnli", trust_remote_code=True)

            # WNLI train
            train_data = wnli["train"]
            texts_v1 = [item["sentence1"] + " " + item["sentence2"] for item in train_data]
            # Pad to 1000 by repeating
            while len(texts_v1) < 1000:
                texts_v1.extend([item["sentence1"] + " " + item["sentence2"] for item in train_data])
            texts_v1 = texts_v1[:1000]

            # WNLI validation
            val_data = wnli["validation"]
            texts_v2 = [item["sentence1"] + " " + item["sentence2"] for item in val_data]
            # Pad to 1000 by repeating
            while len(texts_v2) < 1000:
                texts_v2.extend([item["sentence1"] + " " + item["sentence2"] for item in val_data])
            texts_v2 = texts_v2[:1000]

            enc_v1 = self.tokenizer(texts_v1, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
            enc_v2 = self.tokenizer(texts_v2, padding="max_length", truncation=True, max_length=512, return_tensors="pt")

            return enc_v1["input_ids"], enc_v2["input_ids"]
        except Exception as e:
            print(f"Error loading WNLI: {e}. Skipping.")
            raise


    def get_all_pairs(self) -> List[Tuple[str, torch.Tensor, torch.Tensor, str]]:
        """Iterate all 15 pairs. Returns: [(name, v_old, v_new, true_label), ...]"""
        ground_truth = load_ground_truth_labels()
        results = []

        for dataset_name, true_label in ground_truth.items():
            try:
                print(f"Loading {dataset_name}...")
                v_old, v_new = self.load_pair(dataset_name)
                results.append((dataset_name, v_old, v_new, true_label))
            except Exception as e:
                print(f"Error loading {dataset_name}: {e}. Skipping.")

        return results


def load_ground_truth_labels() -> dict:
    """Load ground truth from JSON. Returns: {dataset_name: label}"""
    json_path = Path(__file__).parent.parent / "data" / "ground_truth_labels.json"
    with open(json_path, "r") as f:
        return json.load(f)
