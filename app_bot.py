import streamlit as st
from pipeline import ask_bot
import os
from datetime import datetime

st.set_page_config(page_title="TontonUp Help", layout="centered")

st.title("TontonUp Support (Beta)")
st.write("Type your problem below, we will do our best to help")

# init session
if 'chat_his' not in st.session_state:
    st.session_state.chat_his = []

# sidebar
with st.sidebar:
    st.subheader("Admin Tools")
    if st.button("Reset Chat"):
        st.session_state.chat_his = []
        st.rerun()

# chat display
for i, m in enumerate(st.session_state.chat_his):
    role = m["role"]
    with st.chat_message(role):
        st.write(m["txt"])
         
        # Feedback buttons for the last bot message
        if role == "bot" and i == len(st.session_state.chat_his)-1:
            c1, c2, c3 = st.columns([0.05, 0.05, 0.9]) # Tight columns for emojis
            
            with c1:
                if st.button("👍", key=f"up_{i}"):
                    st.session_state.feedback = "Thanks!"
            with c2:
                if st.button("👎", key=f"down_{i}"):
                    st.session_state.feedback = "Noted."
            
            # This makes the text appear right next to the buttons
            if 'feedback' in st.session_state and st.session_state.feedback:
                with c3:
                    st.caption(f":green[{st.session_state.feedback}]")

query = st.chat_input("Dah bayar tapi takleh tengok?")

if query:
    st.session_state.chat_his.append({"role": "user", "txt": query})
    with st.chat_message("user"):
        st.write(query)
    
    with st.chat_message("bot"):
        with st.spinner("wait ah..."):
            ans = ask_bot(query)
            st.write(ans)
    
    # save to history
    st.session_state.chat_his.append({"role": "bot", "txt": ans})
    st.rerun()