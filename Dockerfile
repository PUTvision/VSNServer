FROM multiarch/ubuntu-core:armhf-xenial

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    python3-pip build-essential cmake wget pkg-config \
    libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libatlas-base-dev gfortran

ARG OPENCV_VERSION
ARG NUMBER_OF_THREADS
RUN mkdir build && \
    cd build && \
    wget -O opencv.tar.gz \
            https://github.com/Itseez/opencv/archive/$OPENCV_VERSION.tar.gz && \
    tar xf opencv.tar.gz && \
    cmake -D WITH_OPENCL=ON \
          -D WITH_OPENGL=ON \
          -D WITH_TBB=ON \
          -D ENABLE_NEON=ON \
          -D BUILD_WITH_DEBUG_INFO=OFF \
          -D BUILD_TESTS=OFF \
          -D BUILD_PERF_TESTS=OFF \
          -D BUILD_EXAMPLES=OFF \
          -D INSTALL_C_EXAMPLES=OFF \
          -D INSTALL_PYTHON_EXAMPLES=OFF \
          -D CMAKE_BUILD_TYPE=Release \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D CMAKE_SKIP_RPATH=ON \
          opencv-$OPENCV_VERSION && \
    make -j$NUMBER_OF_THREADS && \
    make install && \
    ldconfig

ARG CACHEBUST=1
RUN pip3 install git+https://github.com/PUTvision/VSNClient.git
