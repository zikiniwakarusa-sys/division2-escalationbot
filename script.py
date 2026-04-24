import requests
import json
import os
from datetime import datetime, timedelta, timezone

DATA_URL = "https://hi-dep.github.io/division2/data/event/index.json"

CONFIG_FILE = "config.json"
STATE_FILE = "last.json"

JST = timezone(timedelta(hours=9))

# ------------------------
# ミッション日本語化（event.jsから抜粋）
# ------------------------
MISSION_JA = {
    "Grand Washington Hotel": "グランドワシントンホテル",
    "ViewPoint Museum": "ビューポイント博物館",
    "American History Museum": "アメリカ歴史博物館",
    "Air & Space Museum": "航空宇宙博物館",
    "Jefferson Plaza": "ジェファーソンプラザ",
    "Bank Headquarters": "銀行本部",
    "DCD Headquarters": "DCD本部",
    "Lincoln Memorial": "リンカーン記念堂",
    "Potomac Event Center": "ポトマックイベントセンター",
    "Jefferson Trade Center": "ジェファーソントレードセンター",
    "Space Administration HQ": "宇宙局本部",
    "Federal Emergency Bunker": "フェデラルエマージェンシーバンカー",
    "Camp White Oak": "キャンプホワイトオーク",
    "The Pentagon": "ペンタゴン",
    "DARPA Research Labs": "DARPA",
    "Coney Island Ballpark": "コニーアイランド球場",
    "Coney Island Amusement Park": "コニーアイランド遊園地",
    "The Tombs": "墓所",
    "Stranded Tanker": "座礁タンカー",
    "Pathway Park": "パスウェイパーク",
    "Wall Street": "ウォール街",
    "Liberty Island": "リバティ島",
    "CERA Clinic": "CERA診療所",
    "DUMBO Skate Park": "ダンボ・スケートパーク",
    "H5 Refinery": "H5精製所",
    "Clarke Street Hotel": "クラーク・ストリート",
    "Bridge Park Pier": "ブリッジパーク埠頭",
    "The Art Museum": "美術館",
    "Army Terminal": "陸軍ターミナル",
    "District Union Arena": "ディストリクトユニオンアリーナ",
    "Roosevelt Island": "ルーズベルト島",
    "Capitol Building": "キャピトルビル",
    "Tidal Basin": "タイダルベイスン",
    "Manning National Zoo": "マニング国立動物園",
}

# ------------------------
# 17時リセット
# ------------------------
def get_active_date():
    now = datetime.now(JST)
    reset = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < reset:
        now -= timedelta(days=1)

    return now.strftime("%Y-%m-%d")

# ------------------------
def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def load_last():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_last(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

# ------------------------
# データ取得
# ------------------------
def fetch_data():
    res = requests.get(DATA_URL)
    data = res.json()

    target_day = get_active_date()
    pairs = []

    for section_name, entries in data.items():
        for entry in entries:
            missions = entry.get("missions", [])

            target_loot = None
            for day_data in entry.get("target_loot_by_day", []):
                if day_data.get("day") == target_day:
                    target_loot = day_data.get("target_loot", [])
                    break

            if not target_loot:
                continue

            for i in range(min(len(missions), len(target_loot))):
                mission = missions[i]
                loot = target_loot[i]

                # 日本語化
                mission = MISSION_JA.get(mission, mission)

                if not loot:
                    continue

                pairs.append({
                    "mission": mission,
                    "loot": loot
                })

    return pairs[:10]

# ------------------------
# 投稿
# ------------------------
def post(webhook, pairs):
    now = get_active_date()

    if not pairs:
        return

    description = ""
    for i, p in enumerate(pairs, 1):
        description += f"{i}. {p['mission']} → {p['loot']}\n"

    embed = {
        "title": "🎯 Division2 デイリー情報",
        "description": description,
        "url": "https://hi-dep.github.io/division2/?view=event&lang=ja",
        "color": 16753920,
        "footer": {
            "text": f"更新日: {now}"
        }
    }

    requests.post(webhook, json={"embeds": [embed]})

# ------------------------
# メイン
# ------------------------
def main():
    config = load_config()
    pairs = fetch_data()

    current = {"pairs": pairs}
    last = load_last()

    if current != last and pairs:
        for server in config["servers"]:
            post(server["webhook"], pairs)

        save_last(current)
    else:
        print("変更なし or データなし")

if __name__ == "__main__":
    main()
