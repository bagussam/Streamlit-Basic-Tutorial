# Import the necessary libraries
import streamlit as st
import google.generativeai as genai  # --- PERBAIKAN 1: Cara import yang benar ---

# --- 1. Page Configuration and Title ---
st.title("💬 Gemini Chatbot")
st.caption("A simple and friendly chat using Google's Gemini Flash model")

# --- 2. Sidebar for Settings ---
with st.sidebar:
    st.subheader("Settings")
    google_api_key = st.text_input("Google AI API Key", type="password")
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

# --- 3. API Key and Model Initialization ---
if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()

# --- PERBAIKAN 2: Konfigurasi API key dengan cara yang benar ---
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Invalid API Key or configuration error: {e}")
    st.stop()

# --- PERBAIKAN 3: Buat model dan chat session dengan cara yang benar ---
# Initialize the generative model
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the chat session
if "chat" not in st.session_state:
    # Start a new chat with an empty history
    st.session_state.chat = st.session_state.model.start_chat(history=[])

# Initialize the message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Chat History Management ---
if reset_button:
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    st.rerun()

# --- 5. Display Past Messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. Handle User Input and API Communication ---
prompt = st.chat_input("Type your message here...")

if prompt:
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display assistant's response
    try:
        # Send the prompt to the ongoing chat session
        response = st.session_state.chat.send_message(prompt)
        answer = response.text

        with st.chat_message("assistant"):
            st.markdown(answer)
        
        # Add assistant's response to history
        st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"An error occurred: {e}")