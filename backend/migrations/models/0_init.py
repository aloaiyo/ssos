from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Initial schema created via Tortoise.generate_schemas()
        -- This migration file is a placeholder to track that the initial schema was applied.
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Downgrade not supported for initial migration
        """
