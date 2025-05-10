#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="pulp-fiction-generator",
    version="0.1.0",
    description="Generate pulp fiction stories using AI agents",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "crewai>=0.119.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.4.2",
        "aiohttp>=3.8.5",
        "httpx>=0.24.1",
        "rich>=13.6.0",
        "typer>=0.9.0",
        "markdown>=3.5",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "pulp-fiction=pulp_fiction_generator.__main__:app",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 