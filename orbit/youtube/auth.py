from __future__ import annotations

from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def authenticate(client_secrets: str = "client_secret.json", token_file: str = "token.json"):
    """Run local OAuth for YouTube upload access.

    Optional dependency: google-api-python-client and google-auth-oauthlib.
    Credentials are deliberately stored outside Git-tracked files.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional YouTube dependencies with "
            "pip install '.[youtube]' before authenticating."
        ) from exc

    token_path = Path(token_file)
    credentials = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        credentials = flow.run_local_server(port=0)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials
