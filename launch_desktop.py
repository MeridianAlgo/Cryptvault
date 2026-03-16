#!/usr/bin/env python3
"""
Quick launcher for the CryptVault desktop application.
Double-click this file or run: python launch_desktop.py
"""
import sys
import os

# Ensure package is importable from this directory
sys.path.insert(0, os.path.dirname(__file__))

from cryptvault.desktop import launch_app

if __name__ == "__main__":
    launch_app()
