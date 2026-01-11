from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Create seasons table
        CREATE TABLE IF NOT EXISTS "seasons" (
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "is_deleted" BOOL NOT NULL DEFAULT False,
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(100) NOT NULL,
            "description" TEXT,
            "start_date" DATE NOT NULL,
            "end_date" DATE NOT NULL,
            "status" VARCHAR(9) NOT NULL DEFAULT 'upcoming',
            "club_id" INT NOT NULL REFERENCES "clubs" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "seasons"."status" IS 'UPCOMING: upcoming\nACTIVE: active\nCOMPLETED: completed';
        COMMENT ON TABLE "seasons" IS '시즌 모델 - 순위와 결과를 집계하는 기간 단위';

        -- Create season_rankings table
        CREATE TABLE IF NOT EXISTS "season_rankings" (
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "is_deleted" BOOL NOT NULL DEFAULT False,
            "id" SERIAL NOT NULL PRIMARY KEY,
            "total_matches" INT NOT NULL DEFAULT 0,
            "wins" INT NOT NULL DEFAULT 0,
            "draws" INT NOT NULL DEFAULT 0,
            "losses" INT NOT NULL DEFAULT 0,
            "points" INT NOT NULL DEFAULT 0,
            "rank" INT,
            "last_updated" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "club_member_id" INT NOT NULL REFERENCES "club_members" ("id") ON DELETE CASCADE,
            "season_id" INT NOT NULL REFERENCES "seasons" ("id") ON DELETE CASCADE,
            CONSTRAINT "uid_season_rank_season__01180c" UNIQUE ("season_id", "club_member_id")
        );
        COMMENT ON TABLE "season_rankings" IS '시즌별 랭킹';

        -- Add new columns to sessions table
        ALTER TABLE "sessions" ADD COLUMN IF NOT EXISTS "title" VARCHAR(200);
        ALTER TABLE "sessions" ADD COLUMN IF NOT EXISTS "location" VARCHAR(300);
        ALTER TABLE "sessions" ADD COLUMN IF NOT EXISTS "session_type" VARCHAR(10) NOT NULL DEFAULT 'league';
        ALTER TABLE "sessions" ADD COLUMN IF NOT EXISTS "season_id" INT REFERENCES "seasons" ("id") ON DELETE CASCADE;

        -- Make event_id nullable (sessions can now belong to season instead of event)
        ALTER TABLE "sessions" ALTER COLUMN "event_id" DROP NOT NULL;

        COMMENT ON COLUMN "sessions"."session_type" IS 'LEAGUE: league\nTOURNAMENT: tournament';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Remove new columns from sessions
        ALTER TABLE "sessions" DROP COLUMN IF EXISTS "title";
        ALTER TABLE "sessions" DROP COLUMN IF EXISTS "location";
        ALTER TABLE "sessions" DROP COLUMN IF EXISTS "session_type";
        ALTER TABLE "sessions" DROP COLUMN IF EXISTS "season_id";

        -- Drop new tables
        DROP TABLE IF EXISTS "season_rankings";
        DROP TABLE IF EXISTS "seasons";
    """
