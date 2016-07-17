FROM python:2.7-onbuild

RUN apt-get install imagemagick

ONBUILD COPY requirements.txt /usr/src/app/
ONBUILD RUN pip install --no-cache-dir -r requirements.txt

ONBUILD COPY . /usr/src/app

ENV SPECIFY_KEY  None
ENV SPECIFY_HOST localhost

ENV SPECIFY_PORT 8080
EXPOSE 8080

ENV BASE_DIR /home/specify/attachments/
RUN mkdir -p /home/specify/attachments
VOLUME       /home/specify/attachments

ENTRYPOINT python server.py
