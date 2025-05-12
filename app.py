import streamlit as st
import requests
import re
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Pro",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
# 2. FIREBASE CONFIGURATION
# ======================
if not hasattr(st, 'secrets') or "firebase" not in st.secrets:
    st.error("Firebase configuration missing in secrets!")
    st.stop()

firebase_config = {
    "apiKey": st.secrets.firebase.api_key,
    "authDomain": st.secrets.firebase.auth_domain,
    "projectId": st.secrets.firebase.project_id
}

FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"

# ======================
# 3. AUTHENTICATION FUNCTIONS
# ======================
def handle_signup(first_name, last_name, email, password):
    try:
        response = requests.post(
            FIREBASE_SIGNUP_URL,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            },
            timeout=10
        )
        if response.status_code == 200:
            st.session_state.update({
                'first_name': first_name.strip(),
                'last_name': last_name.strip()
            })
            return True, "Account created successfully!"
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, f"Signup failed: {error}"
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
        return False, f"Login failed: {error}", None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

# ======================
# 4. STREAMLIT UI COMPONENTS
# ======================
def show_auth_ui():
    """Authentication UI with modern styling"""
    with st.container():
        # Header with animation
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="font-size: 2.5rem; background: linear-gradient(90deg, #2563EB, #7C3AED);
                          -webkit-background-clip: text; color: transparent; margin-bottom: 0.5rem;">
                    🔍 FactVerify Pro
                </h1>
                <p style="color: #6B7280; font-size: 1.1rem;">
                    Research-grade answers with verified sources
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Auth container with glass morphism effect
        with stylable_container(
            key="auth_container",
            css_styles="""
                {
                    background: rgba(255, 255, 255, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    max-width: 500px;
                    margin: 0 auto;
                }
            """
        ):
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                with st.form("login_form"):
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
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Please enter both email and password")
            
            with tab2:
                with st.form("signup_form"):
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
                        elif len(password) < 6:
                            st.error("Password must be at least 6 characters")
                        else:
                            success, message = handle_signup(first_name, last_name, email, password)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

def show_main_app():
    """Main application interface with professional UI"""
    # Personalized greeting
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]
    
    # Header with user avatar
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 50px; height: 50px; border-radius: 50%; 
                          background: linear-gradient(135deg, #3B82F6, #8B5CF6);
                          display: flex; align-items: center; justify-content: center;
                          color: white; font-weight: bold; font-size: 1.2rem;">
                    {display_name[0].upper()}
                </div>
                <h1 style="margin: 0;">Welcome back, {display_name}!</h1>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Divider with animation
    st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
                  margin: 1.5rem 0;"></div>
    """, unsafe_allow_html=True)
    
    # Query Interface with modern card
    with stylable_container(
        key="query_card",
        css_styles="""
            {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                border: 1px solid #E5E7EB;
                margin-bottom: 1.5rem;
            }
        """
    ):
        prompt = st.text_area(
            "Enter your research query:",
            placeholder="e.g. 'What are the latest advancements in CRISPR technology with academic sources?'",
            height=150,
            label_visibility="collapsed"
        )
        
        if st.button("Get Verified Answer", type="primary", use_container_width=True):
            if not prompt:
                st.warning("Please enter a research question")
            else:
                with st.spinner("🔍 Verifying with academic databases..."):
                    # Simulate API call
                    st.success("This would show the verified response with sources in production")
                    st.markdown("""
                        <div style="margin-top: 1.5rem; padding: 1.5rem; 
                                  background: #F9FAFB; border-radius: 8px;
                                  border-left: 4px solid #3B82F6;">
                            <h4 style="margin-top: 0; color: #3B82F6;">📚 Sample Verified Response</h4>
                            <p>This is where your verified response with academic sources would appear.</p>
                            <div style="margin-top: 1rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 0.8rem; background: #EFF6FF; 
                                               color: #3B82F6; padding: 0.25rem 0.5rem;
                                               border-radius: 4px;">Source 1</span>
                                    <span>[CRISPR Technology Review](https://example.com) - Nature Journal (2023)</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# ======================
# 5. MAIN APP FLOW
# ======================
# Custom CSS for entire app
st.markdown("""
    <style>
        /* Better default spacing */
        .stApp > div {
            padding-top: 2rem;
        }
        
        /* Improved input fields */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
        }
        
        /* Better buttons */
        .stButton button {
            border-radius: 8px !important;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background: #EFF6FF;
            color: #3B82F6;
        }
    </style>
""", unsafe_allow_html=True)

# Application flow control
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()

# Footer with gradient
st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem; 
              margin-top: 3rem; padding: 1rem;
              background: linear-gradient(90deg, #F9FAFB, #EFF6FF, #F9FAFB);
              border-radius: 12px;">
        FactVerify Pro • {year} • Peer-reviewed knowledge
    </div>
""".format(year=datetime.now().strftime("%Y")), unsafe_allow_html=True)
