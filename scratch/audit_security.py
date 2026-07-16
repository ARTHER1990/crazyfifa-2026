import sys
import os
import sqlite3
import pandas as pd

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import database as db

def calculate_expected_points(pred_home, pred_away, real_home, real_away, pred_qualify=None, real_qualify=None, is_knockout=False):
    try:
        ph = int(pred_home) if str(pred_home).strip() != "" else 0
        pa = int(pred_away) if str(pred_away).strip() != "" else 0
        rh = int(real_home) if str(real_home).strip() != "" else 0
        ra = int(real_away) if str(real_away).strip() != "" else 0
    except ValueError:
        return 0, 0, 0
    
    # คิดคะแนนปกติ
    match_points = 0
    if ph == rh and pa == ra:
        match_points = 3
    else:
        pred_win = (ph > pa) - (ph < pa)
        real_win = (rh > ra) - (rh < ra)
        if pred_win == real_win:
            match_points = 1
            
    # คิดคะแนนโบนัส
    bonus_points = 0
    if is_knockout and real_qualify and str(real_qualify).strip() != "" and str(real_qualify).lower() != "nan":
        pq = str(pred_qualify).strip() if pred_qualify else ""
        if pq == "":
            if ph > pa:
                pq = "home"  # fallback ชั่วคราว
            elif pa > ph:
                pq = "away"
        
        # เปรียบเทียบผู้เข้ารอบจริงกับที่ทาย
        rq = str(real_qualify).strip().lower()
        pq = pq.lower()
        
        if pq == rq:
            bonus_points = 1
            
    return match_points + bonus_points, match_points, bonus_points

