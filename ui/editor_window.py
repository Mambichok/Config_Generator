from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QSpinBox, QLabel,
    QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class EditorWindow(QDialog):
    profile_saved = pyqtSignal()
    
    def __init__(self, pm, profile, cfg):
        super().__init__()
        self.pm = pm
        self.profile = profile
        self.cfg = cfg
        self.items = []
        self.current_app_index = None
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        
        if profile:
            from copy import deepcopy
            self.items = [deepcopy(item) for item in profile.items]
            self.is_new = False
        else:
            self.is_new = True
        
        self.setup_ui()
        self.apply_theme()
        self.load_data()
    
    def tr(self, key):
        return self.cfg.tr(key)
    
    def setup_ui(self):
        self.setWindowTitle(self.tr("profile_editor"))
        self.setMinimumSize(650, 550)
        
        window_layout = QVBoxLayout(self)
        window_layout.setSpacing(8)
        window_layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header = QHBoxLayout()
        self.btn_back = QPushButton(self.tr("back"))
        self.btn_back.clicked.connect(self.go_back)
        
        header.addWidget(self.btn_back)
        header.addStretch()
        
        self.btn_cancel = QPushButton(self.tr("cancel"))
        self.btn_cancel.clicked.connect(self.go_back)
        
        self.btn_save = QPushButton(self.tr("save"))
        self.btn_save.clicked.connect(self.save_profile)
        
        header.addWidget(self.btn_cancel)
        header.addWidget(self.btn_save)
        window_layout.addLayout(header)

        self.content_scroll = QScrollArea()
        self.content_scroll.setWidgetResizable(True)
        self.content_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content_widget = QWidget()
        layout = QVBoxLayout(self.content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        self.content_scroll.setWidget(self.content_widget)
        window_layout.addWidget(self.content_scroll)
        
        # Profile info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(self.tr("profile_name")))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Work")
        info_layout.addWidget(self.name_input, 2)
        
        info_layout.addWidget(QLabel(self.tr("bat_filename")))
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("work")
        info_layout.addWidget(self.filename_input, 1)
        
        self.btn_auto = QPushButton(self.tr("auto"))
        self.btn_auto.setFixedWidth(60)
        self.btn_auto.clicked.connect(self.auto_filename)
        info_layout.addWidget(self.btn_auto)
        layout.addLayout(info_layout)
        
        # Delay
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel(self.tr("delay")))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(self.cfg.get("default_delay", 1))
        self.delay_spin.setSuffix(f" {self.tr('sec')}")
        delay_layout.addWidget(self.delay_spin)
        delay_layout.addStretch()
        
        self.admin_check = QCheckBox(self.tr("run_as_admin"))
        delay_layout.addWidget(self.admin_check)
        layout.addLayout(delay_layout)
        
        # Apps list
        layout.addWidget(QLabel(self.tr("apps_in_profile")))
        layout.addWidget(QLabel(self.tr("drag_tip")))
        
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(4)
        self.apps_table.setHorizontalHeaderLabels(["#", self.tr("display_name").replace(":", ""), self.tr("full_path").replace(":", ""), "TYPE"])
        self.apps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.apps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.apps_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.apps_table.setColumnWidth(0, 30)
        self.apps_table.setColumnWidth(3, 80)
        self.apps_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.apps_table.itemSelectionChanged.connect(self.on_app_selected)
        layout.addWidget(self.apps_table)
        
        # App controls
        app_ctrl = QHBoxLayout()
        self.btn_add_file = QPushButton(self.tr("add_file"))
        self.btn_add_file.clicked.connect(self.add_file)
        
        self.btn_remove_app = QPushButton(self.tr("delete"))
        self.btn_remove_app.setEnabled(False)
        self.btn_remove_app.clicked.connect(self.remove_app)
        
        self.btn_up = QPushButton(self.tr("up"))
        self.btn_up.setEnabled(False)
        self.btn_up.clicked.connect(self.move_up)
        
        self.btn_down = QPushButton(self.tr("down"))
        self.btn_down.setEnabled(False)
        self.btn_down.clicked.connect(self.move_down)
        
        app_ctrl.addWidget(self.btn_add_file)
        app_ctrl.addWidget(self.btn_remove_app)
        app_ctrl.addWidget(self.btn_up)
        app_ctrl.addWidget(self.btn_down)
        layout.addLayout(app_ctrl)
        
        # Details panel
        self.details_frame = QFrame()
        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setSpacing(8)
        
        self.details_title = QLabel(self.tr("settings_app"))
        details_layout.addWidget(self.details_title)
        
        # Display name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(self.tr("display_name")))
        self.app_name_input = QLineEdit()
        name_row.addWidget(self.app_name_input)
        details_layout.addLayout(name_row)
        
        # Path
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel(self.tr("full_path")))
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText(self.tr("paste_path"))
        path_row.addWidget(self.app_path_input)
        
        self.btn_browse = QPushButton(self.tr("browse"))
        self.btn_browse.clicked.connect(self.browse_file)
        path_row.addWidget(self.btn_browse)
        details_layout.addLayout(path_row)
        
        # Args
        args_row = QHBoxLayout()
        args_row.addWidget(QLabel(self.tr("arguments")))
        self.app_args_input = QLineEdit()
        self.app_args_input.setPlaceholderText("--fullscreen")
        args_row.addWidget(self.app_args_input)
        details_layout.addLayout(args_row)
        
        # Browser options
        self.browser_check = QCheckBox(self.tr("is_browser"))
        self.browser_check.stateChanged.connect(self.on_browser_changed)
        details_layout.addWidget(self.browser_check)
        
        self.single_window_check = QCheckBox(self.tr("single_window"))
        self.single_window_check.setEnabled(False)
        details_layout.addWidget(self.single_window_check)
        
        # URLs
        self.urls_label = QLabel(self.tr("urls"))
        self.urls_label.setEnabled(False)
        details_layout.addWidget(self.urls_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        self.url_input.setEnabled(False)
        details_layout.addWidget(self.url_input)
        
        self.btn_add_url = QPushButton(self.tr("add_url"))
        self.btn_add_url.setEnabled(False)
        self.btn_add_url.clicked.connect(self.add_url)
        details_layout.addWidget(self.btn_add_url)
        
        self.urls_list = QTableWidget()
        self.urls_list.setColumnCount(2)
        self.urls_list.setHorizontalHeaderLabels(["URL", ""])
        self.urls_list.setColumnWidth(0, 400)
        self.urls_list.setColumnWidth(1, 40)
        self.urls_list.setMinimumHeight(100)
        self.urls_list.setMaximumHeight(220)
        self.urls_list.setEnabled(False)
        details_layout.addWidget(self.urls_list)
        
        layout.addWidget(self.details_frame)
        
        # Hint
        hint = QLabel(self.tr("tip_drag"))
        hint.setStyleSheet("font-size: 11px; font-style: italic;")
        layout.addWidget(hint)
    
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
            btn_back = "#a06060"
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
            btn_back = "#c08080"
            header_bg = "#f8f8f8"
            border_color = "#999999"
            input_bg = "#ffffff"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_color}; }}
            QLabel {{ color: {fg_color}; font-weight: bold; font-size: 13px; }}
            QLineEdit {{ 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 6px 10px; 
                font-weight: bold; 
                color: {fg_color};
                background: {input_bg};
            }}
            QSpinBox {{ 
                border: 1px solid {border_color}; 
                border-radius: 4px; 
                padding: 6px; 
                font-weight: bold; 
                color: {fg_color};
                background: {input_bg};
            }}
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
            QTableWidget {{ 
                background-color: {table_bg}; 
                border: 1px solid {border_color}; 
                border-radius: 6px; 
                color: {fg_color};
                font-weight: bold;
                gridline-color: {border_color};
            }}
            QTableWidget::item {{ color: {fg_color}; font-weight: bold; padding: 6px; }}
            QTableWidget::item:selected {{ background-color: {table_sel}; }}
            QHeaderView::section {{ 
                background-color: {header_bg}; 
                color: {fg_color}; 
                font-weight: bold; 
                border: 1px solid {border_color};
                padding: 6px;
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
            QFrame {{ 
                border: 1px solid {border_color}; 
                border-radius: 6px; 
                background: {table_bg};
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
        """)
        
        # Special button styles
        self.btn_back.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_back}; color: {fg_color}; border: 1px solid {border_color}; }}
            QPushButton:hover {{ background-color: {btn_back}aa; }}
        """)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_primary}; color: {fg_color}; border: 1px solid {border_color}; }}
            QPushButton:hover {{ background-color: {btn_primary}aa; }}
        """)
        self.btn_add_file.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_primary}; color: {fg_color}; border: 1px solid {border_color}; }}
            QPushButton:hover {{ background-color: {btn_primary}aa; }}
        """)
    
    def load_data(self):
        self.delay_spin.setValue(self.cfg.get("default_delay", 1))
        if not self.profile:
            return
        
        self.name_input.setText(self.profile.name)
        self.filename_input.setText(self.profile.filename)
        self.delay_spin.setValue(self.profile.delay)
        self.admin_check.setChecked(self.profile.run_as_admin)
        self.single_window_check.setChecked(self.profile.single_browser_window)
        
        self.refresh_apps_table()
    
    def refresh_apps_table(self):
        self.apps_table.setRowCount(0)
        for i, item in enumerate(self.items):
            self.apps_table.insertRow(i)
            self.apps_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.apps_table.setItem(i, 1, QTableWidgetItem(item.name))
            self.apps_table.setItem(i, 2, QTableWidgetItem(item.path))
            
            app_type = "BROWSER" if item.is_browser else "APP"
            self.apps_table.setItem(i, 3, QTableWidgetItem(app_type))
    
    def on_app_selected(self):
        self.save_app_details()
        selected = self.apps_table.selectedItems()
        has_selection = len(selected) > 0
        
        self.btn_remove_app.setEnabled(has_selection)
        self.btn_up.setEnabled(has_selection)
        self.btn_down.setEnabled(has_selection)
        
        if has_selection:
            row = selected[0].row()
            self.current_app_index = row
            item = self.items[row]
            self.load_app_details(item)
        else:
            self.current_app_index = None
            self.clear_app_details()
    
    def load_app_details(self, item):
        self.current_app_index = next(
            (index for index, candidate in enumerate(self.items) if candidate is item),
            None
        )
        self.app_name_input.setText(item.name)
        self.app_path_input.setText(item.path)
        self.app_args_input.setText(item.args)
        self.browser_check.setChecked(item.is_browser)
        
        self.urls_list.setRowCount(0)
        for url in item.urls:
            row = self.urls_list.rowCount()
            self.urls_list.insertRow(row)
            self.urls_list.setItem(row, 0, QTableWidgetItem(url))
            del_btn = QPushButton("x")
            del_btn.setStyleSheet("background: #c08080; color: #000; border: 1px solid #999;")
            del_btn.clicked.connect(
                lambda checked=False, button=del_btn: self.remove_url(button)
            )
            self.urls_list.setCellWidget(row, 1, del_btn)

    def save_app_details(self):
        index = self.current_app_index
        if index is None or index >= len(self.items):
            return

        item = self.items[index]
        item.name = self.app_name_input.text().strip()
        path = self.app_path_input.text().strip()
        if len(path) >= 2 and path[0] == path[-1] == '"':
            path = path[1:-1].strip()
        item.path = path.replace("/", "\\")
        item.args = self.app_args_input.text().strip()
        item.is_browser = self.browser_check.isChecked()
        item.urls = [
            self.urls_list.item(row, 0).text()
            for row in range(self.urls_list.rowCount())
            if self.urls_list.item(row, 0)
        ]

        self.apps_table.item(index, 1).setText(item.name)
        self.apps_table.item(index, 2).setText(item.path)
        self.apps_table.item(index, 3).setText("BROWSER" if item.is_browser else "APP")

    def remove_url(self, button):
        url_index = next(
            (
                row for row in range(self.urls_list.rowCount())
                if self.urls_list.cellWidget(row, 1) is button
            ),
            None
        )
        item_index = self.current_app_index
        if url_index is None or item_index is None:
            return

        self.save_app_details()
        del self.items[item_index].urls[url_index]
        self.load_app_details(self.items[item_index])
    
    def clear_app_details(self):
        self.app_name_input.clear()
        self.app_path_input.clear()
        self.app_args_input.clear()
        self.browser_check.setChecked(False)
        self.urls_list.setRowCount(0)
    
    def on_browser_changed(self, state):
        is_browser = state == Qt.CheckState.Checked.value
        self.single_window_check.setEnabled(is_browser)
        self.urls_label.setEnabled(is_browser)
        self.url_input.setEnabled(is_browser)
        self.btn_add_url.setEnabled(is_browser)
        self.urls_list.setEnabled(is_browser)
    
    def add_file(self):
        self.save_app_details()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Applications (*.exe *.lnk);;All Files (*)"
        )
        
        if file_path:
            name = Path(file_path).stem
            is_browser = any(b in name.lower() for b in ["chrome", "firefox", "edge", "opera", "yandex", "brave"])
            
            from models.profile import AppItem
            item = AppItem(name=name, path=file_path, is_browser=is_browser)
            self.items.append(item)
            self.refresh_apps_table()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Application",
            "",
            "Applications (*.exe *.lnk);;All Files (*)"
        )
        
        if file_path:
            self.app_path_input.setText(file_path)
    
    def remove_app(self):
        selected = self.apps_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        self.current_app_index = None
        del self.items[row]
        self.refresh_apps_table()
        self.clear_app_details()
    
    def move_up(self):
        selected = self.apps_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        if row > 0:
            self.save_app_details()
            self.current_app_index = None
            self.items[row], self.items[row - 1] = self.items[row - 1], self.items[row]
            self.refresh_apps_table()
            self.apps_table.selectRow(row - 1)
    
    def move_down(self):
        selected = self.apps_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        if row < len(self.items) - 1:
            self.save_app_details()
            self.current_app_index = None
            self.items[row], self.items[row + 1] = self.items[row + 1], self.items[row]
            self.refresh_apps_table()
            self.apps_table.selectRow(row + 1)
    
    def add_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        
        selected = self.apps_table.selectedItems()
        if not selected:
            return
        
        self.save_app_details()
        row = selected[0].row()
        self.items[row].urls.append(url)
        self.load_app_details(self.items[row])
        self.url_input.clear()
    
    def auto_filename(self):
        name = self.name_input.text().strip()
        if name:
            import re
            filename = re.sub(r'[^a-zA-Z0-9]', '_', name).lower()
            filename = re.sub(r'_+', '_', filename).strip('_')
            self.filename_input.setText(filename)
    
    def save_profile(self):
        name = self.name_input.text().strip()
        filename = self.filename_input.text().strip()
        
        if not name or not filename:
            QMessageBox.warning(self, self.tr("error"), self.tr("name_required"))
            return
        
        from models.profile import Profile
        self.save_app_details()
        profile = Profile(
            name=name,
            filename=filename,
            items=self.items,
            delay=self.delay_spin.value(),
            single_browser_window=self.single_window_check.isChecked(),
            run_as_admin=self.admin_check.isChecked()
        )
        
        try:
            self.pm.save_profile(profile)
            self.profile_saved.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))
    
    def go_back(self):
        reply = QMessageBox.question(
            self, self.tr("cancel"),
            self.tr("discard_changes"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()
            # ВОЗВРАЩАЕМ главное окно!
            self.profile_saved.emit()