import streamlit as st
import requests
import re
from datetime import datetime

# ======================
# 1. INITIALIZATION & CONFIG
# ======================
st.set_page_config(
    page_title="FactVerify Pro",
    page_icon="🔍",
    layout="centered"
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
    st.markdown("""
        <style>
            .auth-container {
                max-width: 500px;
                margin: 0 auto;
                padding: 2rem;
                border-radius: 12px;
                background: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .header-text {
                text-align: center;
                margin-bottom: 2rem;
            }
            .stTabs [role="tablist"] {
                gap: 0.5rem;
            }
            .stTabs [role="tab"] {
                padding: 0.5rem 1rem;
                border-radius: 8px;
                background: #f8f9fa;
            }
            .stTabs [aria-selected="true"] {
                background: #3b82f6;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="header-text">
            <h1 style="color: #2563EB; margin-bottom: 0.5rem;">🔍 FactVerify Pro</h1>
            <p style="color: #6B7280;">Research-grade answers with verified sources</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_main_app():
    """Main application interface with professional UI"""
    # Personalized greeting
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]
    
    # Header with user info
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 50px; height: 50px; border-radius: 50%; 
                          background: #3B82F6; display: flex; align-items: center; 
                          justify-content: center; color: white; font-weight: bold;">
                    {display_name[0].upper()}
                </div>
                <h1 style="margin: 0;">Welcome back, {display_name}!</h1>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Query Interface
    with st.container():
        prompt = st.text_area(
            "Enter your research query:",
            placeholder="e.g. 'What are the latest advancements in CRISPR technology with academic sources?'",
            height=150
        )
        
        if st.button("Get Verified Answer", type="primary", use_container_width=True):
            if not prompt:
                st.warning("Please enter a research question")
            else:
                with st.spinner("🔍 Verifying with academic databases..."):
                    # Simulate API call
                    st.success("This would show the verified response with sources in production")
                    with st.container():
                        st.markdown("""
                            <div style="padding: 1.5rem; background: #F8F9FA; 
                                      border-radius: 8px; border-left: 4px solid #3B82F6;
                                      margin-top: 1rem;">
                                <h4 style="color: #3B82F6; margin-top: 0;">📚 Sample Response</h4>
                                <p>This is where your verified response would appear.</p>
                                <div style="margin-top: 1rem;">
                                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                                        <span style="font-size: 0.8rem; background: #EFF6FF; 
                                                  color: #3B82F6; padding: 0.25rem 0.5rem;
                                                  border-radius: 4px;">Source 1</span>
                                        <span>[Sample Source Title](https://example.com) - Author (2023)</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

# ======================
# 5. MAIN APP FLOW (COMPLETE IMPLEMENTATION)
# ======================

# Custom CSS for entire app
st.markdown("""
    <style>
        /* Main app styling */
        .stApp {
            background-color: #f8fafc;
        }
        
        /* Improved containers */
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        /* Enhanced cards */
        .custom-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 1.5rem;
        }
        
        /* Better input fields */
        .stTextInput input, .stTextArea textarea {
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* Modern buttons */
        .stButton button {
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            font-weight: 500 !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Source items styling */
        .source-item {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #3b82f6;
        }
        
        /* Response metrics */
        .response-metrics {
            font-size: 0.85rem;
            color: #64748b;
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

def display_verified_response(response, sources, response_time):
    """Display formatted response with sources"""
    with st.container():
        st.markdown("""
            <div class="custom-card">
                <h3 style="margin-top: 0; color: #1e40af;">Verified Response</h3>
                <div style="line-height: 1.6;">
        """, unsafe_allow_html=True)
        
        st.write(response)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        if sources:
            with st.container():
                st.markdown("""
                    <div class="custom-card">
                        <h4 style="margin-top: 0; color: #1e40af;">
                            <span style="display: inline-flex; align-items: center; gap: 0.5rem;">
                                📚 Verification Sources
                            </span>
                        </h4>
                """, unsafe_allow_html=True)
                
                for i, source in enumerate(sources, 1):
                    st.markdown(f"""
                        <div class="source-item">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="background: #3b82f6; color: white; 
                                          width: 24px; height: 24px; border-radius: 50%;
                                          display: flex; align-items: center; 
                                          justify-content: center; font-size: 0.75rem;">
                                    {i}
                                </span>
                                {source}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No academic sources found - verify claims independently")
        
        # Response metrics
        st.markdown(f"""
            <div class="response-metrics">
                <span>⏱️ Generated in {response_time:.2f}s</span>
                <span>🔍 {len(sources)} verified sources</span>
            </div>
        """, unsafe_allow_html=True)

def show_main_app():
    """Enhanced main application interface"""
    # Personalized greeting
    first_name = st.session_state.get('first_name', '')
    last_name = st.session_state.get('last_name', '')
    display_name = f"{first_name[0].upper()}. {last_name}" if first_name else st.session_state.email.split('@')[0]
    
    # Header with user profile
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="width: 48px; height: 48px; border-radius: 50%; 
                          background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                          display: flex; align-items: center; justify-content: center;
                          color: white; font-weight: bold; font-size: 1.1rem;">
                    {display_name[0].upper()}
                </div>
                <div>
                    <h1 style="margin: 0; line-height: 1.2;">Welcome back, {display_name}</h1>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                        Ready to verify some information?
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Divider with subtle gradient
    st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
                  margin: 1rem 0 1.5rem;"></div>
    """, unsafe_allow_html=True)
    
    # Query interface in card
    with st.container():
        st.markdown("""
            <div class="custom-card">
                <h3 style="margin-top: 0; color: #1e40af;">New Research Query</h3>
        """, unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Enter your question:",
            placeholder="Example: 'What are the most recent breakthroughs in quantum computing according to peer-reviewed journals?'",
            height=150,
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Get Verified Answer", type="primary", use_container_width=True):
                if not prompt:
                    st.warning("Please enter a research question")
                else:
                    with st.spinner("🔍 Cross-referencing academic databases..."):
                        start_time = datetime.now()
                        # In production: response, sources = get_verified_response(prompt)
                        # For demo purposes:
                        response = """Quantum computing has seen significant advancements in 2023. Researchers at MIT demonstrated error-corrected qubits with 99.9% fidelity (Nature, March 2023), while Google Quantum AI achieved quantum supremacy on a 72-qubit processor (Science, June 2023)."""
                        
                        sources = [
                            "[Scalable Quantum Error Correction](https://www.nature.com/articles/s41586-023-05782-6) - Nature (2023)",
                            "[Quantum Supremacy at 72 Qubits](https://www.science.org/doi/10.1126/science.ade3800) - Science (2023)",
                            "DOI:10.1103/PhysRevX.13.021028 - Physical Review X (2023)"
                        ]
                        
                        response_time = (datetime.now() - start_time).total_seconds()
                        display_verified_response(response, sources, response_time)
        
        with col2:
            st.button("Clear", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Example recent queries (would be dynamic in production)
    with st.expander("📚 Recent Queries", expanded=False):
        st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;">
                <div class="custom-card">
                    <h4 style="margin-top: 0;">CRISPR advancements</h4>
                    <p style="color: #64748b; font-size: 0.9rem;">3 verified sources</p>
                </div>
                <div class="custom-card">
                    <h4 style="margin-top: 0;">mRNA vaccine stability</h4>
                    <p style="color: #64748b; font-size: 0.9rem;">2 verified sources</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ======================
# 6. APPLICATION ROUTING
# ======================
if not st.session_state.logged_in:
    show_auth_ui()
else:
    show_main_app()

# ======================
# 7. FOOTER
# ======================
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-top: 3rem;
              color: #64748b; font-size: 0.9rem; border-top: 1px solid #e2e8f0;">
        <div style="display: flex; justify-content: center; gap: 1.5rem; margin-bottom: 0.5rem;">
            <a href="#" style="color: #3b82f6; text-decoration: none;">Terms</a>
            <a href="#" style="color: #3b82f6; text-decoration: none;">Privacy</a>
            <a href="#" style="color: #3b82f6; text-decoration: none;">Contact</a>
        </div>
        <div>
            FactVerify Pro • {year} • Academic-Grade Verification
        </div>
    </div>
""".format(year=datetime.now().strftime("%Y")), unsafe_allow_html=True)
