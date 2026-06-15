import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import os
import json
import streamlit as st

# ตั้งค่า Credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
LOCAL_KEY_PATH = '.secrets/directed-graph-494807-i7-f79a56b5b375.json'
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit'

@st.cache_resource
def get_gspread_client():
    if os.path.exists(LOCAL_KEY_PATH):
        creds = Credentials.from_service_account_file(LOCAL_KEY_PATH, scopes=SCOPES)
    else:
        creds_info = st.secrets["gcp_service_account"]
        if isinstance(creds_info, str):
            creds_info = json.loads(creds_info)
        else:
            creds_info = dict(creds_info)
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return gspread.authorize(creds)

@st.cache_resource
def get_spreadsheet():
    client = get_gspread_client()
    return client.open_by_url(SHEET_URL)

def get_worksheet(name):
    sh = get_spreadsheet()
    return sh.worksheet(name)

def init_db():
    pass

@st.cache_data(ttl=60)
def get_users_df():
    try:
        ws = get_worksheet('users')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['username', 'total_score', 'pin'])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"Error fetching users: {e}")
        return pd.DataFrame(columns=['username', 'total_score', 'pin'])

@st.cache_data(ttl=60)
def get_matches():
    try:
        ws = get_worksheet('matches')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['id', 'home_team', 'away_team', 'match_time', 'home_score', 'away_score', 'status', 'scorers'])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return pd.DataFrame(columns=['id', 'home_team', 'away_team', 'match_time', 'home_score', 'away_score', 'status', 'scorers'])

@st.cache_data(ttl=60)
def get_predictions_df():
    try:
        ws = get_worksheet('predictions')
        data = ws.get_all_values()
        if not data: return pd.DataFrame(columns=['username', 'match_id', 'pred_home', 'pred_away', 'points_earned'])
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return pd.DataFrame(columns=['username', 'match_id', 'pred_home', 'pred_away', 'points_earned'])

def sync_results_from_web():
    results = [
        {'home': 'Mexico', 'away': 'South Africa', 'h_score': 2, 'a_score': 0, 'status': 'Finished'},
        {'home': 'South Korea', 'away': 'Czech Republic', 'h_score': 2, 'a_score': 1, 'status': 'Finished'},
        {'home': 'Canada', 'away': 'Bosnia and Herzegovina', 'id': 3},
        {'home': 'USA', 'away': 'Paraguay', 'id': 4}
    ]
    
    ws = get_worksheet('matches')
    data = ws.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    
    updated_count = 0
    for res in results:
        if res.get('status') == 'Finished':
            mask = (df['home_team'] == res['home']) & (df['away_team'] == res['away']) & (df['status'] == 'Upcoming')
            if mask.any():
                idx = df.index[mask][0]
                df.at[idx, 'home_score'] = res['h_score']
                df.at[idx, 'away_score'] = res['a_score']
                df.at[idx, 'status'] = 'Finished'
                updated_count += 1
        elif 'id' in res:
            mask = (df['id'].astype(str) == str(res['id'])) & (df['home_team'].str.startswith('TBD') | df['away_team'].str.startswith('TBD'))
            if mask.any():
                idx = df.index[mask][0]
                df.at[idx, 'home_team'] = res['home']
                df.at[idx, 'away_team'] = res['away']
                updated_count += 1
                
    if updated_count > 0:
        ws.clear()
        ws.update([df.columns.values.tolist()] + df.values.tolist())
        update_scores_logic()
    st.cache_data.clear()
    st.cache_resource.clear()
    return updated_count

def normalize_name(username):
    # ... (เหมือนเดิม)
    name = username.strip()
    return 'Art' if name.lower() == 'art' else name

def has_pin(username):
    name = normalize_name(username)
    df = get_users_df()
    if df.empty: return False
    user_row = df[df['username'] == name]
    return not user_row.empty and user_row.iloc[0]['pin'] != ""

def get_or_create_user(username, pin=None):
    name = normalize_name(username)
    ws = get_worksheet('users')
    df = get_users_df()
    
    if name not in df['username'].values:
        new_row = [name, 0, pin if pin else ""]
        ws.append_row(new_row)
    elif pin:
        idx = df.index[df['username'] == name][0] + 2
        ws.update_cell(idx, 3, pin)
    st.cache_data.clear()

def verify_user(username, pin):
    name = normalize_name(username)
    df = get_users_df()
    if df.empty: return False
    user_row = df[df['username'] == name]
    return not user_row.empty and str(user_row.iloc[0]['pin']) == str(pin)

