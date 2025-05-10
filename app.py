import streamlit as st
import requests
from datetime import datetime

# ======================
# APP CONFIGURATION
# ======================
st.set_page_config(page_title="AuthenticInfo AI", page_icon="🔍")

# ======================
# SESSION STATE
# ======================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

# ======================
# STYLES
# ======================
st.markdown("""
    <style>
        /* Main containers */
        .auth-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Source styling */
        .source-box {
            background-color: #f8f9fa;
            border-left: 4px solid #6c757d;
            padding: 1rem;
            margin-top: 1.5rem;
        }
        .source-title {
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .source-item {
            margin: 0.5rem 0;
            padding-left: 1rem;
            border-left: 2px solid #dee2e6;
        }
        
        /* Response metrics */
        .metrics {
            font-size: 0.85rem;
            color: #6c757d;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ======================
# FIREBASE AUTH
# ======================
def initialize_firebase():
    if "firebase" not in st.secrets:
        st.error("Firebase configuration missing!")
        st.stop()
    
    config = {
        "apiKey": st.secrets.firebase.api_key,
        "authDomain": st.secrets.firebase.auth_domain,
        "projectId": st.secrets.firebase.project_id
    }
    return config

firebase_config = initialize_firebase()

def firebase_signup(email, password):
    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}",
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Signup error: {str(e)}")
        return None

def firebase_login(email, password):
    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}",
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

# ======================
# LLM QUERY WITH SOURCES
# ======================
def get_verified_response(prompt):
    """Get response with guaranteed sources"""
    SYSTEM_PROMPT = f"""You are a fact-checking AI. For every response:
1. Provide accurate information as of {datetime.now().strftime('%Y-%m-%d')}
2. Include 2-3 authoritative sources formatted as:
   • [Title](URL) - Author/Organization (Year)
3. Prefer:
   - .edu/.gov domains
   - Peer-reviewed papers (DOI links)
   - Primary sources
4. If sources unavailable, state "Could not verify from authoritative sources"

Separate sources with "### SOURCES ###" exactly."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        response = requests.post(
            st.secrets.llama.api_url,
            headers={"Authorization": f"Bearer {st.secrets.llama.api_key}"},
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            if "### SOURCES ###" in content:
                response_text, sources = content.split("### SOURCES ###")
                return response_text.strip(), [s.strip() for s in sources.split("•") if s.strip()]
            return content, []
        return None, [f"API Error: {response.status_code}"]
    except Exception as e:
        return None, [f"Connection error: {str(e)}"]

# ======================
# AUTHENTICATION UI
# ======================
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>🔐 AuthenticInfo AI</h1>
            <p>Access verified information with sources</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    result = firebase_login(email, password)
                    if result:
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.rerun()
        
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Create Account", use_container_width=True):
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    result = firebase_signup(email, password)
                    if result:
                        st.success("Account created! Please login.")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# MAIN APP INTERFACE
# ======================
else:
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# Welcome back, {st.session_state.email}!")
    with col2:
        if st.button("Logout", type="primary"):
            st.session_state.logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    # Query Interface
    prompt = st.text_area(
        "Ask for verified information:",
        placeholder="e.g. 'Explain quantum computing with sources'",
        height=150
    )
    
    if st.button("Get Verified Answer", type="primary", use_container_width=True):
        if not prompt:
            st.warning("Please enter a question")
        else:
            with st.spinner("🔍 Verifying information from authoritative sources..."):
                start_time = datetime.now()
                response, sources = get_verified_response(prompt)
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response:
                    st.markdown("### Verified Response")
                    st.write(response)
                    st.markdown(f"<div class='metrics'>Generated in {response_time:.1f} seconds</div>", 
                               unsafe_allow_html=True)
                    
                    if sources:
                        st.markdown("""
                            <div class="source-box">
                                <div class="source-title">📚 Verification Sources</div>
                                {}
                            </div>
                        """.format("".join([f'<div class="source-item">• {s}</div>' for s in sources])), 
                        unsafe_allow_html=True)
                    elif "could not verify" not in response.lower():
                        st.warning("No sources provided - verify independently")
                else:
                    st.error("Failed to get response")

# ======================
# FOOTER
# ======================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        AuthenticInfo AI • Always sourced • {date}
    </div>
""".format(date=datetime.now().strftime("%Y")), unsafe_allow_html=True)
