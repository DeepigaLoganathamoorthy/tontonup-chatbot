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
├── pipeline.py                    # the logic for the brain (lite version) (Vector Search + Gemini API)
├── requirements.txt               # Dependency list
├── data_preprocess.py             # the data cleaning and schema decisions
├── embed_model.py                 # embeddings & models used here for RAG
└── data/
    ├── FAQ.docx                   # Raw data
    └── augmented_faq.json         # augmented/metadata
    └── faq_with_embeddings.json   # embeddings imposed
```

---

## The Architecture

  - **Embeddings:** `BAAI/bge-m3`  
  *(Chosen because it works very well with both English and Malay, even when users mix both languages in one sentence. It helps the system understand meaning better and improves search accuracy.)*

- **Vector Database:** `Qdrant`  
  *(Used because it is fast, easy to run locally, and supports filtering by metadata like intent or category. It does not need external services, which makes the system simpler and more stable.)*


- **LLM:** `Gemini 2.5 Flash`  
  *(Fast, cheap, and supports structured JSON output)*

- **UI:** `Streamlit`  
  *(Simple chat interface with feedback logging)*

---

## Setup & Installation

### 1. Clone & Install

You'll need **Python 3.9+**. Some libraries like `sentence-transformers` are heavy (~2GB download on first run).

```bash
pip install streamlit sentence-transformers qdrant_client python-docx requests python-dotenv
```

---

### 2. Secrets Configuration

If running locally, create a `.env` file.  
If deploying to **Streamlit Cloud**, add this to your Secrets:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

---

### 3. Running the App

```bash
streamlit run app_bot.py
```

---

## Key Features & "Human" Logic

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

## ⚠️ Known Issues / Troubleshooting

- **Cold Starts**  
  Streamlit Cloud might "sleep". The first interaction takes ~30 seconds to load the embedding model into RAM.

- **File Locking**  
  If you see a `RuntimeError` regarding Qdrant, it usually means a ghost process is locking the database folder.  
  → Reboot the app from the Streamlit dashboard to fix.

- **Markdown Output Cleaning**  
  The bot strips most asterisks (`*`) to keep responses clean and human-friendly as per TontonUp guidelines.