import streamlit as st
from handlers import ClaudeHandler, ChatGPTHandler
from dotenv import load_dotenv
import os
from pathlib import Path
from themes import THEMES
import toml

def save_theme(theme_config):
    config_path = Path('.streamlit/config.toml')
    config_path.parent.mkdir(exist_ok=True)
    config = {'theme': theme_config}
    with open(config_path, 'w') as f:
        toml.dump(config, f)

load_dotenv()

# Constants
MAX_TOKENS = 4096
MAX_MESSAGES = 100

# Page config
st.set_page_config(page_title="Interfazada", page_icon="🤖", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token_count" not in st.session_state:
    st.session_state.token_count = 0
if "current_model" not in st.session_state:
    st.session_state.current_model = "Claude"
if "editing_message_index" not in st.session_state:
    st.session_state.editing_message_index = None

# Initialize handlers
claude_handler = ClaudeHandler(os.getenv('ANTHROPIC_API_KEY'))
chatgpt_handler = ChatGPTHandler(os.getenv('OPENAI_API_KEY'))

# App title
st.title("Interfazada 💃")

# Display chat messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            if st.session_state.editing_message_index == idx:
                # Show edit interface
                edited_text = st.text_area("Edit message",
                                         value=message["content"],
                                         key=f"edit_{idx}")
                if st.button("Save", key=f"save_{idx}"):
                    st.session_state.messages[idx]["content"] = edited_text
                    st.session_state.editing_message_index = None
                    st.rerun()
                if st.button("Cancel", key=f"cancel_{idx}"):
                    st.session_state.editing_message_index = None
                    st.rerun()
            else:
                st.markdown(f'<div class="{message["role"]}-message">{message["content"]}</div>',
                          unsafe_allow_html=True)

        with col2:
            if message["role"] == "user" and st.session_state.editing_message_index != idx:
                if st.button("✏️", key=f"edit_button_{idx}"):
                    st.session_state.editing_message_index = idx
                    st.rerun()

# Chat input
if prompt := st.chat_input("What would you like to ask?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.token_count += len(prompt.split()) * 1.3

    # Display user message
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    # Get response based on selected model
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        handler = claude_handler if st.session_state.current_model == "Claude" else chatgpt_handler
        full_response = handler.get_response(st.session_state.messages, message_placeholder)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.token_count += len(full_response.split()) * 1.3

# Sidebar
with st.sidebar:
    st.title("Settings")

    st.subheader("Theme")
    selected_theme = st.selectbox('Choose Theme', list(THEMES.keys()))
    if st.button('Apply Theme'):
        save_theme(THEMES[selected_theme])
        st.success('Theme updated! Please refresh the page.')

    st.markdown("---")

    # Model selection
    model = st.radio("Select AI Model", ["Claude", "ChatGPT"],
                     index=0 if st.session_state.current_model == "Claude" else 1)
    if model != st.session_state.current_model:
        st.session_state.current_model = model
        st.session_state.messages = []  # Clear chat when switching models
        st.session_state.token_count = 0

    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    This is a chat interface that supports both Claude and ChatGPT.

    To use:
    1. Select your preferred AI model
    2. Enter your message
    3. Wait for the response
    4. Continue the conversation!
    """)

    # Conversation stats
    st.markdown("---")
    st.subheader("Conversation Stats")
    st.write(f"Messages: {len(st.session_state.messages)}/{MAX_MESSAGES}")
    st.write(f"Estimated tokens: {int(st.session_state.token_count)}/{MAX_TOKENS}")
    progress = st.session_state.token_count / MAX_TOKENS
    st.progress(progress)

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.token_count = 0
        st.session_state.editing_message_index = None