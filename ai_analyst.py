import os
import json
import hashlib
import requests
import pandas as pd
from datetime import datetime

# ค้นหาไฟล์ .env และดึงคีย์ API ของ Gemini
def load_gemini_api_key():
    debug_log = []
    debug_log.append("--- Load Gemini API Key Debug ---")
    
    # 1. พยายามดึงคีย์จาก Streamlit Secrets (สำหรับกรณีรันบน Streamlit Cloud จริง)
    try:
        import streamlit as st
        api_key = st.secrets.get("GEMINI_API_KEY")
        debug_log.append(f"Streamlit Secrets (Root): {'Found' if api_key else 'Not Found'}")
        
        # เผื่อกรณีคุณอาร์ตวางคีย์เยื้องเข้าไปใต้กลุ่ม [gcp_service_account] ใน Dashboard Secrets
        if not api_key and "gcp_service_account" in st.secrets:
            gcp_sec = st.secrets["gcp_service_account"]
            if isinstance(gcp_sec, dict) or hasattr(gcp_sec, "get"):
                api_key = gcp_sec.get("GEMINI_API_KEY")
                debug_log.append(f"Streamlit Secrets (Nested in gcp_service_account): {'Found' if api_key else 'Not Found'}")
                
        if api_key:
            write_debug_key_log(debug_log)
            return api_key
    except Exception as e:
        debug_log.append(f"Streamlit Secrets Error: {e}")

    # 2. ดึงคีย์จากตัวแปรสภาพแวดล้อม (Environment Variables) เผื่อมีการเซ็ตไว้
    api_key = os.environ.get("GEMINI_API_KEY")
    debug_log.append(f"OS Environ: {'Found' if api_key else 'Not Found'}")
    if api_key:
        write_debug_key_log(debug_log)
        return api_key
    
    # 3. หากไม่มี ให้สแกนหาไฟล์ .env จากตู้หลักและโฟลเดอร์โครงการครอบคลุมถึงจุดสัมบูรณ์จริง
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.join(current_dir, ".env"),
        os.path.join(os.path.dirname(current_dir), ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.getcwd()), ".env"),
        "/Users/art/Desktop/ART_JOB/.env"  # เส้นทางสัมบูรณ์ตรงเป้าบนเครื่องแมคของคุณอาร์ต
    ]
    debug_log.append(f"current_dir: {current_dir}")
    debug_log.append(f"getcwd: {os.getcwd()}")
    
    for p in paths_to_try:
        exists = os.path.exists(p)
        debug_log.append(f"Path: {p} (Exists: {exists})")
        if exists:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for line_idx, line in enumerate(f, 1):
                        clean_line = line.strip().replace("\r", "").replace("\n", "")
                        debug_log.append(f"  Line {line_idx}: {repr(clean_line[:20])}...")
                        if clean_line.startswith("GEMINI_API_KEY="):
                            val = clean_line.split("=", 1)[1].strip()
                            # ลบอัญประกาศครอบ (ถ้ามี)
                            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                                val = val[1:-1]
                            debug_log.append(f"  -> Found GEMINI_API_KEY in {p} (Length: {len(val)})")
                            write_debug_key_log(debug_log)
                            return val
            except Exception as e:
                debug_log.append(f"  -> Error reading {p}: {e}")
                
    debug_log.append("Result: Key NOT Found")
    write_debug_key_log(debug_log)
    return None

def write_debug_key_log(log_lines):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(current_dir, "debug_key.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")
    except Exception:
        pass

# คำนวณรหัสแฮช (Hash Value) เพื่อตรวจสอบว่าข้อมูลหลักเปลี่ยนแปลงหรือไม่
def calculate_db_hash(leaderboard_df, matches_df):
    try:
        # ดึงสรุปรายชื่อผู้เล่นและคะแนนสะสมหลัก
        lead_str = ""
        if not leaderboard_df.empty:
            lead_str = "".join(leaderboard_df['username'].astype(str) + leaderboard_df['total_score'].astype(str))
        
        # ดึงสถานะผลการแข่งขันที่เสร็จสิ้น (Finished) และสกอร์จริง
        match_str = ""
        if not matches_df.empty:
            finished_matches = matches_df[matches_df['status'] == 'Finished']
            match_str = "".join(finished_matches['id'].astype(str) + finished_matches['home_score'].astype(str) + finished_matches['away_score'].astype(str))
            
        raw_str = f"{lead_str}_{match_str}"
        return hashlib.md5(raw_str.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"Error calculating hash: {e}")
        return "fallback_hash"

