from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.utils import platform

from camera4kivy import Preview

if platform == 'android':
    from android_permissions import AndroidPermissions
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from android import mActivity
    
    View = autoclass('android.view.View')
    
    @run_on_ui_thread
    def set_fullscreen(instance, width, height):
        mActivity.getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | 
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        )


class CameraScreen(BoxLayout):
    def on_enter(self):
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.connect_camera()
            self.ids.preview.allow_stretch = True
    
    def on_leave(self):
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.disconnect_camera()


class CameraApp(App):
    def build(self):
        Window.fullscreen = True
        Window.orientation = 'sensor'
        
        Builder.load_file('main.kv')
        
        self.camera_screen = CameraScreen()
        return self.camera_screen
    
    def capture_photo(self):
        self.root.ids.preview.capture_photo(location='shared', subdir='Photos')
        print("Foto gespeichert!")
    
    def on_start(self):
        if platform == 'android':
            # Vollbild-Modus aktivieren
            Window.bind(on_resize=set_fullscreen)
            set_fullscreen(None, Window.width, Window.height)
            
            self.dont_gc = AndroidPermissions(self.start_camera)
        else:
            self.start_camera()

    def on_stop(self):
        if hasattr(self.camera_screen, 'on_leave'):
            self.camera_screen.on_leave()
    
    def start_camera(self):
        self.dont_gc = None
        if hasattr(self.camera_screen, 'on_enter'):
            self.camera_screen.on_enter()


if __name__ == '__main__':
    CameraApp().run()