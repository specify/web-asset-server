FROM ubuntu:26.04

LABEL maintainer="Specify Collections Consortium <github.com/specify>"

RUN apt-get update && apt-get -y install --no-install-recommends \
        ghostscript \
        imagemagick \
        libheif-plugin-libde265 \
        python3.14 \
        python3.14-venv \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 999 specify && \
        useradd -r -u 999 -g specify specify

RUN mkdir -p /home/specify && chown specify.specify /home/specify

USER specify
WORKDIR /home/specify

COPY --chown=specify:specify requirements.txt .

RUN python3.14 -m venv ve && ve/bin/pip install --no-cache-dir -r requirements.txt

COPY --chown=specify:specify server.py settings.py storage.py manage_collection_dirs.py ./
COPY --chown=specify:specify views ./views

RUN mkdir -p /home/specify/attachments/

CMD ["ve/bin/python", "server.py"]
