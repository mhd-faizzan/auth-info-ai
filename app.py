import streamlit as st
import requests
from datetime import datetime
import random

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Ai",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Single-page app CSS
st.markdown("""
    <style>
        :root {
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --text: #111827;
            --text-secondary: #6B7280;
            --border: #E5E7EB;
        }
        
        .stApp {
            max-width: 800px !important;
            padding: 1rem !important;
        }
        
        .auth-section {
            background: #F9FAFB;
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        
        .app-section {
            display: none; /* Hidden by default */
        }
        
        .visible {
            display: block;
        }
        
        .form-switch {
            text-align: center;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        
        .switch-btn {
            color: var(--primary);
            cursor: pointer;
            font-weight: 500;
        }
        
        /* Hide scrollbars */
        ::-webkit-scrollbar {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'email': "",
        'show_login': True,
        'form_key': 0  # Used to force form reset
    })

# ======================
# 2. AUTHENTICATION UI (Always Visible)
# ======================
def show_auth_section():
    st.markdown(f"""
        <div class="auth-section" {'style="display: none;"' if st.session_state.logged_in else ''}>
            <h3 style="color: var(--text); margin-bottom: 1.5rem;">
                { 'Sign in to FactVerify' if st.session_state.show_login else 'Create Account' }
            </h3>
    """, unsafe_allow_html=True)
    
    if st.session_state.show_login:
        with st.form(key=f"login_form_{st.session_state.form_key}"):
            email = st.text_input("Email", placeholder="your@email.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            
            if st.form_submit_button("Login", use_container_width=True):
                if email and password:
                    # Simulate login for demo (replace with your actual auth)
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
            
            st.markdown("""
                <div class="form-switch">
                    Don't have an account? 
                    <span class="switch-btn" onclick="switchToSignup()">Create one</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        with st.form(key=f"signup_form_{st.session_state.form_key}"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", placeholder="Given Name")
            with col2:
                last_name = st.text_input("Last Name", placeholder="Family Name")
            
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Register", use_container_width=True):
                if email and password:
                    # Simulate signup for demo (replace with your actual auth)
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.rerun()
            
            st.markdown("""
                <div class="form-switch">
                    Already have an account? 
                    <span class="switch-btn" onclick="switchToLogin()">Sign in</span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 3. MAIN APP UI (Always in DOM)
# ======================
def show_app_section():
    st.markdown(f"""
        <div class="app-section" {'style="display: block;"' if st.session_state.logged_in else ''}>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <h2 style="color: var(--text); margin: 0;">FactVerify Dashboard</h2>
                <button onclick="handleLogout()" style="
                    background: var(--primary); 
                    color: white; 
                    border: none; 
                    padding: 0.5rem 1rem; 
                    border-radius: 8px; 
                    cursor: pointer;
                ">Logout</button>
            </div>
    """, unsafe_allow_html=True)
    
    # Your main app content here
    with st.form(key="query_form"):
        prompt = st.text_area(
            "Enter your research query:",
            placeholder="Example: 'What is the current scientific consensus on climate change?'",
            height=150
        )
        
        if st.form_submit_button("Verify Information", use_container_width=True):
            if prompt:
                st.success("This would show verification results in a real app")
            else:
                st.warning("Please enter a query")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 4. JAVASCRIPT HANDLERS
# ======================
st.markdown("""
    <script>
        function switchToSignup() {
            Streamlit.setComponentValue({"show_login": false, "form_key": Date.now()});
        }
        function switchToLogin() {
            Streamlit.setComponentValue({"show_login": true, "form_key": Date.now()});
        }
        function handleLogout() {
            Streamlit.setComponentValue({"logout": true});
        }
    </script>
""", unsafe_allow_html=True)

# ======================
# 5. RENDER THE SINGLE PAGE APP
# ======================
show_auth_section()
show_app_section()

# Handle JavaScript events
if 'show_login' in st.session_state:
    st.session_state.show_login = st.session_state.get('show_login', True)
    st.session_state.form_key = st.session_state.get('form_key', 0)
    st.rerun()

if st.session_state.get('logout'):
    st.session_state.logged_in = False
    st.session_state.form_key = Date.now()
    st.rerun()
