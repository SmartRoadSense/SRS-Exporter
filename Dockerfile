FROM python:3

WORKDIR /tmp

RUN pip install psycopg2-binary

COPY . /tmp/.

VOLUME /data

CMD ["bash"]
