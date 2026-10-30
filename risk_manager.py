from math import floor
from datetime import datetime

CAPITAL = 10000
RISK_PERCENT = 0.005
DAILY_MAX_LOSS = 100
DEFAULT_RR = 2

print("\n=== INDIAN INTRADAY RISK MANAGER ===")
print("Capital: ₹10,000 | Risk per trade: ₹50")
print("Daily loss limit: ₹100 | Target RR: 1:2\n")

exchange = input("Exchange (NSE/BSE): ").strip().upper()
if exchange not in ("NSE", "BSE"):
    print("Invalid exchange.")
    raise SystemExit

symbol = input("Stock symbol: ").strip().upper()
side = input("Trade side (BUY/SELL): ").strip().upper()

try:
    entry = float(input("Entry price (₹): "))
    stop = float(input("Stop-loss price (₹): "))
    rr = float(input("Reward:Risk (default 2): ") or DEFAULT_RR)
except ValueError:
    print("Please enter valid numbers.")
    raise SystemExit

if not symbol or entry <= 0 or stop <= 0 or rr <= 0:
    print("Invalid input.")
    raise SystemExit

if side == "BUY" and stop >= entry:
    print("BLOCK: BUY stop-loss must be below entry.")
    raise SystemExit
if side == "SELL" and stop <= entry:
    print("BLOCK: SELL stop-loss must be above entry.")
    raise SystemExit
if side not in ("BUY", "SELL"):
    print("Invalid side. Use BUY or SELL.")
    raise SystemExit

risk_per_share = abs(entry - stop)
risk_budget = CAPITAL * RISK_PERCENT
qty_by_risk = floor(risk_budget / risk_per_share)

if side == "BUY":
    qty_by_capital = floor(CAPITAL / entry)
    quantity = min(qty_by_risk, qty_by_capital)
else:
    quantity = qty_by_risk

if quantity < 1:
    print("BLOCK: Even 1 share exceeds your risk budget.")
    raise SystemExit

total_risk = quantity * risk_per_share
target = entry + risk_per_share * rr if side == "BUY" else entry - risk_per_share * rr
investment = quantity * entry if side == "BUY" else None

print("\n========== RISK REPORT ==========")
print("Date:", datetime.now().strftime("%d-%m-%Y"))
print("Exchange:", exchange)
print("Stock:", symbol)
print("Side:", side)
print(f"Entry: ₹{entry:.2f}")
print(f"Stop-loss: ₹{stop:.2f}")
print(f"Quantity: {quantity} shares")
if investment is not None:
    print(f"Approx. trade value: ₹{investment:.2f}")
print(f"Risk per share: ₹{risk_per_share:.2f}")
print(f"Maximum planned loss: ₹{total_risk:.2f}")
print(f"Target (RR 1:{rr:g}): ₹{target:.2f}")
print(f"Estimated gross reward: ₹{total_risk * rr:.2f}")
print("Daily loss limit: ₹100")
print("\nSTATUS: PASS - Within configured risk budget")
print("NOTE: Charges, slippage and gap risk are not included.")
print("This is a calculator only. It does NOT place orders.")
