"""OpenLDAC 现代原生 Windows 用户界面。

基于 CustomTkinter 构建，具备深色模式、实时 VU 电平表、
动态码率监控与一键 HFP 通话保护。本文件为简体中文汉化版本。
"""

from __future__ import annotations
import threading
import time
from typing import Optional
import customtkinter as ctk

from ..app import OpenLDACController
from ..codec.ldac_encoder import EQMID_ABR, EQMID_HQ, EQMID_MQ, EQMID_SQ
from ..utils.logger import register_log_observer, unregister_log_observer

# 主题配置
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 中文字族：避免 CJK 字形回退错乱
FONT_UI = "Microsoft YaHei UI"
FONT_MONO = "Consolas"


def ui_font(size: int = 12, weight: str = "normal") -> ctk.CTkFont:
    """统一返回带中文字族的 CTkFont。"""
    return ctk.CTkFont(family=FONT_UI, size=size, weight=weight)


class MainWindow(ctk.CTk):
    """OpenLDAC 主窗口。"""

    def __init__(self, controller: OpenLDACController) -> None:
        super().__init__()
        self.controller = controller

        self.title("OpenLDAC for Windows — 高解析度蓝牙音频")
        self.geometry("900x680")
        self.minsize(860, 620)

        # 若存在图标则加载
        from pathlib import Path
        icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        # 界面状态
        self._is_updating = True

        self._build_ui()
        self._populate_devices()

        # 订阅日志事件
        register_log_observer(self._on_log_message)
        self._on_log_message("—— OpenLDAC 中文版已启动，请选择蓝牙设备后点击“开始 LDAC 串流” ——")

        # 启动 30 FPS 遥测刷新
        self.after(33, self._poll_telemetry)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. 顶部横幅
        self.header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("#1f2937", "#111827"))
        self.header_frame.grid(row=0, column=0, padx=20, pady=(14, 8), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.header_frame,
            text="🎧 OpenLDAC",
            font=ui_font(24, "bold"),
            text_color="#60a5fa"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=8, sticky="w")

        self.title_desc = ctk.CTkLabel(
            self.header_frame,
            text="面向 Windows 的开源索尼 LDAC 音频方案（990 kbps / 96 kHz）",
            font=ui_font(12),
            text_color="#9ca3af"
        )
        self.title_desc.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 6), sticky="w")

        self.status_badge = ctk.CTkLabel(
            self.header_frame,
            text="● 待机",
            font=ui_font(13, "bold"),
            fg_color="#374151",
            text_color="#9ca3af",
            corner_radius=8,
            padx=14,
            pady=6
        )
        self.status_badge.grid(row=0, column=1, padx=20, pady=8, sticky="e")

        # 2. 主控制卡片
        self.controls_frame = ctk.CTkFrame(self, corner_radius=12)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # 设备选择行
        self.dev_label = ctk.CTkLabel(
            self.controls_frame,
            text="目标蓝牙设备：",
            font=ui_font(13, "bold")
        )
        self.dev_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.device_combo = ctk.CTkComboBox(
            self.controls_frame,
            values=["正在扫描…"],
            width=320,
            font=ui_font(12),
            dropdown_font=ui_font(12),
            command=self._on_device_selected
        )
        self.device_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        self.btn_refresh = ctk.CTkButton(
            self.controls_frame,
            text="⟳ 刷新",
            font=ui_font(12),
            width=100,
            command=self._populate_devices
        )
        self.btn_refresh.grid(row=0, column=2, padx=10, pady=8)

        self.btn_stream = ctk.CTkButton(
            self.controls_frame,
            text="▶ 开始 LDAC 串流",
            font=ui_font(13, "bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            width=190,
            command=self._toggle_stream
        )
        self.btn_stream.grid(row=0, column=3, padx=15, pady=8)

        # 音质预设行（EQMID）
        self.quality_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.quality_frame.grid(row=1, column=0, columnspan=4, padx=15, pady=6, sticky="ew")
        self.quality_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.eqmid_var = ctk.IntVar(value=self.controller.config.eqmid)

        self.rb_hq = ctk.CTkRadioButton(
            self.quality_frame,
            text="★ 音质优先\n990 kbps（录音室母带级）",
            font=ui_font(12),
            variable=self.eqmid_var,
            value=EQMID_HQ,
            command=self._on_quality_changed
        )
        self.rb_hq.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        self.rb_mq = ctk.CTkRadioButton(
            self.quality_frame,
            text="◆ 均衡模式\n660 kbps（推荐）",
            font=ui_font(12),
            variable=self.eqmid_var,
            value=EQMID_MQ,
            command=self._on_quality_changed
        )
        self.rb_mq.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        self.rb_sq = ctk.CTkRadioButton(
            self.quality_frame,
            text="◈ 稳定优先\n330 kbps（最大传输距离）",
            font=ui_font(12),
            variable=self.eqmid_var,
            value=EQMID_SQ,
            command=self._on_quality_changed
        )
        self.rb_sq.grid(row=0, column=2, padx=10, pady=8, sticky="w")

        self.rb_abr = ctk.CTkRadioButton(
            self.quality_frame,
            text="⟳ 自适应码率\n射频环境自动调节",
            font=ui_font(12),
            variable=self.eqmid_var,
            value=EQMID_ABR,
            command=self._on_quality_changed
        )
        self.rb_abr.grid(row=0, column=3, padx=10, pady=8, sticky="w")

        # HFP 通话保护卡片（游戏音频修复）
        self.guard_frame = ctk.CTkFrame(self.controls_frame, fg_color=("#1e293b", "#0f172a"), corner_radius=10)
        self.guard_frame.grid(row=2, column=0, columnspan=4, padx=15, pady=(2, 10), sticky="ew")
        self.guard_frame.grid_columnconfigure(1, weight=1)

        self.guard_icon = ctk.CTkLabel(self.guard_frame, text="🛡️", font=ui_font(24))
        self.guard_icon.grid(row=0, column=0, rowspan=2, padx=(15, 5), pady=6)

        self.guard_title = ctk.CTkLabel(
            self.guard_frame,
            text="游戏 / Hi-Fi 音频锁定（HFP 通话保护）",
            font=ui_font(14, "bold"),
            text_color="#38bdf8"
        )
        self.guard_title.grid(row=0, column=1, padx=10, pady=(8, 2), sticky="w")

        self.guard_desc = ctk.CTkLabel(
            self.guard_frame,
            text="防止开启语音通话时，Windows 与游戏把音频降级成 8/16 kHz 的电话音质。",
            font=ui_font(11),
            text_color="#94a3b8",
            wraplength=620,
            justify="left"
        )
        self.guard_desc.grid(row=1, column=1, padx=10, pady=(0, 8), sticky="w")

        self.guard_switch_var = ctk.BooleanVar(value=self.controller.config.hfp_guard_enabled)
        self.guard_switch = ctk.CTkSwitch(
            self.guard_frame,
            text="锁定已启用",
            font=ui_font(12),
            variable=self.guard_switch_var,
            command=self._on_guard_toggled,
            onvalue=True,
            offvalue=False
        )
        self.guard_switch.grid(row=0, column=2, rowspan=2, padx=20, pady=6)

        # 3. 遥测与可视化面板
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=12)
        self.dashboard_frame.grid(row=2, column=0, padx=20, pady=8, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 数据卡片
        self.card_bitrate = self._create_stat_card(self.dashboard_frame, 0, "码率", "0 kbps", "#3b82f6")
        self.card_sr = self._create_stat_card(self.dashboard_frame, 1, "采样率", "96,000 Hz", "#10b981")
        self.card_frames = self._create_stat_card(self.dashboard_frame, 2, "已编码帧", "0", "#8b5cf6")
        self.card_hfp = self._create_stat_card(self.dashboard_frame, 3, "音频配置", "A2DP Hi-Fi", "#06b6d4")

        # VU 电平表
        self.vu_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.vu_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=8, sticky="ew")
        self.vu_frame.grid_columnconfigure(1, weight=1)

        self.lbl_vu_l = ctk.CTkLabel(self.vu_frame, text="左：", width=40, font=ui_font(12, "bold"))
        self.lbl_vu_l.grid(row=0, column=0, padx=5, pady=2)
        self.bar_vu_l = ctk.CTkProgressBar(self.vu_frame, height=12)
        self.bar_vu_l.set(0.0)
        self.bar_vu_l.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        self.lbl_vu_r = ctk.CTkLabel(self.vu_frame, text="右：", width=40, font=ui_font(12, "bold"))
        self.lbl_vu_r.grid(row=1, column=0, padx=5, pady=2)
        self.bar_vu_r = ctk.CTkProgressBar(self.vu_frame, height=12)
        self.bar_vu_r.set(0.0)
        self.bar_vu_r.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # 诊断日志窗口
        self.log_textbox = ctk.CTkTextbox(
            self.dashboard_frame,
            height=88,
            font=ctk.CTkFont(family=FONT_MONO, size=11),
            wrap="word"
        )
        self.log_textbox.grid(row=2, column=0, columnspan=4, padx=20, pady=(2, 10), sticky="nsew")
        self.dashboard_frame.grid_rowconfigure(2, weight=1)

        # 4. 页脚
        self.footer_label = ctk.CTkLabel(
            self,
            text="OpenLDAC v1.0.0-zh-CN — 开源（Apache-2.0）— 无付费墙、无到期限制，纯用户态 WASAPI 架构",
            font=ui_font(11),
            text_color="#6b7280"
        )
        self.footer_label.grid(row=3, column=0, padx=20, pady=(0, 6))

    def _create_stat_card(self, parent: ctk.CTkFrame, col: int, title: str, value: str, color: str) -> dict:
        frame = ctk.CTkFrame(parent, fg_color=("#1e293b", "#0f172a"), corner_radius=10)
        frame.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")

        lbl_title = ctk.CTkLabel(frame, text=title, font=ui_font(10, "bold"), text_color="#94a3b8")
        lbl_title.pack(padx=10, pady=(8, 2))

        lbl_val = ctk.CTkLabel(frame, text=value, font=ui_font(16, "bold"), text_color=color)
        lbl_val.pack(padx=10, pady=(0, 8))

        return {"frame": frame, "title": lbl_title, "value": lbl_val}

    def _populate_devices(self) -> None:
        devices = self.controller.device_manager.scan_devices()
        dev_names = [d.name for d in devices] if devices else ["未找到蓝牙音频设备"]
        self.device_combo.configure(values=dev_names)

        current_dev = self.controller.active_device
        if current_dev and current_dev.name in dev_names:
            self.device_combo.set(current_dev.name)
        elif dev_names:
            self.device_combo.set(dev_names[0])
            if devices:
                self.controller.active_device = devices[0]

    def _on_device_selected(self, dev_name: str) -> None:
        for d in self.controller.device_manager.cached_devices:
            if d.name == dev_name:
                self.controller.active_device = d
                break

    def _toggle_stream(self) -> None:
        if not self.controller.is_streaming:
            dev_name = self.device_combo.get()
            dev = self.controller.device_manager.get_selected_or_default(dev_name)
            if self.controller.start_streaming(dev):
                self.btn_stream.configure(text="⏹ 停止 LDAC 串流", fg_color="#dc2626", hover_color="#b91c1c")
                self.status_badge.configure(text="● LDAC 串流中", fg_color="#065f46", text_color="#34d399")
        else:
            self.controller.stop_streaming()
            self.btn_stream.configure(text="▶ 开始 LDAC 串流", fg_color="#2563eb", hover_color="#1d4ed8")
            self.status_badge.configure(text="● 待机", fg_color="#374151", text_color="#9ca3af")

    def _on_quality_changed(self) -> None:
        eqmid = self.eqmid_var.get()
        self.controller.set_quality_mode(eqmid)

    def _on_guard_toggled(self) -> None:
        enabled = self.guard_switch_var.get()
        self.controller.toggle_hfp_guard(enabled)

    def _on_log_message(self, msg: str) -> None:
        def append():
            try:
                self.log_textbox.insert("end", msg + "\n")
                self.log_textbox.see("end")
            except Exception:
                pass
        self.after(0, append)

    def _poll_telemetry(self) -> None:
        """定时刷新统计数据与 VU 电平表。"""
        if self._is_updating:
            telem = self.controller.get_telemetry()

            # 更新数据卡片
            bitrate = telem["bitrate_kbps"]
            self.card_bitrate["value"].configure(text=f"{bitrate} kbps" if bitrate > 0 else "0 kbps")
            self.card_sr["value"].configure(text=f"{telem['sample_rate']:,} Hz")
            self.card_frames["value"].configure(text=f"{telem['frames_encoded']:,}")

            hfp_status = "Hi-Fi 已保护" if telem["hfp_guard_active"] else "标准配置"
            self.card_hfp["value"].configure(text=hfp_status)

            # 更新 VU 电平条（带衰减）
            lvl_l = telem["level_l"]
            lvl_r = telem["level_r"]
            self.bar_vu_l.set(min(1.0, max(0.0, lvl_l * 1.5)))
            self.bar_vu_r.set(min(1.0, max(0.0, lvl_r * 1.5)))

            self.after(33, self._poll_telemetry)

    def destroy(self) -> None:
        self._is_updating = False
        unregister_log_observer(self._on_log_message)
        self.controller.shutdown()
        super().destroy()
