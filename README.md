# GREEN · Second Life

A campus marketplace prototype for books, calculators and cycles. All historical data is synthetic and no real users or phone numbers are included.

## Run
Requires Python 3.9+ and no dependencies: `python server.py` (Windows: `py server.py`). Open http://localhost:8000. Listings persist in `data/market.db`; delete it to reset the demo. The synthetic data file is `data/past_listings.csv`.

## Demo
Enter Scientific calculator, Calculators, Good, age 2, original price ₹1,200. Click **See my fair price**, explain it, publish and search or filter for it. Swap is a listing preference, not a negotiation workflow.

## How pricing works
The API selects up to 12 synthetic historical sales of the same category and condition with the closest age. It multiplies the median of their sold/original price ratios by the new item's original price. The range is ±10%, a heuristic, not a confidence interval. The generator uses assumed category, age, and condition effects: these are not evidence of real-world prices. Brand, model, demand and inflation are not modeled; the displayed age span helps show weak matches.

## API contract
- `POST /api/estimate`: JSON `{ "item":"Scientific calculator", "category":"Calculators", "condition":"Good", "age":2, "original":1200, "trade":"Sell" }` returns the suggested price, range, median retention percentage, count, age span and method.
- `POST /api/listings`: same input, returns estimation plus stored listing ID.
- `GET /api/listings?q=calculator&category=Calculators&condition=Good&max_price=1000`: all filters optional.
- `GET /api/insights`: category and condition averages. Run `python insights.py` for condition and age breakdown.

Run tests: `python -m unittest discover -s tests -v`.

## Research
[OLX India](https://www.olx.in/blog/expert-advice/how-to-determine-the-right-price-of-second-hand-items/) discusses comparing second-hand items and considering their age and condition. Our dataset is not from OLX. [US EPA](https://www.epa.gov/electronics-batteries-management/electronics-basic-information-research-and-initiatives) describes how electronics reuse extends product life and reduces raw-material demand; no numerical environmental impact is claimed here.

## Scope and time
First 15 minutes: agree API contract. Next 30: verify pricing and UI. Next 25: add fictional demo listings and practice. Next 20: test gate scenario and filters. Final 10: present. No auth, payments, chat, photos or verified pricing are implemented.
