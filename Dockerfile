# Build 'accelerated' concrete-python with C bindings for Python Thrift
FROM python:3.6-stretch

RUN curl -O http://apache.mirrors.pair.com/thrift/0.11.0/thrift-0.11.0.tar.gz && \
    tar xvfz thrift-0.11.0.tar.gz && \
    cd thrift-0.11.0 && \
    ./configure --with-python  && \
    make && \
    make install
ADD . /tmp/concrete-python
RUN cd /tmp/concrete-python && \
    python setup.py install
RUN thrift-is-accelerated.py
