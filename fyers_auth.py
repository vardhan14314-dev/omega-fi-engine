import os
from fyers_apiv3 import fyersModel

def generate_access_token():
    client_id = os.getenv("FYERS_CLIENT_ID")
    secret_key = os.getenv("FYERS_SECRET_KEY")
    redirect_uri = os.getenv("FYERS_REDIRECT_URI", "https://127.0.0.1/")

    if not client_id or not secret_key:
        raise RuntimeError("FYERS_CLIENT_ID or FYERS_SECRET_KEY not set in environment.")

    # SessionModel is now in fyersModel (v3 SDK)
    session = fyersModel.SessionModel(
        client_id=client_id,
        secret_key=secret_key,
        redirect_uri=redirect_uri,
        response_type="code",
        grant_type="authorization_code",
    )

    # 1) Get login URL
    login_url = session.generate_authcode()
    print("\n1) Open this URL in your browser, log in, and approve access:\n")
    print(login_url)

    # 2) After login, you'll be redirected to redirect_uri with ?auth_code=...
    print("\n2) After login, copy the 'auth_code' from the redirected URL.")
    auth_code = input("Paste auth_code here: ").strip()

    # 3) Exchange auth_code for access_token
    session.set_token(auth_code)
    response = session.generate_token()
    print("\n3) FYERS token response:", response)

    access_token = response.get("access_token")
    if not access_token:
        raise RuntimeError("Failed to get access_token from FYERS response.")

    print("\n✅ Your FYERS ACCESS_TOKEN (copy this to GitHub Secrets):\n")
    print(access_token)

if __name__ == "__main__":
    generate_access_token()
