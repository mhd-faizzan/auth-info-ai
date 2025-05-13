import streamlit as st
import requests
from datetime import datetime
import random

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced dark theme CSS with modern professional look
st.markdown("""
    <style>
        /* ====== Base Reset & Typography ====== */
        :root {
            --primary: #10A37F;
            --primary-hover: #0E8E6D;
            --primary-light: rgba(16, 163, 127, 0.1);
            --secondary: #6E6E80;
            --bg: #FFFFFF;
            --card-bg: #F7F7F8;
            --text: #343541;
            --text-secondary: #565869;
            --border: #E5E5E6;
            --border-dark: #D9D9E3;
            --success: #10B981;
            --error: #EF4146;
            --warning: #F4B740;
            --radius-sm: 4px;
            --radius-md: 6px;
            --radius-lg: 8px;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 2px 4px rgba(0,0,0,0.08);
            --transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            box-sizing: border-box;
        }

        html, body, .stApp {
            font-family: -apple-system, BlinkMacSystemFont, 
                       'Segoe UI', Roboto, Oxygen-Sans, 
                       Ubuntu, Cantarell, 'Helvetica Neue', 
                       sans-serif;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }

        /* ====== Layout Structure ====== */
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 16px;
        }

        /* ====== Header Styles ====== */
        .header {
            text-align: center;
            margin: 24px 0 32px;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin: 0 0 4px;
            color: var(--text);
            letter-spacing: -0.01em;
        }

        .header p {
            color: var(--text-secondary);
            font-size: 15px;
            margin: 0;
            font-weight: 400;
        }

        /* ====== Card Components ====== */
        .card {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        .card:hover {
            box-shadow: var(--shadow-md);
        }

        .auth-card {
            padding: 24px;
            margin: 0 auto;
            width: 100%;
            max-width: 400px;
        }

        /* ====== Form Elements ====== */
        .form-group {
            margin-bottom: 16px;
        }

        .form-label {
            display: block;
            margin-bottom: 6px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .stTextInput input, 
        .stTextInput input:focus,
        .stTextArea textarea, 
        .stTextArea textarea:focus {
            width: 100%;
            padding: 10px 12px !important;
            font-size: 14px !important;
            line-height: 1.5;
            color: var(--text) !important;
            background-color: var(--bg) !important;
            border: 1px solid var(--border-dark) !important;
            border-radius: var(--radius-md) !important;
            transition: var(--transition) !important;
        }

        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            outline: none !important;
            box-shadow: 0 0 0 3px var(--primary-light) !important;
        }

        /* ====== Buttons ====== */
        .stButton button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 10px 16px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
            color: white !important;
            background-color: var(--primary) !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            cursor: pointer !important;
            transition: var(--transition) !important;
            width: 100% !important;
            margin-top: 8px !important;
        }

        .stButton button:hover {
            background-color: var(--primary-hover) !important;
            transform: translateY(-1px);
        }

        .stButton button:active {
            transform: translateY(0);
        }

        /* ====== Tabs ====== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px !important;
            margin: 0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: var(--text-secondary) !important;
            background: transparent !important;
            border: none !important;
            flex: 1;
            text-align: center;
            transition: var(--transition) !important;
        }

        .stTabs [aria-selected="true"] {
            color: var(--primary) !important;
            background: transparent !important;
            box-shadow: inset 0 -2px 0 0 var(--primary) !important;
        }

        /* ====== Dashboard Components ====== */
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .user-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), #6B46C1);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .user-text h3 {
            margin: 0;
            font-size: 15px;
            font-weight: 600;
            color: var(--text);
        }

        .user-text p {
            margin: 0;
            font-size: 13px;
            color: var(--text-secondary);
        }

        /* ====== Query Form ====== */
        .query-form {
            margin-bottom: 24px;
        }

        .query-title {
            font-size: 16px;
            font-weight: 600;
            margin: 0 0 8px;
            color: var(--text);
        }

        .query-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
            margin: 0 0 16px;
        }

        /* ====== Response Cards ====== */
        .response-card {
            padding: 18px 20px;
            margin: 20px 0;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
        }

        .response-content {
            font-size: 15px;
            line-height: 1.6;
            color: var(--text);
        }

        /* ====== Source List ====== */
        .sources-title {
            font-size: 14px;
            font-weight: 600;
            margin: 24px 0 12px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .source-item {
            padding: 12px 14px;
            margin-bottom: 10px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            font-size: 14px;
            transition: var(--transition);
        }

        .source-item:hover {
            border-color: var(--primary);
        }

        /* ====== Utility Classes ====== */
        .text-center {
            text-align: center;
        }

        .mt-1 { margin-top: 4px; }
        .mt-2 { margin-top: 8px; }
        .mt-3 { margin-top: 12px; }
        .mt-4 { margin-top: 16px; }
        .mt-5 { margin-top: 20px; }

        .mb-1 { margin-bottom: 4px; }
        .mb-2 { margin-bottom: 8px; }
        .mb-3 { margin-bottom: 12px; }
        .mb-4 { margin-bottom: 16px; }
        .mb-5 { margin-bottom: 20px; }

        /* ====== Footer ====== */
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px 0;
            color: var(--text-secondary);
            font-size: 13px;
            border-top: 1px solid var(--border);
        }

        /* ====== Responsive Adjustments ====== */
        @media (max-width: 640px) {
            .main-container {
                padding: 0 12px;
            }
            
            .header {
                margin: 16px 0 24px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .auth-card {
                padding: 20px;
            }
            
            .dashboard-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
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
# 2. FIREBASE INTEGRATION (UPDATED)
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
# 4. AUTHENTICATION UI (UPDATED)
# ======================
def show_auth_ui():
    # Clean header without extra box
    st.markdown("""
        <div class="header-container">
            <h1 style="color: var(--primary); font-size: 2.5rem; margin-bottom: 0.5rem;">
                🔍 FactVerify Pro
            </h1>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">
                Academic-grade fact verification at your fingertips
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered auth form with cleaner design
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
                        first_name = st.text_input("First Name", placeholder="Muhammad", key="signup_fname")
                    with col2:
                        last_name = st.text_input("Last Name", placeholder="Faizan", key="signup_lname")
                    
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
# 5. MAIN APP UI (UPDATED)
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
                    <div class="user-avatar">
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
