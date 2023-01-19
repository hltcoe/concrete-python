# Build 'accelerated' concrete-python with C bindings for Python Thrift
FROM python:3.7-bullseye

RUN curl -O http://archive.apache.org/dist/thrift/0.16.0/thrift-0.16.0.tar.gz && \
    tar xvfz thrift-0.16.0.tar.gz && \
    cd thrift-0.16.0 && \
    ./configure --with-python  && \
    make && \
    make install

RUN pip install tox

ADD . /opt/concrete-python
WORKDIR /opt/concrete-python
RUN python setup.py install

RUN thrift-is-accelerated.py
