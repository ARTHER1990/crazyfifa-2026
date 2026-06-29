import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มกระบวนการกู้คืนคู่แข่งขันรอบ 32 ทีมสุดท้ายที่หายไป (ID 68, 69, 70)...")

    # ตารางคู่แข่งขันที่หายไปจากการเคลียร์ฟลัช (กู้คืนกลับมาตามโปรแกรมจริงฟีฟ่า 2026)
    missing_matches = [
        {
            'id': '68',
            'home_team': 'Germany',
            'away_team': 'Paraguay',
            'match_time': '2026-06-30 02:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '69',
            'home_team': 'Netherlands',
            'away_team': 'Morocco',
            'match_time': '2026-06-30 05:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        },
        {
            'id': '70',
            'home_team': 'Brazil',
            'away_team': 'Japan',
            'match_time': '2026-06-30 08:00:00',
            'home_score': '',
            'away_score': '',
            'status': 'Upcoming',
            'scorers': ''
        }
    ]

    # --- 1. จัดการ Google Sheets ---
    print("\n📊 [1/3] กำลังเพิ่มข้อมูลกู้คืนลง Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_added = 0
        sheets_updated = 0
        for match in missing_matches:
            if str(match['id']) not in df_sheets['id'].astype(str).values:
                df_sheets = pd.concat([df_sheets, pd.DataFrame([match])], ignore_index=True)
                sheets_added += 1
                print(f"➕ (Sheets) กู้คืนเพิ่ม Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                idx = df_sheets[df_sheets['id'].astype(str) == str(match['id'])].index[0]
                df_sheets.at[idx, 'home_team'] = str(match['home_team'])
                df_sheets.at[idx, 'away_team'] = str(match['away_team'])
                df_sheets.at[idx, 'match_time'] = str(match['match_time'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                sheets_updated += 1
                print(f"🔄 (Sheets) อัปเดตข้อมูลทับกู้คืน Match ID {match['id']}")
        
        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ กู้คืนข้อมูลลง Google Sheets เรียบร้อยแล้ว! (เพิ่มใหม่ {sheets_added} คู่, อัปเดตทับ {sheets_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการ SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังเพิ่มข้อมูลกู้คืนลง SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sqlite_added = 0
        sqlite_updated = 0
        for match in missing_matches:
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(match['id']),))
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    "INSERT INTO matches (id, home_team, away_team, match_time, home_score, away_score, status, scorers) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(match['id']), match['home_team'], match['away_team'], match['match_time'], None, None, match['status'], match['scorers'])
                )
                sqlite_added += 1
                print(f"➕ (SQLite) กู้คืน Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                cursor.execute(
                    "UPDATE matches SET home_team=?, away_team=?, match_time=?, status=? WHERE id=?",
                    (match['home_team'], match['away_team'], match['match_time'], match['status'], int(match['id']))
                )
                sqlite_updated += 1
                print(f"🔄 (SQLite) อัปเดตทับกู้คืน Match ID {match['id']}")
                
        conn.commit()
        conn.close()
        print(f"✅ บันทึกกู้คืนลง SQLite (worldcup.db) เรียบร้อย! (เพิ่มใหม่ {sqlite_added}, อัปเดตทับ {sqlite_updated})")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. รันระบบคำนวณแต้มและล้างแคช ---
    print("\n⚙️ [3/3] กำลังเคลียร์แคชและซิงค์ข้อมูลใหม่...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และล้างแคช RAM เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการคำนวณ: {e}")

    print("\n🏆 --- การกู้คืนเสร็จสมบูรณ์ --- 🏆")
    print("⚽ คู่ไฮไลท์ Germany vs Paraguay, Netherlands vs Morocco และ Brazil vs Japan (ID 68, 69, 70) กลับมาโลดแล่นบนหน้าจอบอร์ดทายผลเรียบร้อยแล้ว!")

if __name__ == '__main__':
    main()
