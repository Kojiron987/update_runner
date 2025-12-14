# update-runner

## 概要

**update-runner** は Linuxで動作する軽量な OTA 実行エンジンです。  
AWS IoT Jobs や Software Package Catalog と連携し、外部から受け取った OTA パッケージ（スクリプト + ファイル）
を安全かつ確実に適用することを目的としています。

特徴:

- Runner 本体は不変（更新不要）
- パッケージ側にロジックを委譲
- アトミックな更新
- 中断復帰（resume）対応
- JSON-RPC over Unix Domain Socket による外部トリガ受付
