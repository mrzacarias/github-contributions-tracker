#!/usr/bin/env python3
"""
Tests for GitHubContributionsTracker
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.github_contributions_tracker.tracker import GitHubContributionsTracker


class TestGitHubContributionsTracker(unittest.TestCase):
    """Test cases for GitHubContributionsTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test-token'}):
            self.tracker = GitHubContributionsTracker()
    
    def test_init_with_token(self):
        """Test initialization with token."""
        tracker = GitHubContributionsTracker(token="test-token")
        self.assertEqual(tracker.token, "test-token")
    
    def test_init_without_token(self):
        """Test initialization without token raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError):
                GitHubContributionsTracker()
    
    def test_generate_summary_markdown(self):
        """Test markdown summary generation."""
        contributions = {
            'commits': [
                {'repo': 'test-repo', 'message': 'Test commit', 'sha': 'abc123', 'date': datetime.now(), 'url': 'http://test.com'},
                {'repo': 'test-repo', 'message': 'Another commit', 'sha': 'def456', 'date': datetime.now(), 'url': 'http://test.com'}
            ],
            'repositories': [
                {'name': 'test-repo', 'url': 'http://test.com', 'private': False}
            ]
        }
        
        summary = self.tracker.generate_summary(contributions, 'markdown')
        
        self.assertIn("# GitHub Contributions Summary", summary)
        self.assertIn("**Total Commits**: 2", summary)
        self.assertIn("**Repositories with Contributions**: 1", summary)
        self.assertIn("**test-repo**: Test commit (abc123)", summary)
        self.assertIn("**test-repo**: Another commit (def456)", summary)
    
    def test_generate_summary_plain(self):
        """Test plain text summary generation."""
        contributions = {
            'commits': [
                {'repo': 'test-repo', 'message': 'Test commit', 'sha': 'abc123', 'date': datetime.now(), 'url': 'http://test.com'}
            ],
            'repositories': [
                {'name': 'test-repo', 'url': 'http://test.com', 'private': False}
            ]
        }
        
        summary = self.tracker.generate_summary(contributions, 'plain')
        
        self.assertIn("GITHUB CONTRIBUTIONS SUMMARY", summary)
        self.assertIn("Total Commits: 1", summary)
        self.assertIn("test-repo: Test commit (abc123)", summary)
    
    def test_generate_low_level_tasks(self):
        """Test low-level tasks generation."""
        contributions = {
            'commits': [
                {'repo': 'repo1', 'message': 'Commit 1', 'sha': 'abc123', 'date': datetime.now(), 'url': 'http://test.com'},
                {'repo': 'repo1', 'message': 'Commit 2', 'sha': 'def456', 'date': datetime.now(), 'url': 'http://test.com'},
                {'repo': 'repo2', 'message': 'Commit 3', 'sha': 'ghi789', 'date': datetime.now(), 'url': 'http://test.com'}
            ],
            'repositories': []
        }
        
        low_level = self.tracker._generate_low_level_tasks(contributions)
        
        self.assertIn("## Low-Level Tasks", low_level)
        self.assertIn("Repository: repo1", low_level)
        self.assertIn("Repository: repo2", low_level)
        self.assertIn("Commit: abc123 - Commit 1", low_level)
        self.assertIn("Commit: def456 - Commit 2", low_level)
        self.assertIn("Commit: ghi789 - Commit 3", low_level)
    
    def test_generate_low_level_tasks_empty(self):
        """Test low-level tasks generation with empty contributions."""
        contributions = {'commits': [], 'repositories': []}
        
        low_level = self.tracker._generate_low_level_tasks(contributions)
        
        self.assertIn("## Low-Level Tasks", low_level)
        self.assertIn("No commits found", low_level)
    
    def test_generate_repos_only_summary(self):
        """Test repositories-only summary generation."""
        contributions = {
            'commits': [],
            'repositories': [
                {'name': 'repo1', 'url': 'http://repo1.com', 'private': False},
                {'name': 'repo2', 'url': 'http://repo2.com', 'private': True}
            ]
        }
        
        summary = self.tracker.generate_repos_only_summary(contributions, 'markdown')
        
        self.assertIn("# Repositories with Contributions", summary)
        self.assertIn("**Total Repositories**: 2", summary)
        self.assertIn("**repo1** (🌐 Public)", summary)
        self.assertIn("**repo2** (🔒 Private)", summary)
    
    @patch('builtins.open', create=True)
    def test_save_summary(self, mock_open):
        """Test saving summary to file."""
        summary = "# Test Summary\nThis is a test"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        self.tracker.save_summary(summary, "test.md")
        
        mock_open.assert_called_once_with("test.md", 'w', encoding='utf-8')
        mock_file.write.assert_called_once_with(summary)
    
    @patch('builtins.open', create=True)
    def test_save_summary_default_filename(self, mock_open):
        """Test saving summary with default filename."""
        summary = "# Test Summary\nThis is a test"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
            self.tracker.save_summary(summary)
        
        mock_open.assert_called_once_with("github_contributions_20240101_120000.md", 'w', encoding='utf-8')


if __name__ == '__main__':
    unittest.main() 
