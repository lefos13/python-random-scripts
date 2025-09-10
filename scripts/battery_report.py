"""
Battery Health Report Generator

Behavior:
- When run as a bundled EXE dropped into any folder, it generates a battery health report
  in that folder and opens it for review.
- When run as a script via Python, it generates the report in the current working directory.

Output:
- Creates "Battery_Report_YYYYMMDD_HHMMSS.html" in the current directory
- Automatically opens the report in the default web browser
- Uses Windows powercfg utility to generate comprehensive battery information

Dependencies:
- subprocess (built-in) for running powercfg
- webbrowser (built-in) for opening HTML report
- datetime (built-in) for timestamping

Notes:
- Only works on Windows systems with battery (laptops, tablets)
- Requires administrator privileges for full report details
- If double-clicking the EXE, a prompt at the end will keep the console open
- Report includes battery design capacity, current capacity, cycle count, and usage patterns
"""

from __future__ import annotations

import sys
import os
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import tempfile


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_base_dir() -> Path:
    # Always use the current working directory
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


def generate_battery_report(output_path: Path) -> bool:
    """Generate battery report using powercfg."""
    try:
        # Run powercfg to generate battery report
        cmd = ["powercfg", "/batteryreport", "/output", str(output_path)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return output_path.exists()
        
    except subprocess.CalledProcessError as e:
        print(f"Error running powercfg: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: powercfg command not found. This tool only works on Windows.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def enhance_html_report(report_path: Path) -> None:
    """Add some basic styling and additional information to the HTML report."""
    try:
        # Read the original report
        content = report_path.read_text(encoding='utf-8')
        
        # Add custom styling and header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enhanced_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Battery Health Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .content {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        h1, h2, h3 {{
            color: #333;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔋 Battery Health Report</h1>
        <p>Generated on {timestamp}</p>
    </div>
    <div class="content">
"""
        
        # Find where the original content starts (after any existing head/body tags)
        if '<body>' in content:
            original_body = content.split('<body>', 1)[1]
            if '</body>' in original_body:
                original_body = original_body.rsplit('</body>', 1)[0]
        else:
            # If no body tags, use the entire content
            original_body = content
        
        # Add the original content and footer
        enhanced_content += original_body
        enhanced_content += """
    </div>
    <div class="footer">
        <p>Report generated using Windows PowerCfg utility</p>
        <p>💡 For best battery health: avoid extreme temperatures, don't let battery fully discharge frequently</p>
    </div>
</body>
</html>
"""
        
        # Write the enhanced content back
        report_path.write_text(enhanced_content, encoding='utf-8')
        
    except Exception as e:
        print(f"Warning: Could not enhance HTML report: {e}")
        # Continue anyway with the original report


def open_report_in_browser(report_path: Path) -> None:
    """Open the battery report in the default web browser."""
    try:
        webbrowser.open(f"file://{report_path.absolute()}")
        print(f"Report opened in your default web browser")
    except Exception as e:
        print(f"Could not open report automatically: {e}")
        print(f"Please manually open: {report_path}")


def main() -> int:
    base_dir = get_base_dir()
    
    print("🔋 Battery Health Report Generator")
    print(f"Working directory: {base_dir}")
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("❌ Error: This tool only works on Windows systems.")
        if is_frozen():
            input("Press Enter to close...")
        return 1
    
    # Check for administrator privileges
    is_admin = check_admin_privileges()
    if not is_admin:
        print("⚠️  Warning: Not running as administrator.")
        print("   Some detailed battery information may not be available.")
        print("   For complete report, right-click the EXE and 'Run as administrator'")
    else:
        print("✅ Running with administrator privileges - full report available")
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"Battery_Report_{timestamp}.html"
    report_path = base_dir / report_filename
    
    print(f"\n🔄 Generating battery report...")
    print(f"   Output: {report_filename}")
    
    # Generate the battery report
    success = generate_battery_report(report_path)
    
    if not success:
        print("❌ Failed to generate battery report.")
        print("\nPossible reasons:")
        print("   • No battery detected (desktop computer)")
        print("   • PowerCfg service not available")
        print("   • Insufficient permissions")
        
        if is_frozen():
            input("Press Enter to close...")
        return 1
    
    print("✅ Battery report generated successfully!")
    
    # Enhance the HTML report with better styling
    print("🎨 Enhancing report appearance...")
    enhance_html_report(report_path)
    
    # Get file size
    file_size_kb = report_path.stat().st_size / 1024
    print(f"📄 Report size: {file_size_kb:.1f} KB")
    
    # Open in browser
    print("🌐 Opening report in web browser...")
    open_report_in_browser(report_path)
    
    print(f"\n📊 Battery report ready!")
    print(f"   Location: {report_path}")
    print(f"   File: {report_filename}")
    
    print("\n💡 Report includes:")
    print("   • Battery design capacity vs current capacity")
    print("   • Charge cycles and usage history")
    print("   • Power settings and sleep states")
    print("   • Battery life estimates")
    
    if is_frozen():
        print("\n" + "="*50)
        input("Press Enter to close...")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
