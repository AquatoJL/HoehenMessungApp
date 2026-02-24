"""Zur Ausführung im Terminal ausführen: python -m pytest unit-test.py --cov=main --cov=settings --cov=android_permissions --cov-report=html --ignore=config.py -v"""
import pytest
import math, os, json, tempfile
from unittest.mock import MagicMock, patch

from main import CameraScreen
from settings import AppSettings
import android_permissions

class TestCameraScreen:
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

    def test_calculate_tilt_zero_magnitude(self, screen):
        screen.calculate_tilt(0, 0, 0)
        assert screen.tilt_angle == 0

    def test_toggle_mode(self, screen):
        screen.distance = "1.50 m"
        screen.accel_x = 7
        assert screen.button_text == "Entfernung messen"
        assert screen.icon == "arrow-expand-horizontal"
        assert screen.distance_background_color == [0, 0.3, 0, 1]
        screen.toggle_mode()
        assert screen.button_text == "Höhe messen"
        assert screen.icon == "arrow-expand-vertical"
        assert screen.height_background_color == [0, 0.3, 0, 1]
        screen.toggle_mode()
        assert screen.button_text == "Zurücksetzen"
        assert screen.icon == "refresh"
        screen.toggle_mode()
        assert screen.button_text == "Entfernung messen"
        assert screen.icon == "arrow-expand-horizontal"
        assert screen.distance_background_color == [0, 0.3, 0, 1]

    def test_on_phone_height_too_low(self, screen):
        screen.on_phone_height(screen, 0.5)
        assert screen.phone_height == 1.0

    def test_on_phone_height_too_high(self, screen):
        screen.on_phone_height(screen, 3.0)
        assert screen.phone_height == 2.0

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
        screen.tilt_angle = 9
        screen.calculate_object_height()
        assert screen.object_height == "MIN"
        screen.tilt_angle = 171
        screen.calculate_object_height()
        assert screen.object_height == "MAX"

    def test_calculate_object_height_exception(self, screen):
        screen.tilt_angle = 100
        screen.distance = "MAX"
        screen.calculate_object_height()
        assert screen.object_height == "-- m"


class TestAppSettings:
    def test_load_default(self):
        s = AppSettings()
        assert s.get('phone_height') == 1.5

    def test_set_and_get(self):
        s = AppSettings()
        s.set('phone_height', 1.8)
        assert s.get('phone_height') == 1.8

    def test_get_missing_key_returns_none(self):
        s = AppSettings()
        assert s.get('nicht_vorhanden') is None

    def test_get_missing_key_with_default(self):
        s = AppSettings()
        assert s.get('nicht_vorhanden', 42) == 42

    def test_multiple_keys(self):
        s = AppSettings()
        s.set('phone_height', 1.6)
        s.set('phone_height', 1.9)
        assert s.get('phone_height') == 1.9
    
    def test_delete(self):
        s = AppSettings('test_delete')
        s.set('phone_height', 1.2)
        s.delete()
        s2 = AppSettings('test_delete')
        assert s2.get('phone_height') == 1.5


def test_android_permissions_calls_start_app(monkeypatch):
    monkeypatch.setattr('android_permissions.platform', 'win', raising=False)
    start_mock = MagicMock()
    android_permissions.AndroidPermissions(start_app=start_mock)
    start_mock.assert_called_once()

def test_android_permissions_no_start_app(monkeypatch):
    monkeypatch.setattr('android_permissions.platform', 'win', raising=False)
    perms = android_permissions.AndroidPermissions()
    assert perms.permission_dialog_count == 0