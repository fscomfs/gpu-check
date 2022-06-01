from flask import Flask,request,jsonify
import os
import pynvml
import time
import  base64
os.putenv('NODE_IP','192.168.1.1')
os.putenv('NODE_NAME','test')
NODE_IP = "192.168.1.1"
#NODE_IP = os.getenv('NODE_IP')
NODE_NAME="test"
#NODE_NAME = os.getenv('NODE_NAME')
app = Flask(__name__)

def deviceNvmlInit():
    pynvml.nvmlInit()
    print('Driver Version:', pynvml.nvmlSystemGetDriverVersion())
    deviceCount = pynvml.nvmlDeviceGetCount()
    print('deviceCount:',deviceCount)
    return deviceCount

def showDown():
    pynvml.nvmlShutdown()

def checkDeviceIsAvailable(count):
    if count==0:
        return 0
    for i in range(count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        # s = pynvml.nvmlDeviceGetMemoryInfo(handler,1)
        memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        processInfos = pynvml.nvmlDeviceGetGraphicsRunningProcesses_v2(handle)
        picInfo = pynvml.nvmlDeviceGetPciInfo(handle)
        # dis = pynvml.nvmlDeviceDiscoverGpus(picInfo)
        if len(processInfos)>0:
            print("显卡被占用,当前进程数量 count=",len(processInfos))
        for m in memoryInfo:
            print(m)
        print(processInfos)



@app.route('/api/'+NODE_IP+'/checkNvidia', methods = ['GET'])
def checkNvidiaByIp():
    msg = ''
    checkFlag = 0
    try:
        deviceCount = deviceNvmlInit()
        checkDeviceIsAvailable(deviceCount)
    except Exception  as err:
        msg+='初始化启动检测异常'
        checkFlag = 0
        print("检测异常：",err)
    finally:
        showDown()



    return jsonify("ok2")
  
@app.route('/api/'+NODE_NAME+'/checkNvidia', methods = ['GET'])
def checkNvidiaByNodeName():
    path = request.args.get('path')
    return jsonify("ok")

if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0',debug=True)
