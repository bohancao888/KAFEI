import socket
import time
import threading

print_lock = threading.Lock() #锁线程（打印）

def scan_port(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #设置套接字
    s.settimeout(0.5) #设置延迟为500ms
    try:
        s.connect((ip,port))   #传入IP和端口号连接
        banner = ""
        try:
            banner = s.recv(1024).decode('utf-8', 'ignore').strip()
        except:
            pass

            # 没读到再发HTTP探测
        if not banner:
            try:
                s.send(b'HEAD / HTTP/1.1\r\nHost: a\r\n\r\n')
                banner = s.recv(1024).decode('utf-8', 'ignore').strip()
            except:
                banner = "未知服务"
        with print_lock:
            print(f'[*] 目标 {ip} 端口: {port} 开放 | [{banner[:30]}]')   #如果能连接成功，打印信息，这里用到了锁线程
            with open("result.txt", "a", encoding="utf-8") as f:
                f.write(f"端口开放： {ip}:{port} | [{banner[:30]}] \n")
    except:
        pass   #如果失败，则跳过
    s.close()

def main():
    ip = input("请输入目标IP: ")
    start = int(input('开始端口: '))
    end = int(input('结束端口: '))
    print(f"\n[*] 正在扫描 {ip} 的端口 {start} ~ {end}")

    thread_list = []

    max_thread = 500

    for port in range(start,end+1):
        while len(threading.enumerate()) >= max_thread:
            time.sleep(0.01)
        t = threading.Thread(target=scan_port,args=(ip,port))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

    print("\n[*] 扫描完成! ")

if __name__ == "__main__":
    main()




