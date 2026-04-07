#!/usr/bin/env python3
"""CLI-Skript zur Erstellung eines Admin-Benutzers für das WeMood Backend."""

import asyncio
import sys
import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import AsyncSessionLocal
from app.repositories.user_repo import UserRepository


async def create_admin():
    """Fragt Benutzername und Passwort ab und erstellt einen neuen Admin-Benutzer."""
    print("\n" + "=" * 50)
    print("WeMood Backend - Create Admin User")
    print("=" * 50 + "\n")

    # Get username
    username = input("Enter admin username: ").strip()
    if len(username) < 3:
        print("Error: Username must be at least 3 characters.")
        return False

    # Get password
    password = getpass.getpass("Enter admin password: ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters.")
        return False

    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match.")
        return False

    # Create user
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository(session)

        existing = await user_repo.get_by_username(username)
        if existing:
            print(f"Error: User '{username}' already exists.")
            return False

        user = await user_repo.create_user(username, password)
        print(f"\nAdmin user '{user.username}' created successfully!")
        print(f"   User ID: {user.id}")
        print(f"   Created: {user.created_at}")

    return True


def main():
    """Einstiegspunkt für das CLI-Skript."""
    try:
        success = asyncio.run(create_admin())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()