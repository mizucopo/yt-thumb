#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTubeサムネ生成（決定論）
- 入力画像を 1920x1080 (16:9) にセンタークロップ＆リサイズ
- 左下に "#03" のような連番バッジを、指定した“固定ルール”で描画（白文字＋赤フチ）
- JPEGで2MB以下になるように、品質100→99→…と落として保存（できるだけ高品質を維持）

要件:
  pip install pillow

使い方:
  python make_youtube_thumbnail_numbered.py --episode 3 input.png
  python make_youtube_thumbnail_numbered.py --episode 12 --out out.jpg input.jpg
  python make_youtube_thumbnail_numbered.py --episode 7 --glob "./inbox/*" --outdir "./out"
"""
import argparse, glob, io, os
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ==== 固定ルール（あなたのサンプルから抽出した比率）====
# サンプル: 2048x1152 における #05 の赤フチ領域 bbox が
#   x=90..533, y=856..1038 だったことから決定
LEFT_MARGIN_RATIO = 90/2048
BOTTOM_MARGIN_RATIO = (1152-1038)/1152
FONT_HEIGHT_RATIO = (1038-856)/1152   # バッジの見た目高さ（フチ含む）
STROKE_RATIO = 14/1080               # フチの太さ（高さ比）

LIMIT_BYTES = 2 * 1024 * 1024
OUT_W, OUT_H = 1920, 1080

def load_font(size:int):
    # ※「完全一致」を狙うには、使用フォントを固定する必要があります。
    # 今は環境依存を避けるため、Linux標準の太字フォントを優先で使います。
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

def to_1920x1080(img: Image.Image) -> Image.Image:
    # 16:9 へセンタークロップしてから 1920x1080 にリサイズ
    return ImageOps.fit(img, (OUT_W, OUT_H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def choose_font_size(text: str, stroke_w: int, target_h: int) -> ImageFont.FreeTypeFont:
    # textbboxの高さが target_h に最も近くなる font size を二分探索で選ぶ
    lo, hi = 10, 800
    best = None
    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    while lo <= hi:
        mid = (lo + hi) // 2
        font = load_font(mid)
        bbox = dummy_draw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
        h = bbox[3] - bbox[1]
        err = abs(h - target_h)
        if best is None or err < best[0]:
            best = (err, mid)
        if h < target_h:
            lo = mid + 1
        else:
            hi = mid - 1
    return load_font(best[1])

def render_badge(img: Image.Image, episode_num: int) -> Image.Image:
    img = img.convert("RGBA")
    text = f"#{episode_num:02d}"

    W, H = OUT_W, OUT_H
    x = int(round(W * LEFT_MARGIN_RATIO))
    bottom_margin = int(round(H * BOTTOM_MARGIN_RATIO))
    target_h = int(round(H * FONT_HEIGHT_RATIO))

    stroke_w = max(2, int(round(H * STROKE_RATIO)))
    fill = (255, 255, 255, 255)
    stroke = (220, 0, 0, 255)

    font = choose_font_size(text, stroke_w, target_h)
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    y = H - bottom_margin - th

    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, font=font, fill=fill, stroke_fill=stroke, stroke_width=stroke_w)
    return img

def save_jpeg_under_limit(img: Image.Image, out_path: str) -> tuple[int, int, int]:
    # 2MB以内になるまで quality を落として保存
    rgb = img.convert("RGB")
    for subsampling, q_start, q_end in [(0, 100, 70), (1, 69, 50), (2, 49, 25)]:
        for q in range(q_start, q_end - 1, -1):
            buf = io.BytesIO()
            rgb.save(buf, format="JPEG", quality=q, optimize=True, progressive=True, subsampling=subsampling)
            size = buf.tell()
            if size <= LIMIT_BYTES:
                with open(out_path, "wb") as f:
                    f.write(buf.getvalue())
                return q, subsampling, size
    # 最終手段
    rgb.save(out_path, format="JPEG", quality=20, optimize=True, progressive=True, subsampling=2)
    return 20, 2, os.path.getsize(out_path)

def process_one(inp: str, out: str, episode: int) -> tuple[str, int, int, int]:
    img = Image.open(inp)
    img = to_1920x1080(img)
    img = render_badge(img, episode)
    q, subs, size = save_jpeg_under_limit(img, out)
    return out, q, subs, size

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int, required=True, help="連番（例: 3）")
    ap.add_argument("--out", type=str, default=None, help="出力ファイル名（.jpg推奨）")
    ap.add_argument("--glob", type=str, default=None, help="一括処理用 glob（例: './inbox/*'）")
    ap.add_argument("--outdir", type=str, default=None, help="一括出力先ディレクトリ")
    ap.add_argument("input", nargs="?", help="入力画像パス（単発用）")
    args = ap.parse_args()

    if args.glob:
        files = []
        for pat in args.glob.split(","):
            files.extend(glob.glob(pat.strip()))
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            raise SystemExit("No files matched --glob")
        outdir = args.outdir or "./out"
        os.makedirs(outdir, exist_ok=True)
        for inp in files:
            base = os.path.splitext(os.path.basename(inp))[0]
            out = os.path.join(outdir, f"{base}_thumb_{args.episode:02d}.jpg")
            out_path, q, subs, size = process_one(inp, out, args.episode)
            print(f"OK: {out_path}  quality={q} subsampling={subs} size={size} bytes")
        return

    if not args.input:
        raise SystemExit("input を指定するか --glob を使ってください。")

    inp = args.input
    if args.out:
        out = args.out
    else:
        base = os.path.splitext(os.path.basename(inp))[0]
        out = f"{base}_thumb_{args.episode:02d}.jpg"
    out_path, q, subs, size = process_one(inp, out, args.episode)
    print(f"OK: {out_path}  quality={q} subsampling={subs} size={size} bytes")

if __name__ == "__main__":
    main()
