import tempfile
import unittest
from pathlib import Path

from wifi_lab.scan import parse_airodump_csv


CSV = """BSSID, First time seen, Last time seen, channel, Speed, Privacy, Cipher, Authentication, Power, # beacons, # IV, LAN IP, ID-length, ESSID, Key\n02:00:00:00:01:00, 2026-09-21 10:00:00, 2026-09-21 10:00:02, 6, 130, WPA2, CCMP, PSK, -40, 10, 0, 0.0.0.0, 8, LAB_WIFI, \n\nStation MAC, First time seen, Last time seen, Power, # packets, BSSID, Probed ESSIDs\n02:00:00:00:01:01, 2026-09-21 10:00:00, 2026-09-21 10:00:02, -45, 4, 02:00:00:00:01:00, \n"""


class ScanParserTests(unittest.TestCase):
    def test_reads_access_point_and_associated_client(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scan.csv"
            path.write_text(CSV, encoding="utf-8")
            result = parse_airodump_csv(path)

        self.assertEqual(len(result.access_points), 1)
        self.assertEqual(result.access_points[0].essid, "LAB_WIFI")
        self.assertEqual(result.access_points[0].channel, 6)
        self.assertEqual(len(result.clients), 1)
        self.assertEqual(result.clients[0].mac, "02:00:00:00:01:01")


if __name__ == "__main__":
    unittest.main()
