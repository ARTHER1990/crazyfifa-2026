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
    '19': {
        'home_score': '3',
        'away_score': '0',
        'status': 'Finished',
        'scorers': 'Lionel Messi (17, 60, 76)'
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
