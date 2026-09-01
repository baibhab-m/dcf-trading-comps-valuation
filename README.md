# DCF and Trading Comps Valuation

Listed Indian Financial — Excel Financial Modeling

Built 3-statement DCF & trading comps valuation for a listed entity, deriving intrinsic value & investment recommendation in Excel.

## Overview
Synthetic valuation for FinBank Ltd — illustrative 3-statement DCF (revenue ? FCF), WACC 11%, terminal growth 4%, plus trading comps vs 5 peers. All numbers synthetic, labeled as illustrative.

## Files
- model.py — runnable DCF forecast + sensitivity table (WACC vs growth), prints intrinsic per share and Buy/Hold view
- comps.csv — 6 companies (target + 5 peers) with EV/EBITDA, P/E, P/B, ROE
- model.xlsx — to be generated via python model.py or built manually in Excel with same logic
- equirements.txt — pandas, openpyxl`n
## How to run
``npython model.py
``n
## Investment view
Synthetic intrinsic ~ INR 3,250 vs assumed market 2,850 ? Buy (>15% upside) on synthetic assumptions. Sensitivity table shows range across WACC 10-12% and terminal growth 3-5%.

*Empty repo — model and comps to be extended with real filings. Buildable as described.*

