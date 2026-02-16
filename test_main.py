import pytest
import math
from unittest.mock import MagicMock, patch
from main import CameraScreen, CameraApp, AppSettings

class TestHoehenMessungApp:
    @pytest.fixture
    def screen(self):
        with patch('kivy.utils.platform', return_value='win'):
            with patch('plyer.accelerometer', new=None):
                s = CameraScreen()
                s.settings = MagicMock()
                s.settings.get.return_value = 1.5
                s.phone_height = 1.5
                return s

    def test_calculate_tilt_flat(self, screen):
        screen.calculate_tilt(0, 0, 9.81)
        assert screen.tilt_angle == 0

    def test_calculate_tilt_90(self, screen):
        screen.calculate_tilt(9.81, 0, 0)
        assert screen.tilt_angle == 90

    def test_calculate_tilt_over_90(self, screen):
        screen.calculate_tilt(0, 0, -9.81)
        assert screen.tilt_angle > 90

    def test_measure_states(self):
        app = CameraApp()
        app.build()
        assert app.camera_screen.button_text == "Entfernung messen"
        assert app.camera_screen.icon == "arrow-expand-horizontal"
        app.measure()
        assert app.camera_screen.button_text == "Höhe messen"
        assert app.camera_screen.icon == "arrow-expand-vertical"
        app.measure()
        assert app.camera_screen.button_text == "Zurücksetzen"
        assert app.camera_screen.icon == "refresh"
        app.measure()
        assert app.camera_screen.button_text == "Entfernung messen"
        assert app.camera_screen.icon == "arrow-expand-horizontal"

    def test_calculate_distance(self, screen):
        screen.tilt_angle = 45
        screen.calculate_distance()
        expected = 1.5 * math.tan(math.radians(45))
        assert float(screen.distance[:-2]) == pytest.approx(expected, 0.01)
        screen.tilt_angle = 91
        screen.calculate_distance()
        assert screen.distance == "MAX"
        screen.tilt_angle = 0
        screen.calculate_distance()
        assert screen.distance == "-- m"

    def test_calculate_object_height(self, screen):
        screen.tilt_angle = 135
        screen.distance = "2.00 m"
        screen.calculate_object_height()
        expected = 1.5 + (2.00 * math.tan(math.radians(135-90)))
        assert float(screen.object_height[:-2]) == pytest.approx(abs(expected), 0.01)
        screen.tilt_angle = 0
        screen.calculate_object_height()
        assert screen.object_height == "-- m"

    def test_app_settings_SaveAndLoad(self):
        settings = AppSettings()
        settings.set('phone_height', 1.6)
        assert settings.get('phone_height') == 1.6
