import sys
import os
import sqlite3
import pandas as pd

# ตั้งค่า path เพื่อให้ค้นหาโมดูลในระบบได้ถูกต้อง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import database as db

def main():
    print("🚀 เริ่มระบบ Force Flush ล้างแคชและล้างข้อมูลเก่าค้างคาหลังบ้านแบบ 100%...")

    targets_to_remove = ['68', '69', '70']

    # 1. ลบเรคคอร์ดขยะในตาราง predictions ของ Google Sheets (ของ FAII)
    print("\n📊 [1/4] กำลังลบเรคคอร์ดขยะใน Google Sheets (แผ่น predictions)...")
    try:
        ws_pred = db.get_worksheet('predictions')
        data_pred = ws_pred.get_all_values()
        df_pred = pd.DataFrame(data_pred[1:], columns=data_pred[0])
        
        initial_pred_count = len(df_pred)
        df_pred_filtered = df_pred[~df_pred['match_id'].astype(str).isin(targets_to_remove)]
        removed_pred = initial_pred_count - len(df_pred_filtered)
        
        if removed_pred > 0:
            ws_pred.clear()
            ws_pred.update([df_pred_filtered.columns.values.tolist()] + df_pred_filtered.astype(str).values.tolist())
            print(f"🗑️ (Sheets Predictions) ลบสำเร็จ {removed_pred} แถว ของ ID {targets_to_remove}!")
        else:
            print("✅ (Sheets Predictions) ไม่มีคู่ขยะหลงเหลือในแผ่น predictions")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการปรับแผ่น predictions ใน Google Sheets: {e}")

    # 2. บังคับอัปเดตไฟล์ Backup ท้องถิ่น (.backup_data/) ให้เป็นข้อมูลล่าสุดที่ลบแล้ว
    print("\n📂 [2/4] กำลังล้างและอัปเดตไฟล์ Local Backups (.backup_data/)...")
    try:
        backup_dir = os.path.join(BASE_DIR, '.backup_data')
        
        # ดึง matches ใหม่ล่าสุดที่ไม่มีคู่ขยะและบันทึกทับ backup ท้องถิ่น
        ws_matches = db.get_worksheet('matches')
        data_m = ws_matches.get_all_values()
        df_m = pd.DataFrame(data_m[1:], columns=data_m[0])
        db.save_local_backup('matches', df_m)
        print("💾 บันทึกทับไฟล์ matches.json backup ท้องถิ่นสำเร็จ!")

        # ดึง predictions ใหม่ล่าสุดบันทึกทับ backup ท้องถิ่น
        if 'df_pred_filtered' in locals():
            db.save_local_backup('predictions', df_pred_filtered)
            print("💾 บันทึกทับไฟล์ predictions.json backup ท้องถิ่นสำเร็จ!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการบันทึกทับ Local Backups: {e}")

    # 3. ล้างตาราง SQLite matches และ predictions ในเครื่องจริง
    print("\n🗄️ [3/4] กำลังตรวจสอบความคลีนใน SQLite (worldcup.db)...")
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'worldcup.db'))
        cursor = conn.cursor()
        
        # ตรวจเช็ค matches
        cursor.execute("DELETE FROM matches WHERE id IN (68, 69, 70);")
        cursor.execute("DELETE FROM predictions WHERE match_id IN (68, 69, 70);")
        conn.commit()
        conn.close()
        print("✅ เคลียร์ความสะอาดในฐานข้อมูล SQLite เรียบร้อย!")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน SQLite: {e}")

    # 4. บังคับเคลียร์แคช RAM ของ Streamlit (Cache Invalidation)
    print("\n⚡ [4/4] กำลังดำเนินการล้างแคช RAM หลังบ้าน...")
    try:
        # การเคลียร์ resource และ data cache สดๆ
        db.get_gspread_client.clear()
        db.get_spreadsheet.clear()
        db.get_users_df.clear()
        db.get_matches.clear()
        db.get_predictions_df.clear()
        print("🎉 ล้างแคช RAM ภายในหน่วยความจำฝั่ง Python สำเร็จ!")
    except Exception as e:
        print(f"⚠️ เกิดข้อผิดพลาดเบาบางในการล้างแคช RAM: {e}")

if __name__ == '__main__':
    main()
