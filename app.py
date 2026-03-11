import streamlit as st
import os
from typing import Optional
import markdown as md
from chatbot.core import MegaChatbot
from config.settings import APP_TITLE, APP_DESCRIPTION, ASU_AI_API_TOKEN

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with Modern Design
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .block-container {
        background-color: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
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
    
    /* Chat message styling */
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
    
    .user-avatar {
        background: rgba(255,255,255,0.25);
    }
    
    .assistant-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: none;
        margin-left: 20%;
    }
    
    .user-message strong {
        color: #fff;
        font-weight: 600;
    }
    
    .assistant-message {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #667eea;
        margin-right: 20%;
        color: #1e293b;
    }
    
    .assistant-message strong {
        color: #667eea;
        font-weight: 600;
    }
    
    .assistant-message h3, .assistant-message h4 {
        color: #334155;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .assistant-message table {
        border-collapse: collapse;
        width: 100%;
        margin: 0.75rem 0;
        font-size: 0.9rem;
    }
    
    .assistant-message th, .assistant-message td {
        border: 1px solid #cbd5e1;
        padding: 0.5rem 0.75rem;
        text-align: left;
    }
    
    .assistant-message th {
        background-color: #e2e8f0;
        font-weight: 600;
        color: #334155;
    }
    
    .assistant-message tr:nth-child(even) {
        background-color: #f1f5f9;
    }
    
    .assistant-message hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .assistant-message ul, .assistant-message ol {
        padding-left: 1.5rem;
        margin: 0.5rem 0;
    }
    
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
    
    /* Inline code inside paragraphs and list items: light style */
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
    
    .assistant-message ul, .assistant-message ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    .css-1d391kg h2, .css-1d391kg h3, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #fff !important;
    }
    
    .css-1d391kg p, .css-1d391kg label,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Text input styling - chat input box */
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
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
        background-color: #ffffff !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Selectbox */
    .stSelectbox {
        color: #fff;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background-color: #10b981;
        color: white;
    }
    
    .status-error {
        background-color: #ef4444;
        color: white;
    }
    
    /* Mode indicator */
    .mode-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8f 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_chatbot():
    """Initialize and cache the chatbot instance to avoid reloading embeddings."""
    return MegaChatbot()

# Initialize session state
if 'chatbot' not in st.session_state:
    with st.spinner('🚀 Initializing SE Team Chatbot...'):
        st.session_state.chatbot = get_chatbot()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "general"
