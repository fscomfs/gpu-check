FROM cvmart-zhuhai-tcr.tencentcloudcr.com/public_images/ubuntu18.04-cuda11.1-cudnn8-devel-train-test-pytorch1.10.0-openvino2021r3-workspace-base:v1.2
COPY . /home
RUN cd /home && pip3 install -r requirements.txt