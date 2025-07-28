from flask import Flask, request, jsonify, redirect
from models import db, ShortURL, ClickLog
from utils import generate_shortcode
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/shorturls", methods=["POST"])
def create_short_url():
    data = request.get_json()
    original_url = data.get("url")
    validity = data.get("validity", 60)  # default to 60 mins
    custom_shortcode = data.get("shortcode")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    expiry_time = datetime.utcnow() + timedelta(minutes=validity)

    if custom_shortcode:
        if ShortURL.query.filter_by(shortcode=custom_shortcode).first():
            return jsonify({"error": "Shortcode already in use"}), 400
        shortcode = custom_shortcode
    else:
        # Generate unique shortcode
        while True:
            shortcode = generate_shortcode()
            if not ShortURL.query.filter_by(shortcode=shortcode).first():
                break

    new_short = ShortURL(url=original_url, shortcode=shortcode, expiry=expiry_time)
    db.session.add(new_short)
    db.session.commit()

    return jsonify({
        "shortLink": f"https://hostname:port/{shortcode}",
        "expiry": expiry_time.isoformat() + "Z"
    }), 201

@app.route("/shorturls/<shortcode>", methods=["GET"])
def get_short_url_stats(shortcode):
    short = ShortURL.query.filter_by(shortcode=shortcode).first()
    if not short:
        return jsonify({"error": "Shortcode not found"}), 404

    clicks = ClickLog.query.filter_by(shorturl_id=short.id).all()
    click_data = [{
        "timestamp": click.timestamp.isoformat() + "Z",
        "referrer": click.referrer,
        "location": click.location
    } for click in clicks]

    return jsonify({
        "originalURL": short.url,
        "createdAt": short.created_at.isoformat() + "Z",
        "expiry": short.expiry.isoformat() + "Z",
        "clickCount": len(clicks),
        "clickData": click_data
    })

@app.route("/<shortcode>")
def redirect_to_url(shortcode):
    short = ShortURL.query.filter_by(shortcode=shortcode).first()
    if not short or short.expiry < datetime.utcnow():
        return jsonify({"error": "Shortlink expired or not found"}), 404

    referrer = request.headers.get("Referer", "unknown")
    # Just simulating location
    location = request.remote_addr or "unknown"

    log = ClickLog(shorturl_id=short.id, referrer=referrer, location=location)
    db.session.add(log)
    db.session.commit()

    return redirect(short.url)

if __name__ == '__main__':
    app.run(debug=True)