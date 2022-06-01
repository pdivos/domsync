FROM python:3.8
WORKDIR /usr/src/app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH="/usr/src/app/src"
ENV PYTHONIOENCODING=UTF-8

RUN pip install --upgrade pip
RUN pip install --no-cache-dir aiohttp[speedups]==3.8.1
RUN pip install --no-cache-dir aiohttp-session==2.9.0

COPY ./domsync /usr/src/app/domsync
COPY ./tests /usr/src/app/tests
COPY ./setup.py /usr/src/app/
# RUN python setup.py test
RUN pip install /usr/src/app/

RUN python tests/domsync_test.py