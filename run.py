"""OpenLDAC 启动器。

以正确的路径解析方式启动 OpenLDAC 应用程序，并先启用 DPI 感知，
避免在高缩放（125%/150%/200%）显示器上控件溢出窗口。
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

# 确保包根目录在 sys.path 中
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def enable_dpi_awareness() -> None:
    """让进程按物理像素工作，使 Tk 与 Windows 缩放比例一致。"""
    try:
        import ctypes
        # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main() -> None:
    enable_dpi_awareness()

    from src.app import OpenLDACController
    from src.gui.main_window import MainWindow

    controller = OpenLDACController()
    controller.initialize()

    app = MainWindow(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
