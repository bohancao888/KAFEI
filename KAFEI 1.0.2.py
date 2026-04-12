import threading  #多线程
import sys     #强退
import random  #随机选user-agent
import socket   #扫描端口
import requests #链接测活、查询
import json #备案查询
import base64
import mmh3
import re
import time
import urllib3

port_scan_list = set()
scan_lock = threading.Lock()
urllib3.disable_warnings()
print_lock = threading.Lock()  # 另外一个线程锁
subdomain_list = set()  #定义一个序列装载子域名
submain_list_ip = [] #定义一个集合装载子域名的IP

print('''\033[34m                                          
,--. ,--.   ,---.   ,------. ,------. ,--. 
|  .'   /  /  O  \  |  .---' |  .---' |  | 
|  .   '  |  .-.  | |  `--,  |  `--,  |  | 
|  |\   \ |  | |  | |  |`    |  `---. |  | 
`--' '--' `--' `--' `--'     `------' `--' \033[0m

\033[36m        KAFEI V1.0.2 『今昔是何年』\033[0m
\033[36m       心不死则道不生，欲不灭则道不存\033[0m
\033[36m      心不苦则智慧不开，身不苦则福禄不厚\033[0m\n
\033[36m                                  ——王阳明\033[0m
''')

#user-agent库，每次请求随机选一条、顺便凑个行数
user_agent = [
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 12; HarmonyOS; MATE-XT-AL00; HMSCore 6.18.0.350) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.178 HuaweiBrowser/17.0.5.305 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; MATE-XT-AL00 Build/HUAWEIMATE-XT-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.186 Mobile Safari/537.36',
        'Mozilla/5.0w (Linux; Android 16; SM-W9025 Build/AP3A.240905.015.A2) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/29.0 Chrome/136.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 16; SM-W9025) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 16; SM-W9025 Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/136.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.501.1080(0x28000346) Process/appbrand0 APM/Android/16 DeviceModel/SM-W9025 Brand/samsung NetType/WIFI Language/zh_CN',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/136.0.6878.186 Mobile/15E148 Safari/604.1'
]

symbols = {'!','@','#','$','%','^','&','*','(',')','-','_','=',
'+','[',']','{','}',';',':','"',"'",'<','>','/','?','`','~','|','\\'}

def input_content_ok(a):   #检查输入是否存在问题
    for char in a:
        if char in symbols:
            print('\033[31m[*]输入错误，请重新输入！输入错误超三次后自动退出！\033[0m')
            return False
    return True

