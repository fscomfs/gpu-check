from flask import Flask, request, jsonify
import os
import pynvml
import torch

NODE_IP = os.getenv('NODE_IP')
if NODE_IP == None:
    NODE_IP = "0.0.0.0"
NODE_NAME = os.getenv('NODE_NAME')
if NODE_NAME == None:
    NODE_NAME = "-----"
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def deviceNvmlInit():
    pynvml.nvmlInit()
    print('Driver Version:', pynvml.nvmlSystemGetDriverVersion())
    deviceCount = pynvml.nvmlDeviceGetCount()
    print('deviceCount:', deviceCount)
    return deviceCount


def showDown():
    pynvml.nvmlShutdown()


def checkDeviceIsAvailable(gpuNum, appNum, msg):
    if gpuNum == 0:
        return 0
    gpuInfo = []
    for i in range(gpuNum):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        # s = pynvml.nvmlDeviceGetMemoryInfo(handler,1)
        memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        processInfos = pynvml.nvmlDeviceGetGraphicsRunningProcesses_v2(handle)
        picInfo = pynvml.nvmlDeviceGetPciInfo(handle)
        # dis = pynvml.nvmlDeviceDiscoverGpus(picInfo)
        gpuInfo.append({'index': i, 'processCount': len(processInfos)})
    freeGPU = 0
    freeGPUIndex = []
    if len(gpuInfo) > 0:
        for g in gpuInfo:
            if g['processCount'] == 0:
                freeGPU += 1
                freeGPUIndex.append(g["index"])
    if freeGPU < appNum:
        msg += "当前节点[" + NODE_NAME + "]存在进程冲突的可能"
        return 2  # 进程冲突

    try:
        for index in freeGPUIndex:
            aR = torch.rand((10, 1024, 256)).to('cuda:'+index)
            b = (aR + 1) * 2
            print(aR.shape)
    except RuntimeError as rE:
        msg += str(rE)
        if rE.message in "out of memory":
            return 1  # 调用显卡OOM
        else:
            return 3  # 检测出现异常 调用GPU失败
    return 0


@app.route('/api/checkNvidia', methods=['GET'])
def checkNvidia():
    appNum = request.args.get("appNum")
    if appNum == None:
        appNum = 1
    msg = []
    flag = False
    # 0 成功 1内存溢出无法使用 2 进程冲突 3 检测异常 4 没有GPU 5 INIT_ERROR
    status = 0
    statusMsg = ['SUCCESS', 'OOM', 'PROCESS_CONFLICT', "CHECK_ERROR", "NO GPU", "INIT_ERROR"]
    try:
        count = deviceNvmlInit()  # 初始化ml
        status = checkDeviceIsAvailable(count, int(appNum), msg)
    except Exception as err:
        flag = False
        status = 5
        msg += str(err)
    finally:
        showDown()
    return jsonify({'msg': ''.join(msg), 'flag': flag, 'status': status})


@app.route('/api/repair', methods=['GET'])
def gpuRepair():
    return jsonify("ok")


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0', debug=True)
