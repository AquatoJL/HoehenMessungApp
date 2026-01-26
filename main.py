from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class CameraApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.camera = Camera(play=True)
        self.camera.resolution = (640, 480)
        
        btn = Button(text="Foto machen", size_hint=(1, 0.2))
        btn.bind(on_press=self.take_picture)
        
        layout.add_widget(self.camera)
        layout.add_widget(btn)
        return layout

    def take_picture(self, *args):
        self.camera.export_to_png("foto.png")
        print("Foto gespeichert")

if __name__ == '__main__':
    CameraApp().run()
