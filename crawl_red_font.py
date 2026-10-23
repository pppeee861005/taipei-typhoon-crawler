"""
爬蟲實戰手感：抓取人事行政總處最新公告
目標：鎖定「臺北市」，並精準抓取明天是否上班上課的狀態（紅字判定）
"""

import requests
import urllib3
from bs4 import BeautifulSoup

# 關閉 SSL 驗證警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "https://www.dgpa.gov.tw/typh/daily/nds.html"

def check_taipei_status():
    print("=" * 65)
    print("🕸️  連線至行政院人事行政總處（DGPA）即時查詢中...")
    print("=" * 65)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # verify=False 避免政府網站常見的 SSL 憑證檢查失敗
        response = requests.get(TARGET_URL, headers=headers, timeout=15, verify=False)
        html_content = response.content.decode("utf-8")
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        return

    soup = BeautifulSoup(html_content, "html.parser")

    # 1. 抓取網頁上的最新更新時間
    update_time = "未知"
    for div in soup.find_all("div"):
        if "更新時間" in div.text:
            update_time = div.text.strip().replace("\n", " ")
            break
    print(f"🕒 官方資訊時間：{update_time}\n")

    # 2. 像相親挑選一樣：在所有表格列 <tr> 中，鎖定第一欄是「臺北市」的那一列！
    taipei_tr = None
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2:
            first_col_text = tds[0].get_text(strip=True)
            if "臺北市" in first_col_text or "台北市" in first_col_text:
                taipei_tr = tr
                break  # 找到了立刻登記結婚，結束搜尋！

    if not taipei_tr:
        print("⚠️ 未在表格中找到臺北市的公告項目。")
        return

    tds = taipei_tr.find_all("td")
    city_name = tds[0].get_text(strip=True)
    status_td = tds[1]  # 狀態欄位

    # 3. 提取文字與紅字標籤
    full_status_text = status_td.get_text(separator=" ", strip=True)
    red_tags = status_td.find_all(["font", "span"], color=["#FF0000", "#ff0000", "red"])

    print(f"🏙️  目標縣市：【{city_name}】")
    print(f"📋 完整公告內容：{full_status_text}")
    print("-" * 65)

    # 4. 判斷明天狀態
    if "明天已達停止上班及上課標準" in full_status_text or any("停止上班" in t.text for t in red_tags):
        print("🚨 【判定結果】：明天（10/24）停止上班、停止上課！ (放颱風假)")
    elif "照常上班、照常上課" in full_status_text:
        print("💼 【判定結果】：明天（10/24）照常上班、照常上課。")
    else:
        print(f"ℹ️ 【判定結果】：{full_status_text}")

    print("=" * 65)

if __name__ == "__main__":
    check_taipei_status()
