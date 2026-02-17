from kivy.utils import platform
from kivy.clock import mainthread

if platform == 'android':
    from kivy.uix.button import Button
    from kivy.uix.modalview import ModalView
    from kivy.clock import Clock
    from android import api_version, mActivity
    from android.permissions import request_permissions, check_permission, Permission

class AndroidPermissions:
    """Steuert das Einholen der benötigten Android-Berechtigungen und ruft nach Erfolg ein Start-Callback auf."""
    def __init__(self, start_app = None):
        """Initialisiert den Zustand, legt die zu prüfenden Berechtigungen fest und stößt die erste Status-Überprüfung an."""
        self.permission_dialog_count = 0
        self.start_app = start_app
        if platform == 'android':
            self.permissions = [Permission.CAMERA]
            if api_version < 29:
                self.permissions.append(Permission.WRITE_EXTERNAL_STORAGE)
            self.permission_status([],[])
        elif self.start_app:
            self.start_app()

    def permission_status(self, permissions, grants):
        """Prüft per `check_permission`, ob alle benötigten Permissions gewährt sind.
        Wenn ja, wird `start_app` ausgeführt. Andernfalls wird erneut
        ein Permission-Dialog geplant."""
        granted = True
        for p in self.permissions:
            granted = granted and check_permission(p)
        if granted:
            if self.start_app:
                self.start_app()
        elif self.permission_dialog_count < 2:
            Clock.schedule_once(self.permission_dialog)
        
    def permission_dialog(self, dt):
        """Fordert die benötigten Permissions über den Android-Dialog an."""
        self.permission_dialog_count += 1
        request_permissions(self.permissions, self.permission_status)