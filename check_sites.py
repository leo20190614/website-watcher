import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# === 配置 ===
IFTTT_EVENT_NAME = "website_update"
IFTTT_KEY = os.getenv("IFTTT_KEY")  # 从 GitHub Secrets 获取
HISTORY_FILE = "history.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def send_ifttt_notification(title, link):
    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/json/with/key/{IFTTT_KEY}"
    payload = {
        "value1": title,
        "value2": link,
        "value3": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    requests.post(url, json=payload)

def check_changi():
    url = "https://www.changiairport.com/en/corporate/our-media-hub/publications/reports.html"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    pdfs = soup.select("a[href$='.pdf']")
    reports = []
    for link in pdfs:
        title = link.get_text(strip=True)
        href = link["href"]
        full_url = "https://www.changiairport.com" + href
        reports.append((title, full_url))
    return reports

def check_ocbc():
    url = "https://www.ocbc.com/group/research/index"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    pdfs = soup.select("a[href$='.pdf']")
    reports = []
    for link in pdfs:
        title = link.get_text(strip=True)
        href = link["href"]
        full_url = "https://www.ocbc.com" + href
        reports.append((title, full_url))
    return reports

def main():
    history = load_history()
    new_found = False

    for site, fetch_func in [("changi", check_changi), ("ocbc", check_ocbc)]:
        entries = fetch_func()
        if site not in history:
            history[site] = []

        for title, link in entries:
            if link not in history[site]:
                print(f"✅ 新内容：{title}")
                send_ifttt_notification(f"{site.upper()} 有新报告", f"{title}\n{link}")
                history[site].append(link)
                new_found = True
            else:
                break

    if new_found:
        save_history(history)
    else:
        print("无新内容，无需通知")

if __name__ == "__main__":
    main()
