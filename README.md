# OpenLDAC for Windows — 简体中文版

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011%20x64-0078D6.svg)]()
[![Codec](https://img.shields.io/badge/Codec-Sony%20LDAC%20(990%20kbps)-orange.svg)]()
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passed-brightgreen.svg)]()
[![Language](https://img.shields.io/badge/UI-简体中文-red.svg)]()

> **Windows 高解析度索尼 LDAC 音频方案 · 简体中文汉化版**  
> 纯用户态架构，位完美 WASAPI 环回，无内核驱动蓝屏风险，无商业付费墙，并内置 **HFP 通话保护（游戏音质修复）**。本版为上游 [OpenLDAC-Windows v1.0.0](https://github.com/shubhamkjha369/OpenLDAC-Windows) 的汉化版，功能一致，界面与用户可见日志全部中文化，并额外修复了高 DPI 缩放下的界面裁切问题。

---

## 📸 界面预览

![中文界面预览](assets/screenshots/main-window.png)

---

## 🌟 本版亮点

* **🀄 全面中文界面：**
  * 标题、状态徽标、按钮、音质预设、遥测卡片、HFP 保护卡片、诊断日志、页脚全部中文化。
  * 界面与用户可见日志全部中文化（33 处），设备扫描、HFP 拦截、WASAPI 采集、编码器状态都能看懂。
  * 统一 `Microsoft YaHei UI` 字体族，中英文混排不再出现字号跳变或方框。
* **🚀 索尼 LDAC 编码支持（与上游一致）：**
  * **音质优先：** 990 kbps（96 / 48 kHz）或 909 kbps（88.2 / 44.1 kHz）—— 录音室母带级。
  * **均衡模式：** 660 kbps（96 / 48 kHz）或 606 kbps（88.2 / 44.1 kHz）—— 稳定性与听感的平衡点。
  * **稳定优先：** 330 kbps（96 / 48 kHz）或 303 kbps（88.2 / 44.1 kHz）—— 最大传输距离与抗断连。
  * **自适应码率（ABR）：** 依据缓冲健康状况实时调节码率。
* **🛡️ 内置 HFP 通话保护（游戏音质修复）：**
  * 解决 Windows 上那个著名的缺陷：启动游戏（COD、CS2、Valorant、Fortnite）或 Discord 时，
    系统抢占蓝牙耳机麦克风，音频被降级为 **8 kHz / 16 kHz 单声道电话音质**。
  * 在高解析度 A2DP 播放期间抑制低质量通话端点，让游戏音效保持完整立体声。
* **⚡ 纯用户态 WASAPI 架构（与上游一致）：**
  * 通过低延迟 WASAPI 环回直接从 Windows 音频引擎取位完美系统音频。
  * 绕开内核驱动签名（`.sys`）、WHQL 门槛与睡眠唤醒崩溃问题，兼容 Windows 安全启动。
* **🎨 现代 Windows 原生界面（与上游一致）：**
  * CustomTkinter 暗色主题。
  * 实时立体声左右声道 VU 电平表。
  * 实时码率 / 采样率 / 已编码帧遥测。
  * 诊断事件控制台。
* **🖥️ 高 DPI 修复（本版新增）：**
  * 修复上游在 125% – 200% 缩放下底部数据卡片与日志框被窗口裁切的问题。
  * 显式启用 Per-Monitor DPI 感知，消除系统位图拉伸导致的字体模糊。
* **🧪 100% 通过验证：**
  * 10/10 自动化单元与集成测试通过（与上游同一套测试）。

---

## 📁 仓库结构

```
OpenLDAC-Windows-zh/
├── src/
│   ├── app.py                 # 核心串流控制器
│   ├── audio/
│   │   └── wasapi_capture.py  # 零延迟 WASAPI 环回采集
│   ├── codec/
│   │   └── ldac_encoder.py    # 索尼 LDAC 协议与帧编码器
│   ├── bluetooth/
│   │   ├── avdtp_streamer.py  # A2DP AVDTP/RTP 封包
│   │   ├── device_manager.py  # 蓝牙设备发现与配置文件
│   │   └── hfp_guard.py       # 游戏音质 HFP 抑制引擎
│   ├── gui/
│   │   └── main_window.py     # CustomTkinter 暗色主题界面（已汉化）
│   └── utils/
│       ├── config.py          # 用户设置持久化
│       └── logger.py          # 线程安全日志子系统
├── tests/                     # 自动化测试套件（pytest，10 项全通过）
│   ├── test_ldac_codec.py
│   ├── test_avdtp_packet.py
│   ├── test_hfp_guard.py
│   └── test_integration.py
├── installer/
│   ├── build_app.py           # PyInstaller 独立可执行文件构建脚本
│   └── create_installer.py    # 便携 zip 与安装脚本生成器
├── assets/
│   ├── icon.ico
│   ├── icon.png
│   └── screenshots/
│       └── main-window.png    # 中文界面截图
├── docs/
│   ├── ARCHITECTURE.md        # 架构说明（已译中文）
│   └── HFP_DEGRADATION_FIX.md # 蓝牙麦克风降级修复详解（已译中文）
├── CHANGELOG.md               # 版本变更记录
├── NOTICE                     # 上游版权与修改声明
└── run.py                     # 源码启动器（含 DPI 感知初始化）
```

---

## 🚀 快速开始

### 方式 1：直接下载发布版（无需 Python）

* **`OpenLDAC-zh-CN_Portable.exe`（推荐）：**
  * **零安装。** 单个自包含可执行文件（约 26 MB），下载后双击即用，无需 Python 或任何外部运行时。
* **`OpenLDAC-zh-CN-v1.0.0-win-x64.zip`：**
  * 完整应用目录 + 一键安装脚本（`Install_OpenLDAC_zh-CN.bat`），可安装到 `%LOCALAPPDATA%\Programs\OpenLDAC-zh-CN` 并创建桌面快捷方式。
  * 安装目录与原英文版独立，可与 [上游发布版](https://github.com/shubhamkjha369/OpenLDAC-Windows/releases) 并存。

### 方式 2：从源码构建

```powershell
git clone https://github.com/<你的账号>/<仓库名>.git
cd <仓库名>
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python run.py                     # 直接运行源码
python installer\build_app.py     # 打包目录版 + 单文件版到 dist\
```

需要 Python 3.11+（本版用 3.12 构建），Windows 10 1809+ / Windows 11 x64。

---

## 🧪 运行自动化测试

```powershell
pip install pytest
python -m pytest tests -v
```

全部 10 项测试校验编码器帧长与同步字、CRC 计算、RTP 包头、AVDTP 能力元素，以及 HFP 通话保护状态机（与上游同一套测试）。

---

## 💻 系统要求

* **操作系统：** Windows 10（1809+）或 Windows 11（64 位）
* **蓝牙：** 蓝牙 4.0+ 适配器
* **耳机 / 接收端：** 任意支持 LDAC 的蓝牙耳机或 DAC（Sony、Technics、FiiO、Shanling、Soundcore、OPPO Enco 等品牌均有多款型号可用）

---

## 📝 说明

* 本版仅汉化文案、调整字体/边距/DPI，**未改动任何音频链路逻辑**，音质行为与上游 v1.0.0 完全一致。
* 配置文件与原版共用 `%LOCALAPPDATA%\OpenLDAC\config.json`，切换版本不会丢失设备与音质设置。
* 版本变更记录见 [CHANGELOG.md](CHANGELOG.md)。

---

## 📄 许可证

基于 [Apache License 2.0](LICENSE) 发布，上游版权与修改声明见 [NOTICE](NOTICE)。
Sony 与 LDAC 是索尼公司的注册商标。
