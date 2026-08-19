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
    print("YouTube authentication succeeded.")
    print(f"Token written to: {Path(args.token_file).resolve()}")
    print("Keep this file private; it is ignored by Git.")


if __name__ == "__main__":
    main()
