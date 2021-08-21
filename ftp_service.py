"""
ftp服务
多线程并发
"""
from threading import Thread, ThreadError
from socket import *
import sys,os,time

HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)
path = '/home/mx/Python_VScode/File/'
#处理服务端各种请求
class FTPThread(Thread):
    def __init__(self,connect,addr):
        super().__init__()
        self.connect = connect
        self.addr = addr

    def do_list(self):
        #判断文件库是否为空
        file_list = os.listdir(path)
        if not file_list:
            self.connect.send(b'NO')
            return
        else:
            self.connect.send(b'YES')
            time.sleep(0.1)#防止 YES 和 列表消息粘连
            #发送文件列表，添加消息边界防止粘包
            data = '\n'.join(file_list)# 以\ n 作为消息边界
            self.connect.send(data.encode())

    def do_download(self,filename):
        try:
            f = open(path + filename,'rb')
        except:
            #文件不存在
            self.connect.send(b'NO')
            return
        else:
            self.connect.send(b'YES')
            time.sleep(0.1)
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.connect.send(b'##')
                    break
                self.connect.send(data)
            f.close()
    
    def do_upload(self,filename):
        if filename in os.listdir(path):
            self.connect.send(b'NO')
            return
        else:
            self.connect.send(b'YES')
            pp = path + filename
            f = open(pp,'wb')
            while True:
                data = self.connect.recv(1024)
                if data == b'##':
                    break
                f.write(data)
            f.close()







    def run(self):
        while True:
            data = self.connect.recv(1024).decode()
            if not data or data == 'E':#异常退出会返回空字符串，正常退出返回 E
                print('结束对：',self.addr,'的服务')
                return#函数结束即线程退出
            elif data == 'L':
                self.do_list()
            elif data[0] == 'D':
                filename = data.split(' ')[-1]
                self.do_download(filename)
            elif data[0] =='U':
                filename =data.split(' ')[-1]
                self.do_upload(filename)                
  
#网络并发结构搭建
def main():
    sock = socket()
    sock.bind(ADDR)
    sock.listen(3)
    print('listen the port 8888......')
    while True:
        try:
            connect,addr = sock.accept()
            print('客户端地址：',addr)
        except:
            sys.exit('服务退出')
        
        t = FTPThread(connect,addr)
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    main()