import os
import json
import hashlib
import requests
import pandas as pd
from datetime import datetime

# ค้นหาไฟล์ .env และดึงคีย์ API ของ Gemini
def load_gemini_api_key():
    # ดึงคีย์จากตัวแปรสภาพแวดล้อม (Environment Variables) เผื่อมีการเซ็ตไว้
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # หากไม่มี ให้สแกนหาไฟล์ .env จากตู้หลักและโฟลเดอร์โครงการ
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths_to_try = [
        os.path.join(current_dir, ".env"),
        os.path.join(os.path.dirname(current_dir), ".env")
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        val = line.strip().split("=", 1)[1].strip()
                        # ลบอัญประกาศครอบ (ถ้ามี)
                        if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                            val = val[1:-1]
                        return val
    return None

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
    # เลือกรันโมเดลหลัก Gemini 2.5 Flash ทรงพลังความเร็วสูง หรือย้อนกลับไปใช้ Gemini 1.5 Flash เป็นทางเลือกสำรอง (Fallback)
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    
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
                "maxOutputTokens": 1000
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
                
    # 3. ตารางการแข่งขัน 3 นัดถัดไป
    upcoming_matches = ""
    if not matches_df.empty:
        upcoming = matches_df[matches_df['status'] == 'Upcoming'].copy()
        if not upcoming.empty:
            upcoming['match_dt'] = pd.to_datetime(upcoming['match_time'])
            upcoming_sorted = upcoming.sort_values('match_dt', ascending=True).head(3)
            for _, row in upcoming_sorted.iterrows():
                upcoming_matches += f"คู่ {row['home_team']} พบ {row['away_team']} วันที่ {pd.to_datetime(row['match_time']).strftime('%d/%m %H:%M น.')}\n"
        else:
            upcoming_matches = "ไม่มีตารางแข่งรอบถัดไปเร็วๆ นี้\n"
    else:
        upcoming_matches = "ไม่มีข้อมูลการแข่งขันล่วงหน้า\n"
                
    # 4. เจาะหาการทำนายสุดเป๊ะ (Perfect Prediction) ล่าสุด เพื่อหาตัวท็อปเดลี
    prediction_trivia = ""
    if not predictions_df.empty and not matches_df.empty:
        merged = predictions_df.merge(matches_df, left_on='match_id', right_on='id')
        finished_predictions = merged[merged['status'] == 'Finished'].copy()
        if not finished_predictions.empty:
            perfect_predictions = finished_predictions[finished_predictions['points_earned'].astype(str) == '3'].copy()
            if not perfect_predictions.empty:
                perfect_predictions['id_int'] = pd.to_numeric(perfect_predictions['id'], errors='coerce').fillna(0).astype(int)
                recent_perfect = perfect_predictions.sort_values('id_int', ascending=False).head(4)
                for _, row in recent_perfect.iterrows():
                    prediction_trivia += f"- คุณ {row['username']} ทายคู่ {row['home_team']} vs {row['away_team']} ได้ผลลัพธ์ {row['pred_home']}-{row['pred_away']} ตรงเผงสะเทือนวงการ! (รับ 3 แต้มเต็ม)\n"
    
    if not prediction_trivia:
        prediction_trivia = "- ช่วงนี้ผลการทายค่อนข้างคลาดเคลื่อน ไม่มีใครเก็บ 3 แต้มเต็มได้ในนัดล่าสุดครับ\n"

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
1. เริ่มต้นด้วยการแนะนำตัวสั้นๆ และกระชับในฐานะ "ปีเตอร์" รายงานสถานการณ์รอบวันให้คุณอาร์ตและผองเพื่อนผู้ร่วมทายผลทราบ
2. วิเคราะห์หา "Daily MVP" (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน) จากข้อมูลด้านบน (เช่น คนที่ทายผลได้ 3 คะแนนเต็มล่าสุด หรือผู้ที่เก็บคะแนนยึดจ่าฝูงลีดเดอร์บอร์ดอย่างมั่นคง) โดยขิงและแซวสั้นๆ อย่างเฮฮาสนุกสนาน
3. สรุปภาพรวมตารางคะแนนสั้นๆ (เช่น จ่าฝูงสั่นคลอนไหม หรือมีใครกำลังฟอร์มแรงไล่จี้ตูดขึ้นมา)
4. โหมโรงถึงคู่แข่งขันที่กำลังจะมาถึงในนัดถัดไป 1-2 คู่ โดยวิจารณ์เชิงหยอกล้อว่าคู่เหล่านี้จะเป็นนัดเปลี่ยนชีวิตของผู้ทายผลคนไหนบ้าง
5. ใช้ภาษาไทยที่มีชีวิตชีวา มีเสน่ห์ลีลาการวิจารณ์ฟุตบอล ใส่พริกความกวนและสไตล์ผู้บรรยายเกม ใส่ใจความปลอดภัยและเน้นความกระชับสวยงามของเอกสาร
6. กฎสำคัญที่สุด: ทุกครั้งที่ใช้คำศัพท์เทคนิค (Technical Terms) ให้เขียนคำอ่านและความหมายใส่ไว้ในวงเล็บต่อท้ายคำศัพท์นั้นโดยตรง (In-line Parentheses) เสมอ เช่น Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน), Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)
7. ควบคุมเนื้อหารวมให้กระชับและคุ้มค่าตัวอักษรมากที่สุด (ความยาวประมาณ 150-250 คำ) เพื่อให้แสดงผลได้อย่างงดงามและเรียบหรูในแผ่น Dashboard โดยไม่กินพื้นที่มากเกินไป

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
