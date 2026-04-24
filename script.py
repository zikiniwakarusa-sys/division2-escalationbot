import requests
import json
import os
from datetime import datetime, timedelta, timezone

DATA_URL = "https://hi-dep.github.io/division2/data/event/index.json"

CONFIG_FILE = "config.json"
STATE_FILE = "last.json"

# JST
JST = timezone(timedelta(hours=9))

def today_jst():
    return datetime.now(JST).strftime("%Y-%m-%d")

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

def fetch_data():
    res = requests.get(DATA_URL)
    data = res.json()

    today = today_jst()

    items = []
    missions = []

    for section_name, entries in data.items():
        for entry in entries:
            # ミッション
            missions.extend(entry.get("missions", []))

            # その日のターゲット装備
            for day_data in entry.get("target_loot_by_day", []):
                if day_data.get("day") == today:
                    items.extend(day_data.get("target_loot", []))

    return items[:10], missions[:10]

def post(webhook, items, missions):
    now = today_jst()

    embed = {
        "title": "🎯 Division2 デイリー情報",
        "url": "https://hi-dep.github.io/division2/?view=event&lang=ja",
        "color": 16753920,
        "fields": [
            {
                "name": "📦 目標アイテム",
                "value": "\n".join([f"{i+1}. {v}" for i, v in enumerate(items)]) or "なし",
                "inline": False
            },
            {
                "name": "🗺️ ミッション",
                "value": "\n".join([f"{i+1}. {v}" for i, v in enumerate(missions)]) or "なし",
                "inline": False
            }
        ],
        "footer": {
            "text": f"更新日: {now}"
        }
    }

    requests.post(webhook, json={"embeds": [embed]})

def main():
    config = load_config()
    items, missions = fetch_data()

    current = {"items": items, "missions": missions}
    last = load_last()

    if current != last:
        for server in config["servers"]:
            post(server["webhook"], items, missions)
        save_last(current)
    else:
        print("変更なし")

if __name__ == "__main__":
    main()
