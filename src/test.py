import torch
import time
from multiprocessing import Process
import multiprocessing
import logging

logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

_RESULT = multiprocessing.Manager().Array('i', [0])


def c(_RESULT):
    try:
        aR = torch.rand((10, 1024, 256)).to('cuda:0')
        b = (aR + 1) * 2
        print(b)
        logger.error("计算")
    except RuntimeError as rE:
        logger.error(rE)
        logger.error(str(rE))
        if "out of memory" in str(rE):
            _RESULT[0] = 1  # 调用显卡OOM
            logger.error("OOM++++++++++++++++++" + str(_RESULT[0]))
        else:
            _RESULT[0] = 3  # 检测出现异常 调用GPU失败
            logger.error("++++++++++++++++++" + str(_RESULT[0]))
            return


s = []
for i in range(7):
    w = Process(target=c, args=(_RESULT,))
    s.append(w)
    w.start()

for ll in s:
    ll.join()

print(_RESULT[:])
