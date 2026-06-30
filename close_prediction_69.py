import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🔒 เริ่มกระบวนการปิดรับทายผลสำหรับ แมตช์ ID 69 (Netherlands vs Morocco) โดยปรับเวลาเตะให้อยู่ในอดีตเพื่อล็อกการทายผลทันที...")

    target_id = '69'
    locked_time = '2026-06-30 07:50:00'  # ตั้งเวลาให้อยู่ในอดีต (ก่อนเวลาระบบปัจจุบัน) เพื่อผลลัพธ์ล็อกทันที

    # 1. ปรับปรุงใน Google Sheets
    print("\n📊 [1/3] กำลังอัปเดตเวลาเตะใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        if str(target_id) in df_sheets['id'].astype(str).values:
            idx = df_sheets[df_sheets['id'].astype(str) == str(target_id)].index[0]
            old_time = df_sheets.at[idx, 'match_time']
            df_sheets.at[idx, 'match_time'] = locked_time
            
            # บันทึกข้อมูลกลับ
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"✅ (Sheets) ปรับเวลา Match ID {target_id} ({df_sheets.at[idx, 'home_team']} vs {df_sheets.at[idx, 'away_team']}) จาก [{old_time}] เป็น [{locked_time}] (ปิดรับทายผลสำเร็จ)")
        else:
            print(f"❌ ไม่พบ Match ID {target_id} ใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # 2. ปรับปรุงใน SQLite (worldcup.db)
    print("\n🗄️ [2/3] กำลังอัปเดตเวลาเตะใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, home_team, away_team FROM matches WHERE id=?", (int(target_id),))
        row = cursor.fetchone()
        if row is not None:
            cursor.execute(
                "UPDATE matches SET match_time=? WHERE id=?",
                (locked_time, int(target_id))
            )
            conn.commit()
            print(f"✅ (SQLite) ปรับเวลา Match ID {target_id} ({row[1]} vs {row[2]}) เป็น [{locked_time}]")
        else:
            print(f"❌ ไม่พบ Match ID {target_id} ใน SQLite")
        conn.close()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # 3. ล้างแคชและอัปเดตคะแนน
    print("\n⚙️ [3/3] กำลังเคลียร์แคชและรีเฟรชระบบ...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และเคลียร์แคช RAM สำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

    print("\n🏆 --- การปิดรับทายผลเสร็จสมบูรณ์ --- 🏆")

if __name__ == '__main__':
    main()
