#!/usr/bin/env python3
"""
CryptVault Setup Script
Advanced AI-Powered Cryptocurrency Analysis Platform
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="cryptvault",
    version="3.2.4",
    author="MeridianAlgo Algorithmic Research Team (Quantum Meridian)",
    author_email="support@meridianalgo.com",
    description="Advanced AI-Powered Cryptocurrency Analysis Platform with 50+ Patterns & ML Ensemble",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MeridianAlgo/CryptVault",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "ml": [
            "torch>=1.12.0",
            "tensorflow>=2.8.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
            "isort>=5.0.0",
        ],
        "full": [
            "torch>=1.12.0",
            "fastquant>=1.0.0",
            "websockets>=10.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cryptvault=cryptvault:main",
        ],
    },
    keywords=[
        "cryptocurrency",
        "bitcoin",
        "ethereum",
        "trading",
        "analysis",
        "machine learning",
        "AI",
        "technical analysis",
        "chart patterns",
        "LSTM",
        "ensemble models",
        "fintech",
        "tradingview",
        "patterns",
        "forecasting",
    ],
    project_urls={
        "Bug Reports": "https://github.com/MeridianAlgo/CryptVault/issues",
        "Source": "https://github.com/MeridianAlgo/CryptVault",
        "Documentation": "https://github.com/MeridianAlgo/CryptVault/wiki",
        "Changelog": "https://github.com/MeridianAlgo/CryptVault/releases",
        "Homepage": "https://meridianalgo.com",
    },
    include_package_data=True,
    zip_safe=False,
)