def get_headers():
    return {
        "User-Agent": random.choice(user_agent),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

def get_domain_ip(domain):    #解析域名IP
    try:
        domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
        ip = socket.gethostbyname(domain)
        # print(f"\033[32m[*]域名{domain} 解析IP为：{ip}\033[0m")
        return ip
    except:
        print(f'\033[31m[*]域名{domain} 解析失败！\033[0m')
        return None


def cehuo(url):   #调用链接测活，这里可以是ip地址，也可以是域名
    try:
        response = requests.get(url,headers=get_headers(),timeout=3)
        response.encoding = 'utf-8'
        try:
            title = re.findall("<title>(.*?)</title>", response.text)[0]
        except:
            title = "未匹配到标题"
        print(f'\033[33m[*]时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 标题为: [{title}] 页面长度为: [{len(response.text)}] 响应码为: [{response.status_code}] \033[0m')
        log = f'时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 标题为: [{title}] 页面长度为: [{len(response.text)}] 响应码为: [{response.status_code}]\n'
        # time.sleep(1)
        try:
            with open('扫描结果.txt', 'a', encoding='utf-8') as file:
                file.write(log)
        except Exception as e:
            print(f'\033[31m[*]时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 使用扫描结果.txt文件出现这个问题:{str(e)} \033[0m')
    except Exception:
        print(f'\033[31m[*]时间: [{time.strftime("%Y-%m-%d %H:%M:%S")}] 链接 [{url}] 超时，无法访问! \033[0m')

def beian(domain):  #查询备案
    try:
        url = 'https://www.huodaidaohang.cn/commontools/php/apihz.php?action=icp-query&domain=' + domain
        response = requests.get(url,headers=get_headers(),timeout=3)
        data = json.loads(response.text)
    except:
        print("\n\033[31m[*] 查询失败：网络错误或接口异常！\033[0m")
        return
    if data.get("code") == 200:
        print("\n======== 域名备案查询结果 ========")
        print(f"[*]主办单位：{data.get('unit', '无')}")
        print(f"[*]单位类型：{data.get('type', '无')}")
        print(f"[*]备案域名：{data.get('domain', '无')}")
        print(f"[*]ICP备案号：{data.get('icp', '无')}")
        print(f"[*]审核时间：{data.get('time', '无')}")
        print("===============================\n")
    else:
        print(f"\033[33m[*]查询结果：{data.get('msg', '未查询到备案信息')} \033[0m")

def subdomain_find(domain):    #子域名爆破
    # print(f'\033[33m[*]开始对{domain}进行子域名爆破... \033[0m')
    try:
        with open('17w_subdomain.txt', 'r', encoding='utf-8') as f:
            f.seek(0)
            submins = f.read().splitlines()
            for submin in submins:
                son_domain = f'{submin}.{domain}'
                request_son_domain = f'https://{submin}.{domain}'
                if son_domain in subdomain_list:
                    continue
                subdomain_list.add(son_domain)
                try:
                    response = requests.get(request_son_domain, headers=get_headers(), timeout=3)
                    if response.status_code == 200:
                        subdomain_ip = get_domain_ip(son_domain)
                        if subdomain_ip:
                            with print_lock:
                                print(f'\033[32m[*]子域名 {son_domain} 存在! 解析IP为 {subdomain_ip} \033[0m')
                                cehuo(request_son_domain)
                                submain_list_ip.append({
                                'subdomain': request_son_domain,
                                'ip': subdomain_ip
                                })
                except:
                    continue
    except Exception as e:
        print(f'\033[31m[*]存在这个问题:{str(e)} \033[0m')


def port_scan(ip):             #TOP1000扫描
    # print(f'\033[34m[*]开始对IP:{ip}进行TOP1000端口扫描\033[0m')
    port_list = '''7,9,11,13,17,19,21,22,23,26,37,38,43,49,51,53,67,69,70,79,80,81,82,83,84,85,86,88,89,102,104,111,113,119,121,123,135,137,138,139,143,161,175,179,199,211,264,311,389,443,444,445,465,500,502,503,512,515,520,548,554,564,587,623,631,636,646,666,771,777,789,800,801,808,853,873,880,888,902,992,993,995,999,1000,1022,1023,1024,1025,1026,1027,1080,1099,1177,1194,1200,1201,1234,1241,1248,1260,1290,1311,1344,1400,1433,1443,1471,1494,1515,1521,1554,1588,1701,1720,1723,1741,1777,1863,1883,1900,1911,1935,1962,1967,1991,2000,2001,2002,2020,2022,2030,2031,2049,2052,2053,2077,2080,2082,2083,2086,2087,2095,2096,2121,2123,2152,2181,2222,2223,2252,2323,2332,2375,2376,2379,2401,2404,2424,2427,2443,2455,2480,2501,2601,2628,3000,3001,3002,3006,3128,3260,3283,3288,3299,3306,3307,3310,3333,3388,3389,3390,3443,3460,3541,3542,3689,3690,3749,3780,4000,4022,4040,4063,4064,4111,4343,4369,4430,4433,4443,4444,4500,4505,4567,4664,4712,4730,4782,4786,4840,4848,4880,4911,4949,5000,5001,5002,5004,5005,5006,5007,5009,5050,5060,5084,5222,5258,5269,5351,5353,5357,5400,5432,5443,5500,5554,5555,5556,5560,5577,5601,5631,5672,5678,5683,5800,5801,5900,5901,5902,5903,5938,5984,5985,5986,6000,6001,6002,6003,6005,6006,6050,6060,6068,6110,6363,6379,6443,6488,6560,6565,6581,6588,6590,6600,6664,6665,6666,6667,6668,6669,6699,6881,6998,7000,7001,7002,7003,7005,7006,7010,7014,7025,7070,7071,7077,7080,7170,7288,7306,7307,7312,7401,7443,7474,7493,7537,7547,7548,7634,7657,7777,7779,7788,7911,8000,8001,8002,8003,8004,8006,8008,8009,8010,8015,8020,8025,8030,8040,8060,8069,8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090,8091,8092,8093,8094,8095,8096,8097,8098,8099,8111,8112,8118,8123,8125,8126,8139,8159,8161,8180,8181,8182,8200,8222,8291,8333,8334,8377,8378,8388,8443,8500,8545,8546,8554,8649,8686,8800,8834,8880,8883,8887,8888,8889,8899,8983,8999,9000,9001,9002,9003,9009,9010,9030,9042,9050,9051,9080,9083,9090,9091,9100,9151,9191,9200,9295,9333,9418,9443,9444,9527,9530,9595,9600,9653,9700,9711,9869,9944,9981,9997,9999,10000,10001,10003,10162,10243,10333,10443,10554,11001,11211,11300,11310,12300,12345,13579,14000,14147,14265,16010,16030,16992,16993,17000,18000,18001,18080,18081,18245,18246,19999,20000,20547,20880,22105,22222,23023,23424,25000,25105,25565,27015,27017,28017,28080,29876,30001,32400,33338,33890,37215,37777,41795,45554,49151,49152,49153,49154,49155,50000,50050,50070,50100,51106,52869,55442,55553,55555,60001,60010,60030,60443,61613,61616,62078,64738,8848'''
    for port in port_list.split(','):
        port = int(port.replace('\n', ''))
        if port in port_scan_list:
            continue
        port_scan_list.add(port)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect((ip, port))
            s.close()
            with scan_lock:
                print(f'\033[32m[*]端口:{port} ON\033[0m')
        except:
            pass


def ico_hash(url):   #ICO hash计算   FOFA
    try:
        response = requests.get(url,headers=get_headers(),timeout=3)
        icon = re.findall('href="(.*?\.ico)"', response.text)[0]
        if icon.startswith('/'):
            icon = icon[1:]
        host = re.findall('(https?://.*?/)', response.request.url)[0]
        icon_url = host + icon
        icon_response = requests.get(icon_url)
        print(f'\033[33m[*]FOFA语法: icon_hash="{mmh3.hash(base64.b64encode(icon_response.content))}"\033[0m')
    except:
        print(f'\033[31m[*]{url} 源码中未找到ICO文件! \033[0m')


def main():           #程序主函数
    global subdomain_list
    global submain_list_ip
    global port_scan_list
    input_number = 0
    port_scan_thread_list = []
    subdomain_find_thread_list = []
    while True:
        domain = input("\033[35m[*]请输入需要被扫描的域名(例如:baidu.com、apple.com):\033[0m ")
        if input_content_ok(domain) == False:
            input_number +=1
            print('\033[31m[*]请再次输入！\033[0m')

            if input_number >= 3:
                print("\033[31m[*]输入错误3次，程序退出！\033[0m")
                sys.exit(0)  # 强退
        else:
            break
    program_thread = int(input('\033[34m[*]请输入线程 (如：50、100、200)：\033[0m'))
    beian(domain)  #备案查询
    time.sleep(0.1)
    cehuo('https://' +domain)  #链接测活
    time.sleep(0.1)
    ico_hash('https://' + domain) #ico图标查询、hash计算
    time.sleep(0.1)
    ip = get_domain_ip(domain)
    print(f'\033[34m[*]开始对IP:{ip}进行TOP1000端口扫描\033[0m')
    for th in range(program_thread):
        t = threading.Thread(target=port_scan,args=(ip,))  #对IP进行TOP1000端口扫描
        port_scan_thread_list.append(t)
        t.start()
    for t in port_scan_thread_list:
        t.join()
    time.sleep(0.1)
    print(f'\033[33m[*]开始对{domain}进行子域名爆破... \033[0m')
    for th in range(program_thread):
        t = threading.Thread(target=subdomain_find, args=(domain,))  #子域名爆破
        subdomain_find_thread_list.append(t)
        t.start()
    for t in subdomain_find_thread_list:
        t.join()
    time.sleep(0.1)
    if not submain_list_ip:
        print("\033[31m[*]未找到可用子域名! \033[0m")
        print('\033[31m[*]扫描结束! \033[0m')
        return
    seen_ip = set()
    submain_list_ip = [item for item in submain_list_ip if not (item['ip'] in seen_ip or seen_ip.add(item['ip']))]
    for item in submain_list_ip:
        sub = item['subdomain']
        ip = item['ip']
        print(f"\033[*]子域名:({sub}) IP:({ip}) \033[0m ")
        print(f"\033[34m[*]正在扫描子域名IP: {ip}\033[0m ")
        port_scan_list.clear()
        threads = []
        for th in range(program_thread):
            t = threading.Thread(target=port_scan, args=(ip,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    print('\033[33m[*]扫描完成！感谢使用！\033[0m')


main()