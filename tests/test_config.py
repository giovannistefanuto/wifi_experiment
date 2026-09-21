import tempfile
import unittest
from pathlib import Path

from wifi_lab.config import load_settings


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


if __name__ == "__main__":
    unittest.main()
