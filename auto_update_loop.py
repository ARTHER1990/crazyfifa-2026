import os
import sys
import time
from datetime import datetime, timedelta

# กำหนดโฟลเดอร์หลัก
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = BASE_DIR
AUTO_UPDATE_SCRIPT = os.path.join(SCRIPTS_DIR, "auto_update_results.py")

INTERVAL_SECONDS = 7200  # ทุกๆ 2 ชั่วโมง

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("=" * 60)
    print("      🏆 CRAZYFIFA 2026 - TERMINAL AUTO-UPDATE LOOP 🏆      ")
    print("=" * 60)
    print(" 👤 พัฒนาโดย: ปีเตอร์ (Peter AI Assistant)")
    print(" 🛠️  สถานะระบบ: ทำงานอยู่เบื้องหน้า (Terminal Mode)")
    print(" 🔒 ความปลอดภัย: ผ่านฉลุย 100% (ไม่ติด macOS TCC Sandbox)")
    print("=" * 60)

def main():
    print_banner()
    print(f"🚀 เริ่มการทำงานระบบ Loop ทุกๆ {INTERVAL_SECONDS // 3600} ชั่วโมง...")
    
    try:
        while True:
            current_time = datetime.now()
            next_update = current_time + timedelta(seconds=INTERVAL_SECONDS)
            
            print_banner()
            print(f"\n[📡 {current_time.strftime('%Y-%m-%d %H:%M:%S')}] กำลังเริ่มรันสคริปต์อัปเดตออโต้...")
            
            # รันสคริปต์หลัก
            os.system(f"python3 \"{AUTO_UPDATE_SCRIPT}\"")
            
            print("\n" + "-" * 60)
            print(f"✅ บันทึกรอบทำงานเสร็จสิ้น: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳ จะเริ่มอัปเดตรอบถัดไปในเวลา: {next_update.strftime('%H:%M:%S')} น.")
            print("-" * 60)
            
            # ทำตัวนับถอยหลัง (Countdown) แสดงผลเรียลไทม์
            for remaining in range(INTERVAL_SECONDS, 0, -1):
                mins, secs = divmod(remaining, 60)
                hours, mins = divmod(mins, 60)
                sys.stdout.write(f"\r⏱️  นับถอยหลังสู่อัปเดตรอบถัดไป: {hours:02d}:{mins:02d}:{secs:02d} | กด [Ctrl + C] เพื่อหยุดสคริปต์ ")
                sys.stdout.flush()
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n\n👋 หยุดระบบการรันลูปสำเร็จ ขอบคุณครับคุณอาร์ต!")

if __name__ == "__main__":
    main()
