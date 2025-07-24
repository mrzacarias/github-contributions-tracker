#!/usr/bin/env python3
"""
Command-line interface for GitHub Contributions Tracker
"""

import os
import sys
import argparse
from datetime import datetime, timezone
from dateutil import parser as date_parser

from .tracker import GitHubContributionsTracker


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    try:
        parsed_date = date_parser.parse(date_str)
        # Make sure the datetime is timezone-aware
        if parsed_date.tzinfo is None:
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        return parsed_date
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Track GitHub contributions for a time range')
    parser.add_argument('--start-date', '-s', required=True, type=parse_date,
                       help='Start date (YYYY-MM-DD or other formats)')
    parser.add_argument('--end-date', '-e', required=True, type=parse_date,
                       help='End date (YYYY-MM-DD or other formats)')
    parser.add_argument('--token', '-t', help='GitHub personal access token')
    parser.add_argument('--include-private', '-p', action='store_true',
                       help='Include private repositories')
    parser.add_argument('--repos-only', action='store_true',
                       help='Show only repositories with contributions (no detailed breakdown)')
    parser.add_argument('--no-optimize', action='store_true',
                       help='Disable repository optimization (process all repositories)')
    parser.add_argument('--limit', '-l', type=int, help='Limit number of repositories to process (for testing)')
    parser.add_argument('--skip-reviews', action='store_true', help='Skip pull request reviews (much faster)')
    parser.add_argument('--fast', action='store_true', help='Fast mode: skip reviews and limit data per repo')
    parser.add_argument('--graphql', action='store_true', help='Use GraphQL API for much faster data fetching')
    parser.add_argument('--bulk', action='store_true', help='Use bulk search API for maximum efficiency (recommended)')
    parser.add_argument('--conservative', action='store_true', help='Use conservative approach to avoid rate limits')
    parser.add_argument('--output', '-o', help='Output file name')
    parser.add_argument('--print-only', action='store_true',
                       help='Print to console only, don\'t save to file')
    parser.add_argument('--format', '-f', choices=['markdown', 'plain'], default='markdown',
                       help='Output format: markdown or plain text')
    parser.add_argument('--username', '-u', help='GitHub username to track (default: authenticated user)')
    parser.add_argument('--bedrock', action='store_true',
                       help='Use Amazon Bedrock to generate an AI-powered summary of contributions')
    parser.add_argument('--bedrock-model', default='anthropic.claude-3-sonnet-20240229-v1:0',
                       help='Bedrock model ID to use for summarization')
    parser.add_argument('--bedrock-region', default='us-east-1',
                       help='AWS region for Bedrock service')
    
    args = parser.parse_args()
    
    # Validate date range
    if args.start_date >= args.end_date:
        print("Error: Start date must be before end date")
        sys.exit(1)
    
    try:
        # Initialize tracker
        tracker = GitHubContributionsTracker(args.token, args.username)
        
        print(f"Fetching contributions from {args.start_date.date()} to {args.end_date.date()}...")
        
        # Apply fast mode settings
        skip_reviews = args.skip_reviews or args.fast
        
        # Get contributions
        contributions = tracker.get_contributions(
            args.start_date, 
            args.end_date, 
            args.include_private,
            optimize=not args.no_optimize,
            limit=args.limit,
            skip_reviews=skip_reviews,
            use_graphql=args.graphql,
            use_bulk=args.bulk,
            use_conservative=args.conservative
        )
        
        # Generate summary
        if args.bedrock:
            # Use Bedrock for AI-powered summarization
            summary = tracker.generate_bedrock_summary(
                contributions, 
                model_id=args.bedrock_model,
                region=args.bedrock_region
            )
        elif args.repos_only:
            summary = tracker.generate_repos_only_summary(contributions, args.format)
        else:
            summary = tracker.generate_summary(contributions, args.format)
        
        # Output
        if args.print_only:
            print(summary)
        else:
            tracker.save_summary(summary, args.output)
            print("\n" + summary)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
