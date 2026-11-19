import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QLabel

from ui.about_dialog import AboutDialog
from ui.help_dialog import HelpDialog
from ui.main_window import MainWindow


class ConfigStub:
    def tr(self, key):
        return {
            "help": "Help",
            "help_instructions": "<h2>Getting started</h2><p>Choose an application.</p>",
            "telegram_channel": "Telegram channel: @MambichIT",
        }.get(key, key)

    def is_dark_theme(self):
        return False


class UIFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_help_dialog_displays_the_instruction_content(self):
        dialog = HelpDialog(ConfigStub())
        self.addCleanup(dialog.close)

        self.assertIn("Getting started", dialog.instructions.toPlainText())

    def test_about_dialog_displays_creator_telegram_link(self):
        dialog = AboutDialog(ConfigStub())
        self.addCleanup(dialog.close)

        self.assertTrue(
            any("https://t.me/MambichIT" in label.text() for label in dialog.findChildren(QLabel))
        )

    def test_main_window_has_no_extra_maximize_button(self):
        window = MainWindow()
        self.addCleanup(window.close)

        self.assertFalse(hasattr(window, "btn_maximize"))

    def test_returning_from_profile_editor_restores_maximized_layout(self):
        window = MainWindow()
        window.pm.list_profiles = lambda: []
        window.showMaximized()
        self.app.processEvents()
        window._return_to_maximized = True
        window.hide()

        class EditorStub:
            def close(self):
                pass

        window.editor = EditorStub()
        window.on_profile_saved()
        self.app.processEvents()
        self.addCleanup(window.close)

        central = window.centralWidget()
        self.assertTrue(window.isMaximized())
        self.assertEqual(central.width(), window.contentsRect().width())
        self.assertEqual(central.height(), window.contentsRect().height())
