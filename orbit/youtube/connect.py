from __future__ import annotations

import argparse
from pathlib import Path

from orbit.youtube.auth import authenticate


def main() -> None:
    parser = argparse.ArgumentParser(description="Connect ORBIT to a YouTube channel through OAuth 2.0.")
    parser.add_argument("--client-secrets", default="client_secret.json")
    parser.add_argument("--token-file", default="token.json")
    args = parser.parse_args()

    credentials = authenticate(args.client_secrets, args.token_file)

    try:
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Install the optional YouTube dependencies with pip install '.[youtube]'.") from exc

    service = build("youtube", "v3", credentials=credentials)
    response = service.channels().list(part="snippet", mine=True).execute()
    channels = response.get("items", [])
    if not channels:
        raise RuntimeError("OAuth succeeded, but Google returned no YouTube channel for this account.")

    channel = channels[0]
    title = channel.get("snippet", {}).get("title", "Unknown channel")
    channel_id = channel.get("id", "unknown")

    print("YouTube authentication succeeded.")
    print(f"Channel: {title}")
    print(f"Channel ID: {channel_id}")
    print(f"Token written to: {Path(args.token_file).resolve()}")
    print("Keep this token private; it is ignored by Git.")


if __name__ == "__main__":
    main()
