import streamlit as st
import pyrebase
import requests
import json
from datetime import datetime

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.auth_token = None

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            text-align: center;
            padding: 30px;
        }
        .login-form {
            margin-top: 30px;
        }
        .login-container {
            background-color: #f1f1f1;
            padding: 20px;
            border-radius: 10px;
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
        }
        .button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            border: none;
        }
        .button:hover {
            background-color: #45a049;
        }
        .logout-btn {
            background-color: #ff4d4d;
        }
        .logout-btn:hover {
            background-color: #ff3333;
        }
        .heading {
            font-size: 30px;
            font-weight: bold;
            color: #2C3E50;
        }
        .response-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background-color: #ecf0f1;
            max-width: 800px;
            margin: auto;
            word-wrap: break-word;
        }
        .error {
            color: red;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Title of the app
st.markdown("<div class='heading'>🔐 Welcome to InfoAI App!</div>", unsafe_allow_html=True)

# Check if secrets are configured
def check_secrets():
    required_secrets = {
        'firebase': ['api_key', 'auth_domain', 'project_id', 'storage_bucket', 
                    'messaging_sender_id', 'app_id', 'measurement_id'],
        'llama': ['api_key', 'api_url']
    }
    
    for category, keys in required_secrets.items():
        if category not in st.secrets:
            st.error(f"Missing {category} configuration in secrets!")
            return False
        for key in keys:
            if key not in st.secrets[category]:
                st.error(f"Missing {key} in {category} secrets!")
                return False
    return True

if not check_secrets():
    st.stop()

# Initialize Firebase
def initialize_firebase():
    try:
        firebase_config = {
            "apiKey": st.secrets.firebase.api_key,
            "authDomain": st.secrets.firebase.auth_domain,
            "projectId": st.secrets.firebase.project_id,
            "storageBucket": st.secrets.firebase.storage_bucket,
            "messagingSenderId": st.secrets.firebase.messaging_sender_id,
            "appId": st.secrets.firebase.app_id,
            "measurementId": st.secrets.firebase.measurement_id
        }
        return pyrebase.initialize_app(firebase_config).auth()
    except Exception as e:
        st.error(f"Firebase initialization failed: {str(e)}")
        st.stop()

auth = initialize_firebase()

# Authentication functions
def handle_signup(email, password):
    try:
        auth.create_user_with_email_and_password(email, password)
        st.success("Account created successfully! Please log in.")
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        st.error(f"Signup failed: {error.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")

def handle_login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.logged_in = True
        st.session_state.email = email
        st.session_state.auth_token = user['idToken']
        st.success("Login successful!")
    except requests.exceptions.HTTPError as e:
        error_json = e.args[1]
        error = json.loads(error_json)['error']
        st.error(f"Login failed: {error.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Login failed: {str(e)}")

# Query Llama3 model (using example API structure)
def query_llama_model(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {st.secrets.llama.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            st.secrets.llama.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response"), ""
        else:
            return f"API Error: {response.status_code}", response.text
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again.", ""
    except Exception as e:
        return f"Error: {str(e)}", ""

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
                    handle_signup(email, password)
                else:
                    st.error("Please enter both email and password")
        
        if option == "Login":
            if st.button("Login"):
                if email and password:
                    handle_login(email, password)
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
            st.session_state.auth_token = None
            st.rerun()
    
    # AI Query Interface
    user_input = st.text_area("Ask the AI model anything", height=150)
    
    if st.button("Get Answer", use_container_width=True) and user_input:
        with st.spinner("Generating response..."):
            start_time = datetime.now()
            model_response, error_detail = query_llama_model(user_input)
            response_time = (datetime.now() - start_time).total_seconds()
            
            st.markdown("<div class='response-box'>", unsafe_allow_html=True)
            st.write(f"**AI Response (generated in {response_time:.2f}s):**")
            st.write(model_response)
            
            if error_detail:
                st.markdown("---")
                st.write("**Error Details:**")
                st.code(error_detail, language='json')
            
            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Please login to access the AI model.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
    InfoAI App | Powered by Streamlit, Firebase, and Llama3
    </div>
""", unsafe_allow_html=True)
