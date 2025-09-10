"""
JavaScript Development Environment Setup Tool

Behavior:
- When run as a bundled EXE dropped into any folder, it sets up a complete JavaScript
  development environment on a clean Windows PC.
- When run as a script via Python, it performs the same setup from the current directory.

Tools Installed:
- NVM for Windows (Node Version Manager)
- Node.js LTS (via NVM)
- npm (comes with Node.js)
- Git for Windows
- Visual Studio Code (with basic settings configured)
- Chrome Browser (for development/debugging)
- Windows Terminal (modern terminal experience)

Dependencies:
- urllib.request (built-in) for downloading installers
- subprocess (built-in) for running installers
- winreg (built-in) for Windows registry operations

Notes:
- Requires administrator privileges for software installation
- Downloads installers to a temporary "downloads" folder
- Automatically adds tools to PATH where needed
- Configures VS Code with recommended settings (no extensions installed)
- If double-clicking the EXE, a prompt at the end will keep the console open
- Detects existing installations to avoid duplicates
"""

from __future__ import annotations

import sys
import os
import subprocess
import urllib.request
import winreg
from pathlib import Path
from datetime import datetime
import tempfile
import json
import shutil
import argparse


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # Use the executable's directory when running as a bundled EXE so output
    # (reports/downloads) is written next to the EXE; otherwise use current working dir.
    if is_frozen():
        try:
            return Path(sys.executable).resolve().parent
        except Exception:
            return Path.cwd()
    return Path.cwd()


def check_admin_privileges() -> bool:
    """Check if running with administrator privileges."""
    try:
        # Try to access a system directory that requires admin rights
        test_path = Path("C:\\Windows\\System32\\config")
        list(test_path.iterdir())
        return True
    except (PermissionError, OSError):
        return False


def is_in_path(program: str) -> bool:
    """Check if a program is available in PATH."""
    try:
        result = subprocess.run(
            ["where", program],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def check_registry_program(key_path: str, program_name: str) -> bool:
    """Check if a program is installed by looking in Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    if program_name.lower() in subkey_name.lower():
                        return True
                    i += 1
                except OSError:
                    break
        return False
    except FileNotFoundError:
        return False


def check_nvm_installed() -> bool:
    """Check if NVM for Windows is installed."""
    nvm_path = Path(os.path.expandvars("%APPDATA%\\nvm"))
    return nvm_path.exists() or is_in_path("nvm")


def check_node_installed() -> bool:
    """Check if Node.js is installed."""
    return is_in_path("node")


def check_git_installed() -> bool:
    """Check if Git is installed."""
    return is_in_path("git")


def check_vscode_installed() -> bool:
    """Check if Visual Studio Code is installed."""
    return (is_in_path("code") or 
            check_registry_program("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall", "Visual Studio Code"))


def check_chrome_installed() -> bool:
    """Check if Google Chrome is installed."""
    chrome_paths = [
        Path("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"),
        Path("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"),
        Path(os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"))
    ]
    return any(path.exists() for path in chrome_paths)


def check_windows_terminal_installed() -> bool:
    """Check if Windows Terminal is installed."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-AppxPackage Microsoft.WindowsTerminal"],
            capture_output=True,
            text=True,
            check=True
        )
        return "Microsoft.WindowsTerminal" in result.stdout
    except subprocess.CalledProcessError:
        return False


def download_file(url: str, dest_path: Path, description: str) -> bool:
    """Download a file with progress indication."""
    try:
        print(f"  📥 Downloading {description}...")
        urllib.request.urlretrieve(url, dest_path)
        return dest_path.exists()
    except Exception as e:
        print(f"  ❌ Failed to download {description}: {e}")
        return False


def run_installer(installer_path: Path, args: list = None, description: str = "") -> bool:
    """Run an installer with optional arguments."""
    if args is None:
        args = []
    
    try:
        print(f"  🔧 Installing {description}...")
        cmd = [str(installer_path)] + args
        result = subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Installation failed for {description}: {e}")
        return False


def install_nvm() -> bool:
    """Install NVM for Windows."""
    print("📦 Installing NVM for Windows...")
    
    downloads_dir = get_base_dir() / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Download NVM for Windows installer
    nvm_url = "https://github.com/coreybutler/nvm-windows/releases/latest/download/nvm-setup.exe"
    nvm_installer = downloads_dir / "nvm-setup.exe"
    
    if not download_file(nvm_url, nvm_installer, "NVM for Windows"):
        return False
    
    # Install NVM silently
    success = run_installer(nvm_installer, ["/S"], "NVM for Windows")
    
    if success:
        print("  ✅ NVM for Windows installed successfully!")
        print("  ℹ️  You may need to restart your terminal/command prompt")
    
    return success


