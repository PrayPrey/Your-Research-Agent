"""GitHub REST API scraper."""
import requests
import logging
import re
from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


class GitHubScraper:
    """Client for GitHub REST API interactions."""

    def __init__(self, token: str):
        """Initialize GitHub scraper.

        Args:
            token: GitHub personal access token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"token {token}"})

    def parse_repo_url(self, url: str) -> Optional[tuple]:
        """Parse GitHub URL to extract owner and repo.

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (owner, repo) or None if invalid
        """
        match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
        if match:
            owner, repo = match.groups()
            repo = repo.rstrip('.git')
            return owner, repo
        return None

    def get_repo_structure(self, owner: str, repo: str) -> Dict:
        """Get repository file tree via Git Trees API.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary containing repository structure
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/main?recursive=1"

        try:
            response = self.session.get(url, timeout=30)

            # Try master branch if main doesn't exist
            if response.status_code == 404:
                url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/master?recursive=1"
                response = self.session.get(url, timeout=30)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch structure for {owner}/{repo}: {e}")
            return {}

    def check_documentation_files(self, file_tree: List[Dict]) -> Dict[str, bool]:
        """Check for presence of structural documentation files.

        Args:
            file_tree: List of file objects from Git Trees API

        Returns:
            Dictionary with boolean flags for documentation presence
        """
        file_paths = [f['path'] for f in file_tree if f.get('type') == 'blob']

        env_files = ['requirements.txt', 'environment.yml', 'Pipfile', 'environment.yaml']
        has_env_file = any(f in file_paths or f.lower() in [p.lower() for p in file_paths]
                          for f in env_files)

        has_dockerfile = any('dockerfile' in p.lower() for p in file_paths)

        return {
            'env_file': has_env_file,
            'dockerfile': has_dockerfile
        }

    def parse_requirements_for_pins(self, owner: str, repo: str) -> bool:
        """Parse requirements.txt content for pinned versions.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            True if >= 50% of dependencies use pinned versions
        """
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/requirements.txt"

        try:
            response = requests.get(url, timeout=30)

            # Try master branch if main doesn't exist
            if response.status_code == 404:
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/requirements.txt"
                response = requests.get(url, timeout=30)

            if response.status_code != 200:
                return False

            content = response.text

            lines = [l.strip() for l in content.split('\n')
                    if l.strip() and not l.strip().startswith('#')]

            if not lines:
                return False

            pinned_pattern = re.compile(r'==\d+\.\d+')
            pinned_count = sum(1 for line in lines if pinned_pattern.search(line))

            return pinned_count >= len(lines) * 0.5
        except Exception as e:
            logger.debug(f"Failed to parse requirements for {owner}/{repo}: {e}")
            return False

    def get_repo_metadata(self, owner: str, repo: str) -> Dict:
        """Extract control variables: stars, forks, created_at, etc.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with repository metadata
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'created_at': data.get('created_at', ''),
                'language': data.get('language', 'Unknown')
            }
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for {owner}/{repo}: {e}")
            return {}
