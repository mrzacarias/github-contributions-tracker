#!/usr/bin/env python3
"""
Example usage of GitHub Contributions Tracker with Bedrock integration
"""

import os
import sys
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from github_contributions_tracker import GitHubContributionsTracker, BedrockSummarizer

def example_basic_usage():
    """Example of basic usage without Bedrock."""
    print("=== Basic Usage Example ===")
    
    # Set up dates for last week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        # Initialize tracker
        tracker = GitHubContributionsTracker()
        
        # Get contributions
        contributions = tracker.get_contributions(start_date, end_date, include_private=False)
        
        # Generate regular summary
        summary = tracker.generate_summary(contributions, 'markdown')
        print("Regular summary generated successfully!")
        
        return contributions
        
    except Exception as e:
        print(f"Error in basic usage: {e}")
        return None

def example_bedrock_summarization(contributions):
    """Example of using Bedrock for AI-powered summarization."""
    print("\n=== Bedrock Summarization Example ===")
    
    if not contributions:
        print("No contributions to summarize")
        return
    
    try:
        # Initialize tracker
        tracker = GitHubContributionsTracker()
        
        # Generate AI-powered summary
        ai_summary = tracker.generate_bedrock_summary(contributions)
        
        print("AI-powered summary generated successfully!")
        print("\n" + "="*60)
        print("AI-GENERATED SUMMARY:")
        print("="*60)
        print(ai_summary)
        print("="*60)
        
        return ai_summary
        
    except Exception as e:
        print(f"Error in Bedrock summarization: {e}")
        print("Make sure you have AWS credentials configured:")
        print("  aws configure")
        return None

def example_direct_bedrock_usage():
    """Example of using Bedrock summarizer directly."""
    print("\n=== Direct Bedrock Usage Example ===")
    
    # Sample contributions data
    sample_data = """
# GitHub Contributions Summary

## Overview
- **Total Commits**: 5
- **Repositories with Contributions**: 2

## Commits
- **backend-api**: Implement user authentication system (a1b2c3d)
- **backend-api**: Add database migration scripts (e4f5g6h)
- **frontend-app**: Create login page UI (i7j8k9l)
- **frontend-app**: Add form validation (m1n2o3p)
- **backend-api**: Update API documentation (q4r5s6t)

## Repositories with Contributions
- **backend-api** (🌐 Public)
- **frontend-app** (🌐 Public)
"""
    
    try:
        # Initialize Bedrock summarizer directly
        summarizer = BedrockSummarizer()
        
        # Generate summary
        summary = summarizer.summarize_contributions(sample_data)
        
        print("Direct Bedrock usage successful!")
        print("\n" + "="*60)
        print("DIRECT BEDROCK SUMMARY:")
        print("="*60)
        print(summary)
        print("="*60)
        
        return summary
        
    except Exception as e:
        print(f"Error in direct Bedrock usage: {e}")
        return None

def example_custom_bedrock_model():
    """Example of using a different Bedrock model."""
    print("\n=== Custom Bedrock Model Example ===")
    
    # Sample data
    sample_data = """
# GitHub Contributions Summary

## Overview
- **Total Commits**: 3
- **Repositories with Contributions**: 1

## Commits
- **data-pipeline**: Optimize ETL process performance (a1b2c3d)
- **data-pipeline**: Add data validation checks (e4f5g6h)
- **data-pipeline**: Implement error handling and logging (i7j8k9l)

## Repositories with Contributions
- **data-pipeline** (🌐 Public)
"""
    
    try:
        # Use a different model (Haiku for faster processing)
        summarizer = BedrockSummarizer(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region="us-east-1"
        )
        
        # Generate summary
        summary = summarizer.summarize_contributions(sample_data)
        
        print("Custom Bedrock model usage successful!")
        print("\n" + "="*60)
        print("CUSTOM MODEL SUMMARY:")
        print("="*60)
        print(summary)
        print("="*60)
        
        return summary
        
    except Exception as e:
        print(f"Error in custom Bedrock model usage: {e}")
        return None

def main():
    """Run all examples."""
    print("GitHub Contributions Tracker - Bedrock Integration Examples")
    print("=" * 70)
    
    # Check if GitHub token is available
    if not os.getenv('GITHUB_TOKEN'):
        print("Warning: GITHUB_TOKEN environment variable not set.")
        print("Some examples may not work without a GitHub token.")
        print()
    
    # Run examples
    contributions = example_basic_usage()
    example_bedrock_summarization(contributions)
    example_direct_bedrock_usage()
    example_custom_bedrock_model()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("\nTo run the full script with Bedrock:")
    print("python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock")

if __name__ == "__main__":
    main() 
