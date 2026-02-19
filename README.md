# yt-thumb

YouTubeサムネイル画像生成用のDockerイメージ

## Build

```bash
docker build --platform linux/amd64 -t mizucopo/yt-thumb:develop .
```

## Usage

```bash
docker run --rm -v "$PWD":/work \
  mizucopo/yt-thumb:develop \
  input.png \
  -resize 1920x1080 \
  -background black \
  -gravity center \
  -extent 1920x1080 \
  -font "/usr/local/share/fonts/YuseiMagic-Regular.ttf" \
  -pointsize 240 \
  -gravity southwest \
  -kerning 0 \
  -fill none -stroke white -strokewidth 34 -annotate "+80+60" "#13" \
  -fill red -stroke none -annotate "+80+60" "#13" \
  -strip \
  -define jpeg:extent=2000KB \
  output.jpg
```

## GitHub リポジトリ設定

Dockerイメージの自動リリースを有効にするには、以下の設定が必要です。

### Secrets

| 名前 | 説明 |
|------|------|
| `DOCKERHUB_TOKEN` | Docker HubのAccess Token（[Docker Hub Account Settings](https://hub.docker.com/settings/security)で作成） |

## License

- Code: MIT (see [LICENSE](LICENSE))
- Bundled fonts: SIL Open Font License 1.1 (see [licenses/fonts/](licenses/fonts/))
- ImageMagick: ImageMagick License (see https://imagemagick.org/license/)
