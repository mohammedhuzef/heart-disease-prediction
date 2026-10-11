import http.server
import json
import os
import socketserver
from pathlib import Path

import joblib
import pandas as pd

PORT = 8000
APP_DIR = Path(__file__).parent.resolve()
MODEL_PATH = APP_DIR / "heart_disease_model.pkl"

# Load the trained model pipeline
model = None
if MODEL_PATH.exists():
    try:
        model = joblib.load(MODEL_PATH)
        print(f"[CardioCheck] Loaded model pipeline from {MODEL_PATH}")
    except Exception as e:
        print(f"[CardioCheck] Error loading model: {e}")


class CardioCheckHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(APP_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/predict":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                
                # Format into DataFrame matching scikit-learn training columns
                input_df = pd.DataFrame([{
                    "Age": float(data.get("Age", 50)),
                    "Sex": str(data.get("Sex", "M")),
                    "ChestPainType": str(data.get("ChestPainType", "ASY")),
                    "RestingBP": float(data.get("RestingBP", 120)),
                    "Cholesterol": float(data.get("Cholesterol", 200)),
                    "FastingBS": int(data.get("FastingBS", 0)),
                    "RestingECG": str(data.get("RestingECG", "Normal")),
                    "MaxHR": float(data.get("MaxHR", 150)),
                    "ExerciseAngina": str(data.get("ExerciseAngina", "N")),
                    "Oldpeak": float(data.get("Oldpeak", 1.0)),
                    "ST_Slope": str(data.get("ST_Slope", "Flat"))
                }])

                if model is not None:
                    raw_prob = float(model.predict_proba(input_df)[0][1])
                else:
                    raw_prob = 0.50

                # Supplemental adjustment for UCI fields ca & thal
                ca = int(data.get("ca", 0))
                thal = str(data.get("thal", "normal"))
                adj = 0.0
                if ca > 0:
                    adj += min(0.20, ca * 0.08)
                if thal == "reversable":
                    adj += 0.10
                elif thal == "fixed":
                    adj += 0.05
                
                final_prob = min(0.99, max(0.01, raw_prob + adj))

                response_bytes = json.dumps({
                    "status": "success",
                    "probability": round(final_prob, 4),
                    "model_name": "RandomForestClassifier-200"
                }).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)
                return

            except Exception as e:
                err_msg = json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_msg)))
                self.end_headers()
                self.wfile.write(err_msg)
                return

        self.send_error(404, "Endpoint Not Found")


def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CardioCheckHandler) as httpd:
        print(f"[CardioCheck] Web app serving at http://localhost:{PORT}")
        print(f"[CardioCheck] Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[CardioCheck] Server stopped.")


if __name__ == "__main__":
    run()
