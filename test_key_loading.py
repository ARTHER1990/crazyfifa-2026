import os
import sys

def test_loading():
    print("🔎 เริ่มต้นระบบจำลองตรวจสอบกลไกการโหลดคีย์ GEMINI_API_KEY...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_env = os.path.join(current_dir, ".env")
    absolute_env = "/Users/art/Desktop/ART_JOB/.env"
    
    print(f"📁 พิกัด Directory ปัจจุบัน: {current_dir}")
    print(f"📁 พิกัดไฟล์ .env ในโครงการ: {project_env} (มีจริงไหม: {os.path.exists(project_env)})")
    print(f"📁 พิกัดไฟล์ .env สัมบูรณ์: {absolute_env} (มีจริงไหม: {os.path.exists(absolute_env)})")
    
    # ดึงคีย์โดยอ้างอิงโค้ดจาก ai_analyst
    api_key_loaded = None
    paths_to_try = [project_env, absolute_env]
    
    for p in paths_to_try:
        if os.path.exists(p):
            print(f"\n📖 กำลังสแกนตรวจสอบไฟล์: {p}")
            try:
                with open(p, "rb") as f:
                    content_bytes = f.read()
                    print(f"   📊 ขนาดไฟล์ในรูปแบบ Bytes: {len(content_bytes)} bytes")
                    print(f"   📊 ข้อมูลดิบ (Raw Bytes): {content_bytes}")
                
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        repr_line = repr(line)
                        print(f"   [แถวที่ {i}]: {repr_line}")
                        clean_line = line.strip().replace("\r", "").replace("\n", "")
                        
                        # ทดสอบเช็คสตาร์ทด้วย GEMINI_API_KEY=
                        is_start = clean_line.startswith("GEMINI_API_KEY=")
                        print(f"   -> ตัวกรอง clean_line.startswith('GEMINI_API_KEY='): {is_start}")
                        
                        if "GEMINI_API_KEY=" in clean_line:
                            print(f"   💡 พบคำค้นหาในบรรทัดนี้! แต่สตาร์ทตรงๆ ไหม: {is_start}")
                            if not is_start:
                                # วิเคราะห์หาอักขระซ่อนเร้น
                                print("   ⚠️ สันนิษฐาน: พบอักษรขยะหรือ BOM นำหน้าคำค้นหาหลัก!")
                            
                            val = clean_line.split("=", 1)[1].strip()
                            if val.startswith(('"', "'")) and val.endswith(('"', "'")):
                                val = val[1:-1]
                            api_key_loaded = val
                            print(f"   🔑 ดึงคีย์จำลองได้สำเร็จ: {val[:12]}... (ขนาดยาว: {len(val)})")
            except Exception as e:
                print(f"❌ มีข้อผิดพลาดในขั้นตอนทดลองสแกน: {e}")
                
    print("\n-------------------------------------------")
    print(f"🎯 ผลลัพธ์รวม: คีย์ที่โหลดได้จริงคือ: {api_key_loaded if api_key_loaded else 'None'}")
    
    if api_key_loaded:
        print("\n🚀 เริ่มการทดสอบดึง API ของ Gemini ด้วยคีย์นี้จริง...")
        try:
            import requests
            models_to_test = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"]
            for model_name in models_to_test:
                print(f"\n   ⚙️ กำลังทดสอบโมเดล: {model_name}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key_loaded}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": "Hello, please reply with 'OK' if you can read this message."}]}]
                }
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=10)
                    print(f"      📊 สถานะ HTTP Response ({model_name}): {response.status_code}")
                    if response.status_code == 200:
                        res_json = response.json()
                        text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"      ✅ เชื่อมเซิร์ฟเวอร์ AI สำเร็จ! คำตอบจาก Gemini: {repr(text.strip())}")
                    else:
                        print(f"      ❌ เซิร์ฟเวอร์ปฏิเสธการเชื่อมต่อ (Error {response.status_code}): {response.text}")
                except Exception as inner_e:
                    print(f"      ❌ เกิดข้อผิดพลาดเฉพาะตัวในโมเดล {model_name}: {inner_e}")
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาดทางโครงข่ายอินเทอร์เน็ต: {e}")

if __name__ == "__main__":
    test_loading()
