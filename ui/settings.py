# ui/settings.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QFontComboBox, QColorDialog, QGroupBox,
    QFormLayout, QMessageBox, QTabWidget, QWidget, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from config import Config
from theme.theme import ThemeManager

class SettingsDialog(QDialog):
    """設定ダイアログ"""
    
    settings_changed = pyqtSignal()  # 設定変更時に発火
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        try:
            self.config = config
            self.theme_manager = ThemeManager(config)
            self.setWindowTitle("設定")
            self.setModal(True)
            self.resize(600, 500)
            
            # 一時的な設定（適用ボタンで保存）
            self._temp_config = config.get_all()
            
            self._init_ui()
            self._load_settings()
        except Exception as e:
            import traceback
            error_msg = f"設定ダイアログの初期化に失敗しました:\n{str(e)}"
            if config.get("debug.show_traceback", True):
                error_msg += f"\n\n詳細:\n{traceback.format_exc()}"
            print(error_msg)
            raise
    
    def _init_ui(self):
        """UIを初期化"""
        try:
            layout = QVBoxLayout(self)
            
            # タブウィジェット
            tabs = QTabWidget()
            
            # フォントタブ
            try:
                font_tab = self._create_font_tab()
                tabs.addTab(font_tab, "フォント")
            except Exception as e:
                import traceback
                print(f"フォントタブの作成エラー: {e}")
                if self.config.get("debug.show_traceback", True):
                    traceback.print_exc()
            
            # テーマタブ
            try:
                theme_tab = self._create_theme_tab()
                tabs.addTab(theme_tab, "テーマ")
            except Exception as e:
                import traceback
                print(f"テーマタブの作成エラー: {e}")
                if self.config.get("debug.show_traceback", True):
                    traceback.print_exc()
            
            # サーバータブ
            try:
                server_tab = self._create_server_tab()
                tabs.addTab(server_tab, "サーバー")
            except Exception as e:
                import traceback
                print(f"サーバータブの作成エラー: {e}")
                if self.config.get("debug.show_traceback", True):
                    traceback.print_exc()
            
            # デバッグタブ
            try:
                debug_tab = self._create_debug_tab()
                tabs.addTab(debug_tab, "デバッグ")
            except Exception as e:
                import traceback
                print(f"デバッグタブの作成エラー: {e}")
                if self.config.get("debug.show_traceback", True):
                    traceback.print_exc()
            
            layout.addWidget(tabs)
            
            # ボタン
            button_layout = QHBoxLayout()
            
            self.reset_btn = QPushButton("デフォルトに戻す")
            self.reset_btn.clicked.connect(self._reset_to_default)
            button_layout.addWidget(self.reset_btn)
            
            button_layout.addStretch()
            
            self.cancel_btn = QPushButton("キャンセル")
            self.cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_btn)
            
            self.apply_btn = QPushButton("適用")
            self.apply_btn.clicked.connect(self._apply_settings)
            button_layout.addWidget(self.apply_btn)
            
            self.ok_btn = QPushButton("OK")
            self.ok_btn.clicked.connect(self._ok_clicked)
            button_layout.addWidget(self.ok_btn)
            
            layout.addLayout(button_layout)
        except Exception as e:
            import traceback
            error_msg = f"UIの初期化に失敗しました:\n{str(e)}"
            if self.config.get("debug.show_traceback", True):
                error_msg += f"\n\n詳細:\n{traceback.format_exc()}"
            print(error_msg)
            raise
    
    def _create_font_tab(self) -> QWidget:
        """フォント設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # フォントファミリー
        font_group = QGroupBox("フォントファミリー")
        font_layout = QVBoxLayout()
        
        self.font_combo = QFontComboBox()
        font_layout.addWidget(QLabel("フォント:"))
        font_layout.addWidget(self.font_combo)
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # フォントサイズ
        size_group = QGroupBox("フォントサイズ")
        size_layout = QFormLayout()
        
        self.title_size = QSpinBox()
        self.title_size.setRange(8, 100)
        self.title_size.setSuffix(" pt")
        size_layout.addRow("タイトル:", self.title_size)
        
        self.normal_size = QSpinBox()
        self.normal_size.setRange(8, 100)
        self.normal_size.setSuffix(" pt")
        size_layout.addRow("通常:", self.normal_size)
        
        self.small_size = QSpinBox()
        self.small_size.setRange(8, 100)
        self.small_size.setSuffix(" pt")
        size_layout.addRow("小:", self.small_size)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # 太字設定
        bold_group = QGroupBox("太字設定")
        bold_layout = QVBoxLayout()
        
        self.title_bold = QCheckBox("タイトルを太字にする")
        bold_layout.addWidget(self.title_bold)
        
        self.normal_bold = QCheckBox("通常テキストを太字にする")
        bold_layout.addWidget(self.normal_bold)
        
        self.small_bold = QCheckBox("小テキストを太字にする")
        bold_layout.addWidget(self.small_bold)
        
        bold_group.setLayout(bold_layout)
        layout.addWidget(bold_group)
        
        layout.addStretch()
        return widget
    
    def _create_theme_tab(self) -> QWidget:
        """テーマ設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 色設定
        color_group = QGroupBox("色設定")
        color_layout = QFormLayout()
        
        # 背景色
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(80, 30)
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("background_color", self.bg_color_btn))
        color_layout.addRow("背景色:", self.bg_color_btn)
        
        # テキスト色
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(80, 30)
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color", self.text_color_btn))
        color_layout.addRow("テキスト色:", self.text_color_btn)
        
        # アクセント色
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setFixedSize(80, 30)
        self.accent_color_btn.clicked.connect(lambda: self._pick_color("accent_color", self.accent_color_btn))
        color_layout.addRow("アクセント色:", self.accent_color_btn)
        
        # スプラッシュ背景色
        self.splash_bg_color_btn = QPushButton()
        self.splash_bg_color_btn.setFixedSize(80, 30)
        self.splash_bg_color_btn.clicked.connect(lambda: self._pick_color("splash_bg_color", self.splash_bg_color_btn))
        color_layout.addRow("スプラッシュ背景色:", self.splash_bg_color_btn)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # 表示設定
        display_group = QGroupBox("表示設定")
        display_layout = QVBoxLayout()
        
        self.fullscreen_check = QCheckBox("フルスクリーン表示")
        self.fullscreen_check.setToolTip("チェックすると全画面表示、外すとウィンドウ表示になります")
        display_layout.addWidget(self.fullscreen_check)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        return widget
    
    def _create_server_tab(self) -> QWidget:
        """サーバー設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # サーバー設定
        server_group = QGroupBox("サーバー設定")
        server_layout = QFormLayout()
        
        self.server_enabled = QCheckBox("サーバーを有効にする")
        server_layout.addRow("", self.server_enabled)
        
        self.server_port = QSpinBox()
        self.server_port.setRange(1024, 65535)
        server_layout.addRow("ポート番号:", self.server_port)
        
        self.server_host = QLineEdit()
        server_layout.addRow("ホスト:", self.server_host)
        
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)
        
        layout.addStretch()
        return widget
    
    def _create_debug_tab(self) -> QWidget:
        """デバッグ設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # デバッグ設定
        debug_group = QGroupBox("デバッグ設定")
        debug_layout = QVBoxLayout()
        
        self.debug_enabled = QCheckBox("デバッグモードを有効にする")
        self.debug_enabled.setToolTip("詳細なログとエラー情報を表示します")
        debug_layout.addWidget(self.debug_enabled)
        
        self.show_traceback = QCheckBox("トレースバックを表示する")
        self.show_traceback.setToolTip("エラー発生時に詳細なスタックトレースを表示します")
        debug_layout.addWidget(self.show_traceback)
        
        self.log_to_file = QCheckBox("ログをファイルに出力する")
        self.log_to_file.setToolTip("ログをファイルに保存します")
        debug_layout.addWidget(self.log_to_file)
        
        log_file_layout = QFormLayout()
        self.log_file = QLineEdit()
        log_file_layout.addRow("ログファイル名:", self.log_file)
        debug_layout.addLayout(log_file_layout)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        # 説明
        info_label = QLabel(
            "デバッグモードを有効にすると、詳細なログとエラー情報が表示されます。\n"
            "クラッシュの原因を特定する際に役立ちます。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        return widget
    
    def _pick_color(self, color_key: str, button: QPushButton):
        """色選択ダイアログを表示"""
        current_rgb = self._temp_config["theme"][color_key]
        current_color = QColor(current_rgb[0], current_rgb[1], current_rgb[2])
        
        color = QColorDialog.getColor(current_color, self, f"{color_key}を選択")
        if color.isValid():
            rgb = [color.red(), color.green(), color.blue()]
            self._temp_config["theme"][color_key] = rgb
            self._update_color_button(button, color)
    
    def _update_color_button(self, button: QPushButton, color: QColor):
        """色ボタンの表示を更新"""
        button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
    
    def _load_settings(self):
        """設定を読み込んでUIに反映"""
        try:
            # フォント設定
            font_family = self.config.get("font.family", "")
            if font_family:
                index = self.font_combo.findText(font_family)
                if index >= 0:
                    self.font_combo.setCurrentIndex(index)
            
            self.title_size.setValue(self.config.get("font.title_size", 36))
            self.normal_size.setValue(self.config.get("font.normal_size", 20))
            self.small_size.setValue(self.config.get("font.small_size", 14))
            
            self.title_bold.setChecked(self.config.get("font.title_bold", True))
            self.normal_bold.setChecked(self.config.get("font.normal_bold", False))
            self.small_bold.setChecked(self.config.get("font.small_bold", False))
            
            # テーマ設定
            bg_rgb = self.config.get("theme.background_color", [10, 10, 30])
            bg_color = QColor(bg_rgb[0], bg_rgb[1], bg_rgb[2])
            self._update_color_button(self.bg_color_btn, bg_color)
            
            text_rgb = self.config.get("theme.text_color", [255, 255, 255])
            text_color = QColor(text_rgb[0], text_rgb[1], text_rgb[2])
            self._update_color_button(self.text_color_btn, text_color)
            
            accent_rgb = self.config.get("theme.accent_color", [0, 255, 204])
            accent_color = QColor(accent_rgb[0], accent_rgb[1], accent_rgb[2])
            self._update_color_button(self.accent_color_btn, accent_color)
            
            splash_bg_rgb = self.config.get("theme.splash_bg_color", [0, 0, 0])
            splash_bg_color = QColor(splash_bg_rgb[0], splash_bg_rgb[1], splash_bg_rgb[2])
            self._update_color_button(self.splash_bg_color_btn, splash_bg_color)
            
            # 表示設定
            if hasattr(self, 'fullscreen_check'):
                self.fullscreen_check.setChecked(self.config.get("display.fullscreen", False))
            
            # サーバー設定
            if hasattr(self, 'server_enabled'):
                self.server_enabled.setChecked(self.config.get("server.enabled", True))
                self.server_port.setValue(self.config.get("server.port", 8080))
                self.server_host.setText(self.config.get("server.host", "0.0.0.0"))
            
            # デバッグ設定
            if hasattr(self, 'debug_enabled'):
                self.debug_enabled.setChecked(self.config.get("debug.enabled", False))
                self.show_traceback.setChecked(self.config.get("debug.show_traceback", True))
                self.log_to_file.setChecked(self.config.get("debug.log_to_file", False))
                self.log_file.setText(self.config.get("debug.log_file", "pykara_debug.log"))
            
            # 一時設定も更新
            self._temp_config = self.config.get_all()
        except Exception as e:
            import traceback
            error_msg = f"設定の読み込みに失敗しました:\n{str(e)}"
            if self.config.get("debug.show_traceback", True):
                error_msg += f"\n\n詳細:\n{traceback.format_exc()}"
            print(error_msg)
            try:
                QMessageBox.critical(self, "エラー", error_msg)
            except:
                pass
            raise
    
    def _apply_settings(self):
        """設定を適用"""
        # フォント設定を一時設定に反映
        self._temp_config["font"]["family"] = self.font_combo.currentText()
        self._temp_config["font"]["title_size"] = self.title_size.value()
        self._temp_config["font"]["normal_size"] = self.normal_size.value()
        self._temp_config["font"]["small_size"] = self.small_size.value()
        self._temp_config["font"]["title_bold"] = self.title_bold.isChecked()
        self._temp_config["font"]["normal_bold"] = self.normal_bold.isChecked()
        self._temp_config["font"]["small_bold"] = self.small_bold.isChecked()
        
        # 表示設定を一時設定に反映
        if "display" not in self._temp_config:
            self._temp_config["display"] = {}
        self._temp_config["display"]["fullscreen"] = self.fullscreen_check.isChecked()
        
        # サーバー設定を一時設定に反映
        if "server" not in self._temp_config:
            self._temp_config["server"] = {}
        self._temp_config["server"]["enabled"] = self.server_enabled.isChecked()
        self._temp_config["server"]["port"] = self.server_port.value()
        self._temp_config["server"]["host"] = self.server_host.text()
        
        # デバッグ設定を一時設定に反映
        if "debug" not in self._temp_config:
            self._temp_config["debug"] = {}
        self._temp_config["debug"]["enabled"] = self.debug_enabled.isChecked()
        self._temp_config["debug"]["show_traceback"] = self.show_traceback.isChecked()
        self._temp_config["debug"]["log_to_file"] = self.log_to_file.isChecked()
        self._temp_config["debug"]["log_file"] = self.log_file.text()
        
        # 設定を保存
        self.config._config = self._temp_config.copy()
        self.config.save()
        
        # 変更通知
        self.settings_changed.emit()
        
        QMessageBox.information(self, "設定", "設定を適用しました。")
    
    def _ok_clicked(self):
        """OKボタンがクリックされた"""
        self._apply_settings()
        self.accept()
    
    def _reset_to_default(self):
        """デフォルト設定にリセット"""
        reply = QMessageBox.question(
            self, "確認", "デフォルト設定に戻しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_to_default()
            self._load_settings()
            QMessageBox.information(self, "設定", "デフォルト設定に戻しました。")
