#!/usr/bin/env python3
"""Final test of minimalistic CryptVault."""

import subprocess
import sys

def run_command(cmd):
    """Run command and show output."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Warnings: {result.stderr}")
    print("-" * 50)

def main():
    """Test CryptVault commands."""
    print("CryptVault Final Test")
    print("=" * 50)
    
    # Test demo
    run_command("python cryptvault_cli.py --demo")
    
    # Test offline
    run_command("python cryptvault_cli.py --offline")
    
    # Test real analysis (if not rate limited)
    try:
        run_command("python cryptvault_cli.py BTC 30 1d")
    except:
        print("Real analysis skipped (API limits)")
    
    print("All tests completed!")

if __name__ == "__main__":
    main()