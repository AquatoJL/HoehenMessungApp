import json
import os
from kivy.utils import platform

class AppSettings:
    def __init__(self, settings_key="hoehenmessung"):
        self.settings_file = self._get_settings_path(settings_key)
        self.settings = self.load()
    
    def _get_settings_path(self, settings_key):
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                storage_path = app_storage_path()
            except ImportError:
                storage_path = "/sdcard/Download"
        else:
            storage_path = os.path.dirname(os.path.abspath(__file__))
        
        os.makedirs(storage_path, exist_ok=True)
        return os.path.join(storage_path, f'app_settings_{settings_key}.json')
    
    def load(self):
        defaults = {
            'phone_height': 1.5
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    print(settings)
                    for key, value in settings.items():
                        settings[key] = value
                    return settings
            else:
                return defaults
        except Exception:
            return defaults
    
    def save(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save()
    
    def delete(self):
        try:
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
        except Exception:
            pass