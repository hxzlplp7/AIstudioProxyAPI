#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Studio Proxy API - Simple GUI Launcher
Easy to use, modern interface launcher.

Features:
- Modern dark theme
- GNOME system tray support
- Account management (add, delete)
- Proxy settings
- Port configuration
- API test button
- Log saving

Usage:
    poetry run python simple_launcher.py
"""

import json
import os
import platform
import re
import signal
import socket
import subprocess
import shutil
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from typing import Any, Dict, List, Optional

# Project directories
SCRIPT_DIR = Path(__file__).parent.absolute()
AUTH_PROFILES_DIR = SCRIPT_DIR / "auth_profiles"
SAVED_AUTH_DIR = AUTH_PROFILES_DIR / "saved"
ACTIVE_AUTH_DIR = AUTH_PROFILES_DIR / "active"
LAUNCH_SCRIPT = SCRIPT_DIR / "launch_camoufox.py"
CONFIG_FILE = SCRIPT_DIR / "simple_launcher_config.json"
LOG_FILE = SCRIPT_DIR / "logs" / "simple_launcher.log"

# Default settings
DEFAULT_CONFIG = {
    "fastapi_port": 2048,
    "camoufox_port": 9222,
    "stream_port": 3120,
    "proxy_address": "",
    "proxy_enabled": False,
    "last_account": "",
    "dark_mode": True,
    "minimize_to_tray": True,
}

# Modern Color Palette (Dark Theme)
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "success": "#00d26a",
    "warning": "#ffc107",
    "error": "#dc3545",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "border": "#2d2d44",
}


class ModernStyle:
    """Modern style manager"""

    @staticmethod
    def apply(root):
        """Apply dark theme styles"""
        style = ttk.Style()

        # Set theme
        style.theme_use("clam")

        # Frame styles
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("Card.TFrame", background=COLORS["bg_medium"])

        # Label styles
        style.configure(
            "TLabel",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Header.TLabel",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background=COLORS["bg_dark"],
            foreground=COLORS["success"],
            font=("Segoe UI", 11, "bold"),
        )

        # LabelFrame styles
        style.configure(
            "TLabelframe",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
        )
        style.configure(
            "TLabelframe.Label",
            background=COLORS["bg_medium"],
            foreground=COLORS["accent"],
            font=("Segoe UI", 11, "bold"),
        )

        # Button styles
        style.configure(
            "TButton",
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 10),
            padding=(10, 5),
        )
        style.map(
            "TButton",
            background=[
                ("active", COLORS["accent"]),
                ("pressed", COLORS["accent_hover"]),
            ],
        )

        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 10, "bold"),
        )

        # Entry styles
        style.configure(
            "TEntry",
            fieldbackground=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            insertcolor=COLORS["text_primary"],
        )

        # Combobox styles
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["bg_light"],
            background=COLORS["bg_light"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_primary"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["bg_light"])],
            selectbackground=[("readonly", COLORS["accent"])],
        )

        # Radiobutton styles - larger and more visible
        style.configure(
            "TRadiobutton",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 11),
            indicatorsize=20,
        )
        style.map(
            "TRadiobutton",
            indicatorcolor=[
                ("selected", COLORS["accent"]),
                ("!selected", COLORS["bg_light"]),
            ],
            background=[("active", COLORS["bg_light"])],
        )

        # Checkbutton styles - larger and more visible
        style.configure(
            "TCheckbutton",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            font=("Segoe UI", 11),
            indicatorsize=18,
        )
        style.map(
            "TCheckbutton",
            indicatorcolor=[
                ("selected", COLORS["accent"]),
                ("!selected", COLORS["bg_light"]),
            ],
            background=[("active", COLORS["bg_light"])],
        )

        # Notebook styles
        style.configure("TNotebook", background=COLORS["bg_dark"], borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLORS["bg_medium"],
            foreground=COLORS["text_primary"],
            padding=(15, 8),
            font=("Segoe UI", 10),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", COLORS["text_primary"])],
        )

        # Root widget background
        root.configure(bg=COLORS["bg_dark"])


class TrayIcon:
    """GNOME system tray support - AppIndicator3 (Wayland) or pystray (X11)"""

    def __init__(self, app):
        self.app = app
        self.indicator = None
        self.supported = False
        self.backend = None  # "appindicator" or "pystray"

    def create_icon(self):
        """Create tray icon - try AppIndicator3 first, then pystray"""

        # 1. Try GNOME AppIndicator3 first (for Wayland)
        if self._try_appindicator():
            return

        # 2. Then try pystray (for X11)
        if self._try_pystray():
            return

        print("⚠️ 未找到系统托盘支持，已禁用。")

    def _try_appindicator(self) -> bool:
        """Try to create tray with AppIndicator3"""
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("AppIndicator3", "0.1")
            from gi.repository import AppIndicator3, GLib, Gtk

            # Create menu
            menu = Gtk.Menu()

            # Menu items
            item_show = Gtk.MenuItem(label="📂 显示窗口")
            item_show.connect(
                "activate", lambda w: GLib.idle_add(self.app._show_window)
            )
            menu.append(item_show)

            menu.append(Gtk.SeparatorMenuItem())

            item_start = Gtk.MenuItem(label="▶️ 启动")
            item_start.connect("activate", lambda w: GLib.idle_add(self.app._start))
            menu.append(item_start)

            item_stop = Gtk.MenuItem(label="⏹️ 停止")
            item_stop.connect("activate", lambda w: GLib.idle_add(self.app._stop))
            menu.append(item_stop)

            menu.append(Gtk.SeparatorMenuItem())

            item_test = Gtk.MenuItem(label="🔍 API 测试")
            item_test.connect("activate", lambda w: GLib.idle_add(self.app._api_test))
            menu.append(item_test)

            menu.append(Gtk.SeparatorMenuItem())

            item_quit = Gtk.MenuItem(label="❌ 退出")
            item_quit.connect(
                "activate", lambda w: GLib.idle_add(self.app._close_completely)
            )
            menu.append(item_quit)

            menu.show_all()

            # Create AppIndicator
            self.indicator = AppIndicator3.Indicator.new(
                "aistudio-proxy",
                "network-server",  # Use system icon
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_menu(menu)
            self.indicator.set_title("AI Studio 代理")

            # Run GTK main loop in separate thread
            def gtk_main():
                try:
                    Gtk.main()
                except Exception:
                    pass

            threading.Thread(target=gtk_main, daemon=True).start()

            self.supported = True
            self.backend = "appindicator"
            print("✅ GNOME AppIndicator3 托盘已启动 (Wayland 兼容)")
            return True

        except Exception as e:
            print(f"⚠️ AppIndicator3 无法启动: {e}")
            return False

    def _try_pystray(self) -> bool:
        """Try to create tray with pystray"""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Create a simple icon
            size = 64
            image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse([4, 4, size - 4, size - 4], fill=COLORS["accent"])
            draw.ellipse([16, 16, size - 16, size - 16], fill=COLORS["bg_dark"])

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("📂 显示窗口", self._pystray_show),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("▶️ 启动", self._pystray_start),
                pystray.MenuItem("⏹️ 停止", self._pystray_stop),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("🔍 API 测试", self._pystray_test),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❌ 退出", self._pystray_quit),
            )

            self.indicator = pystray.Icon(
                "AI Studio 代理", image, "AI Studio 代理", menu
            )
            threading.Thread(target=self.indicator.run, daemon=True).start()

            self.supported = True
            self.backend = "pystray"
            print("✅ pystray 托盘已启动 (X11)")
            return True

        except Exception as e:
            print(f"⚠️ pystray 无法启动: {e}")
            return False

    def _pystray_show(self, icon=None, item=None):
        self.app.root.after(0, self.app._show_window)

    def _pystray_start(self, icon=None, item=None):
        self.app.root.after(0, self.app._start)

    def _pystray_stop(self, icon=None, item=None):
        self.app.root.after(0, self.app._stop)

    def _pystray_test(self, icon=None, item=None):
        self.app.root.after(0, self.app._api_test)

    def _pystray_quit(self, icon=None, item=None):
        self.app.root.after(0, self.app._close_completely)

    def update_status(self, running: bool):
        """Update tray icon status"""
        if not self.supported:
            return
        # Status update - can be extended later

    def stop(self):
        """Stop tray icon"""
        try:
            if self.backend == "appindicator":
                import gi

                gi.require_version("Gtk", "3.0")
                from gi.repository import Gtk

                Gtk.main_quit()
            elif self.backend == "pystray" and self.indicator:
                self.indicator.stop()
        except Exception:
            pass


class SimpleGUILauncher:
    """Simple GUI Launcher"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 AI Studio 代理 API")
        self.root.geometry("1050x700")
        self.root.minsize(800, 500)

        # Apply modern style
        ModernStyle.apply(self.root)

        # Load configuration
        self.config = self._load_config()

        # Variables
        self.selected_account = tk.StringVar(value=self.config.get("last_account", ""))
        self.run_mode = tk.StringVar(value="headless")
        self.status = tk.StringVar(value="⚪ 就绪")
        self.fastapi_port = tk.StringVar(
            value=str(self.config.get("fastapi_port", 2048))
        )
        self.stream_port = tk.StringVar(value=str(self.config.get("stream_port", 3120)))
        self.proxy_address = tk.StringVar(value=self.config.get("proxy_address", ""))
        self.proxy_enabled = tk.BooleanVar(
            value=self.config.get("proxy_enabled", False)
        )

        self.process: Optional[subprocess.Popen] = None
        self.log_thread: Optional[threading.Thread] = None
        self.running = False

        # Tray icon
        self.tray = TrayIcon(self)

        # Create log directory
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Create interface
        self._create_interface()

        # Load accounts
        self._load_accounts()

        # Start tray icon
        if self.config.get("minimize_to_tray", True):
            self.tray.create_icon()

        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception as e:
            print(f"⚠️ 无法加载配置: {e}")
        return DEFAULT_CONFIG.copy()

    def _save_config(self):
        """Save configuration"""
        try:
            config = {
                "fastapi_port": int(self.fastapi_port.get() or 2048),
                "stream_port": int(self.stream_port.get() or 3120),
                "proxy_address": self.proxy_address.get(),
                "proxy_enabled": self.proxy_enabled.get(),
                "last_account": self.selected_account.get(),
                "dark_mode": True,
                "minimize_to_tray": True,
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self._log(f"⚠️ 无法保存配置: {e}")

    def _create_interface(self):
        """Create modern interface"""

        # Main container
        main_container = ttk.Frame(self.root, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)

        # === HEADER ===
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(
            header_frame, text="🚀 AI Studio 代理 API", style="Header.TLabel"
        ).pack(side=tk.LEFT)

        # Status indicator (top right)
        self.status_label = ttk.Label(
            header_frame, textvariable=self.status, style="Status.TLabel"
        )
        self.status_label.pack(side=tk.RIGHT)

        # === NOTEBOOK (Tabs) ===
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Main Control
        self.main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.main_tab, text="🎮 控制面板")
        self._create_main_tab()

        # Tab 2: Account Management
        self.account_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.account_tab, text="👤 账户管理")
        self._create_account_tab()

        # Tab 3: Settings
        self.settings_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.settings_tab, text="⚙️ 设置")
        self._create_settings_tab()

        # Tab 4: Logs
        self.log_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.log_tab, text="📋 日志")
        self._create_log_tab()

    def _create_main_tab(self):
        """Main control tab"""

        # Account selection (quick access)
        quick_frame = ttk.LabelFrame(self.main_tab, text="⚡ 快速启动", padding="15")
        quick_frame.pack(fill=tk.X, pady=(0, 15))

        row1 = ttk.Frame(quick_frame)
        row1.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row1, text="账户:").pack(side=tk.LEFT)
        self.account_combo = ttk.Combobox(
            row1, textvariable=self.selected_account, state="readonly", width=30
        )
        self.account_combo.pack(side=tk.LEFT, padx=(10, 20))

        ttk.Label(row1, text="模式:").pack(side=tk.LEFT)
        ttk.Radiobutton(
            row1, text="无头模式", variable=self.run_mode, value="headless"
        ).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(
            row1, text="可视化", variable=self.run_mode, value="debug"
        ).pack(side=tk.LEFT)

        # Large buttons
        btn_frame = ttk.Frame(quick_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.start_btn = tk.Button(
            btn_frame,
            text="▶️ 启动",
            command=self._start,
            bg=COLORS["success"],
            fg="white",
            font=("Segoe UI", 14, "bold"),
            height=2,
            width=15,
            cursor="hand2",
            activebackground=COLORS["accent"],
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹️ 停止",
            command=self._stop,
            bg=COLORS["error"],
            fg="white",
            font=("Segoe UI", 14, "bold"),
            height=2,
            width=15,
            cursor="hand2",
            state=tk.DISABLED,
            activebackground=COLORS["accent_hover"],
        )
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Info cards
        info_frame = ttk.Frame(self.main_tab)
        info_frame.pack(fill=tk.X, pady=(15, 0))

        # API Info
        api_card = ttk.LabelFrame(info_frame, text="🌐 API 信息", padding="10")
        api_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.api_url_label = ttk.Label(
            api_card, text=f"http://127.0.0.1:{self.fastapi_port.get()}"
        )
        self.api_url_label.pack(anchor=tk.W)

        api_btn_frame = ttk.Frame(api_card)
        api_btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(api_btn_frame, text="🔍 测试", command=self._api_test).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            api_btn_frame, text="🌐 在浏览器中打开", command=self._open_in_browser
        ).pack(side=tk.LEFT)

        # Status card
        status_card = ttk.LabelFrame(info_frame, text="📊 状态", padding="10")
        status_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.status_details = ttk.Label(status_card, text="服务已停止")
        self.status_details.pack(anchor=tk.W)

        self.pid_label = ttk.Label(status_card, text="PID: -")
        self.pid_label.pack(anchor=tk.W)

    def _create_account_tab(self):
        """Account management tab"""

        # Account list
        list_frame = ttk.LabelFrame(
            self.account_tab, text="📋 已保存的账户", padding="10"
        )
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Listbox
        self.account_listbox = tk.Listbox(
            list_frame,
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            font=("Consolas", 11),
            height=10,
        )
        self.account_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Account buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="➕ 添加新账户", command=self._add_new_account).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="🗑️ 删除所选", command=self._delete_account).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="🔄 刷新", command=self._load_accounts).pack(
            side=tk.LEFT
        )

        # Account details
        detail_frame = ttk.LabelFrame(self.account_tab, text="ℹ️ 账户详情", padding="10")
        detail_frame.pack(fill=tk.X)

        self.account_detail = ttk.Label(detail_frame, text="选择一个账户查看详情")
        self.account_detail.pack(anchor=tk.W)

        # Listbox selection event
        self.account_listbox.bind("<<ListboxSelect>>", self._account_selected)

    def _create_settings_tab(self):
        """Settings tab"""

        # Port settings
        port_frame = ttk.LabelFrame(self.settings_tab, text="🔌 端口设置", padding="10")
        port_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(port_frame)
        row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(row1, text="FastAPI 端口:").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.fastapi_port, width=10).pack(
            side=tk.LEFT, padx=(10, 20)
        )

        ttk.Label(row1, text="流端口:").pack(side=tk.LEFT)
        ttk.Entry(row1, textvariable=self.stream_port, width=10).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # Proxy settings
        proxy_frame = ttk.LabelFrame(
            self.settings_tab, text="🌍 代理设置", padding="10"
        )
        proxy_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(proxy_frame, text="启用代理", variable=self.proxy_enabled).pack(
            anchor=tk.W
        )

        proxy_row = ttk.Frame(proxy_frame)
        proxy_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(proxy_row, text="地址:").pack(side=tk.LEFT)
        ttk.Entry(proxy_row, textvariable=self.proxy_address, width=40).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        ttk.Label(
            proxy_frame,
            text="示例: http://127.0.0.1:7890",
            foreground=COLORS["text_secondary"],
        ).pack(anchor=tk.W, pady=(5, 0))

        # Save button
        save_frame = ttk.Frame(self.settings_tab)
        save_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(save_frame, text="💾 保存设置", command=self._save_and_notify).pack(
            side=tk.LEFT
        )
        ttk.Button(save_frame, text="🔄 恢复默认", command=self._reset_config).pack(
            side=tk.LEFT, padx=(10, 0)
        )

    def _create_log_tab(self):
        """Log tab"""

        # Log area
        self.log_area = scrolledtext.ScrolledText(
            self.log_tab,
            height=20,
            state=tk.DISABLED,
            font=("Consolas", 9),
            bg=COLORS["bg_light"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Log buttons
        btn_frame = ttk.Frame(self.log_tab)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="🗑️ 清空", command=self._clear_logs).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="💾 保存到文件", command=self._save_logs).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="📂 打开日志文件", command=self._open_log_file).pack(
            side=tk.LEFT
        )

    def _log(self, message: str, save_to_file: bool = True):
        """Add message to log area"""
        # Strip ANSI escape codes
        clean_message = re.sub(r'\x1b\[[0-9;]*m', '', message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {clean_message}"

        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{formatted}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

        if save_to_file:
            try:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{formatted}\n")
            except Exception:
                pass

    def _clear_logs(self):
        """Clear log area"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

    def _save_logs(self):
        """Save logs to file"""
        try:
            log_content = self.log_area.get(1.0, tk.END)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = SCRIPT_DIR / "logs" / f"session_{timestamp}.log"
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, "w", encoding="utf-8") as f:
                f.write(log_content)

            self._log(f"✅ 日志已保存: {save_path.name}")
            messagebox.showinfo("成功", f"日志已保存:\n{save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"日志保存失败:\n{e}")

    def _open_log_file(self):
        """Open log file"""
        try:
            if platform.system() == "Linux":
                subprocess.Popen(["xdg-open", str(LOG_FILE.parent)])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(LOG_FILE.parent)])
            else:
                os.startfile(str(LOG_FILE.parent))
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹:\n{e}")

    def _load_accounts(self):
        """Load saved accounts"""
        accounts = []

        if SAVED_AUTH_DIR.exists():
            for file in sorted(SAVED_AUTH_DIR.glob("*.json")):
                if file.name != ".gitkeep":
                    accounts.append(file.stem)

        # Update combobox
        self.account_combo["values"] = accounts

        # Update listbox
        self.account_listbox.delete(0, tk.END)
        for acc in accounts:
            self.account_listbox.insert(tk.END, f"  📧 {acc}")

        # Select last account
        last = self.config.get("last_account", "")
        if last and last in accounts:
            self.selected_account.set(last)
            try:
                idx = accounts.index(last)
                self.account_listbox.selection_set(idx)
            except Exception:
                pass
        elif accounts:
            self.selected_account.set(accounts[0])

        if accounts:
            self._log(f"✅ 已加载 {len(accounts)} 个账户")
        else:
            self._log("⚠️ 未找到已保存的账户")

    def _account_selected(self, event):
        """Show details when account is selected"""
        selection = self.account_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        account_name = self.account_listbox.get(idx).replace("  📧 ", "")

        # Read file info
        auth_file = SAVED_AUTH_DIR / f"{account_name}.json"
        if auth_file.exists():
            stat = auth_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            size_kb = stat.st_size / 1024

            self.account_detail.config(
                text=f"📁 文件: {account_name}.json\n"
                f"📅 修改时间: {mod_time}\n"
                f"📊 大小: {size_kb:.1f} KB"
            )

        # Update combobox as well
        self.selected_account.set(account_name)

    def _add_new_account(self):
        """Add new account"""
        file_name = simpledialog.askstring(
            "新账户",
            "输入账户名称\n(例如: my_gmail_account):",
            parent=self.root,
        )

        if not file_name:
            return

        if not file_name.replace("_", "").replace("-", "").isalnum():
            messagebox.showerror("错误", "只允许使用字母、数字、- 和 _ ！")
            return

        self._log(f"🔐 正在添加新账户: {file_name}")
        self._log("📌 浏览器将打开，请登录您的 Google 账户")
        self._log("📌 登录后，账户将自动保存")

        self._start_internal(mode="debug", save_auth_as=file_name, exit_on_save=True)

    def _delete_account(self):
        """Delete selected account"""
        selection = self.account_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的账户")
            return

        idx = selection[0]
        account_name = self.account_listbox.get(idx).replace("  📧 ", "")

        if not messagebox.askyesno("确认", f"确定要删除 '{account_name}' 吗？"):
            return

        try:
            auth_file = SAVED_AUTH_DIR / f"{account_name}.json"
            if auth_file.exists():
                auth_file.unlink()

            # Also delete from active
            active_file = ACTIVE_AUTH_DIR / f"{account_name}.json"
            if active_file.exists():
                active_file.unlink()

            self._log(f"🗑️ 账户已删除: {account_name}")
            self._load_accounts()

        except Exception as e:
            messagebox.showerror("错误", f"账户删除失败:\n{e}")

    def _api_test(self):
        """Test the API"""
        port = self.fastapi_port.get()
        url = f"http://127.0.0.1:{port}/health"

        self._log(f"🔍 正在测试 API: {url}")

        try:
            import urllib.request

            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    self._log("✅ API 正在运行！")
                    self.status_details.config(text="✅ API 已激活并响应")
                    messagebox.showinfo("成功", "API 正在运行！ ✅")
                else:
                    self._log(f"⚠️ API 响应状态码: {response.status}")
        except urllib.error.URLError:
            self._log("❌ 无法连接到 API，服务可能未运行。")
            self.status_details.config(text="❌ API 无响应")
            messagebox.showwarning("警告", "无法连接到 API。\n服务是否正在运行？")
        except Exception as e:
            self._log(f"❌ API 测试错误: {e}")

    def _open_in_browser(self):
        """Open API in browser"""
        port = self.fastapi_port.get()
        webbrowser.open(f"http://127.0.0.1:{port}")

    def _save_and_notify(self):
        """Save settings and notify"""
        self._save_config()
        self._log("💾 设置已保存")
        messagebox.showinfo("成功", "设置已保存！")

        # Update API URL
        self.api_url_label.config(text=f"http://127.0.0.1:{self.fastapi_port.get()}")

    def _reset_config(self):
        """Reset to default settings"""
        if messagebox.askyesno("确认", "所有设置将恢复为默认值，是否继续？"):
            self.fastapi_port.set(str(DEFAULT_CONFIG["fastapi_port"]))
            self.stream_port.set(str(DEFAULT_CONFIG["stream_port"]))
            self.proxy_address.set("")
            self.proxy_enabled.set(False)
            self._save_config()
            self._log("🔄 设置已恢复为默认值")

    def _is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return False
            except OSError:
                return True

    def _find_port_pids(self, port: int) -> List[int]:
        """Find PIDs using the port"""
        pids = []
        try:
            if platform.system() == "Linux":
                result = subprocess.run(
                    ["lsof", "-t", "-i", f":{port}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.stdout.strip():
                    pids = [int(p) for p in result.stdout.strip().split("\n") if p]
            elif platform.system() == "Windows":
                result = subprocess.run(
                    ["netstat", "-ano"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                for line in result.stdout.split("\n"):
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.split()
                        if parts:
                            try:
                                pids.append(int(parts[-1]))
                            except ValueError:
                                pass
        except Exception as e:
            self._log(f"⚠️ 无法找到端口 PID: {e}")
        return list(set(pids))

    def _clean_node_processes(self):
        """Clean all node processes"""
        self._log("🧹 正在自动清理可能残留的 Node 进程...")
        try:
            if platform.system() == "Windows":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "node.exe", "/T"],
                    capture_output=True,
                    timeout=5,
                )
            else:
                subprocess.run(
                    ["killall", "-9", "node"],
                    capture_output=True,
                    timeout=5,
                )
            time.sleep(1)
        except Exception as e:
            self._log(f"⚠️ 清理 Node 进程异常: {e}")

    def _clean_ports(self) -> bool:
        """Clean ports"""
        self._clean_node_processes()
        
        ports = [
            int(self.fastapi_port.get() or 2048),
            9222,  # Camoufox
            int(self.stream_port.get() or 3120),
        ]
        cleaned = True

        for port in ports:
            if self._is_port_in_use(port):
                self._log(f"🔍 端口 {port} 已被占用，正在清理...")
                pids = self._find_port_pids(port)

                for pid in pids:
                    try:
                        if platform.system() == "Windows":
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(pid)],
                                capture_output=True,
                                timeout=5,
                            )
                        else:
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(0.5)
                            try:
                                os.kill(pid, 0)
                                os.kill(pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        self._log(f"   ✅ PID {pid} 已终止")
                    except Exception as e:
                        self._log(f"   ❌ PID {pid}: {e}")
                        cleaned = False

                time.sleep(1)
                if self._is_port_in_use(port):
                    self._log(f"   ❌ 端口 {port} 仍然被占用！")
                    cleaned = False

        return cleaned

    def _start(self):
        """Start the service"""
        if self.running:
            messagebox.showwarning("警告", "服务已在运行中！")
            return

        account = self.selected_account.get()
        if not account:
            messagebox.showerror("错误", "请选择一个账户！")
            return

        # Save last account
        self.config["last_account"] = account
        self._save_config()

        mode = self.run_mode.get()
        self._start_internal(mode=mode, account=account)

    def _start_internal(
        self,
        mode: str,
        account: str = None,
        save_auth_as: str = None,
        exit_on_save: bool = False,
    ):
        """Internal start function"""

        self._log("🔍 正在检查端口...")
        if not self._clean_ports():
            if not messagebox.askyesno("警告", "部分端口无法清理，是否继续？"):
                self._log("❌ 用户已取消")
                return

        # Build command
        # Use poetry if we are not currently in a virtual environment to ensure dependencies like uvicorn are found
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if not in_venv and shutil.which("poetry"):
            cmd = ["poetry", "run", "python", str(LAUNCH_SCRIPT)]
        else:
            cmd = [sys.executable, str(LAUNCH_SCRIPT)]

        if mode == "headless":
            cmd.append("--headless")
        elif mode == "debug":
            cmd.append("--debug")

        # Port settings
        cmd.extend(["--server-port", self.fastapi_port.get()])
        cmd.extend(["--stream-port", self.stream_port.get()])

        # Account
        if account:
            auth_file = SAVED_AUTH_DIR / f"{account}.json"
            if auth_file.exists():
                cmd.extend(["--active-auth-json", str(auth_file)])

        # Save
        if save_auth_as:
            cmd.extend(["--save-auth-as", save_auth_as])
            cmd.append("--auto-save-auth")

        if exit_on_save:
            cmd.append("--exit-on-auth-save")

        # Proxy
        if self.proxy_enabled.get() and self.proxy_address.get():
            cmd.extend(["--internal-camoufox-proxy", self.proxy_address.get()])

        self._log(f"🚀 正在启动: {mode} 模式")

        # Environment variables
        env = os.environ.copy()
        env["DIRECT_LAUNCH"] = "true"
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"

        # When saving auth (new account), skip manual Enter prompt after login
        # Login completion will be detected automatically by URL change
        if save_auth_as:
            env["SUPPRESS_LOGIN_WAIT"] = "true"

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE if save_auth_as else None,
                text=True,
                encoding="utf-8",
                bufsize=1,
                cwd=str(SCRIPT_DIR),
                env=env,
            )

            self.running = True
            self.status.set("🟢 运行中")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_details.config(text="服务已启动")
            self.pid_label.config(text=f"PID: {self.process.pid}")

            self.tray.update_status(True)

            self.log_thread = threading.Thread(target=self._read_logs, daemon=True)
            self.log_thread.start()

            self._log(f"✅ 服务已启动 (PID: {self.process.pid})")

        except Exception as e:
            self._log(f"❌ 启动错误: {e}")
            messagebox.showerror("错误", f"无法启动:\n{e}")
            self.running = False

    def _read_logs(self):
        """Log reading thread"""
        try:
            while self.process:
                line = self.process.stdout.readline()
                if not line:
                    break
                self.root.after(
                    0,
                    lambda log_line=line.strip(): self._log(
                        log_line, save_to_file=False
                    ),
                )

            if self.process:
                self.process.wait()
                exit_code = self.process.returncode
            else:
                exit_code = -1
                
            self.root.after(0, lambda: self._service_ended(exit_code))
        except Exception as e:
            self.root.after(0, lambda err=e: self._log(f"❌ 日志错误: {err}"))

    def _service_ended(self, exit_code: int):
        """When service ends"""
        self.running = False
        self.process = None

        if exit_code == 0:
            self.status.set("⚪ 已停止")
            self._log("✅ 服务正常结束")
        else:
            self.status.set(f"🔴 错误 ({exit_code})")
            self._log(f"⚠️ 服务异常停止: {exit_code}")

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_details.config(text="服务已停止")
        self.pid_label.config(text="PID: -")

        self.tray.update_status(False)

        # Refresh account list (important after adding new account)
        self._load_accounts()
        self._log("🔄 账户列表已刷新")

    def _stop(self):
        """Stop the service"""
        if not self.running or not self.process:
            return

        self._log("🛑 正在停止...")
        self.status.set("🟡 停止中...")

        try:
            if platform.system() == "Windows":
                self.process.terminate()
            else:
                self.process.send_signal(signal.SIGINT)

            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._log("⚠️ 强制关闭中...")
                self.process.kill()
                self.process.wait(timeout=3)

            self._log("✅ 已停止")
        except Exception as e:
            self._log(f"❌ 停止错误: {e}")

        self._service_ended(0)

    def _show_window(self):
        """Show window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _minimize_to_tray(self):
        """Minimize to tray"""
        if self.tray.supported and self.running:
            self.root.withdraw()
            self._log("📌 已最小化到系统托盘")
        else:
            self._close_completely()

    def _close_completely(self):
        """Close completely"""
        if self.running:
            if messagebox.askyesno("确认", "服务正在运行，是否停止并退出？"):
                self._stop()
            else:
                return

        self._save_config()
        self.tray.stop()
        self.root.destroy()

    def run(self):
        """Run the application"""
        self._log("🚀 AI Studio 代理简易启动器已就绪")
        self.root.mainloop()


def main():
    """Main function"""
    SAVED_AUTH_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_AUTH_DIR.mkdir(parents=True, exist_ok=True)

    app = SimpleGUILauncher()
    app.run()


if __name__ == "__main__":
    main()
