from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clubs" ADD "requires_approval" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "clubs" ADD "is_join_allowed" BOOL NOT NULL  DEFAULT True;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clubs" DROP COLUMN "requires_approval";
        ALTER TABLE "clubs" DROP COLUMN "is_join_allowed";"""
