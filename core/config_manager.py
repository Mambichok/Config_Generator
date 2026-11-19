import json
import winreg
from pathlib import Path
from core.app_paths import resource_path, user_data_dir

class ConfigManager:
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "language": "en",
        "theme": "light",
        "default_delay": 1,
        "bat_folder": None,
        "show_notification": True,
        "minimize_tray": False,
    }
    
    def __init__(self, data_dir=None, locale_dir=None):
        self.data_dir = user_data_dir(data_dir)
        self.config_path = self.data_dir / self.CONFIG_FILE
        self.locale_dir = Path(locale_dir) if locale_dir else resource_path("locales")
        self.config = self.load()
        self._locales = {}
        self.load_locale()
    
    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    # Remove old keys
                    config.pop("background_image", None)
                    return config
            except Exception:
                pass
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
    
    def load_locale(self):
        lang = self.config.get("language", "en")
        locale_file = self.locale_dir / f"{lang}.json"
        
        if locale_file.exists():
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self._locales = json.load(f)
            except Exception:
                self._locales = {}
        else:
            self._locales = {}
    
    def tr(self, key):
        return self._locales.get(key, key)
    
    def is_dark_theme(self):
        theme = self.config.get("theme", "light")
        if theme == "auto":
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0
            except Exception:
                return False
        return theme == "dark"