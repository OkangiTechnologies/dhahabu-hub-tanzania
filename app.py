import os
import time

from flask import Flask, render_template, jsonify
from flask_wtf.csrf import CSRFProtect
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone

app = Flask(__name__)
secret_key = os.environ.get("SECRET_KEY")
if not secret_key and os.environ.get("PRODUCTION") == "1":
    raise RuntimeError("SECRET_KEY must be set when PRODUCTION=1")
app.config["SECRET_KEY"] = secret_key or "local-development-key"
CSRFProtect(app)

OFFICIAL_URL = "https://www.tumemadini.go.tz/"
FALLBACK = {
    "date": "23 Sep 2026",
    "world_usd_oz": 4358.30,
    "world_tzs_g": 372507.24,
    "market_tzs_g": 335256.52,
    "buying_tzs_g": 327806.37,
    "source": OFFICIAL_URL,
    "live": False
}

PRICE_CACHE_SECONDS = 600
price_cache = {"data": None, "expires_at": 0}

def parse_price(text):
    # Accept numbers such as 4,358.30 or 372,507.24
    return float(text.replace(",", "").strip())

def fetch_gold_price():
    if price_cache["data"] and time.time() < price_cache["expires_at"]:
        return dict(price_cache["data"])
    try:
        r = requests.get(OFFICIAL_URL, timeout=12, headers={
            "User-Agent": "Tanzania Gold Miner Hub/1.0"
        })
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = " ".join(soup.stripped_strings)

        # The official page currently presents the four gold values in this order.
        m = re.search(
            r"Gold Indicative Prices.*?World Market Price \(USD/toz\).*?"
            r"([0-9,]+\.[0-9]+).*?"
            r"World Market Price \(TZS/g\).*?([0-9,]+\.[0-9]+).*?"
            r"Mineral Market Price \(TZS/g\).*?([0-9,]+\.[0-9]+).*?"
            r"Buying Centre Price \(TZS/g\).*?([0-9,]+\.[0-9]+)",
            text,
            flags=re.I | re.S
        )
        if not m:
            raise ValueError("Official price table format could not be parsed.")

        # Find the date near the first gold table.
        dm = re.search(r"MINERAL INDICATIVE PRICES\s+([A-Za-z]+\.\s*\d{1,2},\s*\d{4})", text)
        date_text = dm.group(1) if dm else datetime.now().strftime("%d %b %Y")

        data = {
            "date": date_text,
            "world_usd_oz": parse_price(m.group(1)),
            "world_tzs_g": parse_price(m.group(2)),
            "market_tzs_g": parse_price(m.group(3)),
            "buying_tzs_g": parse_price(m.group(4)),
            "source": OFFICIAL_URL,
            "live": True,
            "fetched_at": datetime.now(timezone.utc).isoformat()
        }
        price_cache["data"] = data
        price_cache["expires_at"] = time.time() + PRICE_CACHE_SECONDS
        return dict(data)
    except Exception as exc:
        data = dict(FALLBACK)
        data["error"] = str(exc)
        data["fetched_at"] = datetime.now(timezone.utc).isoformat()
        return data

@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

