FROM python:3

WORKDIR /tmp

RUN pip install psycopg2-binary
#RUN pip install psycopg2
COPY exporter.py  /tmp/.

VOLUME /data

CMD ["bash"]
