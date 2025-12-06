import os
from datetime import datetime, timedelta, timezone
from openai import OpenAI

from fyers_data import get_quotes, get_history

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

with open("omega_prompt.txt", "r", encoding="utf-8") as f:
    OMEGA_SYSTEM_PROMPT = f.read()

def build_next_day_payload():
    symbols_str = os.getenv("NEXT_DAY_SYMBOLS", "")
    if not symbols_str:
        symbols_str = "NSE:HDFCBANK-EQ,NSE:RELIANCE-EQ,NSE:TCS-EQ,NSE:SBIN-EQ,NSE:ICICIBANK-EQ"

    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
    today = datetime.now().date()
    start_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    data = {
        "mode": "NEXT_DAY",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "symbols": []
    }

    for sym in symbols:
        try:
            hist = get_history(sym, "D", start_date, end_date)
            data["symbols"].append({"symbol": sym, "history": hist})
        except Exception as e:
            data["symbols"].append({"symbol": sym, "error": str(e)})

    return data

def build_live_payload():
    symbols_str = os.getenv("SYMBOLS", "")
    if not symbols_str:
        symbols_str = "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX"

    symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
    quotes = get_quotes(symbols)

    data = {
        "mode": "LIVE",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "symbols": symbols,
        "quotes": quotes
    }
    return data

def call_omega(market_payload: dict) -> str:
    mode = market_payload.get("mode", "UNKNOWN")

    user_content = (
        f"Mode: {mode}\n"
        "Below is the market payload from FYERS. "
        "Use it according to your OMEGA-FI system instructions and respond ONLY with clean human-readable analysis.\n\n"
        f"MARKET_PAYLOAD_START\n{market_payload}\nMARKET_PAYLOAD_END\n"
    )

    messages = [
        {"role": "system", "content": OMEGA_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    resp = client.chat.completions.create(
        model="gpt-5.1",
        messages=messages,
        temperature=0.1,
    )

    return resp.choices[0].message.content

def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment.")

    scan_mode = os.getenv("SCAN_MODE", "").upper().strip()
    if scan_mode == "LIVE":
        payload = build_live_payload()
    else:
        payload = build_next_day_payload()

    omega_output = call_omega(payload)

    print("===== OMEGA OUTPUT START =====")
    print(omega_output)
    print("===== OMEGA OUTPUT END =====")

if __name__ == "__main__":
    main()
