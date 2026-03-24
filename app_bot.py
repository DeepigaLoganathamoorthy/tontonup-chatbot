import streamlit as st
from pipe import generate_answer
from datetime import datetime

st.set_page_config(page_title="TontonUp Help", layout="centered")

st.title("TontonUp Support (Beta)")
st.write("Type your problem below, we will do our best to help")

#init session
if 'chat_his' not in st.session_state:
    st.session_state.chat_his = []

#sidebar
with st.sidebar:
    st.subheader("🛠️ Admin Tools")
    if st.button("Reset Chat", use_container_width=True):
        st.session_state.chat_his = []
        st.rerun()
    
    st.divider() # Adds a nice visual line
    
    st.subheader("📡 System Status")
    try:
        from pipe import q_client
        collections = q_client.get_collections().collections
        exists = any(c.name == "faq_collection" for c in collections)
        
        if exists:
            st.success("🟢 Database: Connected")
        else:
            st.warning("🟡 Collection Missing")
            st.info("Run upload_data.py locally.")
    except Exception as e:
        st.error("🔴 Disconnected")
        st.caption(f"Error: {str(e)[:50]}...")

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


if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.chat_his.append({"role": "user", "txt": query})
    
    with st.chat_message("assistant"):
        with st.spinner("Kejap ye..."):
            ans = generate_answer(query)
            st.write(ans)
    
    # Save to history
    st.session_state.chat_his.append({"role": "assistant", "txt": ans})
    st.rerun() 