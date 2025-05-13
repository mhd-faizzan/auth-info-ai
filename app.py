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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional CSS with ChatGPT-like aesthetics
# Replace your existing CSS with this more compact version:
st.markdown("""
    <style>
        :root {
            --primary: #10A37F;
            --primary-hover: #0E8E6D;
            --secondary: #6E6E80;
            --bg: #FFFFFF;
            --card-bg: #F7F7F8;
            --text: #343541;
            --text-secondary: #565869;
            --border: #D9D9E3;
            --success: #10B981;
            --error: #EF4146;
        }
        
        /* Compact containers */
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        /* Compact header */
        .header {
            text-align: center;
            margin: 1.5rem 0 2rem;
        }
        
        /* More compact auth card */
        .auth-card {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 0 auto;
            width: 100%;
            max-width: 400px;
        }
        
        /* Compact form elements */
        .stTextInput input, 
        .stTextInput input:focus,
        .stTextArea textarea, 
        .stTextArea textarea:focus {
            padding: 0.6rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Compact buttons */
        .stButton button {
            padding: 0.6rem 1.25rem !important;
            font-size: 0.9rem !important;
            margin-top: 0.25rem !important;
        }
        
        /* Compact tabs */
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
        
        /* Compact dashboard */
        .dashboard-header {
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
        }
        
        /* Compact user info */
        .user-avatar {
            width: 36px;
            height: 36px;
            font-size: 0.9rem;
        }
        
        /* Compact response cards */
        .response-card {
            padding: 1.25rem;
            margin: 1.25rem 0;
        }
        
        /* Compact source items */
        .source-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
        }
        
        /* Compact titles */
        .auth-title {
            font-size: 1.1rem;
            margin-bottom: 1.25rem;
        }
        
        .query-title {
            font-size: 1.1rem;
            margin-bottom: 0.4rem;
        }
        
        .query-subtitle {
            font-size: 0.85rem;
            margin-bottom: 1.25rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state (unchanged)
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'email': "",
        'first_name': "",
        'last_name': "",
        'id_token': ""
    })

# ======================
# 2. FIREBASE INTEGRATION (unchanged)
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
# 3. LLM INTEGRATION (unchanged)
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
# 4. AUTHENTICATION UI (Professional redesign)
# ======================
def show_auth_ui():
    st.markdown("""
        <div class="main-container">
            <div class="header">
                <h1>FactVerify Pro</h1>
                <p>Academic-grade fact verification powered by AI</p>
            </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form(key="login_form"):
                st.markdown("<div class='auth-title'>Welcome back</div>", unsafe_allow_html=True)
                
                email = st.text_input("Email", placeholder="your@email.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_pass")
                
                if st.form_submit_button("Continue", use_container_width=True):
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
        
        with tab2:
            with st.form(key="signup_form"):
                st.markdown("<div class='auth-title'>Create your account</div>", unsafe_allow_html=True)
                
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
        st.markdown("""
            <div class="footer">
                © 2023 FactVerify Pro. All rights reserved.
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 5. MAIN APP UI (Professional redesign)
# ======================
def show_main_app():
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name} {last_name[0]}." if first_name and last_name else st.session_state.email.split('@')[0]
    
    # Time-based greeting
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    st.markdown("""
        <div class="main-container">
            <div class="dashboard-header">
                <div class="user-info">
                    <div class="user-avatar">
                        {0}
                    </div>
                    <div class="user-text">
                        <h3>{1}, {2}</h3>
                        <p>Ready to verify some facts?</p>
                    </div>
                </div>
                <div>
                    <button onclick="window.location.href='?logout=true'" style="
                        background: none;
                        border: 1px solid var(--border);
                        border-radius: 6px;
                        padding: 0.5rem 1rem;
                        font-size: 0.9rem;
                        cursor: pointer;
                        color: var(--text);
                    ">Log out</button>
                </div>
            </div>
    """.format(
        display_name[0].upper(),
        greeting,
        display_name
    ), unsafe_allow_html=True)
    
    # Query form
    with st.form(key="query_form"):
        st.markdown("<div class='query-title'>New verification</div>", unsafe_allow_html=True)
        st.markdown("<div class='query-subtitle'>Enter a statement or question to verify with academic sources</div>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Your research query:",
            placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=150,
            key="query_input",
            label_visibility="collapsed"
        )
        
        submitted = st.form_submit_button("Verify", use_container_width=True)
        
        if submitted:
            if not prompt:
                st.warning("Please enter a question")
            else:
                with st.spinner("Analyzing with academic sources..."):
                    response, sources = get_verified_response(prompt)
                    
                    if response:
                        st.markdown(f"""
                            <div class="response-card">
                                {response}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sources:
                            st.markdown("<div class='sources-title'>Verified sources</div>", unsafe_allow_html=True)
                            for source in sources:
                                st.markdown(f"""
                                    <div class="source-item">
                                        {source}
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("Failed to get verified response. Please check:")
                        st.error("\n".join(sources) if sources else "Unknown error occurred")
    
    st.markdown("""
        <div class="footer">
            © 2023 FactVerify Pro. All rights reserved.
        </div>
        </div>
    """, unsafe_allow_html=True)

# ======================
# 6. APP ROUTING (unchanged)
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
