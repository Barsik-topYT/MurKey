"""WinActivator 2.2 — активация Windows 10/11 (GUI и CLI). by BarsikYT"""
import sys
import os
import time
import ctypes
import winreg
import subprocess
import threading

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import i18n
from colorama import init, Fore, Style

init(autoreset=True)

WINACTIVATOR_MANUAL = [
    ("Windows 11 Pro", "W269N-WFGWX-YVC9B-4J6C9-T83GX", "11", "Pro"),
    ("Windows 11 Home", "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99", "11", "Home"),
    ("Windows 11 Education", "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2", "11", "Education"),
    ("Windows 11 Enterprise", "NPPR9-FWDCX-D2C8J-H872K-2YT43", "11", "Enterprise"),
    ("Windows 10 Pro", "W269N-WFGWX-YVC9B-4J6C9-T83GX", "10", "Pro"),
    ("Windows 10 Home", "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99", "10", "Home"),
    ("Windows 10 Education", "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2", "10", "Education"),
    ("Windows 10 Enterprise", "NPPR9-FWDCX-D2C8J-H872K-2YT43", "10", "Enterprise"),
]

LANGUAGES = {
    'ru': {
        'gui': {
            'window_title': 'WinActivator 2.2',
            'subtitle': 'Активация Windows 10 / 11',
            'version_label': 'Версия 2.2',
            'wa_system': 'Редакция',
            'wa_auto': 'Автоактивация',
            'wa_manual': 'Ручная (выбор версии)',
            'wa_check': 'Проверить статус',
            'wa_log': 'Журнал',
            'wa_confirm': 'Начать активацию Windows? Требуются права администратора.',
            'confirm': 'Подтверждение',
            'done': 'Готово',
            'error': 'Ошибка',
            'language': 'Язык',
            'exit': 'Выход',
            'lang_changed': 'Язык интерфейса обновлён.',
            'admin_ok': 'Запущено с правами администратора',
            'no_admin': 'Нужны права администратора',
        },
    },
    'en': {
        'gui': {
            'window_title': 'WinActivator 2.2',
            'subtitle': 'Windows 10 / 11 activation',
            'version_label': 'Version 2.2',
            'wa_system': 'Edition',
            'wa_auto': 'Auto activate',
            'wa_manual': 'Manual (pick version)',
            'wa_check': 'Check status',
            'wa_log': 'Log',
            'wa_confirm': 'Start Windows activation? Administrator rights required.',
            'confirm': 'Confirm',
            'done': 'Done',
            'error': 'Error',
            'language': 'Language',
            'exit': 'Exit',
            'lang_changed': 'Interface language updated.',
            'admin_ok': 'Running as administrator',
            'no_admin': 'Administrator rights required',
        },
    },
}


def t_gui(key):
    lang = i18n.get_language()
    return LANGUAGES.get(lang, LANGUAGES['ru'])['gui'].get(key, key)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def winactivator_get_windows_info():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
        )
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        try:
            release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
        except OSError:
            try:
                release_id = winreg.QueryValueEx(key, "CurrentBuild")[0]
            except OSError:
                release_id = "?"
        winreg.CloseKey(key)

        edition = "Unknown"
        if "Pro" in product_name or "Professional" in product_name:
            edition = "Pro"
        elif "Home" in product_name:
            edition = "Home"
        elif "Education" in product_name:
            edition = "Education"
        elif "Enterprise" in product_name:
            edition = "Enterprise"
        elif "Core" in product_name:
            edition = "Home"

        version = "?"
        if "Windows 11" in product_name:
            version = "11"
        elif "Windows 10" in product_name:
            version = "10"

        return {
            "version": version,
            "edition": edition,
            "full_name": product_name,
            "release_id": str(release_id),
        }
    except Exception:
        return None


