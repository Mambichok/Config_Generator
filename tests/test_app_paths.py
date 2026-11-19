import json
import tempfile
import unittest
from pathlib import Path

from core.app_paths import MIGRATION_MARKER, user_data_dir
from core.config_manager import ConfigManager
from models.profile import AppItem, Profile


class AppPathsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.legacy_dir = self.root / "legacy"
        self.data_dir = self.root / "app-data"
        (self.legacy_dir / "profiles").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_migrates_existing_config_and_profiles_once(self):
        old_config = {"language": "ru", "theme": "dark"}
        (self.legacy_dir / "config.json").write_text(
            json.dumps(old_config), encoding="utf-8"
        )
        old_profile = {"name": "Work", "filename": "work", "items": []}
        (self.legacy_dir / "profiles" / "work.json").write_text(
            json.dumps(old_profile), encoding="utf-8"
        )

        user_data_dir(self.data_dir, [self.legacy_dir])

        self.assertEqual(
            json.loads((self.data_dir / "config.json").read_text(encoding="utf-8")),
            old_config
        )
        self.assertTrue((self.data_dir / "profiles" / "work.json").is_file())
        self.assertTrue((self.data_dir / MIGRATION_MARKER).is_file())

        (self.legacy_dir / "config.json").write_text(
            json.dumps({"language": "en"}), encoding="utf-8"
        )
        (self.legacy_dir / "profiles" / "later.json").write_text(
            json.dumps({"name": "Later"}), encoding="utf-8"
        )
        user_data_dir(self.data_dir, [self.legacy_dir])

        self.assertEqual(
            json.loads((self.data_dir / "config.json").read_text(encoding="utf-8")),
            old_config
        )
        self.assertFalse((self.data_dir / "profiles" / "later.json").exists())

    def test_existing_user_data_wins_during_migration(self):
        (self.legacy_dir / "config.json").write_text(
            json.dumps({"language": "ru"}), encoding="utf-8"
        )
        (self.legacy_dir / "profiles" / "work.json").write_text(
            json.dumps({"name": "Legacy"}), encoding="utf-8"
        )
        (self.data_dir / "profiles").mkdir(parents=True)
        (self.data_dir / "config.json").write_text(
            json.dumps({"language": "en"}), encoding="utf-8"
        )
        (self.data_dir / "profiles" / "work.json").write_text(
            json.dumps({"name": "Current"}), encoding="utf-8"
        )

        user_data_dir(self.data_dir, [self.legacy_dir])

        self.assertEqual(
            json.loads((self.data_dir / "config.json").read_text(encoding="utf-8")),
            {"language": "en"}
        )
        self.assertEqual(
            json.loads(
                (self.data_dir / "profiles" / "work.json").read_text(encoding="utf-8")
            ),
            {"name": "Current"}
        )

    def test_config_uses_user_data_path_and_bundled_locale_path(self):
        repo_root = Path(__file__).resolve().parents[1]
        config = ConfigManager(
            data_dir=self.data_dir,
            locale_dir=repo_root / "locales"
        )
        config.set("language", "ru")
        config.load_locale()

        self.assertEqual(config.config_path, self.data_dir / "config.json")
        self.assertEqual(config.tr("about"), "О ПРОГРАММЕ")

    def test_old_profile_without_admin_flag_remains_compatible(self):
        profile_data = {
            "name": "Work",
            "filename": "work",
            "items": [AppItem(name="Browser", path="browser.exe").to_dict()]
        }

        profile = Profile.from_dict(profile_data)

        self.assertFalse(profile.run_as_admin)
        self.assertIn("items", profile_data)

    def test_profile_serializes_admin_flag(self):
        profile = Profile(
            name="Work",
            filename="work",
            items=[],
            run_as_admin=True
        )

        self.assertTrue(Profile.from_dict(profile.to_dict()).run_as_admin)


if __name__ == "__main__":
    unittest.main()
