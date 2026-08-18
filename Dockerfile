FROM alpine:latest

RUN apk add python3 py-pip py3-yaml stunnel tini

COPY --chmod=644 hastunnel.py .

CMD ["tini", "python3", "/hastunnel.py"]
