import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบนำคู่แข่งขันที่ยังไม่สรุปทีม (Placeholders) ของวันที่ 29 มิถุนายน 2026 ออกจากสารบบ...")

    targets_to_remove = [68, 69, 70]

    # 1. จัดการลบใน SQLite (worldcup.db)
    print("\n🗄️ [1/3] กำลังจัดการข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_removed = 0
        for m_id in targets_to_remove:
            cursor.execute("SELECT id, home_team, away_team FROM matches WHERE id=?", (m_id,))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute("DELETE FROM matches WHERE id=?", (m_id,))
                sqlite_removed += 1
                print(f"🗑️ (SQLite) ลบ Match ID {m_id}: {row[1]} vs {row[2]}")
            else:
                print(f"⚠️ (SQLite) ไม่พบ Match ID {m_id} หรือลบไปก่อนแล้ว")
                
        conn.commit()
        conn.close()
        print(f"🎉 ลบข้อมูลใน SQLite สำเร็จ {sqlite_removed} แมตช์!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการลบ SQLite: {e}")

    # 2. จัดการลบใน Google Sheets
    print("\n📊 [2/3] กำลังจัดการข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        initial_count = len(df_sheets)
        
        # กรองแถวที่มี ID อยู่ใน targets_to_remove ออก
        targets_str = [str(x) for x in targets_to_remove]
        df_filtered = df_sheets[~df_sheets['id'].astype(str).isin(targets_str)]
        
        removed_count = initial_count - len(df_filtered)
        
        if removed_count > 0:
            ws.clear()
            ws.update([df_filtered.columns.values.tolist()] + df_filtered.astype(str).values.tolist())
            print(f"🎉 ลบข้อมูลใน Google Sheets สำเร็จ {removed_count} แถว!")
        else:
            print("❌ ไม่พบข้อมูลแมตช์ที่ต้องการลบใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการปรับ Google Sheets: {e}")

if __name__ == '__main__':
    main()
