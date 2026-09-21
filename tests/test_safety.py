import unittest

from wifi_lab.commands import deauth_command
from wifi_lab.models import Target


class SafetyTests(unittest.TestCase):
    def test_deauth_is_directed_and_single(self):
        target = Target(
            label="lab",
            essid="LAB",
            bssid="02:00:00:00:01:00",
            channel=6,
            client_mac="02:00:00:00:01:01",
            authorized=True,
            deauth_enabled=True,
        )
        command = deauth_command("wlan0mon", target)
        self.assertEqual(command[1:3], ["--deauth", "1"])
        self.assertIn("-c", command)
        self.assertIn(target.client_mac, command)

    def test_deauth_requires_client(self):
        with self.assertRaises(ValueError):
            Target(
                label="lab",
                essid="LAB",
                bssid="02:00:00:00:01:00",
                channel=6,
                client_mac=None,
                authorized=True,
                deauth_enabled=True,
            )


if __name__ == "__main__":
    unittest.main()

