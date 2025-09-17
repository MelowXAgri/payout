import requests
from config import Config
import json


class OKConnect:
    def __init__(self, member_id, signature):
        self.member_id = member_id
        self.signature = signature
    
    def get_mutasi(self):
        url = f"https://gateway.okeconnect.com/api/mutasi/qris/{self.member_id}/{self.signature}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

okconn = OKConnect(Config.OK_CONNECT_MEMBER_ID, Config.OK_CONNECT_SIGNATURE)

def get_mutasi(username: str, token: str):
    url = "https://orkut.ftvpn.me/api/mutasi"

    payload = {
        "auth_username": username,
        "auth_token": token
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # kalau HTTP error langsung raise
        return response.json()
    except Exception as e:
        print("❌ Error:", e)
        print("Raw response:", response.text if 'response' in locals() else "No response")
        return None


# contoh pemanggilan
if __name__ == "__main__":
    data = get_mutasi("windashop", "1130455:2KE4VHY31vaBi7mDIkf5qObWUMLu6gNl")
    if data:
        print(json.dumps(data, indent=4))
