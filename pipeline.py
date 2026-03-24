import os, requests, streamlit as st
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# --- CONFIG & KEYS ---
# getting key from streamlit secrets
key = st.secrets.get("GEMINI_API_KEY")

# fixed the model name to 1.5 since 2.5 isnt out yet lol
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"


# --- LOAD RESOURCES (CACHED) ---
@st.cache_resource
def load_stuff():
    # pull bge model from hub
    m = SentenceTransformer("BAAI/bge-m3")
    # connect to the local qdrant folder
    c = QdrantClient(path="./qdrant_data")
    return m, c

model, client = load_stuff()

# --- THE LOGIC ---

def call_gemini(p):
    if not key: return "API Key missing!"
    
    payload = {
        "contents": [{"parts": [{"text": p}]}]
    }
    
    try:
        r = requests.post(url, json=payload)
        res = r.json()
        return res["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return None

def get_context(query):
    # vectorize the user question
    v = model.encode(query, normalize_embeddings=True)
    
    # search top 3
    hits = client.query_points(
        collection_name="faq_collection",
        query=v,
        limit=3
    ).points
    
    if not hits: return ""

    # build a messy string of context
    ctx = ""
    for h in hits:
        p = h.payload["content"]
        s = " -> ".join(p.get("answer_steps", []))
        ctx += f"Q: {p['cleaned_question']}\nA: {p['cleaned_answer']}\nSteps: {s}\n---\n"
    return ctx

def ask_bot(user_q):
    # 1. get matches
    context = get_context(user_q)
    
    # 2. build prompt
    prompt = f"""
    You are a friendly TontonUp support bot. 
    Use the context to answer. If not there, ask them to email support@tonton.com.my.
    Reply in the same language as the user (Malay or English).
    
    Context:
    {context}
    
    User: {user_q}
    """
    
    # 3. get llm response
    ans = call_gemini(prompt)
    
    if not ans:
        return "Maaf, sistem tengah sibuk. Cuba lagi jap lagi."
    
    # clean up potential markdown asterisks
    return ans.replace("*", "").strip()

# for quick testing in terminal if needed
if __name__ == "__main__":
    test = input("Test query: ")
    print(ask_bot(test))