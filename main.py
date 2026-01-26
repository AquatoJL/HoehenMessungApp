from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.xcamera import XCamera

class CameraApp(App):
    def build(self):
        layout = BoxLayout()
        self.camera = XCamera(play=True)
        layout.add_widget(self.camera)
        return layout

if __name__ == '__main__':
    CameraApp().run()
