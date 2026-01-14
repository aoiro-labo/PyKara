# main.py
import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from ui.attract import PyKaraAttract
from config import Config
from server.selection_manager import SelectionManager
from utils.logger import DebugLogger


def main():
    global app
    config = Config()
    logger = DebugLogger(config)
    logger.info("PyKaraを起動しています...")

    app = QApplication(sys.argv)

    width, height = 1920, 1080
    main_window = QMainWindow()
    main_window.setWindowTitle("PyKara - 16:9 Fixed Window")
    main_window.setFixedSize(width, height)
    main_window.show()

    selection_manager = SelectionManager()

    # ----------------------------
    # 動画再生ユーティリティ（黒画面1秒挿入対応）
    # ----------------------------
    def play_video(parent, file_path, on_finished, pre_black=True, post_black=True):
        """動画を再生して終了時に on_finished を呼ぶ"""
        if not os.path.exists(file_path):
            on_finished()
            return

        def show_black(duration_ms, callback):
            black = QWidget(parent)
            black.setStyleSheet("background-color: black;")
            black.setGeometry(0, 0, parent.width(), parent.height())
            black.show()
            QTimer.singleShot(duration_ms, lambda: (black.hide(), black.deleteLater(), callback()))

        def start_video():
            video_widget = QVideoWidget(parent)
            video_widget.setGeometry(0, 0, parent.width(), parent.height())
            video_widget.show()

            player = QMediaPlayer(parent)
            audio_output = QAudioOutput(parent)
            volume = config.get_attract_volume()
            if isinstance(volume, str):
                try:
                    volume = float(volume) / 100.0
                except:
                    volume = 0.5
            audio_output.setVolume(volume)
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
                    if post_black:
                        show_black(1000, on_finished)
                    else:
                        on_finished()

            player.mediaStatusChanged.connect(handle_status)

        if pre_black:
            show_black(1000, start_video)
        else:
            start_video()

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
        # OP動画がない場合は黒画面1秒 → アトラクト表示
        QTimer.singleShot(1000, show_attract)

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
