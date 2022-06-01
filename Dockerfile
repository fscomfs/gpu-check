FROM nvidia/cuda:11.2.0-cudnn8-devel-ubuntu18.04

ENV PYTHON_VERSION 3.7
RUN apt-get update \
    && apt-get install -y software-properties-common curl \
    && apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python3-apt python3-distutils \
    # 设置默认python版本链接
    && update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 40 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 40 \
    && update-alternatives --set python /usr/bin/python${PYTHON_VERSION} \
    && update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION} \
    # pip, wheel, setuptools
    && curl https://bootstrap.pypa.io/get-pip.py -o /usr/local/src/get-pip.py \
    && python${PYTHON_VERSION} /usr/local/src/get-pip.py \

RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 40 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 40 \
    && update-alternatives --set python /usr/bin/python${PYTHON_VERSION} \
    && update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION} \
COPY . /home
RUN cd /home && pip3 -r requirements.txt