def save_prediction(username, match_id, pred_home, pred_away):
    name = normalize_name(username)
    ws = get_worksheet('predictions')
    df = get_predictions_df()
    
    mask = (df['username'] == name) & (df['match_id'].astype(str) == str(match_id))
    if mask.any():
        idx = df.index[mask][0] + 2
        # ใช้ update แบบระบุ range เพื่อความปลอดภัยใน gspread 6.x
        ws.update(f'C{idx}:D{idx}', [[int(pred_home), int(pred_away)]])
    else:
        ws.append_row([name, match_id, int(pred_home), int(pred_away), 0])
    st.cache_data.clear()

def get_user_predictions(username):
    name = normalize_name(username)
    df = get_predictions_df()
    if df.empty: return {}
    user_preds = df[df['username'] == name]
    preds = {}
    for _, row in user_preds.iterrows():
        try:
            m_id = int(row['match_id'])
            p_h = int(row['pred_home']) if row['pred_home'] != "" else 0
            p_a = int(row['pred_away']) if row['pred_away'] != "" else 0
            preds[m_id] = (p_h, p_a)
        except:
            continue
    return preds

def get_leaderboard():
    df_u = get_users_df()
    df_p = get_predictions_df()
    if df_u.empty: return pd.DataFrame(columns=['username', 'total_score', 'pin'])
    
    active_users = df_p['username'].unique() if not df_p.empty else []
    df_u = df_u[df_u['username'].isin(active_users)]
    df_u['total_score'] = pd.to_numeric(df_u['total_score'], errors='coerce').fillna(0).astype(int)
    return df_u.sort_values('total_score', ascending=False)

def get_prediction_history():
    df_p = get_predictions_df()
    df_m = get_matches()
    if df_p.empty or df_m.empty: return pd.DataFrame()
    
    merged = df_p.merge(df_m, left_on='match_id', right_on='id')
    
    res = []
    for _, row in merged.iterrows():
        real = f"{row['home_score']}-{row['away_score']}" if row['status'] == 'Finished' else ( "Live" if row['status'] == 'Live' else "Upcoming")
        res.append({
            'username': row['username'],
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'prediction': f"{row['pred_home']}-{row['pred_away']}",
            'real_score': real,
            'points': row['points_earned'],
            'match_time': row['match_time']
        })
    return pd.DataFrame(res)

def update_scores_logic():
    ws_m = get_worksheet('matches')
    data_m = ws_m.get_all_values()
    df_m = pd.DataFrame(data_m[1:], columns=data_m[0])
    
    ws_p = get_worksheet('predictions')
    data_p = ws_p.get_all_values()
    df_p = pd.DataFrame(data_p[1:], columns=data_p[0])
    
    df_m['id_int'] = pd.to_numeric(df_m['id'], errors='coerce').fillna(0).astype(int)
    df_p['match_id_int'] = pd.to_numeric(df_p['match_id'], errors='coerce').fillna(0).astype(int)
    
    finished = df_m[(df_m['status'] == 'Finished') & (df_m['id_int'] >= 12)]
    
    mask_old = df_p['match_id_int'] < 12
    df_p.loc[mask_old, 'points_earned'] = '0'
    
    for _, m in finished.iterrows():
        m_id = str(m['id'])
        r_h = int(m['home_score']) if str(m['home_score']).strip() != "" else 0
        r_a = int(m['away_score']) if str(m['away_score']).strip() != "" else 0
        
        mask = df_p['match_id'].astype(str) == m_id
        for idx, p in df_p[mask].iterrows():
            p_h = int(p['pred_home']) if str(p['pred_home']).strip() != "" else 0
            p_a = int(p['pred_away']) if str(p['pred_away']).strip() != "" else 0
            points = 0
            if p_h == r_h and p_a == r_a:
                points = 3
            else:
                pred_win = (p_h > p_a) - (p_h < p_a)
                real_win = (r_h > r_a) - (r_h < r_a)
                if pred_win == real_win:
                    points = 1
            df_p.at[idx, 'points_earned'] = str(points)
            
    df_p_save = df_p.drop(columns=['match_id_int'])
    # ล้างชีตก่อนอัปเดตเพื่อป้องกันข้อมูลเก่าค้าง
    ws_p.clear()
    ws_p.update([df_p_save.columns.values.tolist()] + df_p_save.values.tolist())
    
    ws_u = get_worksheet('users')
    data_u = ws_u.get_all_values()
    df_u = pd.DataFrame(data_u[1:], columns=data_u[0])
    
    # คำนวณคะแนนใหม่
    df_p['points_earned_int'] = pd.to_numeric(df_p['points_earned'], errors='coerce').fillna(0).astype(int)
    for idx, u in df_u.iterrows():
        user_points = df_p[df_p['username'] == u['username']]['points_earned_int'].sum()
        df_u.at[idx, 'total_score'] = str(int(user_points))
        
    ws_u.clear()
    ws_u.update([df_u.columns.values.tolist()] + df_u.values.tolist())
    st.cache_data.clear()
    st.cache_resource.clear()

