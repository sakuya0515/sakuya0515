# 葛飾応為「吉原格子先之図」を描く ― リリックモーション 台本 v2

## v2の軸
吉原の格子の前に立ち、ろうそくの炎に手をかざす。そうして見た光が、絵の中の夜と灯になる。
（v1にあった「応・為・栄の隠し落款」「遊女の顔を影に沈める」は本筋から外した）

- 尺：約72秒（ストーリー優先。曲が届いたら合わせる）
- 画面：横 16:9
- 色：B＋C
  - 素描のカット（S）：画像1と同じセピアの木炭・鉛筆。炎・格子から漏れる灯りだけ暖色
  - 絵のカット（P）：実物の「吉原格子先之図」。編集で光と動きをつける（AIで動画化しない）
- 応為の顔・髪・服：画像1で統一

## 仕組み：「見た光」→「描いた光」のつなぎ

応為が見た光（素描）のすぐ後に、絵の中の同じ光（実物）を置く。前後で画面の形をそろえる。

| 見た光（素描） | → | 描いた光（実物） | そろえるもの |
|---|---|---|---|
| S3 格子の影が縦縞で落ちる横顔 | → | P1 絵の格子と黒い人影 | 縦の線のリズム |
| S5 手越しに見つめる炎 | → | P2 絵の提灯と地面の光 | 炎と提灯を画面の同じ位置に |
| S7 筆先が紙に灯りの色を置く | → | P3 暗闇に灯りがともり、絵の全体へ | 暖色の一点から広がる |

## 台本

| # | 秒 | 種類 | 映っているもの | カメラ | 動き | 音 |
|---|---|---|---|---|---|---|
| S1 | 0:00–0:06 | 素描 | 夜。白い紙の前で、筆を持ったまま動かない応為。左にろうそく | slow push-in | 筆先がわずかに揺れる → 視線を上げる | ろうそくの小さな音 |
| S2 | 0:06–0:12 | 素描 | 吉原の張見世。格子の前に立つ後ろ姿。格子のすき間から暖色の灯りが漏れ、輪郭を縁取る | slow push-in | 動かない。髪の毛先だけ夜風で揺れる | 遠くの三味線、ざわめき |
| S3 | 0:12–0:18 | 素描 | 格子の影が縦縞で顔に落ちる横顔。片側だけ暖色の光 | gentle push-in | まばたき → 目をわずかに細める | ほぼ無音 |
| P1 | 0:18–0:26 | 実物 | 絵の格子。明るい格子の前を行く黒い人影 | 編集：ゆっくり右から左へ | 格子の中の明かりがゆっくり強まる | 三味線 |
| S4 | 0:26–0:32 | 素描 | 部屋。ろうそくの炎に手のひらをかざす。指のすき間から光、指の縁が赤く透ける | slow push-in | 指をゆっくり開く → 少し閉じる | 炎の揺れる音 |
| S5 | 0:32–0:38 | 素描 | 手をかざしたまま、炎越しに見つめる顔。下から照らされる。炎は画面中央下 | gentle push-in | 手をゆっくり返す → 視線を炎へ | ほぼ無音 |
| P2 | 0:38–0:46 | 実物 | 絵の提灯（禿の提灯）と地面の光のたまり。提灯がS5の炎と同じ位置に来る構図から始める | 編集：ゆっくり寄る | 提灯の灯りがかすかに揺らぐ | 下駄の音、遠い三味線 |
| S6 | 0:46–0:52 | 素描 | 床に這いつくばって描く全身。やや俯瞰。左にろうそく | slow crane down | 筆を走らせる → 墨をつけ直す | 筆が紙を擦る音 |
| S7 | 0:52–0:58 | 素描 | 紙の上の筆先のクローズアップ。筆が触れたところに、暖色の灯りが一点ともる | slow push-in | 筆先が紙に触れる → 色が小さくにじむ | 無音 |
| P3 | 0:58–1:12 | 実物 | 真っ暗な画面に、絵の提灯の灯りが一つずつともり、格子の明かりが入り、絵の全体へ | 編集：寄りから引いて全体へ | 灯りが増えていく | 曲の終わり |

## 開始の1コマ一覧（AIで生成する画像：7枚）

| 画像 | 内容 |
|---|---|
| S1 | 白い紙の前、筆を持って動かない応為。左にろうそく。斜め45度、少し上から、少し引き |
| S2 | 張見世の格子の前に立つ後ろ姿。格子から漏れる暖色の灯り |
| S3 | 格子の影が縦縞で落ちる横顔 |
| S4 | ろうそくの炎に手のひらをかざす手のクローズアップ |
| S5 | 手越しに炎を見つめる顔、下からの光。炎は画面中央下 |
| S6 | 床に這いつくばって描く全身、やや俯瞰 |
| S7 | 紙の上の筆先。筆が触れた一点だけ暖色 |

P1〜P3は実物の絵から編集で作る（Claudeが作れる。高解像度の画像があれば差し替え）。

## 画風の固定ブロック（全カット共通。毎回そのまま入れる）

```
Style: a rough, unfinished charcoal and graphite sketch on warm cream watercolor paper, in sepia monochrome. Loose, sparse strokes. Hair drawn as a few flowing lines. Soft smudged shading. Large areas of untouched paper; the drawing fades into blank paper toward the edges. The background is only suggested with a few strokes. Small white specks scattered like light. Not manga, not anime, no clean line art.
```

## 画像プロンプト：カット1（16:9）v2

画像1を添付して使う。v1から、部屋の説明を減らし、画風の固定ブロックを入れた。

```
Use the attached image as the reference for both the woman and the drawing style. Keep the same face, eyes, messy loose hair, and the same kimono with the dark collar.

Style: a rough, unfinished charcoal and graphite sketch on warm cream watercolor paper, in sepia monochrome. Loose, sparse strokes. Hair drawn as a few flowing lines. Soft smudged shading. Large areas of untouched paper; the drawing fades into blank paper toward the edges. The background is only suggested with a few strokes. Small white specks scattered like light. Not manga, not anime, no clean line art.

Scene: at night, she kneels and leans over a blank sheet of paper on the floor. She holds a thin brush upright in her right hand, its tip just above the paper, not yet painting. Three-quarter view, both eyes visible, her gaze on the paper. Medium shot from slightly above. She sits in the left two thirds of the frame; the right third is left as blank paper.

Light: a single candle to her left. Its small flame and the soft amber glow on the left side of her face and hands are the only color. Everything else stays sepia.

Horizontal 16:9.
```

### 生成後のチェック

1. 顔が画像1と同じ人に見えるか
2. 筆を持つ指の本数と形
3. 炎とその照り返し以外に色が広がっていないか
4. 素描のタッチが写実やアニメ調に変わっていないか。特に目（輪郭線が濃くなる、目が大きくなる、ハイライトが入る）と、描き込みの量（背景が埋まっていないか）
5. 右側の余白が残っているか（歌詞を置く場所）
