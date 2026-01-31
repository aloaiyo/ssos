from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);
        ALTER TABLE "sessions" ADD "end_datetime" TIMESTAMPTZ NOT NULL;
        ALTER TABLE "sessions" ADD "start_datetime" TIMESTAMPTZ NOT NULL;
        ALTER TABLE "sessions" DROP COLUMN "end_time";
        ALTER TABLE "sessions" DROP COLUMN "date";
        ALTER TABLE "sessions" DROP COLUMN "start_time";
        ALTER TABLE "matches" ADD "scheduled_datetime" TIMESTAMPTZ NOT NULL;
        ALTER TABLE "matches" DROP COLUMN "scheduled_time";
        ALTER TABLE "matches" ALTER COLUMN "match_type" TYPE VARCHAR(14) USING "match_type"::VARCHAR(14);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "matches" ADD "scheduled_time" TIMETZ NOT NULL;
        ALTER TABLE "matches" DROP COLUMN "scheduled_datetime";
        ALTER TABLE "matches" ALTER COLUMN "match_type" TYPE VARCHAR(13) USING "match_type"::VARCHAR(13);
        ALTER TABLE "sessions" ADD "end_time" TIMETZ NOT NULL;
        ALTER TABLE "sessions" ADD "date" DATE NOT NULL;
        ALTER TABLE "sessions" ADD "start_time" TIMETZ NOT NULL;
        ALTER TABLE "sessions" DROP COLUMN "end_datetime";
        ALTER TABLE "sessions" DROP COLUMN "start_datetime";
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);"""
