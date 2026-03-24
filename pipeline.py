import os, requests, streamlit as st
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import json


key = st.secrets.get("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"



@st.cache_resource
def load_stuff():
    m = SentenceTransformer("BAAI/bge-m3")
    db = "./qdrant_data"
    if not os.path.exists(db): os.makedirs(db)
    
    c = QdrantClient(path=db)
    
    try:
        c.get_collection("faq_collection")
    except:
        print("Collection missing! Rebuilding...")
        from qdrant_client.models import VectorParams, Distance, PointStruct
        
        c.recreate_collection(
            collection_name="faq_collection",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        
        with open('./data/augmented_faq.json', 'r') as f:
            data = json.load(f)
            
        points = []
        for i, faq in enumerate(data):
            con = faq["content"]
            # quick and dirty text prep
            txt = f"{con['cleaned_question']} {con.get('answer_summary', '')}"
            v = m.encode(txt, normalize_embeddings=True).tolist()
            
            points.append(PointStruct(
                id=i, 
                vector=v, 
                payload={"content": con, "metadata": faq.get("metadata", {})}
            ))
        
        c.upsert(collection_name="faq_collection", points=points)
        print("Done seeding!")
        
    return m, c


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
    v = model.encode(query, normalize_embeddings=True)
    
    hits = client.query_points(
        collection_name="faq_collection",
        query=v,
        limit=3
    ).points
    
    if not hits: return ""

    ctx = ""
    for h in hits:
        p = h.payload["content"]
        s = " -> ".join(p.get("answer_steps", []))
        ctx += f"Q: {p['cleaned_question']}\nA: {p['cleaned_answer']}\nSteps: {s}\n---\n"
    return ctx

def ask_bot(user_q):
    context = get_context(user_q)
    
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
        return "Maaf, sistem tengah sibuk. Cuba sekejap lagi ye."
    
    # clean up potential markdown asterisks
    return ans.replace("*", "").strip()

# for quick testing in terminal if needed
if __name__ == "__main__":
    test = input("Test query: ")
    print(ask_bot(test))