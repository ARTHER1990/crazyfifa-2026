import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มกระบวนการเพิ่มตารางการแข่งขันรอบ 16 ทีมสุดท้าย (Match ID 89 ถึง 96)...")

    new_matches = [
        {
            'id': '89',
            'home_team': 'Canada',
            'away_team': 'Morocco',
            'match_time': '2026-07-05 04:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '90',
            'home_team': 'Paraguay',
            'away_team': 'France',
            'match_time': '2026-07-05 01:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '91',
            'home_team': 'Brazil',
            'away_team': 'Norway',
            'match_time': '2026-07-06 03:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '92',
            'home_team': 'Mexico',
            'away_team': 'England',
            'match_time': '2026-07-06 09:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '93',
            'home_team': 'Spain',
            'away_team': 'Portugal',
            'match_time': '2026-07-07 03:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '94',
            'home_team': 'United States',
            'away_team': 'Belgium',
            'match_time': '2026-07-07 10:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '95',
            'home_team': 'ผู้ชนะคู่ 86',
            'away_team': 'ผู้ชนะคู่ 88',
            'match_time': '2026-07-07 23:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
        },
        {
            'id': '96',
            'home_team': 'ผู้ชนะคู่ 85',
            'away_team': 'ผู้ชนะคู่ 87',
            'match_time': '2026-07-08 06:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': '',
            'winner_qualify': ''
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
            match_row = {k: v for k, v in match.items() if k in df_sheets.columns}
            if str(match['id']) not in df_sheets['id'].astype(str).values:
                df_sheets = pd.concat([df_sheets, pd.DataFrame([match_row])], ignore_index=True)
                sheets_added += 1
                print(f"➕ (Sheets) เตรียมเพิ่ม Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                idx = df_sheets[df_sheets['id'].astype(str) == str(match['id'])].index[0]
                df_sheets.at[idx, 'home_team'] = str(match['home_team'])
                df_sheets.at[idx, 'away_team'] = str(match['away_team'])
                df_sheets.at[idx, 'match_time'] = str(match['match_time'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                if 'winner_qualify' in df_sheets.columns:
                    df_sheets.at[idx, 'winner_qualify'] = ''
                sheets_updated += 1
                print(f"🔄 (Sheets) อัปเดตข้อมูลทับ Match ID {match['id']}")
        
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
                    "INSERT INTO matches (id, home_team, away_team, match_time, home_score, away_score, status, scorers, winner_qualify) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(match['id']), match['home_team'], match['away_team'], match['match_time'], None, None, match['status'], match['scorers'], '')
                )
                sqlite_added += 1
                print(f"➕ (SQLite) แทรก Match ID {match['id']} เรียบร้อย: {match['home_team']} vs {match['away_team']}")
            else:
                # อัปเดตข้อมูลทับกรณีมีอยู่แล้ว
                cursor.execute(
                    "UPDATE matches SET home_team=?, away_team=?, match_time=?, status=?, winner_qualify='' WHERE id=?",
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
    print("⚽ ตารางการแข่งขันรอบ 16 ทีมสุดท้าย (ID 89 ถึง 96) แสดงบนเว็บบอร์ดเรียบร้อยแล้ว!")

if __name__ == '__main__':
    main()
