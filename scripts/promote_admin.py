#!/usr/bin/env python3
"""Promote a registered user to admin role."""
import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.config import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Set user role to admin")
    parser.add_argument("email", help="Email of the user to promote")
    args = parser.parse_args()

    cfg = load_config()
    db_url = cfg["storage"]["db_url"]
    if not db_url.startswith("sqlite:///"):
        print("This script only supports SQLite db_url paths.", file=sys.stderr)
        raise SystemExit(1)

    db_path = db_url.removeprefix("sqlite:///")
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "UPDATE users SET role = 'admin' WHERE email = ?",
        (args.email.strip(),),
    )
    conn.commit()
    if cur.rowcount == 0:
        print(f"No user found with email: {args.email}")
        print("Register first in the dashboard, then run this script again.")
        raise SystemExit(1)
    print(f"OK — {args.email} is now admin. Log out and log in again in the dashboard.")


if __name__ == "__main__":
    main()
