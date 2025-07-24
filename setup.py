#!/usr/bin/env python3
"""
Setup script for GitHub Contributions Tracker
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="github-contributions-tracker",
    version="1.0.0",
    author="GitHub Contributions Tracker",
    description="Track GitHub contributions and generate AI-powered summaries using Amazon Bedrock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrzacarias/github-contributions-tracker",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "github-contributions=github_contributions_tracker.cli:main",
        ],
    },
    keywords="github, contributions, tracking, bedrock, ai, summary",
    project_urls={
        "Bug Reports": "https://github.com/mrzacarias/github-contributions-tracker/issues",
        "Source": "https://github.com/mrzacarias/github-contributions-tracker",
    },
) 
