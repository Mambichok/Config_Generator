import tempfile
import unittest
from pathlib import Path

from core.bat_generator import BatGenerator
from models.profile import Profile


class BatGeneratorTests(unittest.TestCase):
    def test_admin_profile_generates_single_elevation_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = Profile(
                name="Work",
                filename="work",
                items=[],
                run_as_admin=True
            )

            bat_path = BatGenerator(temp_dir).generate(profile)
            content = bat_path.read_text(encoding="utf-8")

        self.assertEqual(content.count("fltmc >nul 2>&1"), 1)
        self.assertIn("Start-Process", content)
        self.assertIn("Verb RunAs", content)
        self.assertIn("[char]34", content)

    def test_standard_profile_does_not_request_elevation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile = Profile(name="Work", filename="work", items=[])

            bat_path = BatGenerator(temp_dir).generate(profile)
            content = bat_path.read_text(encoding="utf-8")

        self.assertNotIn("fltmc >nul 2>&1", content)
        self.assertNotIn("Verb RunAs", content)


if __name__ == "__main__":
    unittest.main()
