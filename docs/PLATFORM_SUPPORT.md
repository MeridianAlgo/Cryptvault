# Platform Support Guide

CryptVault is designed to work seamlessly across all major operating systems.

## Supported Platforms

### ✅ Ubuntu/Linux

**Tested on:**
- Ubuntu 20.04, 22.04, 24.04
- Debian 10, 11, 12
- Fedora 36+
- Arch Linux

**Installation:**
```bash
# Install Python 3.8+ if not already installed
sudo apt update
sudo apt install python3 python3-pip

# Clone and install
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip3 install -r requirements.txt

# Run
python3 cryptvault_cli.py --demo
```

### ✅ macOS

**Tested on:**
- macOS 11 (Big Sur)
- macOS 12 (Monterey)
- macOS 13 (Ventura)
- macOS 14 (Sonoma)

**Installation:**
```bash
# Install Python 3.8+ using Homebrew
brew install python@3.11

# Clone and install
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip3 install -r requirements.txt

# Run
python3 cryptvault_cli.py --demo
```

### ✅ Windows

**Tested on:**
- Windows 10 (21H2, 22H2)
- Windows 11

**Installation:**
```powershell
# Install Python 3.8+ from python.org or Microsoft Store

# Clone and install
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt

# Run
python cryptvault_cli.py --demo
```

## Python Version Support

| Python Version | Ubuntu | macOS | Windows | Status |
|----------------|--------|-------|---------|--------|
| 3.8            | ✅     | ✅    | ✅      | Supported |
| 3.9            | ✅     | ✅    | ✅      | Supported |
| 3.10           | ✅     | ✅    | ✅      | Supported |
| 3.11           | ✅     | ✅    | ✅      | Supported |
| 3.12           | ✅     | ✅    | ✅      | Supported |

## Platform-Specific Notes

### Linux
- **Terminal Colors**: Full support for ANSI colors
- **Performance**: Best performance on Linux
- **Dependencies**: All dependencies available via pip

### macOS
- **Terminal Colors**: Full support in Terminal.app and iTerm2
- **Performance**: Excellent performance
- **M1/M2 Chips**: Fully compatible with Apple Silicon

### Windows
- **Terminal Colors**: Full support in Windows Terminal, PowerShell, and CMD
- **Performance**: Good performance
- **Path Separators**: Automatically handled by Python

## Troubleshooting

### Linux Issues

**Issue: Permission denied**
```bash
# Solution: Use pip3 with --user flag
pip3 install --user -r requirements.txt
```

**Issue: Missing tkinter**
```bash
# Solution: Install python3-tk
sudo apt install python3-tk
```

### macOS Issues

**Issue: SSL certificate errors**
```bash
# Solution: Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

**Issue: Command not found**
```bash
# Solution: Add Python to PATH
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Windows Issues

**Issue: 'python' not recognized**
```powershell
# Solution: Add Python to PATH or use 'py' command
py cryptvault_cli.py --demo
```

**Issue: Module not found**
```powershell
# Solution: Ensure pip is up to date
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## CI/CD Testing

CryptVault is automatically tested on all platforms via GitHub Actions:

- **Ubuntu Latest**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **macOS Latest**: Python 3.8, 3.9, 3.10, 3.11, 3.12
- **Windows Latest**: Python 3.8, 3.9, 3.10, 3.11, 3.12

Total: 15 test configurations per commit

## Performance Comparison

| Platform | Analysis Speed | Chart Rendering | Memory Usage |
|----------|---------------|-----------------|--------------|
| Ubuntu   | 3.2s          | Instant         | ~150 MB      |
| macOS    | 3.3s          | Instant         | ~160 MB      |
| Windows  | 3.5s          | Instant         | ~170 MB      |

*Tested with BTC 60-day analysis on comparable hardware*

## Recommended Setup

### For Development
- **Ubuntu 22.04** or **macOS 13+** recommended
- Python 3.11 for best performance
- 4GB+ RAM
- SSD for faster data loading

### For Production
- Any supported platform
- Python 3.10+ recommended
- 2GB+ RAM
- Stable internet connection

## Getting Help

If you encounter platform-specific issues:

1. Check this guide first
2. Review [GitHub Issues](https://github.com/MeridianAlgo/Cryptvault/issues)
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Error message
   - Steps to reproduce

## Contributing

Help us improve platform support:
- Test on your platform
- Report compatibility issues
- Submit platform-specific fixes
- Update documentation

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
