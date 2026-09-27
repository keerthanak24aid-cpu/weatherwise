import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from app import app, resolve_debug_mode


class WeatherAppTests(unittest.TestCase):
    def test_debug_mode_defaults_to_off(self):
        os.environ.pop("FLASK_DEBUG", None)
        self.assertFalse(resolve_debug_mode())

    def test_weather_extended_route_returns_data_for_city(self):
        client = app.test_client()
        response = client.get("/weather/extended?city=London")
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        data = response.get_json()
        self.assertTrue(data["city"])
        self.assertIn("temperature_c", data)
        self.assertIn("condition", data)
        self.assertIn("advice", data)


if __name__ == "__main__":
    unittest.main()
