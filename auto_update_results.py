import sys
import os
import sqlite3
import pandas as pd
import requests
import json
import re
from datetime import datetime, timedelta

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db
import ai_analyst as ai

def get_finished_match_info(home_team, away_team, match_time, api_key):
    """
    ใช้ Gemini API พร้อม Search Grounding ค้นหาผลการแข่งขันจากเว็บอย่างเป็นทางการ
    """
    prompt = f"""
    Please search the official web or reliable sources to find the final score and scorers for the 2026 FIFA World Cup match:
    Home Team: {home_team}
    Away Team: {away_team}
    Match Scheduled Time (UTC+7): {match_time}

    If the match is finished, please return a JSON object with the following fields:
    - status: "Finished"
    - home_score: (integer, number of goals scored by {home_team})
    - away_score: (integer, number of goals scored by {away_team})
    - scorers: (string, list of goal scorers with minutes in format: "Scorer Home (minute) | Scorer Away (minute)". Example: "Daizen Maeda (56) | Anthony Elanga (62)". If no goal or no data, use empty string "" or draw line "|")
    - winner: (string, the name of the winning team, or "Draw" if the score is tied, or null if not finished)
    - winner_qualify: (string, the exact name of the team that qualified to the next round / won the match including extra time or penalty shootout, e.g., "Germany" or "Brazil". Must be one of the exact team names: "{home_team}" or "{away_team}". If the match is not finished, or it is a group stage match, use empty string "")

    If the match is not finished yet, is still playing, or hasn't started, please return:
    - status: "Upcoming"
    - home_score: null
    - away_score: null
    - scorers: ""
    - winner: null
    - winner_qualify: ""

    Respond ONLY with a valid JSON block. Do not add markdown fencing like ```json or any explanation text.
    """

    # ลูปเรียกโมเดลตามลำดับ fallback ป้องกันปัญหา 503/404
    models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "tools": [
                {"google_search": {}}
            ],
            "generationConfig": {
                "temperature": 0.1
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                res_json = response.json()
                text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # ใช้ regular expression สกัดปีกกา JSON ป้องกันกรณี AI เขียนอธิบายแถมมา
                match_json = re.search(r'\{.*\}', text, re.DOTALL)
                if match_json:
                    return json.loads(match_json.group(0)), model_name
                else:
                    # ลอง parse ตรงๆ
                    return json.loads(text), model_name
            else:
                print(f"⚠️ {model_name} Error {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"⚠️ ข้อผิดพลาดในการติดต่อโมเดล {model_name}: {e}")
            
    return None, None

def touch_app_py(home_t, away_t, h_score, a_score):
    """
    อัปเดตความคิดเห็นบรรทัดแรกใน app.py เพื่อกระตุ้นให้ Streamlit Cloud ทำการ Auto-redeploy และล้างแคช RAM
    """
    app_path = os.path.join(BASE_DIR, 'app.py')
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        comment_line = f'# Last cache clear and score update: {now_str} (Auto updated: {home_t} {h_score}-{a_score} {away_t})\n'
        
        # ค้นหาคอมเมนต์เดิมที่ขึ้นต้นด้วย '# Last cache clear'
        if content.startswith('# Last cache clear'):
            # ตัดบรรทัดแรกของเดิมทิ้ง
            lines = content.split('\n')
            new_content = comment_line + '\n'.join(lines[1:])
        else:
            new_content = comment_line + content
            
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print("✅ (app.py) ได้อัปเดตคอมเมนต์หัวไฟล์เพื่อกระตุ้นการ Redeploy สำเร็จ!")
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถ Touch app.py ได้: {e}")
        return False

def push_to_github():
    """
    รัน git push เพื่อส่งข้อมูลความเปลี่ยนแปลงขึ้น GitHub กระตุ้นเซิร์ฟเวอร์ออนไลน์
    """
    try:
        import subprocess
        print("\n🐙 [Git] กำลังบันทึกประวัติและส่งข้อมูลขึ้น GitHub...")
        subprocess.run(["git", "add", "app.py", "worldcup.db", "update_results.py"], cwd=BASE_DIR, check=True)
        commit_msg = f"feat: Automated score update and cache flush via Peter AI ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=True)
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("🎉 [Git] ส่งข้อมูลขึ้น GitHub และสั่งล้างแคช RAM บนหน้าเว็บสำเร็จเสร็จสิ้น!")
        return True
    except Exception as e:
        print(f"❌ [Git] เกิดข้อผิดพลาดในการรันคำสั่ง git: {e}")
        return False

def main():
    print("🤖 เริ่มทำงานระบบ AI Auto-Update Results...")
    
    # 1. โหลดคีย์ Gemini
    api_key = ai.load_gemini_api_key()
    if not api_key:
        print("❌ ไม่พบ API Key ของ Gemini ระบบหยุดการทำงาน")
        return
        
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล SQLite ที่เส้นทาง {db_path}")
        return

    # 2. ค้นหาแมตช์ที่เลยเวลาเตะแล้วแต่สถานะยังคงเป็น 'Upcoming'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ดึงคู่แข่งขันที่ยังแข่งไม่เสร็จ
        cursor.execute("SELECT id, home_team, away_team, match_time FROM matches WHERE status='Upcoming'")
        upcoming_matches = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ ดึงข้อมูลจากฐานข้อมูลล้มเหลว: {e}")
        return

    if not upcoming_matches:
        print("😴 ไม่มีคู่แข่งขันที่มีสถานะ 'Upcoming' ในขณะนี้")
        return

    print(f"🔍 พบคู่แข่งขันที่รอการแข่งรวม {len(upcoming_matches)} คู่")
    
    # เวลาปัจจุบัน (เวลาเครื่องไทย UTC+7)
    now = datetime.now()
    
    any_updated = False
    last_match_info = None

    for m_id, home_team, away_team, match_time_str in upcoming_matches:
        try:
            # รูปแบบเวลาในฐานข้อมูลคือ 'YYYY-MM-DD HH:MM:SS'
            match_time = datetime.strptime(match_time_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"⚠️ รูปแบบเวลาของแมตช์ {m_id} ไม่ถูกต้อง ({match_time_str}): {e}")
            continue

        # ตรวจสอบว่าแมตช์นั้นเลยกำหนดเวลามาแล้วเกิน 2 ชั่วโมง 30 นาที หรือไม่ (เวลาแข่งเฉลี่ย 2 ชม.)
        # เพื่อป้องกันการค้นหาระหว่างที่บอลกำลังแข่งอยู่
        time_elapsed = now - match_time
        if time_elapsed < timedelta(hours=2, minutes=30):
            print(f"⏳ Match ID {m_id}: {home_team} vs {away_team} ({match_time_str}) ยังไม่แข่งหรือเพิ่งเริ่มเตะ (เพิ่งผ่านไป {time_elapsed}) ข้ามการค้นหา")
            continue

        print(f"\n📡 ตรวจสอบผล Match ID {m_id}: {home_team} vs {away_team} (เตะเมื่อ {match_time_str})...")
        
        result, model_used = get_finished_match_info(home_team, away_team, match_time_str, api_key)
        if not result:
            print(f"❌ ไม่สามารถดึงผลคะแนนสำหรับคู่ {home_team} vs {away_team} ได้")
            continue

        print(f"🤖 ผลลัพธ์จาก {model_used}: {result}")

        if result.get("status") == "Finished":
            h_score = result.get("home_score")
            a_score = result.get("away_score")
            scorers = result.get("scorers", "")
            
            winner_qualify = result.get("winner_qualify", "")
            if winner_qualify is None or str(winner_qualify).strip() == "" or str(winner_qualify).lower() == "null":
                winner_qualify = ""
                # Fallback: หากเป็นรอบน็อกเอาต์และสกอร์ไม่เสมอ ให้เดาผู้ชนะเป็นผู้เข้ารอบอัตโนมัติ
                try:
                    m_id_int = int(m_id)
                    if m_id_int >= 68:
                        if int(h_score) > int(a_score):
                            winner_qualify = home_team
                        elif int(a_score) > int(h_score):
                            winner_qualify = away_team
                except Exception:
                    pass
            
            if h_score is None or a_score is None:
                print(f"⚠️ ผลสกอร์ไม่สมบูรณ์ ข้ามการเขียนลงฐานข้อมูล")
                continue

            print(f"🔥 ค้นพบผลอย่างเป็นทางการ! {home_team} {h_score} - {a_score} {away_team} | ผู้เข้ารอบ: {winner_qualify}")
            
            # --- อัปเดตใน SQLite ---
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE matches SET home_score=?, away_score=?, status='Finished', scorers=?, winner_qualify=? WHERE id=?",
                    (int(h_score), int(a_score), scorers, winner_qualify, int(m_id))
                )
                conn.commit()
                conn.close()
                print(f"✅ SQLite อัปเดต ID {m_id} สำเร็จ!")
            except Exception as e:
                print(f"❌ อัปเดต SQLite สำหรับ ID {m_id} ล้มเหลว: {e}")
                continue

            # --- อัปเดตใน Google Sheets ---
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
                    print(f"✅ Google Sheets อัปเดต ID {m_id} สำเร็จ!")
                else:
                    print(f"⚠️ ไม่พบ Match ID {m_id} ใน Google Sheets เพื่อประสานข้อมูล")
            except Exception as e:
                print(f"❌ อัปเดต Google Sheets สำหรับ ID {m_id} ล้มเหลว: {e}")
                continue

            any_updated = True
            last_match_info = (home_team, away_team, h_score, a_score)

    if any_updated:
        # --- คำนวณสรุปผลคะแนนทั้งหมด ---
        print("\n🧮 กำลังคำนวณและสรุปแต้มทายผลประจำลีก...")
        try:
            db.update_scores_logic()
            print("🎉 คำนวณและแจกคะแนนสมาชิกทายผลสำเร็จ!")
        except Exception as e:
            print(f"❌ การคำนวณแต้มทายผลมีข้อผิดพลาด: {e}")

        # --- ทัชไฟล์และดัน Git เพื่อล้างแคช RAM บนเว็บจริง ---
        if last_match_info:
            touch_app_py(*last_match_info)
            push_to_github()
    else:
        print("\n😴 ไม่มีแมตช์ใหม่ที่จบการแข่งขันให้บันทึกในรอบนี้ครับ")

if __name__ == "__main__":
    main()
