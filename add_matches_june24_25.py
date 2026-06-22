import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มกระบวนการเพิ่มตารางการแข่งขัน 12 แมตช์ใหม่ของวันที่ 24-25 มิถุนายน 2026 (เวลาท้องถิ่น) เข้าสู่ระบบ...")

    # ตาราง 12 คู่แข่งขันใหม่ที่จะอัปเดตเพิ่ม (ID 45 ถึง 56) แปลงเวลาเป็นเวลาประเทศไทย (UTC+7) เรียบร้อยแล้ว
    new_matches = [
        # วันที่ 24 มิถุนายน 2026 (เวลาท้องถิ่น) -> ตรงกับวันที่ 25 มิถุนายน 2026 (เวลาไทย)
        {
            'id': '45',
            'home_team': 'Switzerland',
            'away_team': 'Canada',
            'match_time': '2026-06-25 02:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '46',
            'home_team': 'Bosnia and Herzegovina',
            'away_team': 'Qatar',
            'match_time': '2026-06-25 02:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '47',
            'home_team': 'Scotland',
            'away_team': 'Brazil',
            'match_time': '2026-06-25 05:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '48',
            'home_team': 'Morocco',
            'away_team': 'Haiti',
            'match_time': '2026-06-25 05:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '49',
            'home_team': 'Czech Republic',
            'away_team': 'Mexico',
            'match_time': '2026-06-25 08:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '50',
            'home_team': 'South Africa',
            'away_team': 'South Korea',
            'match_time': '2026-06-25 08:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        # วันที่ 25 มิถุนายน 2026 (เวลาท้องถิ่น) -> ตรงกับวันที่ 26 มิถุนายน 2026 (เวลาไทย)
        {
            'id': '51',
            'home_team': 'Curaçao',
            'away_team': 'Ivory Coast',
            'match_time': '2026-06-26 03:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '52',
            'home_team': 'Ecuador',
            'away_team': 'Germany',
            'match_time': '2026-06-26 03:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '53',
            'home_team': 'Japan',
            'away_team': 'Sweden',
            'match_time': '2026-06-26 06:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '54',
            'home_team': 'Tunisia',
            'away_team': 'Netherlands',
            'match_time': '2026-06-26 06:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '55',
            'home_team': 'Turkey',
            'away_team': 'USA',
            'match_time': '2026-06-26 09:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '56',
            'home_team': 'Paraguay',
            'away_team': 'Australia',
            'match_time': '2026-06-26 09:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        }
    ]

    # --- 1. จัดการ Google Sheets ---
    print("\n📊 [1/3] กำลังจัดการข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_added = 0
        for match in new_matches:
            if str(match['id']) not in df_sheets['id'].astype(str).values:
                df_sheets = pd.concat([df_sheets, pd.DataFrame([match])], ignore_index=True)
                sheets_added += 1
                print(f"➕ (Sheets) เตรียมเพิ่ม Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                # ถ้ามีอยู่แล้ว ให้ข้ามหรือสามารถอัปเดตทับเพื่อยืนยันความถูกต้องของเวลา
                idx = df_sheets[df_sheets['id'].astype(str) == str(match['id'])].index[0]
                df_sheets.at[idx, 'home_team'] = str(match['home_team'])
                df_sheets.at[idx, 'away_team'] = str(match['away_team'])
                df_sheets.at[idx, 'match_time'] = str(match['match_time'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                print(f"🔄 (Sheets) อัปเดตข้อมูลทับ Match ID {match['id']} เพื่ออัปเดตเวลาแข่งขัน")
        
        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว! (เพิ่มใหม่ {sheets_added} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการ SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังจัดการข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_added = 0
        sqlite_updated = 0
        for match in new_matches:
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(match['id']),))
            row = cursor.fetchone()
            if row is None:
                # แทรกคู่แข่งใหม่
                cursor.execute(
                    "INSERT INTO matches (id, home_team, away_team, match_time, home_score, away_score, status, scorers) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(match['id']), match['home_team'], match['away_team'], match['match_time'], None, None, match['status'], match['scorers'])
                )
                sqlite_added += 1
                print(f"➕ (SQLite) แทรก Match ID {match['id']} เรียบร้อย: {match['home_team']} vs {match['away_team']}")
            else:
                # อัปเดตข้อมูลทับกรณีมีอยู่แล้ว
                cursor.execute(
                    "UPDATE matches SET home_team=?, away_team=?, match_time=?, status=? WHERE id=?",
                    (match['home_team'], match['away_team'], match['match_time'], match['status'], int(match['id']))
                )
                sqlite_updated += 1
                print(f"🔄 (SQLite) อัปเดตข้อมูลทับ Match ID {match['id']}")
                
        conn.commit()
        conn.close()
        print(f"✅ บันทึกข้อมูลลง SQLite (worldcup.db) เรียบร้อย! (เพิ่มใหม่ {sqlite_added}, อัปเดตทับ {sqlite_updated})")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. รันระบบคำนวณแต้มและล้างแคช ---
    print("\n⚙️ [3/3] กำลังคำนวณคะแนนผู้เล่นและล้างแคชระบบ...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และเคลียร์แคช Streamlit เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการรันระบบคำนวณแต้ม: {e}")

    print("\n🏆 --- กระบวนการเสร็จสมบูรณ์ 100% --- 🏆")
    print("⚽ ตารางการแข่งขัน 12 คู่ใหม่ (ID 45 ถึง 56) ของวันที่ 24-25 มิถุนายน 2026 แสดงบนเว็บบอร์ดเรียบร้อยแล้ว!")

if __name__ == '__main__':
    main()
