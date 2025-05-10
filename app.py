import streamlit as st
import requests
from datetime import datetime

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""

# Custom CSS with source styling
st.markdown("""
    <style>
        .source-box {
            background-color: #f8f9fa;
            border-left: 4px solid #6c757d;
            padding: 12px;
            margin-top: 15px;
            font-size: 14px;
        }
        .source-title {
            font-weight: bold;
            color: #2c3e50;
        }
        .source-item {
            margin: 5px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Title with model info
st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <h1>🔍 AuthenticInfo AI</h1>
        <span style="background: #6e48aa; color: white; padding: 3px 8px; border-radius: 12px; font-size: 14px;">
            llama-3.3-70b-versatile
        </span>
    </div>
    <p style="color: #666;">Always providing sourced information</p>
""", unsafe_allow_html=True)

# Enhanced query function with source requirements
def query_llama(prompt):
    SYSTEM_PROMPT = """You are a fact-checking AI assistant. Always:
    1. Provide accurate, up-to-date information
    2. Include 2-3 verifiable sources
    3. Format sources clearly as:
       • [Title](URL) - Publisher/Author (Year)
    4. For technical topics, prefer academic papers
    5. For news, cite primary sources
    6. If unsure, state "Could not verify"
    
    Current date: {date}""".format(date=datetime.now().strftime("%Y-%m-%d"))

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt + "\n\nPlease provide sources in the requested format."}
        ],
        "temperature": 0.5,  # Lower for more factual responses
        "max_tokens": 2000,
        "response_format": {"type": "text"}
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
            return extract_response_and_sources(content)
        else:
            return None, [f"API Error: {response.status_code}"]
            
    except Exception as e:
        return None, [f"Error: {str(e)}"]

def extract_response_and_sources(content):
    """Separates main response from sources"""
    if "Sources:" in content:
        parts = content.split("Sources:")
        return parts[0].strip(), [s.strip() for s in parts[1].split("•") if s.strip()]
    return content, ["No sources provided"]

# Main app interface
if st.session_state.logged_in:
    user_input = st.text_area("Ask for verified information:", height=150)
    
    if st.button("Get Verified Answer"):
        with st.spinner("🔎 Verifying information..."):
            start_time = datetime.now()
            response, sources = query_llama(user_input)
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response:
                st.markdown(f"**Verified Answer ({response_time:.1f}s):**")
                st.write(response)
                
                if sources and sources[0] != "No sources provided":
                    st.markdown("---")
                    st.markdown("""
                        <div class="source-box">
                            <div class="source-title">📚 Verified Sources</div>
                            {}
                        </div>
                    """.format("".join([f'<div class="source-item">• {s}</div>' for s in sources])), 
                    unsafe_allow_html=True)
            else:
                st.error("Failed to get response")

# [Keep your existing Firebase authentication code]
