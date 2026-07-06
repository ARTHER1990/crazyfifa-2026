import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def sync():
    print("🔄 เริ่มต้นกระบวนการซิงก์ข้อมูลตรงจาก Google Sheets เข้าสู่ SQLite...")
    
    # 1. ดึงข้อมูลจาก Google Sheets (Source of Truth)
    try:
        db.get_matches.clear()
        df_sheets = db.get_matches()
        print(f"📊 โหลดข้อมูล matches จาก Google Sheets สำเร็จ! (พบทั้งหมด {len(df_sheets)} คู่)")
    except Exception as e:
        print(f"❌ โหลดข้อมูลจาก Google Sheets ล้มเหลว: {e}")
        return

    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ตรวจสอบว่ามีตาราง matches อยู่หรือไม่ ถ้าไม่มีให้สร้าง
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            home_team TEXT,
            away_team TEXT,
            match_time TEXT,
            home_score INTEGER,
            away_score INTEGER,
            status TEXT,
            scorers TEXT,
            winner_qualify TEXT
        )
    """)
    conn.commit()

    # ดึงข้อมูลจาก SQLite ปัจจุบันมาตรวจสอบความแตกต่าง
    try:
        cursor.execute("SELECT id, home_score, away_score, status, scorers, winner_qualify FROM matches")
        sqlite_rows = cursor.fetchall()
        sqlite_map = {str(row[0]): row for row in sqlite_rows}
    except Exception as e:
        print(f"❌ ดึงข้อมูลจาก SQLite ล้มเหลว: {e}")
        conn.close()
        return

    updated_count = 0
    for _, row in df_sheets.iterrows():
        m_id = str(row['id'])
        h_score_sheet = str(row['home_score']).strip()
        a_score_sheet = str(row['away_score']).strip()
        status_sheet = str(row['status']).strip()
        scorers_sheet = str(row['scorers']).strip()
        winner_qual_sheet = str(row['winner_qualify']).strip()

        # แปลงเป็นสกอร์ที่พร้อมบันทึก
        try:
            h_val = int(float(h_score_sheet)) if h_score_sheet != "" and h_score_sheet.lower() != "nan" else None
            a_val = int(float(a_score_sheet)) if a_score_sheet != "" and a_score_sheet.lower() != "nan" else None
        except ValueError:
            h_val = None
            a_val = None

        need_update = False
        if m_id not in sqlite_map:
            # ถ้าไม่มีแมตช์นี้ใน SQLite
            need_update = True
        else:
            # ถ้ามี ให้เปรียบเทียบค่า
            sq_id, sq_h, sq_a, sq_status, sq_scorers, sq_winner_qual = sqlite_map[m_id]
            
            # เช็คว่ามีค่าไม่ตรงกันหรือไม่
            sq_h_val = int(sq_h) if sq_h is not None and str(sq_h).strip() != "" else None
            sq_a_val = int(sq_a) if sq_a is not None and str(sq_a).strip() != "" else None

            if (sq_h_val != h_val or 
                sq_a_val != a_val or 
                sq_status != status_sheet or 
                str(sq_scorers).strip() != scorers_sheet or 
                str(sq_winner_qual).strip() != winner_qual_sheet):
                need_update = True

        if need_update:
            print(f"✏️  ตรวจพบความแตกต่าง Match ID {m_id}: ในชีต [{status_sheet} {h_score_sheet}-{a_score_sheet}] vs SQLite โลคัล")
            # เขียนทับลง SQLite
            cursor.execute(
                """
                INSERT INTO matches (id, home_team, away_team, match_time, home_score, away_score, status, scorers, winner_qualify)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    home_score = excluded.home_score,
                    away_score = excluded.away_score,
                    status = excluded.status,
                    scorers = excluded.scorers,
                    winner_qualify = excluded.winner_qualify
                """,
                (
                    int(row['id']), 
                    str(row['home_team']), 
                    str(row['away_team']), 
                    str(row['match_time']),
                    h_val, 
                    a_val, 
                    status_sheet, 
                    scorers_sheet, 
                    winner_qual_sheet
                )
            )
            updated_count += 1

    conn.commit()
    conn.close()

    print(f"✅ บันทึกทับ SQLite ท้องถิ่นสำเร็จ {updated_count} คู่!")

    # 2. ทำการอัปเดตและคำนวณแต้มโบนัสและสกอร์สมาชิกใหม่ทั้งหมด
    if updated_count > 0:
        print("\n🧮 กำลังคำนวณและแจกคะแนนผลทาย/โบนัส สมาชิกทุกคนใหม่ย้อนหลังตามข้อมูลชีตสด...")
        try:
            db.update_scores_logic()
            print("🎉 คำนวณและสรุปแต้มใหม่สำเร็จเรียบร้อย!")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการคำนวณแต้ม: {e}")

        # 3. อัปเดตคอมเมนต์ใน app.py บังคับล้างแคช RAM หน้าเว็บออนไลน์
        from auto_update_results import touch_app_py, push_to_github
        print("\n⚡ ทำการ Touch app.py เพื่อกระตุ้นระบบคลาวด์ล้างแคช...")
        touch_app_py("Brazil", "Norway", 1, 2)
        
        print("\n🐙 ทำการส่งข้อมูลขึ้น GitHub ไปยังระบบคลาวด์ออนไลน์...")
        push_to_github()
    else:
        # หากคะแนนตรงกันหมดแล้ว แต่ต้องการอัปเดตแคชและดัน Git เพื่อความสบายใจ หรือล้างแคชออนไลน์ด่วน
        print("\n😴 ข้อมูล SQLite และ Google Sheets ตรงกันครบถ้วนอยู่แล้ว")
        print("⚡ เพื่อป้องกันปัญหาค้างคาของระบบ แนะนำให้ทำการอัปเดตแคชออนไลน์ด่วน...")
        from auto_update_results import touch_app_py, push_to_github
        touch_app_py("Brazil", "Norway", 1, 2)
        push_to_github()

if __name__ == '__main__':
    sync()
