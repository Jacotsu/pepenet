FROM python:3.8.0a3-alpine3.9

ENV IPFS_HOST ipfs

COPY . /app

WORKDIR /app
RUN pip3 install -r requirements.txt

CMD ["sh", "-c", "python3 pepenet.py -H $IPFS_HOST"]

EXPOSE 8000
