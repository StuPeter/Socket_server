#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2019/2/22
# @Author  : 圈圈烃
# @File    : ali_server
# @Description:
#
#
from ProgressBar import ShowProcess
import socket
import struct
import threading
import hashlib
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 当前目录
HEAD_STRUCT = '128sIq32s'
BUFFER_SIZE = 1024


def cal_md5(file_path):
    with open(file_path, 'rb') as fr:
        md5 = hashlib.md5()
        md5.update(fr.read())
        md5 = md5.hexdigest()
        return md5


def unpack_file_info(file_info):
    file_name, file_name_len, file_size, md5 = struct.unpack(HEAD_STRUCT, file_info)
    file_name = file_name[:file_name_len]
    return file_name, file_name_len, file_size, md5


def socket_service():
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 这里value设置为1，表示将SO_REUSEADDR标记为TRUE，操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口，否则操作系统会保留几分钟该端口。
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_addr = ('', 8899)
        tcp_socket.bind(server_addr)
        tcp_socket.listen(5)
    except Exception as e:
        print(e)
        sys.exit(1)
    print("图片接收服务已开启，等待中......")

    while True:
        client_conn, client_addr = tcp_socket.accept()
        t = threading.Thread(target=deal_data, args=(client_conn, client_addr))
        t.start()


def deal_data(client_conn, client_addr):
    print("%s 连接成功" % str(client_addr))
    client_conn.send("你已经成功连接服务器！".encode("utf-8"))
    info_size = struct.calcsize(HEAD_STRUCT)
    file_info_package = client_conn.recv(info_size)
    file_name, file_name_len, file_size, md5_recv = unpack_file_info(file_info_package)
    recved_size = 0
    # 进度条类
    process_bar = ShowProcess(round(file_size / BUFFER_SIZE), 'OK')
    with open(file_name, 'wb') as fw:
        while recved_size < file_size:
            remained_size = file_size - recved_size
            if remained_size > BUFFER_SIZE:
                data_size = BUFFER_SIZE
            else:
                data_size = remained_size
            data_cache = client_conn.recv(data_size)
            recved_size += len(data_cache)  # 实际接收长度和设定的长度可能有出入
            fw.write(data_cache)
            # 显示进度条
            process_bar.show_process()
    # MD5计算校验
    md5 = cal_md5(file_name)
    print("原始md5：%s" % str(md5_recv.decode("utf-8")))
    print("当前md5：%s" % md5)
    if md5 != md5_recv.decode("utf-8"):
        print("MD5 校验失败!")
    else:
        print("MD5 校验成功!文件保存成功！")

    client_conn.close()


def main():
    socket_service()


if __name__ == '__main__':
    main()





