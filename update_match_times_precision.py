import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบปรับพิกัดเวลาเตะแบบความแม่นยำสูง (Precision Kickoff Times) สำหรับ ID 68, 69, 70...")

    # ตารางการปรับเวลาเตะตามเขตเวลาไทย (UTC+7) ที่ถูกต้องที่สุดตามจริง
    updated_times = {
        '70': {  # Brazil vs Japan
            'match_time': '2026-06-30 00:00:00',  # เที่ยงคืนวันนี้พอดีเป๊ะ! (1:00 PM ET)
        },
        '68': {  # Germany vs Paraguay
            'match_time': '2026-06-30 03:30:00',  # ตี 3 ครึ่งคืนนี้ (4:30 PM ET)
        },
        '69': {  # Netherlands vs Morocco
            'match_time': '2026-06-30 08:00:00',  # 8 โมงเช้าพรุ่งนี้ (9:00 PM ET)
        }
    }

    # --- 1. จัดการ Google Sheets ---
    print("\n📊 [1/3] กำลังอัปเดตเวลาเตะใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_updated = 0
        for m_id, details in updated_times.items():
            if str(m_id) in df_sheets['id'].astype(str).values:
                idx = df_sheets[df_sheets['id'].astype(str) == str(m_id)].index[0]
                old_time = df_sheets.at[idx, 'match_time']
                df_sheets.at[idx, 'match_time'] = details['match_time']
                sheets_updated += 1
                print(f"🔄 (Sheets) ปรับเวลา Match ID {m_id} ({df_sheets.at[idx, 'home_team']} vs {df_sheets.at[idx, 'away_team']}): จาก [{old_time}] เป็น [{details['match_time']}]")
        
        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ บันทึกเวลาเตะใหม่ลง Google Sheets สำเร็จ! (ปรับเวลา {sheets_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการ SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังอัปเดตเวลาเตะใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_updated = 0
        for m_id, details in updated_times.items():
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(m_id),))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute(
                    "UPDATE matches SET match_time=? WHERE id=?",
                    (details['match_time'], int(m_id))
                )
                sqlite_updated += 1
                print(f"🔄 (SQLite) ปรับเวลา Match ID {m_id} เป็น [{details['match_time']}]")
                
        conn.commit()
        conn.close()
        print(f"✅ บันทึกเวลาเตะใหม่ลง SQLite (worldcup.db) สำเร็จ! (ปรับเวลา {sqlite_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. เคลียร์แคชระบบเพื่อให้ผลลัพธ์ปรากฏทันที ---
    print("\n⚙️ [3/3] กำลังคำนวณคะแนนผู้เล่นและล้างแคชระบบ...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และล้างแคช RAM เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

    print("\n🏆 --- การปรับเวลาเรียบร้อย 100% --- 🏆")

if __name__ == '__main__':
    main()
