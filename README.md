# TontonUp FAQ Support Bot (RAG + Gemini)

A custom Retrieval-Augmented Generation (RAG) assistant designed for TontonUp customer support. It handles both English and Bahasa Malaysia queries by combining vector search with the Gemini 1.5 Flash API.

---

## The Architecture

- **Embeddings:** `BAAI/bge-m3`  
  *(Chosen for superior English/Malay code-switching support)*

- **Vector Database:** `Qdrant`  
  *(Local storage mode)*

- **LLM:** `Gemini 2.5 Flash`  
  *(Fast, cheap, and supports structured JSON output)*

- **UI:** `Streamlit`  
  *(Simple chat interface with feedback logging)*

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