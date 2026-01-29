from kivy.app import App
from camera4kivy.preview import Preview

class PhotoApp(App):
    def on_start(self):
        self.root.ids.preview.connect_camera(camera_id='back')
    
    def on_stop(self):
        self.root.ids.preview.disconnect_camera()
        return True
    
    def capture_photo(self):
        self.root.ids.preview.capture_photo(location='shared', subdir='Photos')
        print("Foto gespeichert!")
    
    def capture_screenshot(self):
        self.root.ids.preview.capture_screenshot()
    
    def draw_canvas(self, texture, tex_size, tex_pos):
        pass
    
    def file_callback(self, file_name):
        print(f"Datei: {file_name}")

if __name__ == '__main__':
    PhotoApp().run()
