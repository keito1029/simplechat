#!/bin/bash

cd /tmp/testdir
# 2. npmキャッシュとグローバルインストール先を/tmpに設定
export npm_config_cache=/tmp/npm-cache
export npm_config_prefix=/tmp/npm-global
# パスを通す（npm global installの場所）
export PATH=$npm_config_prefix/bin:$PATH

cd simplechat
# 5. CDKプロジェクトの依存関係インストール & フロントエンドビルド
npm install
# 6. AWSアカウントのブートストラップ（初回のみ）
cdk bootstrap
# 7. CDKスタックのデプロイ
cdk deploy
