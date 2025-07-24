#!/usr/bin/env python3
"""
Bedrock summarizer module for GitHub Contributions Tracker
"""

import json
import boto3


class BedrockSummarizer:
    """Summarize contributions using Amazon Bedrock."""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", 
                 region: str = "us-east-1", max_tokens: int = 2000):
        """
        Initialize the Bedrock summarizer.
        
        Args:
            model_id: Bedrock model ID to use
            region: AWS region for Bedrock
            max_tokens: Maximum tokens for response
        """
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
    
    def create_summary_prompt(self, contributions_list: str) -> str:
        """
        Create a prompt for summarizing contributions.
        
        Args:
            contributions_list: String containing the list of contributions
            
        Returns:
            Formatted prompt for Bedrock
        """
        prompt = f"""Hi, would you create a more succinct summary based on this list of contributions?

{contributions_list}

I would like a comprehensive summary that follows this exact format:

# GitHub Contributions Summary - High-Level Tasks

## Overview
- **Total Commits**: [number]
- **Repositories with Contributions**: [number]
- **Time Period**: Based on contributions from [date range]

## High-Level Tasks Completed

### 1. **[Category Name]**
- [Task description 1]
- [Task description 2]
- [Task description 3]

### 2. **[Category Name]**
- [Task description 1]
- [Task description 2]
- [Task description 3]

[Continue with more categories as needed...]

## Key Achievements
- **[Achievement 1]**: [description]
- **[Achievement 2]**: [description]
- **[Achievement 3]**: [description]

## Impact
- [Impact statement 1]
- [Impact statement 2]
- [Impact statement 3]

Please analyze the contributions and group them into logical high-level categories. Focus on the main themes and patterns in the work, not individual commits. Make it professional and strategic, highlighting the key accomplishments and their business impact."""
        
        return prompt
    
    def summarize_contributions(self, contributions_list: str) -> str:
        """
        Summarize contributions using Amazon Bedrock.
        
        Args:
            contributions_list: String containing the list of contributions
            
        Returns:
            Summarized contributions in markdown format
        """
        prompt = self.create_summary_prompt(contributions_list)
        
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response.get('body').read())
            summary = response_body['content'][0]['text'].strip()
            
            return summary
            
        except Exception as e:
            print(f"Error summarizing contributions with Bedrock: {e}")
            return f"Error generating summary: {e}\n\nOriginal contributions:\n{contributions_list}" 
