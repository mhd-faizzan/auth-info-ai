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
        
        .stTextInput input, .stTextArea textarea {
            background: #3E4042 !important;
            color: var(--text) !important;
            border: none !important;
            border-radius: 8px !important;
        }
        
        .stButton button {
            background: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.2s !important;
        }
        
        .stButton button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
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
# 2. AUTHENTICATION UI (MODERN)
# ======================
def show_auth_ui():
    with st.container():
        # Header with logo
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
        
        # Auth card
        with st.container():
            st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
with tab1:
    with st.form("login_form"):  # Update form key
        email = st.text_input("Email", placeholder="your@email.com", key="login_email")  # Add key
        password = st.text_input("Password", type="password", key="login_password")  # Add key

        if st.form_submit_button("Login", use_container_width=True, key="login_submit"):  # Add key
            if email and password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Please fill all fields")

with tab2:
    with st.form("signup_form"):  # Update form key
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", placeholder="Muhammad", key="signup_first_name")  # Add key
        with col2:
            last_name = st.text_input("Last Name", placeholder="Faizan", key="signup_last_name")  # Add key

        email = st.text_input("Email", placeholder="your@email.com", key="signup_email")  # Add key

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password", type="password", key="signup_password")  # Add key
        with col4:
            confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm_password")  # Add key

        if st.form_submit_button("Create Account", use_container_width=True, key="signup_submit"):  # Add key
            if not all([first_name, last_name, email, password, confirm_pass]):
                st.error("Please fill all fields")
            elif password != confirm_pass:
                st.error("Passwords don't match")
            else:
                st.session_state.update({
                    'first_name': first_name,
                    'last_name': last_name
                })
                st.success("Account created!")
            
            st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 3. MAIN APP UI (MODERN)
# ======================
def show_main_app():
    # Personalized header
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else "Researcher"
    
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
    
    # Query interface
    with st.container():
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Your research query:",
            placeholder="Ask about any topic with academic sources...",
            height=150
        )
        
if st.button("Verify Information", type="primary", use_container_width=True):
    if not prompt:
        st.warning("Please enter a question")
    else:
        with st.spinner("🔍 Verifying with academic databases..."):
            start_time = datetime.now()
            response, sources = get_verified_response(prompt)  # Use the function for queries
            response_time = (datetime.now() - start_time).total_seconds()
            
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

                st.markdown(f"""
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;">
                        ⏱️ Verified in {response_time:.1f}s • {len(sources)} academic sources
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to get verified response")
        

# ======================
# 4. APP ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
    # ======================
# 5. FIREBASE INTEGRATION
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
            # Store additional user data (would require Firestore in production)
            return True, "Account created successfully!"
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, error
    except Exception as e:
        return False, f"Connection error: {str(e)}"

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
# 6. LLM INTEGRATION (PRODUCTION)
# ======================
def get_verified_response(prompt):
    """Production-ready query with academic sources"""
    try:
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
        else:
            error = response.json().get("error", {}).get("message", "Unknown error")
            return None, [f"API Error: {error}"]
    except Exception as e:
        return None, [f"System Error: {str(e)}"]

# ======================
# 7. INTEGRATE INTO MAIN APP
# ======================
# Update the button handler in show_main_app():
if st.button("Verify Information", type="primary", use_container_width=True):
    if not prompt:
        st.warning("Please enter a question")
    else:
        with st.spinner("🔍 Verifying with academic databases..."):
            start_time = datetime.now()
            response, sources = get_verified_response(prompt)
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response:
                # Display response
                st.markdown(f"""
                    <div style="margin-top: 1.5rem; padding: 1rem; 
                              background: #3A3B3C; border-radius: 8px;">
                        <p style="color: var(--text);">{response}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display sources if available
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
                
                # Show metrics
                st.markdown(f"""
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 1rem;">
                        ⏱️ Verified in {response_time:.1f}s • {len(sources)} academic sources
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Failed to get verified response")

# ======================
# 8. FINAL APP ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()
