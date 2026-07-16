import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db
from auto_update_results import touch_app_py, push_to_github

def fix_time():
    print("🛠️  เริ่มทำการแก้ไขเวลาแข่งขันของแมตช์ ID 92 (Mexico vs England) ให้เป็นเวลาจริง (07:00 น.)...")
    
    # 1. แก้ไขใน Google Sheets (Source of Truth)
    try:
        db.get_matches.clear()
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        mask = df_sheets['id'].astype(str) == '92'
        if mask.any():
            idx = df_sheets.index[mask][0]
            old_time = df_sheets.at[idx, 'match_time']
            df_sheets.at[idx, 'match_time'] = '2026-07-06 07:00:00'
            print(f"✅ Google Sheets: พบแมตช์ ID 92 ปรับเวลาจาก '{old_time}' -> '2026-07-06 07:00:00'")
            
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print("🎉 บันทึกการแก้ไขลง Google Sheets สำเร็จ!")
        else:
            print("⚠️  ไม่พบ Match ID 92 ใน Google Sheets")
    except Exception as e:
        print(f"❌ แก้ไข Google Sheets ล้มเหลว: {e}")
        return

    # 2. แก้ไขใน SQLite (worldcup.db)
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT match_time FROM matches WHERE id = 92")
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE matches SET match_time = '2026-07-06 07:00:00' WHERE id = 92")
            conn.commit()
            print(f"✅ SQLite: แก้ไขเวลาแมตช์ ID 92 สำเร็จ! (เดิม: '{row[0]}' -> '2026-07-06 07:00:00')")
        else:
            print("⚠️  ไม่พบ Match ID 92 ใน SQLite")
        conn.close()
    except Exception as e:
        print(f"❌ แก้ไข SQLite ล้มเหลว: {e}")
        return

    # 3. ล้างแคชใน memory และรันการอัปเดตแคช
    db.get_matches.clear()
    
    # 4. ทัชไฟล์ app.py และพุชขึ้น GitHub เพื่อกระตุ้นเซิร์ฟเวอร์ออนไลน์บังคับล้างแคช RAM ทันที
    print("\n⚡ ทำการ Touch app.py เพื่อล้างแคชคลาวด์และดันขึ้น GitHub...")
    touch_app_py("Mexico", "England", "", "")
    push_to_github()
    print("\n🏆 เสร็จสิ้นขั้นตอนการแก้ไขเวลาคู่อังกฤษสำเร็จอย่างเป็นทางการเรียบร้อยครับ!")

if __name__ == '__main__':
    fix_time()
