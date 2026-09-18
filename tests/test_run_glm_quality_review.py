import fcntl
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_glm_quality_review as review


class SerialReviewTest(unittest.TestCase):
    def test_competing_process_stops_before_key_or_client(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with (output / ".serial.lock").open("a") as lock, patch.object(review, "OUTPUT", output), patch.object(
                    sys, "argv", ["review", "--probe"]), patch.object(review, "read_key") as key:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with self.assertRaisesRegex(SystemExit, "Another GLM review"):
                    review.main()
                key.assert_not_called()

    def test_timeout_is_recorded_and_cannot_be_silently_retried(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(sys, "argv", ["review", "--probe"]):
            output = Path(directory)
            with patch.object(review, "OUTPUT", output), patch.object(review, "read_key", return_value="synthetic"), patch.object(
                    review.subprocess, "run", side_effect=subprocess.TimeoutExpired("client", 300)) as client:
                with self.assertRaisesRegex(SystemExit, "quota usage unknown"):
                    review.main()
                outcome = json.loads((output / "glm-5.3-flash-probe/outcome.json").read_text())
                self.assertEqual(outcome["status"], "timeout")
                self.assertFalse(outcome["usable_review"])
                self.assertEqual(client.call_count, 1)
                with self.assertRaisesRegex(SystemExit, "already attempted"):
                    review.main()
                self.assertEqual(client.call_count, 1)


if __name__ == "__main__":
    unittest.main()
