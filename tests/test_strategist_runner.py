import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from app.strategist.runner import SAMPLE_SCENARIO, _load_payload_from_cli


class TtyInput(io.StringIO):
    def isatty(self):
        return True


class StrategistRunnerInputTests(unittest.TestCase):
    def test_loads_payload_from_file_when_path_is_provided(self):
        payload = dict(SAMPLE_SCENARIO)
        payload["scenario_id"] = "file-scenario"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "sample_input.json"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with redirect_stdout(io.StringIO()) as output:
                loaded = _load_payload_from_cli(argv=[str(path)], stdin=TtyInput())

        self.assertEqual(loaded["scenario_id"], "file-scenario")
        self.assertIn("Reading input from file...", output.getvalue())

    def test_loads_payload_from_stdin_when_piped(self):
        payload = dict(SAMPLE_SCENARIO)
        payload["scenario_id"] = "stdin-scenario"

        with redirect_stdout(io.StringIO()) as output:
            loaded = _load_payload_from_cli(argv=[], stdin=io.StringIO(json.dumps(payload)))

        self.assertEqual(loaded["scenario_id"], "stdin-scenario")
        self.assertIn("Reading input from stdin...", output.getvalue())

    def test_uses_sample_scenario_when_no_file_or_stdin_is_present(self):
        with redirect_stdout(io.StringIO()) as output:
            loaded = _load_payload_from_cli(argv=[], stdin=TtyInput())

        self.assertEqual(loaded["scenario_id"], SAMPLE_SCENARIO["scenario_id"])
        self.assertIn("Loading sample scenario...", output.getvalue())

    def test_uses_sample_scenario_when_non_tty_stdin_is_empty(self):
        with redirect_stdout(io.StringIO()) as output:
            loaded = _load_payload_from_cli(argv=[], stdin=io.StringIO(""))

        self.assertEqual(loaded["scenario_id"], SAMPLE_SCENARIO["scenario_id"])
        self.assertIn("Loading sample scenario...", output.getvalue())


if __name__ == "__main__":
    unittest.main()
