import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta

# ตั้งค่า path ค้นหาโมดูล
BASE_DIR = '/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026'
sys.path.append(BASE_DIR)

import database as db

def fix_belgium_time():
    print("🛠️ เริ่มทำการแก้ไขเวลาเตะของคู่ ID 94 United States vs Belgium ให้ถูกต้องตามเวลาฟีฟ่าจริง...")
    
    m_id = 94
    correct_time = "2026-07-07 07:00:00"
    
    # 1. อัปเดตใน SQLite
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE matches SET match_time=? WHERE id=?",
            (correct_time, m_id)
        )
        conn.commit()
        conn.close()
        print("✅ SQLite อัปเดตเวลาคู่ ID 94 เป็น 07:00:00 สำเร็จ!")
    except Exception as e:
        print(f"❌ แก้ไข SQLite ล้มเหลว: {e}")
        return

    # 2. แก้ไขใน Google Sheets
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        mask = df_sheets['id'].astype(str) == str(m_id)
        if mask.any():
            idx = df_sheets.index[mask][0]
            df_sheets.at[idx, 'match_time'] = correct_time
            
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print("✅ Google Sheets อัปเดตเวลาคู่ ID 94 เป็น 07:00:00 สำเร็จ!")
        else:
            print("⚠️ ไม่พบ Match ID 94 ใน Google Sheets")
            return
    except Exception as e:
        print(f"❌ แก้ไข Google Sheets ล้มเหลว: {e}")
        return

    # 3. รันอัปเดตแคชเสียง AI และ Git push เพื่ออัปเดตเซิร์ฟเวอร์
    try:
        import subprocess
        print("\n🎙️ [AI Voice] รันสร้างวิเคราะห์และอัปเดตบทวิเคราะห์หลังการแก้ไขเวลาเตะ...")
        subprocess.run(["python3", "generate_latest_ai.py"], cwd=BASE_DIR, check=True)
        print("✅ [AI Voice] สังเคราะห์วิเคราะห์ใหม่เสร็จสิ้น!")
        
        print("\n🐙 [Git] กำลังดันไฟล์แก้ไขขึ้น GitHub...")
        # อัปเดตคอมเมนต์หัวไฟล์ app.py กระตุ้นการ Redeploy
        app_path = os.path.join(BASE_DIR, 'app.py')
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
        comment_line = f'# Last cache clear and score update: {now_str} (Corrected Match 94 time: United States vs Belgium 07:00)\n'
        if content.startswith('# Last cache clear'):
            lines = content.split('\n')
            new_content = comment_line + '\n'.join(lines[1:])
        else:
            new_content = comment_line + content
            
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        # Git Commands
        subprocess.run(["git", "checkout", "main"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "pull", "origin", "main"], cwd=BASE_DIR, check=False)
        
        for file_name in ["app.py", "ai_cache.json", "static/ai_analysis_fast.webp"]:
            subprocess.run(["git", "add", file_name], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "add", "-f", "worldcup.db"], cwd=BASE_DIR, check=False)
        
        commit_msg = f"fix: Correct match 94 kickoff time (United States vs Belgium to 07:00) and lock prediction ({now_str})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
        print("🎉 [Git] ดันไฟล์ขึ้น GitHub และรีบูตหน้าเว็บสำเร็จแล้ว!")
    except Exception as e:
        print(f"❌ กระบวนการ Git/Redeploy มีข้อผิดพลาด: {e}")

if __name__ == '__main__':
    fix_belgium_time()
