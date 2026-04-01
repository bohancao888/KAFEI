import time
import os
import requests
import threading
import re
import random
lock = threading.Lock()
user_agent = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 12; HarmonyOS; MATE-XT-AL00; HMSCore 6.18.0.350) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.178 HuaweiBrowser/17.0.5.305 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; MATE-XT-AL00 Build/HUAWEIMATE-XT-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.186 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 16; SM-W9025 Build/AP3A.240905.015.A2) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/29.0 Chrome/136.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 16; SM-W9025) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 16; SM-W9025 Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.501.1080(0x28000346) Process/appbrand0 APM/Android/16 DeviceModel/SM-W9025 Brand/samsung NetType/WIFI Language/zh_CN',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/136.0.6878.186 Mobile/15E148 Safari/604.1'
        ]
try:
  os.mkdir('资产测活')
except Exception:
    print('文件夹创建失败！请检查目录中是否存在 资产测活 文件夹')
print('''\033[34m                                          
,--. ,--.   ,---.   ,------. ,------. ,--. 
|  .'   /  /  O  \  |  .---' |  .---' |  | 
|  .   '  |  .-.  | |  `--,  |  `--,  |  | 
|  |\   \ |  | |  | |  |`    |  `---. |  | 
`--' '--' `--' `--' `--'     `------' `--' \033[0m
\033[31m [*]KAFEI V1.0.1 一款多线程网络资产测活的小工具\033[0m
\033[31m [*]使用须知：请将需要被扫描的链接置于 /资产测活/资产链接.txt 文件中，程序将会自动运行，一行只能有一条链接!\033[0m''')

headers = {"User-Agent":random.choice(user_agent)}

def scan(url):
        try:
            response = requests.get(url,headers=headers,timeout=3)
            response.encoding = ('utf-8')
            try:
                print(f'\033[33m 时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 标题为: [{re.findall("<title>(.*?)</title>", response.text)[0]}] 页面长度为: [{len(response.text)}] 响应码为: [{response.status_code}] \033[0m')
                log = f'时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 标题为: [{re.findall("<title>(.*?)</title>", response.text)[0]}] 页面长度为: [{len(response.text)}] 响应码为: [{response.status_code}]\n'
                #time.sleep(1)
                try:
                    with open('资产测活/扫描结果.txt', 'a', encoding='utf-8') as file:
                        file.write(log)
                except Exception as e:
                    print(f'\033[31m 时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 出现这个问题: \033[0m' + str(e))
            except Exception as e:
                print(f'\033[31m 时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 出现这个问题:' + str(e) + + '可能没有匹配到title! \033[0m')
        except Exception:
            print(f'\033[31m 时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 超时，无法访问! \033[0m')

thread_list = []
with open('资产测活/资产链接.txt','r',encoding='utf-8') as f:
    f.seek(0)
    urls = f.read().splitlines()
    for url in urls:
        if url.strip():
            t = threading.Thread(target=scan, args=(url,))
            thread_list.append(t)
            t.start()

    for t in thread_list:
        t.join()