if 'image_upload_counter' not in st.session_state:
    st.session_state.image_upload_counter = 0

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 SE Team Chatbot</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{APP_DESCRIPTION} • Powered by ASU AI Platform </p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        st.markdown("---")
        
        # Mode Selection with visual indicator
        st.markdown("### 🔧 Assistant Mode")
        mode = st.selectbox(
            "Choose your mode:",
            ["General Chat", "Dev Setup", "Onboarding"],
            index=["general", "dev_setup", "onboarding"].index(st.session_state.current_mode),
            key="mode_selector"
        )
        
        mode_map = {
            "General Chat": "general",
            "Dev Setup": "dev_setup",
            "Onboarding": "onboarding"
        }
        selected_mode = mode_map[mode]
        
        if selected_mode != st.session_state.current_mode:
            st.session_state.current_mode = selected_mode
            # Clear chat history when switching modes
            st.session_state.chat_history = []
            response = st.session_state.chatbot.switch_mode(selected_mode)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
            
        # Image Upload — available in General Chat and Onboarding modes
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
        
        

    
    # Main content area
    # Current mode indicator
    mode_emoji = {"general": "💬", "dev_setup": "🔧", "onboarding": "📅"}
    mode_names = {"general": "General Chat", "dev_setup": "Dev Setup Assistant", "onboarding": "Onboarding"}
    
    st.markdown(f"""
    <div class="mode-indicator">
        {mode_emoji.get(st.session_state.current_mode, '💬')} 
        Current Mode: {mode_names.get(st.session_state.current_mode, 'General Chat')}
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #94a3b8;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">👋</div>
                <h3 style="color: #475569;">Welcome to SE Team Chatbot!</h3>
                <p>Ask me anything about development setup, team processes, or general support.</p>
            </div>
            """, unsafe_allow_html=True)
        
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
                # Convert markdown to HTML for proper rendering inside styled container
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
    
    # Input area at the bottom
    st.markdown("---")
    
    # Initialize message counter for clearing input
    if 'message_counter' not in st.session_state:
        st.session_state.message_counter = 0
    
    # Callback function for when user submits input
    def on_input_submit():
        """Handle input submission via Enter key or button."""
        user_input = st.session_state.get(f'message_input_{st.session_state.message_counter}', '').strip()
        img_bytes = None
        if uploaded_image:
            img_bytes = uploaded_image.getvalue()
            
        if user_input or img_bytes:
            # Use a more descriptive spinner for long-running tasks
            input_lower = (user_input or "").lower()
            if st.session_state.current_mode == "onboarding" and any(w in input_lower for w in ["agenda", "onboarding plan", "welcome"]):
                spinner_msg = "📝 Generating your 21-day onboarding agenda... This may take a few minutes."
            elif img_bytes:
                spinner_msg = "🖼️ Processing image..."
            else:
                spinner_msg = "🤔 Thinking..."
            with st.spinner(spinner_msg):
                process_user_input(user_input, img_bytes)
            # Increment counter to create a new widget with empty value
            st.session_state.message_counter += 1
            # Clear the image uploader if an image was used
            if img_bytes:
                st.session_state.image_upload_counter += 1
    
    col_input, col_send, col_help = st.columns([6, 1, 1])
    
    with col_input:
        # Use text_input with counter-based key for proper clearing
        user_input = st.text_input(
            "💭 Type your message here...",
            key=f"message_input_{st.session_state.message_counter}",
            placeholder="Ask me to create a work schedule! You can also upload a timetable image in the sidebar." if st.session_state.current_mode == "onboarding" else "Ask me anything! You can also upload an image in the sidebar. (Press Enter to send)",
            label_visibility="collapsed",
            on_change=on_input_submit
        )
    
    with col_send:
        if st.button("🚀 Send", type="primary", use_container_width=True):
            on_input_submit()
    
    with col_help:
        if st.button("💡 Help", use_container_width=True):
            show_help()
            st.rerun()
    
    # Dev setup progress (if in dev_setup mode)
    if st.session_state.current_mode == "dev_setup":
        progress = st.session_state.chatbot.dev_setup_assistant.get_step_progress()
        st.markdown("---")
        st.markdown(f"**📈 Setup Progress: {progress['percentage']:.1f}%**")
        st.progress(progress['percentage'] / 100)
        
        current_step = st.session_state.chatbot.dev_setup_assistant.get_current_step()
        if current_step:
            st.caption(f"Step {current_step['number']}: {current_step['title']}")

def process_user_input(user_input: str, image_bytes: Optional[bytes] = None):
    """Process user input and update chat history."""
    response = st.session_state.chatbot.process_message(user_input, image_bytes=image_bytes)
    
    # If image was uploaded, add a note to the user message
    display_input = user_input
    if image_bytes and not user_input:
        display_input = "[Sent an image of class timetable]"
    elif image_bytes:
        display_input = f"{user_input} [with attached image]"
        
    st.session_state.chat_history.append({"role": "user", "content": display_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

def show_help():
    """Show help information."""
    help_text = """
## 🤖 SE Team Mega Chatbot Help

**Available Modes:**
1. **General Chat** - Ask questions about team processes, tools, and documentation
2. **Dev Setup Assistant** - Step-by-step guidance for development environment setup
3. **Onboarding** - Create agendas and generate work schedules around your classes

**Onboarding Features:**
- **Agendas**: Provide name/role for a personalized agenda
- **Work Schedules**: Upload an image of your class timetable or paste it as text
- **Constraints**: 20 hours/week, Tue-Fri, 9am-5pm, single shift per day, 15-min commute buffer

**How to Use:**
- Use the sidebar to switch modes
- In **Onboarding Mode**, use the file uploader for images
- Type your message and press Enter or click Send
- In dev setup mode, use commands like "next", "previous", "status"

**Need Help?**
- Type "help" in any mode for specific commands
- Use sidebar controls for quick actions
    """
    
    st.session_state.chat_history.append({"role": "assistant", "content": help_text})

if __name__ == "__main__":
    main()