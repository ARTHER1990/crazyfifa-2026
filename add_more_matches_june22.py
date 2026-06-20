import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db
import pandas as pd

# ดึงข้อมูลจาก Google Sheets
ws = db.get_worksheet('matches')
data = ws.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# ตารางคู่แข่งขันใหม่ที่จะอัปเดตเพิ่ม ตั้งแต่วันที่ 19 มิถุนายน ถึง 22 มิถุนายน 2026
# (ต่อจาก ID 35)
new_matches = [
    # วันที่ 19 มิถุนายน 2026 (คู่ตกหล่น 1 คู่)
    {
        'id': '36',
        'home_team': 'Turkey',
        'away_team': 'Paraguay',
        'match_time': '2026-06-19 11:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    # วันที่ 21 มิถุนายน 2026 (June 21, 2026)
    {
        'id': '37',
        'home_team': 'Spain',
        'away_team': 'Saudi Arabia',
        'match_time': '2026-06-21 23:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '38',
        'home_team': 'Belgium',
        'away_team': 'Iran',
        'match_time': '2026-06-21 02:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '39',
        'home_team': 'Uruguay',
        'away_team': 'Cape Verde',
        'match_time': '2026-06-21 05:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '40',
        'home_team': 'New Zealand',
        'away_team': 'Egypt',
        'match_time': '2026-06-21 08:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    # วันที่ 22 มิถุนายน 2026 (June 22, 2026)
    {
        'id': '41',
        'home_team': 'Argentina',
        'away_team': 'Austria',
        'match_time': '2026-06-22 00:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '42',
        'home_team': 'France',
        'away_team': 'Iraq',
        'match_time': '2026-06-22 04:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '43',
        'home_team': 'Norway',
        'away_team': 'Senegal',
        'match_time': '2026-06-22 07:00:00',
        'home_score': '',
        'away_score': '',
        'status': 'Upcoming',
        'scorers': ''
    },
    {
        'id': '44',
        'home_team': 'Jordan',
        'away_team': 'Algeria',
        'match_time': '2026-06-22 09:00:00',
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
    print(f"✅ ดำเนินการเพิ่มตารางการแข่งขันล่วงหน้าเรียบร้อยแล้ว {added_count} แมตช์ (ID 36 ถึง 44)!")
    db.st.cache_data.clear()
else:
    print("ℹ️ ตารางการแข่งขันล่วงหน้าถูกบันทึกในระบบครบถ้วนอยู่แล้ว")
