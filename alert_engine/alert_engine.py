"""
RightAlert BD - Multi-Channel Last-Mile Early Warning Engine
Track 2: Last-Mile Early Warning
Mapathon 2026 | RIMES & Save the Children
"""

import json
import datetime

# ─────────────────────────────────────────
# 1. HAZARD ALERT TEMPLATES (English → Simple Bangla)
# ─────────────────────────────────────────

ALERT_TEMPLATES = {
    "cyclone": {
        "level_3": "⚠️ সতর্কতা: ঘূর্ণিঝড় আসছে। আপনার নিকটতম আশ্রয়কেন্দ্রে যান।",
        "level_4": "🚨 বিপদ সংকেত ৪: ঘূর্ণিঝড় বিপজ্জনক। এখনই আশ্রয়কেন্দ্রে যান!",
        "level_7": "🆘 মহাবিপদ সংকেত: অবিলম্বে নিরাপদ স্থানে যান! জীবন বিপন্ন!",
        "level_10": "🆘 সর্বোচ্চ বিপদ সংকেত ১০: সকলকে তাৎক্ষণিকভাবে সরে যেতে হবে!"
    },
    "flood": {
        "low":    "⚠️ বন্যা সতর্কতা: নদীর পানি বাড়ছে। নিচু এলাকা ছেড়ে যান।",
        "medium": "🚨 বন্যা বিপদ: দ্রুত উঁচু জায়গায় যান এবং শিশুদের নিরাপদ রাখুন।",
        "high":   "🆘 মারাত্মক বন্যা: এখনই ঘর ছাড়ুন! সাহায্যের জন্য স্থানীয় স্বেচ্ছাসেবীকে ডাকুন।"
    },
    "landslide": {
        "watch":   "⚠️ ভূমিধস সতর্কতা: পাহাড়ের কাছে থাকবেন না।",
        "warning": "🚨 ভূমিধস বিপদ: পাহাড়ি এলাকা থেকে দূরে সরে যান।",
        "emergency": "🆘 ভূমিধস জরুরি অবস্থা: তাৎক্ষণিকভাবে সরে যান!"
    }
}

# ─────────────────────────────────────────
# 2. DISTRICT → UPAZILA VULNERABILITY MAP
#    (Sample data — expand with real GIS data)
# ─────────────────────────────────────────

VULNERABILITY_DATA = {
    "Cox's Bazar": {
        "risk_level": "high",
        "hazards": ["cyclone", "flood", "landslide"],
        "upazilas": ["Teknaf", "Ukhia", "Ramu", "Chakaria"],
        "connectivity": "poor",
        "volunteer_count": 12
    },
    "Khulna": {
        "risk_level": "high",
        "hazards": ["cyclone", "flood"],
        "upazilas": ["Dacope", "Koyra", "Paikgacha"],
        "connectivity": "moderate",
        "volunteer_count": 18
    },
    "Sylhet": {
        "risk_level": "medium",
        "hazards": ["flood", "landslide"],
        "upazilas": ["Companiganj", "Gowainghat", "Jaintapur"],
        "connectivity": "moderate",
        "volunteer_count": 9
    },
    "Sunamganj": {
        "risk_level": "high",
        "hazards": ["flood"],
        "upazilas": ["Tahirpur", "Jamalganj", "Bishwamvarpur"],
        "connectivity": "poor",
        "volunteer_count": 7
    }
}

# ─────────────────────────────────────────
# 3. CORE ALERT PROCESSING ENGINE
# ─────────────────────────────────────────

