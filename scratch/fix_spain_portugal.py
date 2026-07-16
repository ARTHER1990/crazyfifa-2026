import os
import sys
import sqlite3
import pandas as pd

# ตั้งค่า path ค้นหาโมดูล
BASE_DIR = '/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026'
sys.path.append(BASE_DIR)

import database as db

def fix_match_93():
    print("🛠️ เริ่มทำการแก้ไขข้อมูลคู่ ID 93 Spain vs Portugal ให้ถูกต้อง...")
    
    # ข้อมูลที่ถูกต้อง
    m_id = 93
    h_score = 1
    a_score = 0
    scorers = "Mikel Merino (90+1)"
    winner_qualify = "Spain"
    
    # 1. แก้ไขใน SQLite
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE matches SET home_score=?, away_score=?, status='Finished', scorers=?, winner_qualify=? WHERE id=?",
            (h_score, a_score, scorers, winner_qualify, m_id)
        )
        conn.commit()
        conn.close()
        print("✅ SQLite อัปเดต ID 93 เป็น 1 - 0 สำเร็จ!")
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
            df_sheets.at[idx, 'home_score'] = str(h_score)
            df_sheets.at[idx, 'away_score'] = str(a_score)
            df_sheets.at[idx, 'status'] = 'Finished'
            df_sheets.at[idx, 'scorers'] = str(scorers)
            if 'winner_qualify' in df_sheets.columns:
                df_sheets.at[idx, 'winner_qualify'] = str(winner_qualify)
            
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print("✅ Google Sheets อัปเดต ID 93 เป็น 1 - 0 สำเร็จ!")
        else:
            print("⚠️ ไม่พบ Match ID 93 ใน Google Sheets")
            return
    except Exception as e:
        print(f"❌ แก้ไข Google Sheets ล้มเหลว: {e}")
        return

    # 3. คำนวณแจกแต้มใหม่ทั้งหมด
    print("\n🧮 กำลังคำนวณและสรุปแต้มทายผลประจำลีกใหม่...")
    try:
        db.update_scores_logic()
        print("🎉 คำนวณและแจกคะแนนสมาชิกทายผลใหม่สำเร็จ!")
    except Exception as e:
        print(f"❌ การคำนวณแต้มทายผลใหม่มีข้อผิดพลาด: {e}")
        return

    # 4. สังเคราะห์เสียงพากย์ใหม่
    try:
        import subprocess
        print("\n🎙️ [AI Voice] เริ่มระบบสร้างบทวิเคราะห์และเสียงพากย์ปีเตอร์ AI ล่าสุดแบบอัตโนมัติ...")
        subprocess.run(["python3", "generate_latest_ai.py"], cwd=BASE_DIR, check=True)
        print("✅ [AI Voice] ปรับปรุงบทวิเคราะห์และสังเคราะห์เสียงใหม่สำเร็จ!")
    except Exception as e_voice:
        print(f"❌ [AI Voice] เกิดข้อผิดพลาดในการสังเคราะห์เสียงใหม่: {e_voice}")

    # 5. ดันข้อมูลขึ้น GitHub เพื่ออัปเดตเซิร์ฟเวอร์จริง
    try:
        import subprocess
        print("\n🐙 [Git] กำลังอัปเดตไฟล์ขึ้น GitHub...")
        
        # อัปเดตคอมเมนต์หัวไฟล์ app.py
        app_path = os.path.join(BASE_DIR, 'app.py')
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        from datetime import datetime, timezone, timedelta
        now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
        comment_line = f'# Last cache clear and score update: {now_str} (Manual Fix: Spain 1-0 Portugal)\n'
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
        
        commit_msg = f"fix: Correct match 93 score (Spain 1-0 Portugal) and recalculate leaderboard points ({now_str})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
        print("🎉 [Git] ส่งข้อมูลผลแก้ไขและแต้มใหม่ขึ้น GitHub และล้างแคชเรียบร้อยแล้ว!")
    except Exception as e:
        print(f"❌ [Git] อัปเดต GitHub ล้มเหลว: {e}")

if __name__ == '__main__':
    fix_match_93()
