import os
import time
import requests
import paramiko

def send_tg_notification(text):
    token = os.getenv("bot_token")
    chat_id = os.getenv("chat_id")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        except Exception as e:
            print(f"Telegram 通知發送失敗: {e}")

def ptt_login_ssh():
    ptt_id_1 = os.getenv("ptt_id_1")
    if not ptt_id_1:
        print("未設定帳號")
        return
    
    username, password = ptt_id_1.split(",")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("正在透過 SSH 嘗試連線至 ptt.cc...")
        # 透過國外 IP 通常能直接連入 PTT SSH (Port 22)
        client.connect('ptt.cc', username='bbs', password='', timeout=15, allow_agent=False, look_for_keys=False)
        
        # 開啟互動式終端機
        chan = client.invoke_shell()
        time.sleep(3)
        
        # 讀取歡迎畫面
        content = chan.recv(9999).decode('big5', errors='ignore')
        
        if "請輸入代號" in content or "Login" in content:
            # 輸入帳號
            chan.send(f"{username}\r\n")
            time.sleep(2)
            
            # 輸入密碼
            chan.send(f"{password}\r\n")
            time.sleep(4)
            
            # 處理可能出現的重複登入或首頁公告，連續敲擊 Enter
            chan.send("\r\n")
            time.sleep(1)
            chan.send("\r\n")
            time.sleep(1)
            
            # 安全登出
            chan.send("g\r\n")
            time.sleep(1)
            chan.send("y\r\n")
            time.sleep(1)
            
            print("SSH 登入與登出程序執行完畢")
            send_tg_notification(f"✅ PTT 帳號 {username} 透過 SSH 自動登入成功！")
        else:
            print("無法辨識 PTT SSH 歡迎畫面")
            send_tg_notification("❌ PTT 自動登入失敗：無法辨識 SSH 歡迎畫面")
            
    except Exception as e:
        print(f"SSH 連線發生錯誤: {e}")
        send_tg_notification(f"❌ PTT SSH 自動登入失敗: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    ptt_login_ssh()
