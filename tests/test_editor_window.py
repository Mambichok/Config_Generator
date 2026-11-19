import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QScrollArea

from core.profile_manager import ProfileManager
from models.profile import AppItem, Profile
from ui.editor_window import EditorWindow


class ConfigStub:
    def get(self, key, default=None):
        return {"default_delay": 4}.get(key, default)

    def tr(self, key):
        return key

    def is_dark_theme(self):
        return False


class EditorWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.profile_manager = ProfileManager(
            Path(self.temp_dir.name) / "profiles"
        )
        self.config = ConfigStub()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_new_profile_uses_configured_default_delay(self):
        window = EditorWindow(self.profile_manager, None, self.config)
        self.addCleanup(window.close)

        self.assertEqual(window.delay_spin.value(), 4)

    def test_editing_profile_preserves_flags_and_saves_app_and_url_changes(self):
        profile = Profile(
            name="Work",
            filename="work",
            items=[
                AppItem(
                    name="Browser",
                    path="C:\\Apps\\browser.exe",
                    is_browser=True,
                    urls=["https://example.com", "https://example.org"]
                ),
                AppItem(name="Editor", path="C:\\Apps\\editor.exe")
            ],
            delay=2,
            single_browser_window=True,
            run_as_admin=True
        )
        window = EditorWindow(self.profile_manager, profile, self.config)
        self.addCleanup(window.close)
        window.apps_table.selectRow(0)
        window.app_name_input.setText("Updated Browser")
        window.app_path_input.setText('"C:\\Apps\\Updated Browser.exe"')
        window.app_args_input.setText("--private")
        window.apps_table.selectRow(1)
        self.assertEqual(window.items[0].name, "Updated Browser")
        window.apps_table.selectRow(0)
        window.urls_list.cellWidget(0, 1).click()
        window.save_profile()

        saved = self.profile_manager.load_profile("work")
        self.assertEqual(saved.items[0].name, "Updated Browser")
        self.assertEqual(saved.items[0].path, "C:\\Apps\\Updated Browser.exe")
        self.assertEqual(saved.items[0].args, "--private")
        self.assertEqual(saved.items[0].urls, ["https://example.org"])
        self.assertTrue(saved.single_browser_window)
        self.assertTrue(saved.run_as_admin)
        self.assertEqual(saved.delay, 2)
        self.assertIsInstance(window.content_scroll, QScrollArea)
        self.assertFalse(window.app_path_input.isReadOnly())


if __name__ == "__main__":
    unittest.main()
