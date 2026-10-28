# OpenLDAC 架构设计记录（ADR）

## 1. 背景与动机

Windows 10 / 11 原生支持蓝牙 A2DP，但仅限 SBC 与 AAC，**不支持索尼 LDAC**（最高 990 kbps @ 96 kHz / 24-bit）。
第三方方案（如 Alternative A2DP Driver，`AltA2DP.sys`）依赖自定义 KMDF PortCls 内核态驱动，
需要商业 EV 证书签名、闭源收费，并且在睡眠 / 唤醒循环中存在内核崩溃隐患。

此外，标准 Windows 蓝牙音频还带着一个致命缺陷：当任何应用（游戏、Discord 等）占用蓝牙设备麦克风时，
Windows 会把连接从 A2DP 立体声降级为 **8 kHz / 16 kHz 单声道电话音质**（Hands-Free Profile）。

## 2. 选定架构：方案 B（用户态 WASAPI + LDAC 传输）

OpenLDAC 实现的是纯**用户态架构**：

```
[ Windows 应用程序（游戏、播放器、浏览器） ]
                       │
                       ▼
           [ Windows 音频引擎（WASAPI） ]
                       │（位完美共享环回）
                       ▼
        [ OpenLDAC WASAPI 环回采集 ]（48/96 kHz，32-bit float）
                       │
                       ▼
            [ 索尼 LDAC 帧编码器 ]
          （子带量化、缩放因子、CRC）
          （音质预设：990 / 660 / 330 kbps 及 ABR）
                       │
                       ▼
           [ AVDTP / RTP 媒体封包器 ]
             （Payload Type 96、时间戳、SSRC）
                       │
                       ▼
   [ 蓝牙 A2DP Source / 传输控制器 ]
                       │
                       ▼
      [ 蓝牙耳机（Sony / ANC 等） ]
```

## 3. 关键设计取舍

1. **零内核暴露：** 不安装任何内核态驱动（`.sys`），系统完整性、安全启动与抗崩溃能力 100% 保留。
2. **HFP 通话保护：** 在高解析度播放期间主动抑制蓝牙免提录音端点，阻止 Windows 把音频链路降级到电话模式，从而修复麦克风导致的音质劣化。
3. **开源与宽松许可：** Apache 2.0，没有到期计时器、试用付费墙或闭源二进制。
4. **独立打包：** 可作为独立 Windows 可执行文件（`OpenLDAC-zh-CN.exe`）与便携安装包完整分发。

> 汉化版说明：本仓库仅本地化了文案与界面排版，架构与上述设计完全一致。
