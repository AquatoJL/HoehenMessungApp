from kivy.app import App
from kivy.lang import Builder
from camera4kivy import Preview

class Camera4KivyApp(App):
    def build(self):
        root = Builder.load_file("main.kv")
        self.preview = root.ids.preview
        return root

    def on_start(self):
        self.preview.connect_camera(camera_id='0')

    def on_stop(self):
        self.preview.disconnect_camera()

if __name__ == "__main__":
    Camera4KivyApp().run()
