import os, json, time, requests, base64
from datetime import datetime, timedelta

TOKENS_FILE = "garmin_tokens.json"
TOKEN_URL = "https://connectapi.garmin.com/oauth2/token"
API_BASE = "https://healthapi.garmin.com/wellness-api/rest"
N8N_WEBHOOK = os.environ.get("N8N_WEBHOOK_URL")
CLIENT_ID = os.environ.get("GARMIN_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GARMIN_CLIENT_SECRET")

def load_tokens():
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def save_tokens(t):
    with open(TOKENS_FILE, "w") as f:
        json.dump(t, f)

def refresh_tokens(tokens):
    if "refresh_token" not in tokens:
        raise SystemExit("No refresh_token available")
    auth = (CLIENT_ID + ":" + CLIENT_SECRET).encode()
    b64 = base64.b64encode(auth).decode()
    headers = {"Authorization": f"Basic {b64}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
    r = requests.post(TOKEN_URL, headers=headers, data=data)
    r.raise_for_status()
    new = r.json()
    # preserve original refresh token if provider didn't return new one
    if "refresh_token" not in new:
        new["refresh_token"] = tokens["refresh_token"]
    save_tokens(new)
    return new

def get_activities(access_token, start_date, end_date):
    url = f"{API_BASE}/activities?startDate={start_date}&endDate={end_date}"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def post_to_n8n(payload):
    if not N8N_WEBHOOK:
        raise SystemExit("Set N8N_WEBHOOK_URL env var")
    r = requests.post(N8N_WEBHOOK, json=payload)
    r.raise_for_status()
    return r.text

def main():
    tokens = load_tokens()
    # naive expiry check: if expires_in present and token older than that, refresh.
    if "expires_in" in tokens and "issued_at" in tokens:
        issued = tokens.get("issued_at", 0)
        if time.time() - issued > tokens["expires_in"] - 30:
            tokens = refresh_tokens(tokens)
    else:
        # try refresh if access token fails later
        pass

    access_token = tokens["access_token"]
    # example: last 7 days
    end = datetime.utcnow().date()
    start = end - timedelta(days=7)
    activities = get_activities(access_token, start.isoformat(), end.isoformat())

    # send to n8n
    res = post_to_n8n({"activities": activities})
    print("n8n response:", res)

if __name__ == "__main__":
    # stamp issued_at to tokens file when first saved
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r+") as f:
            t = json.load(f)
            if "issued_at" not in t:
                t["issued_at"] = int(time.time())
                f.seek(0); f.truncate(); json.dump(t, f)
    main()