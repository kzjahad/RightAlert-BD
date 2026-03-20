"""
RightAlert BD — Web Dashboard Backend
Flask server connecting alert engine to the visual dashboard
"""

from flask import Flask, render_template, jsonify, request
import datetime
import sys
import os

# Import our alert engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'alert_engine'))
from alert_engine import generate_alert, ConfirmationTracker, VULNERABILITY_DATA

app = Flask(__name__)

# Global tracker (in production this would be a database)
tracker = ConfirmationTracker()
active_alerts = []

# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/districts', methods=['GET'])
def get_districts():
    """Returns all district vulnerability data for the map."""
    districts = []
    for name, info in VULNERABILITY_DATA.items():
        districts.append({
            "name": name,
            "risk_level": info["risk_level"],
            "hazards": info["hazards"],
            "upazilas": info["upazilas"],
            "connectivity": info["connectivity"],
            "volunteer_count": info["volunteer_count"]
        })
    return jsonify(districts)


@app.route('/api/send-alert', methods=['POST'])
def send_alert():
    """Receives alert form input and runs the engine."""
    data = request.json
    hazard = data.get('hazard', 'cyclone')
    severity = data.get('severity', 'level_4')
    districts = data.get('districts', [])

    if not districts:
        return jsonify({"error": "No districts selected"}), 400

    result = generate_alert(hazard, severity, districts)
    active_alerts.append(result)

    return jsonify(result)


@app.route('/api/confirm', methods=['POST'])
def confirm_receipt():
    """Volunteer confirms they received and relayed the warning."""
    data = request.json
    entry = tracker.confirm(
        district=data.get('district'),
        upazila=data.get('upazila'),
        confirmed_by=data.get('confirmed_by', 'Volunteer')
    )
    return jsonify(entry)


@app.route('/api/confirmations', methods=['GET'])
def get_confirmations():
    return jsonify(tracker.log)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Dashboard summary stats."""
    return jsonify({
        "total_alerts_sent": len(active_alerts),
        "confirmations_received": len(tracker.log),
        "districts_covered": len(VULNERABILITY_DATA),
        "total_volunteers": sum(v["volunteer_count"] for v in VULNERABILITY_DATA.values()),
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)