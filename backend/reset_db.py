import asyncio
from tortoise import Tortoise
from app.config import TORTOISE_ORM

async def init():
    # DB URL이 postgres인지 확인
    print(f"Connecting to {TORTOISE_ORM['connections']['default']}")
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    
    print("Dropping all tables...")
    try:
        await conn.execute_script("DROP TABLE IF EXISTS aerich CASCADE;")
        await conn.execute_script("DROP TABLE IF EXISTS club_members CASCADE;")
        await conn.execute_script("DROP TABLE IF EXISTS clubs CASCADE;")
        await conn.execute_script("DROP TABLE IF EXISTS users CASCADE;")
        print("All tables dropped.")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(init())
