ARG PY_VERSION
ARG OS_VERSION
FROM python:${PY_VERSION}-${OS_VERSION}
COPY --from=pandoc/core:2.7.2 /usr/bin/pandoc* /usr/bin/
RUN apk add --no-cache \
    gmp \
    libffi \
    lua5.3 \
    lua5.3-lpeg
RUN pip3 install --no-cache-dir pypandoc
COPY . /gitlabform
RUN cd gitlabform && python setup.py develop
WORKDIR /config