from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clubs" ADD "default_break_duration" INT NOT NULL  DEFAULT 5;
        ALTER TABLE "clubs" ADD "default_warmup_duration" INT NOT NULL  DEFAULT 10;
        ALTER TABLE "sessions" ADD "warmup_duration_minutes" INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "clubs" DROP COLUMN "default_break_duration";
        ALTER TABLE "clubs" DROP COLUMN "default_warmup_duration";
        ALTER TABLE "sessions" DROP COLUMN "warmup_duration_minutes";"""
