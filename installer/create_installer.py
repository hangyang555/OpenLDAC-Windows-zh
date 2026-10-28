"""生成 OpenLDAC 中文版（zh-CN）带图标的自包含 Windows 安装包。

产物（dist/installer/）：
  * OpenLDAC-zh-CN-v1.0.0-win-x64.zip  —— 完整目录版 + 一键安装脚本（便携 zip 发布包）
  * Install_OpenLDAC_zh-CN.ps1 / .bat  —— 安装脚本（同时被打进 zip）
"""

import os
import shutil
import zipfile
from pathlib import Path

APP_NAME = "OpenLDAC-zh-CN"
VERSION = "1.0.0"
ZIP_NAME = f"{APP_NAME}-v{VERSION}-win-x64.zip"
INSTALL_DIR_REL = r"%LOCALAPPDATA%\Programs\OpenLDAC-zh-CN"
SHORTCUT_NAME = "OpenLDAC 中文版"


def create_installer():
    root = Path(__file__).resolve().parent.parent
    dist_dir = root / "dist" / APP_NAME
    assets_dir = root / "assets"
    output_dir = root / "dist" / "installer"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not dist_dir.exists():
        print(f"[ERROR] 未找到构建产物目录：{dist_dir}")
        print("        请先运行 python installer\\build_app.py")
        return False

    # 把 assets（图标等）复制进目录版，供快捷方式与界面使用
    target_assets = dist_dir / "assets"
    target_assets.mkdir(parents=True, exist_ok=True)
    if assets_dir.exists():
        for f in assets_dir.glob("*"):
            if f.is_file():
                shutil.copy2(f, target_assets / f.name)

    # 1. 安装脚本（PowerShell）
    setup_ps1 = output_dir / "Install_OpenLDAC_zh-CN.ps1"
    setup_ps1.write_text(r"""# OpenLDAC 中文版 —— Windows 安装脚本
$ErrorActionPreference = "Stop"
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "   OpenLDAC 中文版 安装程序  v1.0.0-zh-CN      " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\OpenLDAC-zh-CN"
Write-Host "安装目录：$InstallDir" -ForegroundColor Yellow

if (Test-Path $InstallDir) {
    Write-Host "检测到旧版本，正在覆盖安装……" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $InstallDir
}
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# 兼容两种布局：zip 根目录 / installer 子目录
$SourceDir = Join-Path $PSScriptRoot "OpenLDAC-zh-CN"
if (-not (Test-Path $SourceDir)) {
    $SourceDir = Join-Path $PSScriptRoot "..\OpenLDAC-zh-CN"
}

Copy-Item -Path "$SourceDir\*" -Destination $InstallDir -Recurse -Force
Write-Host "文件复制完成。" -ForegroundColor Green

# 桌面快捷方式（路径与卸载脚本保持一致，均使用 %USERPROFILE%\Desktop）
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = Join-Path $env:USERPROFILE "Desktop"
if (-not (Test-Path $DesktopPath)) {
    $DesktopPath = [System.Environment]::GetFolderPath('Desktop')
}
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\OpenLDAC-zh-CN.lnk")
$Shortcut.TargetPath = "$InstallDir\OpenLDAC-zh-CN.exe"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Description = "OpenLDAC 中文版 —— 高解析度蓝牙音频（LDAC）"
$IconPath = "$InstallDir\assets\icon.ico"
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = "$IconPath, 0"
}
$Shortcut.Save()

# 卸载脚本（快捷方式名保持 ASCII，避免控制台代码页变化导致 del 路径失效）
$UninstallScript = "$InstallDir\Uninstall.bat"
$uninstallLines = @(
    '@echo off',
    'echo 正在卸载 OpenLDAC 中文版...',
    'del "%USERPROFILE%\Desktop\OpenLDAC-zh-CN.lnk"',
    'echo 已删除桌面快捷方式与程序文件。',
    'echo OpenLDAC 中文版 已卸载。',
    'rem 注意：必须先删快捷方式，再删目录——目录里正躺着本脚本自己',
    'timeout /t 1 >nul',
    'rmdir /s /q "%LOCALAPPDATA%\Programs\OpenLDAC-zh-CN"'
)
$uninstallText = ($uninstallLines -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($UninstallScript, $uninstallText, [System.Text.Encoding]::GetEncoding(936))
Write-Host "`n[完成] OpenLDAC 中文版 安装成功！" -ForegroundColor Green
Write-Host "已在桌面创建快捷方式（OpenLDAC-zh-CN.lnk）。" -ForegroundColor Green
Write-Host "启动路径：$InstallDir\OpenLDAC-zh-CN.exe" -ForegroundColor Green
Write-Host "（配置文件与原英文版共用：$env:LOCALAPPDATA\OpenLDAC\config.json）" -ForegroundColor DarkGray
Start-Sleep -Seconds 3
""", encoding="utf-8-sig")   # 必须带 BOM：Windows PowerShell 5.1 会把无 BOM 的 UTF-8 当成 ANSI，中文字符串会被截断

    # 2. 一键安装批处理
    setup_bat = output_dir / "Install_OpenLDAC_zh-CN.bat"
    setup_bat.write_text(r"""@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install_OpenLDAC_zh-CN.ps1"
pause
""", encoding="utf-8")

    # 3. zip 内附带的使用说明
    readme_txt = output_dir / "使用说明.txt"
    readme_txt.write_text(
        "OpenLDAC 中文版 v1.0.0-zh-CN\r\n"
        "=================================\r\n\r\n"
        "【免安装使用】\r\n"
        "  直接双击 OpenLDAC-zh-CN\\OpenLDAC-zh-CN.exe 即可运行。\r\n\r\n"
        "【安装到系统（推荐）】\r\n"
        "  双击 Install_OpenLDAC_zh-CN.bat，程序会安装到：\r\n"
        "    %LOCALAPPDATA%\\Programs\\OpenLDAC-zh-CN\r\n"
        "  并在桌面创建“OpenLDAC-zh-CN”快捷方式。\r\n"
        "  卸载：运行安装目录下的 Uninstall.bat。\r\n\r\n"
        "【配置文件】\r\n"
        "  %LOCALAPPDATA%\\OpenLDAC\\config.json（与原英文版共用，切换版本不丢设置）\r\n\r\n"
        "【许可】\r\n"
        "  Apache License 2.0。上游项目：\r\n"
        "  https://github.com/shubhamkjha369/OpenLDAC-Windows\r\n"
        "  Sony 与 LDAC 是索尼公司的商标。\r\n",
        encoding="utf-8-sig")

    # 4. 打 zip 发布包：顶层 OpenLDAC-zh-CN/ 目录 + 安装脚本 + 使用说明
    zip_path = output_dir / ZIP_NAME
    print(f"正在生成发布 zip：{zip_path}")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in dist_dir.rglob("*"):
            if file.is_file():
                zipf.write(file, file.relative_to(dist_dir.parent))
        for extra in (setup_ps1, setup_bat, readme_txt):
            zipf.write(extra, extra.name)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[SUCCESS] 安装包已生成：{zip_path}（{size_mb:.1f} MB）")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if create_installer() else 1)
