import streamlit as st
from embed_model import generate_answer
import csv
from datetime import datetime

st.set_page_config(page_title="TontonUp Assistant", page_icon="🎬")

st.title("🎬 TontonUp Assistant")
st.caption("Ask anything about TontonUp")

# -----------------------------
# INIT SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_user_query" not in st.session_state:
    st.session_state.last_user_query = ""


# -----------------------------
# SAVE FEEDBACK
# -----------------------------
def save_feedback(query, response, feedback):
    with open("feedback_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            datetime.now().isoformat(),
            query,
            response,
            feedback
        ])


# -----------------------------
# DISPLAY CHAT
# -----------------------------
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # 👇 show feedback ONLY for assistant messages
        if msg["role"] == "assistant":
            col1, col2 = st.columns(2)

            with col1:
                if st.button("👍 Helpful", key=f"up_{i}"):
                    save_feedback(
                        st.session_state.messages[i-1]["content"],  # user query
                        msg["content"],
                        "positive"
                    )
                    st.success("Thanks for your feedback!")

            with col2:
                if st.button("👎 Not helpful", key=f"down_{i}"):
                    save_feedback(
                        st.session_state.messages[i-1]["content"],
                        msg["content"],
                        "negative"
                    )
                    st.warning("Got it — we'll improve this.")


# -----------------------------
# USER INPUT
# -----------------------------
user_input = st.chat_input("Type your question...")

if user_input:
    st.session_state.last_user_query = user_input

    # save user msg
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # generate answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_answer(user_input)
            st.markdown(response)

    # save bot msg
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("About")
    st.write("TontonUp AI Assistant")

    if st.button("Clear Chat"):
        st.session_state.messages = []


    #streamlit run app.py