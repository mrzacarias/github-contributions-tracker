# GitHub Contributions Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/github-contributions-tracker.svg)](https://badge.fury.io/py/github-contributions-tracker)

A Python script to track your GitHub contributions for a specified time range and generate comprehensive summaries with AI-powered insights using Amazon Bedrock.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install github-contributions-tracker

# Or clone and install locally
git clone https://github.com/mrzacarias/github-contributions-tracker.git
cd github-contributions-tracker
pip install -r requirements.txt

# Basic usage
github-contributions -s 2024-01-01 -e 2024-01-31

# With AI-powered summary
github-contributions -s 2024-01-01 -e 2024-01-31 --bedrock
```

## Features

- 📊 Track commits, pull requests, issues, and reviews
- 📅 Filter by custom date ranges
- 📝 Generate formatted markdown summaries
- 🤖 AI-powered summarization using Amazon Bedrock
- 🔒 Option to include/exclude private repositories
- 💾 Save summaries to files or print to console
- 🎯 Focus on your own contributions only

## 📦 Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install github-contributions-tracker
```

### Option 2: Install from Source

```bash
git clone https://github.com/mrzacarias/github-contributions-tracker.git
cd github-contributions-tracker
pip install -r requirements.txt
```

### 2. Get GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following scopes:
   - `repo` (for private repositories)
   - `read:user`
   - `read:org` (if you want to include organization repositories)

### 3. Set Environment Variable (Optional)

```bash
export GITHUB_TOKEN="your_github_token_here"
```

### 4. AWS Bedrock Setup (Optional - for AI summarization)

To use the AI-powered summarization feature, you need AWS credentials configured:

```bash
# Install AWS CLI and configure credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Usage

### Basic Usage

```bash
python github_contributions.py --start-date 2024-01-01 --end-date 2024-01-31
```

### Advanced Usage

```bash
# Include private repositories
python github_contributions.py -s 2024-01-01 -e 2024-01-31 -p

# Save to specific file
python github_contributions.py -s 2024-01-01 -e 2024-01-31 -o my_contributions.md

# Print to console only
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --print-only

# Use custom token
python github_contributions.py -s 2024-01-01 -e 2024-01-31 -t your_token_here

# Track specific user
python github_contributions.py -s 2024-01-01 -e 2024-01-31 -u octocat

# Plain text output
python github_contributions.py -s 2024-01-01 -e 2024-01-31 -f plain

# AI-powered summary using Amazon Bedrock
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock

# Use specific Bedrock model and region
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock --bedrock-model anthropic.claude-3-haiku-20240307-v1:0 --bedrock-region us-west-2
```

### Command Line Options

- `--start-date, -s`: Start date for contributions (required)
- `--end-date, -e`: End date for contributions (required)
- `--token, -t`: GitHub personal access token
- `--username, -u`: GitHub username to track (default: authenticated user)
- `--include-private, -p`: Include private repositories
- `--repos-only`: Show only repositories with contributions (no detailed breakdown)
- `--no-optimize`: Disable repository optimization (process all repositories)
- `--limit, -l`: Limit number of repositories to process (for testing)
- `--skip-reviews`: Skip pull request reviews (much faster)
- `--fast`: Fast mode: skip reviews and limit data per repo
- `--graphql`: Use GraphQL API for much faster data fetching
- `--bulk`: Use bulk search API for maximum efficiency (recommended)
- `--conservative`: Use conservative approach to avoid rate limits
- `--output, -o`: Output file name
- `--format, -f`: Output format: markdown or plain (default: markdown)
- `--print-only`: Print to console only, don't save to file
- `--bedrock`: Use Amazon Bedrock to generate an AI-powered summary of contributions
- `--bedrock-model`: Bedrock model ID to use for summarization (default: anthropic.claude-3-sonnet-20240229-v1:0)
- `--bedrock-region`: AWS region for Bedrock service (default: us-east-1)

### Date Formats

The script accepts various date formats:
- `2024-01-01`
- `2024/01/01`
- `Jan 1, 2024`
- `1st January 2024`

## AI-Powered Summarization

The script can use Amazon Bedrock to generate intelligent summaries of your contributions. This feature:

- **Analyzes patterns**: Identifies common themes and high-level tasks from your contributions
- **Groups related work**: Combines similar commits and activities into logical categories
- **Provides insights**: Offers a more strategic view of your work beyond just listing commits
- **Markdown output**: Generates clean, structured summaries in markdown format

### Usage

```bash
# Basic AI summarization
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock

