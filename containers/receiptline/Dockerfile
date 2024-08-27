# ベースイメージを指定
FROM node:18

# 作業ディレクトリを作成
WORKDIR /app

# パッケージファイルをコピー
COPY package.json /app/

# 依存関係をインストール
RUN npm install

# エントリーポイントスクリプトとreceipt_server.jsをコピーし、実行権限を付与
COPY ./containers/receiptline/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./containers/receiptline/receipt_server.js /app/receipt_server.js
RUN chmod +x /usr/local/bin/entrypoint.sh

# アプリケーションコードをコピー
COPY . /app/

# エントリーポイントスクリプトを実行
ENTRYPOINT ["entrypoint.sh"]
