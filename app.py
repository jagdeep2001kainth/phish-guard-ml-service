import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import tensorflow as tf

from keras.preprocessing.sequence import pad_sequences
import os

app = Flask(__name__)
CORS(app)

# Load models and vectorizers
rf_model = joblib.load("rf_model_combined.pkl")
tfidf_vectorizer = joblib.load("tfidf_vectorizer.pkl")
lstm_model = tf.keras.models.load_model("lstm_model_combined.h5")
tokenizer = joblib.load("tokenizer.pkl")

MAX_SEQUENCE_LENGTH = 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'ok',
        'rf_model': str(type(rf_model)),
        'vectorizer': str(type(tfidf_vectorizer))
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("Step 1: Request received")
        data = request.json['email_text']
        print(f"Step 2: Email text received: {data[:50]}")
        
        transformed_text = tfidf_vectorizer.transform([data])
        print("Step 3: TF-IDF transform done")
        
        rf_prob = rf_model.predict_proba(transformed_text)[:, 1][0]
        print(f"Step 4: RF prediction done: {rf_prob}")

        # if you still have LSTM
        # seq = tokenizer.texts_to_sequences([data])
        # print("Step 5: Tokenizer done")
        # padded_seq = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
        # print("Step 6: Padding done")
        # lstm_prob = lstm_model.predict(padded_seq, verbose=0)[0][0]
        # print(f"Step 7: LSTM prediction done: {lstm_prob}")

        avg_prob = rf_prob
        prediction = "Phishing" if avg_prob > 0.7 else "Safe"
        phishing_percent = round(float(avg_prob) * 100, 2)
        safe_percent = round((1 - float(avg_prob)) * 100, 2)

        print("Step 8: Returning response")
        return jsonify({
            'prediction': prediction,
            'phishing_probability': phishing_percent,
            'safe_probability': safe_percent,
            'reason': get_reason(data)
        })
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500    

def get_reason(email_text):
    suspicious_keywords = ['verify', 'login', 'urgent', 'password', 'click here', 'account', 'suspend']
    found = [word for word in suspicious_keywords if word.lower() in email_text.lower()]
    return "Suspicious keywords found: " + ", ".join(found) if found else "No major phishing indicators found"


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         data = request.json['email_text']

#         # RF Prediction
#         transformed_text = tfidf_vectorizer.transform([data])
#         rf_prob = rf_model.predict_proba(transformed_text)[:, 1][0]

#         # LSTM Prediction
#         seq = tokenizer.texts_to_sequences([data])
#         padded_seq = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
#         lstm_prob = lstm_model.predict(padded_seq, verbose=0)[0][0]

#         # Ensemble Prediction
#         avg_prob = (rf_prob + lstm_prob) / 2
#         prediction = "Phishing" if avg_prob > 0.8 else "Safe"
#         phishing_percent = round(avg_prob * 100, 2)
#         safe_percent = round((1 - avg_prob) * 100, 2)

#         return jsonify({
#             'prediction': prediction,
#             'phishing_probability': phishing_percent,
#             'safe_probability': safe_percent,
#             'reason': get_reason(data)
            
#         })
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    