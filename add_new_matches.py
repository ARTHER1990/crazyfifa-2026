import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db
import pandas as pd

# ดึงข้อมูล worksheet
ws = db.get_worksheet('matches')
data = ws.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# ตารางคู่ใหม่ที่จะเพิ่ม
new_matches = [
    {
        'id': '17',
        'home_team': 'France',
        'away_team': 'Senegal',
        'match_time': '2026-06-17 02:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '18',
        'home_team': 'Iraq',
        'away_team': 'Norway',
        'match_time': '2026-06-17 05:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '19',
        'home_team': 'Argentina',
        'away_team': 'Algeria',
        'match_time': '2026-06-17 08:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '20',
        'home_team': 'Austria',
        'away_team': 'Jordan',
        'match_time': '2026-06-17 11:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '21',
        'home_team': 'Portugal',
        'away_team': 'DR Congo',
        'match_time': '2026-06-18 02:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '22',
        'home_team': 'England',
        'away_team': 'Croatia',
        'match_time': '2026-06-18 05:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '23',
        'home_team': 'Ghana',
        'away_team': 'Panama',
        'match_time': '2026-06-18 08:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '24',
        'home_team': 'Uzbekistan',
        'away_team': 'Colombia',
        'match_time': '2026-06-18 11:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    }
]

added_count = 0
for match in new_matches:
    if match['id'] not in df['id'].values:
        df = pd.concat([df, pd.DataFrame([match])], ignore_index=True)
        added_count += 1

if added_count > 0:
    ws.update([df.columns.values.tolist()] + df.astype(str).values.tolist())
    print(f"✅ เพิ่มตารางการแข่งขันใหม่สำเร็จ {added_count} แมตช์ (ID 17 ถึง 24)!")
    db.st.cache_data.clear()
else:
    print("ℹ️ ตารางการแข่งขันใหม่ถูกบันทึกในระบบอยู่แล้ว")
