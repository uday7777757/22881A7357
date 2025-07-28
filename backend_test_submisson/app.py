from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
from utils import generate_shortcode
from logger import log_request

app = Flask(__name__)
app.after_request(log_request)

# In-memory store
urls = {}  # shortcode -> {url, expiry, created_at, clicks, click_logs}

@app.route("/shorturls", methods=["POST"])
def create_short_url():
    data = request.get_json()
    original_url = data.get("url")
    validity = data.get("validity", 60)
    custom_shortcode = data.get("shortcode")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    expiry_time = datetime.utcnow() + timedelta(minutes=validity)

    shortcode = custom_shortcode or generate_shortcode()
    if shortcode in urls:
        return jsonify({"error": "Shortcode already exists"}), 400

    urls[shortcode] = {
        "url": original_url,
        "created_at": datetime.utcnow(),
        "expiry": expiry_time,
        "clicks": 0,
        "click_logs": []
    }

    return jsonify({
        "shortLink": f"https://hostname:port/{shortcode}",
        "expiry": expiry_time.isoformat() + "Z"
    }), 201

@app.route("/shorturls/<shortcode>", methods=["GET"])
def get_stats(shortcode):
    if shortcode not in urls:
        return jsonify({"error": "Shortcode not found"}), 404

    data = urls[shortcode]
    return jsonify({
        "originalURL": data["url"],
        "createdAt": data["created_at"].isoformat() + "Z",
        "expiry": data["expiry"].isoformat() + "Z",
        "clickCount": data["clicks"],
        "clickData": data["click_logs"]
    })

@app.route("/<shortcode>", methods=["GET"])
def redirect_short_url(shortcode):
    if shortcode not in urls:
        return jsonify({"error": "Shortcode not found"}), 404

    data = urls[shortcode]
    if data["expiry"] < datetime.utcnow():
        return jsonify({"error": "Link expired"}), 410

    # Log click
    click_info = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "referrer": request.headers.get("Referer", "unknown"),
        "location": request.remote_addr or "unknown"
    }
    data["click_logs"].append(click_info)
    data["clicks"] += 1

    return redirect(data["url"])

if __name__ == "__main__":
    app.run(debug=True)