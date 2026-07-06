import sys
import os
import time

# ตั้งค่า path ให้เรียกโมดูลอื่นๆ ได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db
import ai_analyst

def main():
    print("🚀 เริ่มระบบอัปเดตบทวิเคราะห์ปีเตอร์ AI และสร้างเสียงพากย์แบบ Sync บนเครื่องโลคัล...")
    
    # 1. โหลดข้อมูลจาก SQLite (ซึ่งเราซิงก์จาก Google Sheets มาเรียบร้อยแล้ว)
    leaderboard = db.get_leaderboard()
    matches = db.get_matches()
    predictions = db.get_predictions_df()
    
    print(f"📊 โหลดผู้เล่น {len(leaderboard)} คน, แมตช์ {len(matches)} คู่, การทำนาย {len(predictions)} รายการ...")
    
    # 2. เรียกเจเนอเรตวิเคราะห์ใหม่ (Force Refresh)
    print("\n🎙️ [1/3] กำลังเชื่อมประสาน Gemini API เพื่อวิเคราะห์ข้อมูลล่าสุด...")
    ai_text, model_name, is_cached = ai_analyst.get_ai_summary(
        leaderboard, 
        matches, 
        predictions, 
        force_refresh=True
    )
    
    print(f"✨ ดึงข้อมูลสำเร็จด้วยโมเดล: {model_name}")
    print(f"📝 บทสรุปความยาว {len(ai_text)} ตัวอักษร.")
    
    # 3. บังคับสร้างเสียงพากย์ปีเตอร์ AI แบบ Sync (รอจนรันเสร็จ 100% ค่อยปิดโปรแกรม)
    output_voice_path = os.path.join(BASE_DIR, "static", "ai_analysis_fast.webp")
    cache_path = os.path.join(BASE_DIR, "ai_cache.json")
    
    print("\n🔊 [2/3] กำลังสังเคราะห์ไฟล์เสียงพากย์ปีเตอร์ AI จาก Google TTS (โหมดเสถียร 100% Sync)...")
    start_time = time.time()
    
    # สั่งสร้างเสียงแบบ Sync โดยตรง
    audio_ok = ai_analyst.generate_peter_voice(ai_text, output_voice_path)
    
    duration = time.time() - start_time
    
    if audio_ok and os.path.exists(output_voice_path):
        size = os.path.getsize(output_voice_path)
        print(f"✅ [SUCCESS] สังเคราะห์ไฟล์เสียงสำเร็จใน {duration:.2f} วินาที!")
        print(f"💾 ไฟล์เสียงถูกเซฟที่: {output_voice_path} ({size:,} bytes)")
        
        # อัปเดตแฮชเสียงในไฟล์แคช
        try:
            import json
            import hashlib
            content_hash = hashlib.md5(ai_text.encode("utf-8")).hexdigest()
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f_r:
                    c_data = json.load(f_r)
                c_data["audio_generated_for_hash"] = content_hash
                with open(cache_path, "w", encoding="utf-8") as f_w:
                    json.dump(c_data, f_w, ensure_ascii=False, indent=2)
                print("📝 [SUCCESS] อัปเดตคีย์แคชเสียงใน ai_cache.json เรียบร้อย!")
        except Exception as e_cache:
            print(f"⚠️ เกิดข้อผิดพลาดในการอัปเดตไฟล์แคช: {e_cache}")
    else:
        print("❌ [ERROR] สังเคราะห์ไฟล์เสียงพากย์ล้มเหลว กรุณาตรวจสอบอินเทอร์เน็ตหรือบริการ TTS")
        
if __name__ == "__main__":
    main()
