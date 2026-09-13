"""GitHub Metrics Collection Module

Collects community engagement metrics from GitHub API.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Callable
import pandas as pd
from github import Github, GithubException, RateLimitExceededException
import time
import numpy as np


class GitHubMetricsCollector:
    """Collects GitHub activity metrics for repositories."""

    def __init__(self, github_token: Optional[str] = None, max_retries: int = 3):
        """Initialize GitHub API client.

        Args:
            github_token: Personal Access Token for GitHub API (None = unauthenticated)
            max_retries: Maximum retry attempts for rate-limited requests
        """
        self.github = Github(github_token) if github_token else Github()
        self.max_retries = max_retries

    def collect_commits_per_month(
        self,
        repo_id: str,
        t0: datetime,
        t90: datetime
    ) -> float:
        """Collect commits/month metric for 90-day window.

        Args:
            repo_id: Repository identifier (format: "owner/repo")
            t0: Start date (T0)
            t90: End date (T0 + 90 days)

        Returns:
            Commits per month (normalized to 30-day month)
        """
        def _collect():
            repo = self.github.get_repo(repo_id)
            commits = repo.get_commits(since=t0, until=t90)
            commit_count = commits.totalCount

            # Normalize to commits/month (30 days)
            days_elapsed = (t90 - t0).days
            months = days_elapsed / 30.0
            return commit_count / months if months > 0 else 0.0

        return self._exponential_backoff_retry(_collect)

    def collect_unique_contributors(
        self,
        repo_id: str,
        commits: Optional[List] = None
    ) -> int:
        """Count unique contributors from commit history.

        Args:
            repo_id: Repository identifier
            commits: List of commits (if None, fetch from API)

        Returns:
            Number of unique contributors
        """
        def _collect():
            repo = self.github.get_repo(repo_id)
            contributors = repo.get_contributors()
            return contributors.totalCount

        return self._exponential_backoff_retry(_collect)

    def collect_median_issue_response(
        self,
        repo_id: str,
        t0: datetime,
        t90: datetime
    ) -> Optional[float]:
        """Calculate median issue response time.

        Args:
            repo_id: Repository identifier
            t0: Start date
            t90: End date

        Returns:
            Median response time in days, or None if <5 issues
        """
        def _collect():
            repo = self.github.get_repo(repo_id)
            issues = repo.get_issues(state='all', since=t0)

            response_times = []

            for issue in issues:
                # Filter by temporal window
                if issue.created_at < t0 or issue.created_at > t90:
                    continue

                # Skip pull requests (they are also "issues" in GitHub API)
                if issue.pull_request is not None:
                    continue

                first_response = None

                # Check for first comment
                try:
                    comments = issue.get_comments()
                    if comments.totalCount > 0:
                        first_comment = comments[0]
                        first_response = first_comment.created_at
                except:
                    pass

                # Check for close event
                if issue.closed_at is not None:
                    if first_response is None or issue.closed_at < first_response:
                        first_response = issue.closed_at

                # Calculate response time
                if first_response is not None:
                    response_time = (first_response - issue.created_at).total_seconds() / 86400.0  # days
                    response_times.append(response_time)

            # Require at least 5 issues for meaningful median
            if len(response_times) < 5:
                return None

            return float(np.median(response_times))

        return self._exponential_backoff_retry(_collect)

    def collect_repository_age(
        self,
        repo_id: str,
        t90: datetime
    ) -> int:
        """Calculate repository age at T90.

        Args:
            repo_id: Repository identifier
            t90: Reference date (T0 + 90 days)

        Returns:
            Repository age in days at T90
        """
        def _collect():
            repo = self.github.get_repo(repo_id)
            created_at = repo.created_at
            age_days = (t90 - created_at).days
            return age_days

        return self._exponential_backoff_retry(_collect)

    def collect_all_metrics(self, repo_list: pd.DataFrame) -> pd.DataFrame:
        """Collect all metrics for a list of repositories.

        Args:
            repo_list: DataFrame with columns [repo_id, t0_date]

        Returns:
            DataFrame with columns [repo_id, commits_per_month, unique_contributors,
                                     median_issue_response, repo_age_days]
        """
        results = []

        for idx, row in repo_list.iterrows():
            repo_id = row['repo_id']
            t0 = pd.to_datetime(row['t0_date'])
            t90 = t0 + timedelta(days=90)

            print(f"Collecting metrics for {repo_id} ({idx+1}/{len(repo_list)})...")

            try:
                # Collect metrics
                commits_pm = self.collect_commits_per_month(repo_id, t0, t90)
                contributors = self.collect_unique_contributors(repo_id)
                issue_response = self.collect_median_issue_response(repo_id, t0, t90)
                repo_age = self.collect_repository_age(repo_id, t90)

                results.append({
                    'repo_id': repo_id,
                    'commits_per_month': commits_pm,
                    'unique_contributors': contributors,
                    'median_issue_response': issue_response,
                    'repo_age_days': repo_age
                })

            except Exception as e:
                print(f"  ERROR collecting {repo_id}: {e}")
                # Add null row to maintain alignment
                results.append({
                    'repo_id': repo_id,
                    'commits_per_month': None,
                    'unique_contributors': None,
                    'median_issue_response': None,
                    'repo_age_days': None
                })

            # Check rate limit periodically
            if idx % 10 == 0:
                remaining, reset_time = self._check_rate_limit()
                print(f"  Rate limit: {remaining} requests remaining")

        return pd.DataFrame(results)

    def _exponential_backoff_retry(self, func: Callable, *args, **kwargs):
        """Retry function with exponential backoff on rate limit errors.

        Args:
            func: Function to retry
            *args, **kwargs: Arguments to pass to func

        Returns:
            Function result

        Raises:
            Exception if max retries exceeded
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except RateLimitExceededException as e:
                if attempt == self.max_retries - 1:
                    raise

                # Exponential backoff: 1min, 2min, 4min
                wait_time = (2 ** attempt) * 60
                print(f"  Rate limit exceeded, waiting {wait_time}s (attempt {attempt+1}/{self.max_retries})...")
                time.sleep(wait_time)

            except GithubException as e:
                if e.status == 403:  # Rate limit as GithubException
                    if attempt == self.max_retries - 1:
                        raise

                    wait_time = (2 ** attempt) * 60
                    print(f"  Rate limit (403), waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise  # Other GitHub errors

            except Exception as e:
                # Timeout or other errors
                if attempt == self.max_retries - 1:
                    raise

                wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                print(f"  Error ({type(e).__name__}), retrying in {wait_time}s...")
                time.sleep(wait_time)

        raise Exception(f"Max retries ({self.max_retries}) exceeded")

    def _check_rate_limit(self) -> Tuple[int, int]:
        """Check GitHub API rate limit status.

        Returns:
            Tuple of (remaining_calls, reset_timestamp)
        """
        rate_limit = self.github.get_rate_limit()
        core = rate_limit.core
        return (core.remaining, int(core.reset.timestamp()))
