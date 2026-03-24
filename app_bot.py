import streamlit as st
from pipe import generate_answer
import os
from datetime import datetime

st.set_page_config(page_title="TontonUp Help", layout="centered")

st.title("TontonUp Support (Beta)")
st.write("Type your problem below, we will do our best to help")

#init session
if 'chat_his' not in st.session_state:
    st.session_state.chat_his = []

#sidebar
with st.sidebar:
    st.subheader("Admin Tools")
    if st.button("Reset Chat"):
        st.session_state.chat_his = []
        st.rerun()

#chat display
for i, m in enumerate(st.session_state.chat_his):
    role = m["role"]
    with st.chat_message(role):
        st.markdown(m["txt"]) 

        if role == "bot" and i == len(st.session_state.chat_his)-1:
            spacer, c1, c2 = st.columns([0.8, 0.1, 0.1])

            with spacer:
                st.empty()

            with c1:
                if st.button("👍", key=f"up_{i}"):
                    pass

            with c2:
                if st.button("👎", key=f"down_{i}"):
                    pass

query = st.chat_input("Dah bayar tapi takleh tengok?")

if query:
    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.chat_his.append({"role": "user", "txt": query})
    
    with st.chat_message("assistant"):
        with st.spinner("wait ya..."):
            ans = generate_answer(query)
            st.write(ans)
    
    # save to history
    st.session_state.chat_his.append({"role": "assistant", "txt": ans})
