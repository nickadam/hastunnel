FROM alpine:latest

RUN apk add python3 py-pip stunnel tini

COPY --chmod=644 requirements.txt .

RUN pip3 install -r requirements.txt

COPY --chmod=644 hastunnel.py .

CMD ["tini", "python3", "/hastunnel.py"]
