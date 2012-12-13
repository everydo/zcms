# -*- encoding:utf-8 -*-
import time
import datetime
import os
import shutil
import socket
from random import random
from hashlib import md5
from config import FS_CHARSET
from types import UnicodeType
import array, binascii

def int2ascii(value):
    return binascii.b2a_hex(buffer(array.array('l', (value,))))  # 4byte

def ascii2int(value):
    bin = binascii.a2b_hex(value)
    index, sum = 0, 0
    for c in bin:
        sum += ord(c) << index
        index += 8
    return sum

def timetag(timestamp=None):
    if the_time is None:
        # use gmt time
        the_time = time.gmtime()
        return time.strftime('%Y-%m-%d-%H-%M-%S', the_time)
    else:
        the_time = datetime.datetime.fromtimestamp(timstamp)
        return the_time.strftime('%Y-%m-%d-%H-%M-%S')

def ucopy2(ossrc, osdst):
    # ucopy2 dosn't work with unicode filename yet
    if type(osdst) is UnicodeType and \
           not os.path.supports_unicode_filenames:
        ossrc = ossrc.encode(FS_CHARSET)
        osdst = osdst.encode(FS_CHARSET)
    shutil.copy2(ossrc, osdst)

def ucopytree(ossrc, osdst, symlinks=False):
    # ucopy2 dosn't work with unicode filename yet
    if type(osdst) is UnicodeType and \
            not os.path.supports_unicode_filenames:
        ossrc = ossrc.encode(FS_CHARSET)
        osdst = osdst.encode(FS_CHARSET)
    shutil.copytree(ossrc, osdst, symlinks)

def umove(ossrc, osdst):
    # umove dosn't work with unicode filename yet
    if type(osdst) is UnicodeType and \
           not os.path.supports_unicode_filenames:
        ossrc = ossrc.encode(FS_CHARSET)
        osdst = osdst.encode(FS_CHARSET)
    shutil.move(ossrc, osdst)

try:
    _v_network = str(socket.gethostbyname(socket.gethostname()))
except:
    _v_network = str(random() * 100000000000000000L)

def make_uuid(*args):
    t = str(time.time() * 1000L)
    r = str(random()*100000000000000000L)
    data = t +' '+ r +' '+ _v_network +' '+ str(args)
    uid = md5(data).hexdigest()
    return uid

def rst2frs(filename):
    """ 读取rst的参数，自动补充frs的json元数据 """

    # TODO

    # 读取大标题
    # 读取描述信息
    # 读取作者
    # 读取关键字
    # 当前时间为创建时间
    # 写入.frs文件夹

