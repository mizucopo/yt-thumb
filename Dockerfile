FROM alpine:3.23

RUN apk add --no-cache \
    imagemagick \
    fontconfig \
    ttf-dejavu \
  && fc-cache -f

COPY fonts/*.ttf /usr/local/share/fonts/
COPY licenses/ /licenses/
RUN fc-cache -f

WORKDIR /work
ENTRYPOINT ["magick"]