def install_node_via_nvm() -> bool:
    """Install Node.js LTS via NVM."""
    print("📦 Installing Node.js LTS via NVM...")
    
    try:
        # Refresh environment to pick up NVM
        nvm_path = Path(os.path.expandvars("%APPDATA%\\nvm\\nvm.exe"))
        if not nvm_path.exists():
            nvm_path = Path("C:\\Program Files\\nvm\\nvm.exe")
        
        if not nvm_path.exists():
            print("  ❌ NVM not found. Please restart terminal and try again.")
            return False
        
        # Install latest LTS Node.js
        result = subprocess.run([str(nvm_path), "install", "lts"], check=True, capture_output=True, text=True)
        print("  ✅ Node.js LTS installed via NVM!")
        
        # Use the LTS version
        result = subprocess.run([str(nvm_path), "use", "lts"], check=True, capture_output=True, text=True)
        print("  ✅ Node.js LTS activated!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install Node.js via NVM: {e}")
        return False


def install_git() -> bool:
    """Install Git for Windows."""
    print("📦 Installing Git for Windows...")
    
    downloads_dir = get_base_dir() / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Download Git for Windows installer
    git_url = "https://github.com/git-for-windows/git/releases/latest/download/Git-2.42.0.2-64-bit.exe"
    git_installer = downloads_dir / "git-installer.exe"
    
    # Use a more reliable download URL
    git_url = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
    
    if not download_file(git_url, git_installer, "Git for Windows"):
        return False
    
    # Install Git with default settings
    git_args = [
        "/VERYSILENT",
        "/NORESTART",
        "/COMPONENTS=ext,ext\\shellhere,ext\\guihere,gitlfs,assoc,assoc_sh"
    ]
    
    success = run_installer(git_installer, git_args, "Git for Windows")
    
    if success:
        print("  ✅ Git for Windows installed successfully!")
    
    return success


def install_vscode() -> bool:
    """Install Visual Studio Code."""
    print("📦 Installing Visual Studio Code...")
    
    downloads_dir = get_base_dir() / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Download VS Code installer
    vscode_url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
    vscode_installer = downloads_dir / "vscode-installer.exe"
    
    if not download_file(vscode_url, vscode_installer, "Visual Studio Code"):
        return False
    
    # Install VS Code silently
    vscode_args = [
        "/VERYSILENT",
        "/NORESTART",
        "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath"
    ]
    
    success = run_installer(vscode_installer, vscode_args, "Visual Studio Code")
    
    if success:
        print("  ✅ Visual Studio Code installed successfully!")
    
    return success


def install_chrome() -> bool:
    """Install Google Chrome."""
    print("📦 Installing Google Chrome...")
    
    downloads_dir = get_base_dir() / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    # Download Chrome installer
    chrome_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
    chrome_installer = downloads_dir / "chrome-installer.exe"
    
    if not download_file(chrome_url, chrome_installer, "Google Chrome"):
        return False
    
    # Install Chrome silently
    success = run_installer(chrome_installer, ["/S"], "Google Chrome")
    
    if success:
        print("  ✅ Google Chrome installed successfully!")
    
    return success


def install_windows_terminal() -> bool:
    """Install Windows Terminal via Microsoft Store or direct download."""
    print("📦 Installing Windows Terminal...")
    
    try:
        # Try to install via PowerShell (requires Windows 10 1903+ or Windows 11)
        cmd = [
            "powershell", "-Command",
            "Start-Process ms-windows-store://pdp/?ProductId=9N0DX20HK701"
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        print("  ✅ Windows Terminal installation initiated via Microsoft Store!")
        print("  ℹ️  Please complete the installation in the Microsoft Store")
        return True
        
    except subprocess.CalledProcessError:
        print("  ⚠️  Could not open Microsoft Store. Windows Terminal may need manual installation.")
        return False


def create_vscode_settings() -> None:
    """Create recommended VS Code settings for JavaScript development."""
    try:
        vscode_dir = Path(os.path.expandvars("%APPDATA%\\Code\\User"))
        vscode_dir.mkdir(parents=True, exist_ok=True)
        
        settings_file = vscode_dir / "settings.json"
        
        recommended_settings = {
            "editor.fontSize": 14,
            "editor.tabSize": 2,
            "editor.insertSpaces": True,
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": True
            },
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000,
            "terminal.integrated.defaultProfile.windows": "PowerShell",
            "git.autofetch": True,
            "extensions.autoUpdate": True
        }
        
        if settings_file.exists():
            # Merge with existing settings
            try:
                with open(settings_file, 'r') as f:
                    existing_settings = json.load(f)
                existing_settings.update(recommended_settings)
                recommended_settings = existing_settings
            except (json.JSONDecodeError, IOError):
                pass
        
        with open(settings_file, 'w') as f:
            json.dump(recommended_settings, f, indent=2)
        
        print("  ✅ VS Code settings configured for JavaScript development!")
        
    except Exception as e:
        print(f"  ⚠️  Could not configure VS Code settings: {e}")





