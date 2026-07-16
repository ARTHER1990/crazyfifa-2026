import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มอัปเดตผลรอบรองชนะเลิศ (Semi-finals) ตามข้อมูลจริงจาก FIFA.com...")
    print("="*60)
    print("📋 ข้อมูลผลการแข่งขัน:")
    print("  Match 101: France 0–2 Spain  (14 ก.ค. 2026) → สเปนผ่าน")
    print("  Match 102: England 1–2 Argentina (15 ก.ค. 2026) → อาร์เจนตินาผ่าน")
    print("="*60)

    # ผลการแข่งขันรอบ Semi-finals จาก FIFA.com
    # Spain 2-0 France (14 July): Mikel Oyarzabal (pen), Pedro Porro
    # Argentina 2-1 England (15 July): Anthony Gordon 55' | Enzo Fernandez 85', Lautaro Martinez 90+2'
    results = [
        {
            'id': '101',
            'home_team': 'France',
            'away_team': 'Spain',
            'match_time': '2026-07-15 02:00:00',
            'home_score': '0',
            'away_score': '2',
            'status': 'Finished',
            'scorers': '| Oyarzabal (pen) (67) | Porro (75)',
            'winner_qualify': 'Spain'
        },
        {
            'id': '102',
            'home_team': 'England',
            'away_team': 'Argentina',
            'match_time': '2026-07-16 02:00:00',
            'home_score': '1',
            'away_score': '2',
            'status': 'Finished',
            'scorers': 'Gordon (55) | E. Fernandez (85) | Lautaro (90+2)',
            'winner_qualify': 'Argentina'
        }
    ]

    # --- 1. จัดการ Google Sheets ---
    print("\n📊 [1/3] กำลังอัปเดตผลการแข่งขันใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])

        sheets_updated = 0
        for match in results:
            match_id_str = str(match['id'])
            if match_id_str in df_sheets['id'].astype(str).values:
                idx = df_sheets[df_sheets['id'].astype(str) == match_id_str].index[0]
                df_sheets.at[idx, 'home_score'] = str(match['home_score'])
                df_sheets.at[idx, 'away_score'] = str(match['away_score'])
                df_sheets.at[idx, 'status'] = str(match['status'])
                df_sheets.at[idx, 'scorers'] = str(match['scorers'])
                df_sheets.at[idx, 'winner_qualify'] = str(match['winner_qualify'])
                sheets_updated += 1
                print(f"✅ (Sheets) อัปเดต Match ID {match['id']}: {match['home_team']} {match['home_score']}–{match['away_score']} {match['away_team']} → ผ่าน: {match['winner_qualify']}")
            else:
                print(f"⚠️ (Sheets) ไม่พบ Match ID {match['id']} ในชีต — อาจต้องรัน add_matches_semi_finals.py ก่อน")

        # เขียนบันทึกข้อมูลทั้งหมดกลับลง Google Sheets
        ws.clear()
        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
        print(f"✅ บันทึกข้อมูลลง Google Sheets เรียบร้อย! (อัปเดต {sheets_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # --- 2. จัดการ SQLite (worldcup.db) ---
    print("\n🗄️ [2/3] กำลังอัปเดตผลการแข่งขันใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        sqlite_updated = 0
        for match in results:
            cursor.execute("SELECT id FROM matches WHERE id=?", (int(match['id']),))
            row = cursor.fetchone()
            if row is not None:
                cursor.execute(
                    """UPDATE matches
                       SET home_score=?, away_score=?, status=?, scorers=?, winner_qualify=?
                       WHERE id=?""",
                    (int(match['home_score']), int(match['away_score']),
                     match['status'], match['scorers'],
                     match['winner_qualify'], int(match['id']))
                )
                sqlite_updated += 1
                print(f"✅ (SQLite) อัปเดต Match ID {match['id']}: {match['home_team']} {match['home_score']}–{match['away_score']} {match['away_team']}")
            else:
                print(f"⚠️ (SQLite) ไม่พบ Match ID {match['id']} — อาจต้องรัน add_matches_semi_finals.py ก่อน")

        conn.commit()
        conn.close()
        print(f"✅ บันทึกข้อมูลลง SQLite เรียบร้อย! (อัปเดต {sqlite_updated} คู่)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # --- 3. เพิ่ม Match 103 (Final) + รันคำนวณแต้มและดัน Git ---
    print("\n⚙️ [3/3] กำลังคำนวณคะแนนผู้เล่นและดัน Git...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() เรียบร้อย!")

        from auto_update_results import touch_app_py, push_to_github
        touch_app_py('France', 'Spain', 'Finished', 'Finished')
        push_to_github()
        print("✅ ดัน Git ขึ้น GitHub เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการรันระบบคำนวณแต้มหรือดัน Git: {e}")

    print("\n🏆 --- กระบวนการเสร็จสมบูรณ์ --- 🏆")
    print("⚽ ผลรอบรองชนะเลิศอัปเดตบนเว็บบอร์ดเรียบร้อย!")
    print("🇪🇸 สเปน vs 🇦🇷 อาร์เจนตินา → รอบชิงชนะเลิศ 19 ก.ค. 2026")

if __name__ == '__main__':
    main()
