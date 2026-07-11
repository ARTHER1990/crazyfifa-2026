# Last cache clear and score update: 2026-07-12 05:54 (Auto updated: Norway Live-Live England)
import streamlit as st
import mimetypes
mimetypes.add_type("audio/mp3", ".mp3")
mimetypes.add_type("audio/mpeg", ".mp3")
import database as db
from datetime import datetime, timedelta, timezone
import pandas as pd
import base64
import os
import streamlit.components.v1 as components

# ฟังก์ชันล้างไฟล์ขยะ Icon\r ในโฟลเดอร์ .git ป้องกันปัญหา git bad ref refs/tags/Icon? ถาวร
def cleanup_git_icons():
    try:
        git_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".git")
        if os.path.exists(git_dir):
            for root, dirs, files in os.walk(git_dir):
                for file in files:
                    if file.startswith("Icon"):
                        try:
                            os.remove(os.path.join(root, file))
                        except:
                            pass
    except:
        pass

cleanup_git_icons()

current_dir = os.path.dirname(os.path.abspath(__file__))

# ตรรกะเปิดใช้งานระบบทำนายผลแชมป์โลก (เปิดใช้งานทันทีหลังจากแก้ไขข้อมูลทีมรอบ 16 ทีมถูกต้องครบถ้วนตามความจริงของฟีฟ่า)
IS_CHAMPION_PRED_ACTIVE = True

# ฟังก์ชันสำหรับแปลงค่าตัวเลขอย่างปลอดภัย (ดักจับ None, NaN, ช่องว่าง)
def safe_int(val, default=0):
    if val is None:
        return default
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return default
        return int(val)
    val_str = str(val).strip()
    if val_str == "" or val_str.lower() in ("nan", "none", "null"):
        return default
    try:
        return int(val_str)
    except:
        return default


# แคชระดับโมดูลเพื่อประมวลผลความเร็วสูงสุด (เก็บไว้ใน RAM ข้ามการล้างแคช st.cache_data.clear() ได้อย่างพรีเมี่ยม)
_IMAGE_CACHE = {}
_AUDIO_CACHE = {}
_AUDIO_BASE64_CACHE = {}

# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64
def get_base64_image(image_path):
    if image_path in _IMAGE_CACHE:
        return _IMAGE_CACHE[image_path]
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()
        _IMAGE_CACHE[image_path] = b64
        return b64

# ฟังก์ชันแปลงไฟล์เสียงเป็น Base64 และแคชเก็บใน RAM เพื่อความเร็วกริบไร้รอยต่อ
def get_base64_audio(audio_path):
    if audio_path in _AUDIO_BASE64_CACHE:
        return _AUDIO_BASE64_CACHE[audio_path]
        
    actual_path = audio_path
    if not os.path.exists(actual_path):
        # ตรวจสอบหาไฟล์ในไดเรกทอรี static เผื่อพาร์ทมีการคลาดเคลื่อน
        basename = os.path.basename(audio_path)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(current_dir, "static", basename)
        if os.path.exists(alt_path):
            actual_path = alt_path
        else:
            # ค้นหาไฟล์สำรอง bg_music.mp3 ในห้อง static
            alt_path_music = os.path.join(current_dir, "static", "bg_music.mp3")
            if os.path.exists(alt_path_music):
                actual_path = alt_path_music
            else:
                # ลองค้นหาไฟล์ .webp สำรองบนเว็บเซิร์ฟเวอร์
                alt_path_webp = os.path.join(current_dir, "static", "bg_music.webp")
                if os.path.exists(alt_path_webp):
                    actual_path = alt_path_webp
                else:
                    return ""
                    
    try:
        with open(actual_path, "rb") as audio_file:
            b64 = base64.b64encode(audio_file.read()).decode()
            _AUDIO_BASE64_CACHE[audio_path] = b64
            return b64
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return ""

# ฟังก์ชันสำหรับเพลง
def get_audio_html(is_off=False):
    return ""

def render_audio_hosts_in_sidebar():
    return ""

def get_ambient_audio_html():
    return ""

def get_peter_voice_html(session_audio_id="default_id"):
    return ""