def generate_alert(hazard_type: str, severity: str, affected_districts: list) -> dict:
    """
    Takes a raw national agency alert and generates
    multi-channel, localized warning packages.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Get the Bangla message
    bangla_message = ALERT_TEMPLATES.get(hazard_type, {}).get(severity, "সতর্ক থাকুন।")
    
    alert_packages = []

    for district in affected_districts:
        district_info = VULNERABILITY_DATA.get(district, {})
        if not district_info:
            continue

        # Build multi-channel package per district
        package = {
            "district": district,
            "timestamp": timestamp,
            "hazard": hazard_type,
            "severity": severity,
            "risk_level": district_info.get("risk_level", "unknown"),
            "upazilas": district_info.get("upazilas", []),
            "channels": build_channels(
                district,
                bangla_message,
                district_info
            ),
            "volunteer_alert": build_volunteer_alert(district, district_info, bangla_message),
            "legal_accountability": {
                "issuing_authority": "Bangladesh Meteorological Department",
                "relay_obligation": "District Disaster Management Committee (DDMC)",
                "legal_basis": "Disaster Management Act 2012, Section 21",
                "sendai_target": "Target G - Universal Early Warning Coverage by 2030",
                "timestamp_logged": timestamp  # For accountability tracking
            }
        }
        alert_packages.append(package)

    return {
        "alert_id": f"RA-{timestamp.replace(' ', '-').replace(':', '')}",
        "status": "DISPATCHED",
        "total_districts": len(alert_packages),
        "packages": alert_packages
    }


def build_channels(district: str, message: str, info: dict) -> dict:
    """
    Selects appropriate channels based on connectivity.
    Poor connectivity → prioritize SMS + IVR over internet.
    """
    connectivity = info.get("connectivity", "moderate")
    
    channels = {
        "sms": {
            "active": True,  # Always on — no internet needed
            "message": message,
            "priority": 1,
            "recipients": "All registered community members"
        },
        "ivr_voice_call": {
            "active": True,  # Critical for elderly/illiterate populations
            "script": f"[IVR SCRIPT]: {message} — এই বার্তাটি পুনরায় শুনতে ১ চাপুন।",
            "priority": 2,
            "note": "Targets non-smartphone users"
        },
        "web_dashboard": {
            "active": connectivity in ["moderate", "good"],
            "url": f"/dashboard/alerts/{district.replace(' ', '-').lower()}",
            "priority": 3
        },
        "community_loudspeaker": {
            "active": connectivity == "poor",
            "relay_via": "Local volunteer network",
            "message": message,
            "priority": 1,
            "note": "Activated for poor-connectivity zones"
        }
    }
    return channels


def build_volunteer_alert(district: str, info: dict, message: str) -> dict:
    """
    Generates alert package for volunteer first-responders.
    """
    return {
        "volunteer_count": info.get("volunteer_count", 0),
        "status": "ALERTED",
        "task": f"Confirm receipt of warning in all upazilas: {', '.join(info.get('upazilas', []))}",
        "confirmation_required": True,
        "message_to_deliver": message,
        "fallback": "If no confirmation in 30 mins → escalate to DDMC"
    }


# ─────────────────────────────────────────
# 4. FEEDBACK LOOP — Confirmation Tracker
# ─────────────────────────────────────────

class ConfirmationTracker:
    """
    Tracks whether warnings were confirmed received
    at the last-mile level. This is the accountability layer.
    """
    def __init__(self):
        self.log = []

    def confirm(self, district: str, upazila: str, confirmed_by: str):
        entry = {
            "district": district,
            "upazila": upazila,
            "confirmed_by": confirmed_by,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "CONFIRMED ✅"
        }
        self.log.append(entry)
        print(f"  ✅ Confirmed: {upazila}, {district} — by {confirmed_by}")
        return entry

    def get_unconfirmed(self, expected_districts: list) -> list:
        confirmed = {e["district"] for e in self.log}
        return [d for d in expected_districts if d not in confirmed]

    def report(self):
        print("\n📋 CONFIRMATION REPORT")
        print("=" * 40)
        for entry in self.log:
            print(f"  {entry['status']} {entry['upazila']}, {entry['district']} | {entry['timestamp']}")
        print("=" * 40)


# ─────────────────────────────────────────
# 5. DEMO RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  RightAlert BD — Alert Engine v1.0")
    print("  Mapathon 2026 | RIMES & Save the Children")
    print("=" * 50)

    # Simulate a cyclone signal 7 hitting coastal districts
    print("\n🌀 INCOMING ALERT: Cyclone Signal 7 — Cox's Bazar, Khulna\n")

    alert = generate_alert(
        hazard_type="cyclone",
        severity="level_7",
        affected_districts=["Cox's Bazar", "Khulna"]
    )

    print(f"Alert ID     : {alert['alert_id']}")
    print(f"Status       : {alert['status']}")
    print(f"Districts    : {alert['total_districts']}")
    print()

    for pkg in alert["packages"]:
        print(f"📍 District  : {pkg['district']}")
        print(f"   Risk Level: {pkg['risk_level'].upper()}")
        print(f"   Upazilas  : {', '.join(pkg['upazilas'])}")
        print(f"   SMS Active : {pkg['channels']['sms']['active']}")
        print(f"   IVR Active : {pkg['channels']['ivr_voice_call']['active']}")
        print(f"   Volunteers : {pkg['volunteer_alert']['volunteer_count']} alerted")
        print(f"   Legal Basis: {pkg['legal_accountability']['legal_basis']}")
        print()

    # Simulate confirmation from volunteers
    print("─" * 50)
    print("📲 Volunteer Confirmations Coming In...\n")
    tracker = ConfirmationTracker()
    tracker.confirm("Cox's Bazar", "Teknaf", "Volunteer Rahim")
    tracker.confirm("Cox's Bazar", "Ukhia", "Volunteer Nasrin")
    tracker.confirm("Khulna", "Dacope", "Volunteer Karim")

    tracker.report()

    unconfirmed = tracker.get_unconfirmed(["Cox's Bazar", "Khulna", "Sylhet"])
    if unconfirmed:
        print(f"\n⚠️  ESCALATION NEEDED — No confirmation from: {', '.join(unconfirmed)}")

    print("\n✅ RightAlert BD Engine Demo Complete.")