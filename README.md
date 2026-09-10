# DCF and Trading Comps Valuation

3-statement DCF + trading comps model for a listed Indian financial institution (FinBank Ltd - synthetic), deriving intrinsic value and investment view.

## What it does
- Projects **P&L, Cash Flow Statement, Balance Sheet** for 5 years
- Discounts FCF + terminal value to get **Enterprise Value -> Equity Value -> intrinsic per share**
- Loads `comps.csv` with peers and computes **trading comps valuation** (PE, EV/EBITDA, P/B medians)
- Blends DCF + Comps, emits **BUY / HOLD / SELL** view
- Prints **WACC vs terminal-growth sensitivity** grid

## Run
```bash
pip install -r requirements.txt
python model.py
```

## Files
- `model.py` - main script, all logic
- `comps.csv` - target + 5 peers with market cap, revenue, multiples, ROE

## Note
Synthetic illustrative numbers only. Not investment advice.