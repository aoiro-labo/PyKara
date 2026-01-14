# ui/attract.py
import os
import random
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QKeyEvent

from theme.fonts import FontSet
from theme.theme import ThemeManager
from config import Config
from server.selection_manager import SelectionManager

# 動画再生用
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

# YouTube再生用
from PyQt6.QtWebEngineWidgets import QWebEngineView


class PyKaraAttract(QMainWindow):
    def __init__(self, config: Config, selection_manager: SelectionManager):
        super().__init__()
        self.config = config
        self.selection_manager = selection_manager
        self.theme_manager = ThemeManager(config)

        self.setWindowTitle("PyKara - Attract Mode")

        # --------------------------
        # 背景動画設定
        # --------------------------
        self.attract_mode = config.get("attract_video.mode", "local")
        self.video_widget = None
        self.web_view = None

        if self.attract_mode == "local":
            self._setup_local_video()
        elif self.attract_mode == "youtube":
            self._setup_youtube_video()

        # --------------------------
        # UIオーバーレイ
        # --------------------------
        self._setup_ui_overlay()

        # --------------------------
        # 選曲監視
        # --------------------------
        self.selection_timer = QTimer(self)
        self.selection_timer.timeout.connect(self._check_selection)
        self.selection_timer.start(500)

        # --------------------------
        # 点滅タイマー
        # --------------------------
        self._flash_state = False
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._toggle_flash)
        self.flash_timer.start(800)

    # ==========================
    # ローカル動画再生（通常 + shop動画）
    # ==========================
    def _setup_local_video(self):
        local_dir = self.config.get("attract_video.local_dir", "videos")
        shop_dir = os.path.join(local_dir, "shop")

        # 通常動画
        self.main_videos = [
            os.path.join(local_dir, f)
            for f in os.listdir(local_dir)
            if f.lower().endswith((".mp4", ".mov", ".mkv", ".avi"))
            and os.path.isfile(os.path.join(local_dir, f))
        ]
        # shop動画
        self.shop_videos = [
            os.path.join(shop_dir, f)
            for f in os.listdir(shop_dir)
            if f.lower().endswith((".mp4", ".mov", ".mkv", ".avi"))
            and os.path.isfile(os.path.join(shop_dir, f))
        ]

        # ランダムシャッフル
        random.shuffle(self.main_videos)
        self.main_loop = self.main_videos.copy()
        self.video_queue = self.shop_videos.copy()  # 最初にshop動画を再生
        self.main_cycle_count = 0

        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(self.config.get("attract_video.volume", 0.5))
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.video_widget = QVideoWidget(self)
        self.setCentralWidget(self.video_widget)
        self.player.setVideoOutput(self.video_widget)

        # 最初の動画再生
        if self.video_queue or self.main_loop:
            self._play_next_video()

        self.player.mediaStatusChanged.connect(self._handle_media_status)

    def _play_next_video(self):
        next_video = None

        # shop動画を優先
        if self.video_queue:
            next_video = self.video_queue.pop(0)
        else:
            # 通常動画を消費
            if self.main_loop:
                next_video = self.main_loop.pop(0)
            else:
                # 通常動画1周終了
                self.main_cycle_count += 1
                # shop動画を挟む
                self.video_queue = self.shop_videos.copy()
                random.shuffle(self.main_videos)
                self.main_loop = self.main_videos.copy()
                if self.video_queue:
                    next_video = self.video_queue.pop(0)

        if next_video:
            self.player.setSource(QUrl.fromLocalFile(next_video))
            self.player.play()

    def _handle_media_status(self, status):
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._play_next_video()

    # ==========================
    # YouTube動画再生
    # ==========================
    def _setup_youtube_video(self):
        channel_name = self.config.get("attract_video.youtube_channel", "")
        if not channel_name:
            return

        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)

        embed_url = f"https://www.youtube.com/embed?listType=user_uploads&list={channel_name}&autoplay=1&loop=1&mute=1"
        self.web_view.load(QUrl(embed_url))

    # ==========================
    # UIオーバーレイ（メッセージ表示など）
    # ==========================
    def _setup_ui_overlay(self):
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        overlay.setStyleSheet("background: transparent;")
        overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay_layout = QVBoxLayout(overlay)
        self.overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 選曲待ちメッセージ
        self.msg = QLabel("Sing Your Soul.\n\n[ 選曲をお待ちしています ]", self)
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_font()
        self._update_text_color()
        self.overlay_layout.addWidget(self.msg)

        # 選曲情報ラベル
        self.selection_label = QLabel("", self)
        self.selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selection_label.setFont(FontSet.normal())
        self._update_text_color_label(self.selection_label)
        self.overlay_layout.addWidget(self.selection_label)

    # ==========================
    # テーマ・フォント更新
    # ==========================
    def _update_font(self):
        self.msg.setFont(FontSet.title())

    def _update_text_color(self):
        rgb = self.theme_manager.get_text_color_rgb()
        self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")

    def _update_text_color_label(self, label):
        rgb = self.theme_manager.get_text_color_rgb()
        label.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")

    # ==========================
    # 選曲監視
    # ==========================
    def _check_selection(self):
        selection = self.selection_manager.get_selection()
        if selection:
            title = selection.get("title", "")
            artist = selection.get("artist", "")
            if artist:
                self.selection_label.setText(f"♪ {title}\n{artist}")
            else:
                self.selection_label.setText(f"♪ {title}")
            self.selection_label.show()
            self.flash_timer.stop()
            rgb = self.theme_manager.get_accent_color_rgb()
            self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
            self.msg.setText("選曲が完了しました！\n\n準備中...")
        else:
            self.selection_label.setText("")
            self.selection_label.hide()
            if not self.flash_timer.isActive():
                self.flash_timer.start(800)
            self.msg.setText("Sing Your Soul.\n\n[ 選曲をお待ちしています ]")

    # ==========================
    # 点滅
    # ==========================
    def _toggle_flash(self):
        if self._flash_state:
            rgb = self.theme_manager.get_text_color_rgb()
        else:
            rgb = self.theme_manager.get_accent_color_rgb()
        self.msg.setStyleSheet(f"color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]});")
        self._flash_state = not self._flash_state

    # ==========================
    # 設定変更対応
    # ==========================
    def refresh_settings(self):
        self._update_font()
        self._update_text_color()
        if hasattr(self, "audio_output"):
            self.audio_output.setVolume(self.config.get("attract_video.volume", 0.5))

    # ==========================
    # キー操作
    # ==========================
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_F1:
            try:
                from ui.settings import SettingsDialog
                was_fullscreen = self.isFullScreen()
                if was_fullscreen:
                    self.showNormal()
                dialog = SettingsDialog(self.config, self)
                dialog.settings_changed.connect(self.refresh_settings)
                dialog.exec()
                if was_fullscreen and self.config.get("display.fullscreen", False):
                    self.showFullScreen()
            except Exception as e:
                print(f"設定画面表示エラー: {e}")
        else:
            super().keyPressEvent(event)
