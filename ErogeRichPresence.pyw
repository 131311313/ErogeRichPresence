import time
import json
from pypresence import Presence
import pystray
from PIL import Image
import threading
import sys
import os
import ctypes
from ctypes import wintypes

GAMES = {
    "HENPRI.exe": {
        "jp": "ヘンタイプリズン",
        "en": "Hentai Prison"
    },
    "dohnadohna.exe": {
        "jp": "ドーナドーナ",
        "en": "Dohna Dohna: Let's Do Bad Things Together"
    },
}

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
psapi = ctypes.WinDLL('psapi', use_last_error=True)

def find_process_by_name(process_name):
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == -1:
        return None
    
    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * 260)
        ]
    
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    if not kernel32.Process32First(snapshot, ctypes.byref(pe32)):
        kernel32.CloseHandle(snapshot)
        return None
    
    while True:
        if pe32.szExeFile.decode('utf-8', errors='ignore') == process_name:
            kernel32.CloseHandle(snapshot)
            return pe32.th32ProcessID
        if not kernel32.Process32Next(snapshot, ctypes.byref(pe32)):
            break
    
    kernel32.CloseHandle(snapshot)
    return None

class ErogeRichPresence:
    def __init__(self):
        self.rpc = None
        self.current_game = None
        self.config = self.load_config()
        self.language = self.config.get("language", "jp")
        self.client_ids = {
            "HENPRI.exe": {
                "jp": "1414899272129843233",
                "en": "1414920530485575745"
            },
            "dohnadohna.exe": {
                "jp": "1414922716535980063",
                "en": "1414923130211663893"
            }
        }
        self.last_pid = None
    
    def load_config(self):
        if getattr(sys, 'frozen', False):
            config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
        else:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            default_config = {"language": "jp"}
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        if getattr(sys, 'frozen', False):
            config_path = os.path.join(os.path.dirname(sys.executable), "config.json")
        else:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def add_to_startup(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            exe_path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
            winreg.SetValueEx(key, "ErogeRichPresence", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Startup add error: {e}")
            return False
    
    def remove_from_startup(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "ErogeRichPresence")
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Startup remove error: {e}")
            return False
    
    def is_in_startup(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run", 
                               0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "ErogeRichPresence")
            winreg.CloseKey(key)
            return True
        except:
            return False
    
    def find_games(self):
        for game_name in GAMES.keys():
            pid = find_process_by_name(game_name)
            if pid:
                return game_name, pid
        return None, None
    
    def connect(self, game_exe):
        try:
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
            client_id = self.get_client_id(game_exe)
            self.rpc = Presence(client_id)
            self.rpc.connect()
            print(f"Connected for {game_exe}")
            return True
        except Exception as e:
            print(f"Connect error: {e}")
            self.rpc = None
            return False
    
    def update(self, game_exe):
        if not self.rpc:
            return
        
        game_name = GAMES[game_exe][self.language]
        state = f"{game_name}をプレイ中" if self.language == 'jp' else f"Playing {game_name}"
        
        try:
            self.rpc.update(state=state, large_image="icon")
            print(f"Updated: {state}")
        except Exception as e:
            print(f"Update error: {e}")
    
    def get_client_id(self, game_exe):
        return self.client_ids.get(game_exe, {}).get(self.language, "1414899272129843233")
    
    def clear(self):
        if self.rpc:
            try:
                self.rpc.clear()
            except:
                pass
    
    def toggle_language(self):
        self.language = "en" if self.language == "jp" else "jp"
        self.config["language"] = self.language
        self.save_config(self.config)
        self.last_pid = None
    
    def create_tray(self):
        def on_exit(icon, item):
            icon.stop()
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
            os._exit(0)
        
        def toggle_lang(icon, item):
            self.toggle_language()
            if self.current_game and self.rpc:
                self.rpc.close()
                self.rpc = None
            icon.update_menu()
        
        def toggle_startup(icon, item):
            if self.is_in_startup():
                if self.remove_from_startup():
                    print("Removed from startup")
            else:
                if self.add_to_startup():
                    print("Added to startup")
            icon.update_menu()
        
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            image = Image.open(icon_path) if os.path.exists(icon_path) else Image.new('RGB', (64, 64), 'blue')
        except:
            image = Image.new('RGB', (64, 64), 'blue')
        
        language_menu = pystray.Menu(
            pystray.MenuItem("日本語", toggle_lang, checked=lambda item: self.language == "jp"),
            pystray.MenuItem("English", toggle_lang, checked=lambda item: self.language == "en")
        )
        
        menu = pystray.Menu(
            pystray.MenuItem("Language", language_menu),
            pystray.MenuItem("Startup", toggle_startup, checked=lambda item: self.is_in_startup()),
            pystray.MenuItem("Exit", on_exit)
        )
        
        return pystray.Icon("ErogeRichPresence", image, "ErogeRichPresence", menu)
    
    def run(self):
        tray = self.create_tray()
        threading.Thread(target=tray.run, daemon=True).start()
        
        print("Starting...")
        
        while True:
            game, pid = self.find_games()
            
            if game:
                if pid != self.last_pid:
                    self.last_pid = pid
                    if not self.rpc or self.current_game != game:
                        self.connect(game)
                        self.current_game = game
                    self.update(game)
            else:
                if self.last_pid:
                    self.last_pid = None
                    self.current_game = None
                    if self.rpc:
                        self.clear()
                        self.rpc.close()
                        self.rpc = None
            
            time.sleep(1)

if __name__ == "__main__":
    ErogeRichPresence().run()