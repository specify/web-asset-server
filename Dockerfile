FROM ubuntu:18.04

LABEL maintainer="Specify Collections Consortium <github.com/specify>"

RUN apt-get update && apt-get -y install --no-install-recommends \
        ghostscript \
        imagemagick \
        python3.12 \
        python3-venv \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 999 specify && \
        useradd -r -u 999 -g specify specify

RUN mkdir -p /home/specify && chown specify.specify /home/specify

USER specify
WORKDIR /home/specify

COPY --chown=specify:specify requirements.txt .

RUN python3.12 -m venv ve && ve/bin/pip install --no-cache-dir -r requirements.txt

COPY --chown=specify:specify *.py views ./

RUN mkdir -p /home/specify/attachments/

RUN echo \
        "import os" \
        "\nSERVER = 'paste'" \
        "\nSERVER_NAME = os.environ['SERVER_NAME']" \
        "\nSERVER_PORT = int(os.getenv('SERVER_PORT', 8080))" \
        "\nKEY = os.environ['ATTACHMENT_KEY']" \
        "\nDEBUG = os.getenv('DEBUG_MODE', 'false').lower() == 'true'" \
        >> settings.py

EXPOSE 8080
CMD ve/bin/python server.py
