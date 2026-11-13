# Egatari samples / Egatari のサンプル

Samples of [Egatari](https://github.com/egatari/egatari-spec) lessons, each one a pair: **the request you give a chat AI** and **the lesson it produced**, made with [Egatari Studio](https://github.com/egatari/egatari-studio) and the [parts library](https://github.com/egatari/components).

Egatari のサンプル集。1 つのサンプルは「チャットの AI に渡す頼み方の文」と「それでできた教材」の組です。

Status: the built samples are attached to GitHub Releases (`samples-v0.6.9` and later), each with a `SHA256SUMS` file to check them. Get them from the [latest release](https://github.com/egatari/examples/releases/latest).
今の状態：組んだサンプルは GitHub の Release（`samples-v0.6.9` 以降）に添付しています。どの Release にも、確かめるための `SHA256SUMS` があります。[最新の Release](https://github.com/egatari/examples/releases/latest) から受け取れます。

Get a lesson: the built files (`.ega.html`) are not kept in this repository. Download them from the [Releases](https://github.com/egatari/examples/releases), or build one from its folder with `npx egatari build --portable lessons/<name>` (Egatari Studio v0.6.8 or later).
教材の受け取り方：組んだファイル（`.ega.html`）はこのリポジトリに置いていません。[Releases](https://github.com/egatari/examples/releases) から受け取るか、フォルダから `npx egatari build --portable lessons/<名前>` で組んでください（Egatari Studio v0.6.8 以降）。

The request in each lesson's `sample.json` (used by Studio's "Make one based on this sample") was written afterwards as an example: these lessons were made from plans, not from that one request.
各サンプルの `sample.json` にある頼み方の文（Studio の「このサンプルを参考に作る」で使う）は、後から例として書いたものです。サンプルはその 1 つの頼み方からではなく、計画から作りました。

License: lessons CC BY 4.0, scripts MIT ([LICENSE.md](LICENSE.md)).