def winactivator_select_key(windows_info):
    version_keys = {
        '11': {
            'Pro': 'W269N-WFGWX-YVC9B-4J6C9-T83GX',
            'Home': 'TX9XD-98N7V-6WMQ6-BX7FG-H8Q99',
            'Education': 'NW6C2-QMPVW-D7KKK-3GKT6-VCFB2',
            'Enterprise': 'NPPR9-FWDCX-D2C8J-H872K-2YT43',
        },
        '10': {
            'Pro': 'W269N-WFGWX-YVC9B-4J6C9-T83GX',
            'Home': 'TX9XD-98N7V-6WMQ6-BX7FG-H8Q99',
            'Education': 'NW6C2-QMPVW-D7KKK-3GKT6-VCFB2',
            'Enterprise': 'NPPR9-FWDCX-D2C8J-H872K-2YT43',
        },
    }
    version = windows_info['version']
    edition = windows_info['edition']
    if version in version_keys:
        if edition in version_keys[version]:
            return version_keys[version][edition]
        for fallback in ('Pro', 'Home'):
            if fallback in version_keys[version]:
                return version_keys[version][fallback]
    return 'W269N-WFGWX-YVC9B-4J6C9-T83GX'


def winactivator_activate(windows_info, product_key, log_fn=None):
    def log(msg):
        if log_fn:
            log_fn(msg)

    try:
        log(f"Система: {windows_info['full_name']}")
        log(f"Ключ: {product_key}")
        log("1/4 Установка ключа...")
        result = subprocess.run(
            ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/ipk', product_key],
            capture_output=True, text=True,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        if result.returncode != 0 and "successfully" not in (result.stdout or "").lower():
            log("   Альтернативный метод...")
            subprocess.run(
                ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/ipk', product_key],
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        else:
            log("   Ключ установлен")

        log("2/4 Настройка KMS...")
        for kms in ('kms.digiboy.ir', 'kms8.msguides.com', 'kms.lotro.cc'):
            result = subprocess.run(
                ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/skms', kms],
                capture_output=True, text=True, timeout=15,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
            if result.returncode == 0 or "set to" in (result.stdout or "").lower():
                log(f"   KMS: {kms}")
                break

        log("3/4 Активация...")
        subprocess.run(
            ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/ato'],
            capture_output=True, text=True, timeout=30,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        log("4/4 Проверка...")
        result = subprocess.run(
            ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/xpr'],
            capture_output=True, text=True, timeout=15,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        if result.stdout:
            log(result.stdout.strip())
        log("Активация завершена.")
        return True
    except Exception as e:
        log(f"Ошибка: {e}")
        return False


def winactivator_check_status(log_fn=None):
    try:
        result = subprocess.run(
            ['cscript', '//nologo', r'C:\Windows\System32\slmgr.vbs', '/xpr'],
            capture_output=True, text=True, timeout=15,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
        )
        text = (result.stdout or result.stderr or "Нет данных").strip()
        if log_fn:
            log_fn(text)
        return text
    except Exception as e:
        if log_fn:
            log_fn(str(e))
        return str(e)


def launch_cli():
    """Консольный режим WinActivator 2.2"""
    if not is_admin():
        from gui_utils import run_as_admin_elevate
        run_as_admin_elevate(gui=False, extra_args="--cli")
        return

    def print_header():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
    {Fore.WHITE}{'═' * 60}{Style.RESET_ALL}
    {Fore.YELLOW}{Style.BRIGHT}{'W I N A C T I V A T O R  2.2'.center(60)}{Style.RESET_ALL}
    {Fore.GREEN}{'by BarsikYT'.center(60)}{Style.RESET_ALL}
    {Fore.WHITE}{'═' * 60}{Style.RESET_ALL}
        """)

    while True:
        print_header()
        windows_info = winactivator_get_windows_info()
        if windows_info:
            print(f"\n{Fore.CYAN}  • {windows_info['full_name']}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  • {windows_info['edition']} | Build {windows_info['release_id']}{Style.RESET_ALL}")

        print(f"\n{Fore.WHITE}[1] Автоактивация  [2] Ручная  [3] Статус  [0] Выход{Style.RESET_ALL}")
        choice = input(f"\n{Fore.CYAN}➤ {Style.RESET_ALL}").strip()

        if choice == '1':
            if not windows_info:
                print(f"{Fore.RED}Не удалось определить Windows{Style.RESET_ALL}")
            else:
                key = winactivator_select_key(windows_info)
                confirm = input(f"Ключ {key}. Начать? (y/n): ").lower()
                if confirm in ('y', 'д', 'н'):
                    winactivator_activate(windows_info, key, log_fn=print)
            input("\nEnter...")
        elif choice == '2':
            for i, (name, key, _, _) in enumerate(WINACTIVATOR_MANUAL, 1):
                print(f"  [{i}] {name}")
            c = input("Номер: ").strip()
            if c.isdigit() and 1 <= int(c) <= len(WINACTIVATOR_MANUAL):
                name, key, ver, edition = WINACTIVATOR_MANUAL[int(c) - 1]
                info = {"full_name": name, "version": ver, "edition": edition, "release_id": "?"}
                winactivator_activate(info, key, log_fn=print)
            input("\nEnter...")
        elif choice == '3':
            winactivator_check_status(log_fn=print)
            input("\nEnter...")
        elif choice == '0':
            break


def launch_gui():
    if not is_admin():
        from gui_utils import run_as_admin_elevate
        run_as_admin_elevate(gui=True)
        return

    from gui_utils import hide_console, apply_window_icon
    hide_console()

    try:
        import customtkinter as ctk
        from tkinter import messagebox
    except ImportError:
        print("Установите: pip install customtkinter")
        launch_cli()
        return

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    ACCENT = "#6366f1"
    ACCENT_HOVER = "#4f46e5"
    CARD = "#1e293b"
    SIDEBAR = "#0f172a"
    LOG_BG = "#111827"

    class WinActivatorApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title(t_gui('window_title'))
            self.geometry("720x560")
            self.minsize(640, 480)
            self.configure(fg_color="#0b1220")
            apply_window_icon(self, "murtools")
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)
            self._build_sidebar()
            self._build_main()

        def _build_sidebar(self):
            side = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=SIDEBAR)
            side.grid(row=0, column=0, sticky="ns")
            side.grid_propagate(False)
            inner = ctk.CTkFrame(side, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=14)
            inner.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                inner, text="WinActivator", font=ctk.CTkFont(size=20, weight="bold"), text_color=ACCENT,
            ).grid(row=0, column=0, sticky="ew")
            ctk.CTkLabel(
                inner, text=t_gui('subtitle'), font=ctk.CTkFont(size=11), text_color="#94a3b8",
            ).grid(row=1, column=0, sticky="ew", pady=(2, 2))
            ctk.CTkLabel(
                inner, text=t_gui('version_label'), font=ctk.CTkFont(size=10), text_color="#64748b",
            ).grid(row=2, column=0, sticky="ew", pady=(0, 12))

            admin_txt = t_gui('admin_ok') if is_admin() else t_gui('no_admin')
            admin_clr = "#22c55e" if is_admin() else "#ef4444"
            ctk.CTkLabel(inner, text=f"● {admin_txt}", text_color=admin_clr, anchor="w").grid(
                row=3, column=0, sticky="ew", pady=(0, 8),
            )

            inner.grid_rowconfigure(4, weight=1)
            self.lang_menu = ctk.CTkOptionMenu(
                inner, values=list(i18n.LANG_OPTIONS.values()),
                command=self._change_language, fg_color=CARD,
                button_color=ACCENT, button_hover_color=ACCENT_HOVER,
            )
            self.lang_menu.set(i18n.CODE_TO_LABEL[i18n.get_language()])
            self.lang_menu.grid(row=5, column=0, sticky="ew", pady=(0, 6))
            ctk.CTkButton(
                inner, text=t_gui('exit'), fg_color="#334155", hover_color="#475569",
                command=self.destroy,
            ).grid(row=6, column=0, sticky="ew")

        def _build_main(self):
            if hasattr(self, 'main_frame'):
                self.main_frame.destroy()
            self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.main_frame.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid_rowconfigure(4, weight=1)

            self.info = winactivator_get_windows_info()
            info_text = (
                f"{self.info['full_name']}\n"
                f"{t_gui('wa_system')}: {self.info['edition']} | Build {self.info['release_id']}"
                if self.info else "Windows: ?"
            )
            ctk.CTkLabel(self.main_frame, text=info_text, justify="left", font=ctk.CTkFont(size=13)).grid(
                row=0, column=0, sticky="w", pady=(0, 8),
            )

            self.version_var = ctk.StringVar(value=WINACTIVATOR_MANUAL[0][0])
            ctk.CTkOptionMenu(
                self.main_frame, variable=self.version_var,
                values=[x[0] for x in WINACTIVATOR_MANUAL],
                width=400, fg_color=CARD,
            ).grid(row=1, column=0, sticky="w", pady=8)

            btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            btn_frame.grid(row=2, column=0, sticky="w", pady=8)
            ctk.CTkButton(
                btn_frame, text=t_gui('wa_auto'), fg_color=ACCENT, hover_color=ACCENT_HOVER,
                command=self._auto_activate,
            ).pack(side="left", padx=(0, 8))
            ctk.CTkButton(
                btn_frame, text=t_gui('wa_manual'), fg_color=CARD, hover_color=ACCENT,
                command=self._manual_activate,
            ).pack(side="left", padx=8)
            ctk.CTkButton(
                btn_frame, text=t_gui('wa_check'), fg_color=CARD, hover_color=ACCENT,
                command=self._check,
            ).pack(side="left", padx=8)

            ctk.CTkLabel(self.main_frame, text=t_gui('wa_log'), anchor="w").grid(
                row=3, column=0, sticky="w", pady=(8, 4),
            )
            self.log_box = ctk.CTkTextbox(
                self.main_frame, fg_color=LOG_BG, font=ctk.CTkFont(family="Consolas", size=12),
            )
            self.log_box.grid(row=4, column=0, sticky="nsew")

        def _log(self, msg):
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")

        def _run(self, task):
            def worker():
                try:
                    task()
                except Exception as e:
                    self.after(0, lambda: self._log(f"{t_gui('error')}: {e}"))
            threading.Thread(target=worker, daemon=True).start()

        def _change_language(self, choice):
            i18n.set_language_from_label(choice)
            self.title(t_gui('window_title'))
            self.lang_menu.set(i18n.CODE_TO_LABEL[i18n.get_language()])
            self._build_main()
            messagebox.showinfo(t_gui('done'), t_gui('lang_changed'))

        def _auto_activate(self):
            if not self.info:
                messagebox.showerror(t_gui('error'), "Windows info unavailable")
                return
            if not messagebox.askyesno(t_gui('confirm'), t_gui('wa_confirm')):
                return
            key = winactivator_select_key(self.info)

            def task():
                self.after(0, lambda: self._log("--- Auto ---"))
                winactivator_activate(
                    self.info, key,
                    log_fn=lambda m: self.after(0, lambda x=m: self._log(x)),
                )

            self._run(task)

        def _manual_activate(self):
            if not messagebox.askyesno(t_gui('confirm'), t_gui('wa_confirm')):
                return
            name = self.version_var.get()
            match = next((x for x in WINACTIVATOR_MANUAL if x[0] == name), None)
            if not match:
                return
            _, key, ver, edition = match
            info = {"full_name": name, "version": ver, "edition": edition, "release_id": "?"}

            def task():
                self.after(0, lambda: self._log(f"--- {name} ---"))
                winactivator_activate(
                    info, key,
                    log_fn=lambda m: self.after(0, lambda x=m: self._log(x)),
                )

            self._run(task)

        def _check(self):
            def task():
                self.after(0, lambda: self._log("--- Status ---"))
                winactivator_check_status(
                    log_fn=lambda m: self.after(0, lambda x=m: self._log(x)),
                )

            self._run(task)

    app = WinActivatorApp()
    app.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--cli", "-c", "cli"):
        launch_cli()
    else:
        launch_gui()
