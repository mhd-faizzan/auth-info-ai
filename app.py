import streamlit as st
import requests
from datetime import datetime
import random
from streamlit.components.v1 import html

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Ai",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional DeepSeek-inspired theme with enhanced UI
st.markdown("""
    <style>
        :root {
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --secondary: #3B82F6;
            --bg: #0F172A;
            --card-bg: #1E293B;
            --text: #F8FAFC;
            --text-secondary: #94A3B8;
            --border: #334155;
            --success: #10B981;
            --accent: #60A5FA;
            --highlight: #1E40AF;
            --button-text: #FFFFFF;
            --sidebar-width: 300px;
        }
        
        /* Base styles */
        html, body, .stApp {
            background-color: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Main container */
        .main .block-container {
            max-width: 1200px;
            padding: 2rem 3rem;
        }
        
        /* Headers */
        h1 {
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text !important;
            background-clip: text !important;
            color: transparent !important;
            margin-bottom: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.75rem !important;
            font-weight: 600 !important;
            color: var(--text) !important;
            margin-bottom: 1rem !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
            font-weight: 500 !important;
            color: var(--text) !important;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--primary) !important;
            color: var(--button-text) !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stButton>button:hover {
            background-color: var(--primary-hover) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.2) !important;
        }
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background-color: var(--card-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
        }
        
        /* Tabs */
        .stTabs [aria-selected="true"] {
            background-color: var(--primary) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: 500 !important;
        }
        
        .stTabs [aria-selected="false"] {
            color: var(--text-secondary) !important;
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg) !important;
            border-right: 1px solid var(--border) !important;
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
        }
        
        /* Custom components */
        .header-container {
            text-align: center;
            margin-bottom: 3rem;
            padding-top: 1rem;
        }
        
        .auth-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem 0;
        }
        
        .auth-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 2.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .auth-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        .user-avatar {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
            margin-right: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .response-card {
            margin-top: 2rem;
            padding: 2rem;
            background: var(--card-bg);
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .response-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }
        
        .source-item {
            padding: 1.25rem;
            margin: 1rem 0;
            background: var(--card-bg);
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }
        
        .source-item:hover {
            transform: translateX(8px);
            background: rgba(37, 99, 235, 0.1);
        }
        
        .feedback-container {
            padding: 1.75rem;
            margin-bottom: 2rem;
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .link-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: var(--primary);
            color: var(--button-text) !important;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
            gap: 0.5rem;
        }
        
        .link-button:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(37, 99, 235, 0.2);
            color: var(--button-text);
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-hover);
        }
        
        /* Loading spinner */
        .stSpinner>div>div {
            border-color: var(--primary) transparent transparent transparent !important;
        }
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'email': "",
        'first_name': "",
        'last_name': "",
        'id_token': ""
    })

# ======================
# 2. FIREBASE INTEGRATION
# ======================
def initialize_firebase():
    if not hasattr(st, 'secrets') or "firebase" not in st.secrets:
        st.error("Missing Firebase configuration")
        st.stop()
    
    return {
        "apiKey": st.secrets.firebase.api_key,
        "authDomain": st.secrets.firebase.auth_domain,
        "projectId": st.secrets.firebase.project_id
    }

firebase_config = initialize_firebase()
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"

def handle_signup(first_name, last_name, email, password):
    try:
        response = requests.post(
            FIREBASE_SIGNUP_URL,
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10
        )
        if response.status_code == 200:
            # Update user profile with name
            update_response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={firebase_config['apiKey']}",
                json={
                    "idToken": response.json().get("idToken", ""),
                    "displayName": f"{first_name} {last_name}",
                    "returnSecureToken": True
                },
                timeout=10
            )
            return True, "Account created successfully!", {
                "idToken": response.json().get("idToken", ""),
                "first_name": first_name,
                "last_name": last_name
            }
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error, None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

def handle_login(email, password):
    try:
        response = requests.post(
            FIREBASE_LOGIN_URL,
            json={"email": email, "password": password, "returnSecureToken": True},
            timeout=10
        )
        if response.status_code == 200:
            # Get user info from Firebase
            user_info = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={firebase_config['apiKey']}",
                json={"idToken": response.json().get("idToken", "")},
                timeout=10
            )
            user_data = user_info.json().get("users", [{}])[0]
            names = user_data.get("displayName", "").split() if user_data.get("displayName") else []
            return True, "Login successful!", {
                "idToken": response.json().get("idToken", ""),
                "first_name": names[0] if len(names) > 0 else "",
                "last_name": names[-1] if len(names) > 1 else ""
            }
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error, None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

# ======================
# 3. LLM INTEGRATION
# ======================
def get_verified_response(prompt):
    """Production-ready query with academic sources using Groq API"""
    try:
        if not hasattr(st, 'secrets') or "llama" not in st.secrets:
            return None, ["Missing LLM API configuration"]
            
        headers = {
            "Authorization": f"Bearer {st.secrets.llama.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": f"""You are a senior academic researcher. Provide:
1. Accurate information current to {datetime.now().strftime('%B %Y')}
2. 3-5 academic sources (DOIs or .edu/.gov URLs)
3. Format: [Title](URL) - Author (Year) or DOI:..."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        response = requests.post(
            st.secrets.llama.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            if "###SOURCES###" in content:
                parts = content.split("###SOURCES###")
                return parts[0].strip(), [s.strip() for s in parts[1].split("\n") if s.strip()]
            return content, []
        
        error_msg = response.json().get("error", {}).get("message", "Unknown API error")
        return None, [f"API Error: {error_msg}"]
        
    except Exception as e:
        return None, [f"System Error: {str(e)}"]

# ======================
# 4. AUTHENTICATION UI (UPDATED PROFESSIONAL VERSION)
# ======================
def show_auth_ui():
    st.markdown("""
        <div class="header-container fade-in">
            <h1 style="margin-bottom: 0.5rem;">
                🔍 FactVerify Ai
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                Academic-grade fact verification powered by AI
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.container():
                st.markdown("<div class='auth-card fade-in'>", unsafe_allow_html=True)
                with st.form(key="login_form"):
                    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Welcome back</h3>", unsafe_allow_html=True)
                    
                    email = st.text_input("Email", placeholder="your@email.com", key="login_email")
                    password = st.text_input("Password", type="password", key="login_pass")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.form_submit_button("Login", use_container_width=True):
                            if email and password:
                                with st.spinner("Authenticating..."):
                                    success, message, result = handle_login(email, password)
                                    if success:
                                        st.session_state.update({
                                            'logged_in': True,
                                            'email': email,
                                            'id_token': result.get("idToken", ""),
                                            'first_name': result.get("first_name", ""),
                                            'last_name': result.get("last_name", "")
                                        })
                                        st.rerun()
                                    else:
                                        st.error(message)
                            else:
                                st.error("Please fill all fields")
                    st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            with st.container():
                st.markdown("<div class='auth-card fade-in'>", unsafe_allow_html=True)
                with st.form(key="signup_form"):
                    st.markdown("<h3 style='margin-bottom: 1.5rem;'>Create an account</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name", placeholder="Given Name", key="signup_fname")
                    with col2:
                        last_name = st.text_input("Last Name", placeholder="Family Name", key="signup_lname")
                    
                    email = st.text_input("Email", placeholder="your@email.com", key="signup_email")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        password = st.text_input("Password", type="password", key="signup_pass")
                    with col4:
                        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_cpass")
                    
                    if st.form_submit_button("Create Account", use_container_width=True):
                        if not all([first_name, last_name, email, password, confirm_pass]):
                            st.error("Please fill all fields")
                        elif password != confirm_pass:
                            st.error("Passwords don't match")
                        else:
                            with st.spinner("Creating account..."):
                                success, message, result = handle_signup(first_name, last_name, email, password)
                                if success:
                                    st.session_state.update({
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'logged_in': True,
                                        'email': email,
                                        'id_token': result.get("idToken", "")
                                    })
                                    st.rerun()
                                else:
                                    st.error(message)
                st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 5. MAIN APP UI (UPDATED PROFESSIONAL VERSION)
# ======================
def show_main_app():
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name} {last_name[0]}." if first_name and last_name else st.session_state.email.split('@')[0]
    
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div class="fade-in" style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2.5rem;">
                    <div class="user-avatar">
                        {display_name[0].upper()}
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 600;">{greeting}, {display_name}</h2>
                        <p style="margin: 0; color: var(--text-secondary);">Ready to verify some facts?</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True, key="logout_btn"):
                st.session_state.clear()
                st.rerun()
    
    with st.sidebar:
        st.markdown("""
            <div class="feedback-container fade-in">
                <h3 class="feedback-title">Help Improve FactVerify</h3>
                <p class="feedback-text">
                    We value your feedback to enhance your experience. Share your thoughts or report issues.
                </p>
                <p class="feedback-quote">
                    "Precision in verification leads to clarity in understanding."
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        feedback_url = "https://docs.google.com/forms/d/e/1FAIpQLSdlh_ogw2I3hByMMGTJRFtWwAzKWklAAzFvO7g7ApinQ6jaSw/viewform"
        st.markdown(f"""
            <a href="{feedback_url}" target="_blank" class="link-button fade-in">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                Provide Feedback
            </a>
        """, unsafe_allow_html=True)
    
    with st.form(key="query_form"):
        st.markdown("<h2 style='margin-bottom: 1rem;'>Research Query</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Enter your question or statement to verify with academic sources</p>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Your research query:",
            placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=200,
            key="query_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button(
                "Verify Information", 
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            if not prompt:
                st.warning("Please enter a question")
            else:
                with st.spinner("🔍 Analyzing and verifying information..."):
                    response, sources = get_verified_response(prompt)
                    
                    if response:
                        st.markdown(f"""
                            <div class="response-card fade-in">
                                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                                    </svg>
                                    <h3 style="margin: 0;">Analysis Results</h3>
                                </div>
                                <p style="color: var(--text); font-size: 1.1rem; line-height: 1.7;">{response}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sources:
                            st.markdown("""
                                <div class="fade-in" style="margin-top: 2.5rem;">
                                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                                        </svg>
                                        <h3 style="margin: 0;">Verified Sources</h3>
                                    </div>
                            """, unsafe_allow_html=True)
                            
                            for source in sources:
                                st.markdown(f"""
                                    <div class="source-item fade-in">
                                        <p style="margin: 0; color: var(--text); font-size: 1rem; line-height: 1.6;">{source}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to get verified response. Please check:")
                        st.error("\n".join(sources) if sources else "Unknown error occurred")

# ======================
# 6. APP ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
