FROM multiarch/alpine:armhf-latest-stable

RUN apk add -U python3 curl git && \
    curl --remote-name https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py
ARG CACHEBUST=1
RUN pip3 install git+https://github.com/PUTvision/VSNClient.git
