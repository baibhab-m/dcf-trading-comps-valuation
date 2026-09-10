"""
DCF and Trading Comps Valuation - FinBank Ltd (synthetic)
3-statement DCF + trading comps for a listed Indian financial.
All numbers synthetic and illustrative. Not investment advice.

Pipeline:
  1. Build 3-statement projection (P&L, BS, CFS) for 5 years
  2. Compute FCF, discount to enterprise value, bridge to equity
  3. Compute trading comps valuation from peers in comps.csv
  4. Blend and emit Buy/Hold/Sell view + sensitivity grid
"""

import csv
import math

# ---------- Hard-coded base financials (FY24, INR Cr) ----------
BASE_REVENUE = 12000.0  # FinBank is large-cap; rev in INR Cr
BASE_EBITDA_MARGIN = 0.32
BASE_DA = 300.0
TAX_RATE = 0.25
NET_DEBT = 1800.0
SHARES_CR = 12.5
MARKET_PRICE = 2850.0

# 5-year forecast: revenue growth, EBITDA margin, capex, delta working capital
GROWTH = [0.14, 0.13, 0.11, 0.09, 0.07]
EBITDA_MARGIN = [0.33, 0.335, 0.34, 0.34, 0.335]
CAPEX_PCT_REV = [0.07, 0.07, 0.07, 0.07, 0.07]  # capex as % revenue
DELTA_WC_PCT_REV = [-0.015, -0.015, -0.015, -0.015, -0.015]  # working capital change

WACC = 0.11
TERMINAL_GROWTH = 0.04


# ---------- 3-statement projection ----------
def project_pnl():
    """P&L: Revenue -> EBITDA -> D&A -> EBIT -> Tax -> Net Income."""
    pnl = []
    rev = BASE_REVENUE
    for g, m in zip(GROWTH, EBITDA_MARGIN):
        rev = rev * (1 + g)
        ebitda = rev * m
        ebit = ebitda - BASE_DA
        tax = ebit * TAX_RATE
        net_income = ebit - tax
        pnl.append({"revenue": rev, "ebitda": ebitda, "ebit": ebit, "tax": tax, "net_income": net_income})
    return pnl


def project_cfs(pnl):
    """Cash Flow Statement: NI + D&A - delta WC - capex = FCF."""
    fcf_list = []
    rev = BASE_REVENUE
    for i, (g, capex_pct, wc_pct, row) in enumerate(zip(GROWTH, CAPEX_PCT_REV, DELTA_WC_PCT_REV, pnl)):
        rev = rev * (1 + g)
        fcf = row["net_income"] + BASE_DA + (rev * wc_pct) - (rev * capex_pct)
        fcf_list.append({"fcf": fcf, "capex": rev * capex_pct, "delta_wc": rev * wc_pct, "da": BASE_DA})
    return fcf_list


def project_bs(pnl):
    """Simplified Balance Sheet: equity grows by retained earnings, debt held flat."""
    bs = []
    equity = 19000.0  # synthetic starting equity
    debt = NET_DEBT
    for row in pnl:
        equity += row["net_income"]  # all earnings retained
        bs.append({"equity": equity, "debt": debt, "total_assets": equity + debt + 200})
    return bs


# ---------- DCF valuation ----------
def discount(cashflows, rate):
    return sum(cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cashflows))


