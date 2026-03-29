FROM apache/hadoop:3

USER root

COPY hadoop/mapper.py /opt/mapper.py
COPY hadoop/reducer.py /opt/reducer.py
COPY data/data.csv /opt/data.csv

RUN ln -sf /usr/bin/python2 /usr/bin/python3 || true

USER hadoop