def audit():
    print("======================================================================")
    print("🛡️  เริ่มการตรวจสอบความมั่นคงปลอดภัยและสืบสวนคะแนนดิบ (Security Audit) 🛡️")
    print("======================================================================\n")

    # 1. ดึงข้อมูลดิบสดๆ จาก Google Sheets
    print("📡 1. กำลังดึงข้อมูลล่าสุดจาก Google Sheets...")
    try:
        db.get_users_df.clear()
        db.get_matches.clear()
        db.get_predictions_df.clear()
        
        df_users = db.get_users_df()
        df_matches = db.get_matches()
        df_preds = db.get_predictions_df()
        
        print(f"✅ โหลดข้อมูลผู้เล่น {len(df_users)} คน, แมตช์ {len(df_matches)} คู่, การทำนาย {len(df_preds)} แถว สำเร็จ!\n")
    except Exception as e:
        print(f"❌ โหลดข้อมูลจาก Google Sheets ล้มเหลว: {e}")
        return

    # กรองข้อมูล
    df_matches['id_int'] = pd.to_numeric(df_matches['id'], errors='coerce').fillna(0).astype(int)
    finished_matches = df_matches[(df_matches['status'] == 'Finished') & (df_matches['id_int'] >= 12)]
    finished_map = {str(row['id']): row for _, row in finished_matches.iterrows()}
    
    # 2. ตรวจสอบการคิดแต้มรายแมตช์ใน Google Sheets (มีใครแก้ตัวเลขคะแนนในชีตโดยที่ทายผิดไหม)
    print("🕵️ 2. ตรวจสอบความสอดคล้องคะแนนรายแมตช์ (คำนวณจริง VS บันทึกในชีต)...")
    mismatched_predictions = []
    
    for idx, pred in df_preds.iterrows():
        m_id = str(pred['match_id'])
        user = pred['username']
        
        # สนใจเฉพาะแมตช์ที่แข่งเสร็จและคิดคะแนนแล้ว
        if m_id in finished_map:
            match = finished_map[m_id]
            is_ko = int(m_id) >= 68
            
            # ดึงผู้เข้ารอบจริงและผู้เข้ารอบทาย
            real_winner_qualify = match.get('winner_qualify', '')
            if (not real_winner_qualify or str(real_winner_qualify).lower() == 'nan') and is_ko:
                # คำนวณผู้ชนะตามสกอร์จริงกรณีชีตเว้นว่าง
                try:
                    if int(match['home_score']) > int(match['away_score']):
                        real_winner_qualify = match['home_team']
                    else:
                        real_winner_qualify = match['away_team']
                except:
                    pass
            
            pred_winner_qualify = pred.get('pred_qualify', '')
            if not pred_winner_qualify or str(pred_winner_qualify).strip() == '':
                try:
                    if int(pred['pred_home']) > int(pred['pred_away']):
                        pred_winner_qualify = match['home_team']
                    elif int(pred['pred_away']) > int(pred['pred_home']):
                        pred_winner_qualify = match['away_team']
                except:
                    pass
            
            # คำนวณแต้มที่แท้จริง
            expected, m_pts, b_pts = calculate_expected_points(
                pred['pred_home'], pred['pred_away'],
                match['home_score'], match['away_score'],
                pred_winner_qualify, real_winner_qualify,
                is_ko
            )
            
            # แต้มที่บันทึกจริงในชีต
            try:
                actual = int(float(pred['points_earned'])) if str(pred['points_earned']).strip() != "" else 0
            except:
                actual = 0
                
            if expected != actual:
                mismatched_predictions.append({
                    'username': user,
                    'match_id': m_id,
                    'match_desc': f"{match['home_team']} vs {match['away_team']}",
                    'pred': f"{pred['pred_home']}-{pred['pred_away']}",
                    'real': f"{match['home_score']}-{match['away_score']}",
                    'expected': expected,
                    'actual': actual
                })

    if mismatched_predictions:
        print(f"⚠️  🚨 พบความแตกต่างคะแนนรายแมตช์ {len(mismatched_predictions)} รายการ!:")
        for mp in mismatched_predictions:
            print(f"   [!] ผู้เล่น: {mp['username']:12} | คู่ {mp['match_id']}: {mp['match_desc']:22} | ทาย: {mp['pred']:5} | จริง: {mp['real']:5} | ควรได้: {mp['expected']} แต้ม | แต่บันทึก: {mp['actual']} แต้ม")
    else:
        print("   ✅ คะแนนรายแมตช์ของทุกคนตรงกับผลทายจริง 100% (ไม่มีการโกงตัวเลขคะแนนสะสมรายนัด)")
    print("")

    # 3. ตรวจสอบความสอดคล้องคะแนนรวมสะสม (users.total_score VS ผลรวมแต้มทำนายจริง)
    print("🕵️ 3. ตรวจสอบความสอดคล้องคะแนนสะสมรวมของผู้เล่นแต่ละคน...")
    mismatched_users = []
    
    # รวมคะแนนจริงของผู้ใช้แต่ละคนจากประวัติการทายผลทั้งหมด
    calculated_totals = {}
    for idx, pred in df_preds.iterrows():
        user = pred['username']
        m_id = str(pred['match_id'])
        
        # กรองเฉพาะแมตช์ที่คิดแต้มแล้ว
        if m_id in finished_map:
            match = finished_map[m_id]
            is_ko = int(m_id) >= 68
            
            real_winner_qualify = match.get('winner_qualify', '')
            if (not real_winner_qualify or str(real_winner_qualify).lower() == 'nan') and is_ko:
                try:
                    if int(match['home_score']) > int(match['away_score']):
                        real_winner_qualify = match['home_team']
                    else:
                        real_winner_qualify = match['away_team']
                except:
                    pass
            
            pred_winner_qualify = pred.get('pred_qualify', '')
            if not pred_winner_qualify or str(pred_winner_qualify).strip() == '':
                try:
                    if int(pred['pred_home']) > int(pred['pred_away']):
                        pred_winner_qualify = match['home_team']
                    elif int(pred['pred_away']) > int(pred['pred_home']):
                        pred_winner_qualify = match['away_team']
                except:
                    pass
                    
            expected, _, _ = calculate_expected_points(
                pred['pred_home'], pred['pred_away'],
                match['home_score'], match['away_score'],
                pred_winner_qualify, real_winner_qualify,
                is_ko
            )
            calculated_totals[user] = calculated_totals.get(user, 0) + expected
        else:
            # สำหรับคู่ที่ยังไม่แข่งหรือแมตช์ id < 12 (ไม่คิดแต้ม)
            calculated_totals[user] = calculated_totals.get(user, 0) + 0

    for idx, user_row in df_users.iterrows():
        user = user_row['username']
        try:
            score_in_sheet = int(float(user_row['total_score'])) if str(user_row['total_score']).strip() != "" else 0
        except:
            score_in_sheet = 0
            
        expected_total = calculated_totals.get(user, 0)
        
        if score_in_sheet != expected_total:
            mismatched_users.append({
                'username': user,
                'sheet_total': score_in_sheet,
                'expected_total': expected_total
            })

    if mismatched_users:
        print(f"⚠️  🚨 พบความแตกต่างของผลรวมคะแนนสะสม {len(mismatched_users)} คน!:")
        for mu in mismatched_users:
            print(f"   [!] ผู้เล่น: {mu['username']:12} | คะแนนสะสมในชีต: {mu['sheet_total']:3} แต้ม | แต่คำนวณจริงจากประวัติทายผลได้: {mu['expected_total']:3} แต้ม")
    else:
        print("   ✅ คะแนนสะสมรวมของทุกคนสอดคล้องกับประวัติการทำนายจริง 100% (ไม่มีคะแนนสะสมงอกลอยหรือแก้ไขตรงๆ)")
    print("")

    # 4. เปรียบเทียบข้อมูลสดใน Google Sheets กับฐานข้อมูล SQLite ท้องถิ่น (ตรวจหาการลักลอบแก้ไขย้อนหลัง)
    print("🕵️ 4. ตรวจสอบการแก้ไขผลทายย้อนหลัง (Google Sheets VS SQLite โลคัล)...")
    db_path = os.path.join(BASE_DIR, 'worldcup.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, match_id, pred_home, pred_away, pred_qualify FROM predictions")
        sql_rows = cursor.fetchall()
        sql_map = {f"{row[0]}_{row[1]}": row for row in sql_rows}
        conn.close()
        
        modified_predictions = []
        for idx, pred in df_preds.iterrows():
            key = f"{pred['username']}_{pred['match_id']}"
            m_id = str(pred['match_id'])
            
            # เราจะสนใจเฉพาะคู่แข่งขันที่ Finished แล้วเท่านั้น (ถ้าคู่ยังไม่เริ่มเตะ สามารถเปลี่ยนได้ปกติไม่ถือว่าโกง)
            if m_id in finished_map:
                match = finished_map[m_id]
                
                if key in sql_map:
                    _, _, sql_ph, sql_pa, sql_pq = sql_map[key]
                    
                    sheet_ph = str(pred['pred_home']).strip()
                    sheet_pa = str(pred['pred_away']).strip()
                    sheet_pq = str(pred.get('pred_qualify', '')).strip()
                    
                    sql_ph_str = str(sql_ph).strip() if sql_ph is not None else ""
                    sql_pa_str = str(sql_pa).strip() if sql_pa is not None else ""
                    sql_pq_str = str(sql_pq).strip() if sql_pq is not None else ""
                    
                    # เช็คว่าผลทำนายในชีตไม่ตรงกับ SQLite ที่เสถียรในเครื่อง
                    if sheet_ph != sql_ph_str or sheet_pa != sql_pa_str or sheet_pq != sql_pq_str:
                        modified_predictions.append({
                            'username': pred['username'],
                            'match_id': m_id,
                            'match_desc': f"{match['home_team']} vs {match['away_team']}",
                            'old_pred': f"{sql_ph_str}-{sql_pa_str}" + (f" ({sql_pq_str})" if sql_pq_str else ""),
                            'new_pred': f"{sheet_ph}-{sheet_pa}" + (f" ({sheet_pq})" if sheet_pq else "")
                        })
                        
        if modified_predictions:
            print(f"⚠️  🚨 ตรวจพบการลักลอบแก้ไขคำทำนายหลังจากแมตช์จบการแข่งขันแล้ว {len(modified_predictions)} รายการ!:")
            for mp in modified_predictions:
                print(f"   [!] ผู้เล่น: {mp['username']:12} | คู่ {mp['match_id']}: {mp['match_desc']:22} | คำทำนายเดิมใน SQLite: {mp['old_pred']:10} -> ถูกแก้ในชีตสดเป็น: {mp['new_pred']}")
        else:
            print("   ✅ ไม่พบการแก้ไขผลการทายย้อนหลังในแมตช์ที่เตะจบแล้วเมื่อเทียบกับ SQLite ท้องถิ่น")
    except Exception as e:
        print(f"⚠️ ไม่สามารถตรวจสอบประวัติกับ SQLite ได้: {e}")
    
    print("\n======================================================================")
    print("🛡️  เสร็จสิ้นการตรวจสอบความมั่นคงปลอดภัย")
    print("======================================================================")

if __name__ == '__main__':
    audit()
