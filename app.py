import openai
import streamlit as st
import requests
import json
import io
import random
from config import INSTRUCTIONS

openai.api_key = "null"
openai.api_base = "https://nyx-beta.samirawm7.repl.co/openai"

models = [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "meta-llama/Llama-2-70b-chat-hf",
    "jondurbin/airoboros-l2-70b-gpt4-1.4.1",
]

icon = io.BytesIO(open('assets/icon.png', 'rb').read())
logo = io.BytesIO(open('assets/logo.png', 'rb').read())

def create_completion(messages, model):
    url = "https://nyx-beta.samirawm7.repl.co/openai/chat/completions"

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": True
    }

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8').replace('data: ', '')
                if decoded != '[DONE]':
                    r = json.loads(decoded)
                    if r['choices'][0]['finish_reason'] is None:
                        yield r['choices'][0]['delta']['content']

st.set_page_config(
    layout="wide",
    page_title="NyX Chatbot",
    page_icon=icon,
    initial_sidebar_state="auto",
)

st.markdown('''
<style>
  [data-testid="stDecoration"] {
    display: none;
    width: 0;
    hight: 0;
  }
</style>
''', unsafe_allow_html=True)


with st.sidebar:
    selected_model = st.selectbox("Model", models)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    elif st.button("🗑️ Clear Session"):
        st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == 'assistant':
        
        with st.chat_message("assistant", avatar=icon):
            st.markdown(message["content"])
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
if prompt := st.chat_input("Send a message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=icon):
        message_placeholder = st.empty()
        full_response = ""
        messages = [{"role": "system", "content": INSTRUCTIONS}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        for chunk in create_completion(model=selected_model, messages=messages):
            full_response += chunk
            message_placeholder.markdown(full_response + random.choice(["⬤", "●"]))
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
