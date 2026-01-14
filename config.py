# config.py
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """設定管理クラス"""
    
    DEFAULT_CONFIG = {
        "font": {
            "family": "",  # 空文字列はシステムデフォルト
            "title_size": 36,
            "normal_size": 20,
            "small_size": 14,
            "title_bold": True,
            "normal_bold": False,
            "small_bold": False
        },
        "theme": {
            "background_color": [10, 10, 30],  # RGB
            "text_color": [255, 255, 255],     # RGB
            "accent_color": [0, 255, 204],     # RGB (点滅時の色)
            "splash_bg_color": [0, 0, 0]       # RGB
        },
        "server": {
            "port": 8080,
            "host": "0.0.0.0",  # すべてのインターフェースでリッスン
            "enabled": True
        },
        "debug": {
            "enabled": True,       # デバッグモードを有効化（デフォルトでON）
            "show_traceback": True, # トレースバックを表示
            "log_to_file": False,   # ログをファイルに出力
            "log_file": "pykara_debug.log"
        },
        "display": {
            "fullscreen": False,   # フルスクリーン表示（False=ウィンドウ表示）
            "width": 1920,         # デフォルトウィンドウ幅
            "height": 1080         # デフォルトウィンドウ高さ
        },
        "attract_video": {
            "mode": "local",        # "local" or "youtube"
            "local_dir": "videos",  # ローカル再生用ディレクトリ
            "youtube_channel": "",  # YouTubeチャンネル名
            "volume": 80            # 音量 0～100
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # デフォルト設定とマージ（不足しているキーを補完）
                    merged = self._merge_dict(self.DEFAULT_CONFIG.copy(), config)
                    return merged
            except Exception as e:
                print(f"設定ファイルの読み込みエラー: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 設定ファイルが存在しない場合はデフォルト設定を保存
            self._save_config(self.DEFAULT_CONFIG.copy())
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_dict(self, default: Dict, user: Dict) -> Dict:
        """デフォルト設定とユーザー設定をマージ"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """設定ファイルに保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")
    
    def get(self, key: str, default=None):
        """設定値を取得（ドット記法対応: "font.title_size"）"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """設定値を設定（ドット記法対応: "font.title_size"）"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self):
        """現在の設定をファイルに保存"""
        self._save_config(self._config)
    
    def reset_to_default(self):
        """デフォルト設定にリセット"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """全設定を取得"""
        return self._config.copy()
    
    # -------------------------------
    # ウィンドウサイズ取得用のユーティリティ
    # -------------------------------
    def get_window_width(self) -> int:
        return self.get("display.width", 1920)
    
    def get_window_height(self) -> int:
        return self.get("display.height", 1080)
    
    # -------------------------------
    # アトラクト画面音量取得
    # -------------------------------
    def get_attract_volume(self) -> float:
        """0.0～1.0 の範囲で返す"""
        volume_percent = self.get("attract_video.volume", 80)
        return max(0, min(volume_percent, 100)) / 100.0