"""构建脚本：生成带应用图标的 OpenLDAC 中文版独立可执行文件（目录版 + 单文件版）。"""

import os
import shutil
import sys
import subprocess
from pathlib import Path

APP_NAME = "OpenLDAC-zh-CN"
PORTABLE_NAME = "OpenLDAC-zh-CN_Portable"


def build():
    root = Path(__file__).resolve().parent.parent
    dist_dir = root / "dist"
    build_dir = root / "build_temp"
    run_file = root / "run.py"
    icon_file = root / "assets" / "icon.ico"

    icon_args = [f"--icon={icon_file}"] if icon_file.exists() else []

    # 1. 目录版（dist/OpenLDAC-zh-CN/）
    print("=== 正在构建目录版 (dist/OpenLDAC-zh-CN/) ===")
    cmd_dir = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", APP_NAME,
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        f"--paths={root}",
        *icon_args,
        "--collect-all", "customtkinter",
        "--collect-all", "sounddevice",
        "--collect-all", "comtypes",
        str(run_file)
    ]
    res1 = subprocess.run(cmd_dir, cwd=str(root))

    # 2. 单文件便携版（dist/OpenLDAC-zh-CN_Portable.exe）
    print("\n=== 正在构建单文件便携版 (dist/OpenLDAC-zh-CN_Portable.exe) ===")
    cmd_onefile = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", PORTABLE_NAME,
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        f"--paths={root}",
        *icon_args,
        "--collect-all", "customtkinter",
        "--collect-all", "sounddevice",
        "--collect-all", "comtypes",
        str(run_file)
    ]
    res2 = subprocess.run(cmd_onefile, cwd=str(root))

    # 清理临时构建目录，避免残留 stub 混淆
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    if res1.returncode == 0 and res2.returncode == 0:
        print("\n[SUCCESS] 可执行文件构建完成！")
        print(f"  - 目录版：{dist_dir / APP_NAME / (APP_NAME + '.exe')}")
        print(f"  - 单文件：{dist_dir / (PORTABLE_NAME + '.exe')}")
        return True
    print("\n[ERROR] 构建失败，请检查上方 PyInstaller 输出。")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if build() else 1)
