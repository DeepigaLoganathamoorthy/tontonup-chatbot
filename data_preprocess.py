import docx, re
import requests, json, time, os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def call_gemini_structured(prompt):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": schema
        }
    }

    response = requests.post(GEMINI_URL, headers=headers, json=data)

    if response.status_code != 200:
        print("Gemini API error:", response.text)
        raise ValueError("API failed")

    result = response.json()

    try:
        structured_output = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(structured_output)

    except Exception as e:
        print(e)
        print(result)
        raise


#load doc
path = './data/FAQ.docx'
doc = docx.Document(path)
lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

faq_data = []
current_q = None
current_a = []
collecting = False

for line in lines:
    low_line = line.lower()

    if low_line.startswith("question:"):
        if current_q and current_a:
            faq_data.append({
                "question": current_q,
                "answer": " ".join(current_a)
            })

        #reset
        current_q = line.replace("Question:", "").strip()
        current_a = []
        collecting = False

    elif low_line.startswith("answer:"):
        collecting = True
        part = line.replace("Answer:", "").strip()
        if part:
            current_a.append(part)

    else:
        if collecting:
            current_a.append(line)

if current_q and current_a:
    faq_data.append({
        "question": current_q,
        "answer": " ".join(current_a)
    })


def clean_text(t):
    t = t.lower()
    t = re.sub(r"[^\w\s\?\.\,\-\(\)\:\/']", '', t)
    return re.sub(r'\s+', ' ', t).strip()

processed_faqs = []

for i, faq in enumerate(faq_data):
    # build the final list with IDs
    processed_faqs.append({
        "id": f"faq_{i+1:03}",
        "original_question": faq["question"],
        "original_answer": faq["answer"],
        "cleaned_question": clean_text(faq["question"]),
        "cleaned_answer": clean_text(faq["answer"])
    })

# print(processed_faqs[0])


def build_prompt(cleaned_q, cleaned_a):
    return f"""
        You are a data augmentation assistant for a FAQ chatbot.
        
        Question (Malay):
        {cleaned_q}
        
        Answer (Malay):
        {cleaned_a}
        
        Tasks:
        1. Generate 3 alternate user questions (english)
        2. Create a short answer summary (1 sentence)
        3. Translate question and answer into English
        4. Extract steps ONLY if clearly present
        5. Extract keywords (max 5 per language)
        
        Rules:
        - No hallucination
        - Keep concise
        - STRICT JSON only
        
        Format:
        {{
          "alternate_questions": [],
          "answer_summary": "",
          "cleaned_question_en": "",
          "cleaned_answer_en": "",
          "keywords": {{
            "ms": [],
            "en": []
          }},
          "answer_steps": []
        }}
        """




schema = {
    "type": "object",
    "properties": {
        "alternate_questions": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 4
        },
        "answer_summary": {"type": "string"},
        "cleaned_question_en": {"type": "string"},
        "cleaned_answer_en": {"type": "string"},
        "keywords": {
            "type": "object",
            "properties": {
                "ms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5
                },
                "en": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5
                }
            },
            "required": ["ms", "en"]
        },
        "answer_steps": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "alternate_questions",
        "answer_summary",
        "cleaned_question_en",
        "cleaned_answer_en",
        "keywords",
        "answer_steps"
    ]
}



def assign_metadata(cleaned_q):
    q = cleaned_q.lower()

    if "bayar" in q:
        return "subscription_activation_issue", "payment"
    elif "iklan" in q:
        return "ads_in_subscription", "subscription"
    elif "batal" in q:
        return "cancel_subscription", "subscription"
    elif "kata laluan" in q:
        return "password_reset", "account"
    elif "luar negara" in q:
        return "geo_restriction", "technical"
    elif "ralat" in q:
        return "playback_error", "technical"
    elif "langgan" in q:
        return "subscription_upgrade", "subscription"
    elif "tuisyen" in q:
        return "content_information", "content"
    else:
        return "general_issue", "general"


def limit_keywords(keywords):
    return {
        "ms": keywords.get("ms", [])[:5],
        "en": keywords.get("en", [])[:5]
    }


def augment_faq(faq_id, raw_q, raw_a, cleaned_q, cleaned_a):

    intent, category = assign_metadata(cleaned_q)
    prompt = build_prompt(cleaned_q, cleaned_a)

    parsed = call_gemini_structured(prompt)
    
    def normalize_steps(steps):
        if not steps:
            return []
    
        normalized = []
    
        for step in steps:
            # case 1: already string
            if isinstance(step, str):
                normalized.append(step)
                continue
    
            # case 2: dict
            if isinstance(step, dict):
                method = step.get("method", "")
                substeps = step.get("steps", [])
    
                if isinstance(substeps, list):
                    substeps_text = " -> ".join(substeps)
                else:
                    substeps_text = str(substeps)
    
                if method:
                    normalized.append(f"{method}: {substeps_text}")
                else:
                    normalized.append(substeps_text)
    
        return normalized
    

    
    parsed_steps = normalize_steps(parsed.get("answer_steps", []))

    return {
        "id": faq_id,
        "content": {
            "original_question": raw_q,
            "original_answer": raw_a,
            "cleaned_question": cleaned_q,
            "cleaned_answer": cleaned_a,
            "cleaned_question_en": parsed["cleaned_question_en"],
            "cleaned_answer_en": parsed["cleaned_answer_en"],
            "alternate_questions": parsed["alternate_questions"],
            "answer_summary": parsed["answer_summary"],
            #"answer_steps": parsed["answer_steps"]
            "answer_steps": parsed_steps
        },
        "metadata": {
            "intent": intent,
            "category": category,
            "platform": "TontonUp",
            "language": "ms",
            "keywords": limit_keywords(parsed["keywords"])
        }
    }


augmented_results = []

for faq in processed_faqs:
    print("Processing:", faq["id"])

    result = augment_faq(
        faq["id"],
        faq["original_question"],
        faq["original_answer"],
        faq["cleaned_question"],
        faq["cleaned_answer"]
    )

    if result:
        augmented_results.append(result)

    time.sleep(1)
    

if augmented_results:
    print(augmented_results[0]["content"]["original_answer"])
else:
    print("No results generated")
    
    
output_path = './data/augmented_faq.json'
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(augmented_results, f, ensure_ascii=False, indent=2)