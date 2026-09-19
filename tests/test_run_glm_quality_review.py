import fcntl
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

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
                outcome = json.loads((output / "glm-5.3-probe/outcome.json").read_text())
                self.assertEqual(outcome["status"], "timeout")
                self.assertFalse(outcome["usable_review"])
                self.assertEqual(client.call_count, 1)
                with self.assertRaisesRegex(SystemExit, "already attempted"):
                    review.main()
                self.assertEqual(client.call_count, 1)

    def test_section_prompt_excludes_other_sections(self):
        prompt, hashes = review.build_prompt(SimpleNamespace(probe=False, part="scope"))
        self.assertIn("## 1. Introduction", prompt)
        self.assertNotIn("### 3.1 Frozen retrieval", prompt)
        self.assertEqual(list(hashes), [review.MANUSCRIPT + "#scope"])

    def test_all_streamed_review_segments_are_preserved(self):
        events = [{"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}
                  for text in ("Finding one\u2028continued", "Finding two")]
        events.append({"type": "result", "result": "Finding two", "stop_reason": "end_turn"})
        response = review.parse_response("\n".join(json.dumps(e, ensure_ascii=False) for e in events))
        self.assertEqual(response["review_text"], "Finding one\u2028continued\n\nFinding two")
        self.assertEqual(response["assistant_text_segments"], 2)

    def test_truncated_or_wrong_model_response_is_not_accepted(self):
        for stop, model in (("max_tokens", "glm-5.3"), ("end_turn", "glm-5.3-flash")):
            with self.subTest(stop=stop, model=model), tempfile.TemporaryDirectory() as directory:
                payload = {"type": "result", "subtype": "success", "is_error": False, "stop_reason": stop,
                           "result": "Partial review", "modelUsage": {model: {}}}
                completed = subprocess.CompletedProcess("client", 0, json.dumps(payload), "")
                with patch.object(review, "OUTPUT", Path(directory)), patch.object(sys, "argv", ["review", "--probe"]), patch.object(
                        review, "read_key", return_value="synthetic"), patch.object(review.subprocess, "run", return_value=completed):
                    with self.assertRaises(SystemExit):
                        review.main()
                    outcome = json.loads((Path(directory) / "glm-5.3-probe/outcome.json").read_text())
                    self.assertFalse(outcome["usable_review"])


if __name__ == "__main__":
    unittest.main()
