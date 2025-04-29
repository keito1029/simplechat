#!/bin/bash

# 1. 一時作業ディレクトリの作成
mkdir -p /tmp/testdir
cd /tmp/testdir
# 2. npmキャッシュとグローバルインストール先を/tmpに設定
export npm_config_cache=/tmp/npm-cache
export npm_config_prefix=/tmp/npm-global
# パスを通す（npm global installの場所）
export PATH=$npm_config_prefix/bin:$PATH
# 3. AWS CDKの最新バージョンをインストール
sudo npm install -g aws-cdk@latest
# 4. リポジトリのクローン
git clone https://github.com/keisskaws/simplechat.git
cd simplechat
# 5. CDKプロジェクトの依存関係インストール & フロントエンドビルド
npm install
# 6. AWSアカウントのブートストラップ（初回のみ）
cdk bootstrap
# 7. CDKスタックのデプロイ
cdk deploy
