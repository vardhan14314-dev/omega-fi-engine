import os
from fyers_apiv3 import fyersModel

def get_fyers_client():
    client_id = os.getenv("FYERS_CLIENT_ID")
    access_token = os.getenv("FYERS_ACCESS_TOKEN")

    if not client_id or not access_token:
        raise RuntimeError("Missing FYERS_CLIENT_ID or FYERS_ACCESS_TOKEN in environment.")

    token = f"{client_id}:{access_token}"
    return fyersModel.FyersModel(client_id=client_id, token=token, log_path=None)

def get_quotes(symbols):
    fyers = get_fyers_client()
    payload = {"symbols": ",".join(symbols)}
    return fyers.quotes(payload)

def get_history(symbol, resolution, date_from, date_to):
    fyers = get_fyers_client()
    payload = {
        "symbol": symbol,
        "resolution": resolution,
        "date_format": "1",
        "range_from": date_from,
        "range_to": date_to,
        "cont_flag": "1"
    }
    return fyers.history(payload)
