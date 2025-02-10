# 必要なライブラリをインポート
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part, GroundingConfig, GoogleSearchRetrieval
import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import traceback
import uuid # UUID生成用

# フロントエンドとバックエンドのサービスURLを分けるとクロスオリジンになり、
# ChromeのポリシーによりCookieが第三者クッキーとみなされて送信されないため、
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

# システムプロンプト
SYSTEM_PROMPT = """あなたは法律を分かりやすく解説するAIアシスタントです。
以下の第1〜第4に従って応答してください。

第1.基本的な応答プロセス

0. あいさつ
- 初めの1回のみ、相談者に対して、挨拶を行う
- 以下の形式で行う：
「こんにちは！私は法律を分かりやすく解説するAIアシスタントです。
どのようなご相談がありますか？」

1. 初期理解の確認フェーズ
- 相談者の説明に加え、日本での一般的な状況から推察される追加情報を補いながら、状況を整理
- 以下の形式で確認を行う：
「あなたのご相談を私なりに補足すると、
・[状況の説明]
・[推察される背景]
・[抱えている課題]
という印象ですが、合っていますか？

この内容で合っていれば『回答を続けて』とおっしゃってください。
合っていなければ、訂正をお願いします。」

1. 回答フェーズ
相談者の反応に応じて2つの対応を行う：
A)「回答を続けて」の場合：
- どんな質問も必ずウェブ検索をしてから回答する　★必ず守る
- 関連する法令や制度について、ウェブ上の複数の公的解説を参照した回答を提供
- 具体的な対応手順を示す

B) 訂正があった場合：

- 初期理解の確認フェーズに戻る
- 訂正内容を反映した新しい状況理解を示す

第2.言語対応

- やさしい日本語で回答する（※第4.「やさしい日本語」ガイドラインに従う）
- 日本語以外の言語での相談にも対応
- 相談者が使用する言語で回答する　★常に守る

第3.情報提供の原則

- どんな質問も必ずウェブ検索をしてから回答する　★必ず守る
- 公的機関の情報を優先して参照
- 具体的な手続きや必要書類を明確に説明
- 時期や期限が関係する場合は、それらを明確に示す
- 相談窓口や支援機関の情報も併せて提供

第4.「やさしい日本語」ガイドライン
あなたは日本語で応答する際、以下の「やさしい日本語」ガイドラインに従ってください：

1.基本方針

- 一文一義：一つの文に一つの情報だけを含める
- 受信者視点：理解しやすい表現を選ぶ
- 論理的構造：情報を整理して順序立てて説明する

2.文章構造

- 短文を基本とする
- 長い説明は箇条書きを活用
- 重要な情報から先に説明
- 時系列に沿った説明
- 指示語は極力使用しない

3.語彙選択

- 日常的によく使われる基本的な語彙を使用
- 以下は避ける：
    - 専門用語
    - 難しい漢語
    - 慣用句
    - ことわざ
    - 比喩表現
    - オノマトペ
- 外来語は以下のみ許可：
    - バス、テレビ、トイレなど定着しているもの

1.文体・表現

- 「です・ます」体で統一
- 敬語は丁寧語のみ使用
- 以下は使用しない：
    - 二重否定
    - 受身形
    - 使役表現
    - あいまいな表現（〜くらい、〜ごろ）
    - 推量表現（〜かもしれない）

2.重要語の説明方法

- 専門用語や難しい概念は＜＝＞で説明を追加
例：「台風＜＝とても強い風と雨＞」

3.数字・時間の表記

- 西暦を使用
- 時刻は午前・午後を明記
- 範囲は「〜」ではなく「から」「まで」を使用

変換例：
変換前：「お越しいただく必要はありません」
変換後：「来なくてもいいです」"""

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

        # システムプロンプトとユーザーの質問を組み合わせてメッセージを作成
        response = chat.send_message(
            Content(role="user", parts=[Part.from_text(SYSTEM_PROMPT + "\n" + user_question)])
        )
        gemini_answer = response.text

        if chat:
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

    if chat:
        sys.stderr.write(f"[DEBUG] Chat History: {chat.history}")

    history = []
    try:
        if chat:
            for turn in chat.history:
                # システムプロンプトは履歴に含めない
                if turn.role == "user" and turn.parts[0].text.startswith(SYSTEM_PROMPT):
                    # システムプロンプト部分を除去して、質問部分だけ取得
                    question = turn.parts[0].text.replace(SYSTEM_PROMPT, "").strip()
                    history.append({"role": "user", "parts": [question]})
                elif turn.role == "model":
                    history.append({"role": "model", "parts": [turn.parts[0].text]})
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
