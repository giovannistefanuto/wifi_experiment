import tempfile
import unittest
from pathlib import Path

from wifi_lab.errors import WifiLabError
from wifi_lab.models import Settings
from wifi_lab.runner import CommandRunner
from wifi_lab.workflow import audit_hash, ensure_wordlist, scan_networks


def settings(root: Path, wordlist: Path) -> Settings:
    return Settings(
        monitor_interface="wlan0mon",
        output_dir=root / "captures",
        scan_seconds=20,
        capture_timeout_seconds=30,
        deauth_delay_seconds=5,
        poll_seconds=3,
        wordlist=wordlist,
        targets=(),
    )


class WorkflowErrorTests(unittest.TestCase):
    def test_invalid_scan_duration_fails_before_external_process(self):
        with tempfile.TemporaryDirectory() as directory:
            cfg = settings(Path(directory), Path(directory) / "rockyou.txt")
            with self.assertRaisesRegex(WifiLabError, "tra 5 e 3600"):
                scan_networks(CommandRunner(dry_run=True), cfg, 0)

    def test_corrupt_wordlist_archive_is_reported_and_partial_is_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wordlist = root / "rockyou.txt"
            Path(f"{wordlist}.gz").write_bytes(b"not-a-gzip")
            cfg = settings(root, wordlist)
            with self.assertRaisesRegex(WifiLabError, "corrotto o incompleto"):
                ensure_wordlist(cfg)
            self.assertFalse((cfg.output_dir / "wordlists" / "rockyou.txt.tmp").exists())

    def test_missing_hash_file_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cfg = settings(root, root / "rockyou.txt")
            with self.assertRaisesRegex(WifiLabError, "HC22000 non trovato"):
                audit_hash(CommandRunner(), cfg, root / "missing.hc22000")

    def test_missing_wordlist_is_an_application_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cfg = settings(root, root / "missing.txt")
            with self.assertRaisesRegex(WifiLabError, "Wordlist non trovata"):
                ensure_wordlist(cfg)


if __name__ == "__main__":
    unittest.main()
