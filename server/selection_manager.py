# server/selection_manager.py
from typing import Optional, Dict, Any
from datetime import datetime
from threading import Lock

class SelectionManager:
    """選曲管理クラス（スレッドセーフ）"""
    
    def __init__(self):
        self._lock = Lock()
        self._current_selection: Optional[Dict[str, Any]] = None
    
    def set_selection(self, title: str, artist: str = "", metadata: Dict[str, Any] = None):
        """選曲を設定"""
        with self._lock:
            self._current_selection = {
                "title": title,
                "artist": artist,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_selection(self) -> Optional[Dict[str, Any]]:
        """現在の選曲を取得"""
        with self._lock:
            return self._current_selection.copy() if self._current_selection else None
    
    def clear_selection(self):
        """選曲をクリア"""
        with self._lock:
            self._current_selection = None
    
    def has_selection(self) -> bool:
        """選曲があるかどうか"""
        with self._lock:
            return self._current_selection is not None
