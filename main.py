import os
import socks
import socket
import telnetlib
import time
import requests

def send_tg_notification(text):
    token = os.getenv("bot_token")
    chat_id = os.getenv("chat_id")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": text})

def ptt_login_telnet():
    ptt_id_1 = os.getenv("ptt_id_1")
    if not ptt_id_1:
        print("未設定帳號")
        return
    
    username, password = ptt_id_1.split(",")

    try:
        print("正在設定台灣/動態 Proxy 代理...")
        # 這裡設定一個常見的台灣/亞洲區公開 Socks5 代理（若此 IP 失效，可更換其他免費 Socks5）
        # 註：如果連線依然失敗，代表該免費代理掛了，需更換 proxy_ip
        proxy_ip = "114.35.138.9"  # 台灣中部電信寬頻 IP 範例
        proxy_port = 1080
        
        # 強制將全域的 socket 連線轉向 Proxy
        socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port)
        socket.socket = socks.socksocket

        print(f"正在透過代理 {proxy_ip} 連線至 ptt.cc...")
        tn = telnetlib.Telnet("ptt.cc", 23, timeout=15)
        time.sleep(3)

        # 讀取歡迎畫面
        content = tn.read_very_eager().decode('big5', errors='ignore')
        
        # 輸入帳號
        if "請輸入代號" in content or "Login" in content or "guest" in content:
            tn.write(f"{username}\r\n".encode('big5'))
            time.sleep(2)
            
            # 輸入密碼
            tn.write(f"{password}\r\n".encode('big5'))
            time.sleep(3)
            
            # 處理重複登入或首頁通知
            tn.write(b"\r\n")
            time.sleep(1)
            tn.write(b"\r\n")
            time.sleep(1)
            
            # 安全登出
            tn.write(b"g\r\n") 
            tn.write(b"y\r\n") 
            
            print("登入與登出程序執行完畢")
            send_tg_notification(f"✅ PTT 帳號 {username} 已成功偽裝台灣 IP 登入！")
        else:
            print("無法辨識 PTT 歡迎畫面")
            send_tg_notification("❌ PTT 自動登入失敗：無法辨識歡迎畫面（可能代理伺服器速度過慢）")
            
        tn.close()
    except Exception as e:
        print(f"連線發生錯誤: {e}")
        send_tg_notification(f"❌ PTT 自動登入失敗: {e}")

if __name__ == "__main__":
    ptt_login_telnet()
