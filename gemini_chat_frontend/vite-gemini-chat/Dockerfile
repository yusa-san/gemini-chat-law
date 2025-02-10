# --- Build Stage ---
    FROM node:18-alpine as build
    WORKDIR /app
    
    # package.json と package-lock.json をコピーして依存関係をインストール
    COPY package*.json ./
    RUN npm install
    
    # ソースコードをコピーしてビルド（Vite の場合、ビルド成果物は通常 "dist" ディレクトリに出力されます）
    COPY . .
    RUN npm run build
    
    # --- Production Stage ---
    FROM nginx:stable-alpine
    # ビルド成果物を nginx の公開ディレクトリにコピー
    COPY --from=build /app/dist /usr/share/nginx/html
    
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]    