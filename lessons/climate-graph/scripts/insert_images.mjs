// Put the climographs into deck.html with the same code as Egatari Studio's 「画像を挿入…」
// (kit/core/image-insert.mjs, v0.6.19), then add the source line (the 出典の行 template's <p class="source">).
// Run from an Egatari Studio v0.6.19 checkout:  node <this file> <lesson folder>
import fs from 'node:fs';
import path from 'node:path';
import { insertImage, imageType, dataUrl } from './kit/core/image-insert.mjs';
const dir = path.resolve(process.argv[2]);
let src = fs.readFileSync(path.join(dir, 'deck.html'), 'utf8');
const img = (k) => { const b = fs.readFileSync(path.join(dir, 'images', k + '.png')); return dataUrl(b, imageType(b)); };
const SRC = '<p class="source">出典：気象庁「過去の気象データ検索」の平年値（1991〜2020 年）をもとに作成</p>';
const put = [   // [slide index, image, placement, step, alt]
  [1, 'tokyo', 'left', 0, '東京の雨温図。棒は月ごとの降水量で、6 月と 9 月に多く、冬は少ない。折れ線は月ごとの平均気温で、1 月 5 ℃台から 8 月 27 ℃近くまで上がる'],
  [3, 'sapporo', 'left', 1, '札幌の雨温図。平均気温は 1 月 −3.2 ℃、8 月 22.3 ℃。降水量は 4〜6 月が少なく、秋から冬に 100 mm 前後'],
  [3, 'naha', 'right', 2, '那覇の雨温図。平均気温は 1 月 17.3 ℃、7 月 29.1 ℃。降水量は 5〜6 月と 8〜9 月に多い'],
  [5, 'winter', 'full', 0, '冬（12〜2 月）の降水量の合計の横棒。金沢 719.7 mm、那覇 326.1 mm、札幌 314.8 mm、東京 174.1 mm。金沢がほかの 2 倍以上'],
];
for (const [i, k, placement, step, alt] of put) src = insertImage(src, i, { src: img(k), alt, placement, step: step || undefined });
// 出典の行：画像のあるスライドの本文の終わり（結論の行の前）
const ids = [1, 3, 5];
let n = -1;
src = src.replace(/<section\b[\s\S]*?<\/section>/g, (sec) => { n++; return ids.includes(n) ? sec.replace(/(\n\s*)<div class="concl">/, `\n    ${SRC}$1<div class="concl">`) : sec; });
fs.writeFileSync(path.join(dir, 'deck.html'), src);
console.log('inserted', put.length, 'images; source lines', ids.length);
