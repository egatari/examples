---
title: 付録 Claude Code と npx egatari
kind: appendix
---

この本の本文は、ブラウザの Studio だけで進めた。ここでは、端末（ターミナル）を使う人向けの 2 つの道を短く紹介する。どちらも使わなくてよい。

(sec-lalbqu)=
## Claude Code のスキルで作る

Claude Code（Anthropic の、端末で動く AI エージェント）を使っているなら、Egatari のスキルを入れておくと、作りたいものをふつうの言葉で頼める。Claude が構成案を見せ、承認するとスライド（`deck.html`）と台本（`narration.md`）を新しいフォルダに書く。

Claude Code の中で、次の 3 行を実行する。

```text
/plugin marketplace add egatari/egatari-studio
/plugin install egatari@egatari
/plugin install egatari-studio@egatari
```

- `egatari` は、スライドと台本を書くスキルだけを持つ。Node.js は要らない
- `egatari-studio` は、ローカルで品質チェック・ビルド・動画のエクスポートなどをするスキルを持つ。Node.js が要る

スキルの指示と品質チェックは、Studio のバージョンごとに変わる。入れた後は `/plugin` の Marketplaces のタブで egatari を選び、自動更新（Enable auto-update）を入れておく。

頼み方の例：

> 動きのある HTML スライドで、〇〇の授業を作って。対象は〇〇の学生、15 分、話す人は 1 人。

できたフォルダは、Chrome か Edge の Studio で **ファイル ▾ → フォルダで作業する…** を押して開く。Claude がフォルダを書き換えている間も Studio を開いたままにしておくと、プレビューが自動で新しくなる。

claude.ai（ブラウザやアプリの Claude）や Cowork では、Studio の **AI のスキルをダウンロード** で落とした ZIP ファイルを追加する。こちらは自動では新しくならないので、Studio を更新したら追加し直す。

(sec-sdqvfn)=
## npx egatari で品質チェック・ビルド

Node.js が入っていれば、Studio と同じ品質チェックとビルドを、端末から `npx egatari` で動かせる。インストールは要らない。

```text
npx egatari@0.6.x doctor
npx egatari@0.6.x check <作業フォルダ>/deck.html
npx egatari@0.6.x build <作業フォルダ>/deck.html --portable
```

- `doctor`：Node.js・ブラウザ・uv・ffmpeg がそろっているか、入れたスキルが古くないかを調べる。足りないものは入れ方を案内する
- `check`：品質チェック。Studio の品質チェックのパネルと同じ指摘を出す
- `build --portable`：作業フォルダを Egatari ファイル（`.ega.html`）にする。`--play-only` なら再生専用、`--scorm` なら LMS 用のパッケージになる

ほかに、台本から AI 音声を作る `tts`、全スライドを 1 枚の画像に並べる `sheet`、動画にする `video` などがある。一覧は `npx egatari --help` で見られる。

