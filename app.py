import streamlit as st
import pyrebase
import requests
import json

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

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
    </style>
""", unsafe_allow_html=True)

# Title of the app
st.markdown("<div class='heading'>🔐 Welcome to InfoAI App!</div>", unsafe_allow_html=True)

# Firebase Authentication - Login or Signup
option = st.selectbox("Choose an option", ["Login", "Signup"])

# Input fields for email and password inside a styled container
with st.container():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Function to initialize Firebase with credentials from Streamlit secrets
    def initialize_firebase():
        try:
            firebase_config = {
                "apiKey": st.secrets["firebase"]["api_key"],
                "authDomain": st.secrets["firebase"]["auth_domain"],
                "projectId": st.secrets["firebase"]["project_id"],
                "storageBucket": st.secrets["firebase"]["storage_bucket"],
                "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
                "appId": st.secrets["firebase"]["app_id"],
                "measurementId": st.secrets["firebase"]["measurement_id"]
            }
            firebase = pyrebase.initialize_app(firebase_config)
            return firebase.auth()
        except Exception as e:
            st.error("Error initializing Firebase.")
            st.exception(e)

    # Signup functionality
    if option == "Signup":
        if st.button("Create Account", key="signup", help="Create a new account"):
            try:
                auth = initialize_firebase()
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created! Please log in.")
            except Exception as e:
                st.error("Failed to create account.")
                st.exception(e)

    # Login functionality
    if option == "Login":
        if st.button("Login", key="login", help="Login to your account"):
            try:
                auth = initialize_firebase()
                user = auth.sign_in_with_email_and_password(email, password)
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.email = email
            except Exception as e:
                st.error("Invalid credentials or network issue.")
                st.exception(e)

    st.markdown("</div>", unsafe_allow_html=True)

# Function to query the Llama3-70b-8192 model API using Streamlit secrets
def query_llama_model(query, api_key, model):
    try:
        url = "https://api.llama.com/v1/query"  # Replace with the actual Llama API endpoint for llama3-70b-8192

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": query + " Please provide a reference with your answer.",
            "max_tokens": 150
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "No response from the model.")
            reference = data.get("reference", "No reference provided.")
            return answer, reference
        else:
            st.error(f"Llama API Error: {response.status_code}")
            st.text(response.text)
            return "API returned an error.", "No reference"
    
    except requests.exceptions.Timeout:
        st.error("The request to the Llama API timed out.")
        return "Timeout error", "No reference"

    except requests.exceptions.RequestException as e:
        st.error("Failed to reach the Llama API.")
        st.exception(e)
        return "Network error", "No reference"

    except Exception as e:
        st.error("Unexpected error occurred.")
        st.exception(e)
        return "Unexpected error", "No reference"

# Protect access to the Llama model AI interface
if st.session_state.logged_in:
    st.subheader(f"Welcome, {st.session_state.email}")
    
    user_input = st.text_input("Ask the AI model anything")

    if user_input:
        llama_api_key = st.secrets["llama"]["api_key"]  # Fetch the llama3-70b-8192 API key from Streamlit secrets
        llama_model = "llama3-70b-8192"  # Use the new model name here
        
        model_response, reference = query_llama_model(user_input, llama_api_key, llama_model)
        
        st.markdown("<div class='response-box'>", unsafe_allow_html=True)
        st.write(f"**AI Response**: {model_response}")
        st.write(f"**Reference**: {reference}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Logout", key="logout", help="Logout from your account", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.write("You have been logged out.")

else:
    st.info("Please login to access the AI model.")
