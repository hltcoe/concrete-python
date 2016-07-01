FROM cjmay/thrift:ubuntu

RUN apt-get install -y curl

RUN pip install --upgrade \
        flake8 \
        pytest \
        pytest-cov \
        setuptools \
        tox

WORKDIR /tmp
RUN mkdir -p /usr/local/{include,lib}

RUN curl http://download.redis.io/releases/redis-3.2.0.tar.gz | tar -xz && \
    cd redis-3.2.0 && \
    make && \
    make install && \
    cd deps/hiredis && \
    make install && \
    cd ../.. && \
    cd .. && \
    rm -rf redis-3.2.0*

RUN ldconfig -v

RUN useradd -m -U -s /bin/bash concrete && \
    passwd -l concrete
ADD . /home/concrete/concrete-python
RUN cd /home/concrete/concrete-python && \
    python setup.py install && \
    python setup.py clean && \
    chown -R concrete:concrete /home/concrete

USER concrete
WORKDIR /home/concrete/concrete-python