# เรียกติดต่อบริการเซิร์ฟเวอร์ Google Gemini API โดยตรงผ่านไลบรารี HTTP Requests 
def call_gemini_api(prompt, api_key):
    # เลือกรันโมเดลหลักประสิทธิภาพสูงตามลำดับความเสถียรเพื่อป้องกันปัญหา 503 (High Demand) และ 404 (Not Found)
    models = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.1-flash-lite"]
    
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
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4000
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                res_json = response.json()
                text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return text, model_name
            else:
                print(f"Gemini API returned error {response.status_code} for {model_name}: {response.text}")
        except Exception as e:
            print(f"Network error calling {model_name}: {e}")
            
    return None, None

# ประกอบชุดคำถาม (Prompt Construction) สำหรับส่งให้ AI สรุปวิเคราะห์
def build_analyst_prompt(leaderboard_df, matches_df, predictions_df):
    # 1. ข้อมูลทำเนียบผู้นำ 5 อันดับแรก
    leaderboard_text = ""
    if not leaderboard_df.empty:
        top_5 = leaderboard_df.head(5)
        for idx, (_, row) in enumerate(top_5.iterrows(), 1):
            leaderboard_text += f"อันดับ {idx}: {row['username']} ({row['total_score']} แต้ม)\n"
    else:
        leaderboard_text = "ยังไม่มีประวัติคะแนนสะสม\n"
    
    # 2. ผลการแข่งขัน 4 คู่ล่าสุดที่แข่งเสร็จแล้ว
    recent_matches = ""
    if not matches_df.empty:
        finished_matches = matches_df[matches_df['status'] == 'Finished'].copy()
        if not finished_matches.empty:
            finished_matches['id_int'] = pd.to_numeric(finished_matches['id'], errors='coerce').fillna(0).astype(int)
            latest_finished = finished_matches.sort_values('id_int', ascending=False).head(4)
            for _, row in latest_finished.iterrows():
                scorers_info = f" (ผู้ทำประตู: {row['scorers']})" if str(row['scorers']).strip() != "" else ""
                recent_matches += f"คู่ {row['home_team']} {row['home_score']}-{row['away_score']} {row['away_team']}{scorers_info}\n"
        else:
            recent_matches = "ยังไม่มีผลการแข่งขันที่จบอย่างเป็นทางการ\n"
    else:
        recent_matches = "ไม่มีข้อมูลการแข่งขัน\n"
                
    # 3. ตารางการแข่งขันนัดถัดไปล่วงหน้า (กรองเฉพาะวันพรุ่งนี้เป็นต้นไป)
    upcoming_matches = ""
    if not matches_df.empty:
        upcoming = matches_df[matches_df['status'] == 'Upcoming'].copy()
        if not upcoming.empty:
            upcoming['match_dt'] = pd.to_datetime(upcoming['match_time'])
            
            # กรองเฉพาะแมตช์ที่แข่งขันตั้งแต่วันพรุ่งนี้ (วันถัดไป) เป็นต้นไป เพื่อเลี่ยงคู่วันนี้ที่เตะอยู่
            tomorrow_start = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
            upcoming_future = upcoming[upcoming['match_dt'] >= tomorrow_start]
            
            # ป้องกันกรณีที่ตารางแข่งวันถัดไปหมด ให้ยอมใช้คู่อนาคตที่เหลืออยู่มาแทน
            if upcoming_future.empty:
                upcoming_future = upcoming
                
            upcoming_sorted = upcoming_future.sort_values('match_dt', ascending=True).head(6)
            for _, row in upcoming_sorted.iterrows():
                upcoming_matches += f"คู่ {row['home_team']} พบ {row['away_team']} วันที่ {pd.to_datetime(row['match_time']).strftime('%d/%m %H:%M น.')}\n"
        else:
            upcoming_matches = "ไม่มีตารางแข่งรอบถัดไปเร็วๆ นี้\n"
    else:
        upcoming_matches = "ไม่มีข้อมูลการแข่งขันล่วงหน้า\n"
                
    # 4. เจาะหาการทำนายสุดเป๊ะ (Perfect Prediction) หรือฟอร์มโดดเด่นในรอบล่าสุด เพื่อหาตัวท็อปเดลี
    prediction_trivia = ""
    if not predictions_df.empty and not matches_df.empty:
        merged = predictions_df.merge(matches_df, left_on='match_id', right_on='id')
        finished_predictions = merged[merged['status'] == 'Finished'].copy()
        if not finished_predictions.empty:
            # ค้นหา ID ของกลุ่มแมตช์ที่เสร็จสิ้นล่าสุด 4 นัด (ซึ่งเป็นกลุ่มคู่แข่งขันรอบล่าสุดของวันนี้)
            finished_predictions['id_int'] = pd.to_numeric(finished_predictions['id'], errors='coerce').fillna(0).astype(int)
            latest_match_ids = finished_predictions.sort_values('id_int', ascending=False).head(4)['id'].unique().tolist()
            
            # กรองข้อมูลการทำนายเฉพาะแมตช์ในกลุ่มรอบล่าสุดนี้
            recent_round_preds = finished_predictions[finished_predictions['match_id'].isin(latest_match_ids)].copy()
            
            # 4.1 ลองหาผู้ที่ทายถูกเป๊ะ (ได้ 3 แต้มเต็ม) ในกลุ่มแมตช์รอบล่าสุดนี้ก่อน
            perfect_recent = recent_round_preds[recent_round_preds['points_earned'].astype(str) == '3']
            if not perfect_recent.empty:
                for _, row in perfect_recent.sort_values('id_int', ascending=False).head(4).iterrows():
                    prediction_trivia += f"- คุณ {row['username']} ทายคู่ {row['home_team']} vs {row['away_team']} ได้ผลลัพธ์ {row['pred_home']}-{row['pred_away']} ตรงเผงสะเทือนวงการ! (รับ 3 แต้มเต็มในนัดล่าสุดวันนี้)\n"
            else:
                # 4.2 หากรอบล่าสุดนี้ไม่มีใครทายสกอร์เป๊ะเลย ให้หาผู้เดาทิศทางถูก (รับ 1 แต้มสำคัญ) ในรอบล่าสุดนี้มาไฮไลท์แทน เพื่อให้เกาะติดกระแสข่าววันนี้
                correct_dir_recent = recent_round_preds[recent_round_preds['points_earned'].astype(str) == '1']
                if not correct_dir_recent.empty:
                    prediction_trivia += "*(หมายเหตุสำหรับ AI: แมตช์ล่าสุดวันนี้ไม่มีใครเดาสกอร์เป๊ะ 3 แต้ม แต่มีผู้ทายทิศทางผู้ชนะ/เสมอได้ถูกต้องรับ 1 แต้มเด่น ได้แก่)*\n"
                    # ดึงผู้เล่นฟอร์มดี 4 คนล่าสุดของรอบนี้
                    for _, row in correct_dir_recent.sort_values('id_int', ascending=False).head(4).iterrows():
                        prediction_trivia += f"- คุณ {row['username']} เดาทางคู่ {row['home_team']} vs {row['away_team']} ได้ถูกต้อง (ทาย {row['pred_home']}-{row['pred_away']} | ผลจริง {row['home_score']}-{row['away_score']}) คว้า 1 แต้มสว่างวาบของวันนี้!\n"
            
            # 4.3 กรณีที่รอบล่าสุดไม่มีคะแนนเลยจริงๆ (เช่นเพิ่งเปิดวันใหม่และยังไม่มีใครแข่งเสร็จ) ค่อยตกกลับไปใช้ Perfect 3 แต้มในอดีตมาแสดงประคองไว้ก่อน
            if not prediction_trivia:
                perfect_all = finished_predictions[finished_predictions['points_earned'].astype(str) == '3'].copy()
                if not perfect_all.empty:
                    for _, row in perfect_all.sort_values('id_int', ascending=False).head(4).iterrows():
                        prediction_trivia += f"- คุณ {row['username']} ทายคู่ {row['home_team']} vs {row['away_team']} ได้ผลลัพธ์ {row['pred_home']}-{row['pred_away']} ตรงเผงสะเทือนวงการ! (รับ 3 แต้มเต็มในนัดก่อนหน้านี้)\n"
    
    if not prediction_trivia:
        prediction_trivia = "- ช่วงนี้ผลการทายค่อนข้างคลาดเคลื่อน ไม่มีคะแนนใหม่ถูกบันทึกในนัดล่าสุดครับ\n"

    prompt = f"""
คุณคือ "ปีเตอร์" (Peter) AI นักวิเคราะห์ฟุตบอลอัจฉริยะ (AI Analyst) และผู้ดำเนินรายการผู้รอบรู้ประจำเว็บทายผลบอลโลก CRAZYFIFA 2026 ของคุณอาร์ต
หน้าที่ของคุณคือเขียนบทวิเคราะห์สรุปความเคลื่อนไหวประจำวันแบบสั้น กระชับ มีสีสัน น่าตื่นเต้น และทรงพลังเหมือนผู้บรรยายกีฬาระดับมืออาชีพ

ข้อมูลสถานะปัจจุบันของลีกทายผล:
=== ตารางคะแนนผู้นำสูงสุด (Top 5 Leaderboard) ===
{leaderboard_text}

=== ผลการแข่งขันล่าสุด (Recent Results) ===
{recent_matches}

=== แมตช์ต่อไปที่กำลังจะมาถึง (Upcoming Matches) ===
{upcoming_matches}

=== เกร็ดการทายผลแม่นยำล่าสุด (Recent Perfect Predictions) ===
{prediction_trivia}

คำแนะนำและกฎในการเขียนวิเคราะห์ (Strict Rules):
1. เริ่มต้นด้วยประโยคแนะนำตัวและทักทายสั้นๆ กระชับในฐานะ "ปีเตอร์" โดยใช้รหัสตัวแปรต้นแบบ `{{USERNAME}}` ตรงตัวเป๊ะๆ เช่น "สวัสดีครับคุณ {{USERNAME}} และเหล่านักล่าแต้มทุกคน! ผม \"ปีเตอร์\" AI..." โดยคุณต้องพิมพ์คำว่า `{{USERNAME}}` ห้ามเปลี่ยนเป็นชื่ออื่นเป็นอันขาด เพื่อที่ระบบส่วนหน้า (Frontend) จะนำคำนี้ไปแทนที่ด้วยชื่อจริงของผู้ใช้ที่ล็อกอิน ณ ขณะนั้นแบบไดนามิก (Dynamic: ยืดหยุ่นเคลื่อนไหวได้ตลอดเวลา) เสมอ
2. วิเคราะห์หา "Daily MVP" (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน) จากข้อมูลด้านบน (เช่น คนที่ทายผลได้ 3 คะแนนเต็มล่าสุด หรือผู้ที่เก็บคะแนนยึดจ่าฝูงลีดเดอร์บอร์ดอย่างมั่นคง) โดยขิงและแซวสั้นๆ อย่างเฮฮาสนุกสนาน
3. สรุปภาพรวมตารางคะแนนสั้นๆ (เช่น จ่าฝูงสั่นคลอนไหม หรือมีใครกำลังฟอร์มแรงไล่จี้ตูดขึ้นมา)
4. โหมโรงถึงคู่แข่งขันที่กำลังจะมาถึงในวันถัดไปหรือนัดถัดไปล่วงหน้า 2-4 คู่ เพื่อให้ผู้ใช้เตรียมทายผลล่วงหน้าได้ทันท่วงที โดยวิจารณ์เชิงหยอกล้อ และสำหรับทุกคู่ที่หยิบยกมาวิเคราะห์ คุณต้องนำเสนอ "สถิติการพบกันย้อนหลัง (Head-to-Head)" จากคลังความรู้ฟุตบอลในตัวคุณมาประมาณการเป็นสถิติเปอร์เซ็นต์สั้นกระชับ 1 บรรทัดเสมอ ในรูปแบบ: `สถิติเจอกัน (H2H): [ทีมเหย้า] ชนะ XX% | เสมอ YY% | [ทีมเยือน] ชนะ ZZ%`
5. ใช้ภาษาไทยที่มีชีวิตชีวา มีเสน่ห์ลีลาการวิจารณ์ฟุตบอล ใส่พริกความกวนและสไตล์ผู้บรรยายเกม ใส่ใจความปลอดภัยและเน้นความกระชับสวยงามของเอกสาร
6. กฎสำคัญที่สุด: ทุกครั้งที่ใช้คำศัพท์เทคนิค (Technical Terms) ให้เขียนคำอ่านและความหมายใส่ไว้ในวงเล็บต่อท้ายคำศัพท์นั้นโดยตรง (In-line Parentheses) เสมอ เช่น Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน), Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)
7. ควบคุมเนื้อหารวมให้กระชับและคุ้มค่าตัวอักษรมากที่สุด (ความยาวประมาณ 150-250 คำ) เพื่อให้แสดงผลได้อย่างงดงามและเรียบหรูในแผ่น Dashboard โดยไม่กินพื้นที่มากเกินไป
8. เสริมความพรีเมียมและสวยงามด้วยสีสันและโครงสร้างหัวข้อแบบ HTML เนื่องจากตัวเรนเดอร์ส่วนหน้าเว็บรองรับความปลอดภัยในการแปลผล:
   - ใช้แท็ก <hr style="border: 0; border-top: 1px solid rgba(255, 215, 0, 0.1); margin: 12px 0;"> ขีดคั่นระหว่างส่วนหลักทั้ง 3 ส่วนเพื่อให้หน้าตาสะอาดอ่านง่ายสไตล์บอร์ดแดชบอร์ดระดับพรีเมียม
   - แต่งเติมสีสันให้หัวข้อสำคัญสว่างสะดุดตา เช่น:
     * ส่วนวิเคราะห์รางวัลโดดเด่น: 🏆 <span style="color: #00FF87; font-weight: bold;">วิเคราะห์ Daily MVP ประจำวัน</span> (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน)
     * ส่วนตารางคะแนน: 📊 <span style="color: #00E5FF; font-weight: bold;">ความเคลื่อนไหวบน Leaderboard</span> (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)
     * ส่วนคู่เดือดล่วงหน้า: 🔥 <span style="color: #FF5E36; font-weight: bold;">โหมโรงศึกเดือดสะท้านตารางวันถัดไป</span> (ศึกเปลี่ยนชีวิตล่วงหน้า)
   - สำหรับรายชื่อทีมและคู่แข่งขันที่เป็น บิ๊กแมตช์ (Big Match) คู่นัดตัดสิน หรือนัดสำคัญของคืน ให้เน้นด้วยป้ายเรืองแสงส้มสว่างสดใสเพื่อความโดดเด่นสะดุดตาดังนี้เสมอ: <span class="big-match">[ชื่อเจ้าบ้าน] พบ [ชื่อทีมเยือน]</span>
   - ในบรรทัดสรุปสถิติการพบกันย้อนหลัง (H2H) ให้แสดงด้วยดีไซน์ตัวอักษรสีทองอร่ามสว่างกะทัดรัด ไม่ยาวเทอะทะ และเรียบหรูสไตล์โปรแกรมข้อมูลกีฬา โดยให้ครอบด้วยแท็ก HTML รูปแบบนี้เป๊ะๆ เสมอ:
     <div style="font-size: 0.85rem; color: #FFD700; opacity: 0.95; margin: 4px 0 8px 10px; font-family: 'Kanit', sans-serif, monospace; font-weight: bold; text-shadow: 0 0 8px rgba(255, 215, 0, 0.2);">📊 สถิติเจอกัน (H2H): [ทีมเจ้าบ้าน] ชนะ XX% | เสมอ YY% | [ทีมเยือน] ชนะ ZZ%</div>
9. ห้ามใส่เครื่องหมาย backtick (`) ครอบแท็ก HTML หรือครอบส่วนที่มีแท็ก HTML เป็นอันขาด เนื่องจากจะทำให้ Markdown Engine แปลผลเป็นข้อความโค้ดดิบและไม่เรนเดอร์สีสันสปันสีทองสวยงามบนหน้าจอ

เขียนบทสรุปวิเคราะห์สั้นๆ ประจำวันของคุณได้เลยครับ:
"""
    return prompt

