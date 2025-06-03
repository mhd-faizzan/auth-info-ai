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

# Professional Light Theme with Enhanced Visibility
st.markdown("""
    <style>
        :root {
            --primary: #2563EB;
            --primary-hover: #1E40AF;
            --secondary: #3B82F6;
            --bg: #FFFFFF;
            --card-bg: #FFFFFF;
            --text: #111827;
            --text-secondary: #4B5563;
            --border: #E5E7EB;
            --success: #10B981;
            --accent: #60A5FA;
            --highlight: #EFF6FF;
            --button-text: #FFFFFF;
            --tab-inactive: #F3F4F6;
        }
        
        /* Base styles */
        html, body, .stApp {
            background-color: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        /* Main container */
        .main .block-container {
            padding: 2rem 4rem;
            max-width: 1400px;
        }
        
        /* Hero Section */
        .hero-container {
            text-align: center;
            margin-bottom: 3rem;
            padding: 3rem 0;
        }
        
        .hero-title {
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            margin-bottom: 1rem !important;
            background: linear-gradient(90deg, #2563EB, #3B82F6);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        
        .hero-subtitle {
            font-size: 1.25rem !important;
            color: var(--text-secondary) !important;
            max-width: 700px;
            margin: 0 auto 2rem auto !important;
        }
        
        /* Improved Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            background: var(--tab-inactive);
            padding: 0.5rem;
            border-radius: 12px;
            margin: 1rem 0 2rem 0;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            border-radius: 8px;
            background: transparent !important;
            color: var(--text-secondary) !important;
            font-weight: 600;
            transition: all 0.2s ease;
            border: none;
            margin: 0;
            flex: 1;
            text-align: center;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--primary) !important;
            color: var(--button-text) !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .stTabs [aria-selected="false"]:hover {
            background: #E5E7EB !important;
        }
        
        /* Auth Cards */
        .auth-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 1rem 0;
        }
        
        .auth-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 3rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .auth-title {
            font-size: 1.75rem !important;
            font-weight: 700 !important;
            margin-bottom: 2rem !important;
            color: var(--text) !important;
            text-align: center;
        }
        
        /* Form Elements */
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text);
        }
        
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            background: white !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            padding: 0.875rem 1rem !important;
            border-radius: 8px !important;
            width: 100% !important;
            font-size: 1rem !important;
        }
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
            outline: none !important;
        }
        
        /* Buttons */
        .stButton>button {
            background: var(--primary) !important;
            color: var(--button-text) !important;
            border: none !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.2s ease !important;
            width: 100%;
            margin-top: 1rem;
        }
        
        .stButton>button:hover {
            background: var(--primary-hover) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* User Avatar */
        .user-avatar {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
            margin-right: 1.5rem;
        }
        
        /* Response Cards */
        .response-card {
            margin-top: 2rem;
            padding: 2rem;
            background: white;
            border-radius: 12px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }
        
        .source-item {
            padding: 1.25rem;
            margin: 1rem 0;
            background: white;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg) !important;
            border-right: 1px solid var(--border) !important;
        }
        
        .feedback-container {
            padding: 1.75rem;
            margin-bottom: 2rem;
            background: white;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .link-button {
            display: inline-block;
            background: var(--primary);
            color: white !important;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            font-weight: 600;
            width: 100%;
            transition: all 0.2s ease;
            margin-top: 1.5rem;
        }
        
        .link-button:hover {
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            color: white;
        }
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
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
    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">FactVerify Ai</h1>
            <p class="hero-subtitle">
                Academic-grade fact verification powered by AI. Get accurate information with verified sources.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        # Improved tabs with equal width
        tab1, tab2 = st.tabs(["LOGIN", "SIGN UP"])
        
        with tab1:
            with st.container():
                st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
                with st.form(key="login_form"):
                    st.markdown("<h3 class='auth-title'>Welcome Back</h3>", unsafe_allow_html=True)
                    
                    # Form group with label
                    st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                    st.markdown("<label class='form-label'>Email Address</label>", unsafe_allow_html=True)
                    email = st.text_input("", placeholder="Enter your email", key="login_email", label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Form group with label
                    st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                    st.markdown("<label class='form-label'>Password</label>", unsafe_allow_html=True)
                    password = st.text_input("", type="password", placeholder="Enter your password", key="login_pass", label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.form_submit_button("Login to Your Account"):
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
                st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
                with st.form(key="signup_form"):
                    st.markdown("<h3 class='auth-title'>Create Account</h3>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                        st.markdown("<label class='form-label'>First Name</label>", unsafe_allow_html=True)
                        first_name = st.text_input("", placeholder="Enter first name", key="signup_fname", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                        st.markdown("<label class='form-label'>Last Name</label>", unsafe_allow_html=True)
                        last_name = st.text_input("", placeholder="Enter last name", key="signup_lname", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                    st.markdown("<label class='form-label'>Email Address</label>", unsafe_allow_html=True)
                    email = st.text_input("", placeholder="Enter your email", key="signup_email", label_visibility="collapsed")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                        st.markdown("<label class='form-label'>Password</label>", unsafe_allow_html=True)
                        password = st.text_input("", type="password", placeholder="Create password", key="signup_pass", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown("<div class='form-group'>", unsafe_allow_html=True)
                        st.markdown("<label class='form-label'>Confirm Password</label>", unsafe_allow_html=True)
                        confirm_pass = st.text_input("", type="password", placeholder="Confirm password", key="signup_cpass", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.form_submit_button("Create New Account"):
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
# 5. MAIN APP UI
# ======================
def show_main_app():
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name} {last_name[0]}." if first_name and last_name else st.session_state.email.split('@')[0]
    
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    # Header with greeting
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2.5rem;">
                    <div class="user-avatar">
                        {display_name[0].upper()}
                    </div>
                    <div>
                        <h2 style="margin: 0; color: var(--text); font-size: 1.75rem;">{greeting}, {display_name}</h2>
                        <p style="margin: 0; color: var(--text-secondary); font-size: 1.1rem;">Ready to verify some facts?</p>
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
            <div class="feedback-container">
                <h3 style="color: var(--primary); margin-top: 0;">Help Improve FactVerify</h3>
                <p style="color: var(--text-secondary);">
                    Your feedback helps us enhance the experience for everyone.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        feedback_url = "https://docs.google.com/forms/d/e/1FAIpQLSdlh_ogw2I3hByMMGTJRFtWwAzKWklAAzFvO7g7ApinQ6jaSw/viewform"
        st.markdown(f"""
            <a href="{feedback_url}" target="_blank" class="link-button">
                Provide Feedback
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
                with st.spinner("🔍 Analyzing and verifying information..."):
                    response, sources = get_verified_response(prompt)
                    
                    if response:
                        st.markdown(f"""
                            <div class="response-card">
                                <p style="color: var(--text); font-size: 1.1rem; line-height: 1.7;">{response}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sources:
                            st.markdown("""
                                <div style="margin-top: 2.5rem;">
                                    <h3 style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                                        📚 Verified Sources:
                                    </h3>
                            """, unsafe_allow_html=True)
                            
                            for source in sources:
                                st.markdown(f"""
                                    <div class="source-item">
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
