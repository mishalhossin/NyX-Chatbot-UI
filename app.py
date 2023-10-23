import streamlit as st
import requests
import json
import io
import random
import openai
from config import INSTRUCTIONS
from helper_modules import search

models = [
    "meta-llama/Llama-2-70b-chat-hf",
    "jondurbin/airoboros-l2-70b-gpt4-1.4.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "gpt-3.5-turbo-0613",
]

icon = io.BytesIO(open('assets/icon.png', 'rb').read())
logo = io.BytesIO(open('assets/logo.png', 'rb').read())

@st.cache_resource
def create_completion(messages, model, api_key):
    openai.api_key = api_key
    openai.api_base = 'https://nyx-api.samirawm7.repl.co/openai'

    completion = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )
    yield completion.choices[0].message

st.set_page_config(
    layout="wide",
    page_title="NyX Chatbot",
    page_icon=icon,
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://github.com/mishalhossin/NyX-Chatbot-UI/issues/new",
        'About': "This project provides a user-friendly web-based user interface for interacting with Nyx Chatbot"
    }
)

st.markdown(
'''
<style>
  [data-testid="stDecoration"] {
    display: none;
    width: 0;
    hight: 0;
  }
</style>
''', unsafe_allow_html=True)


api_key = st.sidebar.text_input("API key", placeholder="Get API key by running /generate_key", type='password').strip()
input_api_key = True if api_key else False
if input_api_key:
    internet = st.toggle('Internet access')
    with st.sidebar:  
        st.session_state.selected_model = st.selectbox("Model", models)
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.avatar = 'https://api.dicebear.com/7.x/thumbs/svg?seed={}&backgroundColor=19c37d,1ed4a3&backgroundType=gradientLinear&shapeColor=0a5b83,1c799f'.format(random.randbytes(5).hex())
        elif st.button("Clear Session", use_container_width=True, type='primary'):
            msg = st.toast('Clearing Session data...', icon='🗑️')
            st.session_state.messages = []
            msg.toast("Cleared Session data", icon="🗑️")
        st.session_state.instructions = st.text_area("Instructions", INSTRUCTIONS, height=200)
        st.caption("This project is licensed under the MIT License. See the [LICENSE](https://github.com/mishalhossin/NyX-Chatbot-UI/blob/main/LICENSE) file for details.")
        
    for message in st.session_state.messages:
        if message["role"] == 'assistant':
            
            with st.chat_message("assistant", avatar=icon):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar=st.session_state.avatar):
                st.markdown(message["content"])

    if prompt := st.chat_input("Send a message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=st.session_state.avatar):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar=icon):
            message_placeholder = st.empty()
            full_response = ""
            messages = [{"role": "system", "content": st.session_state.instructions}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            if internet:
                search_results = search(prompt)
                if search_results:
                    messages.append({"role": "user", "content": search_results['content']})
            for chunk in create_completion(model=st.session_state.selected_model, messages=messages, api_key=api_key):
                full_response += chunk
                message_placeholder.markdown(full_response + random.choice(["⬤", "●"]))
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
