import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app)

rf_model = joblib.load("rf_model_combined.pkl")
tfidf_vectorizer = joblib.load("tfidf_vectorizer.pkl")

def get_reason(email_text):
    suspicious_keywords = ['verify', 'login', 'urgent', 'password', 'click here', 'account', 'suspend']
    found = [word for word in suspicious_keywords if word.lower() in email_text.lower()]
    return "Suspicious keywords found: " + ", ".join(found) if found else "No major phishing indicators found"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['email_text']
        transformed_text = tfidf_vectorizer.transform([data])
        rf_prob = rf_model.predict_proba(transformed_text)[:, 1][0]
        prediction = "Phishing" if rf_prob > 0.7 else "Safe"
        phishing_percent = round(float(rf_prob) * 100, 2)
        safe_percent = round((1 - float(rf_prob)) * 100, 2)
        return jsonify({
            'prediction': prediction,
            'phishing_probability': phishing_percent,
            'safe_probability': safe_percent,
            'reason': get_reason(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)