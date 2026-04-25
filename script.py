import requests
import json
import os
from datetime import datetime, timedelta, timezone

DATA_URL = "https://hi-dep.github.io/division2/data/event/index.json"

CONFIG_FILE = "config.json"
STATE_FILE = "last.json"

JST = timezone(timedelta(hours=9))

# ------------------------
# ミッション日本語化
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
# loot日本語化
# ------------------------
LOOT_JA = {
    # 武器
    "assault rifle": "アサルトライフル",
    "rifle": "ライフル",
    "shotgun": "ショットガン",
    "smg": "サブマシンガン",
    "marksman rifle": "マークスマンライフル",
    "lmg": "ライトマシンガン",
    "pistol": "ピストル",

    # 防具
    "mask": "マスク",
    "chest": "ボディアーマー",
    "backpack": "バックパック",
    "gloves": "グローブ",
    "holster": "ホルスター",
    "kneepads": "ニーパッド",

    # ブランド
    "Alps Summit Armaments": "アルプスサミット・アーマメント",
    "Badger Tuff": "バッジャー・タフ",
    "Gila Guard": "ギラ・ガード",
    "Fenris Group AB": "フェンリスグループ社",
    "Providence Defense": "プロビデンスディフェンス",
    "Grupo Sombra S.A.": "グルーポソンブラ",
    "Ceska Vyroba s.r.o.": "チェスカ・ヴィーロバ社",
    "Douglas & Harding": "ダグラス＆ハーディング",
    "Wyvern Wear": "ワイバーンウェア",
    "China Light Industries": "チャイナライト",
    "Hana-U Corporation": "ハナウ",
    "Petrov Defense Group": "ペトロフディフェンス",
    "Overlord Armaments": "オーバーロード",
    "Sokolov Concern": "ソコロフ",
    "Murakami Industries": "ムラカミ",
    "Yaahl Gear": "ヤールギア",
    "System Corruption": "システムコラプション",
    "Future Initiative": "フューチャーイニシアティブ",
    "Foundry Bulwark": "ファウンドリーブルワーク",
    "Hunter's Fury": "ハンターズフューリー",
    "Heartbreaker": "ハートブレイカー",
    "Umbra Initiative": "アンブライニシアティブ",
    "Striker's Battlegear": "ストライカーバトルギア",
    "True Patriot": "トゥルーパトリオット",
    "Hard Wired": "ハードワイヤード",
    "Ongoing Directive": "オンゴーイングディレクティブ",
    "Eclipse Protocol": "エクリプスプロトコル",
    "Royal Works": "ロイヤルワークス",
    "Core Strength": "コア強度"
} 

def translate_loot(name):
    if not name:
        return ""

    key = name.strip().lower()

    if key in LOOT_JA:
        return LOOT_JA[key]

    if name in LOOT_JA:
        return LOOT_JA[name]

    return name

# ------------------------
# 17時リセット
# ------------------------
def get_active_datetime():
    now = datetime.now(JST)
    reset = now.replace(hour=17, minute=0, second=0, microsecond=0)

    if now < reset:
        now -= timedelta(days=1)

    return now

def format_jst(dt):
    return dt.strftime("%Y/%m/%d %H:%M JST")

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

    target_day = get_active_datetime().strftime("%Y-%m-%d")
    result = {}

    for section_name, entries in data.items():
        section_pairs = []

        for entry in entries:
            missions = entry.get("missions", [])

            target_loot = None
            for d in entry.get("target_loot_by_day", []):
                if d.get("day") == target_day:
                    target_loot = d.get("target_loot", [])
                    break

            if not target_loot:
                continue

            for i in range(min(len(missions), len(target_loot))):
                m = MISSION_JA.get(missions[i], missions[i])
                l = translate_loot(target_loot[i])

                if not l:
                    continue

                section_pairs.append((m, l))

        if section_pairs:
            result[section_name] = section_pairs

    return result

# ------------------------
# UI整形（ズレない）
# ------------------------
def format_section(title, pairs):
    lines = ["```"]

    for i, (m, l) in enumerate(pairs, 1):
        lines.append(f"[{i}] {m}")
        lines.append(f"    └ 🎯 {l}")
        lines.append("")

    lines.append("```")

    return {
        "name": f"🎯 {title}",
        "value": "\n".join(lines),
        "inline": False
    }

# ------------------------
# 投稿
# ------------------------
def post(webhook, sections):
    now = datetime.now(JST)
    active = get_active_datetime()

    if not sections:
        return

    embed = {
        "title": "🟧 Division2 エスカレーション",
        "description": "```diff\n+ ESCALATION TARGETED LOOT UPDATED\n```",
        "url": "https://hi-dep.github.io/division2/?view=event&lang=ja",
        "color": 0xFF6A00,
        "fields": [],
        "footer": {
            "text": f"更新: {format_jst(now)} / リセット: 毎日17:00 JST"
        }
    }

    for section, pairs in sections.items():
        embed["fields"].append(format_section(section, pairs))

    requests.post(webhook, json={"embeds": [embed]})

# ------------------------
# メイン
# ------------------------
def main():
    config = load_config()
    sections = fetch_data()

    current = {"sections": sections}
    last = load_last()

    if :
        for server in config["servers"]:
            post(server["webhook"], sections)

        save_last(current)
    else:
        print("変更なし or データなし")

if __name__ == "__main__":
    main()
