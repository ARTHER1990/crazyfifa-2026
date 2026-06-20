import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database as db
import pandas as pd

# ดึงข้อมูลจาก Google Sheets
ws = db.get_worksheet('matches')
data = ws.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# ตารางคู่แข่งขันและวันเวลาแข่งขันประเทศไทยจริงที่ถูกต้อง (UTC+7)
correct_times = {
    # แมตช์เดิมของวันที่ 19 มิถุนายน (ฝั่งอเมริกา) -> ปรับเป็นเวลาไทยจริงวันที่ 20 มิถุนายน
    '25': '2026-06-20 02:00:00',
    '26': '2026-06-20 05:00:00',
    '27': '2026-06-20 08:30:00',
    '36': '2026-06-20 11:00:00',
    
    # แมตช์เดิมของวันที่ 20 มิถุนายน (ฝั่งอเมริกา) -> ปรับเป็นเวลาไทยจริงวันที่ 21 มิถุนายน
    '28': '2026-06-21 01:00:00',
    '29': '2026-06-21 03:00:00',
    '30': '2026-06-21 07:00:00',
    '31': '2026-06-21 09:00:00',
    
    # แมตช์เดิมของวันที่ 21 มิถุนายน (ฝั่งอเมริกา) -> สเปนเป็นวันที่ 21 คู่อื่นเป็นวันที่ 22 ตามเวลาไทยจริง
    '37': '2026-06-21 23:00:00',
    '38': '2026-06-22 02:00:00',
    '39': '2026-06-22 05:00:00',
    '40': '2026-06-22 08:00:00',
    
    # แมตช์เดิมของวันที่ 22 มิถุนายน (ฝั่งอเมริกา) -> อาร์เจนตินาและคู่อื่นเป็นวันที่ 23 ตามเวลาไทยจริง
    '41': '2026-06-23 00:00:00',
    '42': '2026-06-23 04:00:00',
    '43': '2026-06-23 07:00:00',
    '44': '2026-06-23 09:00:00'
}

updated_count = 0
for m_id, correct_time in correct_times.items():
    # ตรวจสอบหาแถวที่มี ID ตรงกันใน DataFrame
    idx = df[df['id'].astype(str) == str(m_id)].index
    if not idx.empty:
        old_time = df.loc[idx[0], 'match_time']
        if old_time != correct_time:
            df.loc[idx[0], 'match_time'] = correct_time
            print(f"🔄 ปรับปรุง แมตช์ ID {m_id}: {df.loc[idx[0], 'home_team']} vs {df.loc[idx[0], 'away_team']} จาก {old_time} -> {correct_time}")
            updated_count += 1

if updated_count > 0:
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.astype(str).values.tolist())
    print(f"✅ บันทึกแก้ไขเวลาประเทศไทยจริงสำเร็จรวม {updated_count} แมตช์!")
    db.st.cache_data.clear()
else:
    print("ℹ️ เวลาแข่งขันในระบบเป็นเวลาไทยจริงและถูกต้องครบถ้วนแล้ว")
