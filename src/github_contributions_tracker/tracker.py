#!/usr/bin/env python3
"""
GitHub Contributions Tracker main module
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import requests
from dateutil import parser as date_parser
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Commit import Commit

from .bedrock_summarizer import BedrockSummarizer


class GitHubContributionsTracker:
    def __init__(self, token: str = None, username: str = None):
        """Initialize the tracker with GitHub token."""
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass --token")
        
        self.github = Github(self.token)
        
        # If username is provided, get that user, otherwise get authenticated user
        if username:
            self.user = self.github.get_user(username)
            print(f"Tracking contributions for user: {username}")
        else:
            self.user = self.github.get_user()
            print(f"Tracking contributions for authenticated user: {self.user.login}")
    
    def get_contributions(self, start_date: datetime, end_date: datetime, 
                         include_private: bool = True, optimize: bool = True, limit: int = None, 
                         skip_reviews: bool = True, use_graphql: bool = False, use_bulk: bool = True, 
                         use_conservative: bool = False) -> Dict[str, List[Any]]:
        """
        Fetch all contributions within the specified date range.
        
        Args:
            start_date: Start date for contributions
            end_date: End date for contributions
            include_private: Whether to include private repositories
            
        Returns:
            Dictionary containing different types of contributions
        """
        contributions = {
            'commits': [],
            'pull_requests': [],
            'issues': [],
            'reviews': [],
            'repositories': []
        }
        
        if optimize:
            # Get repositories with contributions using GitHub's search API
            repos_with_contributions = self._get_repos_with_contributions(start_date, end_date, include_private)
            print(f"Found {len(repos_with_contributions)} repositories with contributions")
        else:
            # Process all repositories (original behavior)
            repos = self.user.get_repos()
            if not include_private:
                repos = [repo for repo in repos if not repo.private]
            repos_with_contributions = [repo.full_name for repo in repos]
            print(f"Processing all {len(repos_with_contributions)} repositories (optimization disabled)")
        
        # Apply limit if specified
        if limit and limit > 0:
            repos_with_contributions = repos_with_contributions[:limit]
            print(f"Limited to {len(repos_with_contributions)} repositories for testing")
        
        # Use conservative approach if requested (rate limit safe)
        if use_conservative:
            return self._fetch_contributions_conservative(start_date, end_date, include_private)
        
        # Use bulk search if requested (most efficient)
        if use_bulk:
            return self._fetch_contributions_bulk_search(start_date, end_date, include_private)
        
        # Use GraphQL if requested
        if use_graphql:
            return self._fetch_contributions_graphql(repos_with_contributions, start_date, end_date)
        
        print("Processing repositories...")
        for i, repo_name in enumerate(repos_with_contributions, 1):
            try:
                print(f"  Processing repository {i}/{len(repos_with_contributions)}: {repo_name}")
                # Get the repository object
                repo = self.github.get_repo(repo_name)
                
                # Get commits with pagination limit
                commits = repo.get_commits(since=start_date, until=end_date, author=self.user, per_page=100)
                if commits.totalCount > 0:
                    print(f"    Found {commits.totalCount} commits")
                    # Limit to first 50 commits per repo for performance
                    commit_count = 0
                    for commit in commits:
                        if commit_count >= 50:  # Limit commits per repo
                            break
                        # Ensure commit date is timezone-aware
                        commit_date = commit.commit.author.date
                        if commit_date.tzinfo is None:
                            commit_date = commit_date.replace(tzinfo=timezone.utc)
                        
                        commit_data = {
                            'repo': repo.name,
                            'sha': commit.sha[:7],
                            'message': commit.commit.message.split('\n')[0],  # First line only
                            'date': commit_date,
                            'url': commit.html_url
                        }
                        contributions['commits'].append(commit_data)
                        print(f"      Commit: {commit_data['sha']} - {commit_data['message']}")
                        commit_count += 1
                
                # Add repository to list
                contributions['repositories'].append({
                    'name': repo.name,
                    'url': repo.html_url,
                    'private': repo.private
                })
                
            except Exception as e:
                print(f"Error processing repository {repo_name}: {e}")
                continue
        
        print(f"Completed processing {len(contributions['repositories'])} repositories")
        
        # Print summary of all commits found
        if contributions['commits']:
            print(f"\n📊 COMMIT SUMMARY:")
            print(f"Total commits found: {len(contributions['commits'])}")
            print(f"Repositories with commits: {len(set(commit['repo'] for commit in contributions['commits']))}")
            print(f"\nAll commits:")
            for commit in contributions['commits']:
                print(f"  {commit['repo']}: {commit['sha']} - {commit['message']}")
        
        return contributions
    
    def _get_repos_with_contributions(self, start_date: datetime, end_date: datetime, 
                                    include_private: bool = False) -> List[str]:
        """
        Get list of repositories where the user has contributed in the given date range.
        Uses GitHub's search API for efficiency.
        
        Args:
            start_date: Start date for contributions
            end_date: End date for contributions
            include_private: Whether to include private repositories
            
        Returns:
            List of repository full names (owner/repo)
        """
        repos_with_contributions = set()
        
        # Format dates for GitHub search API
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        try:
            # Search for commits by the user
            commit_query = f'author:{self.user.login} committer-date:{start_date_str}..{end_date_str}'
            commits = self.github.search_commits(query=commit_query)
            
            print(f"Found {commits.totalCount} commits in search")
            
            for commit in commits:
                # Extract repository name from commit URL
                # URL format: https://github.com/owner/repo/commit/sha
                url_parts = commit.html_url.split('/')
                if len(url_parts) >= 5:
                    repo_name = f"{url_parts[3]}/{url_parts[4]}"
                    repos_with_contributions.add(repo_name)
            

            
            # Note: GitHub search API doesn't directly support PR reviews
            # We'll need to check repositories found through other means for reviews
            
            # Filter out private repositories if not included
            if not include_private:
                filtered_repos = set()
                for repo_name in repos_with_contributions:
                    try:
                        repo = self.github.get_repo(repo_name)
                        if not repo.private:
                            filtered_repos.add(repo_name)
                    except Exception:
                        # If we can't access the repo, skip it (likely private)
                        continue
                repos_with_contributions = filtered_repos
                print(f"After filtering private repos: {len(repos_with_contributions)} repositories")
            else:
                print(f"Total repositories found: {len(repos_with_contributions)}")
            
        except Exception as e:
            print(f"Warning: Could not use search API optimization: {e}")
            print("Falling back to processing all repositories...")
            # Fallback to processing all repositories
            repos = self.user.get_repos()
            if not include_private:
                repos = [repo for repo in repos if not repo.private]
            return [repo.full_name for repo in repos]
        
        return list(repos_with_contributions)
    
    def _fetch_contributions_graphql(self, repos_with_contributions: List[str], start_date: datetime, end_date: datetime) -> Dict[str, List[Any]]:
        """
        Fetch contributions using GraphQL API for better performance.
        This method batches multiple queries and reduces API calls significantly.
        """
        contributions = {
            'commits': [],
            'pull_requests': [],
            'issues': [],
            'reviews': [],
            'repositories': []
        }
        
        # Format dates for GraphQL
        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        print("Using GraphQL API for efficient data fetching...")
        
        # Process repositories in batches of 5 to avoid rate limits
        batch_size = 5
        for i in range(0, len(repos_with_contributions), batch_size):
            batch = repos_with_contributions[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(repos_with_contributions) + batch_size - 1)//batch_size}")
            
            for repo_name in batch:
                try:
                    # Extract owner and repo name
                    owner, repo = repo_name.split('/', 1)
                    
                    # GraphQL query for commits
                    commits_query = """
                    query($owner: String!, $repo: String!, $since: GitTimestamp!, $until: GitTimestamp!) {
                        repository(owner: $owner, name: $repo) {
                            defaultBranchRef {
                                target {
                                    ... on Commit {
                                        history(since: $since, until: $until, first: 50) {
                                            nodes {
                                                oid
                                                messageHeadline
                                                committedDate
                                                url
                                                author {
                                                    user {
                                                        login
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    """
                    
                    # GraphQL query for pull requests
                    prs_query = """
                    query($owner: String!, $repo: String!, $author: String!, $since: DateTime!, $until: DateTime!) {
                        repository(owner: $owner, name: $repo) {
                            pullRequests(first: 20, orderBy: {field: CREATED_AT, direction: DESC}) {
                                nodes {
                                    number
                                    title
                                    state
                                    createdAt
                                    mergedAt
                                    url
                                    author {
                                        login
                                    }
                                }
                            }
                        }
                    }
                    """
                    
                    # GraphQL query for issues
                    issues_query = """
                    query($owner: String!, $repo: String!, $author: String!, $since: DateTime!, $until: $until) {
                        repository(owner: $owner, name: $repo) {
                            issues(first: 20, orderBy: {field: CREATED_AT, direction: DESC}) {
                                nodes {
                                    number
                                    title
                                    state
                                    createdAt
                                    url
                                    author {
                                        login
                                    }
                                }
                            }
                        }
                    }
                    """
                    
                    # Execute queries
                    variables = {
                        "owner": owner,
                        "repo": repo,
                        "since": start_date_str,
                        "until": end_date_str
                    }
                    
                    # Get commits
                    try:
                        commits_result = self.github._Github__requester.requestJson("POST", "/graphql", 
                            input={"query": commits_query, "variables": variables})
                        
                    except Exception as e:
                        print(f"    Error making GraphQL request for {repo_name}: {e}")
                        continue
                    
                    # Handle different response types
                    if isinstance(commits_result, tuple):
                        # GraphQL returns (status_code, headers, response_body)
                        status_code, headers, response_body = commits_result
                        
                        if status_code != 200:
                            print(f"    Warning: GraphQL returned status {status_code} for {repo_name}, skipping...")
                            continue
                        
                        # Parse the response body
                        try:
                            if isinstance(response_body, str):
                                import json
                                commits_result = json.loads(response_body)
                            else:
                                commits_result = response_body
                        except Exception as e:
                            print(f"    Error parsing GraphQL response for {repo_name}: {e}")
                            continue
                            
                    elif isinstance(commits_result, int):
                        print(f"    Warning: GraphQL returned integer response for {repo_name}: {commits_result}, skipping...")
                        continue
                    elif not isinstance(commits_result, dict):
                        print(f"    Warning: GraphQL returned unexpected response type for {repo_name}: {type(commits_result)} = {commits_result}, skipping...")
                        continue
                    
                    # Check for GraphQL errors
                    if commits_result.get("errors"):
                        print(f"    Warning: GraphQL errors for {repo_name}: {commits_result['errors']}")
                        continue
                    
                    # Process commits if we have valid data
                    try:
                        repo_data = commits_result.get("data", {}).get("repository")
                        if not repo_data:
                            print(f"    Warning: No repository data for {repo_name}, skipping...")
                            continue

                        default_branch = repo_data.get("defaultBranchRef")
                        if not default_branch:
                            print(f"    Warning: No default branch for {repo_name}, skipping...")
                            continue

                        target = default_branch.get("target")
                        if not target or "history" not in target:
                            print(f"    Warning: No commit history for {repo_name}, skipping...")
                            continue

                        commits_data = target["history"]["nodes"]
                        print(f"  Repository: {repo_name}")
                        for commit in commits_data:
                            # Filter by author
                            author = commit.get('author')
                            if not author or not author.get('user') or not author['user'].get('login'):
                                continue  # Skip commits with missing author info
                            author_login = author['user']['login']
                            if author_login != self.user.login:
                                continue
                                
                            commit_data = {
                                'repo': repo,
                                'sha': commit['oid'][:7],
                                'message': commit['messageHeadline'],
                                'date': date_parser.parse(commit['committedDate']),
                                'url': commit['url']
                            }
                            contributions['commits'].append(commit_data)
                            print(f"    Commit: {commit_data['sha']} - {commit_data['message']}")
                    except Exception as e:
                        print(f"    Error processing commits for {repo_name}: {e}")
                        continue
                    
                    # Add repository to list
                    contributions['repositories'].append({
                        'name': repo,
                        'url': f"https://github.com/{repo_name}",
                        'private': False  # We'll determine this later if needed
                    })
                    
                except Exception as e:
                    print(f"Error processing repository {repo_name}: {e}")
                    continue
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(repos_with_contributions):
                import time
                time.sleep(1)
        
        # Print summary of all commits found
        if contributions['commits']:
            print(f"\n📊 COMMIT SUMMARY:")
            print(f"Total commits found: {len(contributions['commits'])}")
            print(f"Repositories with commits: {len(set(commit['repo'] for commit in contributions['commits']))}")
            print(f"\nAll commits:")
            for commit in contributions['commits']:
                print(f"  {commit['repo']}: {commit['sha']} - {commit['message']}")
        
        # Check if we found any commits, if not fall back to conservative approach
        if not contributions['commits']:
            print("No commits found via GraphQL, falling back to conservative approach...")
            # We need to determine include_private from the repositories we found
            include_private = any(repo.get('private', False) for repo in contributions['repositories'])
            return self._fetch_contributions_conservative(start_date, end_date, include_private)
        
        return contributions
    
    def _fetch_contributions_bulk_search(self, start_date: datetime, end_date: datetime, include_private: bool = False) -> Dict[str, List[Any]]:
        """
        Fetch contributions using bulk search queries - the smartest approach.
        Uses GitHub's search API with advanced queries to get everything in one go.
        """
        contributions = {
            'commits': [],
            'pull_requests': [],
            'issues': [],
            'reviews': [],
            'repositories': []
        }
        
        # Format dates for search
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        print("Using bulk search API for maximum efficiency...")
        
        try:
            # Bulk search for commits with rate limit handling
            print("Searching for commits...")
            commit_query = f'author:{self.user.login} committer-date:{start_date_str}..{end_date_str}'
            
            try:
                commits = self.github.search_commits(query=commit_query)
            except Exception as e:
                if "403" in str(e) or "rate limit" in str(e).lower():
                    print("Rate limit hit for commits search, falling back to conservative approach...")
                    return self._fetch_contributions_conservative(start_date, end_date, include_private)
                else:
                    raise e
            
            # Group commits by repository
            repo_commits = {}
            for commit in commits:
                url_parts = commit.html_url.split('/')
                if len(url_parts) >= 5:
                    repo_name = f"{url_parts[3]}/{url_parts[4]}"
                    if repo_name not in repo_commits:
                        repo_commits[repo_name] = []
                    repo_commits[repo_name].append(commit)
            
            # Process commits by repository
            for repo_name, repo_commit_list in repo_commits.items():
                owner, repo = repo_name.split('/', 1)
                print(f"  Repository: {repo_name}")
                for commit in repo_commit_list[:50]:  # Limit to 50 commits per repo
                    commit_data = {
                        'repo': repo,
                        'sha': commit.sha[:7],
                        'message': commit.commit.message.split('\n')[0],
                        'date': commit.commit.author.date,
                        'url': commit.html_url
                    }
                    contributions['commits'].append(commit_data)
                    print(f"    Commit: {commit_data['sha']} - {commit_data['message']}")
            
            print(f"Found {len(contributions['commits'])} commits across {len(repo_commits)} repositories")
            
            # Combine all repositories (only commits)
            all_repos = set(repo_commits.keys())
            
            # Filter private repositories if needed
            if not include_private:
                public_repos = set()
                for repo_name in all_repos:
                    try:
                        repo = self.github.get_repo(repo_name)
                        if not repo.private:
                            public_repos.add(repo_name)
                    except Exception:
                        # Skip if we can't access (likely private)
                        continue
                all_repos = public_repos
            
            # Add repositories to contributions
            for repo_name in all_repos:
                owner, repo = repo_name.split('/', 1)
                contributions['repositories'].append({
                    'name': repo,
                    'url': f"https://github.com/{repo_name}",
                    'private': False  # We'll determine this later if needed
                })
            
            print(f"Total repositories with contributions: {len(contributions['repositories'])}")
            
            # Print summary of all commits found
            if contributions['commits']:
                print(f"\n📊 COMMIT SUMMARY:")
                print(f"Total commits found: {len(contributions['commits'])}")
                print(f"Repositories with commits: {len(set(commit['repo'] for commit in contributions['commits']))}")
                print(f"\nAll commits:")
                for commit in contributions['commits']:
                    print(f"  {commit['repo']}: {commit['sha']} - {commit['message']}")
            
        except Exception as e:
            print(f"Error in bulk search: {e}")
            print("Falling back to conservative approach...")
            return self._fetch_contributions_conservative(start_date, end_date, include_private)
        
        return contributions
    
    def _fetch_contributions_conservative(self, start_date: datetime, end_date: datetime, include_private: bool = False) -> Dict[str, List[Any]]:
        """
        Fetch contributions using a conservative approach to avoid rate limits.
        Uses smaller date ranges and processes data in chunks.
        """
        contributions = {
            'commits': [],
            'pull_requests': [],
            'issues': [],
            'reviews': [],
            'repositories': []
        }
        
        print("Using conservative approach to avoid rate limits...")
        
        # Process in weekly chunks to avoid rate limits
        current_date = start_date
        chunk_size = timedelta(days=7)
        
        while current_date < end_date:
            chunk_end = min(current_date + chunk_size, end_date)
            print(f"Processing chunk: {current_date.date()} to {chunk_end.date()}")
            
            try:
                # Get repositories with contributions for this chunk
                repos_with_contributions = self._get_repos_with_contributions(current_date, chunk_end, include_private)
                
                if repos_with_contributions:
                    # Process each repository individually for this chunk
                    for repo_name in repos_with_contributions[:10]:  # Limit to 10 repos per chunk
                        try:
                            repo = self.github.get_repo(repo_name)
                            
                            # Get commits for this chunk
                            commits = repo.get_commits(since=current_date, until=chunk_end, author=self.user, per_page=30)
                            print(f"  Repository: {repo_name}")
                            for commit in commits:
                                commit_data = {
                                    'repo': repo.name,
                                    'sha': commit.sha[:7],
                                    'message': commit.commit.message.split('\n')[0],
                                    'date': commit.commit.author.date,
                                    'url': commit.html_url
                                }
                                contributions['commits'].append(commit_data)
                                print(f"    Commit: {commit_data['sha']} - {commit_data['message']}")
                            

                            
                            # Add repository if not already added
                            repo_exists = any(r['name'] == repo.name for r in contributions['repositories'])
                            if not repo_exists:
                                contributions['repositories'].append({
                                    'name': repo.name,
                                    'url': repo.html_url,
                                    'private': repo.private
                                })
                                
                        except Exception as e:
                            print(f"Error processing repository {repo_name}: {e}")
                            continue
                
                # Small delay between chunks
                import time
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing chunk {current_date.date()} to {chunk_end.date()}: {e}")
            
            current_date = chunk_end
        
        # Print summary of all commits found
        if contributions['commits']:
            print(f"\n📊 COMMIT SUMMARY:")
            print(f"Total commits found: {len(contributions['commits'])}")
            print(f"Repositories with commits: {len(set(commit['repo'] for commit in contributions['commits']))}")
            print(f"\nAll commits:")
            for commit in contributions['commits']:
                print(f"  {commit['repo']}: {commit['sha']} - {commit['message']}")
        
        return contributions
    
    def generate_summary(self, contributions: Dict[str, List[Any]], format_type: str = 'markdown') -> str:
        """
        Generate a formatted summary of contributions.
        
        Args:
            contributions: Dictionary of contributions
            format_type: 'markdown' or 'plain'
            
        Returns:
            Formatted summary string
        """
        summary = []
        
        # Summary statistics
        total_commits = len(contributions['commits'])
        total_repos = len(contributions['repositories'])
        
        if format_type == 'markdown':
            summary.append("# GitHub Contributions Summary\n")
            summary.append(f"## Overview")
            summary.append(f"- **Total Commits**: {total_commits}")
            summary.append(f"- **Repositories with Contributions**: {total_repos}\n")
            
            # Commits
            if contributions['commits']:
                summary.append("## Commits")
                for commit in contributions['commits']:
                    summary.append(f"- **{commit['repo']}**: {commit['message']} ({commit['sha']})")
                summary.append("")
            

            
            # Repositories
            if contributions['repositories']:
                summary.append("## Repositories with Contributions")
                for repo in contributions['repositories']:
                    visibility = "🔒 Private" if repo['private'] else "🌐 Public"
                    summary.append(f"- **{repo['name']}** ({visibility})")
                summary.append("")
        
        else:  # plain text
            summary.append("GITHUB CONTRIBUTIONS SUMMARY")
            summary.append("=" * 40)
            summary.append("")
            summary.append("OVERVIEW")
            summary.append("-" * 10)
            summary.append(f"Total Commits: {total_commits}")
            summary.append(f"Repositories with Contributions: {total_repos}")
            summary.append("")
            
            # Commits
            if contributions['commits']:
                summary.append("COMMITS")
                summary.append("-" * 10)
                for commit in contributions['commits']:
                    summary.append(f"- {commit['repo']}: {commit['message']} ({commit['sha']})")
                summary.append("")
            

            
            # Repositories
            if contributions['repositories']:
                summary.append("REPOSITORIES WITH CONTRIBUTIONS")
                summary.append("-" * 32)
                for repo in contributions['repositories']:
                    visibility = "Private" if repo['private'] else "Public"
                    summary.append(f"- {repo['name']} ({visibility})")
                summary.append("")
        
        return '\n'.join(summary)
    
    def generate_bedrock_summary(self, contributions: Dict[str, List[Any]], 
                                model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                                region: str = "us-east-1") -> str:
        """
        Generate a summarized version of contributions using Amazon Bedrock.
        
        Args:
            contributions: Dictionary of contributions
            model_id: Bedrock model ID to use
            region: AWS region for Bedrock
            
        Returns:
            Summarized contributions in markdown format
        """
        # First generate the regular summary to use as input
        regular_summary = self.generate_summary(contributions, 'markdown')
        
        # Create Bedrock summarizer
        summarizer = BedrockSummarizer(model_id=model_id, region=region)
        
        # Generate the AI-powered summary
        print("Generating AI-powered summary using Amazon Bedrock...")
        bedrock_summary = summarizer.summarize_contributions(regular_summary)
        
        # Add low-level tasks section before the high-level tasks
        low_level_section = self._generate_low_level_tasks(contributions)
        
        # Insert the low-level tasks section before "## High-Level Tasks Completed"
        if "## High-Level Tasks Completed" in bedrock_summary:
            bedrock_summary = bedrock_summary.replace(
                "## High-Level Tasks Completed",
                f"{low_level_section}\n\n## High-Level Tasks Completed"
            )
        else:
            # If the section isn't found, append it after the overview
            if "## Overview" in bedrock_summary:
                overview_end = bedrock_summary.find("##", bedrock_summary.find("## Overview") + 1)
                if overview_end == -1:
                    bedrock_summary += f"\n\n{low_level_section}"
                else:
                    bedrock_summary = bedrock_summary[:overview_end] + f"\n\n{low_level_section}\n\n" + bedrock_summary[overview_end:]
            else:
                bedrock_summary += f"\n\n{low_level_section}"
        
        return bedrock_summary
    
    def _generate_low_level_tasks(self, contributions: Dict[str, List[Any]]) -> str:
        """
        Generate the low-level tasks section with detailed commits organized by repository.
        
        Args:
            contributions: Dictionary of contributions
            
        Returns:
            Formatted low-level tasks section
        """
        if not contributions['commits']:
            return "## Low-Level Tasks\n\nNo commits found in the specified time period."
        
        # Group commits by repository
        repo_commits = {}
        for commit in contributions['commits']:
            repo_name = commit['repo']
            if repo_name not in repo_commits:
                repo_commits[repo_name] = []
            repo_commits[repo_name].append(commit)
        
        # Generate the low-level tasks section
        low_level_section = ["## Low-Level Tasks\n"]
        
        for repo_name in sorted(repo_commits.keys()):
            low_level_section.append(f"  Repository: {repo_name}")
            for commit in repo_commits[repo_name]:
                low_level_section.append(f"    Commit: {commit['sha']} - {commit['message']}")
            low_level_section.append("")  # Empty line between repositories
        
        return '\n'.join(low_level_section)
    
    def generate_repos_only_summary(self, contributions: Dict[str, List[Any]], format_type: str = 'markdown') -> str:
        """
        Generate a summary showing only repositories with contributions.
        
        Args:
            contributions: Dictionary of contributions
            format_type: 'markdown' or 'plain'
            
        Returns:
            Formatted summary string
        """
        summary = []
        total_repos = len(contributions['repositories'])
        
        if format_type == 'markdown':
            summary.append("# Repositories with Contributions\n")
            summary.append(f"**Total Repositories**: {total_repos}\n")
            
            if contributions['repositories']:
                summary.append("## Repository List")
                for repo in contributions['repositories']:
                    visibility = "🔒 Private" if repo['private'] else "🌐 Public"
                    summary.append(f"- **{repo['name']}** ({visibility}) - {repo['url']}")
                summary.append("")
        else:  # plain text
            summary.append("REPOSITORIES WITH CONTRIBUTIONS")
            summary.append("=" * 40)
            summary.append("")
            summary.append(f"Total Repositories: {total_repos}")
            summary.append("")
            
            if contributions['repositories']:
                summary.append("REPOSITORY LIST")
                summary.append("-" * 15)
                for repo in contributions['repositories']:
                    visibility = "Private" if repo['private'] else "Public"
                    summary.append(f"- {repo['name']} ({visibility}) - {repo['url']}")
                summary.append("")
        
        return '\n'.join(summary)
    
    def save_summary(self, summary: str, filename: str = None):
        """Save the summary to a file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"github_contributions_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary saved to: {filename}") 
