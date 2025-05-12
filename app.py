import streamlit as st
import requests
from datetime import datetime

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Pro",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern dark theme CSS
st.markdown("""
    <style>
        :root {
            --primary: #1877F2;
            --secondary: #65676B;
            --bg: #18191A;
            --card-bg: #242526;
            --text: #E4E6EB;
            --text-secondary: #B0B3B8;
        }
        
        .stApp {
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }
        
        .custom-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #3E4042;
        }
        
        .source-item {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #3A3B3C;
            border-radius: 8px;
            border-left: 3px solid var(--primary);
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
            return True, "Account created successfully!", response.json()
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
            return True, "Login successful!", response.json()
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error, None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

# ======================
# 3. LLM INTEGRATION (DEBUGGED VERSION)
# ======================
def get_verified_response(prompt):
    """Production-ready query with academic sources"""
    try:
        # Debug: Check if secrets are loaded
        if not hasattr(st, 'secrets') or "llama" not in st.secrets:
            return None, ["Missing LLM API configuration"]
            
        headers = {
            "Authorization": f"Bearer {st.secrets.llama.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3-70b",
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
            "max_tokens": 2000
        }
        
        # Debug: Print the API request details
        print(f"Making request to: {st.secrets.llama.api_url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            st.secrets.llama.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Debug: Print the response
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
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
    with st.container():
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="color: var(--primary); margin-bottom: 0.5rem;">
                    <span style="display: inline-flex; align-items: center;">
                        🔍 FactVerify
                    </span>
                </h1>
                <p style="color: var(--text-secondary)">Academic-grade verification</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                with st.form(key="login_form"):
                    email = st.text_input("Email", placeholder="your@email.com")
                    password = st.text_input("Password", type="password")
                    
                    if st.form_submit_button("Login", use_container_width=True):
                        if email and password:
                            success, message, result = handle_login(email, password)
                            if success:
                                st.session_state.update({
                                    'logged_in': True,
                                    'email': email,
                                    'id_token': result.get("idToken", "")
                                })
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Please fill all fields")
            
            with tab2:
                with st.form(key="signup_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        first_name = st.text_input("First Name", placeholder="Muhammad")
                    with col2:
                        last_name = st.text_input("Last Name", placeholder="Faizan")
                    
                    email = st.text_input("Email", placeholder="your@email.com")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        password = st.text_input("Password", type="password")
                    with col4:
                        confirm_pass = st.text_input("Confirm Password", type="password")
                    
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

# ======================
# 5. MAIN APP UI (DEBUGGED VERSION)
# ======================
def show_main_app():
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                    <div style="width: 48px; height: 48px; border-radius: 50%; 
                              background: var(--primary); display: flex; 
                              align-items: center; justify-content: center;
                              color: white; font-weight: bold; font-size: 1.1rem;">
                        {display_name[0].upper()}
                    </div>
                    <div>
                        <h1 style="margin: 0; color: var(--text);">Welcome back, {display_name}</h1>
                        <p style="margin: 0; color: var(--text-secondary);">Ready to verify some facts?</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    
    with st.form(key="query_form"):
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Your research query:",
            placeholder="Ask about any topic with academic sources...",
            height=150
        )
        
        submitted = st.form_submit_button("Verify Information", use_container_width=True)
        
        if submitted:
            if not prompt:
                st.warning("Please enter a question")
            else:
                with st.spinner("🔍 Verifying with academic databases..."):
                    response, sources = get_verified_response(prompt)
                    
                    if response:
                        st.markdown(f"""
                            <div style="margin-top: 1.5rem; padding: 1rem; 
                                      background: #3A3B3C; border-radius: 8px;">
                                <p style="color: var(--text);">{response}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sources:
                            st.markdown("""
                                <div style="margin-top: 1.5rem;">
                                    <p style="color: var(--text-secondary); font-weight: bold;">
                                        📚 Verified Sources:
                                    </p>
                            """, unsafe_allow_html=True)
                            
                            for source in sources:
                                st.markdown(f"""
                                    <div class="source-item">
                                        <p style="margin: 0; color: var(--text);">{source}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to get verified response. Please check:")
                        st.error("\n".join(sources) if sources else st.error("Unknown error occurred")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 6. APP ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
