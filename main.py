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
    from plyer import accelerometer
    SENSORS_AVAILABLE = True
except ImportError:
    SENSORS_AVAILABLE = False

if platform == 'android':
    from android_permissions import AndroidPermissions

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
        try:
            accelerometer.enable()
        except:
            return
        Clock.schedule_interval(self.update_sensors, 0.1)

    def update_sensors(self, dt):
        try:
            accel = accelerometer.acceleration[:3]
            if not accel == (None, None, None):
                ax, ay, az = accel
                
                self.pitch_angle = self.calculate_pitch(ax, ay, az)
                self.roll_angle = math.degrees(math.atan2(ay, math.sqrt(ax*ax + az*az)))

                self.accelX = f"X: {accel[0]:.2f}"
                self.accelY = f"Y: {accel[1]:.2f}"
                self.accelZ = f"Z: {accel[2]:.2f}"
        except:
            pass

    def calculate_pitch(self, ax, ay, az):
        self.pitch_angle = math.degrees(math.atan2(ax, math.sqrt(ay*ay + az*az)))
        if az < 0:
            self.pitch_angle += 2*(90-self.pitch_angle)
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
