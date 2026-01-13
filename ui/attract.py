# ui/attract.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QKeyEvent

from theme.fonts import FontSet
from theme.theme import ThemeManager
from config import Config


class PyKaraAttract(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.theme_manager = ThemeManager(config)

        self.setWindowTitle("PyKara - Attract Mode")
        self.showFullScreen()

        # テーマを適用
        self._apply_theme()

        # 中央ウィジェット
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # メインメッセージ
        self.msg = QLabel(
            "Sing Your Soul.\n\n"
            "[ 選曲をお待ちしています ]"
        )
        self._update_font()
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_text_color()

        layout.addWidget(self.msg)

        # 点滅用タイマー
        self._flash_state = False
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_timer.start(800)
    
    def _apply_theme(self):
        """テーマを適用"""
        palette = self.palette()
        palette = self.theme_manager.apply_to_palette(palette)
        self.setPalette(palette)
    
    def _update_font(self):
        """フォントを更新"""
        self.msg.setFont(FontSet.title())
    
    def _update_text_color(self):
        """テキスト色を更新"""
        rgb = self.theme_manager.get_text_color_rgb()
        self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
    
    def _toggle_flash(self):
        """点滅を切り替え"""
        if self._flash_state:
            rgb = self.theme_manager.get_text_color_rgb()
            self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        else:
            rgb = self.theme_manager.get_accent_color_rgb()
            self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        self._flash_state = not self._flash_state
    
    def refresh_settings(self):
        """設定変更後にUIを更新"""
        self._apply_theme()
        self._update_font()
        self._update_text_color()
    
    def keyPressEvent(self, event: QKeyEvent):
        """キー入力処理（F1キーで設定を開く）"""
        if event.key() == Qt.Key.Key_F1:
            from ui.settings import SettingsDialog
            dialog = SettingsDialog(self.config, self)
            dialog.settings_changed.connect(self.refresh_settings)
            dialog.exec()
        else:
            super().keyPressEvent(event)