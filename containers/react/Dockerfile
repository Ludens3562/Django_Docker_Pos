# ベースイメージとしてNode.jsを使用
FROM node:18-alpine

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# アプリケーションのソースコードをコピー
COPY ./reactproj .

RUN npm install

COPY ./containers/react/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh