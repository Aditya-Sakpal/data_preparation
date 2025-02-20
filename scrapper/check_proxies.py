import requests
import queue
import threading

q=queue.Queue()
valid_proxies = []

with open("proxy_list.txt", "r") as f:
    proxies = f.readlines()
    for proxy in proxies:
        q.put(proxy.strip())

def check_proxy():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            response = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
            if response.status_code == 200:
                valid_proxies.append(proxy)
                
                with open("valid_proxies.txt", "a") as f:
                    f.write(proxy + "\n")
                
                print(f"Valid proxy: {proxy}")
        except Exception as e:
            print(f"Invalid proxy: {proxy}")
            continue
        
for _ in range(10):
    t = threading.Thread(target=check_proxy)
    t.start()