from flask import Flask, redirect, request, jsonify
import os, requests, json, base64

app = Flask(__name__)

CLIENT_ID = os.environ.get("GARMIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GARMIN_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("GARMIN_REDIRECT_URI", "http://localhost:5000/callback")
TOKEN_URL = "https://connectapi.garmin.com/oauth2/token"
AUTH_URL = "https://connectapi.garmin.com/oauth2/authorize"
TOKENS_FILE = "garmin_tokens.json"
SCOPE = "activity:read"  # adjust as needed

@app.route("/")
def index():
    url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}"
    return redirect(url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400
    auth = (CLIENT_ID + ":" + CLIENT_SECRET).encode()
    b64 = base64.b64encode(auth).decode()
    headers = {"Authorization": f"Basic {b64}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    resp = requests.post(TOKEN_URL, headers=headers, data=data)
    if resp.status_code != 200:
        return jsonify({"status": "token_exchange_failed", "resp": resp.text}), 400
    tokens = resp.json()
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f)
    return jsonify({"status": "ok", "tokens_saved_to": TOKENS_FILE})

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        raise SystemExit("Set GARMIN_CLIENT_ID and GARMIN_CLIENT_SECRET environment variables")
    app.run(host="0.0.0.0", port=5000, debug=False)