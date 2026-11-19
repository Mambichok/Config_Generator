from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(self.tr("about"))
        self.setMinimumSize(280, 260)
        self.apply_theme()
        self.setup_ui()
    
    def tr(self, key):
        return self.cfg.tr(key)
    
    def apply_theme(self):
        is_dark = self.cfg.is_dark_theme()
        
        if is_dark:
            bg_color = "#2d2d3a"
            fg_color = "#ffffff"
            btn_primary = "#6a8aaa"
            border_color = "#555555"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            btn_primary = "#7a9ab6"
            border_color = "#999999"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_color}; }}
            QLabel {{ color: {fg_color}; font-weight: bold; }}
            QPushButton {{ 
                background-color: {btn_primary}; 
                color: {fg_color}; 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 8px 16px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background-color: {btn_primary}aa; }}
        """)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        icon = QLabel("CG")
        icon.setStyleSheet("""
            background-color: #5a7a96; 
            color: white; 
            border: 1px solid #999; 
            border-radius: 10px; 
            font-size: 20px; 
            font-weight: bold;
        """)
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Config Generator")
        title.setStyleSheet("font-size: 16px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        version = QLabel(self.tr("version"))
        version.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel(self.tr("description"))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc, alignment=Qt.AlignmentFlag.AlignCenter)
        
        telegram_link = QLabel(
            f"<a href='https://t.me/MambichIT'>{self.tr('telegram_channel')}</a>"
        )
        telegram_link.setOpenExternalLinks(True)
        telegram_link.setStyleSheet("color: #5a7a96; text-decoration: underline;")
        layout.addWidget(telegram_link, alignment=Qt.AlignmentFlag.AlignCenter)

        link = QLabel("<a href='https://github.com/Mambichok'>github.com/Mambichok</a>")
        link.setOpenExternalLinks(True)
        link.setStyleSheet("color: #5a7a96; text-decoration: underline;")
        layout.addWidget(link, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_close = QPushButton(self.tr("close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)