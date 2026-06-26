import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบอัปเดตผลสกอร์การแข่งขันประจำวันที่ 26 มิถุนายน 2026...")

    # ข้อมูลสกอร์จริงและรายชื่อผู้ทำประตูอย่างเป็นทางการจาก Wikipedia
    updates = {
        '51': {
            'home_score': '0',
            'away_score': '2',
            'status': 'Finished',
            'scorers': '| Nicolas Pépé (7, 64)'
        },
        '52': {
            'home_score': '2',
            'away_score': '1',
            'status': 'Finished',
            'scorers': 'Angulo (9), Plata (77) | Sané (2)'
        }
    }

    # --- 1. อัปเดตข้อมูลใน SQLite (worldcup.db) ---
    print("\n🗄️ [1/3] กำลังอัปเดตข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_updated = 0
        for m_id, val in updates.items():
            cursor.execute("SELECT id, home_team, away_team FROM matches WHERE id=?", (int(m_id),))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute(
                    "UPDATE matches SET home_score=?, away_score=?, status=?, scorers=? WHERE id=?",
                    (int(val['home_score']), int(val['away_score']), val['status'], val['scorers'], int(m_id))
                )
                sqlite_updated += 1
                print(f"✅ (SQLite) อัปเดต ID {m_id}: {row[1]} {val['home_score']} - {val['away_score']} {row[2]}")
            else:
                print(f"⚠️ (SQLite) ไม่พบ Match ID {m_id} ในฐานข้อมูล")
                
        conn.commit()
        conn.close()
        print(f"🎉 อัปเดต SQLite สำเร็จ {sqlite_updated} แมตช์!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดต SQLite: {e}")

    # --- 2. อัปเดตข้อมูลใน Google Sheets ---
    print("\n📊 [2/3] กำลังอัปเดตข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_updated = 0
        for m_id, val in updates.items():
            mask = df_sheets['id'].astype(str) == str(m_id)
            if mask.any():
                idx = df_sheets.index[mask][0]
                df_sheets.at[idx, 'home_score'] = str(val['home_score'])
                df_sheets.at[idx, 'away_score'] = str(val['away_score'])
                df_sheets.at[idx, 'status'] = str(val['status'])
                df_sheets.at[idx, 'scorers'] = str(val['scorers'])
                sheets_updated += 1
                home_t = df_sheets.at[idx, 'home_team']
                away_t = df_sheets.at[idx, 'away_team']
                print(f"✅ (Sheets) อัปเดต ID {m_id}: {home_t} {val['home_score']} - {val['away_score']} {away_t}")
            else:
                print(f"⚠️ (Sheets) ไม่พบ Match ID {m_id} ใน Google Sheets")
                
        # บันทึกข้อมูลกลับลง Google Sheets
        if sheets_updated > 0:
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"🎉 อัปเดต Google Sheets สำเร็จ {sheets_updated} แมตช์!")
        else:
            print("❌ ไม่มีข้อมูลแมตช์ที่ได้รับการอัปเดตใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดต Google Sheets: {e}")

    # --- 3. รันระบบคำนวณคะแนนสะสมและล้างแคชระบบ ---
    print("\n⚙️ [3/3] กำลังคำนวณผลคะแนนผู้ทายผลและล้างแคชระบบ...")
    try:
        db.update_scores_logic()
        print("🎊 ระบบได้รันฟังก์ชัน update_scores_logic() เรียบร้อย! ผู้ทายผลทุกคนได้รับคะแนนสะสมล่าสุดแล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการคำนวณคะแนน: {e}")

    print("\n🏆 --- กระบวนการอัปเดตผลการแข่งขันและคำนวณคะแนนเสร็จสมบูรณ์เรียบร้อยครับ! --- 🏆")

if __name__ == '__main__':
    main()