def show_standalone_radio_player():
    st.set_page_config(page_title="CrazyFIFA Peter AI Radio", page_icon="📻", layout="centered")
    
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* นำเข้าฟอนต์ Kanit จาก Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600;700&display=swap');
            
            body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #070f14 0%, #0d1e26 50%, #152f3d 100%) !important;
                color: #ffffff !important;
                font-family: 'Kanit', sans-serif !important;
            }
            .radio-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 30px;
                border-radius: 24px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 215, 0, 0.2);
                backdrop-filter: blur(12px);
                box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
                max-width: 400px;
                margin: 40px auto;
            }
            .spinning-disc {
                width: 140px;
                height: 140px;
                border-radius: 50%;
                border: 5px solid #00FF87;
                background: radial-gradient(circle, #000 25%, #222 65%, #050505 70%);
                animation: spin 4s linear infinite;
                box-shadow: 0 0 30px rgba(0, 255, 135, 0.5);
                margin-bottom: 25px;
                position: relative;
            }
            .spinning-disc::after {
                content: "";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 30px;
                height: 30px;
                background: #0d1e26;
                border-radius: 50%;
                border: 3px solid #00FF87;
            }
            @keyframes spin {
                100% { transform: rotate(360deg); }
            }
            .glowing-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #00FF87;
                text-shadow: 0 0 15px rgba(0, 255, 135, 0.4);
                margin-bottom: 8px;
                letter-spacing: 1px;
            }
            .subtitle {
                font-size: 0.95rem;
                opacity: 0.85;
                margin-bottom: 12px;
                color: #60EFFF;
            }
            .info-box {
                font-size: 0.8rem;
                background: rgba(0, 0, 0, 0.3);
                padding: 10px 15px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-top: 15px;
                line-height: 1.4;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="radio-container">
        <div class="spinning-disc"></div>
        <div class="glowing-title">📻 PETER AI RADIO</div>
        <div class="subtitle">วิทยุขอบสนามบอลโลก 2026</div>
        <p style="font-size: 0.9rem; opacity: 0.75; margin: 0 0 15px 0;">ดนตรี Shakira x Burna Boy และเสียงพากย์ปีเตอร์ AI</p>
        <div class="info-box">
            👉 <b>ย่อหน้าต่างนี้ทิ้งไว้ได้เลยครับ</b> เสียงจะเล่นยาวต่อเนื่อง 100% โดยไม่กระตุกหรือเริ่มต้นใหม่เมื่อสลับดูแท็บข้อมูลในหน้าต่างหลัก
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    song_path = os.path.join(current_dir, "Shakira Burna Boy Dai Dai Official Video.mp3")
    audio_html = get_audio_html(song_path, session_audio_id="standalone_radio_session")
    
    st.markdown(audio_html, unsafe_allow_html=True)

# ตรวจสอบว่าเป็นการเรียกเปิดวิทยุปีเตอร์แบบ Standalone ในหน้าต่างใหม่หรือไม่
if st.query_params.get("embed_player") == "true":
    show_standalone_radio_player()
    st.stop()

current_dir = os.path.dirname(os.path.abspath(__file__))
image_full_path = os.path.join(current_dir, "ต่างดาว_optimized.webp")
ufo_base64 = get_base64_image(image_full_path)

# โหลดภาพพิซซ่านาโปลี (พิซซ่า.png) สำหรับลอยเป็น Easter Egg ลำที่ 4
pizza_path = os.path.join(current_dir, "พิซซ่า.png")
pizza_base64 = get_base64_image(pizza_path)

# โหลดภาพ Artwork พื้นหลัง Sidebar (เปลี่ยนจาก Messi เป็น 02.png ตามสั่ง)
bg_sidebar_path = os.path.join(current_dir, "02_optimized.png")
bg_sidebar_base64 = get_base64_image(bg_sidebar_path)

# โหลดภาพแบนเนอร์ของคุณอาร์ต เครซีเว็ป.png
banner_path = os.path.join(current_dir, "เครซีเว็ป.png")
banner_base64 = get_base64_image(banner_path)

# โหลดภาพลูกบอลทัวร์นาเมนต์ ball2026.png
ball_path = os.path.join(current_dir, "ball2026.png")
ball_base64 = get_base64_image(ball_path)

# โหลดภาพ บอลโลก_optimized.webp สำหรับเป็นแบคกราวด์บางๆ ด้านหลังเนื้อหาทำนายผลแชมป์โลกแบบเบาหวิวปานสายฟ้าแลบ
worldcup_bg_path = os.path.join(current_dir, "บอลโลก_optimized.webp")
worldcup_bg_base64 = get_base64_image(worldcup_bg_path)

def safe_markdown(content):
    # ล้างบรรทัดว่าง (Blank lines) ออกทั้งหมดเพื่อป้องกัน Streamlit markdown parser ตีความผิดเป็นข้อความดิบ
    lines = [line for line in content.splitlines() if line.strip() != ""]
    cleaned_content = "\n".join(lines)
    st.markdown(cleaned_content, unsafe_allow_html=True)


# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="🏆 CRAZYFIFA WORLD CUP 2026", layout="wide", page_icon="⚽")

# แผนผังธงชาติ (Lowercase keys สำหรับความยืดหยุ่นสูง)
FLAG_MAP = {
    'mexico': '🇲🇽', 'south africa': '🇿🇦', 'south korea': '🇰🇷', 'czech republic': '🇨🇿',
    'canada': '🇨🇦', 'bosnia and herzegovina': '🇧🇦', 'usa': '🇺🇸', 'paraguay': '🇵🇾',
    'spain': '🇪🇸', 'morocco': '🇲🇦', 'england': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'australia': '🇦🇺',
    'qatar': '🇶🇦', 'switzerland': '🇨🇭', 'brazil': '🇧🇷', 'haiti': '🇭🇹',
    'scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'turkey': '🇹🇷', 'argentina': '🇦🇷', 'france': '🇫🇷',
    'germany': '🇩🇪', 'japan': '🇯🇵', 'portugal': '🇵🇹', 'netherlands': '🇳🇱',
    'curaçao': '🇨🇼', 'côte d\'ivoire': '🇨🇮', 'ecuador': '🇪🇨', 'sweden': '🇸🇪',
    'tunisia': '🇹🇳', 'cape verde': '🇨🇻', 'belgium': '🇧🇪', 'egypt': '🇪🇬',
    'saudi arabia': '🇸🇦', 'uruguay': '🇺🇾', 'iran': '🇮🇷', 'new zealand': '🇳🇿',
    'senegal': '🇸🇳', 'iraq': '🇮🇶', 'norway': '🇳🇴', 'algeria': '🇩🇿',
    'austria': '🇦🇹', 'jordan': '🇯🇴', 'dr congo': '🇨🇩', 'congo dr': '🇨🇩', 'croatia': '🇭🇷',
    'ghana': '🇬🇭', 'panama': '🇵🇦', 'uzbekistan': '🇺🇿', 'colombia': '🇨🇴',
    'italy': '🇮🇹', 'costa rica': '🇨🇷', 'jamaica': '🇯🇲', 'honduras': '🇭🇳',
    'chile': '🇨🇱', 'peru': '🇵🇪', 'venezuela': '🇻🇪', 'nigeria': '🇳🇬',
    'cameroon': '🇨🇲', 'denmark': '🇩🇰', 'poland': '🇵🇱', 'ukraine': '🇺🇦',
    'wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'serbia': '🇷🇸', 'slovenia': '🇸🇮', 'romania': '🇷🇴',
    'georgia': '🇬🇪', 'albania': '🇦🇱', 'hungary': '🇭🇺', 'slovakia': '🇸🇰',
    'china': '🇨🇳', 'vietnam': '🇻🇳', 'thailand': '🇹🇭', 'malaysia': '🇲🇾',
    'runner-up group a': '⚔️', 'runner-up group b': '⚔️',
    'winner group c': '👑', 'runner-up group c': '⚡',
    'winner group e': '👑', 'winner group f': '👑',
    'runner-up group f': '⚡', '3rd group a/b/c/d/f': '🎖️',
}

@st.dialog("🏆 ทำเนียบผู้นำคะแนนสูงสุด 🏆", width="middle")
def show_congrats_dialog(leaders_str, max_score):
    # ปล่อยลูกโป่งสีสันสดใสหรูหราลอยขึ้นมาทันทีที่เปิดป๊อปอัป
    st.balloons()
    
    st.markdown("""
        <style>
        .congrats-dialog-container {
            text-align: center;
            font-family: 'Kanit', sans-serif;
            background: radial-gradient(circle, #1a150b 0%, #0d0901 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1.5px solid #F5B82E;
            box-shadow: 0 0 25px rgba(245, 184, 46, 0.35);
            position: relative;
            overflow: hidden;
        }
        .congrats-title-dl {
            font-size: 1.5rem;
            font-weight: bold;
            color: #FFE9A2;
            text-shadow: 0 0 10px rgba(245,184,46,0.6);
            margin-bottom: 10px;
        }
        .congrats-leader-dl {
            font-size: 2.2rem;
            color: #FFFFFF;
            font-weight: bold;
            margin: 15px 0;
            text-shadow: 0 0 15px rgba(255,255,255,0.6);
        }
        .congrats-score-dl {
            font-size: 1.25rem;
            color: #FFD700;
            font-weight: bold;
            background: rgba(245, 184, 46, 0.15);
            padding: 8px 18px;
            border-radius: 30px;
            display: inline-block;
            margin-bottom: 15px;
            border: 1px solid rgba(245,184,46,0.3);
        }
        /* ซ่อนปุ่มกากบาทปิด (X) ของ Streamlit Dialog เพื่อบังคับให้กดปุ่มนำทางหลักเท่านั้น */
        button[aria-label="Close"] {
            display: none !important;
        }
        /* ห้ามคลิกนอกกรอบเพื่อปิด (Disable Click Outside to Close) */
        [data-testid="stModalBackdrop"], [data-baseweb="modal"] {
            pointer-events: none !important;
        }
        [data-testid="stDialog"], [data-testid="stModal"], [role="dialog"] {
            pointer-events: auto !important;
        }
        /* ฟิลเตอร์ป้องกันคลิกนอกกล่องระบายคลิกทั้งหมด (Click Shield) */
        .dialog-click-shield {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.01);
            z-index: -1;
            pointer-events: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
<div class="dialog-click-shield"></div>
<div class="congrats-dialog-container">
<div class="congrats-title-dl">🏆 ทำเนียบผู้นำคะแนนสูงสุด 🏆</div>
<div style="font-size: 1.05rem; color: #a0aec0;">ขอแสดงความยินดีกับผู้ที่ได้คะแนนนำลิ่วสูงสุดขณะนี้!</div>
<div class="congrats-leader-dl">🎉 {leaders_str} 🎉</div>
<div class="congrats-score-dl">👑 นำอันดับหนึ่งด้วยคะแนนสะสม: {int(max_score)} แต้ม 👑</div>
<div style="color: #FFD700; font-size: 0.95rem; font-weight: bold; margin-bottom: 20px;">🔥 ใครจะเป็นผู้มาโค่นบัลลังก์นี้ได้สำเร็จ? 🔥</div>
<!-- ยิงพลุกระดาษเฉลิมฉลอง (Canvas Confetti) ตระการตาทั่วบานหน้าต่าง -->
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
<script>
function runDialogFireworks() {{
if (window.confetti) {{
var duration = 4 * 1000;
var animationEnd = Date.now() + duration;
var defaults = {{ startVelocity: 28, spread: 360, ticks: 60, zIndex: 999999 }};
function randomInRange(min, max) {{
return Math.random() * (max - min) + min;
}}
var interval = setInterval(function() {{
var timeLeft = animationEnd - Date.now();
if (timeLeft <= 0) {{
return clearInterval(interval);
}}
var particleCount = 50 * (timeLeft / duration);
confetti(Object.assign({{}}, defaults, {{ particleCount, origin: {{ x: randomInRange(0.15, 0.35), y: Math.random() - 0.2 }} }}));
confetti(Object.assign({{}}, defaults, {{ particleCount, origin: {{ x: randomInRange(0.65, 0.85), y: Math.random() - 0.2 }} }}));
}}, 200);
}} else {{
setTimeout(runDialogFireworks, 100);
}}
}}
runDialogFireworks();
</script>
</div>
""", unsafe_allow_html=True)
    
    st.write("")
    if st.button("ลุยต่อกันเลย! ⚽🔥", key="dlg_congrats_continue_btn", use_container_width=True):
        st.session_state.show_congrats_popup = False
        st.balloons()
        # ตรวจสอบทันทีว่าทายแชมป์หรือยัง
        existing_pred = db.get_user_champion_prediction(st.session_state.username)
        if not existing_pred or st.session_state.username == "Art":
            st.session_state.show_champion_popup = True
        st.rerun()


@st.dialog("🔮 ทำนายผลแชมป์โลก 2026 🔮", width="middle")
def show_champion_dialog(username):
    st.markdown("""
        <style>
        .champ-dialog-container {
            font-family: 'Kanit', sans-serif;
            text-align: center;
            background: radial-gradient(circle, #152219 0%, #070d0a 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1.5px solid #4CAF50;
            box-shadow: 0 0 25px rgba(76, 175, 80, 0.35);
        }
        .champ-title-dl {
            font-size: 1.5rem;
            font-weight: bold;
            color: #FFE9A2;
            text-shadow: 0 0 10px rgba(245,184,46,0.6);
            margin-bottom: 10px;
        }
        .champ-desc-dl {
            font-size: 0.95rem;
            color: #a0aec0;
            margin-bottom: 20px;
            line-height: 1.45;
        }
        /* ซ่อนปุ่มกากบาทปิด (X) ของ Streamlit Dialog เพื่อบังคับให้ใช้ปุ่มของกล่องแชทอย่างเสถียร */
        button[aria-label="Close"] {
            display: none !important;
        }
        /* ห้ามคลิกนอกกรอบเพื่อปิด (Disable Click Outside to Close) */
        [data-testid="stModalBackdrop"], [data-baseweb="modal"] {
            pointer-events: none !important;
        }
        [data-testid="stDialog"], [data-testid="stModal"], [role="dialog"] {
            pointer-events: auto !important;
        }
        /* ฟิลเตอร์ป้องกันคลิกนอกกล่องระบายคลิกทั้งหมด (Click Shield) */
        .dialog-click-shield {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.01);
            z-index: -1;
            pointer-events: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="dialog-click-shield"></div>
        <div class="champ-dialog-container">
            <div class="champ-title-dl">🔮 ทำนายผลแชมป์โลก 2026 🔮</div>
            <div class="champ-desc-dl">
                โอกาสแก้ตัวสำหรับผู้ร่วมสนุกที่ไม่ทันรอบแรก! <br>
                เลือกทายผลประเทศที่จะพิชิตถ้วยฟุตบอลโลก 1 ทีมเท่านั้น และจะถูกเก็บข้อมูลไว้เป็นความลับจนกว่าจะถึงวันชิงชนะเลิศ ตัดสินใจให้ดี!
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    global IS_CHAMPION_PRED_ACTIVE
    
    TEAMS_LIST = [
        ("", "🏳️ กรุณาเลือกประเทศที่ต้องการทำนาย..."),
        ("Argentina", "🇦🇷 อาร์เจนตินา (Argentina)"),
        ("Belgium", "🇧🇪 เบลเยียม (Belgium)"),
        ("Colombia", "🇨🇴 โคลอมเบีย (Colombia)"),
        ("Egypt", "🇪🇬 อียิปต์ (Egypt)"),
        ("England", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 อังกฤษ (England)"),
        ("France", "🇫🇷 ฝรั่งเศส (France)"),
        ("Morocco", "🇲🇦 โมร็อกโก (Morocco)"),
        ("Norway", "🇳🇴 นอร์เวย์ (Norway)"),
        ("Spain", "🇪🇸 สเปน (Spain)"),
        ("Switzerland", "🇨🇭 สวิตเซอร์แลนด์ (Switzerland)")
    ]
    
    existing_pred = db.get_user_champion_prediction(username)
    default_idx = 0
    is_locked = False
    
    if existing_pred:
        is_locked = True
        for idx, (code, _) in enumerate(TEAMS_LIST):
            if code == existing_pred:
                default_idx = idx
                break
                
    # แสดงกล่องแจ้งเตือนความปลอดภัยสีทองเมื่อล็อกผลทำนายแล้ว
    if is_locked:
        st.markdown(f"""
            <div style='background-color: rgba(245, 184, 46, 0.08); border: 1.5px solid #F5B82E; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 15px;'>
                <span style='color: #FFE9A2; font-weight: bold; font-size: 0.95rem; text-shadow: 0 0 5px rgba(245,184,46,0.3);'>🔒 สิทธิ์การทำนายของคุณถูกล็อกเรียบร้อยแล้ว</span><br>
                <span style='color: #cbd5e0; font-size: 0.88rem;'>คุณเลือกทายผลแชมป์โลกคือ <b>{TEAMS_LIST[default_idx][1]}</b> และไม่สามารถแก้ไขได้อีกแล้วครับ</span>
            </div>
        """, unsafe_allow_html=True)
    elif not IS_CHAMPION_PRED_ACTIVE:
        # กรณีระบบชะลอการเปิดทำนายผลเพื่อรอจบคู่แข่งขันรอบ 16 ทีมสุดท้ายคืนนี้
        st.markdown(f"""
            <div style='background-color: rgba(245, 184, 46, 0.08); border: 1.5px solid #F5B82E; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 15px;'>
                <span style='color: #FFE9A2; font-weight: bold; font-size: 1.05rem; text-shadow: 0 0 5px rgba(245,184,46,0.3);'>⏳ เตรียมเปิดระบบทำนายผลแชมป์โลกวันพรุ่งนี้!</span><br><br>
                <span style='color: #cbd5e0; font-size: 0.92rem; line-height: 1.55;'>
                    ระบบทำนายผลแชมป์โลก 2026 จะเปิดให้ส่งผลทายอย่างเป็นทางการใน<b>วันพรุ่งนี้</b><br>
                    หลังจากแมตช์การแข่งขันรอบ 16 ทีมสุดท้ายที่เหลือในคืนนี้เตะเสร็จสมบูรณ์ เพื่อให้ได้รายชื่อทีมรอบ 8 ทีมสุดท้ายที่เที่ยงตรงและเท่าเทียมที่สุดสำหรับผู้เล่นทุกคนครับ! ⚽🔥
                </span>
            </div>
        """, unsafe_allow_html=True)
                
    team_codes = [t[0] for t in TEAMS_LIST]
    team_labels = [t[1] for t in TEAMS_LIST]
    
    if IS_CHAMPION_PRED_ACTIVE or is_locked:
        selected_label = st.selectbox(
            "เลือกประเทศแชมป์โลกในใจคุณ:", 
            team_labels, 
            index=default_idx,
            disabled=is_locked  # บล็อกการเปลี่ยนค่าเมื่อล็อกแล้ว
        )
        selected_code = team_codes[team_labels.index(selected_label)]
    
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ ปิดหน้าต่างนี้", use_container_width=True):
            st.session_state.show_champion_popup = False
            st.rerun()
    with col2:
        if is_locked:
            st.button("🔒 ยืนยันคำทำนายแล้ว", use_container_width=True, disabled=True)
        elif not IS_CHAMPION_PRED_ACTIVE:
            st.button("⏳ เตรียมเปิดเร็วๆ นี้", use_container_width=True, disabled=True)
        else:
            if st.button("💾 บันทึกคำทำนาย 🏆", use_container_width=True, type="primary"):
                if selected_code == "":
                    st.error("⚠️ กรุณาเลือกประเทศที่ต้องการทำนายก่อนกดบันทึกนะครับ!")
                else:
                    db.save_champion_prediction(username, selected_code)
                    st.cache_data.clear() # ล้างแคชทั้งหมดของแอปทันทีเพื่อบังคับอัปเดตสีกรอบต้อนรับคุณ Art คมชัดทันใจ 100%
                    st.session_state.show_champion_popup = False
                    st.toast(f"🏆 บันทึกคำทำนายแชมป์โลก: {selected_label} สำเร็จแล้ว!", icon="✅")
                    st.rerun()


@st.cache_data(ttl=1800)
def check_and_sync_scores():
    try:
        db.auto_sync_scores()
    except Exception as e:
        pass

@st.cache_data(ttl=300) # แคชข้อมูลตารางคะแนนจาก Wikipedia ไว้ 5 นาที (เพิ่มความเร็วเว็บ 100 เท่า)
def get_cached_world_cup_standings():
    return db.get_world_cup_standings()



# แผนผังแปลชื่อทีมเป็นภาษาไทยพรีเมี่ยม เพื่อความสมบูรณ์แบบของหน้าตารางคะแนนและผลทาย
TEAM_TRANSLATION_MAP = {
    'mexico': 'เม็กซิโก', 'south africa': 'แอฟริกาใต้', 'south korea': 'เกาหลีใต้', 'czech republic': 'สาธารณรัฐเช็ก',
    'canada': 'แคนาดา', 'bosnia and herzegovina': 'บอสเนียและเฮอร์เซโกวีนา', 'usa': 'สหรัฐอเมริกา', 'paraguay': 'ปารากวัย',
    'spain': 'สเปน', 'morocco': 'โมร็อกโก', 'england': 'อังกฤษ', 'australia': 'ออสเตรเลีย',
    'qatar': 'กาตาร์', 'switzerland': 'สวิตเซอร์แลนด์', 'brazil': 'บราซิล', 'haiti': 'เฮติ',
    'scotland': 'สกอตแลนด์', 'turkey': 'ตุรกี', 'argentina': 'อาร์เจนตินา', 'france': 'ฝรั่งเศส',
    'germany': 'เยอรมนี', 'japan': 'ญี่ปุ่น', 'portugal': 'โปรตุเกส', 'netherlands': 'เนเธอร์แลนด์',
    'curaçao': 'คูราเซา', 'côte d\'ivoire': 'คอตดิวัวร์', 'ecuador': 'เอกวาดอร์', 'sweden': 'สวีเดน',
    'tunisia': 'ตูนิเซีย', 'cape verde': 'เคปเวิร์ด', 'belgium': 'เบลเยียม', 'egypt': 'อียิปต์',
    'saudi arabia': 'ซาอุดีอาระเบีย', 'uruguay': 'อุรุกวัย', 'iran': 'อิหร่าน', 'new zealand': 'นิวซีแลนด์',
    'senegal': 'เซเนกัล', 'iraq': 'อิรัก', 'norway': 'นอร์เวย์', 'algeria': 'แอลจีเรีย',
    'austria': 'ออสเตรีย', 'jordan': 'จอร์แดน', 'dr congo': 'ดีอาร์ คองโก', 'congo dr': 'ดีอาร์ คองโก', 'croatia': 'โครเอเชีย',
    'ghana': 'กานา', 'panama': 'ปานามา', 'uzbekistan': 'อุซเบกิสถาน', 'colombia': 'โคลอมเบีย',
    'italy': 'อิตาลี', 'costa rica': 'คอสตาริกา', 'jamaica': 'จาเมกา', 'honduras': 'ฮอนดูรัส',
    'chile': 'ชิลี', 'peru': 'เปรู', 'venezuela': 'เวเนซุเอลา', 'nigeria': 'ไนจีเรีย',
    'cameroon': 'แคเมอรูน', 'denmark': 'เดนมาร์ก', 'poland': 'โปแลนด์', 'ukraine': 'ยูเครน',
    'wales': 'เวลส์', 'serbia': 'เซอร์เบีย', 'slovenia': 'สโลวีเนีย', 'romania': 'โรมาเนีย',
    'georgia': 'จอร์เจีย', 'albania': 'แอลเบเนีย', 'hungary': 'ฮังการี', 'slovakia': 'สโลวาเกีย',
    'china': 'จีน', 'vietnam': 'เวียดนาม', 'thailand': 'ไทย', 'malaysia': 'มาเลเซีย',
    'china pr': 'จีน', 'united states': 'สหรัฐอเมริกา',
    'runner-up group a': 'รองแชมป์กลุ่ม A', 'runner-up group b': 'รองแชมป์กลุ่ม B',
    'winner group c': 'แชมป์กลุ่ม C', 'runner-up group c': 'รองแชมป์กลุ่ม C',
    'winner group e': 'แชมป์กลุ่ม E', 'winner group f': 'แชมป์กลุ่ม F',
    'runner-up group f': 'รองแชมป์กลุ่ม F', '3rd group a/b/c/d/f': 'อันดับ 3 กลุ่ม A/B/C/D/F'
}

def get_team_display(team_name, show_flag=True):
    clean_name = team_name.strip()
    alias_map = {
        'cabo verde': 'cape verde',
        'czechia': 'czech republic',
        'türkiye': 'turkey',
        'ir iran': 'iran',
        'ivory coast': 'côte d\'ivoire',
        'korea republic': 'south korea',
        'united states': 'usa',
        'china pr': 'china',
        'congo dr': 'dr congo'
    }
    lookup_name = clean_name.lower()
    if lookup_name in alias_map:
        lookup_name = alias_map[lookup_name]
        
    flag = FLAG_MAP.get(lookup_name, '🏳️')
    thai_name = TEAM_TRANSLATION_MAP.get(lookup_name, clean_name)
    
    if show_flag:
        # แสดงผลเป็น "ธงชาติ ชื่อภาษาไทย" (เช่น 🇩🇪 เยอรมนี) เพื่อความสมมาตร พรีเมี่ยม และเหมาะสมกับทุกพื้นที่แสดงผล
        return f"{flag} {thai_name}"
    return thai_name

def generate_gold_match_card(row):
    home = row['home_team']
    away = row['away_team']
    
    home_disp = get_team_display(home)
    away_disp = get_team_display(away)
    
    h_parts = home_disp.split(" ", 1)
    a_parts = away_disp.split(" ", 1)
    
    h_flag = h_parts[0] if len(h_parts) > 0 else "🏳️"
    h_name = h_parts[1] if len(h_parts) > 1 else home
    
    a_flag = a_parts[0] if len(a_parts) > 0 else "🏳️"
    a_name = a_parts[1] if len(a_parts) > 1 else away
    
    h_score = safe_int(row['home_score'])
    a_score = safe_int(row['away_score'])
    
    h_winner_badge = ""
    a_winner_badge = ""
    if h_score > a_score:
        h_winner_badge = '<span class="team-winner-badge">👑 WINNER</span>'
    elif a_score > h_score:
        a_winner_badge = '<span class="team-winner-badge">👑 WINNER</span>'
        
    scorers_html = ""
    if row['scorers'] and row['scorers'].strip() != "":
        scorers_list = [s.strip() for s in row['scorers'].split(',')]
        items = []
        for s in scorers_list:
            text = s
            time_badge = ""
            if "(" in s and ")" in s:
                start_idx = s.find("(")
                end_idx = s.find(")")
                name_part = s[:start_idx].strip()
                time_part = s[start_idx+1:end_idx].strip()
                text = name_part
                time_badge = f' <span class="scorer-time-gold">({time_part})</span>'
            
            items.append(f'<li class="scorer-item-gold"><span class="scorer-icon-gold">⚽✨</span><span>{text}{time_badge}</span></li>')
        
        scorers_html = f'<div class="scorers-container-gold"><div class="scorers-title-gold">⚽ รายชื่อผู้ทำประตู</div><ul class="scorers-list-gold">{"".join(items)}</ul></div>'
    else:
        scorers_html = '<div class="scorers-container-gold"><div class="scorers-title-gold">⚽ รายชื่อผู้ทำประตู</div><div style="font-size: 0.85rem; color: #718096; font-style: italic;">ไม่มีรายงานผู้ทำประตู</div></div>'
        
    match_time_str = pd.to_datetime(row['match_time']).strftime('%H:%M น.')
    
    card_html = (
        f'<div class="gold-match-card">'
        f'<div class="match-card-grid">'
        f'<div class="team-side">'
        f'<span class="team-flag-gold">{h_flag}</span>'
        f'<span class="team-name-gold">{h_name}</span>'
        f'{h_winner_badge}'
        f'</div>'
        f'<div>'
        f'<div class="score-gold">{h_score} - {a_score}</div>'
        f'<div class="match-time-gold">⏱️ {match_time_str}</div>'
        f'</div>'
        f'<div class="team-side">'
        f'<span class="team-flag-gold">{a_flag}</span>'
        f'<span class="team-name-gold">{a_name}</span>'
        f'{a_winner_badge}'
        f'</div>'
        f'</div>'
        f'{scorers_html}'
        f'</div>'
    )
    return card_html

# เริ่มต้นฐานข้อมูล
db.init_db()

bg_opacity_val = 0.67
bg_opacity_bottom = 0.70

# --- SVG Filter สำหรับทำเอฟเฟกต์ธงสะบัดช้าๆ (Slow Flag Waving/Ripple Effect) ---
st.markdown("""
<svg style="position: fixed; width: 0; height: 0; pointer-events: none;">
  <filter id="slow-waving-filter" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.015 0.05" numOctaves="2" result="turbulence">
      <animate attributeName="baseFrequency" 
               values="0.015 0.05; 0.015 0.07; 0.015 0.05" 
               dur="18s" 
               repeatCount="indefinite" />
    </feTurbulence>
    <feDisplacementMap in="SourceGraphic" in2="turbulence" scale="12" xChannelSelector="R" yChannelSelector="G" />
  </filter>
</svg>
""", unsafe_allow_html=True)

# --- CSS ส่วนหัวและแอนิเมชัน ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Kanit', sans-serif;
    }}
    
    /* ปรับแต่ง Sidebar ให้ดูพรีเมี่ยม โทนเขียวตุ่น และบังคับให้ทำ GPU Composite Layer ป้องกันบั๊กภาพเบลอลามจากจอหลัก */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #2d3a31 0%, #1a241e 100%);
        position: relative;
        overflow: hidden !important; /* ล็อกความสูงเพื่อคลิปแสงและถ้วยไม่ให้ทะลุออก */
        border-right: none;
        box-shadow: 2px 0 15px rgba(0,0,0,0.3);
        height: 100vh !important;
        transform: translateZ(0) !important;
        -webkit-transform: translateZ(0) !important;
        backface-visibility: hidden !important;
        -webkit-backface-visibility: hidden !important;
    }}
    
    [data-testid="stSidebarContent"] {{
        overflow-y: auto !important; /* ย้ายสกรอลล์มาไว้ที่เนื้อหาหลัก เพื่อไม่ให้โดนเอฟเฟกต์เบียดบัง */
        height: 100% !important;
        max-height: 100vh !important;
    }}

    [data-testid="stSidebarUserContent"] {{
        overflow-y: visible !important;
        max-height: none !important;
    }}

    
    /* เลเยอร์เส้นแสงสะท้อนพาดผ่าน (Premium Soft Light Sweep) - แก้ไขให้วิ่งทะลุไม่ค้างที่ขอบ */
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: -50%; /* ขยายพื้นที่ด้านบนเพื่อให้คลุมแนวเฉียง */
        left: 0;
        width: 400px; /* เพิ่มความกว้างแสง */
        height: 200%;
        background: linear-gradient(
            to right, 
            rgba(255, 255, 255, 0) 0%, 
            rgba(255, 255, 255, 0.15) 50%, 
            rgba(255, 255, 255, 0) 100%
        );
        transform: translateX(-150%) rotate(-45deg); /* เริ่มต้นนอกจอ */
        filter: blur(40px);
        mix-blend-mode: soft-light;
        animation: light-sweep 6s infinite ease-in-out;
        pointer-events: none;
        z-index: -1;
    }}

    @keyframes light-sweep {{
        0% {{ transform: translateX(-200%) rotate(-45deg); }}
        30% {{ transform: translateX(400%) rotate(-45deg); }} /* วิ่งทะลุออกไปไกลๆ */
        100% {{ transform: translateX(400%) rotate(-45deg); }}
    }}

    /* เลเยอร์พื้นหลัง Sidebar: ลายถ้วยบอลโลกพร้อมเอฟเฟกต์สะบัดช้าๆ */
    [data-testid="stSidebar"]::after {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/png;base64,{bg_sidebar_base64}");
        background-repeat: no-repeat;
        background-size: cover;
        background-position: center;
        opacity: 0.22;
        filter: grayscale(100%) contrast(110%) brightness(85%) url(#slow-waving-filter); /* ใช้ SVG Filter เพื่อทำเอฟเฟกต์สะบัด */
        pointer-events: none;
        z-index: -2; /* ล็อคไว้หลังสุดไม่ให้รบกวนเมนู */
        transform: scale(1.1); /* ขยายเผื่อขอบจากการบิดเบี้ยวของ Filter */
    }}

    /* ระบายสีข้อความเฉพาะจุดอย่างถูกต้องเพื่อไม่ให้ชนโครงสร้าง z-index */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: #e2e8f0 !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {{
        color: #ffffff !important;
    }}
    
    /* 🌟 ปรับแต่งคอนเทนเนอร์ stRadio นอกสุดให้กว้างเต็ม 100% ของไซด์บาร์อย่างแท้จริง แก้ปัญหากล่องหดตัวปุ่มโดนบีบแคบ */
    div[data-testid="stRadio"], .stRadio {{
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    /* ปรับแต่งปุ่มเมนูหลักของไซด์บาร์ให้กรอบกว้างและแผ่ขนาดเท่ากันเป๊ะเสมอกันทุกปุ่ม 100% */
    div[role="radiogroup"] {{
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    div[role="radiogroup"] > label {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #c0c0c066; /* ขอบเงินโครเมี่ยมจางๆ */
        padding: 10px 14px !important; /* คืนค่า padding ปกติเพื่อให้วงกลมตัวเลือกอยู่ในพิกัดธรรมชาติอย่างสมมาตร */
        border-radius: 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
        cursor: pointer !important;
        width: 100% !important; /* บังคับให้ขนาดกรอบขยายตัวสมมาตรเท่ากันทั้งหมด */
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important; /* จัดให้อยู่กึ่งกลางแนวตั้ง */
        position: relative !important;
    }}
    div[role="radiogroup"] > label:hover {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important; /* ขัดขอบเงินให้ชัดขึ้นเมื่อ hover */
        box-shadow: 0 2px 10px rgba(255, 255, 255, 0.05) !important;
    }}
    div[role="radiogroup"] > label[data-selected="true"] {{
        background: linear-gradient(90deg, #5c7a67 0%, #3d5244 100%) !important;
        border: 1.5px solid #ffffff !important; /* ขอบสีขาวสว่างแบบโครเมี่ยมสะท้อนแสง */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }}
    div[role="radiogroup"] > label[data-selected="true"] span {{
        color: #ffffff !important;
        font-weight: 600;
    }}

    /* 🎯 สเปรชพื้นที่เว้นระยะห่างระหว่างเมนูกลุ่มที่ 1 และกลุ่มที่ 2 พร้อมติดป้ายหมวดหมู่แบบหรูหรา */
    div[role="radiogroup"] > label:nth-of-type(4) {{
        margin-top: 57px !important;
        position: relative !important;
    }}
    
    /* ลายเส้นแบ่งส่วน (Separator Line) ยกขึ้นลอยเด่นอยู่เหนือหัวข้อข้อความอย่างชัดเจน */
    div[role="radiogroup"] > label:nth-of-type(4)::before {{
        content: "";
        position: absolute;
        top: -35px !important;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, rgba(255, 215, 0, 0) 0%, rgba(255, 215, 0, 0.25) 50%, rgba(255, 215, 0, 0) 100%);
    }}

    /* ติดป้ายบอกประเภทหมวดหมู่ (Section Label) แขวนไว้ด้านล่างเส้น */
    div[role="radiogroup"] > label:nth-of-type(4)::after {{
        content: "📁 บัญชีผู้ใช้ & สรุปคะแนนสะสม" !important;
        position: absolute;
        top: -26px !important;
        left: 8px;
        font-size: 0.68rem;
        color: rgba(255, 215, 0, 0.55);
        font-weight: 600;
        letter-spacing: 0.8px;
        font-family: 'Kanit', sans-serif;
    }}

    /* 🌟 จัดวาง stMarkdownContainer ให้อยู่ถัดจากวงกลมตัวเลือกวิทยุตามธรรมชาติ และเว้นระยะห่างด้านซ้ายไว้สำหรับวางไอคอนทอง (เฉพาะใน Sidebar) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] {{
        position: relative !important;
        padding-left: 28px !important; /* เว้นที่ว่าง 28px ถัดจากวงกลมสำหรับวางไอคอนทอง */
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    /* 🌟 ยกเลิกการเยื้องติดลบและเปิด overflow ให้แสดงตัวหนังสือทั้งหมดได้ครบถ้วนโดยไม่มีการบดบัง (เฉพาะใน Sidebar) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {{
        text-indent: 0 !important; /* คืนค่าปกติเพื่อไม่ให้ตัวหนังสือแรกโดนดึงไปบังหรือตัดหาย */
        padding-left: 0.15rem !important; /* เว้นช่องไฟนิดหน่อยให้ตัวหนังสือข้อความถัดออกมาอย่างพรีเมี่ยม */
        margin: 0 !important;
        position: relative !important;
        overflow: visible !important; /* เปิดการแสดงผลแบบ visible เพื่อความสมบูรณ์แบบของตัวอักษร */
        display: inline-block !important;
        white-space: normal !important; /* ยอมให้ข้อความหักขึ้นบรรทัดใหม่ได้เมื่อพื้นที่ไม่พอ ป้องกันกินกรอบ */
        word-break: break-word !important; /* หักพยางค์ของข้อความยาวๆ */
        font-size: 0.8rem !important; /* ขนาดฟอนต์กะทัดรัด บาลานซ์ลงตัว */
        font-family: 'Kanit', sans-serif !important;
        line-height: 1.35 !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    /* 🌟 เคลียร์สไตล์ในแท็ก span ที่อยู่ข้างใน เพื่อยกเลิกการดันเยื้องซ้ำซ้อน ช่วยให้ข้อความดั้งเดิมแสดงผลปกติ 100% (เฉพาะใน Sidebar) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] span {{
        text-indent: 0 !important; /* ยกเลิกการเยื้องซ้ำซ้อนเด็ดขาด ช่วยแก้ปัญหาคำด้านหน้าโดนบัง */
        padding-left: 0 !important;
        margin: 0 !important;
        position: relative !important;
        overflow: visible !important;
        display: inline !important; /* ให้ไหลตามแนวข้อความปกติ */
        white-space: normal !important;
    }}

    /* วางไอคอนสีทองพิกัดคงที่ สวยงาม คมชัด ไม่มีฟุ้ง โดยอิงกับ stMarkdownContainer::before เพื่อให้อยู่หลังวงกลมเสมอ (เฉพาะใน Sidebar) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"]::before {{
        content: "" !important;
        position: absolute !important;
        left: 2px !important; /* วางพิกัดถัดจากวงกลมวิทยุพอดีเป๊ะ */
        top: 50% !important;
        transform: translateY(-50%) !important;
        width: 18px !important;
        height: 18px !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        filter: none !important; /* ไม่มีฟุ้งเรืองแสงตามสั่ง คมชัดเหลืองอร่ามพรีเมี่ยม */
        z-index: 5 !important;
    }}

    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z'/%3E%3C/svg%3E") !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M16 11V3H8v6H2v12h20V11h-6zM10 5h4v14h-4V5zM4 11h4v8H4v-8zm16 8h-4v-8h4v8z'/%3E%3C/svg%3E") !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'/%3E%3C/svg%3E") !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M2 4l3 12h14l3-12-6 7-4-7-6 7-4-7z'/%3E%3Ccircle fill='%23F1C40F' cx='12' cy='17' r='2'/%3E%3C/svg%3E") !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(6) [data-testid="stMarkdownContainer"]::before {{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23F1C40F' d='M12.19 2.02c-5.52 0-10 4.48-10 10s4.48 10 10 10 10-4.48 10-10-4.48-10-10-10zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z'/%3E%3C/svg%3E") !important;
    }}

    /* ปรับแต่งช่องกรอกคะแนน (st.number_input) ให้ดูโมเดิร์นคลีนและมีมิติ */
    div[data-testid="stNumberInput"] {{
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 5px 8px !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stNumberInput"]:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }}
    /* ปรับตัวอักษร Label ของช่องกรอกข้อมูลให้ดูมีระเบียบและไม่รกรุงรัง */
    div[data-testid="stNumberInput"] label p {{
        font-size: 0.9rem !important;
        color: #a0aec0 !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
    }}

    /* สไตล์ส่วนหัวพรีเมี่ยมแบบโปร่งใส ไร้รอยต่อ */
    .premium-header {{
        position: relative;
        width: 100%;
        max-width: 1200px;
        height: 250px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        background: transparent;
        border: none;
        box-shadow: none;
        margin-top: -35px;
        margin-bottom: 5px;
        z-index: 10;
        overflow: visible;
    }}

    .title-wrapper {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 950px;
        padding: 0 30px;
        z-index: 2;
    }}

    /* รูปภาพแบนเนอร์ เครซีเว็ป.png กรองพื้นดำมองทะลุ 100% */
    .crazyweb-img {{
        width: 100%;
        height: auto;
        max-height: 210px;
        object-fit: contain;
        mix-blend-mode: screen;
        animation: imageGlowMutedPulse 3.5s ease-in-out infinite alternate;
        will-change: filter, transform;
    }}

    /* แอนิเมชันกระเพื่อมเรืองแสงออร่านีออนสีฟ้าสวยงามชัดเจนระดับกำลังดี (4px ถึง 8px) ไม่บวมหนา */
    @keyframes imageGlowMutedPulse {{
        0% {{
            filter: drop-shadow(0 0 4px rgba(58, 226, 255, 0.35));
            transform: scale(1);
        }}
        100% {{
            filter: drop-shadow(0 0 8px rgba(58, 226, 255, 0.55));
            transform: scale(1.006);
        }}
    }}

    /* แผงมาร์กพิกเซลกาวเป้าถ้วยรางวัลทองคำของคุณอาร์ต */
    .trophy-target-overlay {{
        position: absolute;
        right: 12.9%; /* พิกัดขวาทองคำเป๊ะๆ โดยคุณอาร์ต (ปรับจาก 10.2% กลับสู่สัดส่วนทองคำ) */
        top: 17.0%;    /* พิกัดบนทองคำเป๊ะๆ โดยคุณอาร์ต */
        width: 40px;
        height: 40px;
        pointer-events: none;
        z-index: 12;
        display: flex;
        justify-content: center;
        align-items: center;
        border: none;
        box-shadow: none;
    }}

    /* วงกลมออร่าแสงสีฟ้านีออนชีพจรเต้นเบื้องหลังถ้วยในรูป */
    .trophy-target-overlay::before {{
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(58, 226, 255, 0.55) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: -1;
        filter: blur(10px);
        animation: trophyGlowPulse 3.5s ease-in-out infinite alternate;
        will-change: transform, opacity;
    }}

    @keyframes trophyGlowPulse {{
        0% {{
            transform: scale(0.85);
            opacity: 0.55;
        }}
        100% {{
            transform: scale(1.18);
            opacity: 1.0;
        }}
    }}

    .animated-ball-x {{
        position: absolute;
        width: 38px;
        height: 38px;
        top: 1px;
        left: 1px;
        z-index: 15;
        animation: goal-x 4s infinite;
        will-change: transform;
    }}
    .animated-ball-y {{
        animation: goal-y 4s infinite;
        will-change: transform;
    }}
    .animated-ball {{
        display: inline-block;
        width: 38px;
        height: 38px;
        object-fit: contain;
        animation: goal-ball 4s infinite;
        will-change: transform;
        filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.95)) drop-shadow(0 0 15px rgba(255, 255, 255, 0.7));
    }}
.firework-particle {{
    position: absolute;
    width: 5px;
    height: 5px;
    background: #FFD700;
    border-radius: 50%;
    opacity: 0;
    z-index: 5;
    pointer-events: none;
    top: 10px; 
}}
.white-p {{ background: #FFFFFF; width: 3px; height: 3px; }}

.p1 {{ animation: burst 4s infinite; --tx: -120px; --ty: -150px; }}
.p2 {{ animation: burst 4s infinite; --tx: 120px; --ty: -150px; animation-delay: 0.03s; }}
.p3 {{ animation: burst 4s infinite; --tx: -60px; --ty: -200px; animation-delay: 0.01s; }}
.p4 {{ animation: burst 4s infinite; --tx: 60px; --ty: -200px; animation-delay: 0.04s; }}
.p5 {{ animation: burst 4s infinite; --tx: 0px; --ty: -230px; }}
.p6 {{ animation: burst 4s infinite; --tx: -180px; --ty: -80px; animation-delay: 0.05s; }}
.p7 {{ animation: burst 4s infinite; --tx: 180px; --ty: -80px; animation-delay: 0.07s; }}

@keyframes burst {{
    0%, 34% {{ transform: translate3d(0, 0, 0) scale(1); opacity: 0; }}
    35% {{ opacity: 1; }}
    45% {{ transform: translate3d(var(--tx), var(--ty), 0) scale(0.8); opacity: 0.9; }}
    55% {{ transform: translate3d(calc(var(--tx) * 1.2), calc(var(--ty) * 1.2), 0) scale(0.1); opacity: 0; }}
    100% {{ opacity: 0; }}
}}

@keyframes goal-x {{
    0% {{ transform: translateX(-780px); }}
    3% {{ transform: translateX(-710px); }}
    10% {{ transform: translateX(-420px); }}
    18% {{ transform: translateX(-310px); }}
    26% {{ transform: translateX(-200px); }}
    32% {{ transform: translateX(-80px); }}
    35% {{ transform: translateX(0px); }}
    40% {{ transform: translateX(0px); }}
    100% {{ transform: translateX(0px); }}
}}

@keyframes goal-y {{
    0% {{ transform: translateY(120px); }}
    18% {{ transform: translateY(-120px); }}
    35% {{ transform: translateY(0px); }}
    40% {{ transform: translateY(0px); }}
    100% {{ transform: translateY(0px); }}
}}

@keyframes goal-ball {{
    0% {{ transform: rotate(0deg) scale(2.8); opacity: 0; }}
    3% {{ opacity: 1; }}
    18% {{ transform: rotate(270deg) scale(1.5); }}
    35% {{ transform: rotate(540deg) scale(0.7); opacity: 1; }}
    38% {{ transform: rotate(560deg) scale(0.1); opacity: 0; }}
    40% {{ transform: rotate(560deg) scale(0); opacity: 0; }}
    100% {{ transform: rotate(560deg) scale(0); opacity: 0; }}
}}

@keyframes bounce {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-8px); }}
}}
.bouncing-icon {{
    display: inline-block;
    animation: bounce 1.5s infinite ease-in-out;
    margin-right: 8px;
}}

.ufo-flyer-lg {{
    position: fixed;
    font-size: 1.6rem;
    z-index: 99999;
    top: 65px;
    pointer-events: none;
    animation: ufo-flight-lg 15s linear infinite;
    will-change: transform;
    filter: drop-shadow(0 0 6px rgba(0, 255, 255, 0.9)) drop-shadow(0 0 15px rgba(0, 191, 255, 0.6));
}}

.ufo-flyer-sm {{
    position: fixed;
    font-size: 0.9rem;
    z-index: 99998;
    top: 35px;
    pointer-events: none;
    animation: ufo-flight-sm 22s linear infinite;
    animation-delay: 6s;
    will-change: transform;
    filter: drop-shadow(0 0 4px rgba(223, 0, 254, 0.9)) drop-shadow(0 0 10px rgba(128, 0, 128, 0.6));
}}

.ufo-flyer-mid {{
    position: fixed;
    font-size: 2.2rem; /* ลำใหญ่เด่นๆ */
    z-index: 99999;
    top: 120px; /* วิ่งระดับต่ำลงมาช่วงกลางเว็บ */
    pointer-events: none;
    animation: ufo-flight-mid 12s linear infinite;
    animation-delay: 3s; /* ปล่อยคนละช่วงเวลา */
    will-change: transform;
    filter: drop-shadow(0 0 8px rgba(0, 255, 0, 1)) drop-shadow(0 0 20px rgba(50, 205, 50, 0.7)); /* ออร่าสีเขียวเรืองแสงเด่นๆ */
}}

.pizza-flyer {{
    position: fixed;
    width: 65px;
    height: 65px;
    z-index: 99999;
    top: 95px; /* ความสูงระดับกลางๆ กำลังพอดี */
    pointer-events: none;
    animation: pizza-flight 18s linear infinite;
    animation-delay: 1.5s; /* หลบหลีกจานบินอื่นๆ ไม่ให้ทับซ้อนกัน */
    will-change: transform;
    filter: drop-shadow(0 0 8px rgba(255, 102, 0, 1)) drop-shadow(0 0 20px rgba(255, 69, 0, 0.7)); /* ออร่าสีส้มไฟเตาถ่านร้อนๆ ของแบรนด์ VOILA_PIZZA */
}}

@keyframes ufo-flight-lg {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    25% {{
        transform: translate3d(60vw, -15px, 0);
    }}
    50% {{
        transform: translate3d(0vw, 15px, 0);
    }}
    75% {{
        transform: translate3d(-60vw, -10px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes ufo-flight-sm {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    30% {{
        transform: translate3d(50vw, 10px, 0);
    }}
    60% {{
        transform: translate3d(-20vw, -15px, 0);
    }}
    85% {{
        transform: translate3d(-80vw, 5px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes ufo-flight-mid {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    25% {{
        transform: translate3d(60vw, 30px, 0);
    }}
    50% {{
        transform: translate3d(0vw, -30px, 0);
    }}
    75% {{
        transform: translate3d(-60vw, 20px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}

@keyframes pizza-flight {{
    0% {{
        transform: translate3d(120vw, 0px, 0);
    }}
    20% {{
        transform: translate3d(80vw, -20px, 0);
    }}
    40% {{
        transform: translate3d(40vw, 15px, 0);
    }}
    60% {{
        transform: translate3d(0vw, -15px, 0);
    }}
    80% {{
        transform: translate3d(-50vw, 20px, 0);
    }}
    100% {{
        transform: translate3d(-120vw, 0px, 0);
    }}
}}


/* แต่งปุ่มแบบ Primary (บันทึกแล้ว) ให้แสดงผลเป็นสีเขียวพรีเมี่ยมสวยสะดุดตา */
button[data-testid="baseButton-primary"] {{
    background: linear-gradient(90deg, #2e7d32 0%, #1b5e20 100%) !important;
    color: #ffffff !important;
    border: 1px solid #4caf50 !important;
    box-shadow: 0 4px 10px rgba(46, 125, 50, 0.4) !important;
    font-weight: bold !important;
}}
button[data-testid="baseButton-primary"]:hover {{
    background: linear-gradient(90deg, #388e3c 0%, #2e7d32 100%) !important;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.6) !important;
}}

/* ระบบพื้นหลัง UFO เวอร์ชั่นย้อนกลับ (Step -3) - แก้ไขชิดขอบบนและขยายใหญ่ */
[data-testid="stAppViewContainer"] {{
    background-image: linear-gradient(to bottom, rgba(4, 6, 5, {bg_opacity_val}) 0%, rgba(3, 5, 4, {bg_opacity_bottom}) 100%), url('data:image/webp;base64,{ufo_base64}');
    background-repeat: no-repeat;
    background-position: center 0px; /* บังคับชิดขอบบนสุด */
    background-attachment: fixed;
    background-size: 160vw auto; /* ขยายให้ใหญ่ขึ้นอีกและคุมความกว้าง */
    position: relative;
}}
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background-color: rgba(4, 6, 5, {bg_opacity_val}); /* ปรับระดับความมืดของอวกาศแบบไดนามิกเพื่อขับเน้นให้แบนเนอร์และถ้วยรางวัลเด่นชัดสะดุดตาสุดๆ */
    z-index: -1;
}}
[data-testid="stAppViewContainer"] > section:nth-child(2) {{
    background-color: transparent !important;
}}

/* ซ่อนแถบเครื่องมือพัฒนาของ Streamlit ทั้งหมดทางขวา (Share, Star, Edit, Deploy, Menu) */
[data-testid="stHeaderActionElements"] {{display:none !important;}}
.stAppDeployButton {{display:none !important;}}
[data-testid="stHeaderActionButton"] {{display:none !important;}}
#MainMenu {{display:none !important;}}
footer {{visibility: hidden;}}
[data-testid="stHeader"] {{
    background-color: transparent !important;
    box-shadow: none !important;
}}

/* รองรับการแสดงผลบนโทรศัพท์มือถือ (Mobile Responsive) */
@media (max-width: 768px) {{
    .main-title {{
        font-size: 2.0rem !important;
    }}
    .header-wrapper {{
        height: 120px !important;
    }}
    .trophy-wrapper {{
        font-size: 2.0rem !important;
        margin-left: 10px !important;
    }}
    [data-testid="stAppViewContainer"] {{
        background-size: cover !important;
        background-position: center top !important;
    }}
    /* ดันช่องกรอกข้อมูลและปุ่มให้ดูกระชับขึ้นบนหน้าจอมือถือ */
    .stNumberInput {{
        margin-bottom: 5px !important;
    }}
    /* ซ่อนช่องว่างดันปุ่มเมื่ออยู่ในจอมือถือ */
    .desktop-spacer {{
        display: none !important;
    }}
    /* ล็อก Sidebar หลักไม่ให้แสงเงาทะลุออกนอกขอบเขตด้านล่าง */
    [data-testid="stSidebar"] {{
        overflow: hidden !important;
    }}
    [data-testid="stSidebarContent"] {{
        overflow-y: auto !important;
    }}
    /* ปล่อยให้เฉพาะเนื้อหาภายใน Sidebar เลื่อนแนวตั้งได้ และจะหยุดทันทีเมื่อสุดเนื้อหา */
    [data-testid="stSidebarUserContent"] {{
        overflow-y: visible !important;
        max-height: none !important;
    }}
    /* ย่อขนาดหัวข้อล็อกอินใน Sidebar */
    [data-testid="stSidebar"] h2 {{
        font-size: 1.1rem !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }}
    /* ย่อขนาดและจัดกระชับปุ่มเลือกเมนูหลักใน Sidebar เพื่อให้เห็นครบทุกเมนูโดยไม่ต้องเลื่อน */
    div[role="radiogroup"] > label {{
        padding: 5px 10px !important; /* คืนค่าความสูงกระชับระดับโมบาย */
        margin-bottom: 4px !important;
        border-radius: 6px !important;
    }}
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] {{
        padding-left: 28px !important; /* รักษาที่ว่างสำหรับไอคอนทองบนหน้าจอเล็ก */
    }}
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {{
        font-size: 0.78rem !important;
        text-indent: 0 !important; /* คืนค่าปกติสำหรับจอขนาดเล็กเช่นกัน */
        padding-left: 0.15rem !important;
        overflow: visible !important; /* แสดงตัวหนังสือได้สมบูรณ์บนจอเล็ก */
        display: inline-block !important;
        white-space: normal !important;
    }}
    div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] span,
    div[role="radiogroup"] > label span {{
        font-size: 0.78rem !important;
        text-indent: 0 !important; /* เคลียร์การเยื้องซ้อน ช่วยให้ข้อความแสดงผลปกติ 100% */
        padding-left: 0 !important;
        overflow: visible !important;
        display: inline !important;
        white-space: normal !important;
    }}


/* 🛸 สไตล์ยานรบพิเศษสีเขียวนีออนเรืองแสงพรีเมี่ยมตามตัวอย่าง */
.ufo-battle-element {{
    position: fixed;
    top: 0;
    left: 0;
    width: 48px; /* ย่อขนาดลงตามที่คุณอาร์ตแจ้ง เพื่อไม่ให้ดูเต็มหน้าจอเกินไป */
    height: 30px;
    z-index: 1000000;
    pointer-events: none;
    filter: drop-shadow(0 0 12px #39FF14);
    transition: transform 0.05s linear;
    will-change: transform, filter;
    display: none; /* ซ่อนไว้ก่อนโดยเริ่มต้น จะแสดงเมื่อมีการสั่งโจมตีเท่านั้น */
}}
.ufo-svg-ship {{
    width: 100%;
    height: 100%;
}}
</style>

<!-- จานบินลอยจำลอง (แยกอยู่นอกโครงสร้าง Layout แบนเนอร์เพื่อความเสถียรของพิกัดถ้วยทองคำ) -->
<div class='ufo-flyer-lg'>🛸</div>
<div class='ufo-flyer-sm'>🛸</div>
<div class='ufo-flyer-mid'>🛸</div>
<div class='pizza-flyer'><img src="data:image/png;base64,{pizza_base64}" style="width:100%; height:100%; object-fit:contain;" alt="🍕"></div>

<header class="premium-header">
<div class="title-wrapper">
<!-- ภาพแบนเนอร์ เครซีเว็ป.png โหลดผ่าน Base64 โปร่งแสงพรีเมี่ยม -->
<img class="crazyweb-img" src="data:image/png;base64,{banner_base64}" alt="CRAZYFIFA 2026 Header">
<!-- จุดฉายแอนิเมชันลูกบอลทองคำตกกระทบและส่องประกายออร่าเฉพาะยอดถ้วยฝั่งขวา -->
<div class="trophy-target-overlay">
<div class='animated-ball-x'>
<div class='animated-ball-y'>
<img class='animated-ball' src="data:image/png;base64,{ball_base64}" alt="⚽">
</div>
</div>
<div class='firework-particle p1'></div>
<div class='firework-particle p2'></div>
<div class='firework-particle p3'></div>
<div class='firework-particle p4'></div>
<div class='firework-particle p5'></div>
<div class='firework-particle p6 white-p'></div>
<div class='firework-particle p7 white-p'></div>
</div>
</div>
</header>
""", unsafe_allow_html=True)

# --- ระบบปล่อย UFO พุ่งชนป้ายต้อนรับในไซด์บาร์ ได้รับการย้ายและบูรณาการไว้ใน Sidebar Sandbox โดยตรงอย่างสมบูรณ์แบบเรียบร้อยแล้ว ---


# 1. ระบบผู้ใช้งาน (Sidebar)
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'ufo_exploded_active' not in st.session_state:
    st.session_state.ufo_exploded_active = False
if 'trigger_ufo' not in st.session_state:
    st.session_state.trigger_ufo = False
if 'reset_ufo' not in st.session_state:
    st.session_state.reset_ufo = False

# ตรวจสอบการเปิดป๊อปอัปครั้งแรกในเซสชันปัจจุบัน เพื่อให้เด้งอัตโนมัติเมื่อเข้ามาดูเว็บครั้งแรกสุด
if 'popup_shown_in_session' not in st.session_state:
    st.session_state.popup_shown_in_session = True
    st.session_state.show_congrats_popup = True

st.sidebar.header("👤 เข้าสู่ระบบ")
try:
    leaderboard_df = db.get_leaderboard()
    existing_users = leaderboard_df['username'].tolist() if not leaderboard_df.empty else []
except Exception as e:
    st.sidebar.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
    existing_users = []

options = ["เลือกชื่อของคุณ...", "➕ เพิ่มผู้เล่นใหม่..."] + existing_users

default_idx = 0
if st.session_state.username in existing_users:
    default_idx = existing_users.index(st.session_state.username) + 2

selected_user = st.sidebar.selectbox("ชื่อผู้เล่น:", options, index=default_idx)

if selected_user == "➕ เพิ่มผู้เล่นใหม่...":
    new_name = st.sidebar.text_input("ระบุชื่อเล่นใหม่ (ภาษาอังกฤษ):", placeholder="เช่น Jacky")
    new_pin = st.sidebar.text_input("ตั้งรหัสผ่าน (PIN 4 หลัก):", type="password", max_chars=4)
    if new_name and new_pin:
        formatted_name = db.normalize_name(new_name)
        if st.sidebar.button("ลงทะเบียนและเข้าสู่ระบบ"):
            db.get_or_create_user(formatted_name, new_pin)
            st.session_state.username = formatted_name
            st.session_state.authenticated = True
            st.session_state.show_congrats_popup = True
            # ล้างสถานะป๊อปอัปทับซ้อน เพื่อเริ่มกระบวนการป๊อปอัปใหม่อย่างเสถียร
            for k in ['congrats_start_time', 'auto_champion_check_done', 'show_champion_popup', 'popup_shown_in_session']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
elif selected_user != "เลือกชื่อของคุณ...":
    if st.session_state.username != selected_user:
        st.session_state.authenticated = False
        # ล้างสถานะป๊อปอัปทั้งหมดเพื่อเริ่มต้นใหม่อย่างสดใสสำหรับผู้เล่นคนใหม่
        for k in ['show_congrats_popup', 'congrats_start_time', 'auto_champion_check_done', 'show_champion_popup', 'popup_shown_in_session']:
            if k in st.session_state:
                del st.session_state[k]
    if not st.session_state.authenticated:
        if not db.has_pin(selected_user):
            st.sidebar.warning(f"⚠️ ยังไม่ได้ตั้งรหัส PIN สำหรับ {selected_user}")
            set_pin = st.sidebar.text_input("ตั้งรหัส PIN (4 หลัก):", type="password", max_chars=4)
            if st.sidebar.button("ตั้งรหัสและเข้าสู่ระบบ"):
                if set_pin:
                    db.get_or_create_user(selected_user, set_pin)
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.session_state.toast_shown = False
                    st.session_state.show_congrats_popup = True
                    # ล้างสถานะป๊อปอัปทับซ้อน เพื่อเริ่มกระบวนการป๊อปอัปใหม่อย่างเสถียร
                    for k in ['congrats_start_time', 'auto_champion_check_done', 'show_champion_popup', 'popup_shown_in_session']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()
        else:
            pin_input = st.sidebar.text_input(f"ใส่รหัส PIN ({selected_user}):", type="password", max_chars=4)
            if st.sidebar.button("ยืนยันตัวตน"):
                if db.verify_user(selected_user, pin_input):
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.session_state.toast_shown = False
                    st.session_state.show_congrats_popup = True
                    # ล้างสถานะป๊อปอัปทับซ้อน เพื่อเริ่มกระบวนการป๊อปอัปใหม่อย่างเสถียร
                    for k in ['congrats_start_time', 'auto_champion_check_done', 'show_champion_popup', 'popup_shown_in_session']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()
                else:
                    st.sidebar.error("❌ PIN ไม่ถูกต้อง")
    else:
        st.session_state.username = selected_user
        
        # --- ระบบดึงธีมต้อนรับตามประเทศแชมป์โลกที่คุณอาร์ตทาย (ใส่กิมมิกธงชาติและ Gradient ธงชาติหลังกล่องต้อนรับคุณ Art) ---
        predicted_team = db.get_user_champion_prediction(st.session_state.username)
        TEAM_THEMES = {
            "Argentina": {
                "background": "linear-gradient(135deg, rgba(117, 170, 219, 0.55) 0%, rgba(255, 255, 255, 0.38) 50%, rgba(117, 170, 219, 0.55) 100%)",
                "border": "1px solid rgba(117, 170, 219, 0.9)",
                "emoji": "🇦🇷",
                "text_color": "#FFFFFF"
            },
            "Brazil": {
                "background": "linear-gradient(135deg, rgba(0, 155, 58, 0.5) 0%, rgba(254, 223, 0, 0.35) 50%, rgba(0, 155, 58, 0.5) 100%)",
                "border": "1px solid rgba(254, 223, 0, 0.85)",
                "emoji": "🇧🇷",
                "text_color": "#FFFFFF"
            },
            "Germany": {
                "background": "linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(221, 0, 0, 0.45) 50%, rgba(255, 204, 0, 0.38) 100%)",
                "border": "1px solid rgba(255, 204, 0, 0.8)",
                "emoji": "🇩🇪",
                "text_color": "#FFFFFF"
            },
            "France": {
                "background": "linear-gradient(135deg, rgba(0, 35, 149, 0.5) 0%, rgba(255, 255, 255, 0.35) 50%, rgba(237, 41, 57, 0.5) 100%)",
                "border": "1px solid rgba(237, 41, 57, 0.85)",
                "emoji": "🇫🇷",
                "text_color": "#FFFFFF"
            },
            "Spain": {
                "background": "linear-gradient(135deg, rgba(198, 11, 30, 0.5) 0%, rgba(255, 196, 0, 0.45) 50%, rgba(198, 11, 30, 0.5) 100%)",
                "border": "1px solid rgba(255, 196, 0, 0.85)",
                "emoji": "🇪🇸",
                "text_color": "#FFFFFF"
            },
            "England": {
                "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.45) 0%, rgba(206, 17, 38, 0.45) 100%)",
                "border": "1px solid rgba(206, 17, 38, 0.85)",
                "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                "text_color": "#FFFFFF"
            },
            "Netherlands": {
                "background": "linear-gradient(135deg, rgba(255, 155, 0, 0.55) 0%, rgba(255, 255, 255, 0.3) 50%, rgba(255, 155, 0, 0.55) 100%)",
                "border": "1px solid rgba(255, 155, 0, 0.85)",
                "emoji": "🇳🇱",
                "text_color": "#FFFFFF"
            },
            "Portugal": {
                "background": "linear-gradient(135deg, rgba(4, 106, 56, 0.48) 0%, rgba(218, 41, 28, 0.48) 100%)",
                "border": "1px solid rgba(218, 41, 28, 0.85)",
                "emoji": "🇵🇹",
                "text_color": "#FFFFFF"
            },
            "Belgium": {
                "background": "linear-gradient(135deg, rgba(0, 0, 0, 0.55) 0%, rgba(255, 230, 0, 0.4) 50%, rgba(227, 6, 19, 0.4) 100%)",
                "border": "1px solid rgba(255, 230, 0, 0.8)",
                "emoji": "🇧🇪",
                "text_color": "#FFFFFF"
            },
            "Uruguay": {
                "background": "linear-gradient(135deg, rgba(91, 194, 231, 0.5) 0%, rgba(255, 255, 255, 0.35) 100%)",
                "border": "1px solid rgba(91, 194, 231, 0.85)",
                "emoji": "🇺🇾",
                "text_color": "#FFFFFF"
            },
            "Mexico": {
                "background": "linear-gradient(135deg, rgba(0, 104, 71, 0.5) 0%, rgba(255, 255, 255, 0.3) 50%, rgba(206, 17, 38, 0.5) 100%)",
                "border": "1px solid rgba(0, 104, 71, 0.85)",
                "emoji": "🇲🇽",
                "text_color": "#FFFFFF"
            },
            "Japan": {
                "background": "linear-gradient(135deg, rgba(255, 255, 255, 0.45) 0%, rgba(188, 0, 45, 0.45) 100%)",
                "border": "1px solid rgba(188, 0, 45, 0.85)",
                "emoji": "🇯🇵",
                "text_color": "#FFFFFF"
            },
            "Senegal": {
                "background": "linear-gradient(135deg, rgba(0, 133, 63, 0.45) 0%, rgba(253, 239, 66, 0.4) 50%, rgba(227, 6, 19, 0.4) 100%)",
                "border": "1px solid rgba(253, 239, 66, 0.85)",
                "emoji": "🇸🇳",
                "text_color": "#FFFFFF"
            },
            "Morocco": {
                "background": "linear-gradient(135deg, rgba(193, 39, 45, 0.5) 0%, rgba(0, 98, 51, 0.4) 100%)",
                "border": "1px solid rgba(0, 98, 51, 0.85)",
                "emoji": "🇲🇦",
                "text_color": "#FFFFFF"
            },
            "Colombia": {
                "background": "linear-gradient(135deg, rgba(252, 209, 22, 0.5) 0%, rgba(0, 56, 147, 0.4) 50%, rgba(206, 17, 38, 0.4) 100%)",
                "border": "1px solid rgba(252, 209, 22, 0.85)",
                "emoji": "🇨🇴",
                "text_color": "#FFFFFF"
            },
            "Norway": {
                "background": "linear-gradient(135deg, rgba(239, 43, 45, 0.45) 0%, rgba(0, 32, 91, 0.45) 100%)",
                "border": "1px solid rgba(239, 43, 45, 0.85)",
                "emoji": "🇳🇴",
                "text_color": "#FFFFFF"
            }
        }
        
        # สีเขียวพาสเทลพรีเมียมคลาสสิก (กรณีที่ยังไม่ได้เริ่มทายผลแชมป์โลก) - ตรงตามสกรีนช็อต 100%
        default_theme = {
            "background": "linear-gradient(135deg, rgba(46, 125, 50, 0.48) 0%, rgba(27, 94, 32, 0.48) 100%)",
            "border": "1px solid rgba(76, 175, 80, 0.8)",
            "emoji": "⚽",
            "text_color": "#FFFFFF"
        }
        
        theme = TEAM_THEMES.get(predicted_team, default_theme)
        
        # --- ระบบตรวจสอบทีมตกรอบย้ายขึ้นมาทำงานด้านบน เพื่อป้องกันบั๊กสลับตัวแปร (NameError) ---
        is_team_eliminated = False
        if predicted_team:
            try:
                df_matches_check = db.get_matches()
                df_matches_check['id_int'] = pd.to_numeric(df_matches_check['id'], errors='coerce').fillna(0).astype(int)
                
                pred_lower = predicted_team.strip().lower()
                
                # ค้นหาว่ามีแมตช์ที่รอแข่ง (Upcoming หรืออื่นๆ ที่ยังแข่งไม่เสร็จ) ในรอบน็อกเอาต์ (id >= 68) ที่มีชื่อทีมนี้หรือไม่
                upcoming_ko = df_matches_check[
                    (df_matches_check['id_int'] >= 68) & 
                    (df_matches_check['status'] != 'Finished') & 
                    (
                        (df_matches_check['home_team'].str.strip().str.lower() == pred_lower) | 
                        (df_matches_check['away_team'].str.strip().str.lower() == pred_lower)
                    )
                ]
                
                if not upcoming_ko.empty:
                    is_team_eliminated = False
                else:
                    finished_ko = df_matches_check[
                        (df_matches_check['id_int'] >= 68) & 
                        (df_matches_check['status'] == 'Finished') & 
                        (
                            (df_matches_check['home_team'].str.strip().str.lower() == pred_lower) | 
                            (df_matches_check['away_team'].str.strip().str.lower() == pred_lower)
                        )
                    ]
                    
                    if not finished_ko.empty:
                        latest_match = finished_ko.sort_values(by='id_int', ascending=False).iloc[0]
                        w_qualify = str(latest_match.get('winner_qualify', '')).strip().lower()
                        
                        if w_qualify != "" and w_qualify != "nan" and w_qualify != pred_lower:
                            is_team_eliminated = True
            except Exception as e_check:
                print(f"Error checking team elimination status: {e_check}")

        theme = TEAM_THEMES.get(predicted_team, default_theme)
        
        # --- ระบบปล่อย UFO พุ่งถล่ม Sidebar ชนระเบิดอลังการจากยานจริงที่ลอยอยู่บนเว็บ ---
        # ตรวจสอบทริกเกอร์แอนิเมชันปล่อย UFO หรือไม่
        play_ufo_anim = False
        if st.session_state.get('trigger_ufo', False):
            play_ufo_anim = "true"
            st.session_state.trigger_ufo = False  # เคลียร์สถานะในฝั่ง Python ทันที เพื่อป้องกันไม่ให้แอนิเมชันรันซ้ำเมื่อ Rerun อื่นๆ
        else:
            play_ufo_anim = "false"
            
        ufo_exploded_active_js = "true" if st.session_state.ufo_exploded_active else "false"
        
        # สกัดเอาเฉพาะค่าสี rgba(...) จากขอบดั้งเดิมของประเทศเพื่อป้องกัน Syntax CSS ซ้ำซ้อน
        import re
        border_style = theme['border']
        border_color_match = re.search(r"rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d\.]+\s*\)", border_style)
        if border_color_match:
            border_color = border_color_match.group(0)
        else:
            border_color = "rgba(239, 43, 45, 0.85)"  # ค่า Fallback แดงสว่างนอร์เวย์
        
        # ขอบใช้สไตล์ดั้งเดิม 100% คมเข้มสว่างเรืองแสงสีประจำชาติ (เช่น สีแดงของนอร์เวย์) เด่นชัดตามต้นตำรับ
        border_style_thin = border_style
        
        # คลาสการแสดงผลและลอจิกการ์ด (ปกติ vs RIP ไว้อาลัยขาวดำ)
        welcome_class = "champion-prediction-panel"
        if st.session_state.ufo_exploded_active:
            if play_ufo_anim == "true":
                welcome_class = "champion-prediction-panel"
            else:
                welcome_class = "champion-prediction-panel rip-active"

        # ดีไซน์ป้ายสถานะของการ์ด
        if not predicted_team:
            card_border = "rgba(255, 233, 162, 0.3)"
            status_color = "#FFE9A2"
            status_bg = "rgba(255, 233, 162, 0.15)"
            status_text = "🔮 รอร่วมทำนายแชมป์"
            team_display_name = "ยังไม่ได้เลือกทีม"
            name_color = "#FFE9A2"
            flag_emoji = "⚽"
        elif is_team_eliminated:
            card_border = "rgba(239, 68, 68, 0.3)"
            status_color = "#FF4D4D"
            status_bg = "rgba(239, 68, 68, 0.15)"
            status_text = "❌ ตกรอบเรียบร้อย"
            team_display_name = f"{predicted_team}"
            name_color = "#FF6688"
            flag_emoji = theme['emoji']
        else:
            card_border = "rgba(57, 255, 20, 0.3)"
            status_color = "#39FF14"
            status_bg = "rgba(57, 255, 20, 0.15)"
            status_text = "✅ ยังอยู่ในเส้นทาง"
            team_display_name = f"{predicted_team}"
            name_color = "#39FF14"
            flag_emoji = theme['emoji']
        
        sidebar_html = f"""<style>
/* 🌟 ดีไซน์ตัวการ์ดหลัก Glassmorphism ปรับแต่งโปร่งใสทะลุหลังบางเป็นพิเศษตามต้นตำรับ */
.champion-prediction-panel {{
    background: rgba(10, 16, 35, 0.28) !important;
    backdrop-filter: blur(15px) !important;
    -webkit-backdrop-filter: blur(15px) !important;
    border: 1.5px solid {border_color} !important;
    border-radius: 20px !important;
    padding: 16px 14px !important;
    text-align: left !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35), 
                inset 0 0 15px rgba(255, 255, 255, 0.03),
                0 0 15px {border_color} !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
}}
.champion-prediction-panel::before {{
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -150% !important;
    width: 50% !important;
    height: 100% !important;
    background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0) 100%) !important;
    transform: skewX(-25deg) !important;
    transition: 0.85s !important;
}}
.champion-prediction-panel:hover::before {{
    left: 150% !important;
}}
.champion-prediction-panel:hover {{
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.45), 0 0 15px {border_color} !important;
}}

/* ลอจิกการสลับสเตตัสปกติ / RIP (ขาวดำไว้อาลัย) */
.champion-prediction-panel .welcome-rip-content {{
    display: none !important;
}}
.champion-prediction-panel .welcome-normal-content {{
    display: flex !important;
    width: 100% !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
}}

/* สไตล์ขาวดำเมื่อโดนจานบินถล่มชน */
.champion-prediction-panel.rip-active {{
    filter: grayscale(100%) contrast(0.9) brightness(0.7) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.65), inset 0 0 10px rgba(255, 255, 255, 0.02) !important;
    background: rgba(20, 20, 20, 0.08) !important;
}}
.champion-prediction-panel.rip-active .welcome-normal-content {{
    display: none !important;
}}
.champion-prediction-panel.rip-active .welcome-rip-content {{
    display: flex !important;
    width: 100% !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
}}

.welcome-card-text {{
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    text-align: left !important;
}}

.welcome-title {{
    font-size: 18px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    font-family: 'Kanit', sans-serif !important;
    letter-spacing: -0.2px !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5) !important;
}}

.welcome-sub {{
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #ffffff !important;
    opacity: 0.95 !important;
    font-family: 'Kanit', sans-serif !important;
    letter-spacing: -0.1px !important;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
}}

.welcome-card-flag {{
    font-size: 48px !important;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5)) !important;
    animation: flag-wave 3s ease-in-out infinite !important;
    display: inline-block !important;
    user-select: none !important;
    pointer-events: none !important;
    transform-origin: bottom center !important;
}}

@keyframes flag-wave {{
    0%, 100% {{
        transform: translateY(0) rotate(0deg) scale(1);
    }}
    50% {{
        transform: translateY(-3px) rotate(-5deg) scale(1.04);
    }}
}}
</style>
<div id="ufoBattleWrapper" style="position: relative; overflow: visible; width: 100%; margin-top: 10px; margin-bottom: 12px;">
<div class="{welcome_class}" id="welcomePanel">
    <!-- เนื้อหาโหมดปกติ -->
    <div class="welcome-normal-content">
        <div class="welcome-card-text">
            <div class="welcome-title">ยินดีต้อนรับคุณ {st.session_state.username}</div>
            <div class="welcome-sub">🔮 ทายแชมป์โลก: {flag_emoji} {team_display_name}</div>
        </div>
        <div class="welcome-card-flag" id="welcomeFlag">{flag_emoji}</div>
    </div>
    
    <!-- เนื้อหาโหมดไว้อาลัย RIP ขาวดำ -->
    <div class="welcome-rip-content">
        <div class="welcome-card-text">
            <div class="welcome-title" style="color: #A4B2C5 !important; text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;">⚰️ RIP {team_display_name}</div>
            <div class="welcome-sub" style="color: #8A99AD !important; text-shadow: 0 1px 2px rgba(0,0,0,0.4) !important;">
                บอร์ดส่วนทำนายผลถูกโจมตีทางอวกาศเสร็จสิ้นโดย UFO ลึกลับ! 🛸
            </div>
        </div>
        <div class="welcome-card-flag" style="filter: grayscale(100%) brightness(0.65) !important; animation: none !important;">{flag_emoji}</div>
    </div>
</div>
</div>"""
        
        st.sidebar.markdown(sidebar_html.replace('\n', ' '), unsafe_allow_html=True)
        
        # สร้าง JavaScript และ CSS ระดับ Global (พ่นด้วยสตริงธรรมดาของ Python หลีกเลี่ยง f-string formatting error)
        global_ufo_and_physics_script = """<script>
(function() {
    // 1. ตรวจสอบและดักพ่นองค์ประกอบสไตล์ระดับ Global ไปแขวนไว้ที่ Parent Document Body (Streamlit Main Area)
    var parentWin = (window.parent && window.parent.document) ? window.parent : window;
    var doc = parentWin.document;
    
    // พ่น CSS สไตล์ Global UFO และแรงระเบิดสะท้านจอ
    var styleId = 'global-ufo-style';
    if (!doc.getElementById(styleId)) {
        var styleEl = doc.createElement('style');
        styleEl.id = styleId;
        styleEl.innerHTML = `
            .global-ufo-element {
                position: fixed !important;
                width: 85px !important;
                height: 55px !important;
                z-index: 999999 !important;
                pointer-events: none !important;
                filter: drop-shadow(0 0 15px #39FF14) !important;
                transition: transform 0.05s linear !important;
                display: none;
            }
            .global-ufo-svg {
                width: 100% !important;
                height: 100% !important;
            }
            #globalExplosionCanvas {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 999998 !important;
                pointer-events: none !important;
            }
            @keyframes shake-sidebar-anim-ufo {
                0%, 100% { transform: translateX(0); }
                10% { transform: translateX(-8px) rotate(-1deg); }
                20% { transform: translateX(8px) rotate(1deg); }
                30% { transform: translateX(-6px) rotate(-0.5deg); }
                40% { transform: translateX(6px) rotate(0.5deg); }
                50% { transform: translateX(-4px); }
                60% { transform: translateX(4px); }
                70% { transform: translateX(-2px); }
            }
            .shake-sidebar-ufo {
                animation: shake-sidebar-anim-ufo 0.5s ease-in-out !important;
            }
        `;
        doc.head.appendChild(styleEl);
    }

    // สร้าง Canvas วาดประกายไฟเต็มบอร์ด
    var canvas = doc.getElementById('globalExplosionCanvas');
    if (!canvas) {
        canvas = doc.createElement('canvas');
        canvas.id = 'globalExplosionCanvas';
        doc.body.appendChild(canvas);
    }
    
    var ctx = canvas.getContext('2d');
    var particles = [];

    function resizeCanvas() {
        canvas.width = parentWin.innerWidth;
        canvas.height = parentWin.innerHeight;
    }
    parentWin.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // สะเก็ดระเบิด (Particle Class)
    class GlobalParticle {
        constructor(x, y, color) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 5 + 3;
            this.speedX = (Math.random() * 16) - 4; // พุ่งกระจายเอียงขวา
            this.speedY = (Math.random() - 0.5) * 14 - 2;
            this.gravity = 0.18;
            this.color = color;
            this.alpha = 1;
            this.decay = Math.random() * 0.012 + 0.008;
        }
        update() {
            this.x += this.speedX;
            this.speedY += this.gravity;
            this.y += this.speedY;
            this.alpha -= this.decay;
        }
        draw() {
            ctx.save();
            ctx.globalAlpha = this.alpha;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.shadowBlur = 12;
            ctx.shadowColor = this.color;
            ctx.fill();
            ctx.restore();
        }
    }

    function handleParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        for (let i = particles.length - 1; i >= 0; i--) {
            particles[i].update();
            particles[i].draw();
            if (particles[i].alpha <= 0) {
                particles.splice(i, 1);
            }
        }
        if (particles.length > 0) {
            requestAnimationFrame(handleParticles);
        }
    }

    // สร้างหรือดึงยาน UFO ตัวแม่แบบ Global เปล่งประกายตามเดโมเดี่ยว 100%
    var ufo = doc.getElementById('globalUfo');
    if (!ufo) {
        ufo = doc.createElement('div');
        ufo.id = 'globalUfo';
        ufo.className = 'global-ufo-element';
        ufo.innerHTML = `
            <svg class="global-ufo-svg" viewBox="0 0 100 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M30 42 L15 60 L85 60 L70 42 Z" fill="url(#beamGradGlobal)" opacity="0.65"/>
                <path d="M50 10 C38 10 32 18 32 26 L68 26 C68 18 62 10 50 10 Z" fill="#00FFCC" opacity="0.85"/>
                <circle cx="50" cy="20" r="4.5" fill="#39FF14"/>
                <ellipse cx="50" cy="32" rx="42" ry="12" fill="url(#metalGradGlobal)" stroke="#39FF14" stroke-width="1.8"/>
                <circle cx="22" cy="32" r="3" fill="#39FF14"/>
                <circle cx="36" cy="34" r="3" fill="#39FF14"/>
                <circle cx="50" cy="35" r="3.5" fill="#39FF14"/>
                <circle cx="64" cy="34" r="3" fill="#39FF14"/>
                <circle cx="78" cy="32" r="3" fill="#39FF14"/>
                <line x1="38" y1="44" x2="30" y2="48" stroke="#39FF14" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="62" y1="44" x2="70" y2="48" stroke="#39FF14" stroke-width="2.5" stroke-linecap="round"/>
                <defs>
                    <linearGradient id="metalGradGlobal" x1="0" y1="20" x2="100" y2="44" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#1A2035"/>
                        <stop offset="50%" stop-color="#334460"/>
                        <stop offset="100%" stop-color="#1A2035"/>
                    </linearGradient>
                    <linearGradient id="beamGradGlobal" x1="50" y1="42" x2="50" y2="60" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stop-color="#39FF14" stop-opacity="0.85"/>
                        <stop offset="100%" stop-color="#39FF14" stop-opacity="0"/>
                    </linearGradient>
                </defs>
            </svg>
        `;
        doc.body.appendChild(ufo);
    }

    // กำหนดสถานะและตำแหน่งตั้งต้นของ UFO บน Main Area ฝั่งขวา
    if (typeof parentWin.ufoState === 'undefined') {
        parentWin.ufoState = {
            x: parentWin.innerWidth - 320 - Math.random() * 200,
            y: 120 + Math.random() * (parentWin.innerHeight - 300),
            vx: (Math.random() - 0.5) * 1.8,
            vy: (Math.random() - 0.5) * 1.8,
            isCharging: false,
            isAttacking: false,
            isExploded: __EXPLODED_ACTIVE__,
            animFrame: null
        };
    } else {
        // อัปเดตสถานะระเบิดเมื่อมีการส่งค่ากู้คืนระบบหรือระเบิดสำเร็จ
        parentWin.ufoState.isExploded = __EXPLODED_ACTIVE__;
    }

    var state = parentWin.ufoState;

    // ระบบคืนชีพ UFO เมื่อผู้ใช้กด ซ่อมแซมระบบ
    if (!state.isExploded) {
        ufo.style.display = 'block';
    } else {
        ufo.style.display = 'none';
    }

    // สัญญาณทริกเกอร์แอนิเมชันโจมตีและชนข้ามฟากจากจอหลัก!
    var triggerAttack = __TRIGGER_UFO__;

    if (triggerAttack && !state.isCharging && !state.isAttacking) {
        state.isExploded = false;
        state.isCharging = true;
        ufo.style.display = 'block';

        // เอฟเฟกต์ประมวลผลระบบเสียงพรีเมียม (Web Audio API) ชาร์จเลเซอร์และสั่นสะกดวิญญาณ
        try {
            var audioCtx = new (parentWin.AudioContext || parentWin.webkitAudioContext)();
            if (audioCtx) {
                var osc1 = audioCtx.createOscillator();
                var gain1 = audioCtx.createGain();
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                osc1.type = 'sawtooth';
                osc1.frequency.setValueAtTime(80, audioCtx.currentTime);
                osc1.frequency.linearRampToValueAtTime(850, audioCtx.currentTime + 1.1);
                gain1.gain.setValueAtTime(0.01, audioCtx.currentTime);
                gain1.gain.linearRampToValueAtTime(0.18, audioCtx.currentTime + 1.1);
                osc1.start();
                osc1.stop(audioCtx.currentTime + 1.1);
            }
        } catch(e) { console.log(e); }

        // หน่วงเวลาสั่นตัวชาร์จสะสมประจุไฟฟ้าก่อนพุ่งดิ่งชน 1.1 วินาที
        setTimeout(function() {
            state.isCharging = false;
            state.isAttacking = true;
        }, 1100);
    }

    function updatePhysics() {
        if (state.isExploded) {
            ufo.style.display = 'none';
            return;
        }

        if (state.isCharging) {
            // โหมดสั่นพลาสมาสะสมพลังงาน เรืองแสงสลับสีเขียวนีออนกับสีชมพูวูบวาบ
            var shakeX = state.x + (Math.random() - 0.5) * 8;
            var shakeY = state.y + (Math.random() - 0.5) * 8;
            ufo.style.transform = `translate(${shakeX}px, ${shakeY}px) scale(1.35) rotate(${Math.sin(Date.now() / 15) * 15}deg)`;
            ufo.style.filter = `drop-shadow(0 0 30px #FF007F) drop-shadow(0 0 10px #39FF14)`;
        } 
        else if (!state.isAttacking) {
            // โหมดร่อนอิสระบน Main Area หน้าบอร์ดหลัก
            state.x += state.vx;
            state.y += state.vy;

            // ตีกรอบเขตจำกัด (ไม่ให้บินร่อนทับแถบ Sidebar 350px ฝั่งซ้าย)
            var minX = 360;
            var maxX = parentWin.innerWidth - 90;
            var minY = 40;
            var maxY = parentWin.innerHeight - 80;

            if (state.x <= minX || state.x >= maxX) {
                state.vx *= -1;
                state.x = Math.max(minX, Math.min(maxX, state.x));
            }
            if (state.y <= minY || state.y >= maxY) {
                state.vy *= -1;
                state.y = Math.max(minY, Math.min(maxY, state.y));
            }

            var angle = state.vx * 4.5;
            ufo.style.transform = `translate(${state.x}px, ${state.y}px) rotate(${angle}deg) scale(1.0)`;
            ufo.style.filter = `drop-shadow(0 0 15px #39FF14)`;
        } 
        else {
            // โหมดพุ่งโจมตีข้ามฟากดิ่งชนกล่องทำนายแชมป์ใน Sidebar!
            var welcomePanel = doc.getElementById('welcomePanel');
            var targetX = 120; // ค่าพิกัดเสมือนใจกลาง Sidebar หากหา element ไม่เจอ
            var targetY = parentWin.innerHeight / 2 - 50;

            if (welcomePanel) {
                var rect = welcomePanel.getBoundingClientRect();
                targetX = rect.left + (rect.width / 2) - 42;
                targetY = rect.top + (rect.height / 2) - 27;
            }

            var dx = targetX - state.x;
            var dy = targetY - state.y;
            var distance = Math.hypot(dx, dy);

            if (distance > 12) {
                // อัตราการเคลื่อนที่ดิ่งชนพรีเมียม มองทันสะใจ
                var speed = 10.5;
                state.x += (dx / distance) * speed;
                state.y += (dy / distance) * speed;

                var angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90;
                ufo.style.transform = `translate(${state.x}px, ${state.y}px) rotate(${angle}deg) scale(1.28)`;
            } else {
                // ชนเปรี้ยง! เกิดระเบิดวินาศสันตะโร
                state.isExploded = true;
                state.isAttacking = false;
                ufo.style.display = 'none';

                // เล่นเสียงสังเคราะห์ระเบิดกระหึ่ม
                try {
                    var audioCtx = new (parentWin.AudioContext || parentWin.webkitAudioContext)();
                    if (audioCtx) {
                        var osc2 = audioCtx.createOscillator();
                        var gain2 = audioCtx.createGain();
                        osc2.connect(gain2);
                        gain2.connect(audioCtx.destination);
                        osc2.type = 'triangle';
                        osc2.frequency.setValueAtTime(140, audioCtx.currentTime);
                        osc2.frequency.exponentialRampToValueAtTime(10, audioCtx.currentTime + 0.95);
                        gain2.gain.setValueAtTime(0.42, audioCtx.currentTime);
                        gain2.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.95);
                        osc2.start();
                        osc2.stop(audioCtx.currentTime + 0.95);
                    }
                } catch(e) {}

                // สลับสไตล์เปลี่ยนการ์ดให้กลายเป็นขาวดำ RIP ทันทีที่ชนวินาศสันตะโร!
                if (welcomePanel) {
                    welcomePanel.classList.add('shake-sidebar-ufo');
                    welcomePanel.classList.add('rip-active');
                }

                // สั่นสะเทือนแถบ Sidebar ของ Streamlit ทั้งตัวบอร์ด!
                var sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.classList.add('shake-sidebar-ufo');
                    setTimeout(function() {
                        sidebar.classList.remove('shake-sidebar-ufo');
                    }, 550);
                }

                // เสกสร้างละอองระเบิดสีสันเทศกาล 200 เม็ดฟุ้งเต็มหน้าจอหลักพ่นกระจายข้ามเขต!
                var colors = ['#39FF14', '#FF007F', '#FFE9A2', '#00FFFF', '#FFFFFF', '#FF3333'];
                for (var i = 0; i < 200; i++) {
                    var randomColor = colors[Math.floor(Math.random() * colors.length)];
                    particles.push(new GlobalParticle(targetX + 42, targetY + 27, randomColor));
                }
                handleParticles();
            }
        }

        state.animFrame = requestAnimationFrame(updatePhysics);
    }

    // รันการเคลื่อนไหวของ UFO
    if (state.animFrame) {
        cancelAnimationFrame(state.animFrame);
    }
    state.animFrame = requestAnimationFrame(updatePhysics);

})();
</script>"""
        global_ufo_and_physics_script = global_ufo_and_physics_script.replace('__EXPLODED_ACTIVE__', ufo_exploded_active_js).replace('__TRIGGER_UFO__', play_ufo_anim)
        components.html(global_ufo_and_physics_script, height=0)

        # แทรก CSS สำหรับปุ่ม Streamlit ให้เป็นสีนีออนเด่นตระการตาและมีไฮไลท์นุ่มนวล
        st.sidebar.markdown("""
            <style>
            /* ปุ่มสั่งปล่อย UFO */
            button[aria-label="💥 สั่งปล่อย UFO ล็อกเป้าพุ่งชน!"] {
                background: linear-gradient(135deg, #ff4d4d 0%, #cc0000 100%) !important;
                border: 1px solid #ff3333 !important;
                color: #ffffff !important;
                font-family: 'Kanit', sans-serif !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3) !important;
                transition: all 0.2s ease-in-out !important;
            }
            button[aria-label="💥 สั่งปล่อย UFO ล็อกเป้าพุ่งชน!"]:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 20px rgba(255, 0, 0, 0.55), 0 0 10px rgba(255, 77, 77, 0.4) !important;
                border-color: #ff6666 !important;
            }
            button[aria-label="💥 สั่งปล่อย UFO ล็อกเป้าพุ่งชน!"]:active {
                transform: translateY(1px) !important;
                box-shadow: 0 2px 8px rgba(255, 0, 0, 0.4) !important;
            }

            /* ปุ่มเก็บกู้ภัย */
            button[aria-label="🔧 ซ่อมแซมระบบและเก็บกู้ภัยไซด์บาร์"] {
                background: linear-gradient(135deg, #39FF14 0%, #17b300 100%) !important;
                border: 1px solid #39FF14 !important;
                color: #000000 !important;
                font-family: 'Kanit', sans-serif !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 12px rgba(57, 255, 20, 0.3) !important;
                transition: all 0.2s ease-in-out !important;
            }
            button[aria-label="🔧 ซ่อมแซมระบบและเก็บกู้ภัยไซด์บาร์"]:hover {
                transform: translateY(-1px) !important;
                box-shadow: 0 6px 20px rgba(57, 255, 20, 0.6), 0 0 10px rgba(57, 255, 20, 0.4) !important;
                border-color: #7cff62 !important;
            }
            button[aria-label="🔧 ซ่อมแซมระบบและเก็บกู้ภัยไซด์บาร์"]:active {
                transform: translateY(1px) !important;
                box-shadow: 0 2px 8px rgba(57, 255, 20, 0.4) !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # กล่องข้อความและระบบสั่งปล่อย UFO ปรากฏเฉพาะคนทำนายทีมที่ "ตกรอบ" แล้วเท่านั้น (กิมมิกสุดพรีเมียมระบายความหัวร้อนสะใจ!)
        if predicted_team and is_team_eliminated:
            st.sidebar.markdown(f"""
                <div style="background: rgba(255, 0, 0, 0.08); border: 1px dashed rgba(255, 0, 0, 0.35); border-radius: 8px; padding: 10px; margin-bottom: 8px; text-align: center; font-family: 'Kanit', sans-serif;">
                    <div style="font-size: 12px; color: #ff9999; line-height: 1.4;">
                        🚨 ทีม {predicted_team} ของคุณตกรอบแล้ว! สั่งปล่อยจานบิน UFO ด้านหลังพุ่งชนป้ายต้อนรับเพื่อระบายความหัวร้อนสะใจกันเถอะครับ!
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if not st.session_state.ufo_exploded_active:
                if st.sidebar.button("💥 สั่งปล่อย UFO ล็อกเป้าพุ่งชน!", use_container_width=True):
                    st.session_state.ufo_exploded_active = True
                    st.session_state.trigger_ufo = True
                    st.rerun()
            else:
                if st.sidebar.button("🔧 ซ่อมแซมระบบและเก็บกู้ภัยไซด์บาร์", use_container_width=True):
                    st.session_state.ufo_exploded_active = False
                    st.session_state.reset_ufo = True
                    st.rerun()
        
        # ปุ่มเปิดหน้าต่างทำนายผลแชมป์โลก 2026 แบบพรีเมียมสีทองสว่าง
        st.sidebar.markdown("""
            <style>
            button[aria-label="🏆 ทำนายผลแชมป์โลก 2026"] {
                background: linear-gradient(135deg, #FFE9A2 0%, #F5B82E 40%, #C48200 80%, #FFE9A2 100%) !important;
                background-size: 200% auto !important;
                border: none !important;
                color: #0E0A01 !important;
                font-family: 'Kanit', sans-serif !important;
                font-weight: 700 !important;
                box-shadow: 0 4px 15px rgba(196, 130, 0, 0.2) !important;
                transition: all 0.3s ease !important;
                margin-top: 5px !important;
                margin-bottom: 5px !important;
            }
            button[aria-label="🏆 ทำนายผลแชมป์โลก 2026"]:hover {
                transform: translateY(-1.5px) !important;
                box-shadow: 0 6px 20px rgba(196, 130, 0, 0.35), 0 0 15px rgba(245, 184, 46, 0.3) !important;
                color: #000000 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        if st.sidebar.button("🏆 ทำนายผลแชมป์โลก 2026", use_container_width=True):
            st.session_state.show_champion_popup = True
            st.rerun()
            
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.username = ""
            st.session_state.authenticated = False
            st.session_state.toast_shown = False
            # ล้างค่าเซสชันของป๊อปอัปและตัวกระตุ้นทั้งหมดเพื่อให้สลับบัญชีแล้วเด้งใหม่ได้ 100%
            for key in ['show_congrats_popup', 'congrats_start_time', 'auto_champion_check_done', 'show_champion_popup', 'hidden_champ_team', 'hidden_champ_submit', 'popup_shown_in_session']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        # ลบแถบทดสอบป๊อปอัป (Art Only) ออกตามความต้องการของคุณอาร์ต เพื่อให้แถบ Sidebar สวยงาม สะอาด และเป็นสากลสูงสุดครับ
else:
    st.info("👈 กรุณาเลือกชื่อเพื่อเริ่มเล่นครับ")
    st.stop()

if not st.session_state.authenticated:
    st.stop()

username = st.session_state.username

# --- ระบบป๊อบอัพเด้งพลุแตกเฉลิมฉลองผู้ได้คะแนนสูงสุดตรงกลางจอใหญ่เมื่อล็อกอินใหม่ (ทำงานสำหรับผู้ใช้ทุกคนเพื่อเฉลิมฉลองร่วมกัน) ---
if st.session_state.get('show_congrats_popup', False):
    try:
        leaderboard_df = db.get_leaderboard()
        if not leaderboard_df.empty:
            max_score = leaderboard_df['total_score'].max()
            if max_score > 0:
                leaders_at_top = leaderboard_df[leaderboard_df['total_score'] == max_score]['username'].tolist()
                leaders_str = " & ".join(leaders_at_top)
                show_congrats_dialog(leaders_str, max_score)
                # ปักป้ายสถานะป๊อปอัปความยินดีกำลังเรนเดอร์ในรอบนี้ เพื่อระงับป๊อปอัปแชมป์โลกชั่วคราว (ไม่ให้ซ้อนกัน)
                st.session_state.congrats_active_in_render = True
            else:
                st.session_state.show_congrats_popup = False
        else:
            st.session_state.show_congrats_popup = False
    except Exception as e:
        st.sidebar.error(f"🚨 ดีบัคป๊อปอัปทำงานล้มเหลว: {e}")
        st.session_state.show_congrats_popup = False

# --- ระบบป๊อบอัพเด้งพลุแตกเฉลิมฉลองแบบเก่า (ปิดการใช้งานเพื่อความปลอดภัย) ---
if False:
    try:
        leaderboard_df = db.get_leaderboard()
        show_congrats_rendered = False
        
        if not leaderboard_df.empty:
            max_score = leaderboard_df['total_score'].max()
            if max_score > 0:
                leaders_at_top = leaderboard_df[leaderboard_df['total_score'] == max_score]['username'].tolist()
                leaders_str = " & ".join(leaders_at_top)
                show_congrats_rendered = True
                
                with st.container():
                    # 1. พ่นกล่อง Backdrop, Modal, ปุ่มปิด HTML สำรอง และ JavaScript ดักคลิกกับ Auto-dismiss
                    # 1. พ่นกล่อง Backdrop, Modal, ปุ่มปิด HTML สำรอง และ JavaScript ดักคลิกกับ Auto-dismiss (ใช้สตริงธรรมดาแล้ว .replace() เพื่อตัดบั๊ก f-string)
                    congrats_html = """<div class='congrats-modal-backdrop'>
<div class='congrats-modal'>
<!-- ปุ่มปิดตัว X กากบาทสีทองพรีเมียมที่หาง่ายและใช้สัมผัสปิดได้เร็วบนมือถือ -->
<div class='congrats-close-x' onclick='dismissCongratsPopup()'>&times;</div>
 
<!-- เอฟเฟกต์ประกายดวงดาวลอยละล่อง -->
<div class='congrats-sparkle sp1'>✨</div>
<div class='congrats-sparkle sp2'>⭐</div>
<div class='congrats-sparkle sp3'>✨</div>
<div class='congrats-sparkle sp4'>⭐</div>
<div class='congrats-sparkle sp5'>✨</div>
 
<!-- พลุกระจายตัวฉลองชัย -->
<div class='firework-particle p1'></div>
<div class='firework-particle p2'></div>
<div class='firework-particle p3'></div>
<div class='firework-particle p4'></div>
<div class='firework-particle p5'></div>
 
<div class='congrats-title'>🏆 ทำเนียบผู้นำคะแนนสูงสุด 🏆</div>
<div style='font-size: 1.05rem; color: #a0aec0; margin-bottom: 5px; font-family: Kanit, sans-serif;'>ขอแสดงความยินดีกับผู้ที่ได้คะแนนนำลิ่วสูงสุดขณะนี้!</div>
<div class='congrats-leader'>🎉 __LEADERS_STR__ 🎉</div>
<div class='congrats-score'>👑 นำอันดับหนึ่งด้วยคะแนนสะสม: __MAX_SCORE__ แต้ม 👑</div>
<div style='color: #FFD700; font-size: 0.95rem; font-family: Kanit, sans-serif; font-weight: bold; margin-bottom: 30px; animation: heartbeat 1.5s infinite;'>🔥 ใครจะเป็นผู้มาโค่นบัลลังก์นี้ได้สำเร็จ? 🔥</div>
 
<!-- เว้นพื้นที่ว่างสำหรับวางปุ่มปิด Streamlit ที่ถูกดึงขึ้นมาทับพอดี -->
<div class='congrats-btn-placeholder'></div>
</div>
</div>
<div class='congrats-trigger-marker'></div>
 
<script>
function dismissCongratsPopup() {
    // 1. ค้นหาและทำลายฉากหลังและกล่องป๊อปอัปฝั่งเบราว์เซอร์ทันทีเพื่อปลดล็อกหน้าจอ
    var backdrop = document.querySelector('.congrats-modal-backdrop');
    if (backdrop) {
        backdrop.style.display = 'none';
        backdrop.remove();
    }
    
    // 2. สแกนหาปุ่ม Streamlit ที่มีข้อความ "ลุยต่อกันเลย!" โดยตรงเพื่อความเสถียรสูงสุด ไร้บั๊กพิกัดกล่องทับซ้อน
    var buttons = [];
    try {
        if (window.parent && window.parent.document) {
            buttons = window.parent.document.querySelectorAll('button');
        }
    } catch(e) {}
    if (!buttons || buttons.length === 0) {
        buttons = document.querySelectorAll('button');
    }
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].textContent.includes('ลุยต่อกันเลย!')) {
            buttons[i].click();
            break;
        }
    }
}
 
