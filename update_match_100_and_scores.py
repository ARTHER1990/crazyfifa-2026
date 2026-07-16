import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta

# ตั้งค่า path ให้รองรับการเรียกโมดูลภายในโปรเจค
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("⚽ เริ่มกระบวนการอัปเดตคู่แข่งขัน Match ID 100 ในรอบ 8 ทีมสุดท้าย...")
    
    # กำหนดทีมที่ผ่านเข้ารอบจริงจากผลแข่งขันเมื่อคืน
    home_team = 'Argentina'  # ผู้ชนะจาก Match 95 (Argentina 3 - 2 Egypt)
    away_team = 'Switzerland'  # ผู้ชนะจาก Match 96 (Switzerland 0 - 0 Colombia ชนะจุดโทษ)
    match_id = 100
    
    # 1. จัดการข้อมูลใน Google Sheets (Source of Truth)
    print("\n📊 [1/3] กำลังอัปเดตคู่แข่งขันใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        mask = df_sheets['id'].astype(str) == str(match_id)
        if mask.any():
            idx = df_sheets.index[mask][0]
            old_home = df_sheets.at[idx, 'home_team']
            old_away = df_sheets.at[idx, 'away_team']
            df_sheets.at[idx, 'home_team'] = home_team
            df_sheets.at[idx, 'away_team'] = away_team
            
            # เคลียร์และเขียนข้อมูลชุดใหม่ทับ
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"✅ (Sheets) อัปเดต Match ID {match_id}: จาก [{old_home} vs {old_away}] เป็น [{home_team} vs {away_team}] เรียบร้อย!")
        else:
            print(f"❌ ไม่พบ Match ID {match_id} ใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")
        
    # 2. จัดการข้อมูลใน SQLite (worldcup.db)
    print("\n🗄️ [2/3] กำลังอัปเดตคู่แข่งขันใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE matches SET home_team=?, away_team=? WHERE id=?",
            (home_team, away_team, match_id)
        )
        conn.commit()
        conn.close()
        print(f"✅ (SQLite) อัปเดต Match ID {match_id} เป็น [{home_team} vs {away_team}] เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")
        
    # 3. คำนวณแต้มสะสมและโบนัสทายผลใหม่ทั้งหมดพร้อมเคลียร์แคช
    print("\n⚙️ [3/3] กำลังประมวลผลแต้มสะสมและโบนัสพิเศษของผู้ใช้ทุกคนให้เป็นปัจจุบันที่สุด...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้งาน update_scores_logic() สำเร็จ! สรุปคะแนนลีดเดอร์บอร์ดอัปเดตเป็นสัดส่วนที่ถูกต้องแล้ว")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบคำนวณแต้มสะสม: {e}")
        
    # --- ปรับปรุงหัวไฟล์ app.py และพุชขึ้น GitHub เพื่อบังคับ Redeploy และล้างแคช RAM บนเซิร์ฟเวอร์ออนไลน์ ---
    print("\n🐙 [GitHub] เริ่มการบังคับล้างแคช RAM และ Redeploy ฝั่งออนไลน์...")
    try:
        app_path = os.path.join(BASE_DIR, 'app.py')
        if os.path.exists(app_path):
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
            comment_line = f'# Last cache clear and match 100 update: {now_str} (Manual update Match 100: {home_team} vs {away_team})\n'
            
            # แทนที่หรือเขียนใหม่คอมเมนต์บรรทัดแรกเพื่อกระตุ้น Redeploy
            if content.startswith('# Last cache clear'):
                lines = content.split('\n')
                new_content = comment_line + '\n'.join(lines[1:])
            else:
                new_content = comment_line + content
                
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ ทำการ Touch app.py สำเร็จ เพื่อกระตุ้นการล้างแคช RAM")
            
            # ใช้ subprocess จัดการ Git add, commit, push
            import subprocess
            subprocess.run(["git", "checkout", "main"], cwd=BASE_DIR, check=False)
            subprocess.run(["git", "add", "app.py", "worldcup.db"], cwd=BASE_DIR, check=False)
            
            commit_msg = f"feat: Set Match 100 to Argentina vs Switzerland & update leaderboard score ({now_str})"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
            print("🎉 [GitHub] ดันข้อมูลคะแนนใหม่และแมตช์ที่ได้รับการซ่อมแซมขึ้นเซิร์ฟเวอร์หลักแล้วเรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสั่งการ GitHub / Touch app.py: {e}")

if __name__ == '__main__':
    main()
