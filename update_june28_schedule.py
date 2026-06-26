import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบอัปเดตเลื่อนวันแข่งเป็นวันที่ 28 มิถุนายน 2026 ตามคู่หน้าเว็บฟีฟ่า...")

    # ตารางการปรับเวลาและชื่อทีมตามรูปภาพหน้าจอ
    updates = {
        '61': {
            'home_team': 'Jordan',
            'away_team': 'Argentina',
            'match_time': '2026-06-28 09:00:00'
        },
        '62': {
            'home_team': 'Algeria',
            'away_team': 'Austria',
            'match_time': '2026-06-28 09:00:00'
        },
        '63': {
            'home_team': 'Colombia',
            'away_team': 'Portugal',
            'match_time': '2026-06-28 06:30:00'
        },
        '64': {
            'home_team': 'Congo DR', # เปลี่ยนจาก DR Congo เป็น Congo DR ตามภาพ
            'away_team': 'Uzbekistan',
            'match_time': '2026-06-28 06:30:00'
        },
        '65': {
            'home_team': 'Panama',
            'away_team': 'England',
            'match_time': '2026-06-28 04:00:00'
        },
        '66': {
            'home_team': 'Croatia',
            'away_team': 'Ghana',
            'match_time': '2026-06-28 04:00:00'
        }
    }

    # 1. อัปเดต SQLite (worldcup.db)
    print("\n🗄️ [1/3] กำลังอัปเดตข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_updated = 0
        for m_id, val in updates.items():
            cursor.execute("SELECT id, home_team, away_team, match_time FROM matches WHERE id=?", (int(m_id),))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute(
                    "UPDATE matches SET home_team=?, away_team=?, match_time=? WHERE id=?",
                    (val['home_team'], val['away_team'], val['match_time'], int(m_id))
                )
                sqlite_updated += 1
                print(f"✅ (SQLite) อัปเดต ID {m_id}: {val['home_team']} vs {val['away_team']} ➔ {val['match_time']} (เดิม {row[1]} vs {row[2]} ➔ {row[3]})")
            else:
                print(f"⚠️ (SQLite) ไม่พบ Match ID {m_id} ในฐานข้อมูล")
                
        conn.commit()
        conn.close()
        print(f"🎉 อัปเดต SQLite สำเร็จ {sqlite_updated} แมตช์!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดต SQLite: {e}")

    # 2. อัปเดต Google Sheets
    print("\n📊 [2/3] กำลังอัปเดตข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_updated = 0
        for m_id, val in updates.items():
            mask = df_sheets['id'].astype(str) == str(m_id)
            if mask.any():
                idx = df_sheets.index[mask][0]
                old_home = df_sheets.at[idx, 'home_team']
                old_away = df_sheets.at[idx, 'away_team']
                old_time = df_sheets.at[idx, 'match_time']
                
                df_sheets.at[idx, 'home_team'] = str(val['home_team'])
                df_sheets.at[idx, 'away_team'] = str(val['away_team'])
                df_sheets.at[idx, 'match_time'] = str(val['match_time'])
                sheets_updated += 1
                print(f"✅ (Sheets) อัปเดต ID {m_id}: {val['home_team']} vs {val['away_team']} ➔ {val['match_time']} (เดิม {old_home} vs {old_away} ➔ {old_time})")
            else:
                print(f"⚠️ (Sheets) ไม่พบ Match ID {m_id} ใน Google Sheets")
                
        # บันทึกกลับลง Sheets
        if sheets_updated > 0:
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"🎉 อัปเดต Google Sheets สำเร็จ {sheets_updated} แมตช์!")
        else:
            print("❌ ไม่มีข้อมูลแมตช์ที่ได้รับการอัปเดตใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการอัปเดต Google Sheets: {e}")

if __name__ == '__main__':
    main()
