#!/usr/bin/env python3
"""
GitHub Contributions Tracker

A Python package to track your GitHub contributions for a specified time range
and generate comprehensive summaries with AI-powered insights using Amazon Bedrock.
"""

from .tracker import GitHubContributionsTracker
from .bedrock_summarizer import BedrockSummarizer

__version__ = "1.0.0"
__author__ = "GitHub Contributions Tracker"
__email__ = ""

__all__ = [
    "GitHubContributionsTracker",
    "BedrockSummarizer",
] 
