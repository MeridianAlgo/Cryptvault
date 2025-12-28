#!/usr/bin/env python3
"""
CryptVault Setup Script
Advanced AI-Powered Cryptocurrency Analysis Platform

This setup.py is maintained for backward compatibility.
Modern installations should use pyproject.toml with pip >= 21.0.

Installation:
pip install .
pip install -e . # Development mode
pip install cryptvault[ml] # With optional ML features
pip install cryptvault[full] # With all optional features
"""

from setuptools import setup, find_packages
import os
import sys

# Minimum Python version check
if sys.version_info < (3, 8):
sys.exit("CryptVault requires Python 3.8 or higher")


def read_file(filename):
"""Read a file and return its contents."""
filepath = os.path.join(os.path.dirname(__file__), filename)
if os.path.exists(filepath):
with open(filepath, "r", encoding="utf-8") as fh:
return fh.read()
return ""


def read_requirements(filename):
"""
Read requirements from a file, filtering out comments and empty lines.

Args:
filename: Path to requirements file

Returns:
List of requirement strings
"""
requirements = []
filepath = os.path.join(os.path.dirname(__file__), filename)

if not os.path.exists(filepath):
return requirements

with open(filepath, "r", encoding="utf-8") as fh:
for line in fh:
line = line.strip()
# Skip comments, empty lines, and -r includes
if line and not line.startswith("#") and not line.startswith("-r"):
requirements.append(line)

return requirements


def get_version():
"""Get version from __version__.py file."""
version_file = os.path.join(
os.path.dirname(__file__), "cryptvault", "__version__.py"
)

if os.path.exists(version_file):
version_dict = {}
with open(version_file, "r", encoding="utf-8") as fh:
exec(fh.read(), version_dict)
return version_dict.get("__version__", "4.0.0")

return "4.0.0"


# Read long description from README
long_description = read_file("README.md")

# Read base requirements
install_requires = read_requirements("requirements/base.txt")

# Define optional dependencies (extras)
extras_require = {
# Machine learning features (LSTM neural networks)
"ml": [
"torch>=1.12.0,<3.0.0",
],
# Advanced visualization (interactive charts)
"viz": [
"plotly>=5.0.0,<6.0.0",
"dash>=2.0.0,<3.0.0",
],
# Real-time data streaming
"streaming": [
"websockets>=10.0,<13.0",
],
# Performance optimizations
"fast": [
"numba>=0.55.0,<1.0.0",
],
# Database support
"db": [
"sqlalchemy>=1.4.0,<3.0.0",
"redis>=4.0.0,<6.0.0",
],
# Export formats
"export": [
"openpyxl>=3.0.0,<4.0.0",
"jinja2>=3.0.0,<4.0.0",
],
# Notification services
"notify": [
"requests>=2.25.0,<3.0.0",
],
# Development dependencies
"dev": read_requirements("requirements/dev.txt"),
# Testing dependencies
"test": read_requirements("requirements/test.txt"),
}

# Add 'full' extra that includes all optional features
extras_require["full"] = list(set(
extras_require["ml"] +
extras_require["viz"] +
extras_require["streaming"] +
extras_require["fast"] +
extras_require["db"] +
extras_require["export"] +
extras_require["notify"]
))

setup(
name="cryptvault",
version=get_version(),
author="MeridianAlgo Algorithmic Research Team (Quantum Meridian)",
author_email="support@meridianalgo.com",
description="Advanced AI-Powered Cryptocurrency Analysis Platform with 50+ Patterns & ML Ensemble",
long_description=long_description,
long_description_content_type="text/markdown",
url="https://github.com/MeridianAlgo/CryptVault",
project_urls={
"Homepage": "https://meridianalgo.com",
"Documentation": "https://github.com/MeridianAlgo/CryptVault/wiki",
"Repository": "https://github.com/MeridianAlgo/CryptVault",
"Bug Reports": "https://github.com/MeridianAlgo/CryptVault/issues",
"Changelog": "https://github.com/MeridianAlgo/CryptVault/releases",
"Source Code": "https://github.com/MeridianAlgo/CryptVault",
},
packages=find_packages(
where=".",
include=["cryptvault*"],
exclude=["tests*", "docs*", "examples*", "scripts*"]
),
classifiers=[
"Development Status :: 5 - Production/Stable",
"Intended Audience :: Financial and Insurance Industry",
"Intended Audience :: Developers",
"Intended Audience :: End Users/Desktop",
"Intended Audience :: Science/Research",
"Topic :: Office/Business :: Financial :: Investment",
"Topic :: Scientific/Engineering :: Artificial Intelligence",
"Topic :: Scientific/Engineering :: Information Analysis",
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
"Natural Language :: English",
"Typing :: Typed",
],
keywords=[
"cryptocurrency",
"bitcoin",
"ethereum",
"trading",
"analysis",
"machine-learning",
"AI",
"technical-analysis",
"chart-patterns",
"LSTM",
"ensemble-models",
"fintech",
"tradingview",
"patterns",
"forecasting",
"stocks",
"finance",
],
python_requires=">=3.8",
install_requires=install_requires,
extras_require=extras_require,
entry_points={
"console_scripts": [
"cryptvault=cryptvault_cli:main",
],
},
package_data={
"cryptvault": ["py.typed", "*.yaml", "*.yml", "*.json"],
},
include_package_data=True,
zip_safe=False,
)