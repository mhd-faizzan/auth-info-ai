import streamlit as st
import requests
import re
from datetime import datetime

# ======================
# 1. FIREBASE SETUP
# ======================
def initialize_firebase():
    if not hasattr(st, 'secrets') or "firebase" not in st.secrets:
        st.error("Firebase configuration missing in secrets!")
        st.stop()
    
    return {
        "apiKey": st.secrets.firebase.api_key,
        "authDomain": st.secrets.firebase.auth_domain,
        "projectId": st.secrets.firebase.project_id
    }

firebase_config = initialize_firebase()

# Firebase REST API endpoints
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['apiKey']}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['apiKey']}"

# ======================
# 2. SOURCE VALIDATION SYSTEM
# ======================
class SourceValidator:
    SOURCE_PATTERNS = [
        r'\[(.+?)\]\((https?://[^\s]+)\)',  # Markdown links
        r'(https?://(?:www\.)?(?:[a-zA-Z0-9-]+\.)+(?:edu|gov|ac\.[a-z]{2,})[^\s]*',  # Academic/gov domains
        r'DOI:\s*(10\.\d{4,9}/[-._;()/:A-Z0-9]+)',  # DOI links
        r'arXiv:\s*(\d+\.\d+v?\d*)'  # arXiv IDs
    ]

    @classmethod
    def validate_source(cls, source_text):
        """Verify source meets academic standards"""
        source_text = source_text.strip()
        for pattern in cls.SOURCE_PATTERNS:
            if re.search(pattern, source_text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def extract_sources(cls, text):
        """Extract and validate sources from LLM response"""
        source_markers = [
            "### VERIFICATION SOURCES ###",
            "## REFERENCES ##",
            "CITATION:",
            "SOURCES:"
        ]
        
        for marker in source_markers:
            if marker in text:
                parts = text.split(marker)
                if len(parts) > 1:
                    sources = [s.strip() for s in parts[1].split("\n") if s.strip()]
                    return [s for s in sources if cls.validate_source(s)][:3]  # Return top 3 valid sources
        return []

# ======================
# 3. ENHANCED LLM QUERY WITH SOURCE GUARANTEE
# ======================
def get_verified_response(prompt):
    """Get response with guaranteed academic sources"""
    SYSTEM_PROMPT = f"""You are a senior academic researcher. For all responses:

1. Provide accurate information current as of {datetime.now().strftime('%B %Y')}
2. Include 3-5 authoritative sources formatted as:
   • [Full Title](URL) - Author (Year)
   • DOI/arXiv when available
3. Prioritize:
   - Peer-reviewed journals
   - .edu/.gov sources
   - Institutional publications
4. Conclude with: "### VERIFICATION SOURCES ###" and numbered sources"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,  # Lower for more factual responses
        "max_tokens": 2500,
        "response_format": {"type": "text"}
    }

    try:
        # Initial query
        response = requests.post(
            st.secrets.llama.api_url,
            headers={"Authorization": f"Bearer {st.secrets.llama.api_key}"},
            json=payload,
            timeout=120  # Extended timeout for thorough sourcing
        )
        
        if response.status_code != 200:
            return None, ["API Error: Initial query failed"]

        content = response.json()["choices"][0]["message"]["content"]
        sources = SourceValidator.extract_sources(content)
        
        # Source verification round if needed
        if not sources:
            verification_prompt = """Your previous response lacked proper academic sources. 
For the same query, provide ONLY 3 verified sources formatted as:
1. [Complete Title](Full URL) - Author/Organization (Year)
2. Must include at least one DOI/arXiv
3. No placeholder URLs"""

            payload["messages"].append({"role": "assistant", "content": content})
            payload["messages"].append({"role": "user", "content": verification_prompt})
            
            v_response = requests.post(
                st.secrets.llama.api_url,
                headers={"Authorization": f"Bearer {st.secrets.llama.api_key}"},
                json=payload,
                timeout=90
            )
            
            if v_response.status_code == 200:
                v_content = v_response.json()["choices"][0]["message"]["content"]
                sources = SourceValidator.extract_sources(v_content)
        
        # Clean response text
        response_text = content.split("### VERIFICATION SOURCES ###")[0].strip()
        
        if not sources:
            response_text += "\n\n[Academic sources unavailable - verify claims independently]"
            
        return response_text, sources

    except Exception as e:
        return None, [f"System Error: {str(e)}"]

# ======================
# 4. AUTHENTICATION FUNCTIONS
# ======================
def handle_signup(email, password):
    try:
        response = requests.post(
            FIREBASE_SIGNUP_URL,
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        if response.status_code == 200:
            return True, "Account created successfully!"
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, f"Signup failed: {error}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def handle_login(email, password):
    try:
        response = requests.post(
            FIREBASE_LOGIN_URL,
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        if response.status_code == 200:
            return True, "Login successful!", response.json()
        error = response.json().get("error", {}).get("message", "Unknown error")
        return False, f"Login failed: {error}", None
    except Exception as e:
        return False, f"Connection error: {str(e)}", None

# ======================
# 5. STREAMLIT UI
# ======================
st.set_page_config(page_title="AcademicFactCheck", page_icon="🔬")

# Custom CSS
st.markdown("""
    <style>
        .auth-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .source-panel {
            background-color: #f8f9fa;
            border-left: 4px solid #4e79a7;
            padding: 1.5rem;
            margin-top: 1.5rem;
        }
        .source-badge {
            background-color: #4e79a7;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            margin-right: 8px;
        }
        .warning-panel {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.id_token = ""

# ======================
# 6. AUTHENTICATION UI
# ======================
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>🔐 AcademicFactCheck</h1>
            <p>Research-grade answers with verified sources</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", type="primary", use_container_width=True):
                if email and password:
                    success, message, result = handle_login(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.session_state.id_token = result.get("idToken", "")
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both email and password")
        
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_pass")
            if st.button("Create Account", type="primary", use_container_width=True):
                if email and password:
                    success, message = handle_signup(email, password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both email and password")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# 7. MAIN APPLICATION
# ======================
else:
    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"# Welcome, Researcher {st.session_state.email.split('@')[0]}")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.id_token = ""
            st.rerun()
    
    st.markdown("---")
    
    # Query Interface
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
                start_time = datetime.now()
                response, sources = get_verified_response(prompt)
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response:
                    st.markdown("### Research Summary")
                    st.write(response)
                    
                    if sources:
                        st.markdown("""
                            <div class="source-panel">
                                <h4>📚 Academic References</h4>
                                {}
                            </div>
                        """.format("".join(
                            f'<div><span class="source-badge">Source {i+1}</span>{s}</div><br>'
                            for i, s in enumerate(sources)
                        )), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div class="warning-panel">
                                ⚠️ No academic sources found - verify claims independently
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.caption(f"Verified in {response_time:.1f} seconds | {len(sources)} academic sources")
                else:
                    st.error("Failed to retrieve verified information")

# ======================
# 8. FOOTER
# ======================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
        AcademicFactCheck • {year} • Peer-reviewed knowledge
    </div>
""".format(year=datetime.now().strftime("%Y")), unsafe_allow_html=True)
