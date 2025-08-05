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
from app.models.user_model import Users  # noqa
from app.core.config import settings  # noqa
from app.core.security import hash_password  # noqa


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
                username="system",
                email="system@klampis.com",
                password=hash_password("system"),
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
            return system_user

        except Exception as e:
            print(f"Error creating system user: {e}")
            await session.rollback()
            raise


async def create_admin_user():
    """Create admin user if it doesn't exist."""
    async with async_session_factory() as session:
        try:
            # Check if admin user exists
            result = await session.get(Users, settings.ADMIN_USER_ID)

            if result:
                print(f"Admin user already exists: {result}")
                return result

            # Create admin user
            admin_user = Users(
                username="admin",
                email="admin@klampis.com",
                password=hash_password("admin"),
                name="Administrator",
                role="ADMIN",
                created_by=settings.SYSTEM_USER_ID,
                updated_by=settings.SYSTEM_USER_ID,
                sequence=2
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print(f"Admin user created successfully: {admin_user}")
            print(f"Username: {admin_user.username}")
            print("Password: admin")
            return admin_user

        except Exception as e:
            print(f"Error creating admin user: {e}")
            await session.rollback()
            raise


async def main():
    """Main function to create system user."""
    print("Creating system user...")

    try:
        await create_system_user()
        await create_admin_user()
        print("✅ System user setup completed!")

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