# ฟังก์ชันหลักสำหรับดึงบทวิเคราะห์ (ดึงจาก Cache หรือดึงจาก API จริงกรณีข้อมูลอัปเดต)
def get_ai_summary(leaderboard_df, matches_df, predictions_df, force_refresh=False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(current_dir, "ai_cache.json")
    
    # 1. คำนวณรหัสแฮชเพื่อดูการเปลี่ยนแปลงข้อมูล
    current_hash = calculate_db_hash(leaderboard_df, matches_df)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # ดีบักแฮชเพื่อหาสาเหตุที่แคชหลุดบนระบบจริง
    try:
        debug_log_path = os.path.join(current_dir, "debug_hash.log")
        with open(debug_log_path, "w", encoding="utf-8") as df_log:
            df_log.write(f"date: {today_str}\n")
            df_log.write(f"current_hash: {current_hash}\n")
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    df_log.write(f"cached_hash: {cache_data.get('hash_key')}\n")
                    df_log.write(f"cached_date: {cache_data.get('date')}\n")
            else:
                df_log.write("cache file does not exist\n")
    except Exception as e:
        pass
    
    # 2. ตรวจสอบ Cache ท้องถิ่นก่อนรันงานจริง (เพื่อประหยัดโควตาและเร่งความเร็วในการโหลดหน้าจอ)
    if not force_refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                # ตรวจสอบว่าแฮชตรงกันและวันที่ตรงกันหรือไม่ (ให้เจนใหม่วันละครั้ง หรือเมื่อคะแนนมีการเปลี่ยนแปลง)
                if cache_data.get("hash_key") == current_hash and cache_data.get("date") == today_str:
                    return cache_data.get("content"), cache_data.get("model_used", "Gemini 2.5 Flash"), True
        except Exception as e:
            print(f"Error reading AI cache: {e}")

    # 3. หากต้องการอัปเดตใหม่ หรือไม่มีแคชเดิม ให้เรียกเชื่อมประสานหา API จริง
    api_key = load_gemini_api_key()
    if not api_key:
        # หากไม่พบคีย์ ให้ส่งสัญญาณเตือนอย่างปลอดภัยโดยระบบหลักไม่พังเสียหาย
        return "⚠️ ไม่พบคีย์ `GEMINI_API_KEY` ในไฟล์สภาพแวดล้อม `.env` กรุณาตั้งค่าคีย์เพื่อเปิดใช้งานระบบผู้ช่วยวิเคราะห์ AI อัจฉริยะครับ", "ระบบออฟไลน์", False

    prompt = build_analyst_prompt(leaderboard_df, matches_df, predictions_df)
    ai_text, model_name = call_gemini_api(prompt, api_key)
    
    if ai_text:
        # 4. จัดการจัดเก็บแคชลงไฟล์โลคัลเพื่อใช้ซ้ำรอบถัดไป
        try:
            cache_payload = {
                "date": today_str,
                "hash_key": current_hash,
                "content": ai_text,
                "model_used": model_name,
                "generated_at": datetime.now().isoformat()
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving AI cache: {e}")
            
        return ai_text, model_name, False
    
    # หากเกิดเหตุสุดวิสัยหรือปัญหาเครือข่าย ให้พยายามดึงแคชเดิม (แม้รหัสแฮชจะไม่ตรง) มาแสดงประทังไว้ก่อน
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                return cache_data.get("content") + "\n\n*(⚠️ ข้อความจากแคชเดิมเนื่องจากระบบเชื่อมต่อเซิร์ฟเวอร์ AI มีความขัดข้องชั่วคราว)*", cache_data.get("model_used", "Fallback"), True
        except:
            pass
            
    return "🎙️ ปีเตอร์รายงานตัวครับ! ตอนนี้เซิร์ฟเวอร์ปัญญาประดิษฐ์กำลังพักครึ่งสนามชั่วคราว ไม่สามารถดึงรายงานสดได้ในเวลานี้ โปรดลองใหม่อีกครั้งในภายหลังครับ", "ระบบออฟไลน์", False
