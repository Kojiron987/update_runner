# update-runner

## 1. 概要

**update-runner** は Linuxで動作する軽量な OTA 実行エンジンです。  
AWS IoT Jobs や Software Package Catalog と連携し、外部から受け取った OTA パッケージ（スクリプト + ファイル）
を安全かつ確実に適用することを目的としています。

特徴:

- Runner 本体は不変（更新不要）
- パッケージ側にロジックを委譲
- アトミックな更新
- 中断復帰（resume）対応
- JSON-RPC over Unix Domain Socket による外部トリガ受付

---

## 2. システム構成

`/opt/update-runner/` 配下に以下を保持:

/opt/update-runner/
state.json
active/
staging/
backup/
logs/
ota.sock # Unix Domain Socket


---

## 3. OTA パッケージ仕様

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

3.3 スクリプト要件

    verify.sh: パッケージ整合性チェック。問題なければ 0 を返す

    install.sh: インストール処理。返却コードは以下

exit code	意味
0	成功
1	再試行可能エラー
2	永続的エラー（Job を Rejected にすべき）

両スクリプトは 冪等 であること
途中状態から再開可能にする責務はスクリプト側
4. Runner の状態管理
4.1 state.json

{
  "phase": "idle | downloading | verifying | installing | completed | error",
  "package_version": "",
  "checksum": "",
  "retry_count": 0,
  "last_error": ""
}

4.2 起動時の挙動

    state.json を読み込む

    phase に応じて途中から再開

    idle なら待受

5. 更新フロー
5.1 通常フロー

    Job arrival / JSON-RPC 呼び出し

    パッケージをダウンロードし staging へ展開

    verify.sh 実行（0 以外なら中断）

    staging → active をアトミックに切替

    install.sh 実行

成功なら state 完了 + Job success
5.2 中断復帰

Runner 再起動後:

    phase を読み取り、途中段階を再実行

    verify / install は冪等性前提

6. JSON-RPC over Unix Domain Socket
6.1 UDS パス

/opt/update-runner/ota.sock

6.2 JSON-RPC メソッド
install

OTA パッケージのインストールを開始

Request:

{
  "jsonrpc": "2.0",
  "method": "install",
  "params": {
    "package_path": "/path/to/package.tar.gz"
  },
  "id": 1
}

Response:

{
  "jsonrpc": "2.0",
  "result": "accepted",
  "id": 1
}

status

現在の runner 状態を返す

{
  "phase": "installing",
  "package_version": "1.0.0"
}

cancel

実行中の OTA をキャンセル（可能なら）
7. セーフティ

    active 切替は rename によるアトミック性保証

    verify 失敗時は active を変更しない

    rollback_supported が true の場合は backup を利用

    install の exit code でジョブ通知を振り分け