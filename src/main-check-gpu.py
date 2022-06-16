from flask import Flask, request, jsonify
import os
import pynvml
import torch
import logging
from multiprocessing import Process
import multiprocessing
from ctypes import c_char_p

if not os.path.exists("/home/log"):
    os.makedirs("/home/log")
logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("/home/log/check-gpu.log", mode="a", encoding="utf-8")
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
_RESULT = multiprocessing.Manager().Array('i', [0, 0, 0, 0, 0, 0])
_MSG = multiprocessing.Manager().Value(c_char_p, "")

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
    logger.info("Driver Version:%s", pynvml.nvmlSystemGetDriverVersion())
    deviceCount = pynvml.nvmlDeviceGetCount()
    logger.info("deviceCount: %d", deviceCount)
    return deviceCount


def showDown():
    pynvml.nvmlShutdown()


def gpuCmd(msg, RESULT, gpuIndex):
    cur = gpuIndex
    logger.info("检测第"+str(gpuIndex)+"张卡开始")
    try:
        aR = torch.rand(10).to('cuda:' + str(gpuIndex))
        print(aR.shape)
    except RuntimeError as rE:
        logger.error(rE)
        msg.value = msg.value + ("index:" + str(cur) + "-" + str(rE))
        if "out of memory" in str(rE):
            logger.info("调用显卡OOM")
            RESULT[gpuIndex] = 1  # 调用显卡OOM
            return
        else:
            logger.info("检测出现异常 调用GPU失败")
            msg.value = msg.value + "检测出现异常 调用GPU失败"
            RESULT[gpuIndex] = 3  # 检测出现异常 调用GPU失败
            return
    RESULT[gpuIndex] = 0
    return


def checkDeviceIsAvailable(gpuNum, appNum, msg):
    if gpuNum == 0:
        return 0
    gpuInfo = []
    for i in range(gpuNum):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        # s = pynvml.nvmlDeviceGetMemoryInfo(handler,1)
        memoryInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        # processInfos = pynvml.nvmlDeviceGetGraphicsRunningProcesses_v2(handle)
        # picInfo = pynvml.nvmlDeviceGetPciInfo(handle)
        # dis = pynvml.nvmlDeviceDiscoverGpus(picInfo)
        gpuInfo.append(
            {'index': i, 'processCount': 0,
             'usageRate': (memoryInfo.used / (memoryInfo.total * 1.0)) * 100})
    freeGPU = 0
    freeGPUIndex = []
    if len(gpuInfo) > 0:
        for g in gpuInfo:
            if g['processCount'] == 0 and g['usageRate'] <= 0.3:
                freeGPU += 1
                freeGPUIndex.append(g["index"])
    print("gpuInfo:", gpuInfo)
    print("freeGPUIndex:", freeGPUIndex)
    logger.info("空闲GPU数量 %d", freeGPU)
    if freeGPU < appNum:
        msg.value = msg.value + "当前节点[" + NODE_NAME + "]存在进程冲突的可能"
        logger.info("当前节点[" + NODE_NAME + "]存在进程冲突的可能")
        return 2  # 进程冲突
    process = []
    logger.info("GPU检测开始")
    for gpuIndex in freeGPUIndex:
        s = Process(target=gpuCmd, args=(msg, _RESULT, gpuIndex,))
        process.append(s)
        s.start()

    for p in process:
        p.join()
    logger.info("完成GPU检测" + str(_RESULT))
    if 1 in _RESULT:
        logger.info("GPU异常检测 return 1")
        return 1
    if 2 in _RESULT:
        logger.info("GPU异常检测 return 2")
        return 2
    if 3 in _RESULT:
        logger.info("GPU异常检测 return 3")
        return 3
    if 0 in _RESULT:
        logger.info("GPU异常检测 return 0")
        return 0

    return 0


@app.route('/api/checkNvidia', methods=['GET'])
def checkNvidia():
    for i in _RESULT:
        _RESULT[i] = 0
    _MSG.value = ""
    logger.info("RESULT="+str(_RESULT))
    appNum = request.args.get("appNum")
    if appNum == None:
        appNum = 1
    # 0 成功 1内存溢出无法使用 2 进程冲突 3 检测异常 4 没有GPU 5 INIT_ERROR
    status = '0'
    statusMsg = ['SUCCESS', 'OOM', 'PROCESS_CONFLICT', "CHECK_ERROR", "NO GPU", "INIT_ERROR"]
    try:
        count = deviceNvmlInit()  # 初始化ml
        status = checkDeviceIsAvailable(count, int(appNum), _MSG)
    except Exception as err:
        logger.error(err)
        status = 5
        _MSG.value = _MSG.value + str(err)
    finally:
        logger.info("释放管理器")
        try:
            showDown()
        except Exception as e:
            logger.error(e)
    return jsonify({'msg': _MSG.value, 'status': status})


@app.route('/api/repair', methods=['GET'])
def gpuRepair():
    return jsonify("ok")


if __name__ == '__main__':
    app.run(port=80, host='0.0.0.0', debug=False)
