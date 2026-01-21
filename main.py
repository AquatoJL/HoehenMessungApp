import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line
from kivy.vector import Vector
from kivy.clock import Clock
from plyer import accelerometer, vibrator
import math

CONFIG_FILE = 'settings.json'

class CrosshairWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_pos = Vector(0, 0)
        self.bind(size=self.update_graphics, pos=self.update_graphics)

    def update_crosshair(self, pos):
        self.touch_pos = Vector(*pos)
        self.update_graphics()

    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Line(points=[self.touch_pos[0]-20, self.touch_pos[1], self.touch_pos[0]+20, self.touch_pos[1]], width=3)
            Line(points=[self.touch_pos[0], self.touch_pos[1]-20, self.touch_pos[0], self.touch_pos[1]+20], width=3)

class MeasureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anchor_pos = None
        self.angle = 0
        self.distance = 0
        self.height = 0
        self.phone_height = 1.6
        self.load_config()
        Clock.schedule_interval(self.update_sensors, 1/30.)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.phone_height = config.get('phone_height', 1.6)

    def set_anchor(self):
        self.ids.crosshair.update_crosshair((320, 240))  # Demo center
        vibrator.vibrate(0.1)

    def focus_camera(self):
        pass  # Kamera-Fokus via jnius bei Bedarf

    def take_screenshot(self):
        from kivy.core.window import Window
        Window.screenshot(name=f'measure_{int(math.time())}')

    def update_sensors(self, dt):
        try:
            event = accelerometer.acceleration
            if event:
                self.angle = math.degrees(math.asin(event[1]))  # Pitch approx
                self.ids.angle_lbl.text = f'Winkel: {self.angle:.1f}°'
                
                self.distance = 10 * abs(math.sin(math.radians(self.angle)))
                self.height = self.distance * abs(math.sin(math.radians(self.angle))) + self.phone_height
                self.ids.distance_lbl.text = f'Entfernung: {self.distance:.1f} m'
                self.ids.height_lbl.text = f'Höhe: {self.height:.1f} m[file:1]'
        except Exception as e:
            pass

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ids.crosshair.update_crosshair(touch.pos)
            return True
        return super().on_touch_down(touch)

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.ids.phone_height.text = str(config.get('phone_height', 1.6))

    def save_config(self):
        config = {'phone_height': float(self.ids.phone_height.text)}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        app = App.get_running_app()
        app.root.get_screen('measure').phone_height = config['phone_height']

class HeightMeasureApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MeasureScreen(name='measure'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    HeightMeasureApp().run()
