"""Build script to package NovaCalc into a standalone Windows executable using PyInstaller.
"""

import os
import subprocess
import sys


def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "assets", "icon.ico")
    styles_data = f"{os.path.join(base_dir, 'styles')};styles"
    assets_data = f"{os.path.join(base_dir, 'assets')};assets"

    print("=== NovaCalc PyInstaller Build Script ===")
    print(f"Working Directory: {base_dir}")
    print(f"Icon Path: {icon_path}")

    # Ensure icon exists
    if not os.path.exists(icon_path):
        print("Generating icon...")
        from assets.generate_icon import create_novacalc_icon
        create_novacalc_icon()

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",
        "--onefile",
        f"--name=NovaCalc",
        f"--icon={icon_path}",
        f"--add-data={styles_data}",
        f"--add-data={assets_data}",
        "--clean",
        os.path.join(base_dir, "main.py"),
    ]

    print("Running command:")
    print(" ".join(cmd))

    result = subprocess.run(cmd, cwd=base_dir)
    if result.returncode == 0:
        exe_path = os.path.join(base_dir, "dist", "NovaCalc.exe")
        print("\n==========================================")
        print(f"BUILD SUCCESSFUL! Standalone Executable:")
        print(f"Path: {exe_path}")
        if os.path.exists(exe_path):
            print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
        print("==========================================")
    else:
        print(f"Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
