import json
import os
from kivy.utils import platform

class AppSettings:
    """Verwaltung der App-Einstellungen, die in einer JSON-Datei gespeichert werden, inkl. Laden, Speichern und Löschen einer Datei pro settings_key."""
    def __init__(self, settings_key="hoehenmessung"):
        """Lädt vorhandene App-Einstellungen und speichert den Pfad für die JSON-Datei."""
        self.settings_file = self._get_settings_path(settings_key)
        self.settings = self.load()
    
    def _get_settings_path(self, settings_key):
        """Ermittelt den Speicherpfad abhängig von der Plattform und legt das Verzeichnis an."""
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
        """Lädt Einstellungen aus der JSON-Datei oder liefert Default-Werte."""
        defaults = {
            'phone_height': 1.5
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    for key, value in settings.items():
                        settings[key] = value
                    return settings
            else:
                return defaults
        except Exception:
            return defaults
    
    def save(self):
        """Speichert die aktuellen Einstellungen in die JSON-Datei."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
    
    def get(self, key, default=None):
        """Liest einen Wert aus den Einstellungen."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        "Setzt einen Einstellungswert und speichert sofort."
        self.settings[key] = value
        self.save()
    
    def delete(self):
        """Löscht die JSON-Datei, falls vorhanden."""
        try:
            if os.path.exists(self.settings_file):
                os.remove(self.settings_file)
        except Exception:
            pass