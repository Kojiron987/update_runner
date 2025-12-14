# A-Runner 仕様書

## 1. 概要

Update-Runner は IoT デバイス上で動作する軽量な Update 実行エンジンであり、AWS IoT Jobs または Software Package Catalog と連携し、外部から受け取った Update パッケージ（スクリプト + ファイル）を安全かつ確実に適用することを目的とする。

Update-Runner は以下の特徴を持つ:

Runner 本体は不変（更新しない）

パッケージ側にロジックを委譲

アトミックな更新

中断復帰（resume）

JSON-RPC over Unix Domain Socket による外部トリガ受付

## 2. システム構成
/opt/update-runner/
  state.json
  active/
  staging/
  backup/
  logs/

## 3. パッケージ仕様

### 3.1 ディレクトリ構造

package/
  manifest.json
  scripts/
    verify.sh
    install.sh
  files/

### 3.2 manifest.json

```json
{
  "version": "1.0.0",
  "checksum": "sha256:xxxx",
  "rollback_supported": true
}
```

### 3.3 スクリプト要件

verify.sh: パッケージの整合性をチェックし、問題なければ 0 を返す

install.sh: インストール処理を行い、0 / 1 / 2 を返す

* 0: 成功
* 1: 再試行可能エラー
* 2: 永続的エラー（Job を Rejected にすべき）

両スクリプトは冪等であること

途中状態から再開可能にすること（責務はスクリプト側）

## 4. Runner の状態管理

### 4.1 state.json

```json
{
  "phase": "idle | downloading | verifying | installing | completed | error",
  "package_version": "",
  "checksum": "",
  "retry_count": 0,
  "last_error": ""
}
```

### 4.2 起動時の挙動

1. state.json を読み込む
2. phase に応じて続きを再開
3. idle なら待受

## 5. 更新フロー

### 5.1 通常フロー

1. Job arrival / JSON-RPC 呼び出し
2. パッケージをダウンロードし staging へ展開
3. verify.sh 実行（0 以外なら中断）
4. staging → active をアトミックに切替
5. install.sh 実行

成功なら state 完了 + Job success

### 5.2 中断復帰

Runner 再起動後:

phase を読み取り、途中段階を再実行

verify / install は冪等性前提

## 6. JSON-RPC over Unix Domain Socket

### 6.1 UDS のパス

/run/update_runner/uds.sock

### 6.2 JSON-RPC メソッド

#### 6.2.1 install

パッケージのインストールを開始する

Request:

```json
{
  "jsonrpc": "2.0",
  "method": "install",
  "params": {
    "package_path": "/path/to/package.tar.gz"
  },
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "result": "accepted",
  "id": 1
}
```

#### 6.2.2 status

現在の runner 状態を返す

Result:

```json
{
  "phase": "installing",
  "package_version": "1.0.0"
}
```

## 7. セーフティ

* active 切替は rename によるアトミック性保証
* verify 失敗時は active を触らない
* rollback_supported が true なら backup を利用
* install の exit code でジョブ通知振り分け

## 8. A/B Partition がない前提での安全性

アトミックな active/staging 切替

冪等スクリプト

明確な state.json

中断復帰（resume）

この構造なら A/B なしでも十分安全性を確保できる。

## 9. 今後拡張案

* Software Package Catalog との direct integration
* Progress レポート
* Watchdog 実装
* Job スクリプト向けの標準ライブラリ提供
