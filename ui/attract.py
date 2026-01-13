# ui/attract.py

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QKeyEvent

from theme.fonts import FontSet
from theme.theme import ThemeManager
from config import Config
from server.selection_manager import SelectionManager


class PyKaraAttract(QMainWindow):
    def __init__(self, config: Config, selection_manager: SelectionManager):
        super().__init__()
        self.config = config
        self.theme_manager = ThemeManager(config)
        self.selection_manager = selection_manager

        self.setWindowTitle("PyKara - Attract Mode")
        
        try:
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

            # 選曲情報表示用ラベル
            self.selection_label = QLabel("")
            self.selection_label.setFont(FontSet.normal())
            self.selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._update_text_color_label(self.selection_label)
            layout.addWidget(self.selection_label)

            layout.addWidget(self.msg)

            # 選曲監視用タイマー
            self.selection_timer = QTimer(self)
            self.selection_timer.timeout.connect(self._check_selection)
            self.selection_timer.start(500)  # 0.5秒ごとにチェック

            # 点滅用タイマー
            self._flash_state = False
            self.flash_timer = QTimer(self)
            self.flash_timer.timeout.connect(self._toggle_flash)
            self.flash_timer.start(800)
        except Exception as e:
            import traceback
            print(f"アトラクト画面の初期化エラー: {e}")
            traceback.print_exc()
            raise
    
    def _apply_theme(self):
        """テーマを適用"""
        try:
            palette = self.palette()
            palette = self.theme_manager.apply_to_palette(palette)
            self.setPalette(palette)
        except Exception as e:
            import traceback
            print(f"テーマ適用エラー: {e}")
            traceback.print_exc()
            raise
    
    def _update_font(self):
        """フォントを更新"""
        try:
            self.msg.setFont(FontSet.title())
        except Exception as e:
            import traceback
            print(f"フォント更新エラー: {e}")
            traceback.print_exc()
            raise
    
    def _update_text_color(self):
        """テキスト色を更新"""
        try:
            rgb = self.theme_manager.get_text_color_rgb()
            self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        except Exception as e:
            import traceback
            print(f"テキスト色更新エラー: {e}")
            traceback.print_exc()
            raise
    
    def _update_text_color_label(self, label: QLabel):
        """ラベルのテキスト色を更新"""
        try:
            rgb = self.theme_manager.get_text_color_rgb()
            label.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        except Exception as e:
            import traceback
            print(f"ラベル色更新エラー: {e}")
            traceback.print_exc()
            raise
    
    def _check_selection(self):
        """選曲状態をチェックして表示を更新"""
        selection = self.selection_manager.get_selection()
        if selection:
            title = selection.get('title', '')
            artist = selection.get('artist', '')
            if artist:
                self.selection_label.setText(f"♪ {title}\n{artist}")
            else:
                self.selection_label.setText(f"♪ {title}")
            self.selection_label.show()
            # 選曲があるときは点滅を停止
            self.flash_timer.stop()
            rgb = self.theme_manager.get_accent_color_rgb()
            self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
            self.msg.setText("選曲が完了しました！\n\n準備中...")
        else:
            self.selection_label.setText("")
            self.selection_label.hide()
            # 選曲がないときは点滅を再開
            if not self.flash_timer.isActive():
                self.flash_timer.start(800)
            self.msg.setText(
                "Sing Your Soul.\n\n"
                "[ 選曲をお待ちしています ]"
            )
    
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
            try:
                import traceback
                from ui.settings import SettingsDialog
                
                # フルスクリーンの場合は一時的にウィンドウモードに
                was_fullscreen = self.isFullScreen()
                if was_fullscreen:
                    self.showNormal()
                
                dialog = SettingsDialog(self.config, self)
                dialog.settings_changed.connect(self.refresh_settings)
                dialog.exec()
                
                # 設定に応じてフルスクリーンに戻す
                if was_fullscreen and self.config.get("display.fullscreen", False):
                    self.showFullScreen()
            except Exception as e:
                import traceback
                error_msg = f"設定画面の表示に失敗しました:\n{str(e)}"
                if self.config.get("debug.show_traceback", True):
                    error_msg += f"\n\n詳細:\n{traceback.format_exc()}"
                print(error_msg)
                
                # エラーダイアログを表示
                try:
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Icon.Critical)
                    msg_box.setWindowTitle("エラー")
                    msg_box.setText(error_msg)
                    msg_box.exec()
                except:
                    # ダイアログ表示も失敗した場合はコンソールに出力のみ
                    pass
        else:
            super().keyPressEvent(event)