# Pythonの公式イメージを使用
FROM python:3.9-slim-buster

# 作業ディレクトリを設定
WORKDIR /app

# 必要なライブラリをインストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# 環境変数を設定（APIキーとプロジェクトIDはCloud Runの設定で後から追加）
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
ENV VERTEX_AI_API_KEY=${VERTEX_AI_API_KEY}

# ポート8080でアプリケーションを実行
# CMD ["python", "app.py"]

# ポート8080でアプリケーションを実行 (Gunicornを使用)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "--log-file=-", "app:app"]