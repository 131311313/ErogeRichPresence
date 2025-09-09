import time
import psutil
import json
from pypresence import Presence
import pystray
from PIL import Image
import threading
import sys
import os

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
        self.client_id = None
    
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
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in GAMES:
                    return proc.info['name']
            except:
                continue
        return None
    
    def connect(self, game_exe=None):
        try:
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
            if game_exe:
                self.client_id = self.get_client_id(game_exe)
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            return True
        except Exception as e:
            print(f"RPC connect error: {e}")
            self.rpc = None
            return False
    
    def update(self, game_exe):
        if not self.rpc:
            return
        try:
            game_name = GAMES[game_exe][self.language]
            
            if self.language == "jp":
                state = f"{game_name}をプレイ中"
            else:
                state = f"Playing {game_name}"
            
            print(f"Updating RPC: game_name={game_name}, language={self.language}")
            
            self.rpc.update(
                state=state,
                large_image="icon"
            )
        except Exception as e:
            print(f"RPC update error: {e}")
    
    def get_client_id(self, game_exe):
        if game_exe in self.client_ids:
            return self.client_ids[game_exe][self.language]
        return "1414899272129843233"
    
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
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
                self.rpc = None
            self.current_game = None
            icon.update_menu()
        
        def toggle_startup(icon, item):
            if self.is_in_startup():
                if self.remove_from_startup():
                    print("Removed from startup")
                else:
                    print("Failed to remove from startup")
            else:
                if self.add_to_startup():
                    print("Added to startup")
                else:
                    print("Failed to add to startup")
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
        
        while True:
            game = self.find_games()
            
            if game != self.current_game:
                if game:
                    if self.rpc:
                        self.clear()
                        self.rpc.close()
                        self.rpc = None
                    self.connect(game)
                    if self.rpc:
                        self.update(game)
                else:
                    self.clear()
                self.current_game = game
            elif game and self.rpc:
                try:
                    self.update(game)
                except Exception as e:
                    print(f"Update error: {e}")
                    self.rpc = None
            
            time.sleep(1)

if __name__ == "__main__":
    ErogeRichPresence().run()
