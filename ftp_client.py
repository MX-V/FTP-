"""
ftp客户端
c/s模式下，一般功能就是 发送请求，获取结果
"""
from socket import *
import time,sys
ADDR = ('127.0.0.1',8888)

class FTPClient:
    def __init__(self,sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b'L')
        data = self.sockfd.recv(128)#等待回复，yes/no
        if data.decode() == 'YES':
            #接收
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print('获取文件列表失败')

    def do_download(self,filename):
        data = 'D '+filename
        self.sockfd.send(data.encode())
        #等回复
        data = self.sockfd.recv(128)
        if data.decode() == 'YES':
            f = open(filename,'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':#文件接收完毕
                    break
                f.write(data)
            f.close()
        else:
            print('失败')
    
    def do_upload(self,filename):
        try:
            f = open(filename,'rb')
        except:
            print('该文件不存在')
            return
        filename = filename.split('/')[-1]
        data = 'U '+filename
        self.sockfd.send(data.encode())
        data = self.sockfd.recv(128).decode()
        if data == 'YES':
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print('失败,文件已存在')
            f.close()
    
    def do_quit(self):
        self.sockfd.send(b'E')
        self.sockfd.close()
        sys.exit('谢谢使用')




    

#连接服务端
def main():
    s = socket()
    s.connect(ADDR)
    ftp = FTPClient(s)
    while True:
        print('================命令选项============')
        print('===              list           ===')
        print('===             upload          ===')
        print('===            download         ===')
        print('===              quit           ===')
        print('===================================')

        cmd = input('请输入命令：')
        if cmd == 'list':
            ftp.do_list()
        elif cmd[:8] == 'download':
            filename = cmd.split(' ')[-1]
            ftp.do_download(filename)
        elif cmd[:6] == 'upload':
            filename = cmd.split(' ')[-1]
            ftp.do_upload(filename)
        elif cmd == 'quit':
            ftp.do_quit()
        else:
            print('请输入正确命令')

if __name__ == '__main__':
    main()
