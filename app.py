import streamlit as st
import requests
import json
import time
import logging

# Set page config
st.set_page_config(
    page_title="👗 Fashion Event Tracker",
    page_icon="👠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Glamorous CSS with fashion theme
st.markdown("""
<style>
    /* Pink action buttons */
    .stButton>button {
        background-color: #E91E63 !important;
        color: white !important;
        border: 1px solid #C2185B !important;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #C2185B !important;
        border-color: #AD1457 !important;
        transform: scale(1.02);
    }

    /* Feature card buttons */
    .fashion-card h4 {
        color: white !important;
        padding: 8px;
        background: #9C27B0 !important;
        border-radius: 8px;
        display: inline-block;
    }

    /* Quick action buttons in sidebar */
    .st-emotion-cache-6qob1r .stButton>button {
        background-color: #AB47BC !important;
        color: white !important;
        border: 1px solid #8E24AA !important;
    }

    /* Error/warning buttons */
    .stAlert {
        background-color: #FCE4EC !important;
        color: #000000 !important;
    }
    
    /* Runway-inspired divider */
    .stDivider {
        border-top: 3px dashed #E91E63 !important;
    }
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Bonjour! I'm your Fashion Event Tracker 👗 Ask me about runway shows, designer events, or industry trends!"
    }]

# Configure sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    with st.container():
        api_key = st.text_input("OpenRouter API Key", type="password", help="Required for AI functionality")
        st.markdown("[Get API Key](https://openrouter.ai/keys)")
        
        with st.expander("📘 Quick Start"):
            st.markdown("""
            1. Obtain API key from OpenRouter
            2. Enter key above
            3. Select AI model
            4. Track fashion events!
            """)
        
        model_name = st.selectbox(
            "🤖 AI Model",
            ("deepseek/deepseek-r1-zero:free", "google/palm-2-chat-bison"),
            index=0
        )
        
        with st.expander("⚡ Advanced"):
            temperature = st.slider("🧠 Response Style", 0.0, 1.0, 0.4,
                                  help="Factual ↔ Creative")
            max_retries = st.number_input("🔄 Max Retries", 1, 5, 2)
        
        st.markdown("### 🚀 Quick Actions")
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Chat cleared! Ask me about fashion week events or designer collections!"
            }]
            
        # Fashion calendar filter
        st.markdown("### 📅 Event Filters")
        season = st.selectbox("Season", ["All", "Spring/Summer", "Fall/Winter", "Resort", "Pre-Fall"])
        city = st.multiselect("Fashion Capitals", ["New York", "Paris", "Milan", "London", "Tokyo"])

# Main interface
st.title("👠 Fashion Event Tracker")
st.caption("Your front-row seat to global fashion events, runway shows, and industry happenings")

# Feature cards
with st.container():
    cols = st.columns(4)
    features = [
        ("📅 Calendar", "Upcoming shows & events"),
        ("🌟 Trends", "Emerging styles & colors"),
        ("👗 Designers", "New collections & debuts"),
        ("📸 Street Style", "Top looks from events")
    ]
    for col, (emoji, text) in zip(cols, features):
        col.markdown(
            f"""<div class='fashion-card'>
                <h4>{emoji} {text}</h4>
            </div>""", 
            unsafe_allow_html=True
        )

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about fashion events..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("🔑 API key required in sidebar settings")
            st.markdown("""
            <div style='background: #FCE4EC; padding: 15px; border-radius: 10px; color: #000000 !important;'>
                <h4 style='color: #000000 !important;'>Get Started:</h4>
                <ol style='color: #000000 !important;'>
                    <li>Visit <a href="https://openrouter.ai/keys" style='color: #E91E63 !important;'>OpenRouter</a></li>
                    <li>Create account & get key</li>
                    <li>Enter key in sidebar</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        attempts = 0
        
        with st.spinner("Checking the front row for updates..."):
            time.sleep(0.3)
        
        while attempts < max_retries:
            try:
                # Build filters based on sidebar selections
                filters = []
                if season != "All":
                    filters.append(f"Season: {season}")
                if city:
                    filters.append(f"Cities: {', '.join(city)}")
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://fashion-tracker.streamlit.app",
                        "X-Title": "Fashion Event Tracker"
                    },
                    json={
                        "model": model_name,
                        "messages": [{
                            "role": "system",
                            "content": f"""You are a fashion industry expert. STRICT RULES:
1. Format responses clearly:
   - Event Name (Designer)
   - Date & Location (MM/DD/YYYY, City)
   - Collection Theme/Inspiration
   - Key Trends/Highlights
   - Notable Attendees (if relevant)
2. Use fashion emojis: 👗👠👜👒
3. Current season: {season}
4. Highlight new designers in purple
5. Current date: {time.strftime("%m/%d/%Y")}
6. Never use markdown
{f'- Filtering by: {", ".join(filters)}' if filters else ''}"""
                        }] + st.session_state.messages[-4:],
                        "temperature": temperature,
                        "response_format": {"type": "text"}
                    },
                    timeout=15
                )

                response.raise_for_status()
                data = response.json()
                raw_response = data['choices'][0]['message']['content']
                
                # Format response with fashion-specific styling
                processed_response = raw_response
                formatting_cleaners = [
                    ("**", ""), ("```", ""), ("\\n", "\n"),
                    ("Date:", "<strong>Date:</strong>"),
                    ("Location:", "<strong>Location:</strong>"),
                    ("Trends:", "<strong>Trends:</strong>")
                ]
                
                for pattern, replacement in formatting_cleaners:
                    processed_response = processed_response.replace(pattern, replacement)
                
                # Stream response like a fashion show reveal
                lines = processed_response.split('\n')
                for line in lines:
                    words = line.split()
                    for word in words:
                        full_response += word + " "
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.03)
                    full_response += "\n"
                    response_placeholder.markdown(full_response + "▌")
                
                # Final fashion-forward formatting
                full_response = full_response.replace("NEW COLLECTION", "<span style='color: #9C27B0'>NEW COLLECTION</span>") \
                                           .replace("TRENDING NOW", "<span style='color: #E91E63'>TRENDING NOW</span>")
                
                response_placeholder.markdown(full_response, unsafe_allow_html=True)
                break
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON Error: {str(e)}")
                attempts += 1
                if attempts == max_retries:
                    response_placeholder.error("⚠️ Processing error. Try:")
                    response_placeholder.markdown("""
                    <div style='background: #FCE4EC; padding: 15px; border-radius: 10px; color: #000000 !important;'>
                        <h4 style='color: #000000 !important;'>💡 Fashion Help:</h4>
                        <ul style='color: #000000 !important;'>
                            <li>Specify designer or city</li>
                            <li>Ask about specific seasons</li>
                            <li>Check your internet connection</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                response_placeholder.error(f"🌐 Network Error: {str(e)}")
                full_response = "Connection issue - please refresh and try again"
                break
                
            except Exception as e:
                logging.error(f"Error: {str(e)}")
                response_placeholder.error(f"❌ Unexpected error: {str(e)}")
                full_response = "Please try your request again"
                break

    st.session_state.messages.append({"role": "assistant", "content": full_response})