import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QHeaderView, QCheckBox, QFrame,
    QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

from core.app_paths import resource_path
from core.profile_manager import ProfileManager
from core.bat_generator import BatGenerator
from core.config_manager import ConfigManager



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = ConfigManager()
        self.pm = ProfileManager()
        self._return_to_maximized = False
        self.setup_ui()
        self.apply_theme()
        self.load_profiles_list()
    
    def tr(self, key):
        return self.cfg.tr(key)

    def setup_ui(self):
        self.setWindowTitle(self.tr("app_name"))
        self.setMinimumSize(600, 450)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Toolbar
        toolbar = QHBoxLayout()
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("CG")
        logo_icon.setFixedSize(32, 32)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text = QLabel(self.tr("app_name"))
        logo_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()

        self.btn_help = QPushButton(self.tr("help"))
        self.btn_help.setFixedHeight(28)
        self.btn_help.clicked.connect(self.show_help)
        
        self.btn_settings = QPushButton(self.tr("settings"))
        self.btn_settings.setFixedHeight(28)
        self.btn_settings.clicked.connect(self.show_settings)
        
        self.btn_about = QPushButton(self.tr("about"))
        self.btn_about.setFixedHeight(28)
        self.btn_about.clicked.connect(self.show_about)
        
        toolbar.addLayout(logo_layout)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_help)
        toolbar.addWidget(self.btn_settings)
        toolbar.addWidget(self.btn_about)
        layout.addLayout(toolbar)
        
        # Title
        title = QLabel(self.tr("my_profiles"))
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Profiles table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["", self.tr("profile_name").replace(":", ""), self.tr("last_bat")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(2, 100)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Buttons row
        btn_layout = QHBoxLayout()
        
        self.btn_new = QPushButton(self.tr("new_profile"))
        self.btn_new.clicked.connect(self.create_profile)
        
        self.btn_edit = QPushButton(self.tr("edit"))
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self.edit_profile)
        
        self.btn_delete = QPushButton(self.tr("delete"))
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_profile)
        
        self.btn_generate = QPushButton(self.tr("create_bat"))
        self.btn_generate.setEnabled(False)
        self.btn_generate.clicked.connect(self.generate_bat)
        
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_generate)
        layout.addLayout(btn_layout)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_left = QLabel(f"{self.tr('selected')}: 0 {self.tr('profiles')}")
        self.status_right = QLabel(f"{self.tr('last_bat')}: --")
        status_layout.addWidget(self.status_left)
        status_layout.addStretch()
        status_layout.addWidget(self.status_right)
        layout.addLayout(status_layout)
    
    def apply_theme(self):
        is_dark = self.cfg.is_dark_theme()
        
        if is_dark:
            bg_color = "#2d2d3a"
            fg_color = "#ffffff"
            table_bg = "#3a3a4a"
            table_sel = "#4a5a7a"
            btn_bg = "#5a5a6a"
            btn_primary = "#6a8aaa"
            btn_danger = "#a06060"
            header_bg = "#3a3a4a"
            border_color = "#555555"
            input_bg = "#4a4a5a"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            table_bg = "#ffffff"
            table_sel = "#d0e0f0"
            btn_bg = "#b8b8b8"
            btn_primary = "#7a9ab6"
            btn_danger = "#c08080"
            header_bg = "#f8f8f8"
            border_color = "#999999"
            input_bg = "#ffffff"
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg_color}; }}
            QLabel {{ color: {fg_color}; font-weight: bold; }}
            QPushButton {{ 
                background-color: {btn_bg}; 
                color: {fg_color}; 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 8px 16px; 
                font-weight: bold; 
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {btn_bg}aa; }}
            QPushButton:disabled {{ opacity: 0.5; }}
            QTableWidget {{ 
                background-color: {table_bg}; 
                border: 1px solid {border_color}; 
                border-radius: 6px; 
                color: {fg_color};
                font-weight: bold;
                gridline-color: {border_color};
            }}
            QTableWidget::item {{ color: {fg_color}; font-weight: bold; padding: 8px; }}
            QTableWidget::item:selected {{ background-color: {table_sel}; }}
            QHeaderView::section {{ 
                background-color: {header_bg}; 
                color: {fg_color}; 
                font-weight: bold; 
                border: 1px solid {border_color};
                padding: 8px;
            }}
            QCheckBox {{ color: {fg_color}; font-weight: bold; }}
            QCheckBox::indicator {{ 
                width: 18px; 
                height: 18px; 
                border: 1px solid {border_color};
                border-radius: 3px;
                background: {table_bg};
            }}
            QCheckBox::indicator:checked {{ 
                background: #4caf50;
                border: 1px solid #4caf50;
            }}
            QScrollBar:vertical {{
                background: {header_bg};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {btn_bg};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {border_color};
            }}
        """)
    
    def load_profiles_list(self):
        self.table.setRowCount(0)
        profiles = self.pm.list_profiles()
        
        for i, filename in enumerate(profiles):
            try:
                profile = self.pm.load_profile(filename)
                self.table.insertRow(i)
                
                checkbox = QCheckBox()
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                self.table.setCellWidget(i, 0, checkbox_widget)
                
                name_item = QTableWidgetItem(profile.name)
                name_item.setData(Qt.ItemDataRole.UserRole, filename)
                self.table.setItem(i, 1, name_item)
                
                filepath = self.pm.profiles_dir / f"{filename}.json"
                if filepath.exists():
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    date_str = mtime.strftime("%d.%m.%Y")
                else:
                    date_str = "--"
                self.table.setItem(i, 2, QTableWidgetItem(date_str))
                
            except Exception as e:
                print(f"Error loading profile {filename}: {e}")
        
        self.status_left.setText(f"{self.tr('selected')}: 0 {self.tr('profiles')}")
    
    def on_selection_changed(self):
        selected = self.table.selectedItems()
        has_selection = len(selected) > 0
        
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)
        self.btn_generate.setEnabled(has_selection)
        
        if has_selection:
            name = self.table.item(selected[0].row(), 1).text()
            self.status_left.setText(f"{self.tr('selected')}: {name}")
        else:
            self.status_left.setText(f"{self.tr('selected')}: 0 {self.tr('profiles')}")
    
    def get_selected_filename(self):
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = selected[0].row()
        return self.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
    
    def create_profile(self):
        from ui.editor_window import EditorWindow
        self.editor = EditorWindow(self.pm, None, self.cfg)
        self.editor.profile_saved.connect(self.on_profile_saved)
        self._return_to_maximized = self.isMaximized()
        self.editor.show()
        self.hide()
    
    def edit_profile(self):
        filename = self.get_selected_filename()
        if not filename:
            return
        
        from ui.editor_window import EditorWindow
        try:
            profile = self.pm.load_profile(filename)
            self.editor = EditorWindow(self.pm, profile, self.cfg)
            self.editor.profile_saved.connect(self.on_profile_saved)
            self._return_to_maximized = self.isMaximized()
            self.editor.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))
    
    def on_profile_saved(self):
        if hasattr(self, 'editor'):
            self.editor.close()
            del self.editor
        self.load_profiles_list()
        self.show()
        QTimer.singleShot(0, self._restore_after_editor)

    def _restore_after_editor(self):
        if self._return_to_maximized:
            self.showMaximized()
        else:
            self.showNormal()
        self.layout().activate()
        central = self.centralWidget()
        if central and central.layout():
            central.layout().activate()
            central.update()
        self.raise_()
        self.activateWindow()
    
    def delete_profile(self):
        filename = self.get_selected_filename()
        if not filename:
            return
        
        reply = QMessageBox.question(
            self, self.tr("delete"),
            self.tr("delete_confirm").format(filename),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.pm.delete_profile(filename)
                self.load_profiles_list()
            except Exception as e:
                QMessageBox.critical(self, self.tr("error"), str(e))
    
    def generate_bat(self):
        filename = self.get_selected_filename()
        if not filename:
            return
        
        try:
            profile = self.pm.load_profile(filename)
            bat_folder = self.cfg.get("bat_folder")
            gen = BatGenerator(desktop_path=bat_folder)
            path = gen.generate(profile)
            
            self.status_right.setText(f"{self.tr('last_bat')}: {datetime.now().strftime('%H:%M')}")
            
            reply = QMessageBox.information(
                self, self.tr("success"),
                self.tr("file_created").format(path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import subprocess
                subprocess.run(["explorer", "/select,", str(path)])
                
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))
    
    def show_settings(self):
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.cfg, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cfg.load_locale()
            self.apply_theme()
            self.load_profiles_list()
    
    def show_about(self):
        from ui.about_dialog import AboutDialog
        dialog = AboutDialog(self.cfg, self)
        dialog.exec()

    def show_help(self):
        from ui.help_dialog import HelpDialog
        dialog = HelpDialog(self.cfg, self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    icon_path = resource_path("resources/icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()