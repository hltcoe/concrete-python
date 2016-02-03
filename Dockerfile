FROM ubuntu:latest


RUN apt-get update \
    && apt-get install -y \
        gcc \
        make \
        python \
        python-pip \
        git \
        wget \
        tar \
        vim \
        man \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install ipython
RUN pip install --upgrade setuptools


# pre-install
# Ubuntu's root dot files are (a) archaic and (b) broken
RUN rm /root/.bashrc /root/.profile
RUN echo '#!/bin/bash' > /root/.bash_profile && \
    echo >> /root/.bash_profile && \
    echo 'if [ -f $HOME/.bashrc ] ; then source $HOME/.bashrc ; fi' >> /root/.bash_profile && \
    echo '#!/bin/bash' > /root/.bashrc && \
    echo >> /root/.bashrc && \
    echo 'export PATH="$HOME/bin:$HOME/.local/bin:$PATH"' >> /root/.bashrc && \
    echo 'export LD_LIBRARY_PATH="$HOME/lib:$LD_LIBRARY_PATH"' >> /root/.bashrc && \
    echo 'export LIBRARY_PATH="$HOME/lib:$LIBRARY_PATH"' >> /root/.bashrc && \
    echo 'export C_INCLUDE_PATH="$HOME/include:$C_INCLUDE_PATH"' >> /root/.bashrc && \
    echo 'export CPLUS_INCLUDE_PATH="$HOME/include:$CPLUS_INCLUDE_PATH"' >> /root/.bashrc


# needed for running tests only---can be removed if desired
RUN cd /root && \
    wget http://download.redis.io/releases/redis-3.0.2.tar.gz && \
    tar -xzf redis-3.0.2.tar.gz && \
    cd redis-3.0.2 && \
    make && \
    make install && \
    cd deps/hiredis && \
    make install


# add source
ADD . /root/concrete-python/
RUN bash -c 'source /root/.bashrc && cd /root/concrete-python && python setup.py install'
