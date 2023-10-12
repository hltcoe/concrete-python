FROM ccmaymay/concrete-python-base:thrift-0.19.0

RUN pip install 'tox>=4'

ADD . /opt/concrete-python
WORKDIR /opt/concrete-python
RUN pip install . && \
    thrift-is-accelerated.py
