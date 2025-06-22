

from flask import Flask, render_template, request
from scam_detector import detect_keywords, guess_scam_type, find_similar, check_contact_scam

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    input_type = request.form.get("input_type")

    if input_type == "message":
        message = request.form.get("message", "")

        # 🧠 Normalization is handled INSIDE scam_detector.py
        is_scam, keywords, risk_score = detect_keywords(message)
        scam_type = guess_scam_type(keywords, message)
        similar_cases, exact_match_found = find_similar(message, scam_type)

        if exact_match_found:
            likelihood = 100
        elif similar_cases and risk_score > 0:
            likelihood = risk_score
        else:
            likelihood = 0

        return render_template("result.html",
                               input_type="message",
                               message=message,
                               scam_type=scam_type,
                               similar_cases=similar_cases,
                               likelihood=likelihood)

    elif input_type == "contact":
        contact = request.form.get("contact", "")
        scam_type, found, risk_score = check_contact_scam(contact)
        likelihood = risk_score if found else 0

        return render_template("result.html",
                               input_type="contact",
                               contact=contact,
                               scam_type=scam_type,
                               similar_cases=[],
                               likelihood=likelihood)

    return "Invalid input."

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

