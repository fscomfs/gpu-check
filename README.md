# quick start

build image

docker build -t 192.168.1.130:8099/evtrain/check-gpu-daemon:v1 .

docker build -t uhub.service.ucloud.cn/evtrain/check-gpu-daemon:v1.4 .

curl test175:64235/api/checkNvidia

172.16.0.25



curl -v -x 43.138.87.41:18888  http://172.17.0.45:64235/api/checkNvidia


curl -v -x 106.53.136.157:18888  http://172.16.0.45:64235/api/checkNvidia

for i in 20;  curl test175:64235/api/checkNvidia;done


docker run -it --rm  --privileged   192.168.1.130:8099/evtrain/check-gpu-daemon:v1 bash

for i in $(seq 1 20); do curl test175:64235/api/checkNvidia; done

curl 192.168.1.131:64235/api/checkNvidia
curl 192.168.1.186:64235/api/checkNvidia?appNum=2
curl 192.168.1.187:64235/api/checkNvidia?appNum=2