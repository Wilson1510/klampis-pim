#!/usr/bin/env python3
"""
Script to create system user automatically.

This script creates a system user with ID 1 that will be used for audit trail
in all other models. The system user has no password and SYSTEM role.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.session import async_session_factory  # noqa
from app.models.user import Users  # noqa
from app.core.config import settings  # noqa


async def create_system_user():
    """Create system user if it doesn't exist."""
    async with async_session_factory() as session:
        try:
            # Check if system user exists
            result = await session.get(Users, settings.SYSTEM_USER_ID)

            if result:
                print(f"System user already exists: {result}")
                return result

            # Create system user
            system_user = Users(
                id=settings.SYSTEM_USER_ID,
                username="system",
                password="system",
                name="System User",
                role="SYSTEM",
                created_by=None,
                updated_by=None,
                sequence=1
            )

            session.add(system_user)
            await session.commit()
            await session.refresh(system_user)

            print(f"System user created successfully: {system_user}")
            print(
                f"login with username: {system_user.username} and password: "
                f"{system_user.password}"
            )
            return system_user

        except Exception as e:
            print(f"Error creating system user: {e}")
            await session.rollback()
            raise


async def main():
    """Main function to create system user."""
    print("Creating system user...")

    try:
        system_user = await create_system_user()
        print("✅ System user setup completed!")
        print(f"Role: {system_user.role}")

    except Exception as e:
        print(f"❌ Failed to create system user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
