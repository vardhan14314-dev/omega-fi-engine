import os
from datetime import datetime, timezone
from openai import OpenAI

# Load OpenAI key from env (will be set on Render)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Load OMEGA-FI system prompt from file
with open("omega_prompt.txt", "r", encoding="utf-8") as f:
    OMEGA_SYSTEM_PROMPT = f.read()

def build_dummy_market_payload():
    """
    Temporary dummy payload just to test OMEGA wiring.
    Later we replace this with real broker data.
    """
    now = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp_utc": now,
        "mode": "INTRADAY",
        "symbols": [
            {
                "symbol": "NIFTY",
                "last_price": 25000,
                "change_pct": 0.45,
                "volume": 12345678,
                "ohlc": {
                    "open": 24850,
                    "high": 25100,
                    "low": 24800,
                    "close": 24980
                }
            }
        ]
    }

def call_omega(market_payload: dict) -> str:
    """
    Calls OpenAI with the OMEGA-FI system prompt + payload.
    """
    messages = [
        {"role": "system", "content": OMEGA_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "You are running in automated engine mode.\n"
                "Here is the market payload in JSON format:\n"
                f"{market_payload}\n\n"
                "Run the appropriate logic and respond strictly with the HUMAN_SUMMARY and STRUCTURED_PAYLOAD as defined."
            )
        }
    ]

    response = client.chat.completions.create(
        model="gpt-5.1",  # or your chosen model
        messages=messages,
        temperature=0.1
    )

    return response.choices[0].message.content

def main():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

    payload = build_dummy_market_payload()
    omega_output = call_omega(payload)

    # For now just print, Render logs will capture this
    print("===== OMEGA OUTPUT START =====")
    print(omega_output)
    print("===== OMEGA OUTPUT END =====")

if __name__ == "__main__":
    main()
