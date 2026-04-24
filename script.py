import requests
import json
import os
import re
from datetime import datetime, timedelta, timezone

DATA_URL = "https://hi-dep.github.io/division2/data/event/index.json"
I18N_CATEGORIES = "https://hi-dep.github.io/division2/data/i18n/categories.json"
I18N_ALIASES = "https://hi-dep.github.io/division2/data/i18n/aliases.json"

CONFIG_FILE = "config.json"
STATE_FILE = "last.json"

JST = timezone(timedelta(hours=9))

# ------------------------
# ミッション日本語
# ------------------------
MISSION_JA = {
    "The Art Museum": "美術館",
    "Grand Washington Hotel": "グランドワシントンホテル",
    "American History Museum": "アメリカ歴史博物館",
}

# ------------------------
# 初期化（i18n取得）
# ------------------------
def load_i18n():
    categories = requests.get(I18N_CATEGORIES).json()
    aliases = requests.get(I18N_ALIASES).json()
    return categories, aliases

I18N_CAT, I18N_ALIAS = load_i18n()

# ------------------------
# normalizeKey（JS再現）
# ------------------------
def normalize_key(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())

# ------------------------
# targetlootキー解決
# ------------------------
def resolve_key(name):
    key = normalize_key(name)
    return I18N_ALIAS.get(key, key)

# ------------------------
# 日本語変換
# ------------------------
def translate_loot(name):
    key = resolve_key(name)

    # weapon
    if key in I18N_CAT.get("weapon_type", {}):
        return I18N_CAT["weapon_type"][key]

    # gear
    if key in I18N_CAT.get("gear_slot", {}):
        return I18N_CAT["gear_slot"][key]

    # brand
    if key in I18N_CAT.get("brands", {}):
        return I18N_CAT["brands"][key]

    return name  # fallback

# ------------------------
# 17時リセット
# ------------------------
def get_active_date():
    now = datetime.now(JST)
    reset = now.replace(hour=17, minute=0)

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
    data = requests.get(DATA_URL).json()
    target_day = get_active_date()

    pairs = []

    for section, entries in data.items():
        for entry in entries:
            missions = entry.get("missions", [])

            loot = None
            for d in entry.get("target_loot_by_day", []):
                if d.get("day") == target_day:
                    loot = d.get("target_loot", [])
                    break

            if not loot:
                continue

            for i in range(min(len(missions), len(loot))):
                mission = missions[i]
                item = loot[i]

                mission = MISSION_JA.get(mission, mission)
                item = translate_loot(item)

                if not item:
                    continue

                pairs.append({
                    "mission": mission,
                    "loot": item
                })

    return pairs[:10]

# ------------------------
# 投稿
# ------------------------
def post(webhook, pairs):
    if not pairs:
        return

    desc = ""
    for i, p in enumerate(pairs, 1):
        desc += f"{i}. {p['mission']} → {p['loot']}\n"

    embed = {
        "title": "🎯 Division2 デイリー情報",
        "description": desc,
        "url": "https://hi-dep.github.io/division2/?view=event&lang=ja",
        "color": 16753920
    }

    requests.post(webhook, json={"embeds": [embed]})

# ------------------------
def main():
    config = load_config()
    pairs = fetch_data()

    current = {"pairs": pairs}
    last = load_last()

    if current != last:
        for s in config["servers"]:
            post(s["webhook"], pairs)
        save_last(current)

if __name__ == "__main__":
    main()
