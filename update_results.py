import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db
import pandas as pd

# ดึงข้อมูล worksheet
ws = db.get_worksheet('matches')
data = ws.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# แมตช์ที่จะอัปเดต
updates = {
    '5': {
        'home_score': '1',
        'away_score': '1',
        'status': 'Finished',
        'scorers': 'Boualem Khoukhi (90+5) | Breel Embolo (73 pen)'
    },
    '6': {
        'home_score': '1',
        'away_score': '1',
        'status': 'Finished',
        'scorers': 'Vinícius Júnior (32) | Ismael Saibari (21)'
    },
    '7': {
        'home_score': '0',
        'away_score': '1',
        'status': 'Finished',
        'scorers': 'John McGinn (16)'
    },
    '8': {
        'home_score': '2',
        'away_score': '0',
        'status': 'Finished',
        'scorers': 'Nestory Irankunda (73), Connor Metcalfe (85)'
    },
    '9': {
        'home_score': '7',
        'away_score': '1',
        'status': 'Finished',
        'scorers': 'Felix Nmecha (6), Nico Schlotterbeck (38), Kai Havertz (45+2 pen, 88), Jamal Musiala (47), Nathaniel Brown (68), Deniz Undav (78) | Livano Comenencia (21)'
    },
    '10': {
        'home_score': '2',
        'away_score': '2',
        'status': 'Finished',
        'scorers': 'Virgil van Dijk (51), Crysencio Summerville (64) | Keito Nakamura (57), Daichi Kamada (89)'
    },
    '11': {
        'home_score': '1',
        'away_score': '0',
        'status': 'Finished',
        'scorers': 'Amad Diallo (89)'
    },
    '12': {
        'home_score': '5',
        'away_score': '1',
        'status': 'Finished',
        'scorers': 'Yasin Ayari (7, 90+6), Alexander Isak (30), Viktor Gyökeres (60), Mattias Svanberg (86) | Omar Rekik (43)'
    }
}

updated_count = 0
for m_id, val in updates.items():
    mask = df['id'].astype(str) == m_id
    if mask.any():
        idx = df.index[mask][0]
        df.at[idx, 'home_score'] = val['home_score']
        df.at[idx, 'away_score'] = val['away_score']
        df.at[idx, 'status'] = val['status']
        df.at[idx, 'scorers'] = val['scorers']
        updated_count += 1

if updated_count > 0:
    # เขียนกลับลง Google Sheets (แถวแรกเป็น header)
    ws.update([df.columns.values.tolist()] + df.values.tolist())
    print(f"✅ อัปเดตผลการแข่งขันสำเร็จ {updated_count} แมตช์!")
    
    # รันตรรกะคำนวณคะแนนใหม่
    db.update_scores_logic()
    print("🎊 คำนวณแต้มทายผลของผู้ใช้ทุกคนเรียบร้อยแล้ว!")
else:
    print("❌ ไม่พบแมตช์ที่ระบุสำหรับการอัปเดต")
