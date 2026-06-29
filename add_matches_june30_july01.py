import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มกระบวนการเพิ่มตารางการแข่งขัน 6 แมตช์ใหม่ของวันที่ 30 มิถุนายน ถึง 1 กรกฎาคม 2026 (รอบ 32 ทีมสุดท้าย)...")

    # ตารางการแข่งขันรอบ 32 ทีมสุดท้าย (Match ID 77 ถึง 82)
    new_matches = [
        # --- วันที่ 30 มิถุนายน 2026 (เวลาไทยเช้าวันที่ 1 กรกฎาคม 2026) ---
        {
            'id': '78',
            'home_team': 'Ivory Coast',
            'away_team': 'Norway',
            'match_time': '2026-07-01 01:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '77',
            'home_team': 'France',
            'away_team': 'Sweden',
            'match_time': '2026-07-01 04:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '79',
            'home_team': 'Mexico',
            'away_team': 'Ecuador',
            'match_time': '2026-07-01 08:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        # --- วันที่ 1 กรกฎาคม 2026 (เวลาไทยเช้าวันที่ 2 กรกฎาคม 2026) ---
        {
            'id': '80',
            'home_team': 'England',
            'away_team': 'DR Congo',
            'match_time': '2026-07-02 01:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '82',
            'home_team': 'Belgium',
            'away_team': 'Senegal',
            'match_time': '2026-07-02 04:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '81',
            'home_team': 'United States',
            'away_team': 'Bosnia and Herzegovina',
            'match_time': '2026-07-02 08:00:00',
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
        sheets_updated = 0
        for match in new_matches:
            if str(match['id']) not in df_sheets['id'].astype(str).values:
                df_sheets = pd.concat([df_sheets, pd.DataFrame([match])], ignore_index=True)
                sheets_added += 1
                print(f"➕ (Sheets) เตรียมเพิ่ม Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                idx = df_sheets[df_sheets['id'].astype(str) == str(match['id'])].index[0]
                df_sheets.at[idx, 'home_team'] = str(match['home_team'])
                df_sheets.at[idx, 'away_team'] = str(match['away_team'])
                df_sheets.at[idx, 'match_time'] = str(match['match_time'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                sheets_updated += 1
                print(f"🔄 (Sheets) อัปเดตข้อมูลทับ Match ID {match['id']} เพื่อระบุทีมรอบ 32 ทีมจริง")
        
        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว! (เพิ่มใหม่ {sheets_added} คู่, อัปเดตทับ {sheets_updated} คู่)")
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

    print("\n🏆 --- กระบวนการเสร็จสมบูรณ์ --- 🏆")
    print("⚽ ตารางการแข่งขัน 6 คู่ใหม่ (ID 77 ถึง 82) ประจำวันที่ 30 มิถุนายน ถึง 1 กรกฎาคม 2026 แสดงบนเว็บบอร์ดเรียบร้อยแล้ว!")

if __name__ == '__main__':
    main()
