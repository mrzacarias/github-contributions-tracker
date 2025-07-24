# Contributing to GitHub Contributions Tracker

Thank you for your interest in contributing to GitHub Contributions Tracker! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please create an issue on GitHub:

1. Check if the issue has already been reported
2. Use the appropriate issue template
3. Provide detailed information about the problem
4. Include steps to reproduce the issue

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes with a descriptive message
7. Push to your fork and submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Add comments for complex logic

### Testing

- Run existing tests: `python -m pytest tests/`
- Add tests for new features
- Ensure tests cover edge cases
- Test with different Python versions if possible

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mrzacarias/github-contributions-tracker.git
   cd github-contributions-tracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   export GITHUB_TOKEN="your_github_token"
   export AWS_ACCESS_KEY_ID="your_aws_key"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret"
   ```

## Areas for Contribution

- **Performance improvements**: Optimize API calls and data processing
- **New features**: Add support for additional GitHub APIs
- **Documentation**: Improve README, add examples, create tutorials
- **Testing**: Add more comprehensive test coverage
- **Bug fixes**: Fix reported issues and edge cases
- **UI/UX**: Improve command-line interface and output formatting

## Questions?

If you have questions about contributing, feel free to:

- Open an issue for discussion
- Check the existing documentation
- Review the code and examples

Thank you for contributing to GitHub Contributions Tracker! 
