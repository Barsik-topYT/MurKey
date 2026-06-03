"""Утилиты для GUI-режима: скрытие консоли и запуск без окна терминала."""
import os
import sys
import ctypes

SW_HIDE = 0
CREATE_NO_WINDOW = 0x08000000


def hide_console():
    """Скрывает окно консоли на Windows."""
    if sys.platform != "win32":
        return
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, SW_HIDE)
    except Exception:
        pass


def get_gui_python_executable():
    """Возвращает pythonw.exe для запуска без консоли."""
    if getattr(sys, "frozen", False):
        return sys.executable
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        pythonw = exe[:-10] + "pythonw.exe"
        if os.path.isfile(pythonw):
            return pythonw
    return exe


def build_script_params(extra_args=None):
    """Собирает параметры командной строки для перезапуска скрипта."""
    if getattr(sys, "frozen", False):
        params = ""
    else:
        params = f'"{os.path.abspath(sys.argv[0])}"'
    if extra_args:
        params = f"{params} {extra_args}".strip()
    return params


def run_as_admin_elevate(gui=True, extra_args=None):
    """Перезапуск с правами администратора (pythonw + скрытое окно в GUI-режиме)."""
    exe = get_gui_python_executable() if gui else sys.executable
    params = build_script_params(extra_args)
    show_cmd = SW_HIDE if gui else 1
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, show_cmd)
    sys.exit(0)


def show_admin_message(title, message):
    """Показывает предупреждение о правах администратора без основного окна."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showwarning(title, message, parent=root)
        root.destroy()
    except Exception:
        pass


def popen_hidden(args, **kwargs):
    """subprocess.Popen без всплывающего окна консоли."""
    if sys.platform == "win32":
        kwargs.setdefault("creationflags", CREATE_NO_WINDOW)
    return __import__("subprocess").Popen(args, **kwargs)


def get_assets_dir():
    """Папка assets (рядом со скриптами или внутри EXE PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def get_icon_path(name):
    """Путь к иконке: name = 'murtools' | 'murblocker'."""
    assets = get_assets_dir()
    for ext in (".ico", ".png"):
        path = os.path.join(assets, f"{name}_icon{ext}")
        if os.path.isfile(path):
            return path
    return None


def apply_window_icon(window, name):
    """Устанавливает иконку окна (taskbar + заголовок)."""
    path = get_icon_path(name)
    if not path:
        return False
    try:
        if path.lower().endswith(".ico"):
            window.iconbitmap(path)
            return True
        from tkinter import PhotoImage
        img = PhotoImage(file=path)
        window.iconphoto(True, img)
        window._murtools_icon_ref = img
        return True
    except Exception:
        return False
