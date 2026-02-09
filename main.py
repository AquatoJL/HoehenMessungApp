from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from camera4kivy import Preview
import math

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

    pitch_angle = NumericProperty(0.0)
    roll_angle = NumericProperty(0.0)

    button_text = StringProperty("Entfernung messen")
    phone_height = NumericProperty(1.5)
    object_height = StringProperty("-- m")
    distance = StringProperty("-- m")

    icon = StringProperty("arrow-expand-horizontal")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if SENSORS_AVAILABLE:
            self.start_sensor_updates()
        self.pitch_offset = 0.0

    def start_sensor_updates(self):
        accelerometer.enable()
        Clock.schedule_interval(self.update_sensors, 0.1)

    def update_sensors(self, dt):
        try:
            accel = accelerometer.acceleration[:3]
            if not accel == (None, None, None):
                ax, ay, az = accel
                
                # Pitch & Roll aus Accelerometer berechnen (in Grad)
                self.pitch_angle = self.calculate_pitch(ax, ay, az)
                self.roll_angle = math.degrees(math.atan2(ay, math.sqrt(ax*ax + az*az)))

                self.accelX = f"X: {accel[0]:.2f}"
                self.accelY = f"Y: {accel[1]:.2f}"
                self.accelZ = f"Z: {accel[2]:.2f}"
        except:
            pass

    def calculate_pitch(self, ax, ay, az):
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0: return self.pitch_angle
        ax, ay, az = ax/norm, ay/norm, az/norm
        
        pitch_new = math.degrees(math.atan2(ax, math.sqrt(ay*ay + az*az)))
        
        # Unwrapping-Logik
        if self.pitch_angle > 80 and pitch_new < 10:
            self.pitch_offset += 180
        elif self.pitch_angle < -80 and pitch_new > -10:
            self.pitch_offset -= 180
            
        self.pitch_angle = pitch_new + self.pitch_offset
        return self.pitch_angle

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

    def measure(self):
        if self.camera_screen.button_text == "Entfernung messen":
            self.camera_screen.button_text = "Höhe messen"
            self.camera_screen.distance = self.calculate_distance()
            self.camera_screen.icon = "arrow-expand-vertical"
        elif self.camera_screen.button_text == "Höhe messen":
            self.camera_screen.button_text = "Zurücksetzen"
            self.camera_screen.object_height = self.calculate_object_height()
            self.camera_screen.icon = "refresh"
        else:
            self.camera_screen.button_text = "Entfernung messen"
            self.camera_screen.object_height = "-- m"
            self.camera_screen.distance = "-- m"
            self.camera_screen.icon = "arrow-expand-horizontal"

    def calculate_distance(self):
        if self.camera_screen.pitch_angle != 0:
            try:
                distance = self.camera_screen.phone_height * math.tan(math.radians(self.camera_screen.pitch_angle))
                return f"{distance:.2f} m"
            except ZeroDivisionError:
                return "-- m"
        else:
            return "-- m"

    def calculate_object_height(self):
        if self.camera_screen.pitch_angle != 0:
            try:
                object_height = self.camera_screen.phone_height + (float(self.camera_screen.distance.replace('m','').strip()) * math.tan(math.radians(self.camera_screen.pitch_angle-90)))
                return f"{abs(object_height):.2f} m"
            except ZeroDivisionError:
                return "-- m"
        else:
            return "-- m"

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