// ปิดอัตโนมัติเมื่อครบ 3 วินาที เพื่อให้เด้งทำงานต่อเนื่องลื่นไหลสุดยอด
setTimeout(function() {
    dismissCongratsPopup();
}, 3000);
</script>"""
                    congrats_html = congrats_html.replace("__LEADERS_STR__", leaders_str).replace("__MAX_SCORE__", str(int(max_score)))
                    st.markdown(congrats_html, unsafe_allow_html=True)
                    
                    # 2. ปุ่ม Streamlit ที่จัดวางพิกัดให้อยู่เหนือกำแพง backdrop เสมอ
                    if st.button("ลุยต่อกันเลย! ⚽🔥", key="close_popup_btn", use_container_width=True):
                        st.session_state.show_congrats_popup = False
                        
                        # หากผู้ใช้ยังไม่ได้ทายผลแชมป์โลก ให้กระตุ้นหน้าต่างทำนายแชมป์ขึ้นมาต่อทันที
                        existing_pred = db.get_user_champion_prediction(username)
                        if not existing_pred:
                            st.session_state.show_champion_popup = True
                            
                        st.rerun()
                        
                    # 3. พ่น CSS ควบคุมการเลือนหายไปเอง และยอมให้นิ้วสไลด์เลื่อนผ่าน (Pointer Events PASS-THROUGH)
                    st.markdown(
                        """<style>
