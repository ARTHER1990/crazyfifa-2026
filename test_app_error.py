import sys
import os
import pandas as pd
from datetime import datetime, timezone, timedelta

# เพิ่ม path ค้นหาโมดูล
BASE_DIR = "/Users/art/Desktop/ART_JOB/ฟุตบอลโลก2026"
sys.path.append(BASE_DIR)

import database as db

# จำลอง Session State ใน Streamlit
class MockSessionState:
    def __init__(self):
        self.username = "Art"
        self.authenticated = True
        self.toast_shown = False
        self.unpredicted_count = 0
        self.unpredicted_matches = []

def test_flow():
    print("🔄 เริ่มการทดสอบดึงข้อมูลและจำลอง flow หลังเข้าสู่ระบบ...")
    
    # 1. ลองดึง matches และ users
    try:
        matches = db.get_matches()
        print(f"✅ ดึง Matches สำเร็จ (จำนวน {len(matches)} แถว)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึง Matches: {e}")
        import traceback; traceback.print_exc()
        return

    try:
        users = db.get_users_df()
        print(f"✅ ดึง Users สำเร็จ (จำนวน {len(users)} แถว)")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึง Users: {e}")
        import traceback; traceback.print_exc()
        return

    # 2. จำลองระบบเตือนความจำ (Smart Prediction Reminder) ใน app.py บรรทัดที่ 1005+
    print("\n🔍 ทดสอบระบบคำนวณคู่ที่ยังไม่ได้ทายผล (Reminder)...")
    try:
        all_matches_rem = db.get_matches()
        all_matches_rem['match_dt'] = pd.to_datetime(all_matches_rem['match_time'])
        now_th_rem = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        
        active_upcoming_rem = all_matches_rem[
            (all_matches_rem['status'] != 'Finished') & 
            (all_matches_rem['match_dt'] > now_th_rem)
        ]
        
        user_preds_rem = db.get_user_predictions("Art")
        unpredicted_list = []
        for _, row in active_upcoming_rem.iterrows():
            m_id = int(row['id'])
            if m_id not in user_preds_rem:
                unpredicted_list.append(row)
                
        print(f"✅ คำนวณคู่ที่ยังไม่ได้ทายผลสำเร็จ: {len(unpredicted_list)} คู่")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบ Reminder: {e}")
        import traceback; traceback.print_exc()

    # 3. จำลองแถบสรุปผลแข่งวันนี้ใน Sidebar ใน app.py บรรทัดที่ 1053+
    print("\n📊 ทดสอบระบบสรุปผลแข่งขันวันนี้ (Sidebar)...")
    try:
        all_matches_sb = db.get_matches()
        all_matches_sb['match_dt'] = pd.to_datetime(all_matches_sb['match_time'])
        finished_sb = all_matches_sb[all_matches_sb['status'] == 'Finished'].sort_values('match_time', ascending=False)
        
        if not finished_sb.empty:
            now_th_sb = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            today_date_sb = now_th_sb.date()
            day_matches_sb = finished_sb[finished_sb['match_dt'].dt.date == today_date_sb]
            
            print(f"📅 จำนวนนัดเตะเสร็จสิ้นวันนี้: {len(day_matches_sb)}")
            predictions_sb = db.get_predictions_df()
            
            for _, row_m in day_matches_sb.iterrows():
                m_id = str(row_m['id'])
                
                # ทดสอบจุดแปลงคะแนนที่เสี่ยงพัง
                home_score_str = str(row_m['home_score']).strip()
                away_score_str = str(row_m['away_score']).strip()
                
                h_real = int(home_score_str) if home_score_str != "" and home_score_str != "None" else 0
                a_real = int(away_score_str) if away_score_str != "" and away_score_str != "None" else 0
                
                print(f"⚽ แมตช์ {row_m['home_team']} vs {row_m['away_team']}: ผล {h_real} - {a_real}")
        else:
            print("📅 ไม่มีนัดเตะที่สิ้นสุดการแข่งขันเลย")
        print("✅ ผ่านขั้นตอนสรุปผลแข่งใน Sidebar สำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบสรุปผลแข่ง Sidebar: {e}")
        import traceback; traceback.print_exc()

    # 4. จำลองตรรกะในหน้าทายผลหลัก (app.py บรรทัดที่ 1193+)
    print("\n🏟️ ทดสอบตรรกะหน้าทายผลหลัก...")
    try:
        all_matches = db.get_matches()
        all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])
        
        # ค้นหา unique dates และการจัดกลุ่ม
        upcoming = all_matches[all_matches['status'] != 'Finished'].sort_values('match_time')
        if not upcoming.empty:
            unique_dates = upcoming['match_dt'].dt.date.unique()
            print(f"📅 วันที่แข่งขันที่จะถึงมี {len(unique_dates)} วัน: {list(unique_dates)}")
            for d in unique_dates:
                day_matches = upcoming[upcoming['match_dt'].dt.date == d]
                print(f" - วันที่ {d.strftime('%d/%m/%Y')} มีแข่ง {len(day_matches)} คู่")
                for _, row in day_matches.iterrows():
                    match_id = row['id']
                    home = row['home_team']
                    away = row['away_team']
                    m_time = datetime.strptime(row['match_time'], '%Y-%m-%d %H:%M:%S')
                    status = row['status']
                    
                    # ตรวจสอบการพังของการแปลงผลทาย
                    user_preds_cached = db.get_user_predictions("Art")
                    default_h, default_a = user_preds_cached.get(int(match_id), (0, 0))
                    
                    if status == 'Finished':
                        val_h = int(row['home_score']) if str(row['home_score']).strip() != "" else 0
                        val_a = int(row['away_score']) if str(row['away_score']).strip() != "" else 0
                    else:
                        val_h = int(default_h)
                        val_a = int(default_a)
        else:
            print("📅 ไม่มีนัดเตะที่กำลังจะมาถึงเลย")
        print("✅ ผ่านขั้นตอนหน้าทายผลหลักสำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในหน้าทายผลหลัก: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    test_flow()