def dcf_value(fcf_list):
    pv_fcf = discount([r["fcf"] for r in fcf_list], WACC)
    terminal_fcf = fcf_list[-1]["fcf"]
    tv = terminal_fcf * (1 + TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    pv_tv = tv / ((1 + WACC) ** len(fcf_list))
    ev = pv_fcf + pv_tv
    equity = ev - NET_DEBT
    intrinsic = equity / SHARES_CR
    return {"ev": ev, "equity": equity, "intrinsic_per_share": intrinsic, "pv_fcf": pv_fcf, "pv_terminal": pv_tv}


def view(intrinsic, market):
    upside = intrinsic / market - 1
    if upside > 0.15:
        return f"BUY (upside {upside:.0%})"
    if upside > -0.05:
        return f"HOLD (upside {upside:.0%})"
    return f"SELL (downside {upside:.0%})"


def sensitivity_table(fcf_list):
    print("\n  Sensitivity - intrinsic per share (INR):")
    print("  " + "WACC \\ g".ljust(12) + " ".join(f"{g:>8.0%}" for g in [0.03, 0.04, 0.05]))
    for w in [0.10, 0.11, 0.12]:
        row = [f"WACC {w:.0%}".ljust(12)]
        for g in [0.03, 0.04, 0.05]:
            tv = fcf_list[-1]["fcf"] * (1 + g) / (w - g)
            ev = discount([r["fcf"] for r in fcf_list], w) + tv / ((1 + w) ** len(fcf_list))
            row.append(f"{((ev - NET_DEBT) / SHARES_CR):>8.0f}")
        print("  " + " ".join(row))


# ---------- Trading comps valuation ----------
def load_comps(path="comps.csv"):
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            rows.append({k: float(v) if k != "Company" else v for k, v in row.items()})
    return rows


def comps_valuation(comps):
    """Implied valuation from peer median multiples."""
    target = comps[0]
    peers = comps[1:]
    pe_med = sorted([p["PE"] for p in peers])[len(peers) // 2]
    ev_ebitda_med = sorted([p["EV_EBITDA"] for p in peers])[len(peers) // 2]
    pb_med = sorted([p["Price_Book"] for p in peers])[len(peers) // 2]

    # use target's own earnings/book to back out implied price
    target_eps = target["MarketCap_Cr"] / SHARES_CR / target["PE"]
    target_book = target["MarketCap_Cr"] / SHARES_CR / target["Price_Book"]
    target_ebitda = target["Revenue_Cr"] * BASE_EBITDA_MARGIN

    pe_price = pe_med * target_eps
    pb_price = pb_med * target_book
    ev_implied = ev_ebitda_med * target_ebitda
    eq_implied = ev_implied - NET_DEBT
    ev_ebitda_price = eq_implied / SHARES_CR

    avg_price = (pe_price + pb_price + ev_ebitda_price) / 3
    return {
        "pe_implied": pe_price,
        "pb_implied": pb_price,
        "ev_ebitda_implied": ev_ebitda_price,
        "blended": avg_price,
        "peer_medians": {"PE": pe_med, "EV_EBITDA": ev_ebitda_med, "Price_Book": pb_med},
    }


# ---------- Main ----------
if __name__ == "__main__":
    print("=" * 64)
    print("FinBank Ltd - 3-statement DCF + Trading Comps (synthetic)")
    print("=" * 64)

    pnl = project_pnl()
    cfs = project_cfs(pnl)
    bs = project_bs(pnl)

    print("\nP&L projection (INR Cr):")
    for i, row in enumerate(pnl, 1):
        print(f"  FY{24 + i}: Rev={row['revenue']:.0f}  EBITDA={row['ebitda']:.0f}  EBIT={row['ebit']:.0f}  NI={row['net_income']:.0f}")

    print("\nCash Flow (FCF, INR Cr):")
    for i, row in enumerate(cfs, 1):
        print(f"  FY{24 + i}: FCF={row['fcf']:.0f}  (NI {row['fcf'] - row['da'] - row['delta_wc'] + row['capex']:.0f} + D&A {row['da']:.0f} + dWC {row['delta_wc']:.0f} - Capex {row['capex']:.0f})")

    print("\nBalance Sheet (INR Cr):")
    for i, row in enumerate(bs, 1):
        print(f"  FY{24 + i}: Equity={row['equity']:.0f}  Debt={row['debt']:.0f}  Assets={row['total_assets']:.0f}")

    print("\n" + "-" * 64)
    print("DCF Valuation")
    print("-" * 64)
    dcf = dcf_value(cfs)
    print(f"  PV of FCF (5y): {dcf['pv_fcf']:.0f}")
    print(f"  PV of Terminal: {dcf['pv_terminal']:.0f}")
    print(f"  Enterprise Value: {dcf['ev']:.0f}")
    print(f"  - Net Debt: {NET_DEBT:.0f}")
    print(f"  = Equity Value: {dcf['equity']:.0f}")
    print(f"  / Shares: {SHARES_CR} Cr")
    print(f"  Intrinsic per share: INR {dcf['intrinsic_per_share']:.0f}")
    print(f"  Market price: INR {MARKET_PRICE}")
    print(f"  View: {view(dcf['intrinsic_per_share'], MARKET_PRICE)}")
    sensitivity_table(cfs)

    print("\n" + "-" * 64)
    print("Trading Comps Valuation (peer median multiples)")
    print("-" * 64)
    comps = load_comps("comps.csv")
    cv = comps_valuation(comps)
    print(f"  Peer median PE: {cv['peer_medians']['PE']:.1f}x  -> implied price: INR {cv['pe_implied']:.0f}")
    print(f"  Peer median EV/EBITDA: {cv['peer_medians']['EV_EBITDA']:.1f}x  -> implied price: INR {cv['ev_ebitda_implied']:.0f}")
    print(f"  Peer median P/B: {cv['peer_medians']['Price_Book']:.1f}x  -> implied price: INR {cv['pb_implied']:.0f}")
    print(f"  Blended comps price: INR {cv['blended']:.0f}")
    print(f"  View: {view(cv['blended'], MARKET_PRICE)}")

    final = (dcf["intrinsic_per_share"] + cv["blended"]) / 2
    print("\n" + "=" * 64)
    print(f"DCF: INR {dcf['intrinsic_per_share']:.0f}  |  Comps: INR {cv['blended']:.0f}  |  Blended: INR {final:.0f}")
    print(f"Final view: {view(final, MARKET_PRICE)}")
    print("=" * 64)