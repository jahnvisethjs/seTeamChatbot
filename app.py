import streamlit as st
import os
from typing import Optional
import markdown as md
from chatbot.core import MegaChatbot
from config.settings import APP_TITLE, APP_DESCRIPTION, ASU_AI_API_TOKEN

# ── Credentials (loaded from .env — never hardcoded in source) ────────────────
from dotenv import load_dotenv
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Landing page ───────────────────────────────────────── */
    .landing-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        padding: 1.5rem 2rem 0 2rem;
    }

    .landing-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -1px;
    }

    .landing-subtitle {
        color: #64748b;
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    .role-cards {
        display: flex;
        gap: 2rem;
        justify-content: center;
        flex-wrap: wrap;
    }

    .role-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem 3rem;
        width: 240px;
        text-align: center;
        cursor: pointer;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        border: 2px solid transparent;
        transition: all 0.25s ease;
    }

    .role-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 36px rgba(102,126,234,0.25);
        border-color: #667eea;
    }

    .role-card-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }

    .role-card-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }

    .role-card-desc {
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.5;
    }

    .card-admin { border-top: 4px solid #667eea; }
    .card-student { border-top: 4px solid #10b981; }

    /* ── Login form ─────────────────────────────────────────── */
    .login-box {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        max-width: 420px;
        margin: 0 auto;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border-top: 4px solid #667eea;
    }

    .login-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.25rem;
    }

    .login-subtitle {
        color: #64748b;
        text-align: center;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    /* ── Chatbot CSS (existing) ──────────────────────────────── */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }

    .block-container {
        background-color: white;
        border-radius: 20px;
        padding: 1rem 2rem 2rem 2rem !important;
        padding-top: 0.5rem !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    .chat-message {
        padding: 1.25rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .chat-avatar {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }

    .chat-avatar-icon {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        flex-shrink: 0;
    }

    .user-avatar { background: rgba(255,255,255,0.25); }
    .assistant-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: none;
        margin-left: 20%;
    }

    .user-message strong { color: #fff; font-weight: 600; }

    .assistant-message {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #667eea;
        margin-right: 20%;
        color: #1e293b;
    }

    .assistant-message strong { color: #667eea; font-weight: 600; }
    .assistant-message h3, .assistant-message h4 { color: #334155; margin-top: 1rem; margin-bottom: 0.5rem; }

    .assistant-message table { border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.9rem; }
    .assistant-message th, .assistant-message td { border: 1px solid #cbd5e1; padding: 0.5rem 0.75rem; text-align: left; }
    .assistant-message th { background-color: #e2e8f0; font-weight: 600; color: #334155; }
    .assistant-message tr:nth-child(even) { background-color: #f1f5f9; }
    .assistant-message hr { border: none; border-top: 1px solid #e2e8f0; margin: 1rem 0; }
    .assistant-message ul, .assistant-message ol { padding-left: 1.5rem; margin: 0.5rem 0; }

    .assistant-message pre {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        font-size: 0.9rem;
        margin: 0.75rem 0;
    }

    .assistant-message code {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 6px;
        padding: 0.2rem 0.4rem;
        font-size: 0.88em;
    }

    .assistant-message pre code {
        background-color: transparent !important;
        color: inherit !important;
        padding: 0;
        border-radius: 0;
        font-size: inherit;
    }

    .assistant-message p > code,
    .assistant-message li > code,
    .assistant-message td > code,
    .assistant-message a > code {
        background-color: #e2e8f0 !important;
        color: #667eea !important;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85em;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    .css-1d391kg h2, .css-1d391kg h3,
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fff !important; }
    .css-1d391kg p, .css-1d391kg label,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #cbd5e1 !important; }

    /* Role badge */
    .role-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 1rem;
        text-align: center;
        width: 100%;
    }
    .role-badge-admin  { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .role-badge-student { background: linear-gradient(135deg, #10b981, #059669); color: white; }

    /* Buttons — default (chatbot UI) */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    /* ── Landing card overlay buttons ───────────────────────────────────────
       Streamlit assigns stable class st-key-{keyname} to each button's container.
       We use these to precisely target and overlay admin/student buttons on the cards. */
    .card-wrap {
        position: relative;
        cursor: pointer;
    }
    .role-card {
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    /* Outer element container: pull up over the card and overlay */
    .st-key-btn_admin,
    .st-key-btn_student {
        position: relative !important;
        margin-top: -215px !important;
        height: 215px !important;
        z-index: 20 !important;
    }
    /* The stButton inside and the actual <button> element */
    .st-key-btn_admin .stButton,
    .st-key-btn_student .stButton,
    .st-key-btn_admin [data-testid="stButton"],
    .st-key-btn_student [data-testid="stButton"] {
        width: 100% !important;
        height: 100% !important;
    }
    .st-key-btn_admin button,
    .st-key-btn_student button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        position: relative !important;
        z-index: 20 !important;
    }
    .st-key-btn_admin button:hover,
    .st-key-btn_student button:hover {
        transform: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    /* Hover on the element container lifts the card above */
    .st-key-btn_admin:hover ~ * .role-card,
    .st-key-btn_student:hover ~ * .role-card { /* fallback */ }

    /* Better hover: since the invisible button sits on top (z-index 20),
       detect hover on the whole vertical block instead */
    [data-testid="stVerticalBlock"]:has(.st-key-btn_admin:hover) .role-card,
    [data-testid="stVerticalBlock"]:has(.st-key-btn_student:hover) .role-card {
        transform: translateY(-6px);
        box-shadow: 0 14px 40px rgba(102,126,234,0.22);
        border-color: #667eea;
    }


    /* Input */
    .stTextArea textarea { border-radius: 12px; border: 2px solid #e2e8f0; padding: 1rem; font-size: 1rem; transition: border-color 0.3s ease; }
    .stTextArea textarea:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1); }
    .stTextInput > div > div > input {
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        background-color: #f8fafc !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
        background-color: #ffffff !important;
    }
    .stTextInput > div > div > input::placeholder { color: #94a3b8 !important; }

    /* Progress bar */
    .stProgress > div > div { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }

    /* Mode indicator */
    .mode-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3);
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: linear-gradient(135deg, #5568d3 0%, #653a8f 100%); }

    /* ===== Loading / Processing State ===== */
    [data-stale="true"] {
        opacity: 0.45 !important;
        pointer-events: none;
        transition: opacity 0.3s ease;
    }

    .stSpinner {
        position: fixed !important;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9999;
        display: flex !important;
        align-items: center;
        justify-content: center;
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        animation: overlayFadeIn 0.25s ease-out;
    }
    @keyframes overlayFadeIn { from { opacity: 0; } to { opacity: 1; } }

    .stSpinner > div {
        background: transparent !important;
        box-shadow: none !important;
        font-size: 0 !important;
        color: transparent !important;
        padding: 0 !important;
        display: flex; align-items: center; justify-content: center;
    }
    .stSpinner > div > span, .stSpinner > div > i,
    .stSpinner > div [data-testid="stSpinnerIcon"], .stSpinner > div::before { display: none !important; }

    .stSpinner > div::after {
        content: "";
        display: block;
        width: 48px; height: 48px;
        border: 4px solid rgba(255, 255, 255, 0.25);
        border-top-color: #667eea;
        border-right-color: #764ba2;
        border-radius: 50%;
        animation: spinRing 0.75s linear infinite;
    }
    @keyframes spinRing { to { transform: rotate(360deg); } }

    [data-testid="stStatusWidget"] { position: fixed !important; top: 0; left: 0; right: 0; z-index: 10000; }
    [data-testid="stStatusWidget"] [role="status"] {
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
        background-size: 200% 100%;
        animation: shimmerBar 1.5s ease-in-out infinite;
        height: 3px; border-radius: 0;
    }
    @keyframes shimmerBar { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
</style>
""", unsafe_allow_html=True)
# ── Chatbot cache ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_chatbot():
    """Initialize a new chatbot instance."""
    return MegaChatbot()


# ── Session state init ────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "user_role": None,          # None | "admin" | "student"
        "show_login": False,        # Show admin login form
        "login_error": "",          # Login error message
        "chatbot": None,
        "chat_history": [],
        "current_mode": "general",
        "image_upload_counter": 0,
        "message_counter": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────────────────────────────────────
#  LANDING PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_landing_page():
    st.markdown("""
    <div class="landing-wrapper">
        <div class="landing-title">🤖 SE Team Chatbot</div>
        <div class="landing-subtitle">Your comprehensive assistant for dev setup, onboarding, and team support</div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_admin, col_gap, col_student, col_right = st.columns([1, 2, 0.5, 2, 1])

    with col_admin:
        # White card visual — transparent overlay button makes the whole card clickable
        st.markdown("""
        <div class="card-wrap">
            <div class="role-card card-admin">
                <div class="role-card-icon">🔐</div>
                <div class="role-card-title">Admin</div>
                <div class="role-card-desc">Full access — General Chat, Dev Setup &amp; Onboarding</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("admin", key="btn_admin", use_container_width=True):
            st.session_state.show_login = True
            st.session_state.login_error = ""
            st.rerun()

    with col_student:
        st.markdown("""
        <div class="card-wrap">
            <div class="role-card card-student">
                <div class="role-card-icon">🎓</div>
                <div class="role-card-title">Student</div>
                <div class="role-card-desc">General Chat &amp; Dev Setup — no login required</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("student", key="btn_student", use_container_width=True):
            st.session_state.user_role = "student"
            st.session_state.show_login = False
            _init_chatbot()
            st.rerun()

    # Use components.v1.html to run JS in the parent Streamlit document
    # (st.markdown strips <script> tags; this does not)
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        function moveButtons() {
            var doc = window.parent.document;
            var cards = doc.querySelectorAll('.card-wrap');
            var done = 0;
            cards.forEach(function(card) {
                if (card.querySelector('[data-testid="stButton"]')) { done++; return; }
                var mc = card.closest('[data-testid="stMarkdownContainer"]');
                if (!mc) return;
                var sib = mc.parentElement && mc.parentElement.nextElementSibling;
                while (sib) {
                    var btnWrap = sib.querySelector('[data-testid="stButton"]') || (sib.getAttribute('data-testid') === 'stButton' ? sib : null);
                    if (btnWrap) { card.appendChild(btnWrap); done++; break; }
                    sib = sib.nextElementSibling;
                }
            });
            if (cards.length > 0 && done < cards.length) setTimeout(moveButtons, 150);
        }
        setTimeout(moveButtons, 300);
    })();
    </script>
    """, height=0)


def show_admin_login():
    # Back button
    if st.button("← Back", key="btn_back_login"):
        st.session_state.show_login = False
        st.session_state.login_error = ""
        st.rerun()

    st.markdown("""
    <div class="login-box">
        <div class="login-title">🔐 Admin Login</div>
        <div class="login-subtitle">Enter your credentials to access all features</div>
    </div>
    """, unsafe_allow_html=True)

    col_c, col_form, col_cr = st.columns([1, 2, 1])
    with col_form:
        username = st.text_input("Username", key="login_username", placeholder="Enter username")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Enter password")

        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        if st.button("🔓 Login", key="btn_login", use_container_width=True):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.user_role = "admin"
                st.session_state.show_login = False
                st.session_state.login_error = ""
                _init_chatbot()
                st.rerun()
            else:
                st.session_state.login_error = "❌ Incorrect username or password. Please try again."
                st.rerun()


def _init_chatbot():
    """Load chatbot into session state (cached)."""
    if st.session_state.chatbot is None:
        st.session_state.chatbot = get_chatbot()


# ─────────────────────────────────────────────────────────────────────────────
#  CHATBOT PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_chatbot():
    role = st.session_state.user_role  # "admin" | "student"

    # ── Available modes per role ──
    if role == "admin":
        available_display = ["General Chat", "Dev Setup", "Onboarding"]
    else:
        available_display = ["General Chat", "Dev Setup"]

    mode_map = {
        "General Chat": "general",
        "Dev Setup": "dev_setup",
        "Onboarding": "onboarding",
    }

    # Ensure current_mode is valid for this role
    current_display = next(
        (d for d, k in mode_map.items() if k == st.session_state.current_mode),
        "General Chat"
    )
    if current_display not in available_display:
        st.session_state.current_mode = "general"
        current_display = "General Chat"

    # ── Header ──
    st.markdown('<h1 class="main-header">🤖 SE Team Chatbot</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{APP_DESCRIPTION} • Powered by ASU AI Platform</p>', unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")

        # Role badge
        if role == "admin":
            st.markdown('<div class="role-badge role-badge-admin">🔐 Admin</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="role-badge role-badge-student">🎓 Student</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Mode selector (filtered by role)
        st.markdown("### 🔧 Assistant Mode")
        mode = st.selectbox(
            "Choose your mode:",
            available_display,
            index=available_display.index(current_display),
            key="mode_selector"
        )

        selected_mode = mode_map[mode]

        if selected_mode != st.session_state.current_mode:
            st.session_state.current_mode = selected_mode
            st.session_state.chat_history = []
            response = st.session_state.chatbot.switch_mode(selected_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        # Image upload (General Chat + Onboarding only, Onboarding admin-only)
        uploaded_image = None
        if st.session_state.current_mode in ("general", "onboarding"):
            st.markdown("---")
            if st.session_state.current_mode == "onboarding":
                st.markdown("### 📸 Class Timetable")
                uploaded_image = st.file_uploader(
                    "Upload image of your schedule",
                    type=["jpg", "jpeg", "png"],
                    help="Upload your class timetable and I'll create a work schedule for you!",
                    key=f"image_uploader_{st.session_state.image_upload_counter}"
                )
            else:
                st.markdown("### 🖼️ Image Upload")
                uploaded_image = st.file_uploader(
                    "Upload an image to analyze",
                    type=["jpg", "jpeg", "png"],
                    help="Upload any image and ask questions about it!",
                    key=f"image_uploader_{st.session_state.image_upload_counter}"
                )
            if uploaded_image:
                caption = "Uploaded Timetable" if st.session_state.current_mode == "onboarding" else "Uploaded Image"
                st.image(uploaded_image, caption=caption, use_container_width=True)

        st.markdown("---")

        # Logout / switch role
        if st.button("🔄 Switch Role", key="btn_logout", use_container_width=True):
            # Reset everything except cached chatbot
            st.session_state.user_role = None
            st.session_state.show_login = False
            st.session_state.login_error = ""
            st.session_state.chat_history = []
            st.session_state.current_mode = "general"
            st.session_state.message_counter = 0
            st.session_state.image_upload_counter = 0
            st.rerun()

    # ── Mode indicator ──
    mode_emoji = {"general": "💬", "dev_setup": "🔧", "onboarding": "📅"}
    mode_names = {"general": "General Chat", "dev_setup": "Dev Setup Assistant", "onboarding": "Onboarding"}

    st.markdown(f"""
    <div class="mode-indicator">
        {mode_emoji.get(st.session_state.current_mode, '💬')}
        Current Mode: {mode_names.get(st.session_state.current_mode, 'General Chat')}
    </div>
    """, unsafe_allow_html=True)

    # ── Chat history ──
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            _show_welcome(role)

        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="chat-avatar">
                        <span class="chat-avatar-icon user-avatar">👤</span>
                        <strong>You</strong>
                    </div>
                    <div class="chat-body">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                html_content = md.markdown(
                    message["content"],
                    extensions=['tables', 'fenced_code', 'nl2br']
                )
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="chat-avatar">
                        <span class="chat-avatar-icon assistant-avatar">🤖</span>
                        <strong>Assistant</strong>
                    </div>
                    <div class="chat-body">{html_content}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Input area ──
    st.markdown("---")

    def on_input_submit():
        user_input = st.session_state.get(f'message_input_{st.session_state.message_counter}', '').strip()
        img_bytes = None
        if uploaded_image:
            img_bytes = uploaded_image.getvalue()

        if user_input or img_bytes:
            input_lower = (user_input or "").lower()
            if st.session_state.current_mode == "onboarding" and any(
                w in input_lower for w in ["agenda", "onboarding plan", "welcome"]
            ):
                spinner_msg = "📝 Generating your 21-day onboarding agenda... This may take a few minutes."
            elif img_bytes:
                spinner_msg = "🖼️ Processing image..."
            else:
                spinner_msg = "🤔 Thinking..."

            with st.spinner(spinner_msg):
                process_user_input(user_input, img_bytes)

            st.session_state.message_counter += 1
            if img_bytes:
                st.session_state.image_upload_counter += 1

    col_input, col_send, col_help = st.columns([6, 1, 1])

    with col_input:
        onboarding_placeholder = "Ask me to create a work schedule! You can also upload a timetable image in the sidebar."
        default_placeholder = "Ask me anything! You can also upload an image in the sidebar. (Press Enter to send)"
        st.text_input(
            "💭 Type your message here...",
            key=f"message_input_{st.session_state.message_counter}",
            placeholder=onboarding_placeholder if st.session_state.current_mode == "onboarding" else default_placeholder,
            label_visibility="collapsed",
            on_change=on_input_submit
        )

    with col_send:
        if st.button("🚀 Send", type="primary", use_container_width=True):
            on_input_submit()

    with col_help:
        if st.button("💡 Help", use_container_width=True):
            _show_help(role)
            st.rerun()

    # ── Dev setup progress bar ──
    if st.session_state.current_mode == "dev_setup":
        progress = st.session_state.chatbot.dev_setup_assistant.get_step_progress()
        st.markdown("---")
        st.markdown(f"**📈 Setup Progress: {progress['percentage']:.1f}%**")
        st.progress(progress['percentage'] / 100)
        current_step = st.session_state.chatbot.dev_setup_assistant.get_current_step()
        if current_step:
            st.caption(f"Step {current_step['number']}: {current_step['title']}")


def _show_welcome(role: str):
    st.markdown("""
    <div style="text-align:center; padding:2rem 1rem 1rem; color:#94a3b8;">
        <div style="font-size:3.5rem; margin-bottom:0.5rem;">👋</div>
        <h3 style="color:#475569; margin-bottom:0.25rem;">Welcome to SE Team Chatbot!</h3>
        <p style="color:#64748b;">Ask me anything about development setup, team processes, or general support.</p>
    </div>
    """, unsafe_allow_html=True)

    if role == "admin":
        st.markdown("""
- 🔧 **Dev Setup** — Step-by-step environment setup guide
- 📅 **Onboarding** — Agendas & work schedules for new joiners
- 💬 **General Chat** — Team docs, tools & general support
- 🖼️ **Image Analysis** — Upload an image and ask about it
        """)
    else:
        st.markdown("""
- 🔧 **Dev Setup** — Step-by-step environment setup guide
- 💬 **General Chat** — Team docs, tools & general support
- 🖼️ **Image Analysis** — Upload an image and ask about it
        """)


def _show_help(role: str):
    if role == "admin":
        help_text = """
## 🤖 SE Team Chatbot Help — Admin

**Available Modes:**
1. **General Chat** — Ask questions about team processes, tools, and documentation
2. **Dev Setup Assistant** — Step-by-step guidance for development environment setup
3. **Onboarding** — Create agendas and generate work schedules around your classes

**Onboarding Features (Admin only):**
- **Agendas**: Provide name/role for a personalized agenda
- **Work Schedules**: Upload an image of your class timetable or paste it as text
- **Constraints**: 20 hours/week, Tue-Fri, 9am-5pm, single shift per day, 15-min commute buffer

**How to Use:**
- Use the sidebar to switch modes
- In **Onboarding Mode**, use the file uploader for images
- Type your message and press Enter or click Send
- In dev setup mode, use commands like "next", "previous", "status"
        """
    else:
        help_text = """
## 🤖 SE Team Chatbot Help — Student

**Available Modes:**
1. **General Chat** — Ask questions about team processes, tools, and documentation
2. **Dev Setup Assistant** — Step-by-step guidance for development environment setup

**How to Use:**
- Use the sidebar to switch between General Chat and Dev Setup
- Upload an image in the sidebar (General Chat mode) and ask about it
- Type your message and press Enter or click Send
- In dev setup mode, use commands like "next", "previous", "status"

> 💡 **Need Onboarding access?** Ask your team admin to log in with the Admin role.
        """

    st.session_state.chat_history.append({"role": "assistant", "content": help_text})


def process_user_input(user_input: str, image_bytes: Optional[bytes] = None):
    response = st.session_state.chatbot.process_message(
        user_input,
        mode=st.session_state.current_mode,
        image_bytes=image_bytes
    )
    display_input = user_input
    if image_bytes and not user_input:
        display_input = "[Sent an image of class timetable]"
    elif image_bytes:
        display_input = f"{user_input} [with attached image]"

    st.session_state.chat_history.append({"role": "user", "content": display_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    role = st.session_state.user_role

    if role is None:
        if st.session_state.show_login:
            show_admin_login()
        else:
            show_landing_page()
    else:
        # Make sure chatbot is loaded
        if st.session_state.chatbot is None:
            with st.spinner("🚀 Initializing SE Team Chatbot..."):
                _init_chatbot()
        show_chatbot()


if __name__ == "__main__":
    main()