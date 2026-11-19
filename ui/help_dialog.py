from PyQt6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QTextBrowser


class HelpDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(self.cfg.tr("help"))
        self.setMinimumSize(560, 480)

        is_dark = self.cfg.is_dark_theme()
        background = "#2d2d3a" if is_dark else "#f0f0f0"
        foreground = "#ffffff" if is_dark else "#000000"
        text_background = "#3a3a4a" if is_dark else "#ffffff"
        border = "#555555" if is_dark else "#999999"
        self.setStyleSheet(
            f"QDialog {{ background-color: {background}; }}"
            f"QLabel, QPushButton {{ color: {foreground}; }}"
            f"QTextBrowser {{ background-color: {text_background}; color: {foreground}; "
            f"border: 1px solid {border}; border-radius: 4px; padding: 8px; }}"
        )

        layout = QVBoxLayout(self)
        self.instructions = QTextBrowser()
        self.instructions.setHtml(self.cfg.tr("help_instructions"))
        layout.addWidget(self.instructions)

        close_button = QPushButton(self.cfg.tr("close"))
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
