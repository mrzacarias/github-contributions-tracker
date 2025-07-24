#!/usr/bin/env python3
"""
Tests for BedrockSummarizer
"""

import unittest
from unittest.mock import Mock, patch
import json

from src.github_contributions_tracker.bedrock_summarizer import BedrockSummarizer


class TestBedrockSummarizer(unittest.TestCase):
    """Test cases for BedrockSummarizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.summarizer = BedrockSummarizer()
    
    def test_init(self):
        """Test BedrockSummarizer initialization."""
        summarizer = BedrockSummarizer(
            model_id="test-model",
            region="us-west-2",
            max_tokens=1000
        )
        
        self.assertEqual(summarizer.model_id, "test-model")
        self.assertEqual(summarizer.max_tokens, 1000)
        self.assertIsNotNone(summarizer.bedrock_runtime)
    
    def test_create_summary_prompt(self):
        """Test prompt creation."""
        contributions = "# Test Contributions\n- Commit 1\n- Commit 2"
        prompt = self.summarizer.create_summary_prompt(contributions)
        
        self.assertIn("Hi, would you create a more succinct summary", prompt)
        self.assertIn(contributions, prompt)
        self.assertIn("GitHub Contributions Summary - High-Level Tasks", prompt)
        self.assertIn("## Overview", prompt)
        self.assertIn("## High-Level Tasks Completed", prompt)
        self.assertIn("## Key Achievements", prompt)
        self.assertIn("## Impact", prompt)
    
    @patch('boto3.client')
    def test_summarize_contributions_success(self, mock_boto3_client):
        """Test successful summarization."""
        # Mock the Bedrock response
        mock_response = Mock()
        mock_response.get.return_value.read.return_value = json.dumps({
            'content': [{'text': 'Test AI summary'}]
        })
        
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_model.return_value = mock_response
        mock_boto3_client.return_value = mock_bedrock_client
        
        summarizer = BedrockSummarizer()
        result = summarizer.summarize_contributions("Test contributions")
        
        self.assertEqual(result, "Test AI summary")
        mock_bedrock_client.invoke_model.assert_called_once()
    
    @patch('boto3.client')
    def test_summarize_contributions_error(self, mock_boto3_client):
        """Test error handling in summarization."""
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_model.side_effect = Exception("Test error")
        mock_boto3_client.return_value = mock_bedrock_client
        
        summarizer = BedrockSummarizer()
        result = summarizer.summarize_contributions("Test contributions")
        
        self.assertIn("Error generating summary", result)
        self.assertIn("Test contributions", result)


if __name__ == '__main__':
    unittest.main() 
