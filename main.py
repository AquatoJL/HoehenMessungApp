from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from camera4kivy import Preview
from settings import AppSettings
import math

try:
    from plyer import accelerometer
    SENSORS_AVAILABLE = True
except ImportError:
    SENSORS_AVAILABLE = False

if platform == 'android':
    from android_permissions import AndroidPermissions
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from android import mActivity

    View = autoclass('android.view.View')

    @run_on_ui_thread
    def set_fullscreen(instance, width, height):
        """Setzt die Android-UI in den Fullscreen/Immersive-Modus."""
        mActivity.getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        )

class CameraScreen(BoxLayout):
    """Haupt-Logik der Messansicht (Sensorwerte, Distanz- und Höhenberechnung)."""
    accel_x = NumericProperty(0.0)
    accel_y = NumericProperty(0.0)
    accel_z = NumericProperty(0.0)

    roll_angle = NumericProperty(0.0)
    tilt_angle = NumericProperty(0.0)

    button_text = StringProperty("Entfernung messen")
    icon = StringProperty("arrow-expand-horizontal")
    
    phone_height = NumericProperty()
    object_height = StringProperty("-- m")
    distance = StringProperty("-- m")

    distance_background_color = ListProperty([0, 0.3, 0, 1])
    height_background_color = ListProperty([0.3, 0.3, 0.3, 1])

    def __init__(self, **kwargs):
        """Initialisiert Einstellungen, lädt Telefonhöhe und startet Sensor-Updates."""
        super().__init__(**kwargs)
        self.settings = AppSettings("hoehenmessung")
        self.phone_height = self.settings.get('phone_height')
        if SENSORS_AVAILABLE:
            self.start_sensor_updates()

    def on_phone_height(self, instance, value):
        """Validiert und begrenzt die Gerätehöhe auf 1,0–2,0 m und speichert sie persistent."""
        valid_height = max(1.0, min(2.0, value))
        if value != valid_height:
            self.phone_height = valid_height
        self.settings.set('phone_height', valid_height)

    def start_sensor_updates(self):
        """Aktiviert den Accelerometer und registriert die periodische Aktualisierungen über die Kivy-Clock."""
        try:
            accelerometer.enable()
        except:
            return
        Clock.schedule_interval(self.update_sensors, 0.1)

    def update_sensors(self, dt):
        """Liest aktuelle Sensorwerte, berechnet Tilt/Roll und aktualisiert die Properties sowie Distanz bzw. Objekt­höhe abhängig vom Status."""
        try:
            accel = accelerometer.acceleration[:3]
            if not accel == (None, None, None):
                ax, ay, az = accel
                
                self.calculate_tilt(ax, ay, az)
                self.roll_angle = math.degrees(math.atan2(ay, math.sqrt(ax*ax + az*az)))

                self.accel_x = accel[0]
                self.accel_y = accel[1]
                self.accel_z = accel[2]

                if self.button_text == "Entfernung messen":
                    self.calculate_distance()
                elif self.button_text == "Höhe messen":
                    self.calculate_object_height()
        except:
            pass

    def calculate_tilt(self, ax, ay, az):
        """Berechnet den Neigungswinkel aus Accelerometer-Daten."""
        accel_magnitude = math.sqrt(ax*ax + ay*ay + az*az)
        if accel_magnitude > 0:
            self.tilt_angle = math.degrees(math.acos(az / accel_magnitude))
        else:
            self.tilt_angle = 0
    
    def calculate_distance(self):
        """Berechnet die Entfernung aus Telefonhöhe und Neigungswinkel oder setzt Sonderwerte ("MAX", "-- m")."""
        if self.tilt_angle >= 90:
            self.distance = "MAX"
        elif self.tilt_angle != 0:
            distance = self.phone_height * math.tan(math.radians(self.tilt_angle))
            self.distance = f"{distance:.2f} m"
        else:
            self.distance = "-- m"

    def calculate_object_height(self):
        """Berechnet die Objekt-Höhe anhand gespeicherter Entfernung und aktuellem Neigungswinkel."""
        if self.tilt_angle < 10:
            self.object_height = "MIN"
        elif self.tilt_angle > 170:
            self.object_height = "MAX"
        else:
            try:
                object_height = self.phone_height + (float(self.distance.replace('m','').strip()) * math.tan(math.radians(self.tilt_angle-90)))
                self.object_height = f"{object_height:.2f} m"
            except:
                self.object_height = "-- m"

    def toggle_mode(self):
        """Schaltet den Messmodus um (Entfernung → Höhe → Reset). Aktualisiert Button-Text, Icon und UI-Farben."""
        if self.button_text == "Entfernung messen" and self.distance != "-- m" and self.distance != "MAX" and self.accel_x >= 0:
            self.button_text = "Höhe messen"
            self.icon = "arrow-expand-vertical"
            self.distance_background_color = [0.3, 0.3, 0.3, 1]
            self.height_background_color = [0, 0.3, 0, 1]
        elif self.button_text == "Höhe messen":
            self.button_text = "Zurücksetzen"
            self.icon = "refresh"
            self.height_background_color = [0.3, 0.3, 0.3, 1]
        else:
            self.button_text = "Entfernung messen"
            self.object_height = "-- m"
            self.distance = "-- m"
            self.icon = "arrow-expand-horizontal"
            self.distance_background_color = [0, 0.3, 0, 1]

    def on_enter(self):
        """Verbindet die Kamera-Preview (falls vorhanden)."""
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.connect_camera()
            self.ids.preview.allow_stretch = True

    def on_leave(self):
        """Trennt die Kamera-Preview (falls vorhanden)."""
        if hasattr(self, 'ids') and 'preview' in self.ids:
            self.ids.preview.disconnect_camera()

class CameraApp(MDApp):
    """KivyMD-App, die die KV lädt, `CameraScreen` verwaltet und Android-spezifische Berechtigungen und Fullscreen-Modus handhabt."""
    def build(self):
        """Baut die App-Oberfläche auf, lädt KV-Datei und erstellt `CameraScreen`."""
        Window.orientation = 'landscape'
        Builder.load_file('main.kv')
        self.camera_screen = CameraScreen()
        return self.camera_screen

    def on_start(self):
        """Setzt unter Android Vollbild, initialisiert Berechtigungen und startet die Kamera."""
        if platform == 'android':
            Window.bind(on_resize=set_fullscreen)
            set_fullscreen(None, Window.width, Window.height)
            self.dont_gc = AndroidPermissions(self.start_camera)
        else:
            self.start_camera()

    def on_stop(self):
        """Ruft on_leave() auf, um die Kamera zu stoppen."""
        if hasattr(self.camera_screen, 'on_leave'):
            self.camera_screen.on_leave()

    def start_camera(self):
        """Ruft on_enter() auf, um die Kamera zu starten."""
        self.dont_gc = None
        if hasattr(self.camera_screen, 'on_enter'):
            self.camera_screen.on_enter()

if __name__ == '__main__':
    CameraApp().run()
