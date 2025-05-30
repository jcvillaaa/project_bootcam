import streamlit as st
from agents.cyber_agent.run_agent import extecute

# Page configuration
st.set_page_config(page_title="Red-Grey Chat", layout="centered")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Inject custom CSS for red and grey theme
st.markdown("""
    <style>
        body {
            background-color: #2e2e2e;
        }
        .chat-box {
            background-color: #444;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
        }
        .user-message {
            background-color: #ff4b4b;
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: right;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💬 Red & Grey Chat")

# Function to generate a response based on user input
def get_response(user_input):
    if "hola" in user_input.lower():
        return "¡Hola! ¿Cómo estás?"
    elif "adiós" in user_input.lower():
        return "¡Hasta luego!"
    else:
        return f"Dijiste: {user_input}"

# Display chat history
for entry in st.session_state.chat_history:
    if entry['role'] == 'user':
        st.markdown(f"<div class='user-message'>{entry['message']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-box'>{entry['message']}</div>", unsafe_allow_html=True)

# User input
prompt = st.chat_input("Escribe algo...")
print("***prompt: ", prompt)
if prompt:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "message": prompt})

    # Generate response
    response = extecute(prompt)
    print(response.get("output"))
    st.session_state.chat_history.append({"role": "bot", "message": response.get("output")})

    st.rerun()
