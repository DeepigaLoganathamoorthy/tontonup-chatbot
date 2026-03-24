import streamlit as st
from pipeline import ask_bot # the brain
import csv, os
from datetime import datetime


st.set_page_config(page_title="TontonUp Help", layout="centered")

st.title("TontonUp Support (Beta)")
st.write("Type your problem below, we will do our best to help")

#init session
if 'chat_his' not in st.session_state:
    st.session_state.chat_his = []

#feedback func
def log_it(q, a, type):
    f_path = "feedback_log.csv"
    head = not os.path.exists(f_path)
    with open(f_path, "a", newline="") as f:
        w = csv.writer(f)
        if head:
            w.writerow(["time", "query", "bot_ans", "score"])
        w.writerow([datetime.now(), q, a, type])
    print(f"DEBUG: saved {type} feedback") # dev debug lol

#sidebar
with st.sidebar:
    st.subheader("Admin Tools")
    if st.button("Reset Chat"):
        st.session_state.chat_his = []
        st.rerun()
    st.info("Logs saved to local csv")

#chat
for i, m in enumerate(st.session_state.chat_his):
    role = m["role"]
    with st.chat_message(role):
        st.write(m["txt"])
         
        if role == "bot" and i == len(st.session_state.chat_his)-1:
            # We add a 0.8 width "spacer" column first
            # The buttons (0.1 and 0.1) get shoved to the far right
            spacer, c1, c2 = st.columns([0.8, 0.1, 0.1])
            
            with c1:
                if st.button("👍", key=f"up_{i}"):
                    u_q = st.session_state.chat_his[i-1]["txt"]
                    log_it(u_q, m["txt"], "GOOD")
                    st.toast("Thanks!")
            with c2:
                if st.button("👎", key=f"down_{i}"):
                    u_q = st.session_state.chat_his[i-1]["txt"]
                    log_it(u_q, m["txt"], "BAD")
                    st.toast("Noted.")


query = st.chat_input("Dah bayar tapi takleh tengok?")

if query:
    st.session_state.chat_his.append({"role": "user", "txt": query})
    with st.chat_message("user"):
        st.write(query)
    
    with st.chat_message("bot"):
        with st.spinner("wait ah..."):
            ans = ask_bot(query)
            st.write(ans)
    
    #save to history
    st.session_state.chat_his.append({"role": "bot", "txt": ans})
    
    st.rerun()



    #streamlit run app.py