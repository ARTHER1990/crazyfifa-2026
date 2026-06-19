import streamlit as st
import database as db
from datetime import datetime, timedelta, timezone
import pandas as pd
import base64
import os

# ฟังก์ชันแปลงรูปภาพในเครื่องเป็น Base64
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

current_dir = os.path.dirname(os.path.abspath(__file__))
image_full_path = os.path.join(current_dir, "ต่างดาว_optimized.webp")
ufo_base64 = get_base64_image(image_full_path)

# โหลดภาพ Artwork พื้นหลัง Sidebar (เปลี่ยนจาก Messi เป็น 02.png ตามสั่ง)
bg_sidebar_path = os.path.join(current_dir, "02_optimized.png")
bg_sidebar_base64 = get_base64_image(bg_sidebar_path)

# ฟังก์ชันสำหรับเพลง
def get_audio_html(audio_path):
    if not os.path.exists(audio_path):
        return ""
    with open(audio_path, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()
    return f"""
        <audio autoplay loop id="bg-music">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        <script>
            var audio = document.getElementById("bg-music");
            audio.volume = 0.3; // ตั้งความดังที่ 30% เพื่อความพรีเมี่ยม
        </script>
    """

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
    'austria': '🇦🇹', 'jordan': '🇯🇴', 'dr congo': '🇨🇩', 'croatia': '🇭🇷',
    'ghana': '🇬🇭', 'panama': '🇵🇦', 'uzbekistan': '🇺🇿', 'colombia': '🇨🇴',
    'italy': '🇮🇹', 'costa rica': '🇨🇷', 'jamaica': '🇯🇲', 'honduras': '🇭🇳',
    'chile': '🇨🇱', 'peru': '🇵🇪', 'venezuela': '🇻🇪', 'nigeria': '🇳🇬',
    'cameroon': '🇨🇲', 'denmark': '🇩🇰', 'poland': '🇵🇱', 'ukraine': '🇺🇦',
    'wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'serbia': '🇷🇸', 'slovenia': '🇸🇮', 'romania': '🇷🇴',
    'georgia': '🇬🇪', 'albania': '🇦🇱', 'hungary': '🇭🇺', 'slovakia': '🇸🇰',
    'china': '🇨🇳', 'vietnam': '🇻🇳', 'thailand': '🇹🇭', 'malaysia': '🇲🇾',
}

@st.cache_data(ttl=1800)
def check_and_sync_scores():
    try:
        db.auto_sync_scores()
    except Exception as e:
        pass



def get_team_display(team_name):
    clean_name = team_name.strip()
    alias_map = {
        'cabo verde': 'cape verde',
        'czechia': 'czech republic',
        'türkiye': 'turkey',
        'ir iran': 'iran',
        'ivory coast': 'côte d\'ivoire',
        'korea republic': 'south korea'
    }
    lookup_name = clean_name.lower()
    if lookup_name in alias_map:
        lookup_name = alias_map[lookup_name]
        
    flag = FLAG_MAP.get(lookup_name, '🏳️')
    return f"{clean_name} {flag}"

# เริ่มต้นฐานข้อมูล
db.init_db()

