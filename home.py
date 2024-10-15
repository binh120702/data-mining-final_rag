import numpy as np
import streamlit as st
import sqlite3
import os
import pandas as pd
import requests
from chat_handle import ChatHandler
import json

header_sticky = """
    <style>
        div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
            position: sticky;
            top: 2.875rem;
            background-color: white;
            z-index: 999;
        }
        .fixed-header { 
        }
    </style>
        """

def display_existing_messages_and_return_context():
    context_chat = ''
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    for message in st.session_state["messages"][-min(len(st.session_state["messages"]), 6):]:
        role = message["role"]
        content = message["content"]
        context_chat = context_chat + f"{role} : {content} |"
    return context_chat

def add_user_message_to_session(prompt):
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

def add_bot_message_to_session(response):
    if response:
        with st.chat_message("ai"):
            full_response = st.write_stream(response)
        st.session_state["messages"].append({"role": "ai", "content": full_response})

def call_api(prompt):
    handler = st.session_state['handler']
    result = handler.handle_chat(prompt)
    return result

@st.cache_resource 
def prepare_model():
    return ChatHandler()

def chat():
    chat_container = st.container()
    chat_container.header("Data Mining Final Project", divider="rainbow")
      
    st.session_state['handler'] = prepare_model()

    ### Custom CSS for the sticky header
    chat_container.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
    st.markdown(header_sticky, unsafe_allow_html=True)
    
    
    display_existing_messages_and_return_context()
    query = st.chat_input("Say something")
    if query:
        add_user_message_to_session(query)
        response = call_api(query)
        add_bot_message_to_session(response)

def side_bar():
    with st.sidebar:
        st.header('**RAG**', divider='rainbow')
        if st.button("New conversation"):
            st.session_state["messages"] = []
            st.session_state["handler"].new_conversation()
            display_existing_messages_and_return_context()
        st.header('**Add documents**', divider='rainbow')
        uploaded_file = st.file_uploader("Choose a file")
        if st.button("Add documents") and uploaded_file is not None:
            with st.spinner('Wait for it...'):
                st.session_state["handler"].add_documents([uploaded_file])
        
    
if __name__ == "__main__":
    side_bar()
    chat()