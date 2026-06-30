import sys
import os
import sqlite3
import pandas as pd

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🔄 แก้ไขข้อมูลผู้เข้ารอบ Match ID 68 (Germany vs Paraguay) เป็น 'Paraguay' (เยอรมนีแพ้จุดโทษ) พร้อมคำนวณแต้มสะสมใหม่...")

    # ข้อมูลผู้เข้ารอบที่ถูกต้องตามที่คุณอาร์ตระบุ:
    # Match ID 68: Germany vs Paraguay -> Paraguay ชนะจุดโทษเข้ารอบ
    target_id = '68'
    correct_winner = 'Paraguay'

    # 1. จัดการ Google Sheets
    print("\n📊 [1/3] กำลังอัปเดตข้อมูลผู้เข้ารอบใน Google Sheets...")
    try:
        ws = db.get_worksheet('matches')
        data = ws.get_all_values()
        df_sheets = pd.DataFrame(data[1:], columns=data[0])
        
        mask = df_sheets['id'].astype(str) == str(target_id)
        if mask.any():
            idx = df_sheets.index[mask][0]
            old_winner = df_sheets.at[idx, 'winner_qualify']
            df_sheets.at[idx, 'winner_qualify'] = correct_winner
            
            ws.clear()
            ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
            print(f"✅ (Sheets) แก้ไขผู้เข้ารอบ Match ID {target_id} จาก [{old_winner}] เป็น [{correct_winner}] เรียบร้อยครับ")
        else:
            print(f"❌ ไม่พบ Match ID {target_id} ใน Google Sheets")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ Google Sheets: {e}")

    # 2. จัดการ SQLite (worldcup.db)
    print("\n🗄️ [2/3] กำลังอัปเดตข้อมูลผู้เข้ารอบใน SQLite (worldcup.db)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE matches SET winner_qualify=? WHERE id=?",
            (correct_winner, int(target_id))
        )
        conn.commit()
        conn.close()
        print(f"✅ (SQLite) อัปเดตผู้เข้ารอบ Match ID {target_id} เป็น [{correct_winner}] เรียบร้อยครับ")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการจัดการ SQLite: {e}")

    # 3. คำนวณแต้มทายผลใหม่พร้อมเคลียร์แคช
    print("\n⚙️ [3/3] กำลังคำนวณแต้มทายผลใหม่พร้อมล้างแคชระบบ...")
    try:
        db.update_scores_logic()
        print("✅ เรียกใช้ update_scores_logic() และล้างแคชระบบเรียบร้อยแล้ว!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการคำนวณแต้มใหม่: {e}")

    print("\n🏆 --- แก้ไขข้อมูลเรียบร้อยเสร็จสมบูรณ์ --- 🏆")

if __name__ == '__main__':
    main()