/* สำหรับอุปกรณ์โทรศัพท์มือถือและหน้าจอขนาดเล็ก: ปรับขนาดกล่องและฟอนต์ให้กะทัดรัดพรีเมียม สามารถอ่านและสัมผัสกดปิดได้รวดเร็วปานสายฟ้าแลบ ไม่หน่วงค้างแข็ง! */
@media (max-width: 768px) {
    .congrats-modal {
        padding: 25px 20px !important;
        width: 88% !important;
        max-width: 330px !important;
    }
    .congrats-title {
        font-size: 1.3rem !important;
    }
    .congrats-leader {
        font-size: 1.15rem !important;
    }
    .congrats-score {
        font-size: 0.95rem !important;
    }
    .congrats-btn-placeholder {
        height: 48px !important;
    }
    div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] {
        top: calc(50vh + 105px) !important;
        min-width: 180px !important;
        max-width: 260px !important;
    }
    div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button {
        font-size: 0.95rem !important;
        padding: 10px 25px !important;
    }
}

/* แผงกั้นสีเบลอพื้นหลังเต็มจอ */
.congrats-modal-backdrop {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    background: rgba(8, 8, 16, 0.88) !important;
    backdrop-filter: blur(15px) !important;
    z-index: 999990 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    
    /* กุญแจสำคัญ: ปรับเป็น none เพื่อยอมให้เลื่อนหน้าจอ/รูดจอหลักด้านหลังบนมือถือได้ทันที ไม่ค้างแข็ง! */
    pointer-events: none !important;
    
    /* แอนิเมชันเฟดหายไปเองใน 3 วินาที เพื่อความลื่นไหลต่อเนื่องสูงสุด */
    animation: fade-out-disappear 3s forwards cubic-bezier(0.25, 1, 0.5, 1) !important;
}

/* ตัวการ์ดป๊อปอัปเฉลิมฉลองแชมป์ */
.congrats-modal {
    background: linear-gradient(135deg, rgba(20, 20, 38, 0.95) 0%, rgba(32, 32, 58, 0.98) 100%) !important;
    border: 3px solid #FFD700 !important;
    box-shadow: 0 0 50px rgba(255, 215, 0, 0.5), inset 0 0 20px rgba(255, 215, 0, 0.2) !important;
    border-radius: 28px !important;
    padding: 45px 35px !important;
    text-align: center !important;
    max-width: 520px !important;
    width: 90% !important;
    position: relative !important;
    
    /* เปิดใช้งาน touch / click บนตัวกล่อง Modal เองเพื่อให้กดปุ่มได้ปกติ */
    pointer-events: auto !important;
    
    /* สเกลเด้ง และเฟดหายพร้อมฉากหลัง */
    animation: popup-scale 0.55s cubic-bezier(0.175, 0.885, 0.32, 1.275) both,
               popup-fade-out 3s forwards ease-in-out !important;
}

/* ปุ่มกากบาทปิดสำรองที่มุมขวาบนของการ์ดเพื่อใช้งานง่ายบนโทรศัพท์ */
.congrats-close-x {
    position: absolute !important;
    top: 15px !important;
    right: 20px !important;
    font-size: 2.3rem !important;
    color: rgba(255, 255, 255, 0.4) !important;
    cursor: pointer !important;
    line-height: 1 !important;
    transition: all 0.25s ease !important;
    z-index: 1000005 !important;
    pointer-events: auto !important;
    font-family: Arial, sans-serif !important;
}
.congrats-close-x:hover {
    color: #FFD700 !important;
    transform: scale(1.15) !important;
}

/* ตัวจองพื้นที่ปุ่ม */
.congrats-btn-placeholder {
    height: 55px !important;
}

/* ยึดและดึงคอนเทนเนอร์ปุ่มของสตรีมลิตขึ้นมาลอยตัวบนสุด */
div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] {
    position: fixed !important;
    top: calc(50vh + 125px) !important;
    left: 50vw !important;
    transform: translate(-50%, -50%) !important;
    z-index: 1000000 !important; /* ชั้นสูงสุดเหนือ backdrop */
    width: auto !important;
    min-width: 260px !important;
    max-width: 440px !important;
    display: block !important;
    pointer-events: auto !important;
    
    /* เลือนหายไปพร้อมกล่อง */
    animation: button-fade-out 3s forwards ease-in-out !important;
}

/* สไตล์ปุ่มกดปิดสีทองพรีเมียมตระการตา */
div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button {
    background: linear-gradient(135deg, #FFD700 0%, #FF9F00 100%) !important;
    color: #000000 !important;
    font-weight: 800 !important;
    border: 2px solid #FFFFFF !important;
    padding: 12px 40px !important;
    border-radius: 50px !important;
    box-shadow: 0 8px 25px rgba(255, 215, 0, 0.5), 0 0 15px rgba(255, 215, 0, 0.3) !important;
    font-family: 'Kanit', sans-serif !important;
    font-size: 1.15rem !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    width: 100% !important;
    cursor: pointer !important;
    pointer-events: auto !important;
}

div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button:hover {
    transform: scale(1.06) !important;
    box-shadow: 0 12px 30px rgba(255, 215, 0, 0.7), 0 0 25px rgba(255, 215, 0, 0.5) !important;
}

div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] button:active {
    transform: scale(0.97) !important;
}

/* แอนิเมชันเลือนหาย (Fade Out) และปลอดการบังคลิก */
@keyframes fade-out-disappear {
    0% { opacity: 1; pointer-events: none; }
    70% { opacity: 1; pointer-events: none; }
    95% { opacity: 0; pointer-events: none; }
    100% { opacity: 0; pointer-events: none; display: none !important; }
}

@keyframes popup-fade-out {
    0% { opacity: 1; }
    70% { opacity: 1; transform: scale(1); }
    95% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 0; display: none !important; }
}

@keyframes button-fade-out {
    0% { opacity: 1; pointer-events: auto; }
    70% { opacity: 1; pointer-events: auto; }
    95% { opacity: 0; pointer-events: none; }
    100% { opacity: 0; pointer-events: none; display: none !important; }
}

