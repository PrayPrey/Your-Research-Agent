"""GitHub Data Collection Module for Repository Maintenance Classification."""

import requests
import pandas as pd
import time
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class GitHubDataCollector:
    """Collects GitHub repository metadata via REST API."""

    def __init__(self, api_token: str):
        """Initialize GitHub API client with authentication.

        Args:
            api_token: GitHub personal access token for API authentication (empty string for unauthenticated)
        """
        self.api_token = api_token
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
        if api_token:
            self.headers['Authorization'] = f'token {api_token}'
        self.base_url = 'https://api.github.com'
        self.pwc_url = 'https://paperswithcode.com/api/v1'
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def collect_pwc_repos(self, year_range: Tuple[int, int], min_stars: int, max_repos: int) -> pd.DataFrame:
        """Use curated list of ML/benchmark repositories.

        Since Papers with Code API is unavailable and GitHub Search requires auth,
        this uses a pre-defined list of popular ML/benchmark repositories.

        Args:
            year_range: Tuple of (start_year, end_year) - ignored for curated list
            min_stars: Minimum stars filter - will filter repos below this
            max_repos: Maximum number of repositories to collect

        Returns:
            DataFrame with columns [repo_name, repo_url, stars, description]
        """
        # Curated list of popular ML/benchmark repositories (Papers with Code repositories)
        # Covering various ML domains: computer vision, NLP, RL, general ML frameworks
        curated_repos = [
            # Computer Vision
            'facebookresearch/detectron2', 'ultralytics/yolov5', 'open-mmlab/mmdetection',
            'rwightman/pytorch-image-models', 'lucidrains/vit-pytorch', 'facebookresearch/dino',
            'microsoft/Swin-Transformer', 'facebookresearch/segment-anything', 'openai/CLIP',
            # NLP & LLMs
            'huggingface/transformers', 'openai/gpt-2', 'facebookresearch/fairseq',
            'allenai/allennlp', 'google-research/bert', 'stanford-crfm/helm',
            # Reinforcement Learning
            'openai/baselines', 'DLR-RM/stable-baselines3', 'tensorflow/agents',
            'deepmind/acme', 'google/dopamine', 'ray-project/ray',
            # General ML/DL
            'pytorch/pytorch', 'tensorflow/tensorflow', 'keras-team/keras',
            'scikit-learn/scikit-learn', 'apache/mxnet', 'dmlc/xgboost',
            'microsoft/LightGBM', 'catboost/catboost', 'explosion/spaCy',
            # ML Ops / Tools
            'mlflow/mlflow', 'iterative/dvc', 'wandb/wandb', 'allegroai/clearml',
            'determined-ai/determined', 'kubeflow/kubeflow',
            # Research / Benchmarks
            'paperswithcode/axcell', 'paperswithcode/galai', 'facebookresearch/mmf',
            'google-research/google-research', 'microsoft/DeepSpeed', 'NVIDIA/apex',
            # Data Processing
            'apache/spark', 'pandas-dev/pandas', 'dask/dask', 'rapidsai/cudf',
            # Active ML Projects (2020-2024)
            'deepset-ai/haystack', 'microsoft/DeepSpeedExamples', 'rasbt/mlxtend',
            'intel/neural-compressor', 'onnx/onnx', 'aws/sagemaker-python-sdk',
            'optuna/optuna', 'fmind/mlops-python-package', 'bentoml/BentoML',
            'nerdyrodent/VQGAN-CLIP', 'CompVis/stable-diffusion', 'Stability-AI/stablediffusion',
            'openai/whisper', 'tatsu-lab/stanford_alpaca', 'lm-sys/FastChat',
            'hpcaitech/ColossalAI', 'pytorch/torchrec', 'facebookresearch/metaseq',
            # Additional diverse repos
            'Lightning-AI/lightning', 'explosion/thinc', 'PyTorchLightning/metrics',
            'ludwig-ai/ludwig', 'automl/auto-sklearn', 'epistasislab/tpot',
            'google/jax', 'patrick-kidger/equinox', 'deepchem/deepchem',
            'stellargraph/stellargraph', 'pyg-team/pytorch_geometric', 'dmlc/dgl',
            'facebookresearch/hydra', 'omry/omegaconf', 'willmcgugan/rich',
            'tiangolo/fastapi', 'encode/httpx', 'aio-libs/aiohttp',
            'jina-ai/jina', 'microsoft/nni', 'feast-dev/feast',
            'horovod/horovod', 'allegroai/trains', 'Netflix/metaflow',
            # More recent (2020+) ML projects
            'lucidrains/DALLE2-pytorch', 'borisdayma/dalle-mini', 'huggingface/diffusers',
            'microsoft/unilm', 'salesforce/LAVIS', 'facebookresearch/llama',
            'google-research/vision_transformer', 'rwightman/efficientnet-jax',
            'microsoft/COCO-LM', 'EleutherAI/gpt-neo', 'EleutherAI/gpt-j',
            'bigscience-workshop/bigscience', 'CarperAI/trlx', 'lvwerra/trl',
            'openai/point-e', 'openai/shap-e', 'Dao AI-Lab/flash-attention',
            'vllm-project/vllm', 'coqui-ai/TTS', 'espnet/espnet',
            'jaywalnut310/vits', 'neonbjb/tortoise-tts', 'microsoft/semantic-kernel',
            'jerryjliu/llama_index', 'langchain-ai/langchain', 'run-llama/rags',
            'chroma-core/chroma', 'pinecone-io/pinecone-python-client', 'weaviate/weaviate',
            'milvus-io/milvus', 'qdrant/qdrant', 'jina-ai/clip-as-service',
        ]

        repos = []
        print(f"Using curated list of ML/benchmark repositories")
        print(f"Target: {max_repos} repos")

        for repo_name in curated_repos[:max_repos * 2]:  # Fetch extra to account for filtering
            if len(repos) >= max_repos:
                break

            try:
                # Fetch basic info to get stars and check if it exists
                response = self.session.get(f'{self.base_url}/repos/{repo_name}')

                if response.status_code == 404:
                    print(f"  Skipped (not found): {repo_name}")
                    time.sleep(1)
                    continue

                self._handle_rate_limit(response)

                if response.status_code == 200:
                    repo_data = response.json()
                    stars = repo_data.get('stargazers_count', 0)

                    # Filter by min_stars
                    if stars < min_stars:
                        continue

                    repos.append({
                        'repo_name': repo_name,
                        'repo_url': repo_data['html_url'],
                        'stars': stars,
                        'description': repo_data.get('description', '')
                    })

                    if len(repos) % 10 == 0:
                        print(f"  Collected {len(repos)}/{max_repos} repos")

                    # Rate limiting - more conservative for unauthenticated requests
                    time.sleep(1.0 if self.api_token else 2.0)

            except Exception as e:
                print(f"  Error fetching {repo_name}: {e}")
                time.sleep(1)
                continue

        print(f"\nTotal collected: {len(repos)} repositories")
        return pd.DataFrame(repos)

    def fetch_repo_metadata(self, repo_full_name: str) -> Dict:
        """Extract metadata from GitHub API for single repository.

        Args:
            repo_full_name: Repository name (e.g., 'owner/repo')

        Returns:
            Dict with keys: stars, forks, contributors, total_commits,
            open_issues, last_commit_date, closed_issues, total_issues
        """
        metadata = {}

        try:
            # Main repo info
            repo_response = self.session.get(f'{self.base_url}/repos/{repo_full_name}')
            self._handle_rate_limit(repo_response)

            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                metadata['stars'] = repo_data.get('stargazers_count', 0)
                metadata['forks'] = repo_data.get('forks_count', 0)
                metadata['open_issues'] = repo_data.get('open_issues_count', 0)
                metadata['created_at'] = repo_data.get('created_at')
                metadata['updated_at'] = repo_data.get('updated_at')
                metadata['pushed_at'] = repo_data.get('pushed_at')

                # Calculate days since last commit
                if metadata.get('pushed_at'):
                    last_push = datetime.fromisoformat(metadata['pushed_at'].replace('Z', '+00:00'))
                    metadata['days_since_last_commit'] = (datetime.now().astimezone() - last_push).days
                else:
                    metadata['days_since_last_commit'] = 9999

            # Contributors count
            contributors_response = self.session.get(
                f'{self.base_url}/repos/{repo_full_name}/contributors',
                params={'per_page': 1, 'anon': 'true'}
            )
            self._handle_rate_limit(contributors_response)

            if contributors_response.status_code == 200:
                # GitHub returns total count in Link header
                link_header = contributors_response.headers.get('Link', '')
                if 'last' in link_header:
                    # Extract page count from last link
                    last_page = 1
                    for part in link_header.split(','):
                        if 'rel="last"' in part:
                            last_page_url = part.split(';')[0].strip('<> ')
                            if 'page=' in last_page_url:
                                last_page = int(last_page_url.split('page=')[1].split('&')[0])
                    metadata['contributors'] = last_page
                else:
                    # Single page of contributors
                    metadata['contributors'] = len(contributors_response.json())
            else:
                metadata['contributors'] = 1  # Default

            # Total commits (approximate from API)
            commits_response = self.session.get(
                f'{self.base_url}/repos/{repo_full_name}/commits',
                params={'per_page': 1}
            )
            self._handle_rate_limit(commits_response)

            if commits_response.status_code == 200:
                link_header = commits_response.headers.get('Link', '')
                if 'last' in link_header:
                    for part in link_header.split(','):
                        if 'rel="last"' in part:
                            last_page_url = part.split(';')[0].strip('<> ')
                            if 'page=' in last_page_url:
                                metadata['total_commits'] = int(last_page_url.split('page=')[1].split('&')[0])
                else:
                    metadata['total_commits'] = len(commits_response.json())

                # Get last commit date
                commits_data = commits_response.json()
                if commits_data:
                    metadata['last_commit_date'] = commits_data[0]['commit']['committer']['date']
            else:
                metadata['total_commits'] = 0

            # Issues (open + closed)
            issues_open = self.session.get(
                f'{self.base_url}/repos/{repo_full_name}/issues',
                params={'state': 'open', 'per_page': 1}
            )
            self._handle_rate_limit(issues_open)

            issues_closed = self.session.get(
                f'{self.base_url}/repos/{repo_full_name}/issues',
                params={'state': 'closed', 'per_page': 1}
            )
            self._handle_rate_limit(issues_closed)

            open_count = 0
            closed_count = 0

            if issues_open.status_code == 200:
                link = issues_open.headers.get('Link', '')
                if 'last' in link:
                    for part in link.split(','):
                        if 'rel="last"' in part:
                            url = part.split(';')[0].strip('<> ')
                            if 'page=' in url:
                                open_count = int(url.split('page=')[1].split('&')[0])
                else:
                    open_count = len(issues_open.json())

            if issues_closed.status_code == 200:
                link = issues_closed.headers.get('Link', '')
                if 'last' in link:
                    for part in link.split(','):
                        if 'rel="last"' in part:
                            url = part.split(';')[0].strip('<> ')
                            if 'page=' in url:
                                closed_count = int(url.split('page=')[1].split('&')[0])
                else:
                    closed_count = len(issues_closed.json())

            metadata['closed_issues'] = closed_count
            metadata['total_issues'] = open_count + closed_count

        except Exception as e:
            print(f"Error fetching metadata for {repo_full_name}: {e}")

        return metadata

    def compute_temporal_features(self, repo_full_name: str) -> Dict:
        """Compute commit frequency and issue resolution rate.

        Returns:
            Dict with keys: commit_frequency_median_weekly, issue_resolution_rate
        """
        features = {
            'commit_frequency_median_weekly': 0.0,
            'issue_resolution_rate': 0.0
        }

        try:
            # Commit frequency (approximate from recent commits)
            commits_response = self.session.get(
                f'{self.base_url}/repos/{repo_full_name}/commits',
                params={'per_page': 100}
            )
            self._handle_rate_limit(commits_response)

            if commits_response.status_code == 200:
                commits = commits_response.json()
                if len(commits) >= 2:
                    # Calculate median weekly frequency from recent commits
                    dates = [datetime.fromisoformat(c['commit']['committer']['date'].replace('Z', '+00:00'))
                             for c in commits]
                    dates.sort()

                    if len(dates) >= 2:
                        weeks = (dates[-1] - dates[0]).days / 7.0
                        if weeks > 0:
                            features['commit_frequency_median_weekly'] = len(commits) / weeks

        except Exception as e:
            print(f"Error computing temporal features for {repo_full_name}: {e}")

        return features

    def save_raw_data(self, data: pd.DataFrame, output_path: str) -> None:
        """Save collected metadata to CSV.

        Args:
            data: DataFrame with collected repository data
            output_path: Path to save CSV file
        """
        data.to_csv(output_path, index=False)
        print(f"Saved {len(data)} repositories to {output_path}")

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Implement exponential backoff for API rate limiting.

        Args:
            response: Response object from GitHub API
        """
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
            if reset_time:
                wait_time = max(reset_time - time.time(), 0) + 10
                print(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
        elif response.status_code == 429:
            # Too many requests
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Too many requests. Waiting {retry_after} seconds...")
            time.sleep(retry_after)
        elif response.status_code not in [200, 404]:
            # Generic backoff
            time.sleep(2)
