from flask import Flask, request, jsonify
import joblib
import pandas as pd
import sqlite3
import os
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------
# Load trained models and scaler
# ---------------------------------------------------
dt_model = joblib.load(os.path.join(BASE_DIR, '../models/decision_tree_model.pkl'))
feature_columns = joblib.load(os.path.join(BASE_DIR, '../models/feature_columns.pkl'))
kmeans_model = joblib.load(os.path.join(BASE_DIR, '../models/kmeans_model.pkl'))
cluster_scaler = joblib.load(os.path.join(BASE_DIR, '../models/cluster_scaler.pkl'))
feature_scaler = joblib.load(os.path.join(BASE_DIR, '../models/feature_scaler.pkl'))

NUMERIC_COLS = ['Temperature(F)', 'Humidity(%)', 'Visibility(mi)', 'Wind_Speed(mph)']

print("Models loaded successfully")
print("Feature columns:", feature_columns)

# ---------------------------------------------------
# Set up SQLite database
# ---------------------------------------------------
DB_PATH = os.path.join(BASE_DIR, '../../database/roadsense.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            wind_speed REAL,
            hour INTEGER,
            weather TEXT,
            predicted_severity TEXT,
            cluster INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "RoadSense Flask backend is running. Use POST /predict or GET /history."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if data is None:
            return jsonify({'error': 'No JSON body received'}), 400

        row = pd.DataFrame([[0] * len(feature_columns)], columns=feature_columns, dtype=float)

        if 'Temperature(F)' in row.columns:
            row.at[0, 'Temperature(F)'] = float(data.get('temperature', 0))
        if 'Humidity(%)' in row.columns:
            row.at[0, 'Humidity(%)'] = float(data.get('humidity', 0))
        if 'Wind_Speed(mph)' in row.columns:
            row.at[0, 'Wind_Speed(mph)'] = float(data.get('wind_speed', 0))
        if 'Visibility(mi)' in row.columns:
            row.at[0, 'Visibility(mi)'] = float(data.get('visibility', 0))
        if 'Hour' in row.columns:
            row.at[0, 'Hour'] = float(data.get('hour', 0))
        if 'Sunrise_Sunset' in row.columns:
            row.at[0, 'Sunrise_Sunset'] = 1.0 if data.get('is_night') else 0.0
        if 'Start_Lat' in row.columns:
            row.at[0, 'Start_Lat'] = float(data.get('lat', 0))
        if 'Start_Lng' in row.columns:
            row.at[0, 'Start_Lng'] = float(data.get('lng', 0))

        weather_col = f"Weather_Condition_{data.get('weather', 'Other')}"
        if weather_col in row.columns:
            row.at[0, weather_col] = 1.0

        # Apply the same scaling used during training
        row[NUMERIC_COLS] = feature_scaler.transform(row[NUMERIC_COLS])

        # Classification prediction (with probability)
        pred_proba = dt_model.predict_proba(row[feature_columns])[0]
        pred = dt_model.predict(row[feature_columns])[0]
        major_prob = round(float(pred_proba[1]), 3)
        severity_label = "Major Severity" if int(pred) == 1 else "Minor Severity"

        # Clustering prediction (raw values, scaled separately with cluster_scaler)
        cluster_features = [[
            float(data.get('lat', 0)),
            float(data.get('lng', 0)),
            float(data.get('hour', 0)),
            float(data.get('temperature', 0)),
            float(data.get('visibility', 0))
        ]]
        cluster_scaled = cluster_scaler.transform(cluster_features)
        cluster = int(kmeans_model.predict(cluster_scaled)[0])

        # Log to database
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'INSERT INTO predictions (temperature, humidity, wind_speed, hour, weather, predicted_severity, cluster) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (data.get('temperature', 0), data.get('humidity', 0), data.get('wind_speed', 0),
             data.get('hour', 0), data.get('weather', 'Unknown'), severity_label, cluster)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'severity': severity_label,
            'cluster': cluster,
            'major_severity_probability': major_prob
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT 20').fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=9000, use_reloader=False)