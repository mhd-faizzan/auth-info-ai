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

# Premium dark theme with vibrant accents for presentations
st.markdown("""
    <style>
        :root {
            --primary: #6C63FF;
            --primary-hover: #5A52E0;
            --secondary: #A5A7FF;
            --bg: #121212;
            --card-bg: #1E1E1E;
            --text: #FFFFFF;
            --text-secondary: #B0B0B0;
            --border: #2E2E2E;
            --success: #00C853;
            --accent: #FF6584;
            --accent-hover: #E04D6B;
        }
        
        .stApp {
            background-color: var(--bg) !important;
            color: var(--text) !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
            background-image: radial-gradient(circle at 25% 25%, rgba(108, 99, 255, 0.15) 0%, transparent 55%);
        }
        
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
            border-radius: 16px;
            padding: 2.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
        }
        
        .stTextInput input, .stTextInput input:focus,
        .stTextArea textarea, .stTextArea textarea:focus {
            background: #2A2A2A !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            padding: 12px !important;
            border-radius: 12px !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, 
        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
        }
        
        .stButton button {
            background: var(--primary) !important;
            color: white !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .stButton button:hover {
            background: var(--primary-hover) !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(108, 99, 255, 0.25);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            border-radius: 12px;
            background: transparent;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary) !important;
            color: white !important;
            font-weight: 600;
        }
        
        .source-item {
            padding: 1.25rem;
            margin: 1rem 0;
            background: #2A2A2A;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .source-item:hover {
            transform: translateX(8px);
            background: #333333;
        }
        
        .user-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
            margin-right: 1.5rem;
            box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
        }
        
        .response-card {
            margin-top: 2rem;
            padding: 2rem;
            background: #2A2A2A;
            border-radius: 16px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .response-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
        }
        
        /* Sidebar specific styles */
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg) !important;
            border-right: 1px solid var(--border) !important;
            background-image: radial-gradient(circle at 75% 25%, rgba(108, 99, 255, 0.1) 0%, transparent 55%);
        }
        
        .feedback-container {
            padding: 1.75rem;
            margin-bottom: 2rem;
            background: #2A2A2A;
            border-radius: 16px;
            border: 1px solid var(--border);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .feedback-title {
            color: var(--primary) !important;
            margin-top: 0 !important;
            font-size: 1.25rem !important;
        }
        
        .feedback-text {
            color: var(--text-secondary) !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
        }
        
        .feedback-quote {
            color: var(--secondary) !important;
            font-size: 0.9rem !important;
            font-style: italic !important;
            border-left: 3px solid var(--primary);
            padding-left: 1rem;
            margin-top: 1rem;
        }
        
        /* Custom link button style */
        .link-button {
            display: inline-block;
            background: var(--primary);
            color: white !important;
            padding: 14px 28px;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 1.5rem;
        }
        
        .link-button:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(108, 99, 255, 0.25);
            color: white;
        }
        
        /* Glow effect for presentation focus */
        .glow-effect {
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                box-shadow: 0 0 5px rgba(108, 99, 255, 0.5);
            }
            to {
                box-shadow: 0 0 20px rgba(108, 99, 255, 0.8);
            }
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--card-bg);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-hover);
        }
        
        /* Pulse animation for important elements */
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.02);
            }
            100% {
                transform: scale(1);
            }
        }
    </style>
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
# 4. AUTHENTICATION UI
# ======================
def show_auth_ui():
    # Vibrant header with accent colors
    st.markdown("""
        <div class="header-container">
            <h1 style="color: var(--primary); font-size: 2.75rem; margin-bottom: 0.5rem;">
                🔍 <span style="background: linear-gradient(135deg, var(--primary), var(--accent)); 
                -webkit-background-clip: text; background-clip: text; color: transparent;">FactVerify Ai</span>
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.2rem;">
                Academic-grade fact verification at your fingertips
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered auth form with premium design
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.container():
                st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
                with st.form(key="login_form"):
                    st.markdown("<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Welcome back</h3>", unsafe_allow_html=True)
                    
                    email = st.text_input("Email", placeholder="your@email.com", key="login_email")
                    password = st.text_input("Password", type="password", key="login_pass")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.form_submit_button("Login", use_container_width=True):
                            if email and password:
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
                st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
                with st.form(key="signup_form"):
                    st.markdown("<h3 style='color: var(--text); margin-bottom: 1.5rem;'>Create an account</h3>", unsafe_allow_html=True)
                    
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
# 5. MAIN APP UI
# ======================
def show_main_app():
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]
    
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    # Motivational messages
    motivational_messages = [
        "What fact shall we verify today?",
        "Ready to uncover the truth?",
        "Knowledge is power - let's find some!",
        "Every search brings us closer to truth",
        "Let's explore something fascinating!"
    ]
    random_message = random.choice(motivational_messages)
    
    # Header with greeting
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;">
                    <div class="user-avatar pulse">
                        {display_name[0].upper()}
                    </div>
                    <div>
                        <h1 style="margin: 0; color: var(--text); font-size: 1.8rem;">{greeting}, {display_name}</h1>
                        <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">{random_message}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True, key="logout_btn"):
                st.session_state.clear()
                st.rerun()
    
    # Feedback section in sidebar
    with st.sidebar:
        st.markdown("""
            <div class="feedback-container glow-effect">
                <h3 class="feedback-title">Help Us Improve</h3>
                <p class="feedback-text">
                    Your feedback helps us enhance FactVerify Ai for everyone. Share your thoughts 
                    about your experience, suggest improvements, or report any issues you encountered.
                </p>
                <p class="feedback-quote">
                    "Great products are built through continuous improvement based on user feedback."
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Using markdown with link styled as a button
        feedback_url = "https://docs.google.com/forms/d/e/1FAIpQLSdlh_ogw2I3hByMMGTJRFtWwAzKWklAAzFvO7g7ApinQ6jaSw/viewform"
        st.markdown(f"""
            <a href="{feedback_url}" target="_blank" class="link-button">
                Share Your Feedback
            </a>
        """, unsafe_allow_html=True)
    
    # Enhanced query form
    with st.form(key="query_form"):
        st.markdown("<h2 style='color: var(--text); margin-bottom: 1rem;'>Research Query</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: var(--text-secondary); margin-bottom: 1.5rem;'>Enter your question or statement to verify with academic sources</p>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Your research query:",
            placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=200,
            key="query_input",
            label_visibility="collapsed"
        )
        
        submitted = st.form_submit_button("Verify Information", 
                                        use_container_width=True,
                                        type="primary")
        
        if submitted:
            if not prompt:
                st.warning("Please enter a question")
            else:
                with st.spinner("🔍 Verifying with academic databases..."):
                    response, sources = get_verified_response(prompt)
                    
                    if response:
                        st.markdown(f"""
                            <div class="response-card">
                                <p style="color: var(--text); font-size: 1.1rem; line-height: 1.6;">{response}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sources:
                            st.markdown("""
                                <div style="margin-top: 2rem;">
                                    <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">
                                        📚 Verified Sources:
                                    </h3>
                            """, unsafe_allow_html=True)
                            
                            for source in sources:
                                st.markdown(f"""
                                    <div class="source-item">
                                        <p style="margin: 0; color: var(--text); font-size: 1rem;">{source}</p>
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
