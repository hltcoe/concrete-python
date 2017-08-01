FROM centos:7

RUN yum update -y && yum clean all

RUN yum install -y \
        autoconf \
        automake \
        bzip2-devel \
        bzip2-libs \
        gcc \
        gcc-c++ \
        git \
        libtool \
        libzip \
        libzip-devel \
        m4 \
        make \
        openssl \
        openssl-devel \
        openssl-libs \
        pkgconfig \
        python \
        python-devel \
        tar \
        zlib \
        zlib-devel

RUN curl https://bootstrap.pypa.io/get-pip.py | python && \
    pip install --upgrade setuptools && \
    pip install --upgrade setuptools && \
    pip install --upgrade \
        thrift==0.10.0 \
        tox>=1.6.1

WORKDIR /tmp
RUN mkdir -p /usr/local/{include,lib}

RUN curl https://www.python.org/ftp/python/3.5.3/Python-3.5.3.tgz | tar -xz && \
    pushd Python-3.5.3 && \
    ./configure --prefix=/usr/local && \
    make && \
    make altinstall && \
    popd && \
    rm -rf Python-3.5.3

RUN curl https://bootstrap.pypa.io/get-pip.py | python3.5 && \
    pip3.5 install --upgrade setuptools && \
    pip3.5 install --upgrade setuptools && \
    pip3.5 install --upgrade \
        thrift==0.10.0

RUN ldconfig -v

RUN useradd -m -U -s /bin/bash concrete && \
    passwd -l concrete
ADD . /home/concrete/concrete-python
RUN cd /home/concrete/concrete-python && \
    python setup.py install && \
    python setup.py clean && \
    chown -R concrete:concrete /home/concrete

USER concrete
WORKDIR /home/concrete
