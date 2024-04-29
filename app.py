import os
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

def initialize_state():
    """Inicializa las claves necesarias en st.session_state."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "assistant" not in st.session_state:
        st.session_state["assistant"] = ChatPDF()

def display_messages():
    """Muestra los mensajes en el chat."""
    st.subheader("Chat")
    if "messages" in st.session_state:
        for i, (msg, is_user) in enumerate(st.session_state["messages"]):
            message(msg, is_user=is_user, key=str(i))
    else:
        st.write("No messages available.")
    st.session_state["thinking_spinner"] = st.empty()

def process_input():
    """Procesa la entrada del usuario."""
    try:
        if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
            user_text = st.session_state["user_input"].strip()
            with st.session_state["thinking_spinner"], st.spinner(f"Thinking"):
                agent_text = st.session_state["assistant"].ask(user_text)

            st.session_state["messages"].append((user_text, True))
            st.session_state["messages"].append((agent_text, False))
    except Exception as e:
        st.error(f"Error processing input: {str(e)}")

def read_and_save_file():
    """Lee y guarda el archivo subido."""
    try:
        st.session_state["assistant"].clear()
        st.session_state["messages"] = []
        st.session_state["user_input"] = ""

        for file in st.session_state["file_uploader"]:
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                tf.write(file.getbuffer())
                file_path = tf.name

            with st.session_state["ingestion_spinner"], st.spinner(f"Ingesting {file.name}"):
                st.session_state["assistant"].ingest(file_path)
            os.remove(file_path)
    except Exception as e:
        st.error(f"Error reading and saving file: {str(e)}")

def page():
    """Configura la página y la funcionalidad."""
    initialize_state()

    st.header("ChatPDF")

    st.subheader("Upload a document")
    st.file_uploader(
        "Upload document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

if __name__ == "__main__":
    page()
