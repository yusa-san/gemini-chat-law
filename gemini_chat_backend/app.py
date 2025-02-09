# 必要なライブラリをインポート
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import traceback
import uuid # UUID生成用

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

# CORSの設定
# CORS(app) # すべてのURLからのアクセスを許可
CORS(app, supports_credentials=True) # supports_credentials=Trueを指定してクッキーを許可

# Flaskのセッション管理用シークレットキー
app.secret_key = os.environ.get("FLASK_SECRET_KEY") # 例: "your-secret-key"

# jsonifyの日本語文字化け防止
app.json.ensure_ascii = False

def serialize_history(history):
    """会話履歴 (Content オブジェクトのリスト) をシリアライズ可能な形式に変換"""
    serialized_history = []
    try:
        for turn in history:
            serialized_history.append({
                "role": turn.role,
                "parts": [{"text": part.text} for part in turn.parts]  # Part オブジェクトは text のみ
            })
    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
    return serialized_history

def deserialize_history(serialized_history):
    """シリアライズされた会話履歴から Content オブジェクトのリストを復元"""
    history = []
    try:
        for turn in serialized_history:
            history.append(Content(
                role=turn["role"],
                parts=[Part.from_text(part["text"]) for part in turn["parts"]]
            ))
    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
    return history

# チャットの処理をする関数
@app.route("/<path:path>", methods=["POST"])
def catch_all(path):
    sys.stderr.write(f"[DEBUG] Received request at: {path}")
    sys.stderr.write(f"[DEBUG] Headers: {request.headers}")
    sys.stderr.write(f"[DEBUG] Data: {request.data}")

    # セッションIDを取得（なければ新規作成）
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

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

        # セッションからchatオブジェクトを取得（なければ新規取得）
        serialized_history = session.get('history', [])
        history = deserialize_history(serialized_history)

        # 会話履歴を使って新しい chat オブジェクトを作成
        chat = model.start_chat(history=history)

        # Gemini APIを使って回答を生成
        response = chat.send_message(Part.from_text(user_question))
        gemini_answer = response.text

        # 新しい会話履歴をセッションに保存 (シリアライズ)
        session['history'] = serialize_history(chat.history)

        # ユーザーに回答を返す
        return jsonify({'answer': gemini_answer})

    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
        return jsonify({"error": str(e)}), 500

# チャット履歴を取得する関数
@app.route('/history', methods=['GET'])
def get_history():
    # セッションから会話履歴を取得 (なければ空のリスト)
    serialized_history = session.get('history', [])
    history = deserialize_history(serialized_history)

    #表示用に整形
    formatted_history = []
    try:
        for turn in history:
            formatted_history.append({
                "role": turn.role,
                "parts": [part.text for part in turn.parts]
                })
        return jsonify({'history': formatted_history})

    except Exception as e:
        errmsg = traceback.format_exc()
        sys.stderr.write(f"[ERROR] Exception: {errmsg}")  # スタックトレースを表示
        return jsonify({"error": str(e)}), 500

# ホームページを表示する関数
@app.route("/")
def home():
    return "Hello, Cloud Run!"

# アプリケーションを実行
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
