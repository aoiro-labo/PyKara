# main.py
import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap, QColor, QMouseEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from ui.attract import PyKaraAttract
from config import Config
from theme.fonts import FontSet
from theme.theme import ThemeManager
from server.selection_manager import SelectionManager
from server.api_server import APIServer
from utils.logger import DebugLogger


class NonClickableSplashScreen(QSplashScreen):
    """クリックで閉じないスプラッシュスクリーン"""
    def mousePressEvent(self, event: QMouseEvent):
        event.ignore()
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        event.ignore()


def main():
    global app
    config = Config()
    logger = DebugLogger(config)
    logger.info("PyKaraを起動しています...")

    app = QApplication(sys.argv)

    width, height = 1920, 1080  # デフォルト16:9
    main_window = QMainWindow()
    main_window.setWindowTitle("PyKara - 16:9 Fixed Window")
    main_window.setFixedSize(width, height)
    main_window.show()

    selection_manager = SelectionManager()



    # ----------------------------
    # 動画再生ユーティリティ
    # ----------------------------
    def play_video(parent, file_path, on_finished):
        """動画を再生して終了時に on_finished を呼ぶ"""
        if not os.path.exists(file_path):
            on_finished()
            return

        video_widget = QVideoWidget(parent)
        video_widget.setGeometry(0, 0, parent.width(), parent.height())
        video_widget.show()

        audio_output = QAudioOutput()
        audio_output.setVolume(config.get_attract_volume())
        player = QMediaPlayer()
        player.setAudioOutput(audio_output)
        player.setVideoOutput(video_widget)
        player.setSource(QUrl.fromLocalFile(file_path))

        player.play()

        def handle_status(status):
            from PyQt6.QtMultimedia import QMediaPlayer
            if status == QMediaPlayer.MediaStatus.EndOfMedia:
                player.stop()
                video_widget.hide()
                video_widget.deleteLater()
                on_finished()

        player.mediaStatusChanged.connect(handle_status)

    # ----------------------------
    # アトラクト画面表示
    # ----------------------------
    def show_attract():
        try:
            attract = PyKaraAttract(config, selection_manager)
            attract.setParent(main_window)
            attract.setGeometry(0, 0, width, height)
            attract.show()
            attract.raise_()
            attract.activateWindow()
            splash.finish(attract)

            # 終了時ED動画再生設定
            def play_ed_and_quit():
                ed_path_mp4 = os.path.join(config.get("attract_video.local_dir", "videos"), "shop", "ed.mp4")
                ed_path_mkv = os.path.join(config.get("attract_video.local_dir", "videos"), "shop", "ed.mkv")
                ed_file = ed_path_mp4 if os.path.exists(ed_path_mp4) else ed_path_mkv
                if os.path.exists(ed_file):
                    play_video(main_window, ed_file, lambda: app.quit())
                else:
                    app.quit()

            main_window.closeEvent = lambda event: (event.ignore(), play_ed_and_quit())

        except Exception as e:
            splash.close()
            QMessageBox.critical(None, "エラー",
                                 f"アトラクト画面表示失敗:\n{str(e)}\n\n詳細:\n{traceback.format_exc()}")
            sys.exit(1)

    # ----------------------------
    # 起動時OP動画再生 → アトラクト表示
    # ----------------------------
    op_path_mp4 = os.path.join(config.get("attract_video.local_dir", "videos"), "shop", "op.mp4")
    op_path_mkv = os.path.join(config.get("attract_video.local_dir", "videos"), "shop", "op.mkv")
    op_file = op_path_mp4 if os.path.exists(op_path_mp4) else op_path_mkv

    if os.path.exists(op_file):
        play_video(main_window, op_file, show_attract)
    else:
        # OP動画がない場合は3秒後にアトラクト表示
        QTimer.singleShot(3000, show_attract)

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"致命的なエラー: {e}")
        traceback.print_exc()
        sys.exit(1)
