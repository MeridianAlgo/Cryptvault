#!/usr/bin/env python3
"""
CryptVault Desktop Charts Launcher
Launch the advanced desktop charting platform
"""

import sys
import os
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'matplotlib',
        'tkinter',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            if package == 'tkinter':
                print(f"   • {package} (usually comes with Python)")
            else:
                print(f"   • {package}")
        
        print("\n💡 Install missing packages:")
        for package in missing_packages:
            if package != 'tkinter':
                print(f"   pip install {package}")
        
        if 'tkinter' in missing_packages:
            print("\n   For tkinter:")
            print("   • Windows: Usually included with Python")
            print("   • Ubuntu/Debian: sudo apt-get install python3-tk")
            print("   • macOS: Usually included with Python")
        
        return False
    
    return True

def launch_desktop_charts():
    """Launch the desktop charting application"""
    print("🚀 Launching CryptVault Desktop Charts...")
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Cannot launch - missing requirements")
        return False
    
    try:
        # Import and run the desktop charts
        from cryptvault.visualization.desktop_charts import CryptVaultDesktopCharts
        
        print("✅ Starting desktop application...")
        app = CryptVaultDesktopCharts()
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error launching desktop charts: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎯 CryptVault Desktop Charts Launcher")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Launch application
    success = launch_desktop_charts()
    
    if success:
        print("\n✅ Desktop charts launched successfully!")
    else:
        print("\n❌ Failed to launch desktop charts")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure all requirements are installed")
        print("   2. Run from the project root directory")
        print("   3. Check that CryptVault is properly installed")

if __name__ == "__main__":
    main()