# With custom model and region
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock \
  --bedrock-model anthropic.claude-3-haiku-20240307-v1:0 \
  --bedrock-region us-west-2
```

### Available Models

- `anthropic.claude-3-sonnet-20240229-v1:0` (default) - Balanced performance and quality
- `anthropic.claude-3-haiku-20240307-v1:0` - Fastest, good for quick summaries
- `anthropic.claude-3-opus-20240229-v1:0` - Highest quality, best for complex analysis
- `anthropic.claude-3-5-sonnet-20241022-v2:0` - Latest model with improved capabilities

## Output Formats

The script can generate output in three formats:

### AI-Powered Summary (Bedrock)

When using the `--bedrock` flag, the script generates an intelligent summary that:

- **Groups related work**: Combines similar commits into logical categories
- **Identifies patterns**: Recognizes common themes and high-level tasks
- **Provides insights**: Offers strategic analysis of your contributions
- **Clean structure**: Well-formatted markdown with clear sections

Example output:
```markdown
# GitHub Contributions Summary - High-Level Tasks

## Overview
- **Total Commits**: 15
- **Repositories with Contributions**: 3
- **Time Period**: Based on contributions from 2024-01-01 to 2024-01-31

## High-Level Tasks Completed

### 1. **Infrastructure & System Management**
- Fixed authentication issues in user management module
- Resolved database connection problems
- Updated dependency versions for security patches

### 2. **Feature Development & API Enhancement**
- Implemented new API endpoints for data processing
- Added user dashboard with analytics
- Created automated testing framework

### 3. **Code Quality & Documentation**
- Updated API documentation
- Refactored legacy code for better maintainability
- Added comprehensive unit tests

## Key Achievements
- **System Reliability**: Improved authentication and database stability
- **Feature Delivery**: Successfully implemented new API endpoints and user dashboard
- **Code Quality**: Enhanced maintainability through refactoring and testing

## Impact
- Enhanced system reliability and user experience
- Improved development workflow with better testing coverage
- Strengthened codebase maintainability and documentation
```

### Markdown Format (Default)

The script generates a markdown file with the following structure:

```markdown
# GitHub Contributions Summary

## Overview
- **Total Commits**: 15
- **Total Pull Requests**: 3
- **Total Issues**: 2
- **Total Reviews**: 5

## Commits
- **repo-name**: Fix bug in authentication module (a1b2c3d)
- **another-repo**: Add new feature for user management (e4f5g6h)