def main() -> int:
    base_dir = get_base_dir()
    
    parser = argparse.ArgumentParser(description="JS Dev setup tool")
    parser.add_argument('--dry-run', action='store_true', help='Simulate the setup without downloading or installing')
    args = parser.parse_args()
    dry_run = args.dry_run
    
    print("🚀 JavaScript Development Environment Setup")
    print(f"Working directory: {base_dir}")
    print("=" * 60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ Error: This tool only works on Windows systems.")
        if is_frozen():
            input("Press Enter to close...")
        return 1
    
    # Check for administrator privileges
    is_admin = check_admin_privileges()
    insufficient_privileges = False
    if not is_admin and not dry_run:
        print("⚠️  Warning: Administrator privileges not detected.")
        print("   The script cannot install software without elevation.")
        print("   A report will be generated showing what would have been done.")
        insufficient_privileges = True
    
    if dry_run:
        print("⚠️  Dry-run mode: No changes will be made, downloads and installers will be simulated.")
    elif not insufficient_privileges:
        print("✅ Running with administrator privileges")

    # Determine whether we can perform installations
    can_install = is_admin or dry_run

    # Check current installation status
    print("\n🔍 Checking current installation status...")
    
    tools_status = {
        "NVM": check_nvm_installed(),
        "Node.js": check_node_installed(),
        "Git": check_git_installed(),
        "VS Code": check_vscode_installed(),
        "Chrome": check_chrome_installed(),
        "Windows Terminal": check_windows_terminal_installed()
    }
    
    for tool, installed in tools_status.items():
        status = "✅ Installed" if installed else "❌ Not found"
        print(f"  {tool}: {status}")
    
    # Install missing tools
    print(f"\n🔧 Installing missing development tools...")
    
    downloads_dir = base_dir / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    
    installation_results = {}
    actions_log = []  # collect human readable actions for report
    
    # Install NVM first (required for Node.js)
    if not tools_status["NVM"]:
        if dry_run:
            msg = "(dry) Would download and run NVM installer"
            print(f"  {msg}")
            installation_results["NVM"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped NVM install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["NVM"] = False
            actions_log.append(msg)
        else:
            msg = "Downloading and installing NVM for Windows"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["NVM"] = install_nvm()
            actions_log.append(f"  Result: {'Success' if installation_results['NVM'] else 'Failed'}")
    else:
        msg = "NVM already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["NVM"] = True
        actions_log.append(msg)

    # Install Node.js via NVM
    if not tools_status["Node.js"]:
        if installation_results.get("NVM") is False and not dry_run:
            msg = "Skipped Node.js install (NVM missing or failed)"
            print(f"  {msg}")
            installation_results["Node.js"] = False
            actions_log.append(msg)
        elif dry_run:
            msg = "(dry) Would install Node.js LTS via NVM"
            print(f"  {msg}")
            installation_results["Node.js"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped Node.js install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["Node.js"] = False
            actions_log.append(msg)
        else:
            msg = "Installing Node.js LTS via NVM"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["Node.js"] = install_node_via_nvm()
            actions_log.append(f"  Result: {'Success' if installation_results['Node.js'] else 'Failed'}")
    else:
        msg = "Node.js already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["Node.js"] = True
        actions_log.append(msg)

    # Install Git
    if not tools_status["Git"]:
        if dry_run:
            msg = "(dry) Would download and install Git for Windows"
            print(f"  {msg}")
            installation_results["Git"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped Git install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["Git"] = False
            actions_log.append(msg)
        else:
            msg = "Downloading and installing Git for Windows"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["Git"] = install_git()
            actions_log.append(f"  Result: {'Success' if installation_results['Git'] else 'Failed'}")
    else:
        msg = "Git already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["Git"] = True
        actions_log.append(msg)

    # Install VS Code
    if not tools_status["VS Code"]:
        if dry_run:
            msg = "(dry) Would download and install Visual Studio Code"
            print(f"  {msg}")
            installation_results["VS Code"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped VS Code install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["VS Code"] = False
            actions_log.append(msg)
        else:
            msg = "Downloading and installing Visual Studio Code"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["VS Code"] = install_vscode()
            actions_log.append(f"  Result: {'Success' if installation_results['VS Code'] else 'Failed'}")
    else:
        msg = "VS Code already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["VS Code"] = True
        actions_log.append(msg)

    # Install Chrome
    if not tools_status["Chrome"]:
        if dry_run:
            msg = "(dry) Would download and install Google Chrome"
            print(f"  {msg}")
            installation_results["Chrome"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped Chrome install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["Chrome"] = False
            actions_log.append(msg)
        else:
            msg = "Downloading and installing Google Chrome"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["Chrome"] = install_chrome()
            actions_log.append(f"  Result: {'Success' if installation_results['Chrome'] else 'Failed'}")
    else:
        msg = "Chrome already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["Chrome"] = True
        actions_log.append(msg)

    # Install Windows Terminal
    if not tools_status["Windows Terminal"]:
        if dry_run:
            msg = "(dry) Would initiate Windows Terminal installation via Microsoft Store"
            print(f"  {msg}")
            installation_results["Windows Terminal"] = True
            actions_log.append(msg)
        elif not can_install:
            msg = "Skipped Windows Terminal install due to insufficient privileges"
            print(f"  {msg}")
            installation_results["Windows Terminal"] = False
            actions_log.append(msg)
        else:
            msg = "Initiating Windows Terminal installation via Microsoft Store"
            print(f"  {msg}...")
            actions_log.append(msg)
            installation_results["Windows Terminal"] = install_windows_terminal()
            actions_log.append(f"  Result: {'Success' if installation_results['Windows Terminal'] else 'Failed'}")
    else:
        msg = "Windows Terminal already installed, skipped"
        print(f"📦 {msg}...")
        installation_results["Windows Terminal"] = True
        actions_log.append(msg)
    
    # Configure VS Code if it was installed or already exists
    if installation_results.get("VS Code", tools_status["VS Code"]):
        print("\n⚙️  Configuring VS Code for JavaScript development...")
        if dry_run:
            msg = "(dry) Would create VS Code settings"
            print(f"  {msg}")
            actions_log.append(msg)
        else:
            msg = "Creating VS Code settings"
            print(f"  {msg}...")
            actions_log.append(msg)
            try:
                create_vscode_settings()
                actions_log.append("  Result: VS Code configured")
            except Exception as e:
                actions_log.append(f"  Error configuring VS Code: {e}")
                print(f"  ⚠️  Error during VS Code configuration: {e}")
    
    # Clean up downloads
    try:
        if not dry_run:
            shutil.rmtree(downloads_dir)
            print(f"\n🧹 Cleaned up download files")
            actions_log.append("Cleaned up downloads folder")
        else:
            print(f"\n(dry) Would remove downloads folder: {downloads_dir}")
            actions_log.append(f"(dry) Would remove downloads folder: {downloads_dir}")
    except Exception:
        pass
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 60)
    
    all_success = True
    for tool, success in installation_results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {tool}: {status}")
        if not success:
            all_success = False
    
    # Write report to file
    try:
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = base_dir / f"js_dev_setup_report_{report_timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as rf:
            rf.write(f"JavaScript Dev Setup Report - {report_timestamp}\n")
            rf.write("\nDetected tool status:\n")
            for tool, installed in tools_status.items():
                rf.write(f"  {tool}: {'Installed' if installed else 'Not found'}\n")
            rf.write("\nActions performed:\n")
            for line in actions_log:
                rf.write(f"  {line}\n")
            rf.write("\nSummary:\n")
            for tool, success in installation_results.items():
                rf.write(f"  {tool}: {'Success' if success else 'Failed'}\n")
            rf.write(f"\nDry-run: {dry_run}\n")
        
        print(f"\n📝 Report written: {report_file}")
    except Exception as e:
        print(f"Could not write report file: {e}")
    
    if all_success:
        print("\n🎉 JavaScript development environment setup complete! (dry-run)" if dry_run else "\n🎉 JavaScript development environment setup complete!")
        print("\n💡 Next steps:")
        print("   1. Restart your terminal/command prompt")
        print("   2. Verify Node.js: nvm list")
        print("   3. Create a new project: mkdir my-project && cd my-project")
        print("   4. Initialize project: npm init -y")
        print("   5. Open in VS Code: code .")
        
        print("\n🛠️  Available tools:")
        print("   • NVM: nvm install <version>, nvm use <version>")
        print("   • Node.js & npm: node --version, npm --version")
        print("   • Git: git --version")
        print("   • VS Code: code <folder>")
        print("   • Package managers: npm, npx")
    else:
        print("\n⚠️  Some installations failed. Please check error messages above.")
        print("   You may need to install failed components manually.")
    
    if is_frozen():
        print("\n" + "="*60)
        input("Press Enter to close...")
    
    return 0 if all_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
