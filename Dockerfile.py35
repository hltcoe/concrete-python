FROM python:3.5-alpine

ADD . /tmp/concrete-python
WORKDIR /tmp/concrete-python
RUN pip install tox
RUN python setup.py install