# --- CSS ส่วนหัวและแอนิเมชัน ---
st.markdown(f"""
<!-- SVG Filter สำหรับทำเอฟเฟกต์ธงสะบัดช้าๆ (Slow Flag Waving/Ripple Effect) - ปรับให้นุ่มนวลขึ้นไม่ลายตา -->
<svg style="position: fixed; width: 0; height: 0; pointer-events: none;">
  <filter id="slow-waving-filter" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.01 0.03" numOctaves="1" result="turbulence">
      <animate attributeName="baseFrequency" 
               values="0.01 0.03; 0.01 0.04; 0.01 0.03" 
               dur="12s" 
               repeatCount="indefinite" />
    </feTurbulence>
    <feDisplacementMap in="SourceGraphic" in2="turbulence" scale="12" xChannelSelector="R" yChannelSelector="G" />
  </filter>
</svg>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Kanit', sans-serif;
    }}
    
    /* ปรับแต่ง Sidebar ให้ดูพรีเมี่ยม โทนเขียวตุ่น */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #2d3a31 0%, #1a241e 100%);
        position: relative;
        overflow-y: auto !important; /* เปิด scrolling ในแนวตั้งสำหรับ sidebar หลัก */
        border-right: none;
        box-shadow: 2px 0 15px rgba(0,0,0,0.3);
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
        filter: grayscale(100%) contrast(110%) brightness(85%) url(#slow-waving-filter); /* ใช้ SVG Filter กวนพิกเซล */
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
    
    /* ปรับแต่งปุ่มเมนู พร้อมขอบเงินโครเมี่ยม */
    div[role="radiogroup"] > label {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid #c0c0c066; /* ขอบเงินโครเมี่ยมจางๆ */
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }}
    div[role="radiogroup"] > label:hover {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid #c0c0c0; /* ขัดขอบเงินให้ชัดขึ้นเมื่อ hover */
        transform: translateX(5px);
    }}
    div[role="radiogroup"] > label[data-selected="true"] {{
        background: linear-gradient(90deg, #5c7a67 0%, #3d5244 100%) !important;
        border: 1.5px solid #ffffff; /* ขอบสีขาวสว่างแบบโครเมี่ยมสะท้อนแสง */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }}
    div[role="radiogroup"] > label[data-selected="true"] span {{
        color: #ffffff !important;
        font-weight: 600;
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

    .header-wrapper {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 140px;
    margin-top: -35px;
    overflow: visible;
    position: relative;
    z-index: 10;
}}
.main-title {{
    color: #FFD700;
    font-size: 3.5rem;
    font-weight: bold;
    margin: 0;
    letter-spacing: 2px;
    position: relative;
    animation: rising-mist 3s ease-in-out infinite;
}}

@keyframes rising-mist {{
    0% {{
        text-shadow: 
            0 0 10px rgba(0, 212, 255, 0.8),
            0 -4px 15px rgba(0, 150, 255, 0.5),
            0 -8px 25px rgba(135, 206, 250, 0.3),
            3px 3px 6px rgba(0,0,0,0.5);
    }}
    50% {{
        text-shadow: 
            0 0 14px rgba(0, 212, 255, 0.9),
            0 -8px 22px rgba(0, 150, 255, 0.7),
            0 -16px 35px rgba(135, 206, 250, 0.5),
            3px 3px 6px rgba(0,0,0,0.5);
    }}
    100% {{
        text-shadow: 
            0 0 10px rgba(0, 212, 255, 0.8),
            0 -4px 15px rgba(0, 150, 255, 0.5),
            0 -8px 25px rgba(135, 206, 250, 0.3),
            3px 3px 6px rgba(0,0,0,0.5);
    }}
}}
.trophy-wrapper {{
    position: relative;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    font-size: 3rem;
    margin-left: 20px;
}}
.animated-ball-x {{
    position: absolute;
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
    font-size: 1.5rem;
    animation: goal-ball 4s infinite;
    will-change: transform;
    filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.9)) drop-shadow(0 0 15px rgba(255, 255, 255, 0.6));
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
    35% {{ transform: translateY(-10px); }}
    40% {{ transform: translateY(-10px); }}
    100% {{ transform: translateY(-10px); }}
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
    background-image: url('data:image/webp;base64,{ufo_base64}');
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
    background-color: rgba(14, 20, 16, 0.9); /* ปรับเป็นสีเขียวดำทึบโปร่งแสง 90% ให้เข้ากับธีมหลัก */
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
        padding: 5px 10px !important;
        margin-bottom: 4px !important;
        border-radius: 6px !important;
    }}
    div[role="radiogroup"] > label span {{
        font-size: 0.8rem !important;
    }}
}}
</style>

<div class='header-wrapper'>
    <div class='main-title'>CRAZYFIFA 2026</div>
    <div class='ufo-flyer-lg'>🛸</div>
    <div class='ufo-flyer-sm'>🛸</div>
    <div class='ufo-flyer-mid'>🛸</div>
    <div class='trophy-wrapper'>
        🏆
        <div class='animated-ball-x'>
            <div class='animated-ball-y'>
                <span class='animated-ball'>⚽</span>
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
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; margin-top: -30px; color: #888;'>WORLD CUP PREDICTION CHALLENGE</h3>", unsafe_allow_html=True)

# 1. ระบบผู้ใช้งาน (Sidebar)
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.header("👤 เข้าสู่ระบบ")
try:
    leaderboard_df = db.get_leaderboard()
    existing_users = leaderboard_df['username'].tolist() if not leaderboard_df.empty else []
except Exception as e:
    st.sidebar.error(f"⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
    existing_users = []

options = ["เลือกชื่อของคุณ..."] + existing_users + ["➕ เพิ่มผู้เล่นใหม่..."]

default_idx = 0
if st.session_state.username in existing_users:
    default_idx = existing_users.index(st.session_state.username) + 1

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
            st.rerun()
elif selected_user != "เลือกชื่อของคุณ...":
    if st.session_state.username != selected_user:
        st.session_state.authenticated = False
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
                    st.rerun()
        else:
            pin_input = st.sidebar.text_input(f"ใส่รหัส PIN ({selected_user}):", type="password", max_chars=4)
            if st.sidebar.button("ยืนยันตัวตน"):
                if db.verify_user(selected_user, pin_input):
                    st.session_state.username = selected_user
                    st.session_state.authenticated = True
                    st.session_state.toast_shown = False
                    st.session_state.show_congrats_popup = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ PIN ไม่ถูกต้อง")
    else:
        st.session_state.username = selected_user
        st.sidebar.success(f"ยินดีต้อนรับคุณ **{st.session_state.username}**")
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.username = ""
            st.session_state.authenticated = False
            st.session_state.toast_shown = False
            st.rerun()
else:
    st.info("👈 กรุณาเลือกชื่อเพื่อเริ่มเล่นครับ")
    st.stop()

if not st.session_state.authenticated:
    st.stop()

username = st.session_state.username

# --- ระบบป๊อบอัพเด้งพลุแตกเฉลิมฉลองผู้ได้คะแนนสูงสุดตรงกลางจอใหญ่เมื่อล็อกอินใหม่ ---
if st.session_state.get('show_congrats_popup', False):
    try:
        import time
        # เก็บบันทึกเวลาเริ่มต้นแสดงผลของป๊อปอัป
        if 'congrats_start_time' not in st.session_state:
            st.session_state.congrats_start_time = time.time()
            
        # หากเวลาผ่านไปมากกว่า 10.5 วินาที ให้ปิดป๊อปอัปนี้อัตโนมัติทางหลังบ้านในการรีรันรอบถัดไป
        if time.time() - st.session_state.congrats_start_time > 10.5:
            st.session_state.show_congrats_popup = False
            st.rerun()
            
        leaderboard_df = db.get_leaderboard()
        if not leaderboard_df.empty:
            max_score = leaderboard_df['total_score'].max()
            if max_score > 0:
                leaders_at_top = leaderboard_df[leaderboard_df['total_score'] == max_score]['username'].tolist()
                leaders_str = " & ".join(leaders_at_top)
                
                with st.container():
                    # 1. พ่นกล่อง Backdrop, Modal, ปุ่มปิด HTML สำรอง และ JavaScript ดักคลิกกับ Auto-dismiss
                    st.markdown(
                        f"""<div class='congrats-modal-backdrop'>
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
<div class='congrats-leader'>🎉 {leaders_str} 🎉</div>
<div class='congrats-score'>👑 นำอันดับหนึ่งด้วยคะแนนสะสม: {int(max_score)} แต้ม 👑</div>
<div style='color: #FFD700; font-size: 0.95rem; font-family: Kanit, sans-serif; font-weight: bold; margin-bottom: 30px; animation: heartbeat 1.5s infinite;'>🔥 ใครจะเป็นผู้มาโค่นบัลลังก์นี้ได้สำเร็จ? 🔥</div>

<!-- เว้นพื้นที่ว่างสำหรับวางปุ่มปิด Streamlit ที่ถูกดึงขึ้นมาทับพอดี -->
<div class='congrats-btn-placeholder'></div>
</div>
</div>
<div class='congrats-trigger-marker'></div>

<script>
function dismissCongratsPopup() {{
    // 1. ค้นหาและทำลายฉากหลังและกล่องป๊อปอัปฝั่งเบราว์เซอร์ทันทีเพื่อปลดล็อกหน้าจอ
    var backdrop = document.querySelector('.congrats-modal-backdrop');
    if (backdrop) {{
        backdrop.style.display = 'none';
        backdrop.remove();
    }}
    
    // 2. ค้นหามาร์กเกอร์และทำการสกัดปุ่มกดปิดของ Streamlit เพื่อทำการกระตุ้นคลิกหลังบ้าน
    var marker = document.querySelector('.congrats-trigger-marker');
    if (marker) {{
        var parentContainer = marker.parentElement;
        if (parentContainer) {{
            // หา container ของปุ่มสตรีมลิตที่อยู่ถัดไป
            var nextEl = parentContainer.nextElementSibling;
            if (nextEl) {{
                var btn = nextEl.querySelector('button');
                if (btn) {{
                    btn.click();
                }}
            }}
        }}
    }}
}}

// ปิดอัตโนมัติเมื่อครบ 10 วินาที
setTimeout(function() {{
    dismissCongratsPopup();
}}, 10000);
</script>""",
                        unsafe_allow_html=True
                    )
                    
                    # 2. ปุ่ม Streamlit ที่จัดวางพิกัดให้อยู่เหนือกำแพง backdrop เสมอ
                    if st.button("ลุยต่อกันเลย! ⚽🔥", key="close_popup_btn", use_container_width=True):
                        st.session_state.show_congrats_popup = False
                        st.rerun()
                        
                    # 3. พ่น CSS ควบคุมการเลือนหายไปเอง และยอมให้นิ้วสไลด์เลื่อนผ่าน (Pointer Events PASS-THROUGH)
                    st.markdown(
                        """<style>
/* สำหรับอุปกรณ์โทรศัพท์มือถือและหน้าจอขนาดเล็ก: ปิดการทำงานและการครอบสัมผัสของระบบ Congrats ทั้งหมดโดยสมบูรณ์ เพื่อป้องกันไม่ให้โทรศัพท์ค้างแข็งและเปิดให้เลื่อนหน้าจอโฮมกรอกคะแนนได้ฉลุยทันที! */
@media (max-width: 768px) {
    .congrats-modal-backdrop {
        display: none !important;
        pointer-events: none !important;
    }
    .congrats-modal {
        display: none !important;
        pointer-events: none !important;
    }
    div[data-testid="element-container"]:has(.congrats-trigger-marker),
    div[data-testid="element-container"]:has(.congrats-trigger-marker) + div[data-testid="element-container"] {
        display: none !important;
        pointer-events: none !important;
        position: static !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
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
    
    /* แอนิเมชันเฟดหายไปเองใน 10 วินาที */
    animation: fade-out-disappear 10s forwards cubic-bezier(0.25, 1, 0.5, 1) !important;
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
               popup-fade-out 10s forwards ease-in-out !important;
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
    animation: button-fade-out 10s forwards ease-in-out !important;
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
    80% { opacity: 1; pointer-events: none; }
    95% { opacity: 0; pointer-events: none; }
    100% { opacity: 0; pointer-events: none; display: none !important; }
}

@keyframes popup-fade-out {
    0% { opacity: 1; }
    80% { opacity: 1; transform: scale(1); }
    95% { opacity: 0; transform: scale(0.9); }
    100% { opacity: 0; display: none !important; }
}

@keyframes button-fade-out {
    0% { opacity: 1; pointer-events: auto; }
    80% { opacity: 1; pointer-events: auto; }
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
    except Exception as e:
        pass

# --- ตรวจสอบอัปเดตผลสกอร์แบบเรียลไทม์อัตโนมัติ (แคชไว้ 30 นาที) ---
check_and_sync_scores()


# --- คำนวณคู่แข่งขันที่ยังไม่ได้ทายผลสำหรับเตือนความจำ ---
if 'toast_shown' not in st.session_state:
    st.session_state.toast_shown = False

try:
    all_matches_rem = db.get_matches()
    all_matches_rem['match_dt'] = pd.to_datetime(all_matches_rem['match_time'])
    now_th_rem = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
    
    # ดึงคู่ที่ยังไม่จบการแข่งขัน และเวลาเตะยังไม่ถึงกำหนด (ยังแก้ไขได้)
    active_upcoming_rem = all_matches_rem[
        (all_matches_rem['status'] != 'Finished') & 
        (all_matches_rem['match_dt'] > now_th_rem)
    ]
    
    user_preds_rem = db.get_user_predictions(username)
    unpredicted_list = []
    
    for _, row in active_upcoming_rem.iterrows():
        m_id = int(row['id'])
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

# --- ระบบเพลงประกอบ (เล่นอัตโนมัติหลัง Login) ---
if st.session_state.authenticated:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎵 บรรยากาศสนาม")
    music_on = st.sidebar.toggle("เปิดเสียงเชียร์", value=True)
    if music_on:
        song_path = os.path.join(current_dir, "Shakira Burna Boy Dai Dai Official Video.mp3")
        st.components.v1.html(get_audio_html(song_path), height=0)
        st.sidebar.caption("📻 กำลังบรรเลง: Shakira & Burna Boy - Dai Dai")

    # --- แถบสรุปผลการแข่งขันของวันนี้/วันล่าสุดย้อนหลัง 1 วันใน Sidebar ---
    st.sidebar.markdown("---")

    # ดึงข้อมูลแมตช์และประวัติการทายผลทั้งหมด
    all_matches_sb = db.get_matches()
    all_matches_sb['match_dt'] = pd.to_datetime(all_matches_sb['match_time'])
    finished_sb = all_matches_sb[all_matches_sb['status'] == 'Finished'].sort_values('match_time', ascending=False)

    if not finished_sb.empty:
        # คำนวณวันปัจจุบัน (เวลาไทย UTC+7)
        now_th_sb = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        today_date_sb = now_th_sb.date()
        
        # กรองเฉพาะแมตช์ที่แข่งเสร็จในวันนี้จริง ๆ (ตามเวลาไทย UTC+7)
        day_matches_sb = finished_sb[finished_sb['match_dt'].dt.date == today_date_sb]
        
        st.sidebar.subheader("📅 สรุปผลแข่งวันนี้")
        
        if day_matches_sb.empty:
            st.sidebar.info("ไม่มีสรุปผลแข่งของวันนี้")
        
        # ดึงประวัติการทายเพื่อประมวลผลความถูกต้องของผู้ใช้งานทั้งหมด
        predictions_sb = db.get_predictions_df()
        
        for _, row_m in day_matches_sb.iterrows():
            m_id = str(row_m['id'])
            h_real = int(row_m['home_score']) if row_m['home_score'] != "" else 0
            a_real = int(row_m['away_score']) if row_m['away_score'] != "" else 0
            real_win = (h_real > a_real) - (h_real < a_real)
            
            home_flag = FLAG_MAP.get(row_m['home_team'].strip().lower(), '🏳️')
            away_flag = FLAG_MAP.get(row_m['away_team'].strip().lower(), '🏳️')
            
            exp_title = f"{row_m['home_team']} {home_flag} {h_real} - {a_real} {row_m['away_team']} {away_flag}"
            
            with st.sidebar.expander(exp_title):
                st.markdown(f"**⚽ ผู้ทำประตู:** {row_m['scorers'] if row_m['scorers'] else 'ไม่มีข้อมูล'}")
                st.markdown("**🎯 ผลทายของทุกคนในคู่นี้:**")
                
                # กรองคำทายของคู่นี้
                m_preds = predictions_sb[predictions_sb['match_id'].astype(str) == m_id]
                if m_preds.empty:
                    st.markdown("<small style='color:#888;'>ยังไม่มีผู้เล่นทายคู่นี้</small>", unsafe_allow_html=True)
                else:
                    for _, row_p in m_preds.iterrows():
                        u_name = row_p['username']
                        p_h = int(row_p['pred_home']) if row_p['pred_home'] != "" else 0
                        p_a = int(row_p['pred_away']) if row_p['pred_away'] != "" else 0
                        pred_win = (p_h > p_a) - (p_h < p_a)
                        
                        # คำนวณแต้มทายผล
                        if p_h == h_real and p_a == a_real:
                            hl_class = "pred-highlight-exact"
                            pt_txt = "🏆 3 แต้ม"
                        elif pred_win == real_win:
                            hl_class = "pred-highlight-winner"
                            pt_txt = "🟢 1 แต้ม"
                        else:
                            hl_class = "pred-highlight-wrong"
                            pt_txt = "❌ 0 แต้ม"
                        
                        st.markdown(
                            f"""
                            <div class='{hl_class}' style='font-size:0.8rem; padding:6px; border-radius:6px; margin-bottom:4px;'>
                                👤 <b>{u_name}</b>: ทาย {p_h} - {p_a} ({pt_txt})
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
    else:
        st.sidebar.info("ไม่มีสรุปผลแข่งของวันนี้")

    st.sidebar.markdown("---")

menu_options = ["🏟️ ศึกชิงแชมป์โลก 2026", "📜 ผลการแข่งขันย้อนหลัง", "📑 ประวัติการทายผล", "🏆 ทำเนียบแชมป์ (Leaderboard)"]
if st.session_state.username == "Art":
    menu_options.append("💎 ห้องควบคุมระบบ (Admin)")
menu = st.sidebar.radio("เมนูหลัก", menu_options)

# 2. หน้าทายผลการแข่งขัน
if menu == "🏟️ ศึกชิงแชมป์โลก 2026":
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

    all_matches = db.get_matches()
    all_matches['match_dt'] = pd.to_datetime(all_matches['match_time'])

    # ดึงผลทำนายของผู้เล่นในครั้งเดียวที่นี่! เพื่อประหยัดการเชื่อมต่อ API ของ Google Sheets (Quota Saving)
    try:
        user_preds_cached = db.get_user_predictions(username)
    except Exception as e:
        user_preds_cached = {}

    def render_match(row, username):
        match_id = row['id']
        home = row['home_team']
        away = row['away_team']
        home_display = get_team_display(home)
        away_display = get_team_display(away)

        m_time = datetime.strptime(row['match_time'], '%Y-%m-%d %H:%M:%S')
        status = row['status']
        now_th = datetime.now(timezone(timedelta(hours=7))).replace(tzinfo=None)
        is_locked = now_th > m_time or status == 'Finished'

        has_pred = match_id in user_preds_cached
        default_h, default_a = user_preds_cached.get(match_id, (0, 0))
        
        # กำหนดคะแนนที่จะแสดงในช่องกรอก (ถ้าเกมจบแล้ว ให้แสดงสกอร์จริงในช่องที่ปิดการแก้ไข)
        if status == 'Finished':
            val_h = int(row['home_score']) if row['home_score'] != "" else 0
            val_a = int(row['away_score']) if row['away_score'] != "" else 0
        else:
            val_h = int(default_h)
            val_a = int(default_a)

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
                        db.save_prediction(username, match_id, pred_h, pred_a)
                        st.toast(f"⚽ บันทึกผลทาย {home_display} vs {away_display} เรียบร้อยแล้ว!")
                        # บังคับให้หน้าจอ Rerun ทันทีหลังกดส่ง เพื่อแสดงปุ่มติ๊กถูก
                        st.rerun()
                        
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
                        h_score_val = int(row['home_score']) if row['home_score'] != "" else 0
                        a_score_val = int(row['away_score']) if row['away_score'] != "" else 0
                        winner_name = home if h_score_val > a_score_val else (away if a_score_val > h_score_val else "เสมอ")
                        winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                        st.info(f"🏆 **ชนะ:** {winner_display} ({h_score_val}-{a_score_val})")
                        if row['scorers']: st.caption(f"⚽ **คนยิง:** {row['scorers']}")
                        if has_pred:
                            st.info(f"🎯 **คุณทายผลไว้:** {int(default_h)} - {int(default_a)}")
                        else:
                            st.info("🎯 **คุณไม่ได้ทายคู่นี้ไว้**")
                    else:
                        st.warning("🔒 ปิดรับผลทาย")
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
                
            st.markdown(f"### <span class='bouncing-icon'>⚽</span> ตารางแข่งขันวันที่ {d.strftime('%d/%m/%Y')}{label_suffix}", unsafe_allow_html=True)
            day_matches = upcoming[upcoming['match_dt'].dt.date == d]
            for _, row in day_matches.iterrows():
                render_match(row, username)
    else:
        st.info("ไม่มีการแข่งขันที่กำลังจะมาถึงในขณะนี้ครับ")

# 3. หน้าผลการแข่งขันย้อนหลัง
elif menu == "📜 ผลการแข่งขันย้อนหลัง":
    st.header("📜 ผลการแข่งขันย้อนหลังทั้งหมด")
    st.info("💡 รวบรวมข้อมูลผลสกอร์และรายชื่อผู้ทำประตูในทุกแมตช์ที่จบการแข่งขันแล้ว")
    st.markdown("---")
    
    all_matches = db.get_matches()
    finished = all_matches[all_matches['status'] == 'Finished'].sort_values('match_time', ascending=False)
    
    if finished.empty:
        st.info("ยังไม่มีการแข่งขันใดที่สิ้นสุดลงในขณะนี้ครับ")
    else:
        # จัดกลุ่มการแข่งขันย้อนหลังตามวันที่เตะเพื่อความเป็นระเบียบและให้เปิดดูง่าย
        finished['match_dt'] = pd.to_datetime(finished['match_time'])
        unique_dates = finished['match_dt'].dt.date.unique()
        
        for d in unique_dates:
            st.subheader(f"🗓️ วันที่ {d.strftime('%d/%m/%Y')}")
            day_matches = finished[finished['match_dt'].dt.date == d]
            
            for _, row in day_matches.iterrows():
                home = row['home_team']
                away = row['away_team']
                home_display = get_team_display(home)
                away_display = get_team_display(away)
                h_score = int(row['home_score']) if row['home_score'] != "" else 0
                a_score = int(row['away_score']) if row['away_score'] != "" else 0
                
                expander_label = f"⚽ {home_display}  {h_score} - {a_score}  {away_display}"
                
                with st.expander(expander_label):
                    st.markdown(f"### 🏟️ {home_display} vs {away_display}")
                    st.write(f"🗓️ **เวลาแข่งขัน:** {pd.to_datetime(row['match_time']).strftime('%d/%m/%Y %H:%M น.')}")
                    
                    winner_name = home if h_score > a_score else (away if a_score > h_score else "เสมอ")
                    winner_display = get_team_display(winner_name) if winner_name != "เสมอ" else "เสมอ"
                    st.write(f"🏆 **ผลการแข่งขัน:** {winner_display}")
                    
                    st.markdown("---")
                    st.markdown("⚽ **รายชื่อผู้ยิงประตู:**")
                    if row['scorers'] and row['scorers'].strip() != "":
                        scorers_list = [s.strip() for s in row['scorers'].split(',')]
                        for s in scorers_list:
                            st.write(f"- {s}")
                    else:
                        st.write("ไม่มีข้อมูลการยิงประตู")
            st.divider()

# 4. หน้า Leaderboard
elif menu == "🏆 ทำเนียบแชมป์ (Leaderboard)":
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
        def add_gimmick(row):
            score = row['total_score']
            username = row['username']
            if score > 0:
                if score == gold_score:
                    return f"👑 {username} 🥇"
                elif score == silver_score:
                    return f"⭐️ {username} 🥈"
                elif score == bronze_score:
                    return f"✨ {username} 🥉"
            return f"👤 {username}"
        
        leaderboard['รายชื่อผู้เล่น'] = leaderboard.apply(add_gimmick, axis=1)
        st.dataframe(
            leaderboard[['อันดับ', 'รายชื่อผู้เล่น', 'total_score']].rename(columns={'total_score': 'คะแนนสะสม'}), 
            width='stretch', 
            hide_index=True,
            column_config={
                "อันดับ": st.column_config.NumberColumn("อันดับ", width="small"),
                "รายชื่อผู้เล่น": st.column_config.TextColumn("รายชื่อผู้เล่น", width="large"),
                "คะแนนสะสม": st.column_config.NumberColumn("คะแนนสะสม", width="medium")
            }
        )

# 5. หน้าประวัติการทายผล (แยกออกมาตามคำปรึกษาคุณอาร์ต)
elif menu == "📑 ประวัติการทายผล":
    st.header("📑 ประวัติการทายผลการแข่งขัน")
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
                    h_real = int(row_m['home_score']) if row_m['home_score'] != "" else 0
                    a_real = int(row_m['away_score']) if row_m['away_score'] != "" else 0
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
                                p_h = int(row_p['pred_home']) if row_p['pred_home'] != "" else 0
                                p_a = int(row_p['pred_away']) if row_p['pred_away'] != "" else 0
                                pred_win = (p_h > p_a) - (p_h < p_a)
                                
                                # ตรวจแต้มทายผล
                                if p_h == h_real and p_a == a_real:
                                    pt_label = "🏆 ทายถูกตรงเป๊ะ! ได้ 3 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(153, 101, 21, 0.1) 100%);
                                    border: 1px solid #FFD700;
                                    color: #FFD700;
                                    """
                                elif pred_win == real_win:
                                    pt_label = "🟢 ทายถูกฝั่ง! ได้ 1 คะแนน"
                                    card_style = """
                                    background: linear-gradient(135deg, rgba(46, 125, 50, 0.2) 0%, rgba(27, 94, 32, 0.1) 100%);
                                    border: 1px solid #4CAF50;
                                    color: #81C784;
                                    """
                                else:
                                    pt_label = "❌ ทายผิด! ได้ 0 คะแนน"
                                    card_style = """
                                    background: rgba(255, 255, 255, 0.02);
                                    border: 1px solid rgba(255, 255, 255, 0.08);
                                    color: #a0aec0;
                                    """
                                
                                st.markdown(
                                    f"""
                                    <div style='padding: 10px 15px; border-radius: 8px; margin-bottom: 6px; {card_style}'>
                                        👤 ผู้เล่น: <b>{u_name}</b> | ผลทาย: <b>{p_h} - {p_a}</b> &nbsp;&nbsp;&nbsp;&nbsp; ({pt_label})
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
                
                st.subheader(f"🗓️ ตารางแข่งขันวันที่ {date_str}{label_suffix}")
                day_matches = upcoming_matches[upcoming_matches['match_dt'].dt.date == d]
                
                for _, row_m in day_matches.iterrows():
                    m_id = row_m['id']
                    home_team = row_m['home_team']
                    away_team = row_m['away_team']
                    
                    has_pred = int(m_id) in user_preds
                    home_disp = get_team_display(home_team)
                    away_disp = get_team_display(away_team)
                    
                    m_time = datetime.strptime(row_m['match_time'], '%Y-%m-%d %H:%M:%S')
                    is_locked = now_th > m_time or row_m['status'] == 'Finished'
                    
                    if has_pred:
                        pred_h, pred_a = user_preds[int(m_id)]
                        pred_text = f"🔥 ผลทายของคุณ: &nbsp;<b>{pred_h} - {pred_a}</b>"
                        card_style = """
                        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 150, 255, 0.03) 100%);
                        border: 1px solid rgba(0, 212, 255, 0.2);
                        color: #e2e8f0;
                        """
                    else:
                        pred_text = "⚠️ คุณยังไม่ได้ทายผลคู่นี้"
                        card_style = """
                        background: rgba(255, 255, 255, 0.01);
                        border: 1px solid rgba(255, 255, 255, 0.05);
                        color: #a0aec0;
                        """
                    
                    status_text = "🔒 ปิดรับผลทายแล้ว" if is_locked else "🔓 เปิดรับผลทาย (สามารถแก้ไขได้ที่หน้าแรก)"
                    st.markdown(
                        f"""
                        <div style='padding: 15px; border-radius: 12px; margin-bottom: 12px; {card_style}'>
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
elif menu == "💎 ห้องควบคุมระบบ (Admin)":
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
    st.subheader("✍️ กรอกผลคะแนนด้วยตนเอง")
    matches = db.get_matches()
    upcoming = matches[matches['status'] != 'Finished']
    if not upcoming.empty:
        selected = st.selectbox("เลือกแมตช์:", [f"{r['id']}: {r['home_team']} vs {r['away_team']}" for i, r in upcoming.iterrows()])
        m_id = int(selected.split(":")[0])
        c1, c2 = st.columns(2)
        real_h = c1.number_input("สกอร์ Home", min_value=0, step=1)
        real_a = c2.number_input("สกอร์ Away", min_value=0, step=1)
        if st.button("ยืนยันผล"):
            import sqlite3
            conn = sqlite3.connect('worldcup.db')
            conn.execute("UPDATE matches SET home_score=?, away_score=?, status='Finished' WHERE id=?", (real_h, real_a, m_id))
            conn.commit()
            conn.close()
            db.update_scores_logic()
            st.success("อัปเดตเรียบร้อย!")
            st.balloons()

st.sidebar.markdown("---")
st.sidebar.caption("Power by Gemini 3.1 Pro & Streamlit")
