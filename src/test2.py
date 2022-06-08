import torch
from multiprocessing import Process
import multiprocessing
import logging
import time

logger = logging.getLogger('main')
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

_RESULT = multiprocessing.Manager().Array('i', [0])


def c():
    linear1 = torch.nn.Linear(1024*1800, 1024, bias=False).cuda()
    print(torch.cuda.memory_allocated())
    time.sleep(100)

c()
