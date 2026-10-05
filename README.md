# Dhahabu Hub Tanzania

A practical, mobile-first web resource for small-scale gold miners in Tanzania.

## Features
- Mining Commission gold-price feed through a server-side endpoint
- Official licence guidance: PML, broker and dealer licences
- Buying, selling and export guidance
- Non-hazardous plant-selection checklist for vat leaching and elution
- Mineral market/buying-centre overview
- Official source links
- Simple gross-value calculator
- Responsive desktop/mobile layout

## Run locally

1. Install Python 3.12 or newer.
2. Open PowerShell in this folder.
3. Create a virtual environment:

   `python -m venv venv`

4. Activate it:

   `.\venv\Scripts\Activate.ps1`

5. Install dependencies:

   `python -m pip install -r requirements.txt`

6. Start the site:

   `python app.py`

7. Open:

   `http://127.0.0.1:5000`

## Price feed
`/api/gold-price` fetches the Mining Commission website server-side and attempts to parse the current gold indicative-price table. A verified fallback is included so the dashboard remains usable if the Commission site is temporarily unavailable.

For production deployment, replace scraping with an official API/data endpoint if the Commission provides one. Add caching, monitoring and source-change alerts.

## Important
This is an information portal, not legal or engineering advice. Licensing, fees, export rules and plant requirements can change. Confirm current requirements with the Mining Commission before acting.

## Official sources
- https://www.tumemadini.go.tz/
- https://www.tumemadini.go.tz/pages/view-previous-prices/
- https://www.tumemadini.go.tz/pages/licenseservice/
- https://www.tumemadini.go.tz/pages/applicationprocedure/
- https://www.tumemadini.go.tz/pages/procedures-for-exportation-of-minerals/
- https://www.tumemadini.go.tz/publications/regulations/
- https://www.tumemadini.go.tz/statistics/list-of-mineral-markets/
- https://www.tumemadini.go.tz/statistics/list-of-buying-centers/