@keyframes popup-scale {
    0% { transform: scale(0.5); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

@keyframes heartbeat {
    0% { transform: scale(1); }
    50% { transform: scale(1.04); }
    100% { transform: scale(1); }
}

.congrats-title {
    font-size: 1.7rem !important;
    color: #FFD700 !important;
    font-weight: 850 !important;
    margin-bottom: 8px !important;
    text-shadow: 0 0 15px rgba(255, 215, 0, 0.6) !important;
    font-family: 'Kanit', sans-serif !important;
}

.congrats-leader {
    font-size: 2.4rem !important;
    color: #FFFFFF !important;
    font-weight: 900 !important;
    margin: 18px 0 !important;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.7), 0 0 10px rgba(255, 215, 0, 0.4) !important;
    font-family: 'Kanit', sans-serif !important;
    animation: heartbeat 2s infinite !important;
}

.congrats-score {
    font-size: 1.3rem !important;
    color: #00E676 !important;
    font-weight: bold !important;
    margin-bottom: 20px !important;
    text-shadow: 0 0 10px rgba(0, 230, 118, 0.4) !important;
    font-family: 'Kanit', sans-serif !important;
}

/* วิ้งวิ้งและประกายดาว */
.congrats-sparkle {
    position: absolute !important;
    font-size: 1.5rem !important;
    animation: float-sparkle 3s infinite ease-in-out !important;
}
.sp1 { top: 10%; left: 8%; animation-delay: 0s !important; }
.sp2 { top: 15%; right: 10%; animation-delay: 0.5s !important; }
.sp3 { bottom: 25%; left: 12%; animation-delay: 1s !important; }
.sp4 { bottom: 20%; right: 15%; animation-delay: 1.5s !important; }
.sp5 { top: 50%; left: 5%; animation-delay: 0.8s !important; }

@keyframes float-sparkle {
    0%, 100% { transform: translateY(0) scale(0.8); opacity: 0.3; }
    50% { transform: translateY(-15px) scale(1.2); opacity: 1; text-shadow: 0 0 12px #FFD700; }
}

/* พลุกระจายแฉก */
.firework-particle {
    position: absolute !important;
    width: 6px !important;
    height: 6px !important;
    border-radius: 50% !important;
    background: #FFD700 !important;
    animation: explode 4s infinite ease-out !important;
    opacity: 0 !important;
}
.p1 { top: 20%; left: 20%; background: #FF3D00 !important; animation-delay: 0.2s !important; }
.p2 { top: 30%; right: 25%; background: #00E676 !important; animation-delay: 1.2s !important; }
.p3 { bottom: 35%; left: 25%; background: #29B6F6 !important; animation-delay: 2.2s !important; }
.p4 { bottom: 40%; right: 20%; background: #EC407A !important; animation-delay: 0.7s !important; }
.p5 { top: 12%; left: 50%; background: #FFEB3B !important; animation-delay: 1.7s !important; }

@keyframes explode {
    0% { transform: scale(0); opacity: 1; }
    20% { transform: scale(1.5) translate(var(--dx, 20px), var(--dy, -20px)); opacity: 0.9; }
    80%, 100% { transform: scale(0.5) translate(var(--dx, 40px), var(--dy, -40px)); opacity: 0; }
}

.p1 { --dx: -30px; --dy: -40px; }
.p2 { --dx: 45px; --dy: -30px; }
.p3 { --dx: -40px; --dy: 35px; }
.p4 { --dx: 35px; --dy: 40px; }
.p5 { --dx: 10px; --dy: -45px; }
</style>""",
                        unsafe_allow_html=True
                    )
                    
                    st.balloons()
                    
        # ป้องกันอาการล็อกค้าง: หากเงื่อนไขทำเนียบผู้นำไม่สมบูรณ์ (คะแนนนำเป็น 0 หรือว่าง) ให้สลับไปทำนายผลแชมป์โลกทันที
        if not show_congrats_rendered:
            st.session_state.show_congrats_popup = False
            existing_pred = db.get_user_champion_prediction(username)
            if not existing_pred and IS_CHAMPION_PRED_ACTIVE:
                st.session_state.show_champion_popup = True
            st.rerun()
    except Exception as e:
        # พิมพ์ Error ออกมาให้เห็นจะๆ บนหน้าจอเพื่อช่วยดีบัค
        st.sidebar.error(f"🚨 ดีบัคป๊อปอัปทำงานล้มเหลว: {e}")
        st.session_state.show_congrats_popup = False


# --- ระบบป๊อบอัพทำนายผลแชมป์โลก 2026 (ระบบเสถียรแบบล็อกสิทธิ์ถาวร 100%) ---
if 'show_champion_popup' not in st.session_state:
    st.session_state.show_champion_popup = False

# ตรวจสอบการเปิดป๊อปอัปทายผลแชมป์โลกครั้งแรกอัตโนมัติเมื่อล็อกอิน (สำหรับผู้ใช้ทุกคน)
if st.session_state.get('username'):
    # ต้องไม่แสดงในรอบที่มีการเรนเดอร์ป๊อปอัปความยินดีอยู่ เพื่อเลี่ยงการแสดงหน้าต่างซ้อนกัน
    if not st.session_state.get('show_congrats_popup', False) and not st.session_state.get('congrats_active_in_render', False):
        if 'auto_champion_check_done' not in st.session_state:
            st.session_state.auto_champion_check_done = True
            existing_pred = db.get_user_champion_prediction(username)
            # เด้งอัตโนมัติก็ต่อเมื่อเปิดรับทำนายจริงแล้ว หรือแอดมิน Art ต้องการทดสอบระบบ
            if (not existing_pred and IS_CHAMPION_PRED_ACTIVE) or username == "Art":
                st.session_state.show_champion_popup = True
                st.rerun()

    if st.session_state.get('show_champion_popup', False):
        show_champion_dialog(username)

# --- ระบบป๊อบอัพทำนายผลแชมป์โลกแบบเก่า (ปิดการใช้งานเพื่อความปลอดภัย) ---
if False:
    existing_pred = db.get_user_champion_prediction(username)
    
    # 1. กล่อง Input และปุ่มส่งข้อมูล Streamlit แบบล่องหนแต่อยู่ใน DOM (ป้องกันไม่ให้เบราว์เซอร์หรือสตรีมลิตบล็อกอีเวนต์ส่งค่า)
    st.markdown("<div style='opacity:0; position:absolute; width:0; height:0; pointer-events:none; overflow:hidden;' class='hidden-streamlit-inputs'>", unsafe_allow_html=True)
    selected_team_input = st.text_input("hidden_champ_input", key="hidden_champ_team", label_visibility="collapsed")
    submit_trigger = st.button("hidden_submit_btn", key="hidden_champ_submit")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # เมื่อปุ่มเบื้องหลังสตรีมลิตถูกคลิกผ่าน JavaScript สะพานเชื่อม
    if submit_trigger or st.session_state.get("hidden_champ_submit", False):
        val = st.session_state.get("hidden_champ_team", "").strip()
        if val:
            db.save_champion_prediction(username, val)
            st.session_state.show_champion_popup = False
            st.toast(f"🏆 บันทึกคำทำนายแชมป์โลก: {val} สำเร็จแล้ว! ตัดสินใจให้ดี!", icon="✅")
            st.rerun()
            
    # ดึงค่า Base64 สำหรับ ภาพ บอลโลก.png แบ็กกราวด์พรีเมียม
    worldcup_bg_b64 = worldcup_bg_base64 # ดึงจากที่โหลดไว้ตอนต้นไฟล์
    
    # รายชื่อทีมที่เข้ารอบ 10 ทีมสุดท้ายที่ยังอยู่ในเส้นทางลุ้นแชมป์โลก 2026
    TEAMS_LIST = [
        ("Argentina", "🇦🇷 อาร์เจนตินา (Argentina)"),
        ("Belgium", "🇧🇪 เบลเยียม (Belgium)"),
        ("Colombia", "🇨🇴 โคลอมเบีย (Colombia)"),
        ("Egypt", "🇪🇬 อียิปต์ (Egypt)"),
        ("England", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 อังกฤษ (England)"),
        ("France", "🇫🇷 ฝรั่งเศส (France)"),
        ("Morocco", "🇲🇦 โมร็อกโก (Morocco)"),
        ("Norway", "🇳🇴 นอร์เวย์ (Norway)"),
        ("Spain", "🇪🇸 สเปน (Spain)"),
        ("Switzerland", "🇨🇭 สวิตเซอร์แลนด์ (Switzerland)")
    ]
    
    # แปลงชื่อทีมภาษาอังกฤษเป็นคำอ่านภาษาไทยเพื่อแสดงผลในหน้าล็อก
    TEAM_TH_NAMES = {t[0]: t[1] for t in TEAMS_LIST}
    
    # สร้างมาร์กเกอร์และแผงควบคุมสไลเดอร์และปุ่ม HTML ด้วยสไตล์คัสตอมพรีเมียมเวิลด์คลาส
    if not existing_pred:
        # --- Status 1: Form Selection Form ---
        options_html = "".join([f'<option value="{code}">{label}</option>' for code, label in TEAMS_LIST])
        
        safe_markdown(f"""<div class="champ-modal-backdrop">
<div class="champ-modal">
<!-- ปุ่มกากบาทปิดตัว x สีทองพรีเมียมเพื่อปิดใช้งาน -->
<div class="champ-close-x" onclick="closeChampModal()">&times;</div>

<!-- ออร่าแสงหนุนหลังกล่องบางๆ -->
<div class="champ-ambient-glow"></div>

<!-- Countdown สิทธิ์จำกัดรอบ 16 ทีมพรีเมียม -->
<div class="champ-countdown-badge">
<span>🔴 สิทธิ์จำกัดรอบ 16 ทีม! นับถอยหลังปิดรับทายผล:</span>
<span class="champ-countdown-timer" id="champ-timer">23:59:59</span>
</div>

<div class="champ-trophy">🏆</div>
<h2 class="champ-h2">ทำนายผลแชมป์โลก 2026</h2>
<p class="champ-p">โอกาสแก้ตัวสำหรับผู้ร่วมสนุกที่ไม่ทันรอบแรก! เลือกทายผลประเทศที่จะพิชิตถ้วยฟุตบอลโลก 1 ทีมเท่านั้น และจะถูกเก็บข้อมูลไว้เป็นความลับจนกว่าจะถึงวันชิงชนะเลิศ ตัดสินใจให้ดี!</p>

<div class="champ-form-group">
<label class="champ-label">เลือกประเทศแชมป์โลกในใจคุณ</label>
<div class="champ-select-wrapper">
<select id="teamSelect" class="champ-select">
<option value="" disabled selected>-- เลือกประเทศที่คุณมั่นใจ --</option>
{options_html}
</select>
</div>
</div>

<button class="champ-btn-submit" onclick="submitChampPrediction()">
<span>บันทึกคำทำนายแชมป์โลก</span>
<span>🏆</span>
</button>
</div>
</div>

<div class="champ-trigger-marker"></div>

<script>
// นับถอยหลัง 24 ชม. ปรับเป็นตัวเลขเรียลไทม์จำลอง
var totalSecs = 24 * 60 * 60;
var timerEl = document.getElementById("champ-timer");
function updateChampTimer() {{
    var h = Math.floor(totalSecs / 3600);
    var m = Math.floor((totalSecs % 3600) / 60);
    var s = totalSecs % 60;
    h = h < 10 ? '0' + h : h;
    m = m < 10 ? '0' + m : m;
    s = s < 10 ? '0' + s : s;
    if (timerEl) {{
        timerEl.textContent = h + ":" + m + ":" + s;
    }}
    if (totalSecs > 0) {{
        totalSecs--;
    }} else {{
        if (timerEl) timerEl.textContent = "ปิดรับทายผล";
    }}
}}
setInterval(updateChampTimer, 1000);
updateChampTimer();

function closeChampModal() {{
    var backdrop = document.querySelector('.champ-modal-backdrop');
    if (backdrop) backdrop.remove();
    
    // ค้นหาแบบเปรียบเทียบจากข้อความเพื่อความชัวร์แบบไร้ที่ติ ทะลุ iframe ทั้งหมด
    var buttons = [];
    try {{
        if (window.parent && window.parent.document) {{
            buttons = window.parent.document.querySelectorAll('button');
        }}
    }} catch(e) {{}}
    if (!buttons || buttons.length === 0) {{
        buttons = document.querySelectorAll('button');
    }}
    for (var i = 0; i < buttons.length; i++) {{
        if (buttons[i].textContent.includes('❌ ปิดหน้าต่างนี้')) {{
            buttons[i].click();
            break;
        }}
    }}
}}

function submitChampPrediction() {{
    var selectEl = document.getElementById('teamSelect');
    if (!selectEl) return;
    var val = selectEl.value;
    if (!val) {{
        alert("กรุณาเลือกประเทศในใจคุณก่อนกดส่งคำทำนายนะครับ! 😉");
        return;
    }}
    
    // ค้นหาแบบสแกนเจาะจงและปลอดภัย 100% ครอบคลุมถึง Parent Iframe ของ Streamlit
    var docList = [document];
    try {{
        if (window.parent && window.parent.document) {{
            docList.push(window.parent.document);
        }}
    }} catch(e) {{}}
    
    var stInput = null;
    var stBtn = null;
    
    for (var d = 0; d < docList.length; d++) {{
        var currDoc = docList[d];
        
        var inputs = currDoc.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {{
            if (inputs[i].getAttribute('aria-label') === 'hidden_champ_input' || 
                (inputs[i].id && inputs[i].id.includes('hidden_champ_input')) ||
                inputs[i].placeholder === 'hidden_champ_input' ||
                (inputs[i].closest && inputs[i].closest('.hidden-streamlit-inputs'))) {{
                stInput = inputs[i];
                break;
            }}
        }}
        if (stInput) {{
            var buttons = currDoc.querySelectorAll('button');
            for (var k = 0; k < buttons.length; k++) {{
                if (buttons[k].textContent.includes('hidden_submit_btn') || 
                    buttons[k].getAttribute('aria-label') === 'hidden_submit_btn') {{
                    stBtn = buttons[k];
                    break;
                }}
            }}
        }}
        if (stInput && stBtn) break;
    }}
    
    if (stInput && stBtn) {{
        var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeSetter.call(stInput, val);
        stInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        stInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        
        setTimeout(function() {{
            stBtn.click();
        }}, 150);
    }} else {{
        // Fallback หาปุ่มหรืออินพุตอันแรกที่เป็นของกลุ่มซ่อน
        var hiddenDiv = document.querySelector('.hidden-streamlit-inputs');
        if (!hiddenDiv && window.parent && window.parent.document) {{
            hiddenDiv = window.parent.document.querySelector('.hidden-streamlit-inputs');
        }}
        if (hiddenDiv) {{
            var fbInput = hiddenDiv.querySelector('input');
            var fbBtn = hiddenDiv.querySelector('button');
            if (fbInput && fbBtn) {{
                var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                nativeSetter.call(fbInput, val);
                fbInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                fbInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                setTimeout(function() {{
                    fbBtn.click();
                }}, 150);
                return;
            }}
        }}
        alert("ระบบบันทึกติดขัด กรุณาลองเลือกทีมและกดบันทึกใหม่อีกครั้งนะครับ! 😉");
    }}
}}
</script>""")
    else:
        # --- Status 2: Locked State ---
        user_choice_th = TEAM_TH_NAMES.get(existing_pred, existing_pred)
        safe_markdown(f"""<div class="champ-modal-backdrop">
<div class="champ-modal">
<!-- ปุ่มกากบาทปิดตัว x สีทองพรีเมียมเพื่อปิดใช้งาน -->
<div class="champ-close-x" onclick="closeChampModal()">&times;</div>

<div class="champ-stamp-badge">🔒</div>
<h2 class="champ-h2">ทำนายผลแชมป์โลกสำเร็จแล้ว</h2>
<p class="champ-p">ระบบได้ทำการบันทึกและล็อกคำทำนายของคุณไว้เป็นความลับสูงสุดของฐานข้อมูลเรียบร้อยแล้ว ไม่สามารถแก้ไขได้ รอลุ้นผลพร้อมกันในวันนัดชิงชนะเลิศ!</p>

<div class="champ-predicted-info">
<div class="champ-predicted-label">ทีมที่คุณมั่นใจว่าจะได้แชมป์</div>
<div class="champ-predicted-team">{user_choice_th}</div>
</div>

<div class="champ-lock-notice">
<span>🔐</span>
<span class="champ-shimmer">SECRET KEY ENCRYPTED IN DATABASE</span>
</div>
</div>
</div>

<div class="champ-trigger-marker"></div>

<script>
function closeChampModal() {{
    var backdrop = document.querySelector('.champ-modal-backdrop');
    if (backdrop) backdrop.remove();
    
    // ค้นหาแบบเปรียบเทียบจากข้อความเพื่อความชัวร์แบบไร้ที่ติ ทะลุ iframe ทั้งหมด
    var buttons = [];
    try {{
        if (window.parent && window.parent.document) {{
            buttons = window.parent.document.querySelectorAll('button');
        }}
    }} catch(e) {{}}
    if (!buttons || buttons.length === 0) {{
        buttons = document.querySelectorAll('button');
    }}
    for (var i = 0; i < buttons.length; i++) {{
        if (buttons[i].textContent.includes('❌ ปิดหน้าต่างนี้')) {{
            buttons[i].click();
            break;
        }}
    }}
}}
</script>""")
        
    # พ่น CSS ของแผงควบคุม Champion Prediction ครอบคลุมการแสดงผลเบลอกลางจอและเด้งตอบสนองสวยงาม
    safe_markdown(f"""
        <style>
        .champ-modal-backdrop {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background: rgba(6, 9, 19, 0.9) !important;
            backdrop-filter: blur(25px) !important;
            -webkit-backdrop-filter: blur(25px) !important;
            z-index: 999990 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            pointer-events: none !important;
            animation: champ-fade-in 0.4s forwards ease !important;
            padding: 20px !important;
        }}
        .champ-modal {{
            background-image: 
                linear-gradient(rgba(13, 20, 38, 0.91), rgba(13, 20, 38, 0.96)),
                url('data:image/png;base64,{worldcup_bg_b64}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border-radius: 28px !important;
            padding: 40px 30px !important;
            box-shadow: 0 25px 55px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important;
            max-width: 500px !important;
            width: 100% !important;
            position: relative !important;
            text-align: center !important;
            pointer-events: auto !important;
            border: 1.5px solid rgba(255, 241, 197, 0.2) !important;
            animation: champ-popup-scale 0.5s cubic-bezier(0.16, 1, 0.3, 1) both !important;
        }}
        .champ-close-x {{
            position: absolute !important;
            top: 15px !important;
            right: 20px !important;
            font-size: 2rem !important;
            color: rgba(255, 255, 255, 0.4) !important;
            cursor: pointer !important;
            line-height: 1 !important;
            transition: all 0.25s ease !important;
            z-index: 1000005 !important;
            font-family: Arial, sans-serif !important;
        }}
        .champ-close-x:hover {{
            color: #E3A824 !important;
            transform: scale(1.15) !important;
        }}
        .champ-ambient-glow {{
            position: absolute !important;
            width: 300px !important;
            height: 300px !important;
            background: radial-gradient(circle, rgba(227, 168, 36, 0.08) 0%, transparent 70%) !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            pointer-events: none !important;
            z-index: 0 !important;
        }}
        .champ-countdown-badge {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            background: rgba(239, 68, 68, 0.08) !important;
            border: 1.5px solid rgba(239, 68, 68, 0.3) !important;
            color: #FF6666 !important;
            padding: 6px 14px !important;
            border-radius: 50px !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            margin-bottom: 20px !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.1) !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-countdown-timer {{
            font-weight: 900 !important;
            font-size: 13px !important;
            color: #FF4D4D !important;
            letter-spacing: 1px !important;
        }}
        .champ-trophy {{
            font-size: 64px !important;
            line-height: 1 !important;
            filter: drop-shadow(0 0 15px rgba(227, 168, 36, 0.5)) !important;
            margin-bottom: 15px !important;
            animation: champ-bounce 3.5s ease-in-out infinite !important;
        }}
        .champ-stamp-badge {{
            width: 80px !important;
            height: 80px !important;
            background: rgba(227, 168, 36, 0.12) !important;
            border: 2px dashed #E3A824 !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto 20px !important;
            color: #FFF1C5 !important;
            font-size: 32px !important;
            box-shadow: 0 0 20px rgba(227, 168, 36, 0.15) !important;
        }}
        .champ-h2 {{
            font-size: 26px !important;
            font-weight: 900 !important;
            background: linear-gradient(135deg, #FFF9E6 0%, #FFDF80 30%, #E3A824 65%, #8C6200 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            margin-bottom: 12px !important;
            line-height: 1.25 !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-p {{
            color: #A4B2C5 !important;
            font-size: 13.5px !important;
            line-height: 1.5 !important;
            margin-bottom: 25px !important;
            font-weight: 400 !important;
            padding: 0 10px !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-form-group {{
            margin-bottom: 25px !important;
            text-align: left !important;
        }}
        .champ-label {{
            display: block !important;
            font-size: 11px !important;
            font-weight: 800 !important;
            color: #FFEAA5 !important;
            margin-bottom: 8px !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-select-wrapper {{
            position: relative !important;
            width: 100% !important;
        }}
        .champ-select {{
            width: 100% !important;
            background: rgba(6, 9, 19, 0.9) !important;
            border: 1.5px solid rgba(227, 168, 36, 0.25) !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            font-size: 15px !important;
            color: #FFFFFF !important;
            font-family: 'Kanit', sans-serif !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            outline: none !important;
            appearance: none !important;
            -webkit-appearance: none !important;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease !important;
        }}
        .champ-select:focus {{
            border-color: #E3A824 !important;
            box-shadow: 0 0 12px rgba(227, 168, 36, 0.25), inset 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        }}
        .champ-select-wrapper::after {{
            content: "▼" !important;
            font-size: 10px !important;
            color: #E3A824 !important;
            position: absolute !important;
            right: 18px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            pointer-events: none !important;
        }}
        .champ-btn-submit {{
            width: 100% !important;
            background: linear-gradient(135deg, #FFE9A2 0%, #F5B82E 40%, #C48200 80%, #FFE9A2 100%) !important;
            background-size: 200% auto !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 15px 24px !important;
            color: #0E0A01 !important;
            font-size: 15px !important;
            font-weight: 800 !important;
            cursor: pointer !important;
            box-shadow: 0 10px 25px rgba(140, 98, 0, 0.3) !important;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
            font-family: 'Kanit', sans-serif !important;
            letter-spacing: 0.5px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 10px !important;
            position: relative !important;
            overflow: hidden !important;
            animation: champ-flow-shimmer 4s linear infinite !important;
        }}
        .champ-btn-submit:hover {{
            transform: translateY(-1.5px) !important;
            box-shadow: 0 12px 25px rgba(140, 98, 0, 0.5), 0 0 15px rgba(245, 184, 46, 0.3) !important;
            color: #000000 !important;
        }}
        .champ-predicted-info {{
            background: linear-gradient(180deg, rgba(8, 12, 23, 0.8) 0%, rgba(4, 6, 13, 0.95) 100%) !important;
            border: 1.5px solid rgba(227, 168, 36, 0.2) !important;
            border-radius: 14px !important;
            padding: 18px !important;
            margin-bottom: 22px !important;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5) !important;
            text-align: center !important;
        }}
        .champ-predicted-label {{
            font-size: 11px !important;
            font-weight: 700 !important;
            color: #8B9BB4 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            margin-bottom: 6px !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-predicted-team {{
            font-size: 20px !important;
            font-weight: 800 !important;
            color: #FFEAA5 !important;
            text-shadow: 0 0 12px rgba(255, 224, 114, 0.3) !important;
            font-family: 'Kanit', sans-serif !important;
        }}
        .champ-lock-notice {{
            color: #A0AEC0 !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            background: rgba(255, 255, 255, 0.03) !important;
            padding: 6px 14px !important;
            border-radius: 30px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            font-family: 'Segoe UI', Arial, sans-serif !important;
        }}
        .champ-shimmer {{
            background: linear-gradient(90deg, #E3A824 20%, #FFFFFF 50%, #E3A824 80%) !important;
            background-size: 200% auto !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: champ-shimmer-anim 4s linear infinite !important;
        }}
        
        /* สตรีมลิตปิดทับกริบ */
        div[data-testid="element-container"]:has(.champ-trigger-marker) + div[data-testid="element-container"] {{
            position: fixed !important;
            top: calc(50vh + 175px) !important;
            left: 50vw !important;
            transform: translate(-50%, -50%) !important;
            z-index: 1000000 !important;
            width: auto !important;
            min-width: 180px !important;
            max-width: 400px !important;
            display: block !important;
            pointer-events: auto !important;
        }}
        div[data-testid="element-container"]:has(.champ-trigger-marker) + div[data-testid="element-container"] button {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
            color: #FF6666 !important;
            font-weight: 700 !important;
            border: 1.5px solid rgba(239, 68, 68, 0.3) !important;
            padding: 8px 30px !important;
            border-radius: 50px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
            font-family: 'Kanit', sans-serif !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            cursor: pointer !important;
        }}
        div[data-testid="element-container"]:has(.champ-trigger-marker) + div[data-testid="element-container"] button:hover {{
            transform: scale(1.04) !important;
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15) !important;
            border-color: #FF4D4D !important;
        }}
        
        @keyframes champ-flow-shimmer {{
            0% {{ background-position: 0% center; }}
            100% {{ background-position: -200% center; }}
        }}
        @keyframes champ-shimmer-anim {{
            to {{ background-position: -200% center; }}
        }}
        @keyframes champ-bounce {{
            0%, 100% {{ transform: translateY(0) scale(1); }}
            50% {{ transform: translateY(-6px) scale(1.02); }}
        }}
        @keyframes champ-fade-in {{
            0% {{ opacity: 0; pointer-events: none; }}
            100% {{ opacity: 1; pointer-events: auto; }}
        }}
        @keyframes champ-popup-scale {{
            0% {{ transform: scale(0.9); opacity: 0; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        </style>
    """)
    
    # ปุ่มยกเลิก/ปิดพรีเมียมของสตรีมลิตสำหรับควบคุม liveness state หลังบ้าน
    if st.button("❌ ปิดหน้าต่างนี้", key="close_champ_popup_btn", use_container_width=True):
        st.session_state.show_champion_popup = False
        st.rerun()


# --- ตรวจสอบอัปเดตผลสกอร์แบบเรียลไทม์อัตโนมัติ (แคชไว้ 30 นาที) ---
check_and_sync_scores()


# --- คำนวณคู่แข่งขันที่ยังไม่ได้ทายผลสำหรับเตือนความจำ ---
if 'toast_shown' not in st.session_state:
    st.session_state.toast_shown = False
if 'music_saved_preference' not in st.session_state:
    st.session_state.music_saved_preference = True


try:
    all_matches_rem = db.get_matches()
    all_matches_rem['match_dt'] = pd.to_datetime(all_matches_rem['match_time'])
    now_th_rem = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    
    # ดึงคู่ที่ยังไม่จบการแข่งขัน และเวลาเตะต้องมากกว่าเวลาปัจจุบันอย่างน้อย 1 ชั่วโมง (สามารถแก้ไขได้)
    active_upcoming_rem = all_matches_rem[
        (all_matches_rem['status'] != 'Finished') & 
        (all_matches_rem['match_dt'] > now_th_rem + pd.Timedelta(hours=1))
    ]
    
    user_preds_rem = db.get_user_predictions(username)
    unpredicted_list = []
    
    for _, row in active_upcoming_rem.iterrows():
        m_id = safe_int(row['id'])
        if m_id not in user_preds_rem:
            unpredicted_list.append(row)
            
    st.session_state.unpredicted_count = len(unpredicted_list)
    st.session_state.unpredicted_matches = unpredicted_list
    
    # สั่นแจ้งเตือน (Toast) ครั้งแรกตอนล็อกอินสำเร็จ
    if not st.session_state.toast_shown and len(unpredicted_list) > 0:
        st.toast(f"🚨 คุณ {username}! ยังมีคู่แข่งขันที่ยังไม่ได้ทายผลอีก {len(unpredicted_list)} คู่ครับ!", icon="🚨")
        st.session_state.toast_shown = True
except Exception as e:
    st.session_state.unpredicted_count = 0
    st.session_state.unpredicted_matches = []

# --- ระบบเมนูและเพลงประกอบ (จัดลำดับประมวลผลสูงสุดเพื่อขจัดอาการกดย้ำ) ---
if st.session_state.authenticated:
    # 🧭 เมนูนำทางหลัก (ย้ายขึ้นบนสุดเพื่อลำดับสิทธิ์การทำงานลำดับแรก ขจัดปัญหาความหน่วงและอาการกดย้ำ)
    menu_options = ["ศึกชิงแชมป์โลก 2026 (World Cup)", "ผลการแข่งขันย้อนหลัง (Match Results)", "ตารางคะแนนกลุ่ม (Standings)", "ประวัติการทายผล (My Predictions)", "ทำเนียบแชมป์ (Leaderboard)"]
    if st.session_state.username == "Art":
        menu_options.append("ห้องควบคุมระบบ (Admin)")

    # เพื่อแก้ปัญหาการกดยื่นเปลี่ยนเมนูแล้วหน้าเว็บค้างหรือไม่ไปตามหน้าที่เลือก (Navigation Desynchronization Bug)
    # เราผูกระบบเข้ากับ Session State (main_navigation_menu) เพื่อล็อกสถานะการเลือกของหน้านั้นๆ ให้คงอยู่และทำงานได้แม่นยำ 100% ปลอดภัยสูง
    if "main_navigation_menu" not in st.session_state or st.session_state.main_navigation_menu not in menu_options:
        st.session_state.main_navigation_menu = menu_options[0]
        
    try:
        menu_default_idx = menu_options.index(st.session_state.main_navigation_menu)
    except ValueError:
        menu_default_idx = 0
        
    menu = st.sidebar.radio(
        "เมนูหลัก", 
        menu_options, 
        index=menu_default_idx, 
        key="main_navigation_menu"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📻 เครื่องเล่นเสียงควบคุม")
    
    # 1. แถบเสียงพากย์ปีเตอร์ AI (วิเคราะห์คะแนน 1.60x)
    speech_file_path = os.path.join(current_dir, "static", "ai_analysis_fast.webp")
    if not os.path.exists(speech_file_path):
        speech_file_path = os.path.join(current_dir, "static", "ai_analysis_fast.mp3")
    if os.path.exists(speech_file_path):
        st.sidebar.audio(
            speech_file_path,
            format="audio/webp" if speech_file_path.endswith(".webp") else "audio/mp3",
            autoplay=True
        )
    
    # 2. แถบเสียงบรรยากาศสนาม (กล่อมเบาๆ)
    music_file_path = os.path.join(current_dir, "static", "stadium_crowd_low.webp")
    if not os.path.exists(music_file_path):
        music_file_path = os.path.join(current_dir, "static", "stadium_crowd_low.mp3")
    if os.path.exists(music_file_path):
        st.sidebar.audio(
            music_file_path,
            format="audio/webp" if music_file_path.endswith(".webp") else "audio/mp3",
            autoplay=True,
            loop=True
        )

    # --- แถบสรุปผลการแข่งขันของวันนี้/วันล่าสุดย้อนหลัง 1 วันใน Sidebar ---
    st.sidebar.markdown("---")

    try:
        # ดึงข้อมูลแมตช์และประวัติการทายผลทั้งหมด
        all_matches_sb = db.get_matches()
        all_matches_sb['match_dt'] = pd.to_datetime(all_matches_sb['match_time'])
        finished_sb = all_matches_sb[all_matches_sb['status'] == 'Finished'].sort_values('match_time', ascending=False)

        if not finished_sb.empty:
            # คำนวณวันปัจจุบัน (เวลาไทย UTC+7)
            now_th_sb = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            today_date_sb = now_th_sb.date()
            yesterday_date_sb = today_date_sb - timedelta(days=1)
            
            # กรองแมตช์ที่แข่งเสร็จในวันนี้และเมื่อวาน (ตามเวลาไทย UTC+7) เพื่อความต่อเนื่องพรีเมี่ยมครอบคลุมคู่ดึก
            day_matches_sb = finished_sb[finished_sb['match_dt'].dt.date.isin([today_date_sb, yesterday_date_sb])]
            
            st.sidebar.subheader("📅 ผลการแข่งขันล่าสุด")
            
            if day_matches_sb.empty:
                st.sidebar.info("ไม่มีผลการแข่งขันล่าสุด")
            
            # ดึงประวัติการทายเพื่อประมวลผลความถูกต้องของผู้ใช้งานทั้งหมด
            predictions_sb = db.get_predictions_df()
            
            for _, row_m in day_matches_sb.iterrows():
                m_id = str(row_m['id'])
                h_real = safe_int(row_m['home_score'])
                a_real = safe_int(row_m['away_score'])
                real_win = (h_real > a_real) - (h_real < a_real)
                
                home_display = get_team_display(row_m['home_team'])
                away_display = get_team_display(row_m['away_team'])
                
                exp_title = f"{home_display} {h_real} - {a_real} {away_display}"
                
                with st.sidebar.expander(exp_title):
                    st.markdown(f"**⚽ ผู้ทำประตู:** {row_m['scorers'] if row_m['scorers'] else 'ไม่มีข้อมูล'}")
                    st.markdown("**🎯 ผลทายของทุกคน in คู่นี้:**")
                    
                    # กรองคำทายของคู่นี้
                    m_preds = predictions_sb[predictions_sb['match_id'].astype(str) == m_id]
                    if m_preds.empty:
                        st.markdown("<small style='color:#888;'>ยังไม่มีผู้เล่นทายคู่นี้</small>", unsafe_allow_html=True)
                    else:
                        preds_html_list = []
                        for _, row_p in m_preds.iterrows():
                            u_name = row_p['username']
                            p_h = safe_int(row_p['pred_home'])
                            p_a = safe_int(row_p['pred_away'])
                            pred_win = (p_h > p_a) - (p_h < p_a)
                            
                            # คำนวณแต้มและสไตล์สีสันเพื่อความพรีเมี่ยมตระการตา
                            if p_h == h_real and p_a == a_real:
                                hl_style = "background: rgba(255, 215, 0, 0.12); border: 1px solid rgba(255, 215, 0, 0.35); color: #ffd700;"
                                pt_txt = "🏆 3 แต้ม"
                            elif pred_win == real_win:
                                hl_style = "background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.25); color: #2ecc71;"
                                pt_txt = "🟢 1 แต้ม"
                            else:
                                hl_style = "background: rgba(231, 76, 60, 0.08); border: 1px solid rgba(231, 76, 60, 0.15); color: #e74c3c;"
                                pt_txt = "❌ 0 แต้ม"
                            
                            # จัดการแสดงผลระบบโบนัสรอบน็อกเอาต์ (Golden Bonus: Match ID >= 68)
                            bonus_txt = ""
                            pred_q_txt = ""
                            m_id_int = safe_int(m_id)
                            if m_id_int >= 68:
                                p_qualify = str(row_p.get('pred_qualify', '')).strip()
                                if p_qualify == "":
                                    try:
                                        if p_h > p_a:
                                            p_qualify = str(row_m.get('home_team', '')).strip()
                                        elif p_a > p_h:
                                            p_qualify = str(row_m.get('away_team', '')).strip()
                                    except Exception:
                                        pass
                                w_qualify = str(row_m.get('winner_qualify', '')).strip()
                                if p_qualify:
                                    # แสดงธง/ชื่อทีมที่เลือกเข้ารอบ
                                    pred_q_txt = f" <span style='opacity: 0.8;'>🗳️ เลือก {get_team_display(p_qualify)}</span>"
                                if w_qualify != "" and w_qualify.lower() != "nan":
                                    if p_qualify != "" and p_qualify.lower() == w_qualify.lower():
                                        bonus_txt = " <b style='color: #ffffff;'>+ 🌟 โบนัส 1 แต้ม</b>"
                                    else:
                                        bonus_txt = " <span style='color: #ffffff; opacity: 0.6;'>+ ❌ โบนัส 0 แต้ม</span>"
                            
                            preds_html_list.append(
                                f"<div style='font-size:0.8rem; padding:6px 10px; border-radius:6px; margin-bottom:5px; {hl_style}'>"
                                f"👤 <b>{u_name}</b>: ทาย {p_h} - {p_a}{pred_q_txt} ({pt_txt}{bonus_txt})"
                                f"</div>"
                            )
                        
                        # หุ้มผลทายทั้งหมดไว้ในกล่อง scroll ย่อยเพื่อจำกัดความสูงไม่ให้ล้นหน้าจอ
                        all_preds_html = "".join(preds_html_list)
                        st.markdown(
                            f"<div style='max-height:180px; overflow-y:auto; padding-right:5px; scrollbar-width:thin; scrollbar-color:rgba(255,215,0,0.35) transparent;'>"
                            f"{all_preds_html}"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        if m_id_int >= 68:
                            st.markdown("<div style='font-size:0.7rem; color: #888; margin-top:5px; padding-left:2px;'>💡 <i>รอบน็อกเอาต์: ทายฝั่งเข้ารอบถูก โบนัส +1 แต้ม (ผิด +0)</i></div>", unsafe_allow_html=True)
        else:
            st.sidebar.info("ไม่มีผลการแข่งขันล่าสุด")
    except Exception as sb_err:
        st.sidebar.error(f"⚠️ เกิดข้อผิดพลาดในการสรุปผลล่าสุด: {sb_err}")

    st.sidebar.markdown("---")



# 2. หน้าทายผลการแข่งขัน
if menu == "ศึกชิงแชมป์โลก 2026 (World Cup)":
    # 🚨 แสดงระบบกันลืม (Smart Prediction Reminder)
    if 'unpredicted_matches' in st.session_state and st.session_state.unpredicted_matches:
        matches_list_html = []
        for m in st.session_state.unpredicted_matches:
            h_disp = get_team_display(m['home_team'])
            a_disp = get_team_display(m['away_team'])
            m_t = pd.to_datetime(m['match_time']).strftime('%d/%m/%Y %H:%M น.')
            matches_list_html.append(
                f"<div style='margin-bottom: 5px;'>⚽ <b>{h_disp} vs {a_disp}</b> (⏰ เริ่มเตะ {m_t})</div>"
            )
        matches_html = "".join(matches_list_html)
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, rgba(255, 75, 75, 0.15) 0%, rgba(255, 0, 0, 0.05) 100%); 
                        border: 1px solid #FF4B4B; padding: 15px 20px; border-radius: 12px; margin-bottom: 10px; 
                        box-shadow: 0 0 15px rgba(255, 75, 75, 0.2);'>
                <div style='color: #FF4B4B; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px; font-family: Kanit, sans-serif;'>
                    🚨 คุณ {username} ครับ! ยังมีคู่แข่งขันที่ยังไม่ได้ทายผลอีก {len(st.session_state.unpredicted_matches)} คู่:
                </div>
                <div style='color: #e2e8f0; font-size: 0.95rem; font-family: Kanit, sans-serif; padding-left: 10px;'>
                    {matches_html}
                </div>
                <div style='color: #a0aec0; font-size: 0.85rem; margin-top: 10px; font-style: italic;'>
                    *กรุณากรอกผลและกด \"บันทึกผลทาย\" ด้านล่างก่อนเวลาเตะเพื่อป้องกันการเสียแต้มสะสม
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    # ระบบแสดงข้อมูลทำเนียบผู้นำเฉพาะผู้เล่นที่มีคะแนนสะสมมากกว่า 0 ขึ้นมาทันที
    try:
        leaderboard_df = db.get_leaderboard()
        # กรองเฉพาะผู้เล่นที่มีคะแนนมากกว่า 0 คะแนนเท่านั้น
        leaderboard_df = leaderboard_df[leaderboard_df['total_score'] > 0]
        
        if not leaderboard_df.empty:
            top_3 = leaderboard_df.head(3)
            leaders_list = []
            for idx, (_, row) in enumerate(top_3.iterrows(), 1):
                medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else "🥉")
                leaders_list.append(f"{medal} <b>{row['username']}</b> ({int(row['total_score'])} แต้ม)")
            
            leaders_html = " &nbsp;&nbsp;|&nbsp;&nbsp; ".join(leaders_list)
            
            # เพิ่มระยะห่างไม่ให้เบียดชิดกับป้ายแบนเนอร์ CRAZYFIFA 2026 หัวข้อหลักด้านบน
            st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
            
            # เรนเดอร์กล่องแสดงทำเนียบผู้เล่น Top 3 แบบเรียบง่ายขนาดกะทัดรัด (ไม่ต้องคลิกเปิด)
            st.markdown(
                f"""
                <div style='background: rgba(255, 215, 0, 0.05); border: 1px solid rgba(255, 215, 0, 0.2); 
                            padding: 10px 20px; border-radius: 12px; text-align: center; margin-bottom: 25px;'>
                    <span style='color: #FFD700; font-weight: bold; font-size: 0.95rem; margin-right: 15px; font-family: Kanit, sans-serif;'>🔥 3 อันดับผู้นำท็อปฟอร์ม:</span>
                    <span style='color: #e2e8f0; font-size: 0.95rem; font-family: Kanit, sans-serif;'>{leaders_html}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
    except Exception as e:
        pass

    # 🎙️ เพิ่มบอร์ดวิเคราะห์วิจารณ์บอลโลกประจำวันโดย "ปีเตอร์ AI" (Glassmorphism AI Analyst Board)
    try:
        # อิมพอร์ต ai_analyst ท้องถิ่นเพื่อรันงาน
        import importlib
        import ai_analyst
        importlib.reload(ai_analyst)
        
        # ดึงสถานะชื่อผู้ใช้
        current_username = username
        is_admin = (current_username == "Art")
        
        # จัดตั้งตัวแปรส่งสัญญาณ Force Refresh
        force_ai = False
        if is_admin:
            # วาง Marker นำทางและแต่งปุ่มแอดมินให้คลิกได้ลื่นไหล 100%
            st.markdown("<span class='force-ai-marker'></span>", unsafe_allow_html=True)
            if st.button("🔄 ปลุกพลังปีเตอร์ AI วิเคราะห์ข้อมูลใหม่ (Admin Only)", key="btn_force_ai"):
                force_ai = True
                
        # ดึงบทสรุปและจัดการแคชอัตโนมัติ
        predictions_df_for_ai = db.get_predictions_df()
        current_matches_for_ai = db.get_matches()
        
        ai_report, model_used, is_cached = ai_analyst.get_ai_summary(
            leaderboard_df if 'leaderboard_df' in locals() else db.get_leaderboard(), 
            current_matches_for_ai, 
            predictions_df_for_ai, 
            force_refresh=force_ai
        )
        
        if ai_report:
            # กำหนดป้ายแสดงสถานะ (Badge Text) สำหรับแอดมินและผู้ใช้งานทั่วไปเพื่อความสวยงามเป็นส่วนตัว
            if is_admin:
                badge_text = f"🤖 {model_used} {'(จากแคช)' if is_cached else '(คำนวณใหม่)'}"
            else:
                badge_text = "🟢 ปีเตอร์ AI วิเคราะห์ล่าสุด"

            # ใช้ Glassmorphism CSS สไตล์พรีเมี่ยม
            st.markdown(
                f"""
                <style>
                /* ดันปุ่มสั่งรัน AI ของแอดมินให้ลอยขึ้นชั้นบนสุดเพื่อแก้ปัญหากล่องล่างบังปุ่มคลิกยาก */
                div[data-testid="element-container"]:has(.force-ai-marker) + div[data-testid="element-container"] {{
                    position: relative !important;
                    z-index: 9999 !important;
                    margin-bottom: 12px !important;
                }}
                div[data-testid="element-container"]:has(.force-ai-marker) + div[data-testid="element-container"] button {{
                    pointer-events: auto !important;
                    cursor: pointer !important;
                    z-index: 10000 !important;
                }}
                .peter-ai-box {{
                    background: linear-gradient(135deg, rgba(45, 58, 49, 0.4) 0%, rgba(26, 36, 30, 0.5) 100%);
                    border: 1px solid rgba(255, 215, 0, 0.25);
                    padding: 22px 26px;
                    border-radius: 16px;
                    margin-bottom: 25px;
                    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
                    backdrop-filter: blur(8px);
                    -webkit-backdrop-filter: blur(8px);
                    font-family: 'Kanit', sans-serif;
                    position: relative;
                    overflow: hidden;
                }}
                .peter-ai-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 12px;
                    border-bottom: 1px solid rgba(255, 215, 0, 0.15);
                    padding-bottom: 10px;
                }}
                .peter-ai-title {{
                    color: #FFD700;
                    font-weight: 600;
                    font-size: 1.15rem;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .peter-ai-badge {{
                    background: rgba(255, 215, 0, 0.12);
                    color: #FFD700;
                    font-size: 0.72rem;
                    padding: 3px 10px;
                    border-radius: 20px;
                    font-family: 'Kanit', sans-serif, monospace;
                    border: 1px solid rgba(255, 215, 0, 0.2);
                }}
                .peter-ai-content {{
                    color: #e2e8f0;
                    font-size: 0.95rem;
                    line-height: 1.6;
                }}
                .big-match {{
                    background: rgba(255, 94, 54, 0.12) !important;
                    color: #FF5E36 !important;
                    border: 1px solid rgba(255, 94, 54, 0.25) !important;
                    padding: 2px 8px !important;
                    border-radius: 6px !important;
                    font-weight: bold !important;
                    display: inline-block !important;
                    margin: 2px 0 !important;
                }}
                </style>
                <div class="peter-ai-box">
                    <div class="peter-ai-header">
                        <div class="peter-ai-title">🎙️ ปีเตอร์ AI สรุปวิเคราะห์และวิจารณ์ประจำวัน</div>
                        <div class="peter-ai-badge">{badge_text}</div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            # ปรับแต่งคำทักทายแบบ Dynamic ตามชื่อผู้ใช้ที่ล็อกอินจริงใน Session (เซสชัน: ช่วงเวลาการใช้งานของผู้ใช้)
            personalized_report = ai_report
            if "{USERNAME}" in personalized_report:
                personalized_report = personalized_report.replace("{USERNAME}", current_username)
            else:
                # รองรับการแทนที่คำทักทายแบบเก่า (Static) เผื่อในไฟล์แคชเก่ายังไม่มีตัวแปร {USERNAME} เพื่อให้ทำงานได้ทันทีโดยไม่ต้องรอแอดมินล้างแคช
                for old_greet in ["คุณอาร์ตและผองเพื่อน", "คุณอาร์ตและเหล่านักล่าแต้มทุกคน", "คุณอาร์ตและเหล่านักล่าแต้ม", "คุณอาร์ตและแก๊งผู้ร่วมทายผล", "คุณอาร์ต"]:
                    if old_greet in personalized_report:
                        # แทนที่คำทักทายด้วยชื่อของผู้ใช้ที่ล็อกอินจริง
                        personalized_report = personalized_report.replace(old_greet, f"คุณ {current_username} และเหล่านักล่าแต้มทุกคน")
                        break
            
            # ดำเนินการลบเครื่องหมายแบ็กทิกที่ครอบรอบคำสำคัญที่อาจหลงเหลือมาจากประวัติแคชเดิม
            for term in [
                "Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)", 
                "Daily MVP (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน)",
                "Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน)",
                "Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)"
            ]:
                personalized_report = personalized_report.replace(f"`{term}`", term)
            
            # ตกแต่งเสริมสีสันและไฮไลท์แบบไฮเอนด์ด้วยการตรวจจับประเด็น (Fallback High-end Highlights) สำหรับแคชเดิมที่ยังไม่มีโค้ดสี HTML ติดมาจากระบบหลังบ้าน
            personalized_report = personalized_report.replace(
                "Daily MVP (เดลี เอ็มวีพี: ผู้เล่นทำผลงานโดดเด่นประจำวัน)",
                "🏆 <span style='color: #00FF87; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,135,0.15);'>วิเคราะห์ Daily MVP ประจำวัน</span>"
            ).replace(
                "Daily MVP (เดลี เอ็มวีพี: ผู้ทำคะแนนหรือผลงานได้โดดเด่นสะดุดตาประจำวัน)",
                "🏆 <span style='color: #00FF87; font-weight: bold; text-shadow: 0 0 10px rgba(0,255,135,0.15);'>วิเคราะห์ Daily MVP ประจำวัน</span>"
            ).replace(
                "Leaderboard (ลีดเดอร์บอร์ด: ตารางคะแนนผู้นำ)",
                "📊 <span style='color: #00E5FF; font-weight: bold; text-shadow: 0 0 10px rgba(0,229,255,0.15);'>ความเคลื่อนไหวบน Leaderboard</span>"
            ).replace(
                "Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)",
                "<span style='color: #FFD700; font-weight: bold;'>Perfect Prediction (เพอร์เฟกต์ พรีดิกชัน: การทายผลสกอร์ได้อย่างถูกต้องแม่นยำร้อยเปอร์เซ็นต์)</span>"
            ).replace(
                "โหมโรงศึกเดือดสะท้านตารางคืนนี้",
                "โหมโรงศึกเดือดสะท้านตารางวันถัดไป"
            ).replace(
                "โหมโรงศึกเดือดสะท้านตารางล่วงหน้า",
                "โหมโรงศึกเดือดสะท้านตารางวันถัดไป"
            ).replace(
                "ศึกเปลี่ยนชีวิตประจำค่ำคืน",
                "ศึกเปลี่ยนชีวิตล่วงหน้า"
            )

            # แทรกขีดคั่นสวยงามแบบอัตโนมัติหากพบหัวข้อย่อยแบบเดิมเพื่อแบ่งสัดส่วนบอร์ดไม่ให้อ่านยาก
            for old_section in ["ตำแหน่ง Daily MVP", "สถานการณ์บน Leaderboard", "คืนนี้เตรียมตัวรับแรงกระแทก", "แมตช์ต่อไปที่กำลังจะมาถึง", "โหมโรงศึกเดือดสะท้านตารางคืนนี้", "โหมโรงศึกเดือดสะท้านตารางวันถัดไป", "โหมโรงศึกเดือดสะท้านตารางล่วงหน้า"]:
                if old_section in personalized_report:
                    personalized_report = personalized_report.replace(
                        old_section,
                        f"<hr style='border: 0; border-top: 1px solid rgba(255, 215, 0, 0.08); margin: 12px 0;'>{old_section}"
                    )

            # ตกแต่งรายชื่อคู่แข่งขันเปลี่ยนชีวิตของคืนนี้ให้เรืองแสงส้มสะดุดตาโดดเด่น (Dynamic Upcoming Match Highlighting)
            upcoming_matches_list = []
            if not current_matches_for_ai.empty:
                upcoming = current_matches_for_ai[current_matches_for_ai['status'] == 'Upcoming']
                for _, row in upcoming.iterrows():
                    upcoming_matches_list.extend([
                        f"{row['home_team']} พบ {row['away_team']}",
                        f"{row['home_team']} vs {row['away_team']}"
                    ])

            for tonight_match in upcoming_matches_list + ["Portugal พบ Uzbekistan", "England ดวลเดือด Ghana"]:
                if tonight_match in personalized_report:
                    if f"class='big-match'>{tonight_match}" not in personalized_report and f'class="big-match">{tonight_match}' not in personalized_report:
                        personalized_report = personalized_report.replace(
                            tonight_match,
                            f"<span class='big-match'>🔥 {tonight_match}</span>"
                        )

            # ดำเนินการคลีนแบ็กทิก (Backticks Strip) ที่อาจครอบรอบแท็ก HTML ทั้งหมดออกไปเพื่อป้องกัน Markdown เอสเคปคีย์
            # เช่น `📊 <span ...>...</span>` -> 📊 <span ...>...</span>
            import re
            personalized_report = re.sub(r'`([^`]*<[^`]+>[^`]*)`', r'\1', personalized_report)

            # แสดงเนื้อหาบทสรุปเป็น markdown เพื่อประมวลผลข้อความและ HTML ให้สวยงาม
            st.markdown(personalized_report, unsafe_allow_html=True)
            
            # ดึงแฮชของบทวิเคราะห์เพื่อแยกแยะเสียงพากย์วิเคราะห์ชุดปัจจุบัน
            current_voice_version = "default_v1"
            try:
                cache_path_sb = os.path.join(current_dir, "ai_cache.json")
                if os.path.exists(cache_path_sb):
                    with open(cache_path_sb, "r", encoding="utf-8") as f_r_sb:
                        import json
                        c_data_sb = json.load(f_r_sb)
                        current_voice_version = c_data_sb.get("hash_key", "default_v1")
            except:
                pass
            st.session_state.current_voice_version = current_voice_version
            
            # แทรกปุ่มฟังเสียงพากย์ของปีเตอร์ AI
            peter_voice_html = get_peter_voice_html(session_audio_id=current_voice_version)
            st.markdown(peter_voice_html, unsafe_allow_html=True)
            
            # ปิดกล่อง HTML
            st.markdown("</div>", unsafe_allow_html=True)
            if force_ai:
                st.success("🔄 ปลดล็อกพลังปีเตอร์และเขียนสรุปบทวิเคราะห์ใหม่สำเร็จเรียบร้อยครับ!")
    except Exception as e_ai:
        # ใช้ Try-Except ครอบโครงสร้าง AI ทั้งหมดเพื่อความปลอดภัย 100% ต่อระบบ
        pass

    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])

    # ดึงผลทำนายของผู้เล่นในครั้งเดียวที่นี่! เพื่อประหยัดการเชื่อมต่อ API ของ Google Sheets (Quota Saving)
    try:
        user_preds_cached = db.get_user_predictions(username)
    except Exception as e:
        user_preds_cached = {}

    def render_match(row, username):
        match_id = safe_int(row['id'])
        home = row['home_team']
        away = row['away_team']
        home_display = get_team_display(home)
        away_display = get_team_display(away)

        # แปลงเวลาเตะอย่างยืดหยุ่นและปลอดภัยจากประเภทข้อมูล Timestamp/String
        m_time = row['match_dt'] if 'match_dt' in row and pd.notnull(row['match_dt']) else pd.to_datetime(row['match_time'])
        if not isinstance(m_time, datetime):
            m_time = m_time.to_pydatetime()
        status = row['status']
        now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        # ปิดรับทายผลล่วงหน้าก่อนเวลาแข่งขันจริง 1 ชั่วโมง หรือเมื่อเกมเริ่มเตะ/แข่งจบแล้ว ตามสเปกความปลอดภัยสูงสุด
        is_locked = now_th > (m_time - timedelta(hours=1)) or status in ['Finished', 'Live']

        has_pred = match_id in user_preds_cached
        preds_tuple = user_preds_cached.get(match_id, (0, 0, ""))
        default_h = preds_tuple[0]
        default_a = preds_tuple[1]
        default_q = preds_tuple[2] if len(preds_tuple) > 2 else ""
        
        # กำหนดคะแนนที่จะแสดงในช่องกรอก (ถ้าเกมจบแล้ว ให้แสดงสกอร์จริงในช่องที่ปิดการแก้ไข)
        if status == 'Finished':
            val_h = safe_int(row['home_score'])
            val_a = safe_int(row['away_score'])
        else:
            val_h = safe_int(default_h)
            val_a = safe_int(default_a)

        # ตรวจสอบว่าเป็นรอบน็อกเอาต์หรือไม่จาก Match ID >= 68
        is_knockout = match_id >= 68

        # ใช้ Hybrid Form-Container: 
        # หากไม่โดนล็อก (สามารถทายผลได้) ให้ครอบด้วย st.form เพื่อป้องกันหน้าจอ Rerun ทันทีขณะเปลี่ยนค่าตัวเลข
        if not is_locked:
            with st.form(key=f"form_match_{match_id}", clear_on_submit=False):
                # แถวแรก: แสดงคู่แข่งขันและเวลาเตะตัวใหญ่สวยงามชัดเจน
                st.subheader(f"{home_display} 🆚 {away_display}")
                st.caption(f"⏰ เวลาเตะ: {m_time.strftime('%d/%m/%Y %H:%M')}")
                
                # แถวสอง: แสดงช่องกรอกคะแนนของทั้งสองทีมพร้อมปุ่มบันทึกผล
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    pred_h = st.number_input(
                        label="⚽ สกอร์ทีมเหย้า",
                        min_value=0,
                        step=1,
                        value=val_h,
                        key=f"h_{match_id}"
                    )
                with col2:
                    pred_a = st.number_input(
                        label="⚽ สกอร์ทีมเยือน",
                        min_value=0,
                        step=1,
                        value=val_a,
                        key=f"a_{match_id}"
                    )
                
                pred_q_choice = "ยังไม่ได้เลือกผู้เข้ารอบ"
                pred_q = ""
                if is_knockout:
                    st.markdown("<div style='margin-top: 10px; margin-bottom: 5px; border-top: 1px dashed rgba(212, 175, 55, 0.3); padding-top: 8px;'></div>", unsafe_allow_html=True)
                    # หาอินเดกซ์เริ่มต้นของทีมเข้ารอบจากคำทายเก่า หรือบังคับให้เป็นว่างเพื่อให้ผู้เล่นเลือกเองโดยไม่มีการทายออโต้ค้างไว้
                    default_index = 0
                    if default_q == home:
                        default_index = 1
                    elif default_q == away:
                        default_index = 2
                    
                    def format_qualify_team(val):
                        if val == "ยังไม่ได้เลือกผู้เข้ารอบ":
                            return "⚪ ยังไม่ได้เลือกผู้เข้ารอบ"
                        return get_team_display(val)
                    
                    pred_q_choice = st.radio(
                        "🏆 **GOLDEN BONUS: ทายทีมที่ได้เข้ารอบต่อไป (รวมต่อเวลา/จุดโทษ) ได้สะสม +1 แต้ม**",
                        options=["ยังไม่ได้เลือกผู้เข้ารอบ", home, away],
                        format_func=format_qualify_team,
                        index=default_index,
                        horizontal=True,
                        key=f"q_{match_id}"
                    )
                    if pred_q_choice != "ยังไม่ได้เลือกผู้เข้ารอบ":
                        pred_q = pred_q_choice
                
                with col3:
                    st.markdown("<div class='desktop-spacer' style='height: 28px;'></div>", unsafe_allow_html=True)
                    if has_pred:
                        btn_label = "✅ บันทึกแล้ว (แก้ไข)"
                        btn_type = "primary"
                    else:
                        btn_label = "บันทึกผลทาย"
                        btn_type = "secondary"
                        
                    # ใช้ปุ่ม st.form_submit_button แทน st.button สำหรับส่วนประกอบภายใน st.form
                    if st.form_submit_button(btn_label, use_container_width=True, type=btn_type):
                        if is_knockout and pred_q_choice == "ยังไม่ได้เลือกผู้เข้ารอบ":
                            st.error("⚠️ **คุณยังไม่ได้เลือกฝั่งเข้ารอบ (Golden Bonus)! กรุณาเลือกทีมที่เข้ารอบถัดไปก่อนบันทึกผลนะครับ**")
                        else:
                            try:
                                db.save_prediction(username, match_id, pred_h, pred_a, pred_q)
                                st.toast(f"⚽ บันทึกผลทาย {home_display} vs {away_display} เรียบร้อยแล้ว!")
                                st.rerun()
                            except Exception as e:
                                err_str = str(e)
                                if "429" in err_str or "quota" in err_str.lower() or "limit" in err_str.lower():
                                    st.warning("⚠️ **ระบบหนาแน่นชั่วคราว (Google Sheets Quota)** กรุณาเว้นระยะ 10-30 วินาที แล้วลองกดบันทึกใหม่อีกครั้งนะครับ 😊")
                                else:
                                    st.error(f"❌ **เกิดข้อผิดพลาดในการบันทึกข้อมูล:** {err_str}")
                        
                    if has_pred:
                        st.markdown("<div style='color: #4CAF50; font-size: 0.95rem; font-weight: bold; margin-top: 6px; text-align: center;'>✅ บันทึกผลทายแล้ว</div>", unsafe_allow_html=True)
        else:
            # หากโดนล็อกแล้ว (ปิดรับทายหรือเกมแข่งจบแล้ว) เรนเดอร์แบบธรรมดาด้วย st.container() โดยไม่ต้องใช้ st.form()
            with st.container():
                st.subheader(f"{home_display} 🆚 {away_display}")
                st.caption(f"⏰ เวลาเตะ: {m_time.strftime('%d/%m/%Y %H:%M')}")
                
                col1, col2, col3 = st.columns([3, 3, 2])
                with col1:
                    st.number_input(
                        label="⚽ สกอร์ทีมเหย้า",
                        min_value=0,
                        step=1,
                        value=val_h,
                        key=f"h_{match_id}",
                        disabled=True
                    )
                with col2:
                    st.number_input(
                        label="⚽ สกอร์ทีมเยือน",
                        min_value=0,
                        step=1,
                        value=val_a,
                        key=f"a_{match_id}",
                        disabled=True
                    )
                with col3:
                    st.markdown("<div class='desktop-spacer' style='height: 28px;'></div>", unsafe_allow_html=True)
                    if status == 'Finished':
                        st.warning("🏁 สิ้นสุดการแข่งขัน")
                        h_score_val = safe_int(row['home_score'])
                        a_score_val = safe_int(row['away_score'])
                        winner_name = home if h_score_val > a_score_val else (away if a_score_val > h_score_val else "เสมอ")
                        winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                        st.info(f"🏆 **ชนะ:** {winner_display} ({h_score_val}-{a_score_val})")
                        if row['scorers']: st.caption(f"⚽ **คนยิง:** {row['scorers']}")
                        if has_pred:
                            st.info(f"🎯 **คุณทายผลไว้:** {safe_int(default_h)} - {safe_int(default_a)}")
                        else:
                            st.info("🎯 **คุณไม่ได้ทายคู่นี้ไว้**")
                    else:
                        st.warning("🔒 ปิดรับผลทาย")
                        if has_pred:
                            st.info(f"🎯 **คุณทายผลไว้:** {safe_int(default_h)} - {safe_int(default_a)}")
                
                # แสดงผลการทายโบนัสและการเข้ารอบจริง
                if is_knockout:
                    st.markdown("<div style='margin-top: 10px; margin-bottom: 5px; border-top: 1px dashed rgba(212, 175, 55, 0.25); padding-top: 8px;'></div>", unsafe_allow_html=True)
                    cb1, cb2 = st.columns(2)
                    with cb1:
                        if has_pred and default_q != "":
                            st.info(f"🏆 **คุณทายผู้เข้ารอบ:** {get_team_display(default_q)}")
                        else:
                            st.info("🏆 **ไม่ได้รับบันทึกทายโบนัส**")
                    with cb2:
                        w_qualify = str(row.get('winner_qualify', '')).strip()
                        if status == 'Finished' and w_qualify != "" and w_qualify.lower() != 'nan':
                            st.success(f"👑 **ผู้เข้ารอบจริง:** {get_team_display(w_qualify)}")
                        else:
                            st.info("⏳ รอผลทีมเข้ารอบถัดไป")
        st.divider()

    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    if not finished.empty:
        with st.expander("🏁 ดูผลการแข่งขันนัดก่อนหน้าที่สิ้นสุดลงแล้ว (คลิกเพื่อขยายดู)"):
            for _, row in finished.iterrows():
                render_match(row, username)

    upcoming = all_matches[all_matches['status'] != 'Finished'].sort_values('match_time')
    if not upcoming.empty:
        # แสดงตารางการแข่งขันที่กำลังจะมาถึงทั้งหมดโดยจัดกลุ่มตามวัน
        unique_dates = upcoming['match_dt'].dt.date.unique()
        for d in unique_dates:
            now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
            today = now_th.date()
            tomorrow = today + pd.Timedelta(days=1)
            day_after = today + pd.Timedelta(days=2)
            
            label_suffix = ""
            if d == today:
                label_suffix = " (วันนี้)"
            elif d == tomorrow:
                label_suffix = " (วันพรุ่งนี้)"
            elif d == day_after:
                label_suffix = " (วันมะรืนนี้)"
                
            fifa_label = ""
            if d.strftime('%d/%m/%Y') == "24/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 23 มิ.ย.)"
            elif d.strftime('%d/%m/%Y') == "25/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 24 มิ.ย.)"
            elif d.strftime('%d/%m/%Y') == "26/06/2026":
                fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 25 มิ.ย.)"
                
            st.markdown(f"### <span class='bouncing-icon'>⚽</span> ตารางแข่งขันวันที่ {d.strftime('%d/%m/%Y')}{label_suffix}{fifa_label}", unsafe_allow_html=True)
            day_matches = upcoming[upcoming['match_dt'].dt.date == d]
            for _, row in day_matches.iterrows():
                render_match(row, username)
    else:
        st.info("ไม่มีการแข่งขันที่กำลังจะมาถึงในขณะนี้ครับ")

# 3. หน้าผลการแข่งขันย้อนหลัง (Match Results - Championship Golden Upgrade)
elif menu == "ผลการแข่งขันย้อนหลัง (Match Results)":
    st.markdown("""
    <div class="premium-results-header">
        <div class="premium-results-title">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" style="fill: #ffd700; filter: drop-shadow(0 0 6px rgba(255,215,0,0.45)); margin-right: 12px; flex-shrink: 0;"><path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v3c0 2.44 1.72 4.44 4 4.9V19H5v2h14v-2h-2v-4.1c2.28-.46 4-2.46 4-4.9V7c0-1.1-.9-2-2-2zM5 10V7h2v3H5zm14 0h-2V7h2v3z"/></svg>
            <span>ผลการแข่งขันย้อนหลังทั้งหมด</span>
        </div>
        <div class="premium-results-subtitle">
            <span class="gold-sparkle">✨</span> รวบรวมข้อมูลผลสกอร์และรายชื่อผู้ทำประตูในทุกแมตช์ที่จบการแข่งขันแล้วในเกียรติยศแห่งแชมเปี้ยน
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # สไตล์ CSS เพิ่มเติมสำหรับธีมทองพรีเมียม (Gold Accents & Golden Champion Style)
    st.markdown("""
    <style>
    /* สไตล์แถบคาดวันที่สีทองหรูหราแบบกรอบทองบางประกายเรืองแสง (Championship Premium Glassy Header) */
    .gold-date-header {
        background: rgba(18, 30, 22, 0.92); /* ปรับทึบขึ้นเพื่อป้องกันบั๊กภาพเบลอลามจาก backdrop-filter ของเบราว์เซอร์ */
        color: #ffd700;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-top: 30px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Kanit', sans-serif;
        border: 1px solid rgba(212, 175, 55, 0.35);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        z-index: 5;
    }
    .gold-date-header:hover {
        border-color: rgba(212, 175, 55, 0.6);
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.12);
        background: rgba(24, 40, 30, 0.95);
    }
    
    /* สไตล์หัวข้อหลักหน้าผลการแข่งขัน (Premium Results Page Header - Glassmorphic Gold Thin Border) */
    .premium-results-header {
        background: rgba(18, 30, 22, 0.90); /* ปรับทึบขึ้นเพื่อป้องกันบั๊กภาพเบลอลามจาก backdrop-filter ของเบราว์เซอร์ */
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 16px;
        padding: 20px 24px;
        margin-top: 5px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        position: relative;
        z-index: 5;
    }
    .premium-results-header:hover {
        border-color: rgba(212, 175, 55, 0.45);
        box-shadow: 0 6px 24px rgba(212, 175, 55, 0.08);
        background: rgba(22, 38, 27, 0.95);
    }
    .premium-results-title {
        display: flex;
        align-items: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffd700;
        margin-bottom: 6px;
        font-family: 'Kanit', sans-serif;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.15);
    }
    .premium-results-subtitle {
        color: #e2e8f0;
        font-size: 0.9rem;
        line-height: 1.45;
        font-family: 'Kanit', sans-serif;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .gold-sparkle {
        color: #ffd700;
        display: inline-block;
        font-weight: bold;
    }
    
    /* สไตล์การ์ดแมตช์ขอบทองเรืองแสง (Championship Premium Card) */
    .gold-match-card {
        background: rgba(15, 28, 19, 0.88);
        border: 1.5px solid #d4af37;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.08);
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: 'Kanit', sans-serif;
        position: relative;
        overflow: hidden;
        z-index: 5;
    }
    .gold-match-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.30);
        border-color: #f1c40f;
    }
    
    /* ปลอกแสงสว่างวาบขอบมุมการ์ด */
    .gold-match-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -150%;
        width: 50%;
        height: 100%;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,215,0,0.15) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-25deg);
        transition: 0.75s;
    }
    .gold-match-card:hover::before {
        left: 150%;
        transition: 0.75s;
    }

    .match-card-grid {
        display: grid;
        grid-template-columns: 1fr 140px 1fr;
        align-items: center;
        text-align: center;
        gap: 10px;
    }
    
    .team-side {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* ธงชาติสะบัดสง่างามขนาดใหญ่ */
    .team-flag-gold {
        font-size: 2.3rem;
        filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.4)) drop-shadow(0 0 2px rgba(212, 175, 55, 0.4));
        line-height: 1;
        margin-bottom: 8px;
    }
    
    .team-name-gold {
        font-size: 1.22rem;
        font-weight: 700;
        color: #e2e8f0;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }
    
    /* ป้ายผู้ชนะขอบทองคำเรืองแสง */
    .team-winner-badge {
        color: #ffd700;
        font-size: 0.78rem;
        font-weight: bold;
        margin-top: 8px;
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(139, 101, 8, 0.1) 100%);
        padding: 3px 12px;
        border-radius: 20px;
        border: 1px solid rgba(212, 175, 55, 0.5);
        display: inline-flex;
        align-items: center;
        gap: 4px;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 6px rgba(212,175,55,0.15);
    }
    
    /* สกอร์สีทองสว่าง */
    .score-gold {
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff3a1 0%, #ffd700 30%, #cca01d 70%, #997300 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 3px 10px rgba(212, 175, 55, 0.4));
        font-family: 'Outfit', 'Arial Black', sans-serif;
        letter-spacing: 2px;
        line-height: 1;
    }
    
    .match-time-gold {
        font-size: 0.76rem;
        color: #a0aec0;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* รายชื่อผู้ทำประตู (Scorers Grid) */
    .scorers-container-gold {
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px dashed rgba(212, 175, 55, 0.25);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .scorers-title-gold {
        font-size: 0.8rem;
        color: #92a498;
        margin-bottom: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .scorers-list-gold {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 16px;
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .scorer-item-gold {
        font-size: 0.88rem;
        color: #e2e8f0;
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.04);
        padding: 4px 12px;
        border-radius: 8px;
        border: 1px solid rgba(212, 175, 55, 0.1);
    }
    
    .scorer-icon-gold {
        color: #ffd700;
        filter: drop-shadow(0 0 3px rgba(255, 215, 0, 0.6));
    }
    
    .scorer-time-gold {
        color: #f1c40f;
        font-weight: 700;
        font-size: 0.82rem;
    }

    /* ========================================================================= */
    /* 🌟 CRITICAL SYSTEM OVERRIDES: บังคับปลดล็อกและเปิดระบบสกรอลแนวตั้งสำหรับหน้านี้ */
    /* ========================================================================= */
    
    /* ปลุกระดับคอนเทนเนอร์หลักส่วนเนื้อหาของ Streamlit ให้สกรอลแนวตั้งได้ฉลุยลื่นไหล โดยไม่ยุ่งเกี่ยวกับ Sidebar และโครงสร้างสากล */
    [data-testid="stAppViewContainer"] > section:nth-child(2), 
    .main {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        scrollbar-gutter: stable !important;
    }
    .main .block-container {
        overflow-y: visible !important;
        overflow-x: hidden !important;
        height: auto !important;
        max-height: none !important;
    }

    /* คืนสิทธิ์การตอบรับเมาส์เลื่อนให้แก่แผงคอนเทนเนอร์การแสดงผล */
    [data-testid="stAppViewContainer"] > section:nth-child(2) {
        pointer-events: auto !important;
    }

    /* 🌟 รักษาและสปอยล์ขนาดปุ่มเลื่อนสีทอง (Scrollbar Thumb) กว้าง 16px เด่นสะกดสายตา ติ๊กง่าย ลากลื่น 100% */
    [data-testid="stAppViewContainer"] > section:nth-child(2)::-webkit-scrollbar,
    .main::-webkit-scrollbar {
        width: 16px !important;
        height: 16px !important;
        display: block !important;
    }
    [data-testid="stAppViewContainer"] > section:nth-child(2)::-webkit-scrollbar-track,
    .main::-webkit-scrollbar-track {
        background: rgba(10, 20, 14, 0.65) !important;
        border-radius: 10px !important;
        border-left: 1px solid rgba(255, 215, 0, 0.1) !important;
    }
    [data-testid="stAppViewContainer"] > section:nth-child(2)::-webkit-scrollbar-thumb,
    .main::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ffd700 0%, #d4af37 50%, #b38820 100%) !important;
        border: 3px solid rgba(15, 28, 19, 0.95) !important;
        border-radius: 10px !important;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.3) !important;
    }
    [data-testid="stAppViewContainer"] > section:nth-child(2)::-webkit-scrollbar-thumb:hover,
    .main::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ffffff 0%, #ffd700 45%, #cfa32e 100%) !important;
        border: 2px solid rgba(15, 28, 19, 0.95) !important;
        box-shadow: 0 0 14px rgba(255, 215, 0, 0.6) !important;
    }
    </style>
    """,unsafe_allow_html=True)
    
    all_matches = db.get_matches()
    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    
    if finished.empty:
        st.info("ยังไม่มีการแข่งขันใดที่สิ้นสุดลงในขณะนี้ครับ")
    else:
        # จัดกลุ่มการแข่งขันย้อนหลังตามวันที่เตะเพื่อความเป็นระเบียบและให้เปิดดูง่าย
        finished['match_dt'] = pd.to_datetime(finished['match_time'])
        unique_dates = finished['match_dt'].dt.date.unique()
        
        for d in unique_dates:
            # ใช้แถบหัวข้อวันที่สีทองพรีเมียม (กรอบทองบางโปร่งแสงพร้อมไอคอนคู่ธีม)
            date_str = d.strftime('%d/%m/%Y')
            st.markdown(f"""
            <div class="gold-date-header">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" style="fill: #ffd700; flex-shrink: 0; filter: drop-shadow(0 0 5px rgba(255, 215, 0, 0.45));"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                <span style="letter-spacing: 0.6px; font-weight: 600; text-shadow: 0 0 8px rgba(255, 215, 0, 0.3);">วันที่ {date_str}</span>
            </div>
            """, unsafe_allow_html=True)
            
            day_matches = finished[finished['match_dt'].dt.date == d]
            
            for _, row in day_matches.iterrows():
                card_html = generate_gold_match_card(row)
                st.markdown(card_html, unsafe_allow_html=True)
                
            st.divider()

elif menu == "ตารางคะแนนกลุ่ม (Standings)":
    st.header("🏅 ตารางคะแนนแบ่งกลุ่มศึกฟุตบอลโลก 2026")
    st.info("💡 **กฎการเข้ารอบน็อกเอาต์ (รอบ 32 ทีมสุดท้าย):**\n- 🟢 อันดับ 1 และ 2 ของทุกกลุ่ม (A ถึง L) เข้ารอบโดยอัตโนมัติ (รวม 24 ทีม)\n- 🟡 ทีมอันดับ 3 ที่มีผลงานดีที่สุด 8 ทีม จากทั้ง 12 กลุ่ม จะได้รับตั๋วเข้ารอบเช่นกัน!")
    st.markdown("---")
    
    # ดึงข้อมูลตารางคะแนนจากหลังบ้าน (ดึงผ่าน Cache เพื่อเพิ่มความเร็วสายฟ้าแลบ)
    with st.spinner("🔄 กำลังดึงตารางคะแนนเรียลไทม์จากระบบสากล..."):
        standings = get_cached_world_cup_standings()
        
    if not standings:
        st.error("⚠️ ไม่สามารถดึงข้อมูลตารางคะแนนได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง")
    else:
        # แทรก CSS สำหรับแต่งตารางให้พรีเมี่ยม
        st.markdown("""
        <style>
        .standings-table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(30, 45, 36, 0.3) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            color: #e0e6ed !important;
            font-family: 'Kanit', sans-serif !important;
            margin-bottom: 5px !important;
        }
        .standings-table th {
            background: rgba(20, 32, 24, 0.85) !important;
            color: #ffd700 !important;
            font-weight: 600 !important;
            padding: 8px 2px !important;
            text-align: center !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-bottom: 2px solid rgba(255, 215, 0, 0.15) !important;
            font-size: 0.76rem !important;
            line-height: 1.25 !important;
            white-space: nowrap !important; /* บังคับตัวหนังสือหัวข้อเรียงบรรทัดเดียวกัน ห้ามแตกตัวแนวตั้ง */
        }
        .standings-table td {
            padding: 8px 4px !important;
            text-align: center !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            font-size: 0.84rem !important;
        }
        .standings-table tr:hover {
            background-color: rgba(255, 215, 0, 0.08) !important;
        }
        .standings-table .team-cell {
            text-align: left !important;
            font-weight: 500 !important;
            color: #ffffff !important;
            padding-left: 10px !important;
        }
        .standings-table .qualified-glow {
            background: rgba(46, 204, 113, 0.06) !important;
        }
        .standings-table .qualified-glow td {
            border: 1px solid rgba(46, 204, 113, 0.15) !important;
        }
        .standings-table .qualified-warning {
            background: rgba(241, 196, 15, 0.04) !important;
        }
        .standings-table .qualified-warning td {
            border: 1px solid rgba(241, 196, 15, 0.12) !important;
        }
        .standings-table .pts-cell {
            font-weight: bold !important;
            color: #ffd700 !important;
        }
        /* ตกแต่งการ์ดตารางเปรียบเทียบอันดับ 3 เป็นกรอบทองเรืองแสงหรูหราพรีเมียม */
        .third-placed-gold-card {
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.04) 0%, rgba(15, 23, 18, 0.65) 100%) !important;
            padding: 20px !important;
            border-radius: 16px !important;
            border: 2.2px solid #ffd700 !important; /* ขอบทองคำสว่างชัดเจน */
            margin-bottom: 25px !important;
            overflow-x: auto !important;
            /* เงาเรืองแสงสีทองพรีเมียมแบบมีมิติไล่ระดับชั้นลึกตระการตา */
            box-shadow: 0 8px 32px rgba(255, 215, 0, 0.15), inset 0 0 15px rgba(255, 215, 0, 0.08) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .third-placed-gold-card:hover {
            border-color: #ffe066 !important; /* ทองสว่างขึ้นเมื่อเมาส์ชี้ผ่าน */
            box-shadow: 0 12px 40px rgba(255, 215, 0, 0.28), inset 0 0 20px rgba(255, 215, 0, 0.15) !important;
            transform: translateY(-2px) !important;
        }
        
        /* ตกแต่งการ์ดตารางกลุ่มปกติ (A-L) ให้ดูเป็นระเบียบสวยงาม */
        .normal-table-card {
            background: rgba(15, 23, 18, 0.55) !important;
            padding: 15px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 215, 0, 0.1) !important;
            margin-bottom: 20px !important;
            overflow-x: auto !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .normal-table-card:hover {
            border-color: rgba(255, 215, 0, 0.25) !important;
            box-shadow: 0 6px 20px rgba(255, 215, 0, 0.05) !important;
            transform: translateY(-1px) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # สร้างฟังก์ชันวาดตาราง HTML ในบล็อกนี้เพื่อความง่ายและปลอดภัย
        def render_html_table(df, title, is_third_placed=False):
            team_width = "25%" if is_third_placed else "33%"
            wrapper_class = "third-placed-gold-card" if is_third_placed else "normal-table-card"
            html_code = f"""<div class='{wrapper_class}'>
<h4 style='color: #ffd700; margin-top: 0; margin-bottom: 12px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>🏆 {title}</h4>
<table class='standings-table' style='width: 100%; table-layout: fixed;'>
<thead>
<tr>
<th style='width: 7%;'>อันดับ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pos</span></th>
{"<th style='width: 8%;'>กลุ่ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Grp</span></th>" if is_third_placed else ""}
<th style='text-align: left; width: {team_width}; padding-left: 10px;'>ทีมชาติ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Team</span></th>
<th style='width: 7%;'>แข่ง<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pld</span></th>
<th style='width: 7%;'>ชนะ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>W</span></th>
<th style='width: 7%;'>เสมอ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>D</span></th>
<th style='width: 7%;'>แพ้<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>L</span></th>
<th style='width: 7%;'>ได้<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GF</span></th>
<th style='width: 7%;'>เสีย<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GA</span></th>
<th style='width: 8%;'>+/-<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GD</span></th>
<th style='width: 10%;'>แต้ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pts</span></th>
</tr>
</thead>
<tbody>"""
            
            for idx, row in df.iterrows():
                pos = str(row['Pos']).strip()
                team_name = str(row['Team']).strip()
                team_display = get_team_display(team_name)
                
                # แยกธงและชื่อชาติเพื่อจัดระเบียบ UI ให้ไม่มีปัญหารอยต่อและการตัดบรรทัดใหม่
                parts = team_display.split(" ", 1)
                if len(parts) == 2:
                    flag_emoji, clean_thai_name = parts[0], parts[1]
                else:
                    flag_emoji, clean_thai_name = "🏳️", team_display
                
                # ตกแต่งแถวตามสถานการณ์เข้ารอบ
                row_class = ""
                badge = ""
                if is_third_placed:
                    try:
                        pos_num = int(pos)
                        if pos_num <= 8:
                            row_class = "qualified-glow"
                            badge = " <span style='color: #2ecc71; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[เข้ารอบ]</span>"
                        else:
                            row_class = ""
                            badge = " <span style='color: #e74c3c; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[ตกรอบ]</span>"
                    except:
                        pass
                else:
                    if pos == "1" or pos == "2":
                        row_class = "qualified-glow"
                        badge = " <span style='color: #2ecc71; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[เข้ารอบ]</span>"
                    elif pos == "3":
                        row_class = "qualified-warning"
                        badge = " <span style='color: #f1c40f; font-size: 0.72rem; font-weight: bold; margin-left: auto; padding-left: 5px; white-space: nowrap;'>[ลุ้นอันดับ 3]</span>"
                    else:
                        row_class = ""
                        badge = ""
                        
                html_code += f"<tr class='{row_class}'>"
                html_code += f"<td><b>{pos}</b></td>"
                if is_third_placed:
                    grp = str(row.get('Grp', '')).strip()
                    html_code += f"<td><span style='background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;'><b>{grp}</b></span></td>"
                    
                html_code += f"""<td class='team-cell'>
<div style='display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden;'>
<span style='font-size: 1.15rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); line-height: 1; display: inline-block;'>{flag_emoji}</span>
<span style='font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;' title='{clean_thai_name}'>{clean_thai_name}</span>
{badge}
</div>
</td>"""
                html_code += f"<td>{row['Pld']}</td>"
                html_code += f"<td>{row['W']}</td>"
                html_code += f"<td>{row['D']}</td>"
                html_code += f"<td>{row['L']}</td>"
                html_code += f"<td>{row['GF']}</td>"
                html_code += f"<td>{row['GA']}</td>"
                
                # ตกแต่งสีสันของผลต่างประตูได้เสีย (+ เป็นเขียว, - เป็นแดง)
                gd = str(row['GD']).strip()
                gd_style = "color: #e0e6ed;"
                if gd.startswith('+'):
                    gd_style = "color: #2ecc71; font-weight: bold;"
                elif gd.startswith('-') or gd.startswith('−'):
                    gd_style = "color: #e74c3c; font-weight: bold;"
                html_code += f"<td><span style='{gd_style}'>{gd}</span></td>"
                
                html_code += f"<td class='pts-cell'>{row['Pts']}</td>"
                html_code += f"</tr>"
                
            html_code += """</tbody></table></div>"""
            return html_code

        # สร้างแท็บย่อยสลับดูตารางคะแนนแบบสวยงาม (เพิ่มแท็บที่ 5 สรุปทีมเข้ารอบชัวร์ๆ ตามสั่งคุณอาร์ต)
        t1, t2, t3, t4, t5 = st.tabs(["🔥 กลุ่ม A - D", "⚡ กลุ่ม E - H", "🌟 กลุ่ม I - L", "🏅 ทีมอันดับ 3 ที่ดีที่สุด", "🏆 สรุปทีมเข้ารอบ 32 ทีม (Qualified)"])
        
        with t1:
            col1, col2 = st.columns(2)
            with col1:
                if "Group A" in standings:
                    st.markdown(render_html_table(standings["Group A"], "กลุ่ม A"), unsafe_allow_html=True)
                if "Group C" in standings:
                    st.markdown(render_html_table(standings["Group C"], "กลุ่ม C"), unsafe_allow_html=True)
            with col2:
                if "Group B" in standings:
                    st.markdown(render_html_table(standings["Group B"], "กลุ่ม B"), unsafe_allow_html=True)
                if "Group D" in standings:
                    st.markdown(render_html_table(standings["Group D"], "กลุ่ม D"), unsafe_allow_html=True)
                    
        with t2:
            col1, col2 = st.columns(2)
            with col1:
                if "Group E" in standings:
                    st.markdown(render_html_table(standings["Group E"], "กลุ่ม E"), unsafe_allow_html=True)
                if "Group G" in standings:
                    st.markdown(render_html_table(standings["Group G"], "กลุ่ม G"), unsafe_allow_html=True)
            with col2:
                if "Group F" in standings:
                    st.markdown(render_html_table(standings["Group F"], "กลุ่ม F"), unsafe_allow_html=True)
                if "Group H" in standings:
                    st.markdown(render_html_table(standings["Group H"], "กลุ่ม H"), unsafe_allow_html=True)
                    
        with t3:
            col1, col2 = st.columns(2)
            with col1:
                if "Group I" in standings:
                    st.markdown(render_html_table(standings["Group I"], "กลุ่ม I"), unsafe_allow_html=True)
                if "Group K" in standings:
                    st.markdown(render_html_table(standings["Group K"], "กลุ่ม K"), unsafe_allow_html=True)
            with col2:
                if "Group J" in standings:
                    st.markdown(render_html_table(standings["Group J"], "กลุ่ม J"), unsafe_allow_html=True)
                if "Group L" in standings:
                    st.markdown(render_html_table(standings["Group L"], "กลุ่ม L"), unsafe_allow_html=True)
                    
        with t4:
            # 1. แถบชี้แจงระดับพรีเมียมสีทองเรืองแสง (Premium Info Card) ช่วยคลายความสับสนตามคำแนะนำของคุณอาร์ต
            st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(255, 215, 0, 0.05) 0%, rgba(15, 23, 18, 0.75) 100%); padding: 18px; border-radius: 14px; border: 1.8px solid #ffd700; box-shadow: 0 4px 20px rgba(255, 215, 0, 0.1), inset 0 0 12px rgba(255, 215, 0, 0.05); margin-bottom: 25px;'>
                    <h4 style='color: #ffd700; margin-top: 0; margin-bottom: 8px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>💡 ทำไมตารางนี้ไม่มีทีมยักษ์ใหญ่อย่าง ฝรั่งเศส, อังกฤษ หรือสเปน?</h4>
                    <p style='color: #e0e6ed; font-size: 0.86rem; line-height: 1.5; margin: 0;'>
                        เนื่องจากทีมชั้นยอดที่ได้ <b>อันดับ 1 (แชมป์กลุ่ม) และอันดับ 2 (รองแชมป์กลุ่ม)</b> ของแต่ละกลุ่ม (A ถึง L) ได้สิทธิ์ <b>ผ่านเข้ารอบ 32 ทีมสุดท้ายโดยตรงทันที</b> เรียบร้อยแล้ว! 
                        ดังนั้น ตารางด้านล่างนี้จึงเป็น <b>"ตารางเปรียบเทียบอันดับ 3"</b> เพื่อหา 8 ทีมที่มีผลงานดีที่สุดไปสมทบเท่านั้น 
                        คุณอาร์ตสามารถเลื่อนลงไปดูรายชื่อทีมแกร่งเหล่านั้นได้ที่ตาราง <b>"👑 ทีมชั้นนำที่ผ่านเข้ารอบโดยตรงแล้ว"</b> ที่อยู่ด้านล่างหน้าจอเดียวกันนี้ หรือสลับดูแท็บย่อยที่ 5 ได้เลยครับ
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if "Third-placed" in standings:
                st.markdown(render_html_table(standings["Third-placed"], "ตารางเปรียบเทียบอันดับ 3 (คัดเลือก 8 ทีมที่ดีที่สุดเข้ารอบ)", is_third_placed=True), unsafe_allow_html=True)
            else:
                st.info("ยังไม่มีข้อมูลการเปรียบเทียบทีมอันดับ 3 ในขณะนี้")
                
            st.markdown("<br><hr style='border: 1px solid rgba(255, 255, 255, 0.05);'><br>", unsafe_allow_html=True)
            
            # 2. เพิ่มตารางสรุป "ทีมชั้นยอดที่ผ่านเข้ารอบโดยตรงแล้ว (Directly Qualified - Top Teams)"
            st.markdown("""
                <div style='margin-bottom: 15px;'>
                    <h3 style='color: #2ecc71; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px; margin-bottom: 5px;'>👑 ทีมชั้นนำที่ผ่านเข้ารอบน็อกเอาต์โดยตรงแล้ว (อันดับ 1 & 2)</h3>
                    <p style='color: #a0aec0; font-size: 0.84rem; margin-top: 0;'>รายชื่อทีมชาติผลงานสุดแกร่งที่ได้อันดับ 1 และ 2 ของแต่ละกลุ่ม (Group A-L) ซึ่งผ่านเข้ารอบโดยอัตโนมัติ ไม่ต้องลุ้นอันดับ 3</p>
                </div>
            """, unsafe_allow_html=True)
            
            # สกัดทีมอันดับ 1 และ 2 จากทุกกลุ่ม
            direct_teams = []
            for g in ["Group A", "Group B", "Group C", "Group D", "Group E", "Group F", "Group G", "Group H", "Group I", "Group J", "Group K", "Group L"]:
                if g in standings:
                    df_g = standings[g]
                    for _, row in df_g.iterrows():
                        pos = str(row['Pos']).strip()
                        if pos in ["1", "2"]:
                            direct_teams.append({
                                'Pos': pos,
                                'Grp': g.replace("Group ", ""),
                                'Team': row['Team'],
                                'Pld': row['Pld'],
                                'W': row['W'],
                                'D': row['D'],
                                'L': row['L'],
                                'GF': row['GF'],
                                'GA': row['GA'],
                                'GD': row['GD'],
                                'Pts': row['Pts']
                            })
            
            if direct_teams:
                import pandas as pd
                df_direct = pd.DataFrame(direct_teams)
                
                # แปลงคอลัมน์ตัวเลขเพื่อจัดเรียงประสิทธิภาพรอบแบ่งกลุ่มอย่างแม่นยำ
                df_direct['Pts_int'] = df_direct['Pts'].apply(safe_int)
                
                def parse_gd(val):
                    val_str = str(val).replace('+', '').replace('−', '-').replace('-', '-').strip()
                    try:
                        return int(val_str)
                    except:
                        return 0
                        
                df_direct['GD_int'] = df_direct['GD'].apply(parse_gd)
                df_direct['GF_int'] = df_direct['GF'].apply(safe_int)
                
                # เรียงลำดับจากผลงานสะสมสูงสุด: คะแนนสูงสุด -> ผลต่างได้เสียสูงสุด -> ยิงประตูได้มากที่สุด
                df_direct = df_direct.sort_values(by=['Pts_int', 'GD_int', 'GF_int'], ascending=[False, False, False]).reset_index(drop=True)
                
                # แสดงเป็นตาราง HTML สวยงามพรีเมียมเรืองแสงเขียวอ่อน
                html_direct = """<div class='normal-table-card' style='border: 1.8px solid rgba(46, 204, 113, 0.4); box-shadow: 0 4px 20px rgba(46, 204, 113, 0.05);'>
<h4 style='color: #2ecc71; margin-top: 0; margin-bottom: 12px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>✨ ตารางผลงานสโมสรชาติเข้ารอบน็อกเอาต์โดยตรง (24 ทีมแรก)</h4>
<table class='standings-table' style='width: 100%; table-layout: fixed;'>
<thead>
<tr>
<th style='width: 8%;'>อันดับ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Rank</span></th>
<th style='width: 8%;'>กลุ่ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Grp</span></th>
<th style='text-align: left; width: 28%; padding-left: 10px;'>ทีมชาติ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Team</span></th>
<th style='width: 12%;'>อันดับในกลุ่ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Group Pos</span></th>
<th style='width: 7%;'>แข่ง<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pld</span></th>
<th style='width: 7%;'>ชนะ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>W</span></th>
<th style='width: 7%;'>เสมอ<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>D</span></th>
<th style='width: 7%;'>แพ้<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>L</span></th>
<th style='width: 8%;'>+/-<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>GD</span></th>
<th style='width: 10%;'>แต้ม<br><span style='font-size: 0.66rem; opacity: 0.75; font-weight: normal;'>Pts</span></th>
</tr>
</thead>
<tbody>"""
                for idx, row in df_direct.iterrows():
                    rank = idx + 1
                    grp = row['Grp']
                    team_name = row['Team']
                    team_display = get_team_display(team_name)
                    group_pos = row['Pos']
                    
                    parts = team_display.split(" ", 1)
                    if len(parts) == 2:
                        flag_emoji, clean_thai_name = parts[0], parts[1]
                    else:
                        flag_emoji, clean_thai_name = "🏳️", team_display
                        
                    if group_pos == "1":
                        pos_badge = "<span style='color: #ffd700; background: rgba(255,215,0,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: bold;'>🥇 แชมป์กลุ่ม</span>"
                    else:
                        pos_badge = "<span style='color: #29b6f6; background: rgba(41,182,246,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-weight: bold;'>🥈 รองแชมป์</span>"
                        
                    html_direct += f"""<tr class='qualified-glow'>
<td><b>{rank}</b></td>
<td><span style='background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;'><b>{grp}</b></span></td>
<td class='team-cell'>
<div style='display: flex; align-items: center; gap: 6px; white-space: nowrap; overflow: hidden;'>
<span style='font-size: 1.15rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); line-height: 1; display: inline-block;'>{flag_emoji}</span>
<span style='font-weight: 500; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;' title='{clean_thai_name}'>{clean_thai_name}</span>
</div>
</td>
<td>{pos_badge}</td>
<td>{row['Pld']}</td>
<td>{row['W']}</td>
<td>{row['D']}</td>
<td>{row['L']}</td>"""
                    
                    gd = str(row['GD']).strip()
                    gd_style = "color: #e0e6ed;"
                    if gd.startswith('+'):
                        gd_style = "color: #2ecc71; font-weight: bold;"
                    elif gd.startswith('-') or gd.startswith('−'):
                        gd_style = "color: #e74c3c; font-weight: bold;"
                        
                    html_direct += f"<td><span style='{gd_style}'>{gd}</span></td>"
                    html_direct += f"<td class='pts-cell' style='font-weight: bold; color: #2ecc71;'>{row['Pts']}</td>"
                    html_direct += f"</tr>"
                    
                html_direct += "</tbody></table></div>"
                st.markdown(html_direct, unsafe_allow_html=True)
            else:
                st.info("ยังไม่มีข้อมูลทีมเข้ารอบโดยตรงในขณะนี้")
                
        with t5:
            st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(46, 204, 113, 0.05) 0%, rgba(15, 23, 18, 0.65) 100%); padding: 20px; border-radius: 16px; border: 2.2px solid #2ecc71; box-shadow: 0 8px 32px rgba(46, 204, 113, 0.15), inset 0 0 15px rgba(46, 204, 113, 0.08); margin-bottom: 25px;'>
                    <h3 style='color: #2ecc71; margin-top: 0; margin-bottom: 5px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>🏆 ทำเนียบทีมชาติผ่านเข้ารอบ 32 ทีมสุดท้าย</h3>
                    <p style='color: #e0e6ed; font-size: 0.88rem; margin-bottom: 12px;'>รายชื่อทีมชาติที่อยู่ในเกณฑ์ผ่านเข้าสู่รอบน็อกเอาต์ (Round of 32) ตามสถิติตารางคะแนนกลุ่มปัจจุบัน</p>
                    <div style='background: rgba(255, 255, 255, 0.05); border-left: 4px solid #f1c40f; padding: 10px 15px; border-radius: 4px; font-size: 0.8rem; line-height: 1.45; color: #ffd700;'>
                        <b>💡 หมายเหตุเรียลไทม์:</b> รายชื่อทีมชาติที่ปรากฏในทำเนียบนี้ เป็นการประมวลผลดึงจาก <b>ทีมชาติอันดับ 1 และอันดับ 2 ของแต่ละกลุ่ม ณ ปัจจุบัน</b> เพื่อจำลองสถานะชั่วคราวเท่านั้น (เนื่องจากรอบแบ่งกลุ่มยังแข่งขันไม่เสร็จสิ้นครบถ้วนทุกนัด บางทีมอาจสลับลำดับขึ้นมาแม้สถิติคณิตศาสตร์อาจตกรอบหรือยังไม่เข้ารอบอย่างเป็นทางการจริง) ข้อมูลทีมที่การันตีเข้ารอบ 100% ชัวร์ๆ จะสมบูรณ์แบบสูงสุดเมื่อทุกแมตช์ในรอบแบ่งกลุ่มแข่งจบและบันทึกคะแนนเสร็จสิ้นครบทุกกลุ่มแล้วครับ
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # สกัดทีมเข้ารอบแบบเรียลไทม์
            group_winners = []      # แชมป์กลุ่ม (Pos 1)
            group_runners_up = []   # รองแชมป์กลุ่ม (Pos 2)
            best_3rd_places = []    # อันดับ 3 ที่ดีที่สุด 8 ทีม
            
            for g in ["Group A", "Group B", "Group C", "Group D", "Group E", "Group F", "Group G", "Group H", "Group I", "Group J", "Group K", "Group L"]:
                if g in standings:
                    df_g = standings[g]
                    for _, row in df_g.iterrows():
                        pos = str(row['Pos']).strip()
                        pld = safe_int(row.get('Pld', 0))
                        pts = safe_int(row.get('Pts', 0))
                        team_n = str(row['Team']).strip()
                        
                        # กติกาเข้ารอบชัวร์ๆ: อันดับ 1 และ 2 ของกลุ่มเมื่อแข่งจบหรือการันตีเข้ารอบ
                        if pos == "1":
                            group_winners.append((g.replace("Group ", "กลุ่ม "), team_n, pts, pld))
                        elif pos == "2":
                            group_runners_up.append((g.replace("Group ", "กลุ่ม "), team_n, pts, pld))
                            
            if "Third-placed" in standings:
                df_third = standings["Third-placed"]
                for _, row in df_third.iterrows():
                    try:
                        pos = int(str(row['Pos']).strip())
                        if pos <= 8:
                            best_3rd_places.append((f"กลุ่ม {row.get('Grp', '').strip()}", str(row['Team']).strip(), safe_int(row.get('Pts', 0)), safe_int(row.get('Pld', 0))))
                    except:
                        pass
                        
            col_q1, col_q2, col_q3 = st.columns(3)
            
            with col_q1:
                st.markdown("""
                    <div style='background: rgba(15, 23, 18, 0.55); padding: 18px; border-radius: 12px; border: 1.5px solid #ffd700; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                        <h4 style='color: #ffd700; margin-top: 0; margin-bottom: 15px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>👑 แชมป์กลุ่ม (Group Winners)</h4>
                        <div style='display: flex; flex-direction: column; gap: 10px;'>
                """, unsafe_allow_html=True)
                
                if group_winners:
                    for grp, team, pts, pld in group_winners:
                        display = get_team_display(team)
                        st.markdown(f"""
                            <div style='display: flex; align-items: center; justify-content: space-between; background: rgba(255, 215, 0, 0.04); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255, 215, 0, 0.15);'>
                                <span style='font-size: 0.92rem; font-weight: 500; color: #ffffff;'>{display}</span>
                                <span style='font-size: 0.72rem; color: #ffd700; background: rgba(255,215,0,0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{grp} | {pts} Pts</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #718096; font-size: 0.88rem; text-align: center;'>ยังไม่มีข้อมูลสรุปแชมป์กลุ่ม</p>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)
                
            with col_q2:
                st.markdown("""
                    <div style='background: rgba(15, 23, 18, 0.55); padding: 18px; border-radius: 12px; border: 1.5px solid #29b6f6; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                        <h4 style='color: #29b6f6; margin-top: 0; margin-bottom: 15px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>🥈 รองแชมป์กลุ่ม (Runners-up)</h4>
                        <div style='display: flex; flex-direction: column; gap: 10px;'>
                """, unsafe_allow_html=True)
                
                if group_runners_up:
                    for grp, team, pts, pld in group_runners_up:
                        display = get_team_display(team)
                        st.markdown(f"""
                            <div style='display: flex; align-items: center; justify-content: space-between; background: rgba(41, 182, 246, 0.04); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(41, 182, 246, 0.15);'>
                                <span style='font-size: 0.92rem; font-weight: 500; color: #ffffff;'>{display}</span>
                                <span style='font-size: 0.72rem; color: #29b6f6; background: rgba(41,182,246,0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{grp} | {pts} Pts</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #718096; font-size: 0.88rem; text-align: center;'>ยังไม่มีข้อมูลสรุปรองแชมป์กลุ่ม</p>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)
                
            with col_q3:
                st.markdown("""
                    <div style='background: rgba(15, 23, 18, 0.55); padding: 18px; border-radius: 12px; border: 1.5px solid #2ecc71; height: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                        <h4 style='color: #2ecc71; margin-top: 0; margin-bottom: 15px; font-family: "Kanit", sans-serif; display: flex; align-items: center; gap: 8px;'>🏅 อันดับ 3 ที่ดีที่สุด (Best 3rd)</h4>
                        <div style='display: flex; flex-direction: column; gap: 10px;'>
                """, unsafe_allow_html=True)
                
                if best_3rd_places:
                    for grp, team, pts, pld in best_3rd_places:
                        display = get_team_display(team)
                        st.markdown(f"""
                            <div style='display: flex; align-items: center; justify-content: space-between; background: rgba(46, 204, 113, 0.04); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(46, 204, 113, 0.15);'>
                                <span style='font-size: 0.92rem; font-weight: 500; color: #ffffff;'>{display}</span>
                                <span style='font-size: 0.72rem; color: #2ecc71; background: rgba(46,204,113,0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;'>{grp} | {pts} Pts</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color: #718096; font-size: 0.88rem; text-align: center;'>ยังไม่มีข้อมูลสรุปอันดับ 3 ที่ดีที่สุด</p>", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)

# 4. หน้า Leaderboard
elif menu == "ทำเนียบแชมป์ (Leaderboard)":
    st.header("🏆 ทำเนียบยอดนักทายผล")
    st.info("💡 **กฎการให้คะแนน:**\n- ✅ ทายถูกฝั่ง: 1 คะแนน\n- 🎯 ทายถูกเป๊ะ (รวมเสมอ): 3 คะแนน\n- ❌ ทายผิด: 0 คะแนน")
    st.markdown("---")
    st.subheader("🌟 อันดับเกียรติยศสะสมรวม")
    leaderboard = db.get_leaderboard()
    if not leaderboard.empty:
        # หาคะแนนสะสมสูงสุดเรียงตามลำดับ (Unique Scores) เพื่อมอบรางวัลเหรียญทอง เงิน และทองแดงตามลำดับ
        top_scores = sorted(leaderboard['total_score'].unique(), reverse=True)
        gold_score = top_scores[0] if len(top_scores) > 0 else -1
        silver_score = top_scores[1] if len(top_scores) > 1 else -1
        bronze_score = top_scores[2] if len(top_scores) > 2 else -1
        
        leaderboard['อันดับ'] = range(1, len(leaderboard) + 1)
        
        # 🎨 สร้างระบบเรนเดอร์ตารางอันดับเกียรติยศ HTML/CSS สไตล์พรีเมียมเรืองแสงทองคำตระการตาตามความพึงพอใจของคุณอาร์ต
        def render_leaderboard_html(df):
            html_code = """<style>
/* กรอบสวรรค์ทองคำจำลอง แผ่ออร่าความเรืองแสงตระการตาชั้นสูง */
.leaderboard-gold-card {
    background: linear-gradient(180deg, rgba(255, 215, 0, 0.04) 0%, rgba(15, 23, 18, 0.65) 100%) !important;
    padding: 24px !important;
    border-radius: 20px !important;
    border: 2.5px solid #ffd700 !important; /* กรอบทองหนาพรีเมียมโดดเด่น */
    margin-top: 15px !important;
    margin-bottom: 25px !important;
    /* เงาเรืองแสงรอบตัว 3 มิติ ร่วมกับเงาเรืองสะท้อนด้านใน (inset) ป้องกันการถูกตัดขอบเหลี่ยมในทุกหน้าจอ */
    box-shadow: 0 10px 35px rgba(255, 215, 0, 0.18), inset 0 0 20px rgba(255, 215, 0, 0.08) !important;
    overflow-x: auto !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.leaderboard-gold-card:hover {
    box-shadow: 0 15px 45px rgba(255, 215, 0, 0.28), inset 0 0 25px rgba(255, 215, 0, 0.12) !important;
    border-color: #ffe066 !important;
    transform: translateY(-2px);
}
.leaderboard-table {
    width: 100%;
    border-collapse: collapse !important;
    font-family: 'Kanit', sans-serif !important;
    color: #f1f5f9 !important;
}
.leaderboard-table th {
    background: rgba(20, 32, 24, 0.9) !important;
    color: #ffd700 !important;
    font-weight: 600 !important;
    padding: 14px 10px !important;
    text-align: center !important;
    border-bottom: 2.5px solid rgba(255, 215, 0, 0.3) !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px;
    white-space: nowrap !important;
}
.leaderboard-table td {
    padding: 14px 10px !important;
    text-align: center !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    font-size: 0.98rem !important;
}
.leaderboard-table tr:hover {
    background-color: rgba(255, 215, 0, 0.08) !important;
}

/* พื้นหลังและแถบข้างเรืองแสงตามระดับเกียรติยศ */
.row-rank-1 {
    background: rgba(255, 215, 0, 0.12) !important;
    font-weight: bold !important;
    border-left: 5px solid #ffd700 !important;
}
.row-rank-2 {
    background: rgba(192, 192, 192, 0.08) !important;
    font-weight: bold !important;
    border-left: 5px solid #c0c0c0 !important;
}
.row-rank-3 {
    background: rgba(205, 127, 50, 0.06) !important;
    font-weight: bold !important;
    border-left: 5px solid #cd7f32 !important;
}

/* ป้ายตราเกียรติยศอันดับ 1-3 ดีไซน์นูนต่ำลอยตัว 3D */
.badge-rank-1 {
    background: linear-gradient(135deg, #ffe066 0%, #ffd700 100%) !important;
    color: #0d1510 !important;
    padding: 4px 12px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 3px 8px rgba(255, 215, 0, 0.35) !important;
    display: inline-block;
}
.badge-rank-2 {
    background: linear-gradient(135deg, #ffffff 0%, #a3a3a3 100%) !important;
    color: #0d1510 !important;
    padding: 4px 12px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 3px 8px rgba(255, 255, 255, 0.25) !important;
    display: inline-block;
}
.badge-rank-3 {
    background: linear-gradient(135deg, #f0a25e 0%, #8f4d22 100%) !important;
    color: #ffffff !important;
    padding: 4px 12px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    box-shadow: 0 3px 8px rgba(143, 77, 34, 0.25) !important;
    display: inline-block;
}
</style>
<div class='leaderboard-gold-card'>
<table class='leaderboard-table'>
<thead>
    <tr>
        <th style='width: 15%;'>อันดับ<br><span style='font-size: 0.68rem; opacity: 0.75; font-weight: normal;'>Rank</span></th>
        <th style='text-align: left; padding-left: 20px;'>รายชื่อยอดนักทายผล<br><span style='font-size: 0.68rem; opacity: 0.75; font-weight: normal;'>Competitor</span></th>
        <th style='width: 25%;'>คะแนนสะสม<br><span style='font-size: 0.68rem; opacity: 0.75; font-weight: normal;'>Total Score</span></th>
    </tr>
</thead>
<tbody>"""
            
            for idx, row in df.iterrows():
                rank = row['อันดับ']
                username = row['username']
                score = row['total_score']
                
                row_class = ""
                rank_display = f"<b>{rank}</b>"
                
                if score > 0:
                    if score == gold_score:
                        row_class = "row-rank-1"
                        rank_display = f"<span class='badge-rank-1'>🥇 {rank}</span>"
                        user_display = f"👑 <b>{username}</b>"
                    elif score == silver_score:
                        row_class = "row-rank-2"
                        rank_display = f"<span class='badge-rank-2'>🥈 {rank}</span>"
                        user_display = f"⭐️ <b>{username}</b>"
                    elif score == bronze_score:
                        row_class = "row-rank-3"
                        rank_display = f"<span class='badge-rank-3'>🥉 {rank}</span>"
                        user_display = f"✨ <b>{username}</b>"
                    else:
                        user_display = f"👤 {username}"
                else:
                    user_display = f"👤 {username}"
                    
                html_code += f"""<tr class='{row_class}'>
    <td>{rank_display}</td>
    <td style='text-align: left; padding-left: 20px; font-weight: 500;'>{user_display}</td>
    <td style='font-weight: 700; color: #ffd700; font-size: 1.15rem; font-family: "Courier New", monospace;'>{score}</td>
</tr>"""
                
            html_code += """</tbody>
</table>
</div>"""
            return html_code

        # แสดงผลตาราง HTML สไตล์พรีเมียมจำลองลงบนหน้า Streamlit โดยทำความสะอาดช่องว่างนำหน้าเพื่อป้องกัน Markdown Bug
        raw_html = render_leaderboard_html(leaderboard)
        cleaned_html = "\n".join([line.strip() for line in raw_html.split("\n")])
        st.markdown(cleaned_html, unsafe_allow_html=True)


# 5. หน้าประวัติการทายผล (แยกออกมาตามคำปรึกษาคุณอาร์ต)
elif menu == "ประวัติการทายผล (My Predictions)":
    st.header("📑 ประวัติการทายผลการแข่งขัน")
    
    # 🎨 แทรก CSS (ซีเอสเอส: ภาษาที่ใช้ในการกำหนดรูปแบบการแสดงผลของหน้าเว็บ) เพื่อตกแต่งกรอบและการไฮไลท์แบบพรีเมียม
    st.markdown("""
        <style>
        /* ================================================================= */
        /* 0. ตกแต่งหัวข้อแท็บย่อย (st.tabs) ให้มีขอบมนและไฮไลท์กรอบเรืองแสงหรูหรา */
        /* ================================================================= */
        /* สั่งให้โครงสร้างแท็บทั้งหมดเปิดเผยเงาเรืองแสง ไม่โดนตัดขอบเป็นสี่เหลี่ยม */
        .stTabs, 
        div[data-testid="stTabs"],
        .stTabs [data-baseweb="tab-list"] {
            overflow: visible !important;
        }

        /* จัดระยะห่างของลิสต์แท็บให้สวยงาม และนำเส้นใต้พื้นหลังเดิมออก */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px !important;
            border-bottom: none !important; /* ปิดเส้นนอนใต้แท็บแบบเดิมถาวร */
            padding-bottom: 12px !important; /* เพิ่มช่องว่างด้านล่างเพื่อเว้นระยะห่าง */
        }

        /* ตกแต่งแท็บแต่ละอันในสถานะปกติ (Inactive) เป็นรูปทรงแคปซูลยาเม็ดพรีเมียม */
        .stTabs [data-baseweb="tab"] {
            border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 20px !important; /* ปรับเป็นขอบมนเต็มรูปแบบทรงแคปซูลลอยตัว */
            padding: 8px 24px !important;
            background-color: rgba(255, 255, 255, 0.02) !important;
            color: rgba(255, 255, 255, 0.6) !important;
            font-weight: 500 !important;
            font-size: 1.05rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        /* เอฟเฟกต์โฮเวอร์ (Hover) ของปุ่มแท็บ */
        .stTabs [data-baseweb="tab"]:hover {
            color: #ffffff !important;
            border-color: rgba(255, 215, 0, 0.4) !important;
            background-color: rgba(255, 215, 0, 0.05) !important;
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.05) !important;
        }

        /* ตกแต่งแท็บเมื่อถูกคลิกเลือกใช้งาน (Active) ด้วยขอบทองสว่างรอบตัว 100% */
        .stTabs [aria-selected="true"] {
            color: #ffd700 !important; /* อักษรและไอคอนสีทอง */
            border: 2px solid #ffd700 !important; /* ขอบทองสว่างชัดรอบด้าน 100% ครบทุกด้าน */
            border-radius: 20px !important;
            background: linear-gradient(180deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.03) 100%) !important;
            font-weight: 700 !important;
            /* ใช้เงานอกบางเบาสลัว ร่วมกับเงาเรืองแสงด้านใน (inset) เพื่อให้แผ่ออร่าหรูหรามีมิติโดยไม่มีวันโดนตัดขอบเหลี่ยม */
            box-shadow: 0 2px 6px rgba(255, 215, 0, 0.12), inset 0 0 10px rgba(255, 215, 0, 0.25) !important;
        }

        /* ซ่อนขีดไฮไลท์สไตล์ดั้งเดิมเพื่อไม่ให้รบกวนขอบทองของเรา */
        div[data-baseweb="tab-highlight"] {
            background-color: transparent !important;
        }
        div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* ================================================================= */
        /* 1. ตกแต่งครอบการ์ดผลแข่งเสร็จแล้ว (Match Card Wrapper) ด้วยกรอบหนาเรืองแสง */
        /* ================================================================= */
        .match-card-wrapper {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 14px !important;
            padding: 4px !important; /* เว้นระยะห่างรอบ expander เล็กน้อยให้เห็นกรอบโค้งเด่นชัด */
            margin-bottom: 16px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        .match-card-wrapper:hover {
            border-color: rgba(255, 215, 0, 0.5) !important; /* เปลี่ยนเป็นสีทองเรืองแสงเมื่อเมาส์ชี้ผ่าน */
            box-shadow: 0 6px 22px rgba(255, 215, 0, 0.2) !important;
            background-color: rgba(255, 255, 255, 0.04) !important;
            transform: translateY(-2px);
        }
        
        /* ซ่อนกรอบเดิมของ st.expander เพื่อป้องกันกรอบซ้อนและขัดแย้งกันในแต่ละเบราว์เซอร์ */
        div[data-testid="stExpander"], div.stExpander, .streamlit-expander {
            background-color: transparent !important;
            border: none !important;
            margin-bottom: 0px !important;
            box-shadow: none !important;
        }
        
        /* ตกแต่งส่วนหัวของ expander (ปุ่มสรุปข้อมูลแมตช์) */
        div[data-testid="stExpander"] > details > summary,
        div.stExpander > details > summary,
        .streamlit-expander > details > summary {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border-radius: 10px 10px 0 0 !important;
            padding: 14px 18px !important;
            color: #f8fafc !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            transition: color 0.2s ease !important;
        }
        
        div[data-testid="stExpander"] > details > summary:hover,
        div.stExpander > details > summary:hover,
        .streamlit-expander > details > summary:hover {
            color: #ffd700 !important; /* ตัวอักษรเปลี่ยนเป็นสีทองเมื่อโฮเวอร์ */
        }
        
        /* ตกแต่งเนื้อหาด้านในเมื่อขยาย expander ออกมา */
        div[data-testid="stExpander"] > details > div[role="region"],
        div.stExpander > details > div[role="region"],
        .streamlit-expander > details > div[role="region"] {
            padding: 20px !important;
            background-color: rgba(0, 0, 0, 0.25) !important;
            border-radius: 0 0 10px 10px !important;
        }

        /* ================================================================= */
        /* 2. ตกแต่งการ์ดผลทายล่วงหน้า (Upcoming Match Cards) ให้เด่นชัดพรีเมียม */
        /* ================================================================= */
        .upcoming-card {
            padding: 18px 22px;
            border-radius: 14px;
            margin-bottom: 15px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            box-sizing: border-box;
        }
        
        /* กรณีทายผลแล้ว: ดีไซน์สีฟ้าน้ำทะเล (Cyan/Aqua) */
        .upcoming-card.has-prediction {
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(0, 150, 255, 0.03) 100%);
            border: 1.5px solid rgba(0, 212, 255, 0.35) !important;
            box-shadow: 0 4px 15px rgba(0, 212, 255, 0.05) !important;
        }
        
        .upcoming-card.has-prediction:hover {
            border-color: rgba(0, 212, 255, 0.75) !important;
            box-shadow: 0 6px 22px rgba(0, 212, 255, 0.2) !important;
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.12) 0%, rgba(0, 150, 255, 0.05) 100%);
            transform: translateY(-2px);
        }
        
        /* กรณีที่ยังไม่ทายผล: ดีไซน์ขอบประสีส้มแดงเพื่อเตือนสายตา */
        .upcoming-card.no-prediction {
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.05) 0%, rgba(255, 107, 107, 0.02) 100%);
            border: 1.5px dashed rgba(255, 107, 107, 0.45) !important;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.02) !important;
        }
        
        .upcoming-card.no-prediction:hover {
            border-color: rgba(255, 107, 107, 0.8) !important;
            box-shadow: 0 6px 22px rgba(255, 107, 107, 0.15) !important;
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.08) 0%, rgba(255, 107, 107, 0.04) 100%);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.info("💡 เลือกดูสรุปผลการแข่งขันและการทายผลของเพื่อนๆ แยกตามวัน โดยคนที่ทายถูกเป๊ะได้รับ 3 แต้ม (สีทอง 🏆) และถูกฝั่งได้รับ 1 แต้ม (สีเขียว 🟢)")
    st.markdown("---")
    
    # ดึงข้อมูลแมตช์และคำทำนาย
    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])
    
    # สร้าง Tab แยกข้อมูล
    tab_finished, tab_upcoming = st.tabs(["🏁 ผลการทายที่แข่งเสร็จแล้ว", "🔮 ผลทายล่วงหน้าของคุณ"])
    
    with tab_finished:
        finished_matches = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
        if finished_matches.empty:
            st.info("ยังไม่มีผลการแข่งขันที่เสร็จสิ้นในขณะนี้ครับ")
        else:
            # ดึงประวัติการทายทั้งหมด
            predictions_df = db.get_predictions_df()
            
            # จัดกลุ่มตามวันแข่งขัน
            unique_dates = finished_matches['match_dt'].dt.date.unique()
            
            for d in unique_dates:
                date_str = d.strftime('%d/%m/%Y')
                st.subheader(f"🗓️ ผลแข่งขันประจำวันที่ {date_str}")
                day_matches = finished_matches[finished_matches['match_dt'].dt.date == d]
                
                for _, row_m in day_matches.iterrows():
                    m_id = str(row_m['id'])
                    home_team = row_m['home_team']
                    away_team = row_m['away_team']
                    h_real = safe_int(row_m['home_score'])
                    a_real = safe_int(row_m['away_score'])
                    real_win = (h_real > a_real) - (h_real < a_real)
                    
                    home_disp = get_team_display(home_team)
                    away_disp = get_team_display(away_team)
                    
                    expander_label = f"⚽ {home_disp}  {h_real} - {a_real}  {away_disp}"
                    
                    with st.expander(expander_label):
                        st.markdown(f"**⏰ เวลาแข่ง:** {pd.to_datetime(row_m['match_time']).strftime('%d/%m/%Y %H:%M น.')}")
                        if row_m['scorers']:
                            st.markdown(f"⚽ **ผู้ทำประตู:** {row_m['scorers']}")
                        
                        st.markdown("---")
                        st.markdown("**🎯 ผลการทายของผู้เล่นทั้งหมดในคู่นี้:**")
                        
                        m_preds = predictions_df[predictions_df['match_id'].astype(str) == m_id]
                        if m_preds.empty:
                            st.write("ยังไม่มีผู้เล่นใดทายผลคู่นี้ไว้ในระบบ")
                        else:
                            for _, row_p in m_preds.iterrows():
                                u_name = row_p['username']
                                p_h = safe_int(row_p['pred_home'])
                                p_a = safe_int(row_p['pred_away'])
                                pred_win = (p_h > p_a) - (p_h < p_a)
                                
                                # จัดการแสดงผลระบบโบนัสรอบน็อกเอาต์ (Golden Bonus: Match ID >= 68)
                                bonus_txt = ""
                                pred_q_txt = ""
                                m_id_int = safe_int(m_id)
                                if m_id_int >= 68:
                                    p_qualify = str(row_p.get('pred_qualify', '')).strip()
                                    if p_qualify == "":
                                        try:
                                            if p_h > p_a:
                                                p_qualify = str(row_m.get('home_team', '')).strip()
                                            elif p_a > p_h:
                                                p_qualify = str(row_m.get('away_team', '')).strip()
                                        except Exception:
                                            pass
                                    w_qualify = str(row_m.get('winner_qualify', '')).strip()
                                    if p_qualify:
                                        pred_q_txt = f" | 🗳️ เลือก {get_team_display(p_qualify)}"
                                    if w_qualify != "" and w_qualify.lower() != "nan":
                                        if p_qualify != "" and p_qualify.lower() == w_qualify.lower():
                                            bonus_txt = " <b style='color: #ffffff;'>+ 🌟 โบนัส 1 แต้ม</b>"
                                        else:
                                            bonus_txt = " <span style='color: #ffffff; opacity: 0.7;'>+ ❌ โบนัส 0 แต้ม</span>"
                                
                                # ตรวจแต้มทายผล
                                if p_h == h_real and p_a == a_real:
                                    pt_label = "🏆 ทายถูกตรงเป๊ะ! ได้ 3 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(153, 101, 21, 0.08) 100%);
                                    border: 1px solid rgba(255, 215, 0, 0.4);
                                    color: #FFD700;
                                    """
                                elif pred_win == real_win:
                                    pt_label = "🟢 ทายถูกฝั่ง! ได้ 1 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(46, 204, 113, 0.12) 0%, rgba(39, 174, 96, 0.06) 100%);
                                    border: 1px solid rgba(46, 204, 113, 0.3);
                                    color: #2ecc71;
                                    """
                                else:
                                    pt_label = "❌ ทายผิด! ได้ 0 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(231, 76, 60, 0.1) 0%, rgba(192, 57, 43, 0.05) 100%);
                                    border: 1px solid rgba(231, 76, 60, 0.22);
                                    color: #e74c3c;
                                    """
                                
                                st.markdown(
                                    f"""
                                    <div style='padding: 10px 15px; border-radius: 8px; margin-bottom: 6px; {card_style} font-size: 0.9rem; font-family: Kanit, sans-serif;'>
                                        👤 ผู้เล่น: <b>{u_name}</b> | ผลทาย: <b>{p_h} - {p_a}</b>{pred_q_txt} &nbsp;&nbsp;&nbsp;&nbsp; ({pt_label}{bonus_txt})
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                st.divider()

    with tab_upcoming:
        st.info("💡 หน้านี้แสดงข้อมูลเฉพาะสกอร์ที่คุณทายไว้ล่วงหน้าสำหรับคู่แข่งขันที่ยังไม่เริ่มเตะ เพื่อความปลอดภัยในการป้องกันการลอกเลียนแบบผลทายของกันและกันครับ")
        upcoming_matches = all_matches[all_matches['status'] != 'Finished'].sort_values('match_time')
        
        if upcoming_matches.empty:
            st.success("คุณเข้าร่วมการแข่งครบถ้วนหมดแล้ว ไม่มีคู่การแข่งขันล่วงหน้าค้างอยู่ครับ")
        else:
            user_preds = db.get_user_predictions(username)
            unique_dates_uc = upcoming_matches['match_dt'].dt.date.unique()
            
            for d in unique_dates_uc:
                date_str = d.strftime('%d/%m/%Y')
                
                # ตรวจป้าย วันนี้ / วันพรุ่งนี้ / วันมะรืนนี้
                now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
                today_d = now_th.date()
                tomorrow_d = today_d + pd.Timedelta(days=1)
                day_after_d = today_d + pd.Timedelta(days=2)
                
                label_suffix = ""
                if d == today_d:
                    label_suffix = " (วันนี้)"
                elif d == tomorrow_d:
                    label_suffix = " (วันพรุ่งนี้)"
                elif d == day_after_d:
                    label_suffix = " (วันมะรืนนี้)"
                
                fifa_label = ""
                if date_str == "24/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 23 มิ.ย.)"
                elif date_str == "25/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 24 มิ.ย.)"
                elif date_str == "26/06/2026":
                    fifa_label = " 🇺🇸 (ตรงกับโปรแกรมฟีฟ่าวันที่ 25 มิ.ย.)"
                
                st.subheader(f"🗓️ ตารางแข่งขันวันที่ {date_str}{label_suffix}{fifa_label}")
                day_matches = upcoming_matches[upcoming_matches['match_dt'].dt.date == d]
                
                for _, row_m in day_matches.iterrows():
                    m_id = row_m['id']
                    home_team = row_m['home_team']
                    away_team = row_m['away_team']
                    
                    has_pred = safe_int(m_id) in user_preds
                    home_disp = get_team_display(home_team)
                    away_disp = get_team_display(away_team)
                    
                    # แปลงเวลาเตะอย่างยืดหยุ่นและปลอดภัยจากประเภทข้อมูล Timestamp/String
                    m_time = row_m['match_dt'] if 'match_dt' in row_m and pd.notnull(row_m['match_dt']) else pd.to_datetime(row_m['match_time'])
                    if not isinstance(m_time, datetime):
                        m_time = m_time.to_pydatetime()
                    # ปิดรับทายผลล่วงหน้าก่อนเวลาแข่งขันจริง 1 ชั่วโมง หรือเมื่อบอลกำลังเตะ/แข่งจบแล้ว เพื่อป้องกันการลักไก่แก้ไขสกอร์
                    is_locked = now_th > (m_time - timedelta(hours=1)) or row_m['status'] in ['Finished', 'Live']
                    
                    if has_pred:
                        pred_h, pred_a, *extra = user_preds[safe_int(m_id)]
                        pred_text = f"🔥 ผลทายของคุณ: &nbsp;<b>{pred_h} - {pred_a}</b>"
                        card_class = "upcoming-card has-prediction"
                    else:
                        pred_text = "⚠️ คุณยังไม่ได้ทายผลคู่นี้"
                        card_class = "upcoming-card no-prediction"
                    
                    status_text = "🔒 ปิดรับผลทายแล้ว" if is_locked else "🔓 เปิดรับผลทาย (สามารถแก้ไขได้ที่หน้าแรก)"
                    st.markdown(
                        f"""
                        <div class='{card_class}'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <span style='font-size: 1.05rem; font-weight: bold;'>⚽ {home_disp} vs {away_disp}</span>
                                <span style='font-size: 0.85rem; color: #a0aec0;'>⏰ เวลาเตะ: {m_time.strftime('%H:%M น.')}</span>
                            </div>
                            <div style='margin-top: 10px; font-size: 1rem;'>
                                {pred_text}
                            </div>
                            <div style='margin-top: 8px; font-size: 0.8rem; color: #888;'>
                                สถานะ: {status_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# 4. หน้า Admin
elif menu == "ห้องควบคุมระบบ (Admin)":
    st.header("💎 ศูนย์ควบคุมการจัดการ (Director)")
    
    # ทางลัดเปิด Google Sheets
    st.sidebar.markdown("---")
    st.sidebar.link_button("🔗 เปิด Google Sheets (DB)", "https://docs.google.com/spreadsheets/d/1MWZoajy6xNEQunVccEqNcb4iV4124qRxrDS5pHLf57c/edit")
    
    # ส่วนการซิงค์ข้อมูลอัตโนมัติ
    st.subheader("🔄 ระบบซิงค์อัตโนมัติ")
    if st.button("ซิงค์ข้อมูลทีมและผลการแข่งขัน (Sync)"):
        with st.spinner("กำลังดึงข้อมูลล่าสุดจากระบบ..."):
            updated = db.sync_results_from_web()
            if updated > 0:
                st.success(f"✅ อัปเดตข้อมูลสำเร็จ! (พบการเปลี่ยนแปลง {updated} รายการ)")
                st.balloons()
            else:
                st.info("ℹ️ ข้อมูลเป็นปัจจุบันอยู่แล้วครับ")
    
    st.divider()
    st.subheader("⚡ ระบบเคลียร์แคชและบังคับอัปเดต (Force Flush)")
    if st.button("ล้างแคชระบบและรีดึงข้อมูลใหม่ทันที (Clear Cache)"):
        with st.spinner("กำลังทำการล้างแคช RAM ทั้งระบบ..."):
            db.get_gspread_client.clear()
            db.get_spreadsheet.clear()
            db.get_users_df.clear()
            db.get_matches.clear()
            db.get_predictions_df.clear()
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ ล้างแคช RAM และเชื่อมโยงข้อมูลสดใหม่เรียบร้อย!")
            st.rerun()

    st.divider()
    st.subheader("✍️ กรอกผลคะแนนด้วยตนเอง")
    matches = db.get_matches()
    upcoming = matches[matches['status'] != 'Finished']
    if not upcoming.empty:
        # สร้างแมปของชื่อเพื่อใช้เก็ตรวมข้อมูลแมตช์จริง
        match_map = {int(r['id']): r for i, r in upcoming.iterrows()}
        selected = st.selectbox("เลือกแมตช์:", [f"{r['id']}: {r['home_team']} vs {r['away_team']}" for i, r in upcoming.iterrows()])
        m_id = int(selected.split(":")[0])
        
        match_row = match_map[m_id]
        home_t = match_row['home_team']
        away_t = match_row['away_team']
        
        c1, c2 = st.columns(2)
        real_h = c1.number_input(f"สกอร์ {home_t}", min_value=0, step=1, key=f"admin_h_{m_id}")
        real_a = c2.number_input(f"สกอร์ {away_t}", min_value=0, step=1, key=f"admin_a_{m_id}")
        
        is_ko = m_id >= 68
        admin_winner = ""
        if is_ko:
            st.markdown("<div style='margin-top: 10px; margin-bottom: 5px; border-top: 1px dashed rgba(212, 175, 55, 0.3); padding-top: 8px;'></div>", unsafe_allow_html=True)
            # ตั้งทีมเข้ารอบเริ่มต้นเผื่อสกอร์ปกติมีคนชนะ
            def_winner_idx = 0
            if real_a > real_h:
                def_winner_idx = 1
            admin_winner = st.selectbox(
                "👑 ทีมผ่านเข้ารอบถัดไป (สำหรับนัดน็อกเอาต์ รวมต่อเวลา/จุดโทษ):",
                options=[home_t, away_t],
                index=def_winner_idx,
                key=f"admin_w_{m_id}"
            )
            
        if st.button("ยืนยันผล", key="admin_submit_btn"):
            with st.spinner("กำลังอัปเดตคะแนนลงระบบ..."):
                import sqlite3
                conn = sqlite3.connect('worldcup.db')
                if is_ko:
                    conn.execute("UPDATE matches SET home_score=?, away_score=?, status='Finished', winner_qualify=? WHERE id=?", (real_h, real_a, admin_winner, m_id))
                else:
                    conn.execute("UPDATE matches SET home_score=?, away_score=?, status='Finished' WHERE id=?", (real_h, real_a, m_id))
                conn.commit()
                conn.close()
                
                # ซิงค์ข้อมูลลง Google Sheets ด้วยตนเองเพื่อให้ข้อมูลเชื่อมโยงสมบูรณ์แบบ
                try:
                    ws = db.get_worksheet('matches')
                    data = ws.get_all_values()
                    df_sheets = pd.DataFrame(data[1:], columns=data[0])
                    mask = df_sheets['id'].astype(str) == str(m_id)
                    if mask.any():
                        idx = df_sheets.index[mask][0]
                        df_sheets.at[idx, 'home_score'] = str(real_h)
                        df_sheets.at[idx, 'away_score'] = str(real_a)
                        df_sheets.at[idx, 'status'] = 'Finished'
                        if is_ko:
                            df_sheets.at[idx, 'winner_qualify'] = str(admin_winner)
                        
                        ws.clear()
                        ws.update([df_sheets.columns.values.tolist()] + df_sheets.astype(str).values.tolist())
                except Exception as e_sheet:
                    st.error(f"⚠️ เกิดข้อผิดพลาดในการบันทึก Google Sheets: {e_sheet}")
                
                db.update_scores_logic()
                st.success("อัปเดตผลการแข่งขันและคะแนนสะสมของผู้เล่นเรียบร้อย!")
                st.balloons()

st.sidebar.markdown("---")
st.sidebar.caption("Power by Gemini 3.1 Pro & Streamlit")

# --- ตรรกะอัจฉริยะล้างสถานะป๊อปอัปความยินดี เพื่อเตรียมเปิดทางให้ป๊อปอัปทายผลแชมป์โลกทำงานได้หลังปิดกากบาท (X) หรือปิดด้วยหนทางอื่น ---
if st.session_state.get('congrats_active_in_render', False):
    st.session_state.congrats_active_in_render = False
    st.session_state.show_congrats_popup = False
