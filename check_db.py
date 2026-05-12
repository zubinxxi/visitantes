import asyncio
import os
from sqlmodel import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Mock the settings or read from .env if needed
# For now, let's try to find the DB URL from the env or hardcode if standard
# Actually, I can just read backend/app/core/config.py or .env

def get_db_url():
    if os.path.exists('backend/.env'):
        with open('backend/.env', 'r') as f:
            for line in f:
                if line.startswith('DATABASE_URL='):
                    return line.split('=', 1)[1].strip()
    return "mysql+aiomysql://root:root@localhost/visitorsdb" # Fallback

DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check_sysadmin():
    from backend.app.models.security import SecUser, SecUserGroupLink
    async with async_session() as session:
        result = await session.execute(select(SecUser).where(SecUser.login == 'sysadmin'))
        user = result.scalars().first()
        if user:
            print(f"User: {user.login}, active: {user.active}, priv_admin: {user.priv_admin}")
            groups_result = await session.execute(select(SecUserGroupLink).where(SecUserGroupLink.login == 'sysadmin'))
            groups = groups_result.scalars().all()
            print(f"Groups: {[g.group_id for g in groups]}")
        else:
            print("User sysadmin not found")

if __name__ == "__main__":
    asyncio.run(check_sysadmin())
