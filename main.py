from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.properties import StringProperty
from kivy.clock import Clock
from camera4kivy import Preview

try:
    from plyer import accelerometer, compass, gyroscope
    SENSORS_AVAILABLE = True
except ImportError:
    SENSORS_AVAILABLE = False
    print("Plyer nicht verfügbar - Sensoren deaktiviert")

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
    accelX = StringProperty("X: 0.0")
    accelY = StringProperty("Y: 0.0")
    accelZ = StringProperty("Z: 0.0")
    spatialAzimuth = StringProperty("Azimuth: 0.0°")
    spatialPitch = StringProperty("Pitch: 0.0°")
    spatialRoll = StringProperty("Roll: 0.0°")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if SENSORS_AVAILABLE:
            self.start_sensor_updates()

    def start_sensor_updates(self):
        Clock.schedule_interval(self.update_sensors, 0.1)

    def update_sensors(self, dt):
        try:
            if hasattr(accelerometer, 'enabled') and accelerometer.enabled:
                accel = accelerometer.acceleration[:3]
                if accel:
                    self.accelX = f"X: {accel[0]:.2f}"
                    self.accelY = f"Y: {accel[1]:.2f}"
                    self.accelZ = f"Z: {accel[2]:.2f}"

            if hasattr(compass, 'enabled') and compass.enabled:
                compass_data = compass.read()
                if compass_data:
                    self.spatialAzimuth = f"Azimuth: {compass_data[0]:.1f}°"

            try:
                if hasattr(gyroscope, 'enabled') and gyroscope.enabled:
                    gyro = gyroscope.read()
                    if gyro:
                        self.spatialPitch = f"Pitch: {gyro[1]:.1f}°"
                        self.spatialRoll = f"Roll: {gyro[2]:.1f}°"
            except:
                pass

        except Exception as e:
            print(f"Sensor-Fehler: {e}")

    def on_enter(self):
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.connect_camera()
            self.ids.preview.allow_stretch = True

    def on_leave(self):
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.disconnect_camera()

class CameraApp(MDApp):
    def build(self):
        Window.orientation = 'landscape'
        Builder.load_file('main.kv')
        self.camera_screen = CameraScreen()
        return self.camera_screen

    def capture_photo(self):
        self.root.ids.preview.capture_photo(location='shared', subdir='Photos')
        print("Foto gespeichert!")

    def on_start(self):
        if platform == 'android':
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