## Pull Requests
- **repo-name**: Implement new API endpoint (#123) - ✅ Merged
- **another-repo**: Update documentation (#124) - 🔄 Open

## Issues
- **repo-name**: Bug report for login issue (#125) - ✅ Closed

## Pull Request Reviews
- **repo-name**: Reviewed PR #126 - Add unit tests
```

### Plain Text Format

```
GITHUB CONTRIBUTIONS SUMMARY
========================================

OVERVIEW
----------
Total Commits: 15
Total Pull Requests: 3
Total Issues: 2
Total Reviews: 5

COMMITS
----------
- repo-name: Fix bug in authentication module (a1b2c3d)
- another-repo: Add new feature for user management (e4f5g6h)

PULL REQUESTS
---------------
- repo-name: Implement new API endpoint (#123) - MERGED
- another-repo: Update documentation (#124) - OPEN

ISSUES
--------
- repo-name: Bug report for login issue (#125) - CLOSED

PULL REQUEST REVIEWS
----------------------
- repo-name: Reviewed PR #126 - Add unit tests
```

## Performance Optimization

The script offers multiple optimization strategies:

### 1. **Bulk Search API (Recommended)**
- **Single API calls** for all commits, PRs, and issues
- **Maximum efficiency**: 50-100x faster than individual repo processing
- **Smart grouping**: Automatically groups contributions by repository
- **Use**: `--bulk` flag

### 2. **GraphQL API**
- **Batched queries**: Multiple repositories in single requests
- **Structured data**: More efficient than REST API
- **Use**: `--graphql` flag

### 3. **Conservative Approach**
- **Rate Limit Safe**: Processes data in weekly chunks to avoid rate limits
- **Gradual Processing**: Small delays between chunks to respect API limits
- **Fallback Friendly**: Automatically handles rate limit errors gracefully
- **Use**: `--conservative` flag

### 4. **Search API Optimization**
- **Smart Repository Filtering**: Uses GitHub search API to find only repositories with contributions
- **Reduced API Calls**: Processes only relevant repositories instead of all repositories
- **Fallback Mode**: Automatically falls back to processing all repositories if search API fails
- **Disable Optimization**: Use `--no-optimize` flag to process all repositories (original behavior)

## Repository Filtering

The script intelligently filters repositories to show only those where you actually made contributions:

- **Automatic Filtering**: Only repositories with commits, PRs, issues, or reviews are included
- **Repository List**: Shows a summary of all repositories with contributions
- **Visibility Indicators**: Displays whether each repository is public or private
- **Repos-Only Mode**: Use `--repos-only` flag to show only repository names without detailed breakdown

## User Detection

The script automatically detects which user's contributions to track:

1. **Default**: Uses the authenticated user from your GitHub token
2. **Custom User**: Use `--username` flag to track any public user's contributions
3. **Private Repos**: Only accessible for the authenticated user or users with appropriate permissions

## Examples

### Track Last Month's Contributions

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31
```

### Track This Week's Work

```bash
python github_contributions.py -s "2024-01-22" -e "2024-01-28"
```

### Generate Report for Q4 2023

```bash
python github_contributions.py -s "2023-10-01" -e "2023-12-31" -o q4_2023_contributions.md
```

### Show Only Repositories with Contributions

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --repos-only
```

### Plain Text Repositories Only

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --repos-only -f plain
```

### Disable Optimization (Process All Repositories)

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --no-optimize
```

### Fast Mode (Skip Reviews)

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --fast
```

### Skip Reviews Only

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --skip-reviews
```

### Bulk Search (Recommended - Fastest)

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bulk
```

### GraphQL API

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --graphql
```

### Conservative Approach (Rate Limit Safe)

```bash
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --conservative
```

### AI-Powered Summary

```bash
# Basic AI summarization
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock

# Fast AI summary with Haiku model
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock --bedrock-model anthropic.claude-3-haiku-20240307-v1:0

# High-quality analysis with Opus model
python github_contributions.py -s 2024-01-01 -e 2024-01-31 --bedrock --bedrock-model anthropic.claude-3-opus-20240229-v1:0
```

## Troubleshooting

### Common Issues

1. **"GitHub token is required"**
   - Set the `GITHUB_TOKEN` environment variable or use the `--token` flag

2. **"Invalid date format"**
   - Use standard date formats like `YYYY-MM-DD`

3. **"Start date must be before end date"**
   - Ensure your start date is earlier than your end date

4. **Rate limiting**
   - GitHub API has rate limits. The script handles this automatically, but for large repositories, it may take time

### Performance Notes

- **Bulk Search (Recommended)**: 50-100x faster than individual repository processing
- **GraphQL API**: 10-20x faster than REST API for multiple repositories
- **Search API Optimization**: 5-10x faster for users with many repositories
- **Sequential Processing**: Repositories are processed sequentially to avoid rate limiting
- **Fallback Safety**: Automatically falls back to processing all repositories if optimization fails
- **Data Limits**: Limits commits (50), PRs (20), issues (20), and reviews (10) per repository
- **Fast Mode**: Use `--fast` or `--skip-reviews` to skip slow review processing
- **Large Repositories**: May still take time for repositories with many commits
- **Date Range Impact**: Shorter date ranges generally process faster

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) for AI-powered summarization
- [Claude](https://www.anthropic.com/claude) for intelligent content analysis

## 📞 Support

- 📧 Create an [issue](https://github.com/mrzacarias/github-contributions-tracker/issues) for bugs or feature requests
- 📖 Check the [documentation](README.md) for usage examples
- 🔧 Review the [contributing guide](CONTRIBUTING.md) for development setup 
