FROM alpine:latest
LABEL maintainer=manasmbellani

RUN apk add --update \
    python3 \
    py3-pip

COPY . /app
WORKDIR /app

ENTRYPOINT [ "python3", "pyrevdnsall.py" ]