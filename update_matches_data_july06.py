import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db
from auto_update_results import touch_app_py, push_to_github

def run_update():
    print("🔄 [1/4] เริ่มต้นอัปเดตข้อมูลการแข่งขันใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        # ค้นหาและอัปเดต Match ID 92 (Mexico vs England)
        idx_92 = df_sheets[df_sheets['id'].astype(str) == '92'].index[0]
        df_sheets.at[idx_92, 'winner_qualify'] = 'England'
        # เสริมความมั่นใจว่าสกอร์และสถานะตรงกับความจริง
        df_sheets.at[idx_92, 'home_score'] = '2'
        df_sheets.at[idx_92, 'away_score'] = '3'
        df_sheets.at[idx_92, 'status'] = 'Finished'
        df_sheets.at[idx_92, 'scorers'] = "Quiñones42'Jiménez69'(pen.) | Bellingham36',38'Kane60'(pen.)"
        print("✅ (Sheets) อัปเดตข้อมูลและบันทึกผู้ชนะ Match ID 92 -> England เรียบร้อย!")
        
        # ค้นหาและอัปเดต Match ID 95 (Argentina vs Egypt)
        idx_95 = df_sheets[df_sheets['id'].astype(str) == '95'].index[0]
        df_sheets.at[idx_95, 'home_team'] = 'Argentina'
        df_sheets.at[idx_95, 'away_team'] = 'Egypt'
        print("✅ (Sheets) อัปเดตทีมจริงคู่ Match ID 95 -> Argentina vs Egypt เรียบร้อย!")
        
        # ค้นหาและอัปเดต Match ID 96 (Switzerland vs Colombia)
        idx_96 = df_sheets[df_sheets['id'].astype(str) == '96'].index[0]
        df_sheets.at[idx_96, 'home_team'] = 'Switzerland'
        df_sheets.at[idx_96, 'away_team'] = 'Colombia'
        df_sheets.at[idx_96, 'match_time'] = '2026-07-08 03:00:00'
        print("✅ (Sheets) อัปเดตทีมจริงและเวลาแข่งขัน Match ID 96 -> Switzerland vs Colombia เตะเวลา 03:00 น. เรียบร้อย!")
        
        # เขียนบันทึกคืน Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print("💾 บันทึกการอัปเดตลง Google Sheets เรียบร้อยแล้ว!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในขั้นตอน Google Sheets: {e}")
        return

    print("\n🗄️ [2/4] เริ่มต้นอัปเดตข้อมูลการแข่งขันใน SQLite ท้องถิ่น...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # อัปเดต Match ID 92
        cursor.execute("""
            UPDATE matches 
            SET home_score=2, away_score=3, status='Finished', 
                scorers=\"Quiñones42'Jiménez69'(pen.) | Bellingham36',38'Kane60'(pen.)\", 
                winner_qualify='England' 
            WHERE id=92
        """)
        
        # อัปเดต Match ID 95
        cursor.execute("""
            UPDATE matches 
            SET home_team='Argentina', away_team='Egypt' 
            WHERE id=95
        """)
        
        # อัปเดต Match ID 96
        cursor.execute("""
            UPDATE matches 
            SET home_team='Switzerland', away_team='Colombia', match_time='2026-07-08 03:00:00' 
            WHERE id=96
        """)
        
        conn.commit()
        conn.close()
        print("✅ (SQLite) บันทึกทับฐานข้อมูล SQLite ท้องถิ่นสำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในขั้นตอน SQLite: {e}")
        return

    print("\n🧮 [3/4] กำลังคำนวณคะแนนเดาผลการแข่งขันและโบนัสสมาชิกทุกคนใหม่ทั้งหมด...")
    try:
        db.update_scores_logic()
        print("🎉 คำนวณแจกโบนัสและอัปเดตคะแนนสะสมใหม่สมบูรณ์!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในขั้นตอนคำนวณคะแนน: {e}")
        return

    print("\n⚡ [4/4] ดำเนินการล้างแคช RAM บน Cloud และส่งการเปลี่ยนแปลงขึ้น GitHub...")
    try:
        # สุ่มแตะข้อมูลเพื่อให้เกิด redeploy ล้างแคช RAM
        touch_app_py("Mexico", "England", 2, 3)
        push_to_github()
        print("🚀 เสร็จสมบูรณ์ทุกขั้นตอนเรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในขั้นตอนรีพลอยด์/พุช GitHub: {e}")

if __name__ == '__main__':
    run_update()
