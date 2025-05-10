import streamlit as st
import requests
import json
from datetime import datetime

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.id_token = ""

# Custom CSS for styling
st.markdown("""
    <style>
        /* [Keep all your existing CSS styles] */
    </style>
""", unsafe_allow_html=True)

# Title of the app
st.markdown("<div class='heading'>🔐 Welcome to InfoAI App!</div>", unsafe_allow_html=True)

# Check if secrets are configured
def check_secrets():
    required_config = {
        "firebase": ["api_key", "auth_domain", "project_id"],
        "llama": ["api_key", "api_url"]
    }
    
    for service, keys in required_config.items():
        if service not in st.secrets:
            st.error(f"Missing {service} configuration in secrets!")
            return False
        for key in keys:
            if key not in st.secrets[service]:
                st.error(f"Missing {key} in {service} secrets!")
                return False
    return True

if not check_secrets():
    st.stop()

# Firebase Authentication REST API endpoints
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={st.secrets.firebase.api_key}"
FIREBASE_LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={st.secrets.firebase.api_key}"

# Authentication functions
def firebase_signup(email, password):
    try:
        response = requests.post(
            FIREBASE_SIGNUP_URL,
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Signup error: {str(e)}")
        return None

def firebase_login(email, password):
    try:
        response = requests.post(
            FIREBASE_LOGIN_URL,
            json={"email": email, "password": password, "returnSecureToken": True}
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None

# LLM Query Function (Llama3-70b-8192)
def query_llama(prompt):
    headers = {
        "Authorization": f"Bearer {st.secrets.llama.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(
            st.secrets.llama.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            return f"Error: API returned status code {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

# Authentication UI
if not st.session_state.logged_in:
    option = st.selectbox("Choose an option", ["Login", "Signup"])
    
    with st.container():
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if option == "Signup":
            if st.button("Create Account"):
                if email and password:
                    result = firebase_signup(email, password)
                    if result:
                        st.success("Account created! Please log in.")
                else:
                    st.error("Please enter both email and password")
        
        if option == "Login":
            if st.button("Login"):
                if email and password:
                    result = firebase_login(email, password)
                    if result:
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.session_state.id_token = result.get("idToken", "")
                        st.success("Login successful!")
                        st.rerun()
                else:
                    st.error("Please enter both email and password")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main App Interface
if st.session_state.logged_in:
    st.subheader(f"Welcome, {st.session_state.email}")
    
    # Display logout button at top right
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout", key="logout", help="Logout from your account"):
            st.session_state.logged_in = False
            st.session_state.email = ""
            st.session_state.id_token = ""
            st.rerun()
    
    # AI Query Interface
    user_input = st.text_area("Ask Llama3-70b anything", height=150,
                            placeholder="Type your question here...")
    
    if st.button("Get Answer", use_container_width=True) and user_input:
        with st.spinner("Llama3 is thinking..."):
            start_time = datetime.now()
            response = query_llama(user_input)
            response_time = (datetime.now() - start_time).total_seconds()
            
            st.markdown("<div class='response-box'>", unsafe_allow_html=True)
            st.write(f"**Llama3-70b Response ({response_time:.2f}s):**")
            st.write(response)
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Please login to access the AI model.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    Powered by Streamlit, Firebase, and Llama3-70b-8192
    </div>
""", unsafe_allow_html=True)
