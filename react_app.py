# Import the necessary libraries
import streamlit as st  # For creating the web app interface
from langchain_google_genai import ChatGoogleGenerativeAI  # For interacting with Google Gemini via LangChain
from langgraph.prebuilt import create_react_agent  # For creating a ReAct agent
from langchain_core.messages import HumanMessage, AIMessage  # For message formatting

# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("💬 LangGraph ReAct Chatbot")
st.caption("A simple and friendly chat using LangGraph with Google's Gemini model")

# --- 2. Sidebar for Settings ---

# Create a sidebar section for app settings using 'with st.sidebar:'
with st.sidebar:
    # Add a subheader to organize the settings
    st.subheader("Settings")
        
    # Create a button to reset the conversation.
    # 'help' provides a tooltip that appears when hovering over the button.
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

# --- 3. API Key and Agent Initialization ---

# Hanya buat agen baru jika belum ada di session state
if "agent" not in st.session_state:
    try:
        # Ambil API key langsung dari Streamlit Secrets
        # Pastikan nama "GOOGLE_API_KEY" sama dengan yang ada di Secrets Anda
        api_key_from_secrets = st.secrets["GOOGLE_API_KEY"]
        
        # Inisialisasi LLM dengan API key dari secrets
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key_from_secrets,
            temperature=0.7
        )
        
        # Buat ReAct agent
        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[], 
            prompt="You are a helpful, friendly assistant. Respond concisely and clearly."
        )

    except KeyError:
        st.error("Kunci API Google tidak ditemukan di Secrets. Harap tambahkan terlebih dahulu.")
        st.stop()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengonfigurasi agen: {e}")
        st.stop()

# --- 4. Chat History Management ---

# Initialize the message history (as a list) if it doesn't exist.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Handle the reset button click.
if reset_button:
    # If the reset button is clicked, clear the agent and message history from memory.
    st.session_state.pop("agent", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and Agent Communication ---

# Create a chat input box at the bottom of the page.
# The user's typed message will be stored in the 'prompt' variable.
prompt = st.chat_input("Type your message here...")

# Check if the user has entered a message.
if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    # Use a 'try...except' block to gracefully handle potential errors (e.g., network issues, API errors).
    try:
        # Convert the message history to the format expected by the agent
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Send the user's prompt to the agent
        response = st.session_state.agent.invoke({"messages": messages})
        
        # Extract the answer from the response
        if "messages" in response and len(response["messages"]) > 0:
            answer = response["messages"][-1].content
        else:
            answer = "I'm sorry, I couldn't generate a response."

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        answer = f"An error occurred: {e}"

    # 4. Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": answer})