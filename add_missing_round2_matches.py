import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path ค้นหาโมดูลระบบ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มกระบวนการเพิ่ม 4 แมตช์ที่ตกหล่นเข้าสู่ระบบฐานข้อมูล...")

    # ข้อมูล 4 แมตช์เป้าหมายที่แข่งขันเสร็จสิ้นแล้วเมื่อวันที่ 18 มิถุนายน 2026
    missing_matches = [
        {
            'id': '32',
            'home_team': 'Czech Republic',
            'away_team': 'South Africa',
            'match_time': '2026-06-18 15:00:00',
            'home_score': '1',
            'away_score': '1',
            'status': 'Finished',
            'scorers': "Sadílek 6' | Mokoena 83' (pen.)"
        },
        {
            'id': '33',
            'home_team': 'Switzerland',
            'away_team': 'Bosnia and Herzegovina',
            'match_time': '2026-06-18 18:00:00',
            'home_score': '4',
            'away_score': '1',
            'status': 'Finished',
            'scorers': "Manzambi 74', 90', Vargas 84', Xhaka 90+7' (pen.) | Mahmić 90+3'"
        },
        {
            'id': '34',
            'home_team': 'Canada',
            'away_team': 'Qatar',
            'match_time': '2026-06-18 21:00:00',
            'home_score': '6',
            'away_score': '0',
            'status': 'Finished',
            'scorers': "Larin 16', J. David 29', 45+3', 90+2', Saliba 64', Manai 75' (o.g.) |"
        },
        {
            'id': '35',
            'home_team': 'Mexico',
            'away_team': 'South Korea',
            'match_time': '2026-06-18 23:30:00',
            'home_score': '1',
            'away_score': '0',
            'status': 'Finished',
            'scorers': "Romo 50' |"
        }
    ]

    # --- 1. จัดการ Google Sheets ---
    print("\n📊 [1/3] กำลังจัดการข้อมูลใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        sheets_added = 0
        for match in missing_matches:
            if str(match['id']) not in df_sheets['id'].astype(str).values:
                df_sheets = pd.concat([df_sheets, pd.DataFrame([match])], ignore_index=True)
                sheets_added += 1
                print(f"➕ (Sheets) เตรียมเพิ่ม Match ID {match['id']}: {match['home_team']} vs {match['away_team']}")
            else:
                # ถ้ามีอยู่แล้วแต่อยากอัปเดตผลทับเพื่อความชัวร์
                idx = df_sheets[df_sheets['id'].astype(str) == str(match['id'])].index[0]
                df_sheets.at[idx, 'home_score'] = str(match['home_score'])
                df_sheets.at[idx, 'away_score'] = str(match['away_score'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                df_sheets.at[idx, 'scorers'] = str(match['scorers'])
                print(f"🔄 (Sheets) อัปเดตข้อมูลทับ Match ID {match['id']} เพื่อรับประกันความถูกต้อง")
        
        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ บันทึกข้อมูลลง Google Sheets เรียบร้อยแล้ว!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการ SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังจัดการข้อมูลใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ตรวจสอบโครงสร้างตาราง matches ใน SQLite
        cursor.execute("PRAGMA table_info(matches)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"ℹ️ โครงสร้างตาราง SQLite ปัจจุบัน: {columns}")
        
        sqlite_added = 0
        sqlite_updated = 0
        for match in missing_matches:
            # เช็คว่ามี id นี้แล้วยัง
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(match['id']),))
            row = cursor.fetchone()
            if row is None:
                # แทรกใหม่
                cursor.execute(
                    "INSERT INTO matches (id, home_team, away_team, match_time, home_score, away_score, status, scorers) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (int(match['id']), match['home_team'], match['away_team'], match['match_time'], int(match['home_score']), int(match['away_score']), match['status'], match['scorers'])
                )
                sqlite_added += 1
                print(f"➕ (SQLite) แทรก Match ID {match['id']} เรียบร้อย")
            else:
                # อัปเดตทับ
                cursor.execute(
                    "UPDATE matches SET home_team=?, away_team=?, match_time=?, home_score=?, away_score=?, status=?, scorers=? WHERE id=?",
                    (match['home_team'], match['away_team'], match['match_time'], int(match['home_score']), int(match['away_score']), match['status'], match['scorers'], int(match['id']))
                )
                sqlite_updated += 1
                print(f"🔄 (SQLite) อัปเดตข้อมูลทับ Match ID {match['id']}")
                
        conn.commit()
        conn.close()
        print(f"✅ บันทึกข้อมูลลง SQLite (worldcup.db) เรียบร้อย! (เพิ่มใหม่ {sqlite_added}, อัปเดตทับ {sqlite_updated})")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. รันระบบคำนวณแต้มและล้างแคช ---
    print("\n⚙️ [3/3] กำลังคำนวณคะแนนผู้เล่นใหม่และล้างแคชระบบ...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และเคลียร์แคช Streamlit เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการรันระบบคำนวณแต้ม: {e}")

    print("\n🏆 --- กระบวนการเสร็จสมบูรณ์ 100% --- 🏆")
    print("⚽ ตอนนี้คู่ทั้ง 4 จะแสดงในระบบในฐานะแมตช์ที่แข่งเสร็จสิ้นแล้ว และจะปิดการทายผลโดยอัตโนมัติ!")

if __name__ == '__main__':
    main()
