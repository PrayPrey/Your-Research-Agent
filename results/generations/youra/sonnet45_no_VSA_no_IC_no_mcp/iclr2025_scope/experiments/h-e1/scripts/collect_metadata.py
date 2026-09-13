#!/usr/bin/env python3
"""
H-E1 Metadata Collection Pipeline
Collect papers, READMEs, and code from ArXiv/GitHub/HuggingFace for 20 benchmarks.
"""
import os
import sys
import time
import json
import yaml
import logging
import requests
import arxiv
from pathlib import Path
from typing import Dict, List, Optional
from git import Repo, GitCommandError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkCollector:
    def __init__(self, output_dir: str, retry_limit: int = 3):
        self.output_dir = Path(output_dir)
        self.retry_limit = retry_limit
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def collect_all(self, benchmark_list: List[Dict]) -> Dict:
        """Collect metadata for all benchmarks"""
        results = {
            'successful': [],
            'failed': [],
            'partial': []
        }
        
        for benchmark in benchmark_list:
            name = benchmark['name']
            logger.info(f"Processing {name}...")
            
            bench_dir = self.output_dir / 'benchmarks' / name
            bench_dir.mkdir(parents=True, exist_ok=True)
            
            sources = {
                'paper': False,
                'readme': False,
                'code': False
            }
            
            # Download paper
            if benchmark.get('arxiv_id'):
                sources['paper'] = self.download_paper(
                    benchmark['arxiv_id'], 
                    str(bench_dir / 'paper.pdf')
                )
            
            # Clone repository
            if benchmark.get('github_url'):
                sources['readme'], sources['code'] = self.clone_repo(
                    benchmark['github_url'],
                    str(bench_dir)
                )
            
            # Fetch HuggingFace metadata
            hf_meta = {}
            if benchmark.get('hf_name'):
                hf_meta = self.fetch_huggingface_metadata(benchmark['hf_name'])
            
            # Save metadata summary
            metadata = {
                'name': name,
                'domain': benchmark.get('domain', 'unknown'),
                'expected_compliant': benchmark.get('expected_compliant', None),
                'sources_collected': sources,
                'huggingface_metadata': hf_meta,
                'collection_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            with open(bench_dir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Categorize result
            if all(sources.values()):
                results['successful'].append(name)
            elif any(sources.values()):
                results['partial'].append(name)
            else:
                results['failed'].append(name)
        
        return results
    
    def download_paper(self, arxiv_id: str, dest: str) -> bool:
        """Download paper from ArXiv with retry"""
        for attempt in range(self.retry_limit):
            try:
                client = arxiv.Client()
                search = arxiv.Search(id_list=[arxiv_id])
                paper = next(client.results(search))
                paper.download_pdf(filename=dest)
                logger.info(f"Downloaded paper {arxiv_id}")
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/{self.retry_limit} failed for {arxiv_id}: {e}")
                if attempt < self.retry_limit - 1:
                    time.sleep(2 ** attempt)
        
        logger.error(f"Failed to download paper {arxiv_id} after {self.retry_limit} attempts")
        return False
    
    def clone_repo(self, github_url: str, dest: str, filter_patterns: Optional[List[str]] = None) -> tuple:
        """Clone GitHub repo and extract README + eval scripts"""
        if filter_patterns is None:
            filter_patterns = ['eval*.py', 'test*.py', 'metrics.py', 'benchmark*.py']
        
        readme_ok = False
        code_ok = False
        
        for attempt in range(self.retry_limit):
            try:
                repo_dir = Path(dest) / 'repo_clone'
                if repo_dir.exists():
                    import shutil
                    shutil.rmtree(repo_dir)
                
                Repo.clone_from(github_url, repo_dir, depth=1)
                
                # Extract README
                for readme_name in ['README.md', 'README.rst', 'README.txt', 'README']:
                    readme_path = repo_dir / readme_name
                    if readme_path.exists():
                        import shutil
                        shutil.copy(readme_path, Path(dest) / 'README.md')
                        readme_ok = True
                        break
                
                # Extract eval scripts
                eval_scripts = []
                for pattern in filter_patterns:
                    eval_scripts.extend(repo_dir.rglob(pattern))
                
                if eval_scripts:
                    # Copy first matching eval script
                    import shutil
                    shutil.copy(eval_scripts[0], Path(dest) / 'eval_script.py')
                    code_ok = True
                
                logger.info(f"Cloned repo {github_url} (README: {readme_ok}, Code: {code_ok})")
                return readme_ok, code_ok
                
            except (GitCommandError, Exception) as e:
                logger.warning(f"Attempt {attempt+1}/{self.retry_limit} failed for {github_url}: {e}")
                if attempt < self.retry_limit - 1:
                    time.sleep(2 ** attempt)
        
        logger.error(f"Failed to clone {github_url} after {self.retry_limit} attempts")
        return False, False
    
    def fetch_huggingface_metadata(self, dataset_name: str) -> Dict:
        """Check HuggingFace registry for dataset existence"""
        try:
            url = f"https://huggingface.co/api/datasets/{dataset_name}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'available': True,
                    'downloads': data.get('downloads', 0),
                    'tags': data.get('tags', [])
                }
            else:
                return {'available': False}
        except Exception as e:
            logger.warning(f"Failed to fetch HF metadata for {dataset_name}: {e}")
            return {'available': False, 'error': str(e)}

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Collect benchmark metadata')
    parser.add_argument('--benchmarks', required=True, help='Path to benchmarks.yaml')
    parser.add_argument('--output', required=True, help='Output directory')
    args = parser.parse_args()
    
    with open(args.benchmarks, 'r') as f:
        config = yaml.safe_load(f)
    
    collector = BenchmarkCollector(args.output)
    results = collector.collect_all(config['benchmarks'])
    
    print("\n=== Collection Summary ===")
    print(f"Successful: {len(results['successful'])} - {results['successful']}")
    print(f"Partial: {len(results['partial'])} - {results['partial']}")
    print(f"Failed: {len(results['failed'])} - {results['failed']}")
    
    completeness = len(results['successful']) / (len(results['successful']) + len(results['partial']) + len(results['failed']))
    print(f"\nCompleteness: {completeness:.2%}")
    
    if completeness < 0.9:
        print("WARNING: Completeness < 90%, gate may fail")
        sys.exit(1)

if __name__ == '__main__':
    main()
