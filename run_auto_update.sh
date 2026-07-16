#!/bin/bash
# สคริปต์สำหรับรันอัปเดตผลและล้างแคชอัตโนมัติประจำลีก CRAZYFIFA 2026

BASE_DIR="/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026"
LOG_FILE="$BASE_DIR/auto_update.log"

# ตรวจสอบความถูกต้องของสคริปต์
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] เริ่มทำงานระบบอัปเดตอัตโนมัติ ===" >> "$LOG_FILE"

# ตั้งค่า PATH ให้ครอบคลุมเพื่อความปลอดภัยสำหรับ Launchd บน macOS
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# นำทางเข้าโฟลเดอร์หลักและสั่งรัน Python3
cd "$BASE_DIR"
/usr/bin/python3 "$BASE_DIR/auto_update_results.py" >> "$LOG_FILE" 2>&1

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] ทำงานสำเร็จเสร็จสิ้น ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