LANDING_PAGES = {
    "licensing": {
        "kicker": "LICENSING",
        "title": "Choose the licence that matches your activity.",
        "intro": "Start with the right mineral or trading permission, then confirm the current procedure directly with the Mining Commission.",
        "cards": [
            ("Primary Mining Licence", "For small-scale mining operations. Confirm the area, mineral, eligibility, fees and current application process.", "https://www.tumemadini.go.tz/pages/licenseservice/"),
            ("Broker Licence", "Allows an authorized broker to buy minerals from specified buying stations and sell to a licensed dealer. It does not authorize export.", "https://www.tumemadini.go.tz/pages/licenseservice/"),
            ("Dealer Licence", "Supports mineral trading and export subject to current requirements, permits and supporting documents.", "https://www.tumemadini.go.tz/pages/licenseservice/")
        ],
        "steps": ["Identify your activity", "Confirm the area and mineral", "Prepare the current application", "Operate within the licence"]
    },
    "trade": {
        "kicker": "BUYING, SELLING & EXPORT",
        "title": "Trade gold through the legal system.",
        "intro": "Use authorized markets and buying centres, keep transaction records, and confirm current charges before completing a sale or export.",
        "cards": [
            ("Before you sell", "Confirm the buyer is authorized, use an approved market or buying centre, request valuation documentation and keep your records.", "https://www.tumemadini.go.tz/statistics/list-of-mineral-markets/"),
            ("Export essentials", "The correct mineral or dealer authorization, an export permit and proof of applicable royalty and inspection payments may be required.", "https://www.tumemadini.go.tz/pages/procedures-for-exportation-of-minerals/"),
            ("Protect your transaction", "Confirm purity, weight, valuation, royalty, inspection and clearance charges. Avoid informal routes promising an unusually high price.", "https://www.tumemadini.go.tz/")
        ],
        "steps": ["Verify the buyer", "Confirm valuation and purity", "Keep transaction documents", "Confirm export requirements"]
    },
    "processing": {
        "kicker": "PROCESSING PLANTS",
        "title": "Evaluate a processing plant with evidence.",
        "intro": "A professional plant decision starts with ore testing, authorization, recovery evidence, worker safety and environmental controls.",
        "cards": [
            ("Know your ore", "Use representative sampling and testing to understand grade, mineralogy and how the ore responds to processing.", "https://www.tumemadini.go.tz/"),
            ("Check authorization", "Confirm the plant and operator hold the permissions required for the activity and location.", "https://www.tumemadini.go.tz/pages/licenseservice/"),
            ("Verify recovery and safety", "Ask for measured recovery, operating costs, containment, tailings control, PPE, ventilation and emergency procedures.", "https://www.tumemadini.go.tz/publications/regulations/")
        ],
        "steps": ["Test representative ore", "Verify legal authorization", "Inspect containment and safety", "Compare measured recovery and cost"]
    },
    "markets": {
        "kicker": "MARKETS & BUYING CENTRES",
        "title": "Find the right place to trade.",
        "intro": "Use the official Mining Commission lists for current names, locations and contacts before travelling.",
        "cards": [
            ("Mineral markets", "Examples include Mbeya, Songwe, Tabora and Kigoma. Check the current official market list before making travel plans.", "https://www.tumemadini.go.tz/statistics/list-of-mineral-markets/"),
            ("Buying centres", "Buying centres operate under applicable authorization. Confirm the current location and buyer details before selling.", "https://www.tumemadini.go.tz/statistics/list-of-buying-centers/"),
            ("Travel prepared", "Carry the required documents, confirm operating hours and keep a record of the transaction and valuation.", "https://www.tumemadini.go.tz/")
        ],
        "steps": ["Choose the market or centre", "Confirm current location", "Bring required documents", "Keep transaction records"]
    },
    "sources": {
        "kicker": "OFFICIAL SOURCES",
        "title": "Verify important decisions with primary sources.",
        "intro": "Dhahabu Yetu provides a practical starting point. Use these Mining Commission pages for current rules, prices, licences and procedures.",
        "cards": [
            ("Mining Commission", "Official website and current public information.", "https://www.tumemadini.go.tz/"),
            ("Gold price history", "Previous indicative gold prices and reference data.", "https://www.tumemadini.go.tz/pages/view-previous-prices/"),
            ("Licence services", "Licence types and descriptions.", "https://www.tumemadini.go.tz/pages/licenseservice/"),
            ("Application procedures", "Current licence application guidance.", "https://www.tumemadini.go.tz/pages/applicationprocedure/"),
            ("Export procedures", "Export rights, permits and listed fees.", "https://www.tumemadini.go.tz/pages/procedures-for-exportation-of-minerals/"),
            ("Mining regulations", "Licensing, environmental and mineral-trade regulations.", "https://www.tumemadini.go.tz/publications/regulations/")
        ],
        "steps": []
    }
}

@app.route("/<page>", methods=["GET"])
def landing_page(page):
    if page == "privacy":
        return privacy()
    if page == "terms":
        return terms()
    if page not in LANDING_PAGES:
        return not_found(None)
    image = {"trade": "gold-sample-scale.jpeg", "markets": "geita-gold-market.jpeg"}.get(page, "mining-worker.jpeg")
    return render_template("landing.html", page=LANDING_PAGES[page], image=image)

@app.route("/privacy", methods=["GET"])
def privacy():
    return render_template("privacy.html")

@app.route("/terms", methods=["GET"])
def terms():
    return render_template("terms.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("auth.html", mode="login")

@app.route("/register", methods=["GET"])
def register():
    return render_template("auth.html", mode="register")

@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="The page you requested was not found."), 404

@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500

@app.route("/api/gold-price", methods=["GET"])
def gold_price():
    return jsonify(fetch_gold_price())

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
