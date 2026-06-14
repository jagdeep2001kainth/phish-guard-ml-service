from flask import Flask, request, jsonify 
from flask_cors import CORS
import joblib
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)
CORS(app)

# Load models and vectorizers
rf_model = joblib.load("rf_model_combined.pkl")
tfidf_vectorizer = joblib.load("tfidf_vectorizer.pkl")
lstm_model = tf.keras.models.load_model("lstm_model_combined.h5")
tokenizer = joblib.load("tokenizer.pkl")

MAX_SEQUENCE_LENGTH = 500  # Match training config

# Helper function to generate a basic explanation
def get_reason(email_text):
    suspicious_keywords = ['verify', 'login', 'urgent', 'password', 'click here', 'account', 'suspend']
    found = [word for word in suspicious_keywords if word.lower() in email_text.lower()]
    return "Suspicious keywords found: " + ", ".join(found) if found else "No major phishing indicators found"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json['email_text']

        # RF Prediction
        transformed_text = tfidf_vectorizer.transform([data])
        rf_prob = rf_model.predict_proba(transformed_text)[:, 1][0]

        # LSTM Prediction
        seq = tokenizer.texts_to_sequences([data])
        padded_seq = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
        lstm_prob = lstm_model.predict(padded_seq, verbose=0)[0][0]

        # Ensemble Prediction
        avg_prob = (rf_prob + lstm_prob) / 2
        prediction = "Phishing" if avg_prob > 0.8 else "Safe"

        phishing_percent = round(avg_prob * 100, 2)
        safe_percent = round((1 - avg_prob) * 100, 2)

        return jsonify({
            'prediction': prediction,
            'phishing_probability': phishing_percent,
            'safe_probability': safe_percent
        })

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
