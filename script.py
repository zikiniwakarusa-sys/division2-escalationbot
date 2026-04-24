import requests
import json
import os
from datetime import datetime, timedelta, timezone

DATA_URL = "https://hi-dep.github.io/division2/data/event/index.json"

CONFIG_FILE = "config.json"
STATE_FILE = "last.json"

JST = timezone(timedelta(hours=9))

# ------------------------
# 17時リセット対応の日付
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
# データ取得（完全修正版）
# ------------------------
def fetch_data():
    res = requests.get(DATA_URL)
    data = res.json()

    target_day = get_active_date()
    pairs = []

    for section_name, entries in data.items():
        for entry in entries:
            missions = entry.get("missions", [])

            # 日付一致のlootだけ取る
            target_loot = None
            for day_data in entry.get("target_loot_by_day", []):
                if day_data.get("day") == target_day:
                    target_loot = day_data.get("target_loot", [])
                    break

            # 一致しなければスキップ（←重要）
            if not target_loot:
                continue

            # ミッションと紐付け
            for i in range(min(len(missions), len(target_loot))):
                mission = missions[i]
                loot = target_loot[i]

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
        return  # ← 何も送らない

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
