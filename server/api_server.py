# server/api_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
from typing import Optional
import logging

class APIServer:
    """HTTP APIサーバー（Flask）"""
    
    def __init__(self, selection_manager, config):
        self.selection_manager = selection_manager
        self.config = config
        self.app = Flask(__name__)
        CORS(self.app)  # CORSを有効化（別UIからのアクセスを許可）
        self.server_thread: Optional[Thread] = None
        self._setup_routes()
        
        # Flaskのログを抑制
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    def _setup_routes(self):
        """ルートを設定"""
        
        @self.app.route('/api/status', methods=['GET'])
        def status():
            """サーバー状態を取得"""
            return jsonify({
                "status": "running",
                "has_selection": self.selection_manager.has_selection()
            })
        
        @self.app.route('/api/select', methods=['POST'])
        def select_song():
            """選曲を設定"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "JSONデータが必要です"}), 400
                
                title = data.get('title', '')
                if not title:
                    return jsonify({"error": "titleは必須です"}), 400
                
                artist = data.get('artist', '')
                metadata = data.get('metadata', {})
                
                self.selection_manager.set_selection(title, artist, metadata)
                
                return jsonify({
                    "success": True,
                    "message": f"選曲しました: {title}",
                    "selection": self.selection_manager.get_selection()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/selection', methods=['GET'])
        def get_selection():
            """現在の選曲を取得"""
            selection = self.selection_manager.get_selection()
            if selection:
                return jsonify({"success": True, "selection": selection})
            else:
                return jsonify({"success": True, "selection": None})
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_selection():
            """選曲をクリア"""
            self.selection_manager.clear_selection()
            return jsonify({"success": True, "message": "選曲をクリアしました"})
        
        @self.app.route('/api/songs', methods=['GET'])
        def list_songs():
            """楽曲リストを取得（モック）"""
            # 実際の実装では、データベースから楽曲リストを取得
            return jsonify({
                "success": True,
                "songs": [
                    {"id": 1, "title": "サンプル曲1", "artist": "アーティスト1"},
                    {"id": 2, "title": "サンプル曲2", "artist": "アーティスト2"},
                ]
            })
    
    def start(self):
        """サーバーを起動（別スレッドで）"""
        if self.server_thread and self.server_thread.is_alive():
            return  # 既に起動中
        
        port = self.config.get("server.port", 8080)
        host = self.config.get("server.host", "0.0.0.0")
        
        def run_server():
            self.app.run(host=host, port=port, debug=False, use_reloader=False)
        
        self.server_thread = Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"APIサーバーを起動しました: http://{host}:{port}")
    
    def stop(self):
        """サーバーを停止"""
        # Flaskの開発サーバーは停止が難しいため、daemonスレッドとして実行
        # アプリケーション終了時に自動的に停止されます
        pass
    
    def get_url(self) -> str:
        """サーバーのURLを取得"""
        port = self.config.get("server.port", 8080)
        host = self.config.get("server.host", "0.0.0.0")
        if host == "0.0.0.0":
            host = "localhost"
        return f"http://{host}:{port}"
