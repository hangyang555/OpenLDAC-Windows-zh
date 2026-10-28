# Windows 蓝牙麦克风导致的音频降级：根因与修复

## 问题现象

把蓝牙耳机（Sony WH-1000XM4/XM5、WF-1000XM4/XM5、boat Nirvana Ion ANC、Airdopes、Bose 等）连到 Windows 后，
只要启动任意游戏（Call of Duty、Valorant、CS2、Fortnite）或打开 Discord，游戏音频会立刻变得发闷、空洞、尖细、像老式电话一样压缩。

只有手动进入声音设置、禁用耳机麦克风之后，音质才会恢复。

## 技术根因

蓝牙经典（Bluetooth Classic）跑在共享的 2.4 GHz 频段上，带宽有限。一支蓝牙耳机向 Windows 暴露两个配置文件：

1. **A2DP（高级音频分发配置文件）：** 高码率单向立体声串流（LDAC 最高 990 kbps、AAC 256 kbps、SBC 328 kbps）。游戏、音乐、电影的理想选择。
2. **HFP / HSP（免提配置文件）：** 双向低码率语音通信。受射频限制，HFP 输出被限制为 **8 kHz CVSD（AM 电话音质）** 或 **16 kHz mSBC（低质语音）**，且为单声道。

当 Windows 检测到某个应用（开了队内语音的游戏、Discord、Zoom、Windows 录音机）在耳机麦克风端点上打开了录音流时：

* Windows 立即挂起 A2DP 立体声播放；
* Windows 强制把全部系统与游戏音频输出改走耳机的 **Hands-Free AG Audio** 端点，8,000 Hz 或 16,000 Hz 单声道；
* 商业方案 Alternative A2DP Driver 只是记录一行 `Suspended by HFP`，然后就任由音质降级发生。

## OpenLDAC 如何修复：HFP 通话保护

OpenLDAC 内置了 **HFP 通话保护（HFP Telephony Guard）**：

1. 自动枚举并识别当前蓝牙音频设备关联的全部 Hands-Free 录音端点。
2. 当 **游戏 / Hi-Fi 音频锁定** 开启时，OpenLDAC 抑制耳机麦克风端点。
3. 因为任何应用都无法从蓝牙射频拿到音频采集句柄，Windows 也就不会收到切换到 HFP 的信号。
4. 游戏与语音应用会无缝回退到笔记本内置麦克风、外接 USB 麦克风或摄像头麦克风。
5. 整个游戏过程里，游戏音频始终锁定在位完美、通透的 **高解析度立体声 LDAC（最高 990 kbps）**。
6. 用户关闭锁定或退出 OpenLDAC 后，通话端点会自动恢复。

> 汉化版说明：本文件为上游文档的中文翻译，实现逻辑未做任何改动。
