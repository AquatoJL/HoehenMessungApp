from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.app import App

# Android Permissions
try:
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.CAMERA])
except ImportError:
    pass

class CameraScreen(Screen):
    pass

class CameraApp(App):
    def build(self):
        Builder.load_file('main.kv')
        ms = ScreenManager()
        ms.add_widget(CameraScreen(name='camera'))
        return ms

if __name__ == '__main__':
    CameraApp().run()
