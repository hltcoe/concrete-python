FROM ubuntu:trusty

RUN apt-get update

RUN apt-get install -y \
        autoconf \
        automake \
        curl \
        gcc \
        git \
        libtool \
        m4 \
        make \
        pkg-config \
        python \
        python-dev \
        python-pip

RUN pip install --upgrade --ignore-installed setuptools six
RUN pip install --upgrade \
        flake8 \
        pytest \
        pytest-cov \
        tox \
        Twisted

WORKDIR /tmp
RUN mkdir -p /usr/local/{include,lib}

RUN curl http://download.redis.io/releases/redis-3.0.7.tar.gz | tar -xz && \
    cd redis-3.0.7 && \
    make && \
    make install && \
    cd deps/hiredis && \
    make install && \
    cd ../.. && \
    cd .. && \
    rm -rf redis-3.0.7*

RUN ldconfig -v

RUN useradd -m -U -s /bin/bash concrete && \
    passwd -l concrete
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> \
        /home/concrete/.bashrc
ADD . /home/concrete/concrete-python
RUN chown -R concrete:concrete /home/concrete

USER concrete
WORKDIR /home/concrete/concrete-python
RUN python setup.py build
