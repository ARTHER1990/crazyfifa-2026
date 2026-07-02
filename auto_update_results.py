import sys
import os
import sqlite3
import pandas as pd
import requests
import json
import re
import time
from datetime import datetime, timedelta, timezone

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db
import ai_analyst as ai

def get_finished_match_info(home_team, away_team, match_time, api_key, m_id=None):
    """
    ใช้ Gemini API พร้อม Search Grounding ค้นหาผลการแข่งขันจากเว็บอย่างเป็นทางการ
    """
    is_knockout = False
    match_type_desc = "Group Stage match"
    if m_id is not None:
        try:
            if int(m_id) >= 68:
                is_knockout = True
                match_type_desc = "KNOCKOUT match (Round of 16, Quarter-finals, Semi-finals, or Final)"
        except ValueError:
            pass

    prompt = f"""
    Please search the official web or reliable sources to find the final score and scorers for the 2026 FIFA World Cup match:
    Home Team: {home_team}
    Away Team: {away_team}
    Match Scheduled Time (UTC+7): {match_time}
    Match Type: {match_type_desc} (Match ID: {m_id})

    If the match is finished, please return a JSON object with the following fields:
    - status: "Finished"
    - home_score: (integer, number of goals scored by {home_team} at the end of normal/extra time)
    - away_score: (integer, number of goals scored by {away_team} at the end of normal/extra time)
    - scorers: (string, list of goal scorers with minutes in format: "Scorer Home (minute) | Scorer Away (minute)". Example: "Daizen Maeda (56) | Anthony Elanga (62)". If no goal or no data, use empty string "" or draw line "|")
    - winner: (string, the name of the winning team at 90/120 mins, or "Draw" if the score is tied, or null if not finished)
    - winner_qualify: (string, the exact name of the team that qualified to the next round / won the match including extra time or penalty shootout, e.g., "Germany" or "Brazil". For KNOCKOUT matches, if the score is a draw (e.g., 1-1, 2-2), you MUST search carefully to find which team advanced to the next round via penalty shootout or extra time. Must be one of the exact team names: "{home_team}" or "{away_team}". If the match is not finished, or it is a group stage match, use empty string "")

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
    models = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
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
            elif response.status_code == 429:
                print(f"⚠️ {model_name} เจอ Rate Limit (429 Resource Exhausted) - หยุดทำการส่งคำขอและรอคูลดาวน์...")
                time.sleep(30) # พักผ่อนทันที 30 วินาที
                break # หากกุญแจโดนบล็อกแล้ว ให้ข้ามลูปโมเดลอื่นในคู่นี้ไปเลยเพื่อไม่ให้โดนแบนเพิ่ม
            else:
                print(f"⚠️ {model_name} Error {response.status_code}: {response.text[:200]}")
                time.sleep(5) # ดีเลย์ 5 วินาทีก่อนจะลองสลับรุ่นโมเดล (ลดปัญหา Quick Retry)
        except Exception as e:
            print(f"⚠️ ข้อผิดพลาดในการติดต่อโมเดล {model_name}: {e}")
            time.sleep(5)
            
    return None, None

def get_finished_matches_batch_info(matches_list, api_key):
    """
    ใช้ Gemini API พร้อม Search Grounding ค้นหาผลการแข่งขันของหลายๆ คู่พร้อมกันในการเรียกครั้งเดียว (Batch Mode)
    """
    matches_text = ""
    for m_id, home_team, away_team, match_time, m_status in matches_list:
        is_knockout = "Yes" if int(m_id) >= 68 else "No"
        matches_text += f"- Match ID: {m_id} | {home_team} vs {away_team} | Scheduled Time (UTC+7): {match_time} | Knockout Match: {is_knockout}\n"

    prompt = f"""
    You are an expert sports data analyst. Please search official and reliable sources (especially FIFA.com) to find the official results of the following 2026 FIFA World Cup matches:

    {matches_text}

    For each match in the list, please analyze whether it is finished. If finished, provide the final score, scorers, and knockout winner if applicable.
    
    You must respond with a JSON object where the keys are the string representation of Match IDs (e.g. "5", "6") and the values are objects with the following fields:
    - status: "Finished" if the match is officially finished, "Upcoming" if not finished or hasn't started yet.
    - home_score: (integer, goals scored by home team at the end of normal/extra time, or null if upcoming)
    - away_score: (integer, goals scored by away team at the end of normal/extra time, or null if upcoming)
    - scorers: (string, format: "Scorer Home (minute) | Scorer Away (minute)". If no goals or no data, use empty string "" or "|")
    - winner: (string, winning team at 90/120 mins, or "Draw" if tied, or null if upcoming)
    - winner_qualify: (string, exact name of team that qualified to the next round / won the match including extra time or penalty shootouts. Must be one of the exact team names. Only applicable for Knockout matches. If not a knockout match or not finished, use empty string "")

    Respond ONLY with a valid JSON block containing all requested matches. Do not add markdown fencing or explanation.
    """

    # ใช้ระบบ fallback โมเดลที่พร้อมใช้งานจริง
    models = ["gemini-2.5-flash", "gemini-2.5-pro"]
    
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
            print(f"📡 ส่งคำขอค้นหาข้อมูลผลบอลแบบ Batch ไปยัง {model_name}...")
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            if response.status_code == 200:
                res_json = response.json()
                text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # ใช้ regular expression สกัดปีกกา JSON
                match_json = re.search(r'\{.*\}', text, re.DOTALL)
                if match_json:
                    return json.loads(match_json.group(0)), model_name
                else:
                    return json.loads(text), model_name
            elif response.status_code == 429:
                print(f"⚠️ {model_name} เจอ Rate Limit (429) ในโหมด Batch - หยุดรอดูผลคูลดาวน์...")
                time.sleep(30)
                break
            else:
                print(f"⚠️ {model_name} Error {response.status_code}: {response.text[:200]}")
                time.sleep(5)
        except Exception as e:
            print(f"⚠️ ข้อผิดพลาดในการติดต่อโมเดล {model_name} ในโหมด Batch: {e}")
            time.sleep(5)
            
    return None, None

def touch_app_py(home_t, away_t, h_score, a_score):
    """
    อัปเดตความคิดเห็นบรรทัดแรกใน app.py เพื่อกระตุ้นให้ Streamlit Cloud ทำการ Auto-redeploy และล้างแคช RAM
    """
    app_path = os.path.join(BASE_DIR, 'app.py')
    try:
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        now_str = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
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
        
        # 1. แอดไฟล์ธรรมดา
        for file_name in ["app.py", "update_results.py"]:
            try:
                subprocess.run(["git", "add", file_name], cwd=BASE_DIR, check=False)
            except Exception as e:
                print(f"⚠️ ไม่สามารถแอดไฟล์ {file_name}: {e}")
                
        # 2. แอดไฟล์ worldcup.db โดยใช้แฟลก -f บังคับเนื่องจากติด .gitignore
        try:
            subprocess.run(["git", "add", "-f", "worldcup.db"], cwd=BASE_DIR, check=False)
        except Exception as e:
            print(f"⚠️ ไม่สามารถแอด -f worldcup.db: {e}")
            
        # 3. ลองรัน commit (ยอมให้ผ่านไปได้แม้ทำงานไม่มีการเปลี่ยนแปลงจริง)
        now_th = datetime.now(timezone(timedelta(hours=7))).strftime('%Y-%m-%d %H:%M')
        commit_msg = f"feat: Automated score update and cache flush via Peter AI ({now_th})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE_DIR, check=False)
        
        # 4. รัน git push ส่งข้อมูลขึ้นเซิร์ฟเวอร์
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        print("🎉 [Git] ส่งข้อมูลขึ้น GitHub และสั่งล้างแคช RAM บนหน้าเว็บสำเร็จเสร็จสิ้น!")
        return True
    except Exception as e:
        print(f"❌ [Git] เกิดข้อผิดพลาดในการรันคำสั่ง git push: {e}")
        return False


def main():
    print("🤖 เริ่มทำงานระบบ AI Auto-Update Results (Batch-First)...")
    
    # 1. โหลดคีย์ Gemini
    api_key = ai.load_gemini_api_key()
    if not api_key:
        print("❌ ไม่พบ API Key ของ Gemini ระบบหยุดการทำงาน")
        return
        
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล SQLite ที่เส้นทาง {db_path}")
        return

    # 2. ค้นหาแมตช์ที่เลยเวลาเตะแล้วแต่สถานะยังคงเป็น 'Upcoming' หรือแมตช์ที่แข่งเสร็จในรอบน็อกเอาต์แล้วแต่ไม่มีผู้เข้ารอบสะสม
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ดึงคู่แข่งขันที่ยังแข่งไม่เสร็จ หรือคู่ที่จบแล้วในรอบน็อกเอาต์ (ID >= 68) แต่ขาดผู้เข้ารอบสะสม (winner_qualify)
        cursor.execute("""
            SELECT id, home_team, away_team, match_time, status 
            FROM matches 
            WHERE status='Upcoming' 
               OR (status='Finished' AND id >= 68 AND (winner_qualify IS NULL OR TRIM(winner_qualify) = ''))
        """)
        upcoming_matches = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"❌ ดึงข้อมูลจากฐานข้อมูลล้มเหลว: {e}")
        return

    if not upcoming_matches:
        print("😴 ไม่มีคู่แข่งขันที่มีสถานะ 'Upcoming' หรือน็อกเอาต์ที่ขาดผู้เข้ารอบสะสมในขณะนี้")
        return

    # บังคับใช้เวลาปัจจุบันเป็นเวลาไทย (UTC+7) เสมอ เพื่อแก้ปัญหาเมื่อรันบนเซิร์ฟเวอร์ GitHub Actions (UTC)
    now = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    
    # กรองเฉพาะคู่แข่งขันที่เลยเวลาเตะ/ถึงเวลาอัปเดตผลแล้วจริงๆ เพื่อนำมาทำเป็น Batch
    matches_to_query = []
    for m_id, home_team, away_team, match_time_str, m_status in upcoming_matches:
        try:
            match_time = datetime.strptime(match_time_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"⚠️ รูปแบบเวลาของแมตช์ {m_id} ไม่ถูกต้อง ({match_time_str}): {e}")
            continue

        if m_status == 'Upcoming':
            time_elapsed = now - match_time
            if time_elapsed < timedelta(hours=2, minutes=30):
                print(f"⏳ Match ID {m_id}: {home_team} vs {away_team} ({match_time_str}) ยังไม่แข่งหรือเพิ่งเริ่มเตะ (ผ่านไป {time_elapsed}) ข้ามการอัปเดตในรอบนี้")
                continue
        
        matches_to_query.append((m_id, home_team, away_team, match_time_str, m_status))

    if not matches_to_query:
        print("😴 ไม่มีคู่แข่งขันที่พร้อมสแกนหาผลคะแนนในรอบนี้ครับ")
        return

    print(f"🔍 พบคู่แข่งขันที่พร้อมอัปเดตผลจำนวน {len(matches_to_query)} คู่ (เข้าสู่โหมดการสืบค้นรวบยอด Batch)")

    any_updated = False
    last_match_info = None
    batch_results = None
    model_used = None

    # --- ขั้นตอนรวบยอด Batch ---
    try:
        batch_results, model_used = get_finished_matches_batch_info(matches_to_query, api_key)
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดในระบบประมวลผลสรุปรวม Batch: {e}")

    # ตัวแปรสำหรับเก็บผลการแข่งขันที่จะเขียนลงฐานข้อมูล
    processed_matches = {}

    if batch_results and isinstance(batch_results, dict):
        print(f"🎉 ได้รับข้อมูลรวบยอด Batch เรียบร้อยจาก {model_used}!")
        processed_matches = batch_results
    else:
        # --- Fallback: หากระบบ Batch ทำงานล้มเหลว ให้กลับมาเรียกใช้แบบแยกทีละคู่ (Single Query) เพื่อความเสถียรสูงสุด ---
        print("⚠️ ระบบรวบยอด Batch ล้มเหลว! กำลังเริ่มระบบสำรองค้นหาทีละคู่ (Single Match Query Fallback)...")
        for m_id, home_team, away_team, match_time_str, m_status in matches_to_query:
            print(f"\n📡 [Fallback] ค้นหาผล Match ID {m_id}: {home_team} vs {away_team}...")
            result, single_model = get_finished_match_info(home_team, away_team, match_time_str, api_key, m_id)
            
            # มีระบบนอนหลับเพื่อป้องกัน Rate limit
            print("⏳ [Fallback] หน่วงเวลา 20 วินาทีตามสเปกความปลอดภัย...")
            time.sleep(20)

            if result:
                processed_matches[str(m_id)] = result

    # --- นำผลลัพธ์ที่ประมวลผลเสร็จแล้วมาบันทึกลงระบบ (SQLite & Google Sheets) ---
    for m_id, home_team, away_team, match_time_str, m_status in matches_to_query:
        m_id_str = str(m_id)
        if m_id_str not in processed_matches:
            continue

        result = processed_matches[m_id_str]
        if not result or result.get("status") != "Finished":
            continue

        h_score = result.get("home_score")
        a_score = result.get("away_score")
        scorers = result.get("scorers", "")
        winner_qualify = result.get("winner_qualify", "")

        if h_score is None or a_score is None:
            print(f"⚠️ สกอร์ของ Match ID {m_id} ไม่สมบูรณ์ ข้ามการเขียนข้อมูล")
            continue

        if winner_qualify is None or str(winner_qualify).strip() == "" or str(winner_qualify).lower() == "null":
            winner_qualify = ""
            # Fallback คำนวณผู้ชนะรอบน็อกเอาต์แบบนุ่มนวล
            try:
                if int(m_id) >= 68:
                    if int(h_score) > int(a_score):
                        winner_qualify = home_team
                    elif int(a_score) > int(h_score):
                        winner_qualify = away_team
            except Exception:
                pass

        print(f"🔥 บันทึกผลแมตช์อย่างเป็นทางการ! Match ID {m_id}: {home_team} {h_score} - {a_score} {away_team} | ผู้เข้ารอบ: {winner_qualify}")

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
            print(f"❌ อัปเดต SQLite ID {m_id} ล้มเหลว: {e}")
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
                print(f"⚠️ ไม่พบ Match ID {m_id} ใน Google Sheets เพื่ออัปเดต")
        except Exception as e:
            print(f"❌ อัปเดต Google Sheets ID {m_id} ล้มเหลว: {e}")
            continue

        any_updated = True
        last_match_info = (home_team, away_team, h_score, a_score)

    # --- หากมีการบันทึกคะแนนใหม่ ค่อยคำนวณแจกแต้มสรุปคะแนนประจำลีก ---
    if any_updated:
        print("\n🧮 กำลังคำนวณและสรุปแต้มทายผลประจำลีก...")
        try:
            db.update_scores_logic()
            print("🎉 คำนวณและแจกคะแนนสมาชิกทายผลสำเร็จ!")
        except Exception as e:
            print(f"❌ การคำนวณแต้มทายผลมีข้อผิดพลาด: {e}")

        # --- ทัชไฟล์และดัน Git เพื่อล้างแคช RAM บนหน้าเว็บจริง ---
        if last_match_info:
            touch_app_py(*last_match_info)
            push_to_github()
    else:
        print("\n😴 ไม่มีแมตช์ใหม่ที่เตะจบให้บันทึกในรอบนี้ครับ")

if __name__ == "__main__":
    main()
