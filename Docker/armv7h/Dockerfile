FROM rivi/armhf-archlinux

RUN pacman --noconfirm -Syu opencv python-numpy && \
    yes | pacman -Scc

ARG CACHEBUST=1
RUN pacman --noconfirm -Sy python-pip git && \
    pip install git+https://github.com/PUTvision/VSNClient.git && \
    pacman --noconfirm -Rs python-pip git && \
    yes | pacman -Scc
