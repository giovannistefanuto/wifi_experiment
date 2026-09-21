import tempfile
import unittest
from pathlib import Path

from wifi_lab.config import load_settings
from wifi_lab.errors import ConfigurationError


class ConfigTests(unittest.TestCase):
    def test_discovery_configuration_can_omit_targets(self):
        content = """[lab]
monitor_interface = "wlan0mon"
output_dir = "../captures"
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "discovery.toml"
            path.write_text(content, encoding="utf-8")
            settings = load_settings(path)

        self.assertEqual(settings.monitor_interface, "wlan0mon")
        self.assertEqual(settings.targets, ())

    def test_missing_configuration_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.toml"
            with self.assertRaisesRegex(ConfigurationError, "Configurazione non trovata"):
                load_settings(path)

    def test_invalid_toml_has_context(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.toml"
            path.write_text("[lab\nmonitor_interface =", encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "TOML non valido"):
                load_settings(path)

    def test_string_boolean_is_rejected(self):
        content = '''[lab]
monitor_interface = "wlan0mon"

[[targets]]
label = "lab"
bssid = "02:00:00:00:01:00"
channel = 6
authorized = "true"
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lab.toml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "true oppure false"):
                load_settings(path)

    def test_duplicate_target_is_rejected(self):
        content = '''[lab]
monitor_interface = "wlan0mon"

[[targets]]
label = "one"
bssid = "02:00:00:00:01:00"
channel = 6

[[targets]]
label = "two"
bssid = "02:00:00:00:01:00"
channel = 6
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lab.toml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ConfigurationError, "BSSID duplicati"):
                load_settings(path)


if __name__ == "__main__":
    unittest.main()
