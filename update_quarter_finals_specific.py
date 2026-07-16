import sys
import os
import pandas as pd

# ตั้งค่า path ให้เรียกใช้ database module ได้
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def update():
    print("🚀 เริ่มระบบอัปเดตผลการแข่งขันรอบ 8 ทีมสุดท้าย (แมตช์ 98, 99, 100) ลงใน Google Sheets...")
    
    # 1. ดึง worksheet matches จาก Google Sheets
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"❌ โหลดข้อมูลจาก Google Sheets ล้มเหลว: {e}")
        return

    # ข้อมูลที่จะอัปเดต
    updates = {
        '98': {
            'home_score': '2',
            'away_score': '1',
            'status': 'Finished',
            'scorers': 'Fabián Ruiz (30), Mikel Merino (88) | Charles De Ketelaere (41)',
            'winner_qualify': 'Spain'
        },
        '99': {
            'home_score': '1',
            'away_score': '2',
            'status': 'Finished',
            'scorers': 'Andreas Schjelderup (36) | Jude Bellingham (45+2, 93)',
            'winner_qualify': 'England'
        },
        '100': {
            'home_score': '3',
            'away_score': '1',
            'status': 'Finished',
            'scorers': 'Alexis Mac Allister (10), Julián Alvarez (112), Lautaro Martínez (120+1) | Dan Ndoye (67)',
            'winner_qualify': 'Argentina'
        }
    }

    # อัปเดตลง DataFrame
    updated_count = 0
    for match_id, fields in updates.items():
        mask = df_sheets['id'].astype(str) == str(match_id)
        if mask.any():
            idx = df_sheets.index[mask][0]
            for col, val in fields.items():
                df_sheets.at[idx, col] = str(val)
            print(f"✅ อัปเดต DataFrame สำหรับ Match ID {match_id} สำเร็จ! ({df_sheets.at[idx, 'home_team']} vs {df_sheets.at[idx, 'away_team']})")
            updated_count += 1
        else:
            print(f"⚠️ ไม่พบ Match ID {match_id} ใน Google Sheets")

    if updated_count > 0:
        try:
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print("🎉 บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว!")
        except Exception as e:
            print(f"❌ บันทึกข้อมูลลง Google Sheets ล้มเหลว: {e}")
            return
            
        # 2. รันการซิงค์ SQLite ในโลคัล
        print("\n🔄 กำลังรันซิงค์ข้อมูลจาก Sheets เข้าสู่ SQLite โลคัล...")
        import sync_sheets_to_sqlite
        sync_sheets_to_sqlite.sync()
    else:
        print("😴 ไม่มีคู่แข่งขันใดได้รับการอัปเดต")

if __name__ == '__main__':
    update()
