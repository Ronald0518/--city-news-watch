import requests
from bs4 import BeautifulSoup
from sheets_writer import get_sheet

def detect_selectors(url):
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 找一個包含最多連結的容器
    candidates = soup.select("ul, ol, div")
    container = max(candidates, key=lambda c: len(c.find_all("a")), default=None)

    if not container:
        return None

    # 預設值
    list_selector = container.name
    if container.get("class"):
        list_selector += "." + container.get("class")[0]
    if container.name in ["ul", "ol"]:
        list_selector += " li"

    return {
        "list_selector": list_selector,
        "title_selector": "a",
        "link_attr": "href"
    }

def auto_fill():
    sheet = get_sheet("city-news-db")  # 你的 Sheet 名稱
    rows = sheet.get_all_values()

    # 第一列是標題，所以從第二列開始
    for i in range(2, len(rows) + 1):
        list_sel, title_sel, link_attr = rows[i-1][3:6]  # D:E:F 欄
        if not list_sel:  # 如果還沒填
            url = rows[i-1][2]  # 首頁網址在 C 欄
            selectors = detect_selectors(url)
            if selectors:
                sheet.update(f"D{i}", selectors["list_selector"])
                sheet.update(f"E{i}", selectors["title_selector"])
                sheet.update(f"F{i}", selectors["link_attr"])
                print(f"✅ 已補齊：{rows[i-1][1]}")

if __name__ == "__main__":
    auto_fill()