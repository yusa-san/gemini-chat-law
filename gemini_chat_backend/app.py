# 必要なライブラリをインポート
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import traceback
import uuid # UUID生成用

# バックエンドではセッション管理を行わないことにした

# 環境変数からAPIキーとプロジェクトIDを取得（安全な方法）
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") # 例: "your-project-id"
API_KEY = os.environ.get("VERTEX_AI_API_KEY") # 例: "your-api-key"
LOCATION = "asia-northeast1" # リージョンを指定

# Vertex AIを初期化
vertexai.init(project=PROJECT_ID, location=LOCATION, api_key=API_KEY)

# Geminiモデルを準備
model = GenerativeModel("gemini-1.5-pro-002") #モデルは状況によって、適切なものに変更ください

# チャット履歴を保存するためのリストは非推奨

# Flaskを使ってWebアプリケーションを作成
app = Flask(__name__)

# CORSの設定 # 特定のURLからのアクセスのみ許可
CORS(app, supports_credentials=True,
    resources={r"/*": {"origins":"http://localhost:5173"}})

# jsonifyの日本語文字化け防止
app.json.ensure_ascii = False

# グローバル変数でチャット履歴を保持（デバッグ用）
chat = None

# チャットの処理をする関数
@app.route("/<path:path>", methods=["POST"])
def catch_all(path):
    sys.stderr.write(f"[DEBUG] Received request at: {path}")
    sys.stderr.write(f"[DEBUG] Headers: {request.headers}")
    sys.stderr.write(f"[DEBUG] Received Data: {request.data}")

    global chat

    # ユーザーからの質問を受け取る
    if not request.data:
        return jsonify({"error": "Empty request body"}), 400  # 空のデータをチェック
    
    try:
        data = request.get_json()
        sys.stderr.write(f"[DEBUG] Received Data: {data}")
        sys.stderr.write(f"[DEBUG] Type of Recieved Data: {type(data)}")

        # dataがdictか確かめる
        if isinstance(data, dict):
            sys.stderr.write("[DEBUG] Received Data is a dictionary")
        else:
            sys.stderr.write("[ERROR] Received Data is NOT a dictionary!")

        # data が dict ではなかった場合、エラーメッセージを返す
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON format"}), 400

        try:
            user_question = data.get('question', '')
        except Exception as e:
            errmsg = traceback.format_exc()
            sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
            return jsonify({"error": str(e)}), 500

        if chat is None:
            chat = model.start_chat()
        response = chat.send_message(Part.from_text(user_question))
        gemini_answer = response.text

        sys.stderr.write(f"[DEBUG] Chat History: {chat.history}")

        # ユーザーに回答を返す
        return jsonify({'answer': gemini_answer})

    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
        return jsonify({"error": str(e)}), 500

# チャット履歴を取得する関数
@app.route('/history', methods=['GET'])
def get_history():

    global chat
    sys.stderr.write(f"[DEBUG] Chat History: {chat.history}")

    history = []
    try:
        if chat:
            for turn in chat.history:
                history.append({
                    "role": turn.role,
                    "parts": [part.text for part in turn.parts]
                })
        return jsonify({'history': history})

    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
        return jsonify({"error": str(e)}), 500

# ホームページを表示する関数
@app.route("/")
def home():
    return "Hello World!"

# アプリケーションを実行
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
