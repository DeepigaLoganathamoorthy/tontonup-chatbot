# TontonUp FAQ Support Bot (RAG + Gemini)

A professional **Retrieval-Augmented Generation (RAG)** assistant designed for TontonUp customer support. This system can handle both **English and Bahasa Malaysia queries smoothly** by combining semantic search with the **Gemini 2.5 Flash API**.

---
## The Architecture (Detailed Design)

This system uses a **modular RAG pipeline** to make sure it is reliable, supports multiple languages, and reduces hallucination.

Instead of a simple flow, this system includes:
- data augmentation  
- intent-based retrieval  
- confidence-based fallback logic  

to improve accuracy and give better responses.

---

### 1. Data Ingestion & Structuring

- Source data is extracted from a `.docx` FAQ file using a **rule-based parser** to identify `Question:` and `Answer:` blocks.
- Each FAQ is converted into a structured format:

**Normalization**
- Lowercasing
- Symbol cleaning
- Whitespace normalization  
→ Reduces noise in retrieval.

**Storage**
- Saved into: `augmented_faq.json`

---

### 2. LLM-Based Data Augmentation

Each entry is enriched using **Gemini 2.5 Flash** with a strict JSON schema to generate:

- 3 Alternate Questions (query expansion)
- Answer Summary (semantic compression)
- Cross-lingual Support (English translations of Malay content)
- Procedural Extraction (step-by-step instructions from long answers)

---

### 3. Metadata & Intent Tagging

FAQs are assigned lightweight metadata for filtered retrieval:

- **Intents**:  
  `subscription_activation_issue`, `password_reset`, `playback_error`, etc.

- **Categories**:  
  `payment`, `technical`, `content`

- **Analytics**:  
  Enables tracking of common user issues

---

### 4. Embedding Strategy

- **Model**: `BAAI/bge-m3` (Multilingual powerhouse)

- **Normalization**:

```normalize_embeddings=True``` :: Ensures stable cosine similarity performance

---

### 5. Vector Database (Qdrant)

- **Storage**: Local persistent storage in `./qdrant_data`
- **Metric**: Cosine Similarity
- **Vector Size**: 1024

**Why Qdrant?**
- Native metadata filtering
- Fast local inference
- No external API dependency

---

### 6. Retrieval & Answering Pipeline

The system evaluates confidence to prevent hallucinations:

- **Intent Classification**  
Gemini classifies the user query into a specific intent

- **Filtered Search**  
Qdrant searches within that intent

- **Confidence Check**
- If score ≥ 0.7 → Return original FAQ answer (**100% accuracy**)
- If score < 0.7 → Build context from top 3 hits + Gemini generates response

- **Fallback**
- If no relevant context → redirect to  
  `support@tonton.com.my`

---

## Project Structure

```text
.
├── app_bot.py                     # Streamlit UI & Chat Logic
├── pipe.py                        # the logic for the brain (lite version) (Vector Search + Gemini API)
├── requirements.txt               # Dependency list
├── Dockerfile                     # Containerization
├── data_preprocess.py             # the data cleaning and schema decisions
├── embed_model.py                 # embeddings & models used here for RAG
├── upload_qdrant.py               # store embeddings in Qdrant cloud
└── data/
    ├── FAQ.docx                   # Raw data
    └── augmented_faq.json         # augmented/metadata
    └── faq_with_embeddings.json   # embeddings imposed
```

---

## Overall Technical Stack
- **Embeddings:** `BAAI/bge-m3` 
(Chosen for its elite performance in handling "Manglish" and code-switching).

- **Vector Database:** Qdrant 
(Supports native metadata filtering and fast local/cloud inference).

- **LLM:** Gemini 2.5 Flash 
(Requirement & supports Malaysian/English language rules).

- **UI:** Streamlit 
(Interactive chat interface with admin status monitoring).

- **Deployment:** Fully Dockerized for consistent environment scaling.
---

## Setup & Installation

### 1. Environment Configuration
Create a **.env** file in the root directory with the following variables:

```bash
GEMINI_API_KEY=your_google_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
GEMINI_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```
### 2. Running with Docker
The fastest way to get the system running in a contained environment:

```bash
#Build the image
docker build -t tontonup-bot .

#Run the container
docker run -d -p 8501:8501 --name tonton-live --env-file .env tontonup-bot
Access the bot at: http://localhost:8501
```
### 3. Local Development
```bash
pip install -r requirements.txt
streamlit run app_bot.py
```
---

## Features & Logic

- **Multi-lingual Handling**  
  Uses the `BGE-M3` model specifically to catch nuances in Manglish/Malay slang  
  *(e.g., "takleh", "dah bayar")*

- **Auto-Seeding**  
  If `qdrant_data` is missing or the collection is empty, `pipeline.py` will automatically read your JSON and rebuild the vector store on startup.

- **Confidence Threshold**  
  The bot checks the search score. If the match is weak, it defaults to a polite *"Please email support"* instead of making things up.

- **Feedback System**  
  Includes 👍 / 👎 buttons. This can be used in future for logs.
---
## Issues

- **Cold Starts**  
  Streamlit Cloud might "sleep". The first interaction takes ~30 seconds to load the embedding model into RAM.

- **File Locking**  
  If you see a `RuntimeError` regarding Qdrant, it usually means a ghost process is locking the database folder.  
  → Reboot the app from the Streamlit dashboard to fix.

- **Markdown Output Cleaning**  
  The bot strips most asterisks (`*`) to keep responses clean and human-friendly as per TontonUp guidelines.