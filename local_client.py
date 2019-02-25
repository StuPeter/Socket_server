#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2019/2/22
# @Author  : 圈圈烃
# @File    : local_client
# @Description:
#
#
import socket
import struct
import hashlib
import sys
import os
from ProgressBar import ShowProcess


BUFFER_SIZE = 1024
HEAD_STRUCT = '128sIq32s'


def cal_md5(file_path):
    with open(file_path, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


def get_file_info(file_path):
    file_name = os.path.basename(file_path)
    file_name_len = len(file_name)
    file_size = os.stat(file_path).st_size
    md5 = cal_md5(file_path)
    return file_name, file_name_len, file_size, md5


def socket_client(path):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = ('127.0.0.1', 8899)
        tcp_socket.connect(server_addr)
        print("连接服务器，准备上传......")
    except Exception as e:
        print(e)
        sys.exit(1)

    print(tcp_socket.recv(1024).decode("utf-8"))

    if os.path.isfile(path):
        file_name, file_name_len, file_size, md5 = get_file_info(path)
        # 定义文件头信息，包含文件名和文件大小
        filehead = struct.pack(HEAD_STRUCT, file_name.encode('utf-8'), file_name_len, file_size, md5.encode('utf-8'))
        tcp_socket.send(filehead)
        sent_size = 0
        # 进度条类
        process_bar = ShowProcess(round(file_size/BUFFER_SIZE), 'OK')

        with open(path, 'rb') as fr:

            while sent_size < file_size:
                # 传输文件
                remain_size = file_size - sent_size
                if remain_size > BUFFER_SIZE:
                    data_size = BUFFER_SIZE
                else:
                    data_size = remain_size
                data_cache = fr.read(data_size)
                sent_size += data_size
                tcp_socket.send(data_cache)
                # 显示进度条
                process_bar.show_process()
            print("%s 文件传输完毕！" % path)
        print('上传成功！连接关闭')


def main():
    path = "d:\\Users\\Administrator\\Downloads\\会声会影X8\\x8-64.exe"
    socket_client(path)


if __name__ == '__main__':
    main()
