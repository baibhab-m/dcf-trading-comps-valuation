"""
DCF and Trading Comps Valuation — FinBank Ltd (synthetic)
Illustrative 3-statement DCF + trading comps for a listed Indian financial.
All numbers are synthetic and for demonstration only — labeled as illustrative.
"""
import pandas as pd

# Synthetic base financials (FY24)
revenue = 1200  # INR Cr
ebitda_margin = 0.32
ebit = revenue * ebitda_margin
tax_rate = 0.25
nopat = ebit * (1 - tax_rate)
wc_change = -15
capex = 80
fcf = nopat + 30 - wc_change - capex  # 30 = D&A synthetic

print(f"Base FCF (FY24): {fcf:.1f} Cr")

# Forecast 5 years: revenue growth, margin
growth = [0.14, 0.13, 0.11, 0.09, 0.07]
ebitda_m = [0.33, 0.335, 0.34, 0.34, 0.335]
fcf_forecast = []
rev = revenue
for g, m in zip(growth, ebitda_m):
    rev *= (1+g)
    ebit = rev * m
    nopat = ebit * (1-tax_rate)
    fcf_forecast.append(nopat + 35 - 18 - 85)  # D&A, wc, capex synthetic

print("FCF forecast:", [f"{x:.1f}" for x in fcf_forecast])

# WACC and terminal
wacc = 0.11
terminal_growth = 0.04
terminal_value = fcf_forecast[-1] * (1+terminal_growth) / (wacc - terminal_growth)
print(f"Terminal value: {terminal_value:.1f} Cr")

# Discount
import math
pv = sum(fcf / ((1+wacc)**(i+1)) for i,fcf in enumerate(fcf_forecast))
pv_terminal = terminal_value / ((1+wacc)**5)
enterprise_value = pv + pv_terminal
net_debt = 180
equity_value = enterprise_value - net_debt
shares = 12.5  # Cr shares
intrinsic = equity_value / shares
print(f"Enterprise value: {enterprise_value:.1f} Cr | Equity: {equity_value:.1f} Cr | Intrinsic per share: {intrinsic:.0f} INR")
print(f"Assumed market price: 2850 | View: {'Buy' if intrinsic>2850*1.15 else 'Hold' if intrinsic>2850 else 'Sell'}")

# Sensitivity table
print("\nSensitivity (WACC vs Terminal Growth) — Equity per share:")
for w in [0.10, 0.11, 0.12]:
    row=[]
    for g in [0.03,0.04,0.05]:
        tv = fcf_forecast[-1]*(1+g)/(w-g)
        ev = sum(fcf/((1+w)**(i+1)) for i,fcf in enumerate(fcf_forecast)) + tv/((1+w)**5)
        eq = ev - net_debt
        row.append(f"{eq/shares:.0f}")
    print(f"WACC {w:.0%}:", " | ".join(row))
