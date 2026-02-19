# yt-thumb

YouTubeサムネイル画像生成用のDockerコンテナ

## Build

```bash
docker build -t mizucopo/yt-thumb:develop .
```

## Usage

```bash
docker run --rm -v $(pwd):/work mizucopo/yt-thumb:develop convert input.png output.jpg
```

## License

- Code: MIT (see [LICENSE](LICENSE))
- Bundled fonts: SIL Open Font License 1.1 (see [licenses/fonts/](licenses/fonts/))
- ImageMagick: ImageMagick License (see https://imagemagick.org/license/)
