import sys
import os
import sqlite3
import pandas as pd

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบอัปเดตผู้เข้ารอบน็อกเอาต์ (winner_qualify) และคำนวณแต้มสะสมโบนัสพิเศษ...")

    # ข้อมูลทีมเข้ารอบของเมื่อคืน:
    # Match ID 70: Brazil vs Japan (Brazil ชนะ 2-1) -> Brazil เข้ารอบ
    # Match ID 68: Germany vs Paraguay (เสมอ 1-1) -> Germany ชนะจุดโทษเข้ารอบ
    winners = {
        '70': 'Brazil',
        '68': 'Germany'
    }

    # 1. จัดการ Google Sheets
    print("\n📊 [1/3] กำลังอัปเดตข้อมูลผู้เข้ารอบใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_updated = 0
        for m_id, winner in winners.items():
            mask = df_sheets['id'].astype(str) == str(m_id)
            if mask.any():
                idx = df_sheets.index[mask][0]
                old_winner = df_sheets.at[idx, 'winner_qualify']
                df_sheets.at[idx, 'winner_qualify'] = winner
                sheets_updated += 1
                print(f"🔄 (Sheets) ปรับผู้เข้ารอบ Match ID {m_id} ({df_sheets.at[idx, 'home_team']} vs {df_sheets.at[idx, 'away_team']}): จาก [{old_winner}] เป็น [{winner}]")
        
        if sheets_updated > 0:
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"✅ บันทึกข้อมูลกลับลง Google Sheets สำเร็จ! (อัปเดต {sheets_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # 2. จัดการ SQLite (worldcup.db)
    print("\n🗄️ [2/3] กำลังอัปเดตข้อมูลผู้เข้ารอบใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_updated = 0
        for m_id, winner in winners.items():
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(m_id),))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute(
                    "UPDATE matches SET winner_qualify=? WHERE id=?",
                    (winner, int(m_id))
                )
                sqlite_updated += 1
                print(f"🔄 (SQLite) อัปเดตผู้เข้ารอบ Match ID {m_id} เป็น [{winner}]")
                
        conn.commit()
        conn.close()
        print(f"✅ บันทึกข้อมูลผู้เข้ารอบลง SQLite สำเร็จ! (อัปเดต {sqlite_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # 3. คำนวณแต้มทายผลใหม่พร้อมเคลียร์แคช
    print("\n⚙️ [3/3] กำลังคำนวณแต้มทายผลของผู้เข้าร่วมรอบน็อกเอาต์ใหม่พร้อมล้างแคช...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และล้างแคชสำเร็จ แต้มโบนัส +1 สะสมเข้าระบบสำหรับผู้ทายถูกเรียบร้อยแล้ว!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการคำนวณแต้มใหม่: {e}")

    print("\n🏆 --- กระบวนการอัปเดตโบนัสรอบน็อกเอาต์สำเร็จสมบูรณ์ --- 🏆")

if __name__ == '__main__':
    main()
