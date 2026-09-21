import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from wifi_lab.errors import CommandExecutionError
from wifi_lab.runner import CommandRunner


class RunnerTests(unittest.TestCase):
    def test_empty_command_is_rejected(self):
        with self.assertRaisesRegex(CommandExecutionError, "vuoto"):
            CommandRunner().run([])

    @patch("wifi_lab.runner.subprocess.run", side_effect=FileNotFoundError())
    def test_missing_tool_has_install_hint(self, _mock_run):
        with self.assertRaisesRegex(CommandExecutionError, "setup_kali.sh"):
            CommandRunner().run(["missing-tool"])

    @patch(
        "wifi_lab.runner.subprocess.run",
        side_effect=subprocess.TimeoutExpired(["slow-tool"], timeout=3),
    )
    def test_timeout_reports_duration_and_command(self, _mock_run):
        with self.assertRaisesRegex(CommandExecutionError, "Timeout dopo 3s: slow-tool"):
            CommandRunner().run(["slow-tool"], timeout=3)

    @patch("wifi_lab.runner.subprocess.run")
    def test_nonzero_checked_command_includes_stderr(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            ["tool"], returncode=9, stdout="", stderr="dettaglio utile"
        )
        with self.assertRaisesRegex(CommandExecutionError, "dettaglio utile"):
            CommandRunner().run(["tool"], check=True)

    def test_start_rejects_empty_command_before_opening_log(self):
        with self.assertRaises(CommandExecutionError):
            CommandRunner().start([], Path("unused.log"))


if __name__ == "__main__":
    unittest.main()
