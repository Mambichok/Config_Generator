from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QSpinBox, QLineEdit,
    QLabel, QCheckBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle(self.tr("settings"))
        self.setMinimumSize(400, 350)
        
        self.setup_ui()
        self.apply_theme()
        self.load_settings()
    
    def tr(self, key):
        return self.cfg.tr(key)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # General section
        layout.addWidget(QLabel(self.tr("general")))
        layout.addWidget(self.create_separator())
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel(self.tr("default_delay")))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setSuffix(f" {self.tr('sec')}")
        delay_layout.addWidget(self.delay_spin)
        delay_layout.addStretch()
        layout.addLayout(delay_layout)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel(self.tr("bat_folder")))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Desktop")
        folder_layout.addWidget(self.folder_input)
        
        self.btn_browse_folder = QPushButton(self.tr("browse"))
        self.btn_browse_folder.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.btn_browse_folder)
        layout.addLayout(folder_layout)
        
        self.notify_check = QCheckBox(self.tr("show_notification"))
        layout.addWidget(self.notify_check)
        
        # Appearance section
        layout.addWidget(QLabel(self.tr("appearance")))
        layout.addWidget(self.create_separator())
        
        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel(self.tr("theme")))
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(self.tr("language")))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Русский"])
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        self.tray_check = QCheckBox(self.tr("minimize_tray"))
        layout.addWidget(self.tray_check)
        
        layout.addStretch()
        
        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        
        self.btn_reset = QPushButton(self.tr("reset"))
        self.btn_reset.clicked.connect(self.reset_settings)
        
        self.btn_save = QPushButton(self.tr("save"))
        self.btn_save.clicked.connect(self.save_settings)
        
        footer.addWidget(self.btn_reset)
        footer.addWidget(self.btn_save)
        layout.addLayout(footer)
    
    def apply_theme(self):
        is_dark = self.cfg.is_dark_theme()
        
        if is_dark:
            bg_color = "#2d2d3a"
            fg_color = "#ffffff"
            btn_bg = "#5a5a6a"
            btn_primary = "#6a8aaa"
            header_bg = "#3a3a4a"
            border_color = "#555555"
            input_bg = "#4a4a5a"
            combo_bg = "#4a4a5a"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            btn_bg = "#b8b8b8"
            btn_primary = "#7a9ab6"
            header_bg = "#f8f8f8"
            border_color = "#999999"
            input_bg = "#ffffff"
            combo_bg = "#ffffff"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_color}; }}
            QLabel {{ color: {fg_color}; font-weight: bold; font-size: 13px; }}
            QPushButton {{ 
                background-color: {btn_bg}; 
                color: {fg_color}; 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 6px 14px; 
                font-weight: bold; 
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {btn_bg}aa; }}
            QSpinBox {{ 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 4px; 
                font-weight: bold; 
                color: {fg_color};
                background: {input_bg};
            }}
            QLineEdit {{ 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 4px 8px; 
                font-weight: bold; 
                color: {fg_color};
                background: {input_bg};
            }}
            QCheckBox {{ color: {fg_color}; font-weight: bold; }}
            QCheckBox::indicator {{ 
                width: 18px; 
                height: 18px; 
                border: 1px solid {border_color};
                border-radius: 3px;
                background: {input_bg};
            }}
            QCheckBox::indicator:checked {{ 
                background: #4caf50;
                border: 1px solid #4caf50;
            }}
            QComboBox {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
                background: {combo_bg};
                color: {fg_color};
                font-weight: bold;
                min-width: 100px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {combo_bg};
                color: {fg_color};
                border: 1px solid {border_color};
                selection-background-color: {btn_primary};
                selection-color: {fg_color};
            }}
        """)
        
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_primary}; color: {fg_color}; border: 1px solid {border_color}; }}
            QPushButton:hover {{ background-color: {btn_primary}aa; }}
        """)
    
    def create_separator(self):
        from PyQt6.QtWidgets import QFrame
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #5a7a96; max-height: 2px; border: none;")
        return line
    
    def load_settings(self):
        self.delay_spin.setValue(self.cfg.get("default_delay", 1))
        self.folder_input.setText(self.cfg.get("bat_folder") or "")
        self.notify_check.setChecked(self.cfg.get("show_notification", True))
        self.tray_check.setChecked(self.cfg.get("minimize_tray", False))
        
        theme = self.cfg.get("theme", "light")
        self.theme_combo.setCurrentIndex({"light": 0, "dark": 1, "auto": 2}.get(theme, 0))
        
        lang = self.cfg.get("language", "en")
        self.lang_combo.setCurrentIndex(0 if lang == "en" else 1)
    
    def save_settings(self):
        theme_map = {0: "light", 1: "dark", 2: "auto"}
        lang_map = {0: "en", 1: "ru"}
        
        self.cfg.set("default_delay", self.delay_spin.value())
        self.cfg.set("bat_folder", self.folder_input.text() or None)
        self.cfg.set("show_notification", self.notify_check.isChecked())
        self.cfg.set("minimize_tray", self.tray_check.isChecked())
        self.cfg.set("theme", theme_map.get(self.theme_combo.currentIndex(), "light"))
        self.cfg.set("language", lang_map.get(self.lang_combo.currentIndex(), "en"))
        
        self.cfg.save()
        self.cfg.load_locale()
        self.accept()
    
    def reset_settings(self):
        self.delay_spin.setValue(1)
        self.folder_input.clear()
        self.notify_check.setChecked(True)
        self.tray_check.setChecked(False)
        self.theme_combo.setCurrentIndex(0)
        self.lang_combo.setCurrentIndex(0)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)