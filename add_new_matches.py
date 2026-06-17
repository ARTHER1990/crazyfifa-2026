import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db
import pandas as pd

# ดึงข้อมูล worksheet
ws = db.get_worksheet('matches')
data = ws.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# ตารางคู่ใหม่ที่จะเพิ่มสำหรับวันที่ 19 และ 20 มิถุนายน 2026
# (ต่อจาก ID 24)
new_matches = [
    # วันที่ 19 มิถุนายน 2026 (June 19, 2026)
    {
        'id': '25',
        'home_team': 'USA',
        'away_team': 'Australia',
        'match_time': '2026-06-19 02:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '26',
        'home_team': 'Scotland',
        'away_team': 'Morocco',
        'match_time': '2026-06-19 05:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '27',
        'home_team': 'Brazil',
        'away_team': 'Haiti',
        'match_time': '2026-06-19 08:30:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    # วันที่ 20 มิถุนายน 2026 (June 20, 2026)
    {
        'id': '28',
        'home_team': 'Netherlands',
        'away_team': 'Sweden',
        'match_time': '2026-06-20 01:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '29',
        'home_team': 'Germany',
        'away_team': 'Ivory Coast',
        'match_time': '2026-06-20 03:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '30',
        'home_team': 'Ecuador',
        'away_team': 'Curaçao',
        'match_time': '2026-06-20 07:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '31',
        'home_team': 'Tunisia',
        'away_team': 'Japan',
        'match_time': '2026-06-20 09:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    }
]

added_count = 0
for match in new_matches:
    if str(match['id']) not in df['id'].astype(str).values:
        df = pd.concat([df, pd.DataFrame([match])], ignore_index=True)
        added_count += 1

if added_count > 0:
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.astype(str).values.tolist())
    print(f"✅ เพิ่มตารางการแข่งขันใหม่สำเร็จ {added_count} แมตช์ (ID 25 ถึง 31)!")
    db.st.cache_data.clear()
else:
    print("ℹ️ ตารางการแข่งขันใหม่ถูกบันทึกในระบบอยู่แล้ว")
