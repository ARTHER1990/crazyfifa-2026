import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("⚽ เริ่มกระบวนการอัปเดตผลการแข่งขันอย่างเป็นทางการของ Match ID 82: Belgium vs Senegal...")

    target_id = '82'
    home_score = 3
    away_score = 2
    scorers = "Romelu Lukaku (86), Youri Tielemans (89, 120+5 pen) | Diarra (25), Ismaïla Sarr (51)"
    winner_qualify = "Belgium"

    # --- 1. จัดการข้อมูลใน Google Sheets ---
    print("\n📊 [1/3] กำลังจัดการข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        mask = df_sheets['id'].astype(str) == str(target_id)
        if mask.any():
            idx = df_sheets.index[mask][0]
            df_sheets.at[idx, 'home_score'] = str(home_score)
            df_sheets.at[idx, 'away_score'] = str(away_score)
            df_sheets.at[idx, 'status'] = 'Finished'
            df_sheets.at[idx, 'scorers'] = scorers
            if 'winner_qualify' in df_sheets.columns:
                df_sheets.at[idx, 'winner_qualify'] = winner_qualify
            
            # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"✅ Google Sheets อัปเดต ID {target_id} (Belgium vs Senegal) สำเร็จ!")
        else:
            print(f"⚠️ ไม่พบ Match ID {target_id} ใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการข้อมูลใน SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังจัดการข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM matches WHERE id=?", (int(target_id),))
        row = cursor.fetchone()
        if row is not None:
            cursor.execute(
                "UPDATE matches SET home_score=?, away_score=?, status='Finished', scorers=?, winner_qualify=? WHERE id=?",
                (int(home_score), int(away_score), scorers, winner_qualify, int(target_id))
            )
            conn.commit()
            print(f"✅ SQLite อัปเดต ID {target_id} (Belgium vs Senegal) สำเร็จ!")
        else:
            print(f"⚠️ ไม่พบ Match ID {target_id} ใน SQLite")
        conn.close()
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. คำนวณแจกแต้มสรุปคะแนนประจำลีก และ รีเฟรชระบบ ---
    print("\n⚙️ [3/3] กำลังคำนวณคะแนนแจกจ่ายสมาชิกและเคลียร์แคชระบบ...")
    try:
        # คำนวณแจกแต้มสรุปคะแนน
        db.update_scores_logic()
        print("✅ คำนวณและสรุปแจกคะแนนสมาชิกทายผลสำเร็จ!")
        
        # กระตุ้นให้ล้างแคช Streamlit Cloud
        app_path = os.path.join(BASE_DIR, 'app.py')
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            comment_line = f'# Last cache clear and score update: {now_str} (Auto updated Match 82 Belgium 3-2 Senegal)\n'
            if content.startswith('# Last cache clear'):
                lines = content.split('\n')
                new_content = comment_line + '\n'.join(lines[1:])
            else:
                new_content = comment_line + content
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ ปรับแต่งหัวไฟล์ app.py สำเร็จ เพื่อบังคับล้างแคช RAM บน Streamlit Cloud")
            
        # Push ขึ้น GitHub ออโต้
        print("\n🐙 [Git] กำลังทำการส่งความเปลี่ยนแปลงขึ้น GitHub...")
        import subprocess
        subprocess.run(["git", "add", "app.py"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "add", "-f", "worldcup.db"], cwd=BASE_DIR, check=False)
        commit_msg = f"feat: Updated Match 82 results (Belgium 3-2 Senegal) and calculated prediction scores via Peter AI ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("🎉 [Git] ส่งข้อมูลขึ้น GitHub สำเร็จเสร็จสิ้น!")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")

    print("\n🏆 --- การสรุปผลคะแนน Match 82 เสร็จสิ้น --- 🏆")

if __name__ == '__main__':
    main()
