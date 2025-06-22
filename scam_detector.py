# ✅ Final fix — scam_detector.py with phone number/email contact check from dedicated column

import pandas as pd
import re
import string

GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1GN9WA6XKslGycoIyPDzYEr4kLP_t6JXG4i_Fp-54V-w/export?format=csv"

KEYWORDS = [
    'job offer', 'interview', 'resume', 'salary', 'training',
    'loan', 'credit', 'emi', 'insta loan', 'low interest',
    'upi', 'verify upi', 'bank', 'kyc', 'account', 'ifsc', 'scan qr', 'blocked', 'payment link',
    'otp', 'winner', 'lottery', 'gift card', 'reward', 'prize',
    'bitcoin', 'investment', 'bonus'
]

def normalize(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_data():
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        df.columns = df.columns.str.strip().str.lower()
        df['message'] = df['paste the scam message/explain the call details'].fillna('').astype(str).apply(normalize)
        df['type'] = df['what type of scam was it?'].fillna('').astype(str).str.strip().str.title()
        df['contact'] = df['phone number/contact used by the scammer'].fillna('').astype(str).apply(normalize)
        return df
    except Exception as e:
        print("❌ Failed to load dataset:", e)
        return pd.DataFrame(columns=["message", "type", "contact"])

def detect_keywords(text):
    clean_text = normalize(text)
    found_keywords = [kw for kw in KEYWORDS if kw in clean_text]
    risk_score = 0
    if found_keywords:
        risk_score = 50 + (len(found_keywords) * 10)
        risk_score = min(risk_score, 85)
    return (len(found_keywords) > 0), found_keywords, risk_score

def guess_scam_type(keywords, text=""):
    full_text = " ".join(keywords).lower() + " " + text.lower()
    if any(x in full_text for x in ['job', 'interview', 'resume', 'salary', 'training']):
        return "Job Scam"
    elif any(x in full_text for x in ['loan', 'credit', 'emi', 'insta loan']):
        return "Loan Scam"
    elif any(x in full_text for x in ['upi', 'bank', 'kyc', 'account', 'ifsc', 'scan', 'verify', 'payment']):
        return "Banking Scam"
    elif any(x in full_text for x in ['gift', 'winner', 'prize', 'lottery', 'reward']):
        return "Prize Scam"
    else:
        return "General Scam"

def find_similar(user_text, scam_type):
    df = load_data()
    user_text_clean = normalize(user_text)
    similar_cases = []
    exact_match_found = False
    for _, row in df.iterrows():
        db_text = row['message']
        if user_text_clean == db_text:
            exact_match_found = True
            similar_cases = [{"message": row['message'], "type": row['type'], "match": "exact"}]
            break
        elif any(word in db_text for word in user_text_clean.split()):
            similar_cases.append({"message": row['message'], "type": row['type'], "match": "partial"})
    return similar_cases, exact_match_found

def check_contact_scam(contact):
    df = load_data()
    contact_clean = normalize(contact)

    for _, row in df.iterrows():
        if contact_clean == row['contact'] or contact_clean in row['message']:
            return row['type'], True, 100

    found, _, risk_score = detect_keywords(contact_clean)
    if found:
        return "Keyword Match", True, risk_score

    return "Unknown", False, 0
