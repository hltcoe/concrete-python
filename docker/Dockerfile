FROM ubuntu:latest


RUN apt-get update \
    && apt-get install -y \
        gcc \
        git \
        make \
        man \
        python \
        python-dev \
        python-pip \
        tar \
        vim \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install ipython tox flake8 mock pytest
RUN pip install --upgrade setuptools


WORKDIR /tmp

# install redis---only needed in order to run redis tests
ENV redis_version=redis-3.0.6
RUN wget http://download.redis.io/releases/${redis_version}.tar.gz \
    && tar -xzf ${redis_version}.tar.gz \
    && cd ${redis_version} \
    && make \
    && make install PREFIX=/usr/local \
    && cd deps/hiredis \
    && make install PREFIX=/usr/local \
    && cd ../../.. \
    && rm -rf ${redis_version}*

# install concrete-python system-wide
ADD . concrete-python/
RUN cd concrete-python \
    && python setup.py install \
    && cd .. \
    && rm -rf concrete-python


# add hltcoe user
RUN useradd -U -m -s /bin/bash hltcoe \
    && passwd -l hltcoe

# set up hltcoe user environment, including local copy of source,
# and switch to hltcoe user
WORKDIR /home/hltcoe

ADD . concrete-python/
RUN chown -R hltcoe:hltcoe concrete-python

USER hltcoe
RUN cp concrete-python/docker/bash_profile .bash_profile \
    && cat concrete-python/docker/bashrc.append >> .bashrc
