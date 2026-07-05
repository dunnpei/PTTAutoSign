import os
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
    # 這裡直接解析環境變數中的帳密
    ptt_id_1 = os.getenv("ptt_id_1")
    if not ptt_id_1:
        print("未設定帳號")
        return
    
    username, password = ptt_id_1.split(",")

    try:
        # 直接連線到 PTT 的 Telnet 埠口
        print("正在連線至 ptt.cc...")
        tn = telnetlib.Telnet("ptt.cc", 23, timeout=10)
        time.sleep(2)

        # 讀取歡迎畫面
        content = tn.read_very_eager().decode('big5', errors='ignore')
        
        # 輸入帳號
        if "請輸入代號" in content or "Login" in content or "guest" in content:
            tn.write(f"{username}\r\n".encode('big5'))
            time.sleep(2)
            
            # 輸入密碼
            tn.write(f"{password}\r\n".encode('big5'))
            time.sleep(3)
            
            # 處理重複登入或首頁通知（多按幾次 Enter 或者是大寫 G 離開）
            tn.write(b"\r\n")
            time.sleep(1)
            tn.write(b"\r\n")
            time.sleep(1)
            
            # 安全登出，維持良好習慣
            tn.write(b"g\r\n") # 離開安全步道
            tn.write(b"y\r\n") # 確定登出
            
            print("登入與登出程序執行完畢")
            send_tg_notification(f"✅ PTT 帳號 {username} 透過 Telnet 自動登入成功！")
        else:
            print("無法辨識 PTT 歡迎畫面")
            send_tg_notification("❌ PTT 自動登入失敗：無法辨識歡迎畫面")
            
        tn.close()
    except Exception as e:
        print(f"連線發生錯誤: {e}")
        send_tg_notification(f"❌ PTT 自動登入失敗: {e}")

if __name__ == "__main__":
    ptt_login_telnet()
